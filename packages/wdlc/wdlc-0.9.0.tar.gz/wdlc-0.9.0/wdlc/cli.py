#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WDLC Command Line Interface

"""
import sys
import io
import signal 

if sys.platform == 'win32':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCP(65001)
    kernel32.SetConsoleOutputCP(65001)
    
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf-8')



from wdlc import inspect_binary_model, deploy
import argparse
import os
import importlib.util
import torch
import torch.nn as nn
import json
import subprocess
import signal
import time
import psutil
from wdlc.wdlc import WDLC

SERVER_PID_DIR = os.path.expanduser("~/.wdlc/servers")

def ensure_pid_dir():
    """Ensure the PID directory exists"""
    os.makedirs(SERVER_PID_DIR, exist_ok=True)

class Colors:
    # Main colors
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    RESET = '\033[0m'
    
    @staticmethod
    def strip_colors():
        """Disable colors for non-terminal output"""
        if not sys.stdout.isatty():
            for attr in dir(Colors):
                if not attr.startswith('_') and attr != 'strip_colors':
                    setattr(Colors, attr, '')

Colors.strip_colors()

class Chars:
    """Unicode characters with Windows fallbacks"""
    def __init__(self):
        self.TOP_LEFT = '┌'
        self.TOP_RIGHT = '┐' 
        self.BOTTOM_LEFT = '└'
        self.BOTTOM_RIGHT = '┘'
        self.HORIZONTAL = '─'
        self.VERTICAL = '│'
        self.CROSS_LEFT = '├'
        self.CROSS_RIGHT = '┤'
            
            # Unicode icons
        self.INFO = 'ℹ'
        self.SUCCESS = '✓'
        self.WARNING = '⚠'
        self.ERROR = '✗'
        self.LOADING = '⟳'
        self.BULLET = '•'
            
            # Emoji characters
        self.PARTY = '🎉'
        self.SERVER = '🌐'
        self.CHART = '📊'
        self.FOLDER = '📁'
        self.PACKAGE = '📦'
        self.MEMO = '📝'
        self.WRENCH = '🔧'
        self.MAG = '🔍'
        self.STOP = '🛑'
        self.WAVE = '👋'
        self.GAMEPAD = '🎮'
        
            
      
    
    

# Global instance
chars = Chars()

SERVER_PID_DIR = os.path.expanduser("~/.wdlc/servers")

def ensure_pid_dir():
    """Ensure the PID directory exists"""
    os.makedirs(SERVER_PID_DIR, exist_ok=True)

def get_server_pid_file(port):
    """Get the PID file path for a server"""
    ensure_pid_dir()
    return os.path.join(SERVER_PID_DIR, f"server_{port}.pid")

def save_server_info(port, pid, model_path, format_type):
    """Save server information"""
    ensure_pid_dir()
    info_file = os.path.join(SERVER_PID_DIR, f"server_{port}.json")
    info = {
        "pid": pid,
        "port": port,
        "model_path": os.path.abspath(model_path),
        "format_type": format_type,
        "started_at": time.time(),
        "url": f"http://localhost:{port}"
    }
    with open(info_file, 'w') as f:
        json.dump(info, f, indent=2)

def get_server_info(port):
    """Get server information"""
    info_file = os.path.join(SERVER_PID_DIR, f"server_{port}.json")
    if os.path.exists(info_file):
        with open(info_file, 'r') as f:
            return json.load(f)
    return None

def list_running_servers():
    """List all running WDLC servers"""
    ensure_pid_dir()
    servers = []
    for filename in os.listdir(SERVER_PID_DIR):
        if filename.startswith("server_") and filename.endswith(".json"):
            port = filename.replace("server_", "").replace(".json", "")
            info = get_server_info(int(port))
            if info and is_server_running(info["pid"]):
                servers.append(info)
            else:
                cleanup_server_files(int(port))
    return servers

def is_server_running(pid):
    """Check if a server process is running"""
    try:
        return psutil.pid_exists(pid)
    except:
        return False

def cleanup_server_files(port):
    """Clean up server files"""
    pid_file = get_server_pid_file(port)
    info_file = os.path.join(SERVER_PID_DIR, f"server_{port}.json")
    
    for file_path in [pid_file, info_file]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

def stop_server(port):
    """Stop a server by port"""
    info = get_server_info(port)
    if not info:
        return False, "Server not found"
    
    pid = info["pid"]
    if not is_server_running(pid):
        cleanup_server_files(port)
        return False, "Server is not running"
    
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        
        if is_server_running(pid):
            os.kill(pid, signal.SIGKILL)
        
        cleanup_server_files(port)
        return True, "Server stopped successfully"
    except Exception as e:
        return False, f"Failed to stop server: {e}"

def print_header(title, subtitle=None):
    """Print a compact header box like print_box but tailored for headers."""
    safe_title = strip_ansi(title)
    if subtitle:
        safe_sub = strip_ansi(subtitle)
        content_width = max(len(safe_title), len(safe_sub))
    else:
        content_width = len(safe_title)

    width = content_width + 4

    print(f"\n{Colors.CYAN}{chars.TOP_LEFT}{chars.HORIZONTAL * (width - 2)}{chars.TOP_RIGHT}{Colors.RESET}")

    title_padding = width - len(safe_title) - 4
    print(f"{Colors.CYAN}{chars.VERTICAL}{Colors.BOLD} {title}{' ' * title_padding} {Colors.RESET}{Colors.CYAN}{chars.VERTICAL}{Colors.RESET}")

    if subtitle:
        print(f"{Colors.CYAN}{chars.CROSS_LEFT}{chars.HORIZONTAL * (width - 2)}{chars.CROSS_RIGHT}{Colors.RESET}")
        sub_padding = width - len(safe_sub) - 4
        print(f"{Colors.CYAN}{chars.VERTICAL}{Colors.GRAY} {subtitle}{' ' * sub_padding} {Colors.RESET}{Colors.CYAN}{chars.VERTICAL}{Colors.RESET}")

    print(f"{Colors.CYAN}{chars.BOTTOM_LEFT}{chars.HORIZONTAL * (width - 2)}{chars.BOTTOM_RIGHT}{Colors.RESET}")

def print_step(step, message, status="info"):
    """Print a step with icon and formatting"""
    icons = {
        "info": f"{Colors.BLUE}{chars.INFO}{Colors.RESET}",
        "success": f"{Colors.GREEN}{chars.SUCCESS}{Colors.RESET}",
        "warning": f"{Colors.YELLOW}{chars.WARNING}{Colors.RESET}",
        "error": f"{Colors.RED}{chars.ERROR}{Colors.RESET}",
        "loading": f"{Colors.YELLOW}{chars.LOADING}{Colors.RESET}",
    }
    
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "loading": Colors.YELLOW,
    }
    
    icon = icons.get(status, icons["info"])
    color = colors.get(status, Colors.BLUE)
    
    print(f"{icon} {Colors.BOLD}Step {step}:{Colors.RESET} {color}{message}{Colors.RESET}")

def print_detail(key, value, indent=2):
    """Print a key-value pair with nice formatting"""
    spaces = " " * indent
    print(f"{spaces}{Colors.GRAY}{chars.BULLET}{Colors.RESET} {Colors.DIM}{key}:{Colors.RESET} {Colors.WHITE}{value}{Colors.RESET}")

def strip_ansi(text):
    """Remove ANSI escape sequences from text for accurate width calculation"""
    import re
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

def print_box(title, content, color=Colors.BLUE):
    """Print content in a nice box"""
    lines = content.split('\n')
    max_line_length = max(len(strip_ansi(line)) for line in lines)
    title_length = len(strip_ansi(title))
    width = max(max_line_length, title_length) + 4
    
    print(f"\n{color}{chars.TOP_LEFT}{chars.HORIZONTAL * (width - 2)}{chars.TOP_RIGHT}{Colors.RESET}")
    title_padding = width - title_length - 4
    print(f"{color}{chars.VERTICAL}{Colors.BOLD} {title}{' ' * title_padding} {Colors.RESET}{color}{chars.VERTICAL}{Colors.RESET}")
    print(f"{color}{chars.CROSS_LEFT}{chars.HORIZONTAL * (width - 2)}{chars.CROSS_RIGHT}{Colors.RESET}")
    
    for line in lines:
        line_padding = width - len(strip_ansi(line)) - 4
        print(f"{color}{chars.VERTICAL}{Colors.RESET} {line}{' ' * line_padding} {color}{chars.VERTICAL}{Colors.RESET}")
    
    print(f"{color}{chars.BOTTOM_LEFT}{chars.HORIZONTAL * (width - 2)}{chars.BOTTOM_RIGHT}{Colors.RESET}")

def print_progress_bar(current, total, width=40):
    """Print a simple progress bar"""
    filled = int(width * current / total)
    if chars.unicode_supported:
        bar = '█' * filled + '░' * (width - filled)
    else:
        bar = '#' * filled + '-' * (width - filled)
    percentage = int(100 * current / total)
    print(f"\r{Colors.CYAN}[{bar}]{Colors.RESET} {percentage}%", end='', flush=True)

def load_model_from_script(script_path):
    """Load PyTorch model from a Python script"""
    global deploy  
    
    print_header("Model Loading", "Extracting PyTorch model")
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    print_step(1, f"Loading script: {Colors.CYAN}{script_path}{Colors.RESET}")
    
    spec = importlib.util.spec_from_file_location("model_script", script_path)
    module = importlib.util.module_from_spec(spec)
    
    original_deploy = deploy  
   
    original_compile = WDLC.compile
    def dummy_deploy(self, *args, **kwargs):
        print_detail("Skipped", "deploy() call during loading", 4)
        pass
    def dummy_compile(self, *args, **kwargs):
        print_detail("Skipped", "compile() call during loading", 4)
        return None
    deploy = dummy_deploy
    WDLC.compile = dummy_compile
    
    print_step(2, "Executing Model", "loading")
    
    original_stdout = sys.stdout
    try:
        sys.stdout = open(os.devnull, 'w', encoding='utf-8')
        spec.loader.exec_module(module)
    finally:
        sys.stdout.close()
        sys.stdout = original_stdout
        deploy = original_deploy
        WDLC.compile = original_compile
    
    print_step(3, "Analyzing module for model and parameters", "loading")
    
    model = None
    input_size = None
    
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        
        if isinstance(attr, torch.nn.Module) and model is None:
            model = attr
            print_detail("Model found", f"{Colors.GREEN}{type(model).__name__}{Colors.RESET}", 4)
        
        if attr_name in ['input_size', 'input_dim', 'num_features'] and isinstance(attr, int):
            input_size = attr
            print_detail("Input size", f"{Colors.GREEN}{input_size}{Colors.RESET}", 4)
    
    if model is None:
        raise ValueError("No PyTorch model found in script. Make sure you have a model variable.")
    
    if input_size is None:
        if hasattr(model, 'fc1') and hasattr(model.fc1, 'in_features'):
            input_size = model.fc1.in_features
            print_detail("Input size (inferred)", f"{Colors.YELLOW}{input_size}{Colors.RESET}", 4)
        else:
            raise ValueError("Could not determine input_size. Please define 'input_size' variable in your script.")
    
    print_step(4, "Model extraction complete", "success")
    return model, input_size

def cmd_compile(args):
    """Compile a PyTorch model to WDLC format"""
    print_header("WDLC Compiler", "PyTorch → WebGPU")
    
    try:
        model, input_size = load_model_from_script(args.script)
        
        print_header("Compilation Setup")
        wdlc = WDLC(model, input_size)
        
        if args.binary is not None:
            if args.binary is True:
                output_path = os.path.abspath('model.wdlc')
                print_detail('Note', f"No output path provided for --binary; using default: {Colors.CYAN}{output_path}{Colors.RESET}")
            else:
                output_path = args.binary
                if not output_path.endswith('.wdlc'):
                    output_path = output_path + '.wdlc'
                output_path = os.path.abspath(output_path)

            wdlc.set_output_format('binary')
            format_type = f"{Colors.PURPLE}Binary (.wdlc){Colors.RESET}"
            print_step(1, f"Format: {format_type}")
            print_detail('Output', f"{Colors.CYAN}{output_path}{Colors.RESET}")

        elif args.folder:
            wdlc.set_output_format('dir')
            output_path = args.folder
            format_type = f"{Colors.BLUE}Folder structure{Colors.RESET}"
            print_step(1, f"Format: {format_type}")
            print_detail('Output', f"{Colors.CYAN}{output_path}{Colors.RESET}")
        else:
            wdlc.set_output_format('dir')
            output_path = os.path.abspath('web_model')
            format_type = f"{Colors.BLUE}Folder structure{Colors.RESET}"
            print_step(1, f"Format: {format_type}")
            print_detail('Output', f"{Colors.CYAN}{output_path}{Colors.RESET}")
            
       

        
        print_step(2, "Starting compilation...", "loading")
        
        original_stdout = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w', encoding='utf-8')
            result_path = wdlc.compile(output_path)
        finally:
            sys.stdout.close()
            sys.stdout = original_stdout
        
        print_step(3, "Compilation completed", "success")
        
        if os.path.isfile(result_path):
            file_size = os.path.getsize(result_path) / 1024  
            print_detail("File size", f"{file_size:.2f} KB")
        
        print_box("✓ Success", f"Model compiled successfully!\nOutput: {result_path}", Colors.GREEN)
        
        if args.serve:
            print_header("Development Server")
            print_step(1, f"Starting server on port {args.port}...", "loading")
            deploy(result_path, args.port)
            
    except Exception as e:
        print_box("✗ Error", str(e), Colors.RED)
        sys.exit(1)

def cmd_inspect(args):
    """Inspect a compiled WDLC model"""
    print_header("WDLC Inspector", "Model analysis")
    
    if not os.path.exists(args.model):
        print_box("✗ Error", f"Model file not found: {args.model}", Colors.RED)
        return
    
    print_step(1, f"Loading model: {Colors.CYAN}{args.model}{Colors.RESET}")
    
    
    print_step(3, "Analyzing model structure...", "loading")
    
    original_stdout = sys.stdout
    try:
        import io
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        model_data = inspect_binary_model(args.model)
        
        sys.stdout = original_stdout
        output = captured_output.getvalue()
        
        if model_data:
            print_step(4, "Model inspection completed", "success")
            
            metadata = model_data.get('metadata', {})
            
            model_info = f"""Version: {model_data.get('version', 'N/A')}
