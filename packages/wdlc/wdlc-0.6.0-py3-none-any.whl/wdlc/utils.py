import torch.nn as nn
import numpy as np
import json
import os
import gzip
from io import BytesIO
import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial


def flatten_sequential(module, parent_name=""):
    flattened = []

    if isinstance(module, nn.Sequential):
        for idx, submodule in enumerate(module):
            name = f"{parent_name}_{idx}" if parent_name else f"seq_{idx}"
            if isinstance(submodule, nn.Sequential):
                flattened.extend(flatten_sequential(submodule, parent_name=name))
            else:
                flattened.append((name, submodule))

    else:
        name = parent_name if parent_name else type(module).__name__
        flattened.append((name, module))

    return flattened


def save_binary(layers, weights_data, output_path, input_shape):
        """Save model as single binary file"""
        
        print(f"🔄 Compiling model to binary format...")
        
        model_data = {
            "version": "1.0.0",
            "metadata": {
                "input_shape": input_shape,
                "num_layers": len(layers),
                "total_parameters": sum(w.size for w in weights_data.values()),
                "framework": "pytorch",
                "compiler": "WDLC",
                "layers_info": [
                    {
                        "name": layer["name"],
                        "type": layer["type"],
                        **({"in_features": layer["in_features"], "out_features": layer["out_features"]} 
                           if layer["type"] == "linear" else {})
                    }
                    for layer in layers
                ]
            },
            "graph": layers,
            "weights": {}
        }

        total_weight_size = 0
        for key, weight_array in weights_data.items():
            # Save as numpy binary format
            buffer = BytesIO()
            np.save(buffer, weight_array)
            buffer.seek(0)
            binary_data = buffer.read()
            
            model_data["weights"][key] = {
                "data": base64.b64encode(binary_data).decode('utf-8'),
                "shape": weight_array.shape,
                "dtype": str(weight_array.dtype),
                "size": weight_array.size
            }

            total_weight_size += len(binary_data)

        # Convert to JSON and compress
        json_str = json.dumps(model_data, separators=(',', ':')) 
        json_bytes = json_str.encode('utf-8')
        compressed_data = gzip.compress(json_bytes, compresslevel=9)
        
        with open(output_path, 'wb') as f:
            f.write(compressed_data)
        
        compression_ratio = len(json_bytes) / len(compressed_data)
        print(f"✅ Binary export completed!")
        print(f"   📁 Output file: {output_path}")
        print(f"   📊 File size: {len(compressed_data) / 1024:.2f} KB")
        print(f"   🗜️  Compression ratio: {compression_ratio:.2f}x")
        print(f"   🧠 Total parameters: {model_data['metadata']['total_parameters']:,}")
        print(f"   🏗️  Layers: {model_data['metadata']['num_layers']}")


def save_to_dir(layers, weights_data, output_dir):
        """Save model as directory structure (original format)"""
        
        print(f"🔄 Exporting compiled model to {output_dir}")
        
        os.makedirs(output_dir, exist_ok=True)

        for key, weight_array in weights_data.items():
            filename = f"{key}.npy"
            np.save(os.path.join(output_dir, filename), weight_array)

        with open(os.path.join(output_dir, "graph.json"), "w") as f:
            json.dump(layers, f, indent=2)

        total_params = sum(w.size for w in weights_data.values())
        print(f"✅ Directory export completed!")
        print(f"   📁 Output directory: {output_dir}")
        print(f"   🧠 Total parameters: {total_params:,}")
        print(f"   🏗️  Layers: {len(layers)}")