Framework: {metadata.get('framework', 'N/A')}
Input Size: {metadata.get('input_size', 'N/A')}
Layers: {metadata.get('num_layers', 'N/A')}
Parameters: {metadata.get('total_parameters', 'N/A'):,}"""
            
            print_box(f"{chars.CHART} Model Information", model_info, Colors.BLUE)
            
            if 'layers_info' in metadata:
                print(f"\n{Colors.BOLD}🏗️  Architecture:{Colors.RESET}")
                for i, layer in enumerate(metadata['layers_info'], 1):
                    if layer['type'] == 'linear':
                        layer_desc = f"Linear({layer['in_features']} → {layer['out_features']})"
                        color = Colors.BLUE
                    else:
                        layer_desc = layer['type'].upper()
                        color = Colors.YELLOW
                    
                    print(f"  {Colors.GRAY}{i:2d}.{Colors.RESET} {Colors.BOLD}{layer['name']:<8}{Colors.RESET} {color}{layer_desc}{Colors.RESET}")
            
            
            
    except Exception as e:
        sys.stdout = original_stdout
        print_box("✗ Error", f"Inspection failed: {str(e)}", Colors.RED)
    
    print_box("✓ Complete", "Inspection finished successfully", Colors.GREEN)

def print_server_banner(port, model_path, format_type, model_info=None):
    """Print a beautiful server banner"""
    print(f"\n{Colors.GREEN}{Colors.BOLD}{chars.PARTY} WDLC Server Ready!{Colors.RESET}\n")
    
    local_url = f"http://localhost:{port}"
    network_url = f"http://127.0.0.1:{port}"
    
    server_info = f"""Local:     {Colors.CYAN}{Colors.BOLD}{local_url}{Colors.RESET}
Network:   {Colors.CYAN}{local_url}{Colors.RESET}
Model:     {Colors.YELLOW}{os.path.basename(model_path)}{Colors.RESET}
Format:    {format_type}"""

    if model_info:
        server_info += f"""
Parameters: {Colors.PURPLE}{model_info.get('total_parameters', 'N/A'):,}{Colors.RESET}
Layers:     {Colors.BLUE}{model_info.get('num_layers', 'N/A')}{Colors.RESET}"""

    print_box(f"{chars.SERVER} Server Information", server_info, Colors.GREEN)
    
    model_name = os.path.basename(model_path)
    if format_type.startswith("Binary"):
        js_example = f"""// Load binary model
const model = WDLC('{local_url}/{model_name}');
await model.init();
const output = await model.predict([1,2,3,4,5]);"""
    else:
        js_example = f"""// Load folder model  
const model = WDLC('{local_url}/{model_name}');
await model.init();
const output = await model.predict([1,2,3,4,5]);"""
    
    print(f"\n{Colors.BOLD}{chars.MEMO} Usage Example:{Colors.RESET}")
    print(f"{Colors.DIM}{js_example}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{chars.GAMEPAD} Controls:{Colors.RESET}")
    print(f"  {Colors.CYAN}Ctrl+C{Colors.RESET}  Stop the server")
    print(f"  {Colors.CYAN}Ctrl+Z{Colors.RESET}  Background the process")
    
    print(f"\n{Colors.DIM}{'─' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}> Server is running... {Colors.DIM}(Press Ctrl+C to stop){Colors.RESET}")
    print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}\n")

def get_model_info(model_path):
    """Extract model information for display"""
    try:
        if model_path.endswith('.wdlc'):
            import gzip
            import json
            with open(model_path, 'rb') as f:
                compressed_data = f.read()
            json_bytes = gzip.decompress(compressed_data)
            model_data = json.loads(json_bytes.decode('utf-8'))
            return model_data.get('metadata', {})
        elif os.path.isdir(model_path):
            graph_path = os.path.join(model_path, 'graph.json')
            if os.path.exists(graph_path):
                with open(graph_path, 'r') as f:
                    graph = json.load(f)
                return {
                    'num_layers': len(graph),
                    'total_parameters': 'Unknown'  
                }
    except:
        pass
    return None

def cmd_serve(args):
    """Serve a compiled WDLC model"""
    print_header("WDLC Development Server", "Model deployment ")
    
    if not os.path.exists(args.model):
        print_box("✗ Error", f"Model not found: {args.model}", Colors.RED)
        return
    
    existing_info = get_server_info(args.port)
    if existing_info:
        if is_server_running(existing_info["pid"]):
            print_box("⚠ Warning", f"Server already running on port {args.port}\nUse 'wdlc stop {args.port}' to stop it first", Colors.YELLOW)
            return
        else:
            # Clean up stale server files
            cleanup_server_files(args.port)
    
    print_step(1, f"Model: {Colors.CYAN}{args.model}{Colors.RESET}")
    
    model_info = get_model_info(args.model)
    if model_info:
        print_detail("Parameters", f"{model_info.get('total_parameters', 'Unknown'):,}")
        print_detail("Layers", f"{model_info.get('num_layers', 'Unknown')}")
    
    if os.path.isfile(args.model) and args.model.endswith('.wdlc'):
        format_type = "Binary (.wdlc)"
        format_display = f"{Colors.PURPLE}{format_type}{Colors.RESET}"
        
        file_size = os.path.getsize(args.model) / 1024
        print_detail("File size", f"{file_size:.2f} KB")
        
    elif os.path.isdir(args.model):
        format_type = "Folder structure"
        format_display = f"{Colors.BLUE}{format_type}{Colors.RESET}"
        
        try:
            file_count = len(os.listdir(args.model))
            print_detail("Files", f"{file_count}")
        except:
            pass
    else:
        print_box("✗ Error", f"Unrecognized model format: {args.model}\nExpected: .wdlc file or directory containing graph.json", Colors.RED)
        return
    
    print_step(2, f"Format: {format_display}")
    
    if args.background:
        print_step(3, f"Starting server in background on port {Colors.YELLOW}{args.port}{Colors.RESET}...", "loading")
        
        script_path = os.path.abspath(__file__)
        cmd = [
            sys.executable,"-u" ,script_path, "serve", args.model,
            "--port", str(args.port),
            "--foreground"  
        ]
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
      
        # Open log files for writing
        stdout_log = open(os.path.join(log_dir, f"server_{args.port}.out.log"), 'w')
        stderr_log = open(os.path.join(log_dir, f"server_{args.port}.err.log"), 'w')
        
        popen_kwargs = {
            'stdout': stdout_log,
            'stderr': stderr_log,
            'stdin': subprocess.DEVNULL,
        }
        if sys.platform != 'win32':
            popen_kwargs['preexec_fn'] = os.setsid
        else:
            popen_kwargs['creationflags'] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
          

        process = subprocess.Popen(cmd, **popen_kwargs)
        
        # Close the log file handles in the parent process - the child process has its own handles
        stdout_log.close()
        stderr_log.close()
        
        time.sleep(2)
        if process.poll() is None:
            print_step(4, "Server started successfully", "success")
            
            server_info = f"""PID:       {Colors.GREEN}{process.pid}{Colors.RESET}