def inspect_binary_model(file_path, test_input=None):
    """Utility to load and inspect binary model without WebGPU"""
    print(f"🔍 Inspecting binary model: {file_path}")

    try:
        with open(file_path, 'rb') as f:
            compressed_data = f.read()

        # Decompress
        json_bytes = gzip.decompress(compressed_data)
        model_data = json.loads(json_bytes.decode('utf-8'))

        metadata = model_data['metadata']
        print(f"   📊 Model version: {model_data['version']}")
        print(f"   🔢 Input shape: {metadata['input_shape']}")
        print(f"   🏗️  Layers: {metadata['num_layers']}")
        print(f"   🧠 Total parameters: {metadata['total_parameters']:,}")
        print(f"   🔧 Framework: {metadata['framework']}")
        print(f"   ⚙️  Compiler: {metadata['compiler']}")

        print(f"\n   🏗️  Layer Architecture:")
        for i, layer_info in enumerate(metadata['layers_info'], 1):
            if layer_info['type'] == 'linear':
                print(f"      {i}. {layer_info['name']}: Linear({layer_info['in_features']} → {layer_info['out_features']})")
            else:
                print(f"      {i}. {layer_info['name']}: {layer_info['type'].upper()}")

        print(f"\n   💾 File size: {len(compressed_data) / 1024:.2f} KB")
        print(f"   🗜️  Compression ratio: {len(json_bytes) / len(compressed_data):.2f}x")
        return model_data

    except Exception as e:
        print(f"❌ Error inspecting model: {e}")
        return None


class CORSRequestHandler(SimpleHTTPRequestHandler):
    """CORS-enabled request handler that only serves model files and redirects root to model"""
    
    def __init__(self, *args, allowed_paths=None, model_redirect=None, **kwargs):
        self.allowed_paths = allowed_paths or set()
        self.model_redirect = model_redirect 
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        return super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()
    
    def do_GET(self):
        requested_path = self.path.lstrip('/')
        
        if requested_path == '':
            if self.model_redirect:
                self.send_response(302, 'Found')
                self.send_header('Location', f'/{self.model_redirect}')
                self.end_headers()
                return
            
        if requested_path in self.allowed_paths:
            return super().do_GET()
        
        self.send_response(403, 'Forbidden')
        self.end_headers()
        self.wfile.write(b'Access denied: Only model files are accessible')
    
def deploy(model_path, port=8000):
    """Deploy model file or directory to HTTP server.
    
    Only serves model files and prevents access to other files in the directory.
    Root directory requests are redirected to the model.
    This is a free function intended to be called from the CLI as:
        deploy(model_path, port)
    """
    if model_path is None:
        print(f"❌ Error: model_path is required")
        return

    if os.path.isfile(model_path) and model_path.endswith('.wdlc'):
        # For binary models, serve only the specific .wdlc file
        web_dir = os.path.dirname(os.path.abspath(model_path)) or "."
        model_filename = os.path.basename(model_path)
        allowed_paths = {model_filename}
        
        handler = partial(CORSRequestHandler, 
                         directory=web_dir, 
                         allowed_paths=allowed_paths,
                         model_redirect=model_filename)

        server = HTTPServer(("", port), handler)

        print(f"> Serving binary model with CORS")
        print(f"    Server: http://localhost:{port}")
        print(f"    Model URL: http://localhost:{port}/{model_filename}")
        print(f"    Serving from: {web_dir}")
        print(f"\n   JavaScript usage:")
        print(f"   const model = new WDLC();")
        print(f"   await model.load('http://localhost:{port}/{model_filename}');")
        print(f"\n Press Ctrl+C to stop the server")

    elif os.path.isdir(model_path):
        # For model directories, serve only model-related files
        model_dir = os.path.abspath(model_path)
        web_dir = os.path.dirname(model_dir) or "."
        model_dir_name = os.path.basename(model_path)
        
        # Get list of model files in the directory
        allowed_files = set()
        try:
            for file in os.listdir(model_dir):
                if file.endswith(('.npy', '.json')):
                    allowed_files.add(f"{model_dir_name}/{file}")
        except OSError as e:
            print(f"❌ Error reading model directory: {e}")
            return
        
        # Allow access to the directory itself for listing
        allowed_files.add(f"{model_dir_name}/")
        
        handler = partial(CORSRequestHandler, 
                         directory=web_dir, 
                         allowed_paths=allowed_files,
                         model_redirect=f"{model_dir_name}/")

        server = HTTPServer(("", port), handler)

        print(f"> Serving model directory")
        print(f"    Server: http://localhost:{port}")
        print(f"    Model URL: http://localhost:{port}/{model_dir_name}")
        print(f"    Serving from: {web_dir}")
        print(f"\n   JavaScript usage:")
        print(f"   const model = new WDLC('http://localhost:{port}/{model_dir_name}');")
        print(f"   await model.init();")
        print(f"\n Press Ctrl+C to stop the server")

    else:
        print(f"❌ Error: Model path '{model_path}' not found!")
        return

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n Server stopped")
        