URL:       {Colors.CYAN}http://localhost:{args.port}{Colors.RESET}
Model:     {Colors.YELLOW}{os.path.basename(args.model)}{Colors.RESET}
Format:    {format_display}"""

            if model_info:
                server_info += f"""
Parameters: {Colors.PURPLE}{model_info.get('total_parameters', 'N/A'):,}{Colors.RESET}
Layers:     {Colors.BLUE}{model_info.get('num_layers', 'N/A')}{Colors.RESET}"""

            print_box("> Background Server Started", server_info, Colors.GREEN)
            
            print(f"\n{Colors.BOLD}{chars.MEMO} Management Commands:{Colors.RESET}")
            print(f"  {Colors.CYAN}wdlc status{Colors.RESET}           List all running servers")
            print(f"  {Colors.CYAN}wdlc stop {args.port}{Colors.RESET}           Stop this server")
            print(f"  {Colors.CYAN}wdlc stop --all{Colors.RESET}       Stop all servers")
            
        else:
            stdout_log.close()
            stderr_log.close()
            print_box("✗ Error", "Failed to start server in background", Colors.RED)
    else:
        if not args.foreground:
            print_step(3, f"Initializing server on port {Colors.YELLOW}{args.port}{Colors.RESET}...", "loading")
            print_server_banner(args.port, args.model, format_display, model_info)
            
            def handler(sig, frame):
             raise KeyboardInterrupt
            signal.signal(signal.SIGINT, handler)
            
        try:
            current_pid = os.getpid()
            save_server_info(args.port, current_pid, args.model, format_type)
            wdlc = WDLC(None, None)
            if os.path.isfile(args.model) and args.model.endswith('.wdlc'):
                wdlc.set_output_format("binary")
            else:
                wdlc.set_output_format("dir")
            
            deploy(args.model, args.port)
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}{chars.STOP} Server stopped by user{Colors.RESET}")
            cleanup_server_files(args.port)
            if chars.WAVE:
                print(f"{Colors.DIM}Thank you for using WDLC! {chars.WAVE}{Colors.RESET}")
            else:
                print(f"{Colors.DIM}Thank you for using WDLC!{Colors.RESET}")
        finally:
            cleanup_server_files(args.port)

def cmd_status(args):
    """Show status of running servers"""
    print_header("WDLC Server Status", "Running servers overview")
    
    servers = list_running_servers()
    
    if not servers:
        print_box("ℹ Info", "No WDLC servers are currently running", Colors.BLUE)
        print(f"\n{Colors.DIM}Use {Colors.CYAN}wdlc serve <model>{Colors.RESET}{Colors.DIM} to start a server{Colors.RESET}")
        return
    
    print_step(1, f"Found {Colors.GREEN}{len(servers)}{Colors.RESET} running server(s)")
    
    for i, server in enumerate(servers, 1):
        uptime = time.time() - server['started_at']
        uptime_str = f"{int(uptime // 60)}m {int(uptime % 60)}s"
        
        model_name = os.path.basename(server['model_path'])
        
        server_info = f"""PID:       {Colors.GREEN}{server['pid']}{Colors.RESET}
Port:      {Colors.YELLOW}{server['port']}{Colors.RESET}
URL:       {Colors.CYAN}{server['url']}{Colors.RESET}
Model:     {Colors.BLUE}{model_name}{Colors.RESET}
Format:    {server['format_type']}
Uptime:    {Colors.DIM}{uptime_str}{Colors.RESET}
Path:      {Colors.DIM}{server['model_path']}{Colors.RESET}"""
        
        print_box(f"> Server #{i}", server_info, Colors.GREEN)
    
    print(f"\n{Colors.BOLD}{chars.MEMO} Management Commands:{Colors.RESET}")
    print(f"  {Colors.CYAN}wdlc stop <port>{Colors.RESET}     Stop specific server")
    print(f"  {Colors.CYAN}wdlc stop --all{Colors.RESET}      Stop all servers")

def cmd_stop(args):
    """Stop running servers"""
    print_header("WDLC Server Management", "Stop running servers")
    
    if args.all:
        servers = list_running_servers()
        if not servers:
            print_box("ℹ Info", "No servers are currently running", Colors.BLUE)
            return
        
        print_step(1, f"Stopping {Colors.YELLOW}{len(servers)}{Colors.RESET} server(s)...", "loading")
        
        stopped_count = 0
        for server in servers:
            success, message = stop_server(server['port'])
            if success:
                stopped_count += 1
                print_detail(f"Port {server['port']}", f"{Colors.GREEN}Stopped{Colors.RESET}")
            else:
                print_detail(f"Port {server['port']}", f"{Colors.RED}Failed: {message}{Colors.RESET}")
        
        if stopped_count == len(servers):
            print_step(2, f"All servers stopped successfully", "success")
        else:
            print_step(2, f"Stopped {stopped_count}/{len(servers)} servers", "warning")
            
    elif args.port:
        print_step(1, f"Stopping server on port {Colors.YELLOW}{args.port}{Colors.RESET}...", "loading")
        
        success, message = stop_server(args.port)
        if success:
            print_step(2, message, "success")
            print_box("✓ Success", f"Server on port {args.port} has been stopped", Colors.GREEN)
        else:
            print_step(2, message, "error")
            print_box("✗ Error", f"Failed to stop server on port {args.port}: {message}", Colors.RED)
    else:
        print_box("✗ Error", "Please specify --port <port> or --all", Colors.RED)

def print_help():
    """Print a redesigned help screen using print_header and print_box."""

    header = f"{Colors.CYAN}{Colors.BOLD}WDLC - WebGPU Deep Learning Compiler{Colors.RESET}"

    print(header)

    # Combine usage and commands in one box
    usage_and_commands = (
        "wdlc [-h] {compile,inspect,serve,status,stop} ...\n\n"
        f"{Colors.BOLD}positional arguments:{Colors.RESET}\n"
        "  {compile,inspect,serve,status,stop}    Available commands\n\n"
        f"{Colors.BOLD}options:{Colors.RESET}\n"
        "  -h, --help            show this help message and exit\n\n"
        f"{Colors.BOLD}Commands:{Colors.RESET}\n"
        "  compile    - Compile PyTorch model to WDLC format (binary or folder)\n"
        "  inspect    - Inspect a compiled .wdlc model for structure\n"
        "  serve      - Serve a compiled model for development (foreground/background)\n"
        "  status     - Show running development servers\n"
        "  stop       - Stop running servers by port or all at once"
    )
    print_box("Usage & Commands", usage_and_commands, Colors.BLUE)



    
  





def main():
 
    header_title = f"{Colors.CYAN}{Colors.BOLD}WDLC - WebGPU Deep Learning Compiler{Colors.RESET}"
    header_desc = f"{Colors.DIM}Compile PyTorch models for efficient WebGPU inference{Colors.RESET}"
 
    class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
        def _format_usage(self, usage, actions, groups, prefix):
            if prefix is None:
                prefix = f'{Colors.BOLD}Usage:{Colors.RESET} '
            return super()._format_usage(usage, actions, groups, prefix)

    parser = argparse.ArgumentParser(
        description=header_desc,
        formatter_class=CustomHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(
        dest='command', 
        help=f'{Colors.BOLD}Available commands{Colors.RESET}',
        metavar=f'{Colors.CYAN}{{compile,inspect,serve,status,stop}}{Colors.RESET}'
    )
    
    compile_parser = subparsers.add_parser(
        'compile', 
        help=f'{Colors.GREEN}{chars.WRENCH}{Colors.RESET} Compile PyTorch model to WDLC format',
        description=f"""
{Colors.BOLD}Compile PyTorch Models{Colors.RESET}

Convert PyTorch neural networks into optimized WebGPU-ready formats.
Supports both single-file binary format and traditional folder structure.

{Colors.BOLD}Format Options:{Colors.RESET}
  {Colors.PURPLE}Binary (.wdlc):{Colors.RESET}  Single compressed file, easy deployment
  {Colors.BLUE}Folder:{Colors.RESET}          Traditional structure with separate weight files
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    compile_parser.add_argument('script', help=f'{Colors.CYAN}Python script{Colors.RESET} containing PyTorch model')
    
    format_group = compile_parser.add_mutually_exclusive_group()
    format_group.add_argument('--binary', nargs='?', const=True, metavar='PATH', help=f'{Colors.PURPLE}Compile to binary format{Colors.RESET} (.wdlc file). If no PATH is provided, defaults to model.wdlc')
    format_group.add_argument('--folder', metavar='PATH', help=f'{Colors.BLUE}Compile to folder format{Colors.RESET}')
    
    compile_parser.add_argument('--serve', action='store_true', help=f'{Colors.GREEN}Start server{Colors.RESET} after compilation')
    compile_parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    
    inspect_parser = subparsers.add_parser(
        'inspect', 
        help=f'{Colors.YELLOW}{chars.MAG}{Colors.RESET} Inspect compiled WDLC model',
        description=f"""
{Colors.BOLD}Model Inspector{Colors.RESET}

Analyze compiled WDLC models to understand their structure, parameters.

{Colors.BOLD}Features:{Colors.RESET}
  • Model architecture visualization
  • Parameter counting and analysis   
  • Compression statistics
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    inspect_parser.add_argument('model', help=f'{Colors.CYAN}Path to .wdlc file{Colors.RESET}')
    
    
    serve_parser = subparsers.add_parser(
        'serve', 
        help=f'{Colors.BLUE}>{Colors.RESET} Serve compiled WDLC model',
        description=f"""
{Colors.BOLD}Development Server{Colors.RESET}

Launch HTTP server to serve your compiled models for
web development and testing. Supports working on foreground and background modes.

{Colors.BOLD}Server Features:{Colors.RESET}
  • CORS enabled for cross-origin requests
  • Automatic format detection
  • Background process management
  • Model information display
  • Usage examples in browser console
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    serve_parser.add_argument('model', help=f'{Colors.CYAN}Path to model{Colors.RESET} (.wdlc file or directory)')
    serve_parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    serve_parser.add_argument('--background', '-b', action='store_true', help=f'{Colors.GREEN}Run in background{Colors.RESET}')
    serve_parser.add_argument('--foreground', action='store_true', help=argparse.SUPPRESS)  
    
    
    status_parser = subparsers.add_parser(
        'status', 
        help=f'{Colors.CYAN}{chars.CHART}{Colors.RESET} Show running server status',
        description=f"""
{Colors.BOLD}Server Status{Colors.RESET}

Display information about all currently running WDLC development servers
including process IDs, ports, uptime, and model information.

{Colors.BOLD}Information Displayed:{Colors.RESET}
  • Process ID and port
  • Server URL and uptime  
  • Model path and format
  • Parameter count and layer info
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    stop_parser = subparsers.add_parser(
        'stop', 
        help=f'{Colors.RED}{chars.STOP}{Colors.RESET} Stop running servers',
        description=f"""
{Colors.BOLD}Server Management{Colors.RESET}

Stop running WDLC development servers by port number or stop all servers
at once. Performs graceful shutdown with fallback to force termination.

{Colors.BOLD}Stop Options:{Colors.RESET}
  • Stop specific server by port
  • Stop all running servers
  • Automatic cleanup of process files
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    stop_group = stop_parser.add_mutually_exclusive_group(required=True)
    stop_group.add_argument('--port', type=int, help=f'{Colors.YELLOW}Port{Colors.RESET} of server to stop')
    stop_group.add_argument('--all', action='store_true', help=f'{Colors.RED}Stop all{Colors.RESET} running servers')
    

    help_flags = ('-h', '--help', '-help')
    arg0 = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        sub_names = list(subparsers.choices.keys())
    except Exception:
        sub_names = []

    help_index = None
    for i, tok in enumerate(sys.argv[1:], start=1):
        if tok in help_flags:
            help_index = i
            break

    if help_index == 1 and len(sys.argv) > 2 and sys.argv[2] in sub_names:
        sub = sys.argv[2]
        subparser = subparsers.choices.get(sub)
        if subparser:
            orig_desc = getattr(subparser, 'description', None)
            orig_ep = getattr(subparser, 'epilog', None)
            try:
                subparser.description = None
                subparser.epilog = None
                sub_help = subparser.format_help()
            finally:
                subparser.description = orig_desc
                subparser.epilog = orig_ep

            print_box(f'Options — {sub}', sub_help, Colors.GRAY)
            return

    if arg0 and arg0.lower() == 'help' and len(sys.argv) > 2 and sys.argv[2] in sub_names:
        sub = sys.argv[2]
        subparser = subparsers.choices.get(sub)
        if subparser:
            orig_desc = getattr(subparser, 'description', None)
            orig_ep = getattr(subparser, 'epilog', None)
            try:
                subparser.description = None
                subparser.epilog = None
                sub_help = subparser.format_help()
            finally:
                subparser.description = orig_desc
                subparser.epilog = orig_ep

            print_box(f'Options — {sub}', sub_help, Colors.GRAY)
            return

    if help_index is not None and help_index > 1:
        pass
    elif any(f in sys.argv for f in help_flags) or (arg0 and arg0.lower() == 'help'):
        print_help()     
        parser.description = None
        parser.epilog = None
    

        return

    args = parser.parse_args()
    
    if not args.command:
        print_box(header_title, header_desc, Colors.CYAN)
        print(f"\n{Colors.RED}Error:{Colors.RESET} No command specified")
        print(f"{Colors.DIM}Use {Colors.CYAN}wdlc --help{Colors.RESET}{Colors.DIM} for usage information{Colors.RESET}")
        return
    
    
    try:
        if args.command == 'compile':
            cmd_compile(args)
        elif args.command == 'inspect':
            cmd_inspect(args)
        elif args.command == 'serve':
            if hasattr(args, 'foreground') and args.foreground:
                args.background = False
            cmd_serve(args)
        elif args.command == 'status':
            cmd_status(args)
        elif args.command == 'stop':
            cmd_stop(args)
        elif args.command == 'help':
            print_help()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠{Colors.RESET} {Colors.BOLD}Interrupted by user{Colors.RESET}")
        if chars.WAVE:
            print(f"{Colors.DIM}Goodbye! {chars.WAVE}{Colors.RESET}")
        else:
            print(f"{Colors.DIM}Goodbye!{Colors.RESET}")
    except Exception as e:
        print_box("✗ Fatal Error", str(e), Colors.RED)
        print(f"{Colors.DIM}If this error persists, please report it at: https://github.com/wdlc-ai/wdlc/issues{Colors.RESET}")
        sys.exit(1)

if __name__ == '__main__':
    main()