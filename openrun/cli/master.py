import sys
import os
import platform
import subprocess

def get_system_ram():
    """
    Returns total physical memory (RAM) in bytes, and free system memory if possible.
    Returns (total_ram, free_ram) as a tuple of ints.
    """
    total_ram = 8 * 1024 * 1024 * 1024 # fallback to 8GB
    free_ram = 4 * 1024 * 1024 * 1024  # fallback to 4GB
    
    try:
        system = platform.system()
        if system == "Windows":
            # Using ctypes MEMORYSTATUSEX is 100% robust and needs no subprocess!
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                total_ram = stat.ullTotalPhys
                free_ram = stat.ullAvailPhys
        elif system == "Linux":
            with open("/proc/meminfo", "r") as f:
                meminfo = f.read()
            for line in meminfo.splitlines():
                if "MemTotal" in line:
                    total_ram = int(line.split()[1]) * 1024
                elif "MemAvailable" in line:
                    free_ram = int(line.split()[1]) * 1024
        elif system == "Darwin":
            # macOS sysctl
            out = subprocess.check_output(["sysctl", "hw.memsize"]).decode().strip()
            total_ram = int(out.split(":")[1].strip())
            # For free ram we can run vm_stat as fallback
            try:
                vm_stat = subprocess.check_output(["vm_stat"]).decode().strip()
                page_size = 4096
                for line in vm_stat.splitlines():
                    if "page size of" in line:
                        page_size = int(line.split()[-2])
                    elif "Pages free:" in line:
                        free_ram = int(line.split()[-1].replace(".", "")) * page_size
            except Exception:
                free_ram = total_ram // 2
    except Exception:
        pass
        
    return total_ram, free_ram

def get_hardware_specs():
    """
    Analyzes system hardware (CPU, RAM, GPU/VRAM) and returns a formatted dictionary of specifications.
    """
    total_ram, free_ram = get_system_ram()
    cpu_cores = os.cpu_count() or 4
    
    specs = {
        "os": f"{platform.system()} {platform.release()}",
        "cpu_cores": cpu_cores,
        "total_ram": total_ram,
        "free_ram": free_ram,
        "gpu_available": False,
        "gpu_name": "None",
        "total_vram": 0,
        "free_vram": 0
    }
    
    # Try getting GPU VRAM via PyTorch
    try:
        import torch
        if torch.cuda.is_available():
            specs["gpu_available"] = True
            specs["gpu_name"] = torch.cuda.get_device_name(0)
            try:
                free_v, total_v = torch.cuda.mem_get_info(0)
                specs["total_vram"] = total_v
                specs["free_vram"] = free_v
            except Exception:
                # Fallback device properties
                props = torch.cuda.get_device_properties(0)
                specs["total_vram"] = props.total_memory
                specs["free_vram"] = props.total_memory # assume free for fallback
    except Exception:
        pass
        
    # If not detected by PyTorch, try calling nvidia-smi as a fallback!
    if not specs["gpu_available"]:
        try:
            import shutil
            if shutil.which("nvidia-smi"):
                out = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"], text=True).strip()
                parts = [p.strip() for p in out.split(",")]
                if len(parts) >= 3:
                    specs["gpu_available"] = True
                    specs["gpu_name"] = parts[0]
                    specs["total_vram"] = int(parts[1]) * 1024 * 1024
                    specs["free_vram"] = int(parts[2]) * 1024 * 1024
        except Exception:
            pass
            
    return specs

def run_master_analysis():
    """
    Analyzes system specifications, scores model compatibility, estimates execution performance (t/s),
    and displays a beautiful recommendation report in the terminal.
    """
    from openrun.models.registry import PREDEFINED_MODELS, load_dynamic_models
    
    # Configure console encoding
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
            
    # Try updating with dynamic catalog first
    try:
        load_dynamic_models()
    except Exception:
        pass
        
    print("\n\033[1;93m⚡ OpenRun System Hardware & Model Master Analyzer\033[0m")
    
    specs = get_hardware_specs()
    
    # 1. Print System Hardware Summary Dashboard
    print("\033[90m" + "━" * 95 + "\033[0m")
    print(f"\033[1m⚙️  SYSTEM SPECIFICATIONS DASHBOARD\033[0m")
    print(f"   • \033[1mOperating System:\033[0m  {specs['os']}")
    print(f"   • \033[1mProcessor Cores:\033[0m   {specs['cpu_cores']} logical threads")
    print(f"   • \033[1mSystem RAM:\033[0m        {specs['total_ram'] / (1024**3):.2f} GB Total  ({specs['free_ram'] / (1024**3):.2f} GB Free)")
    
    if specs["gpu_available"]:
        vram_total_gb = specs["total_vram"] / (1024**3)
        vram_free_gb = specs["free_vram"] / (1024**3)
        print(f"   • \033[1mGPU Acceleration:\033[0m \033[92mActive\033[0m")
        print(f"   • \033[1mGraphics Hardware:\033[0m \033[96m{specs['gpu_name']}\033[0m")
        print(f"   • \033[1mDedicated VRAM:\033[0m    \033[95m{vram_total_gb:.2f} GB Total\033[0m  ({vram_free_gb:.2f} GB Free)")
    else:
        print(f"   • \033[1mGPU Acceleration:\033[0m \033[91mUnavailable / CPU Only\033[0m")
        print(f"     \033[90mℹ Note: Models will run on CPU offloading, which is significantly slower.\033[0m")
        
    print("\033[90m" + "━" * 95 + "\033[0m")
    print(f"\033[1m🎯 MODEL COMPATIBILITY & PERFORMANCE SUGGESTIONS\033[0m\n")
    
    # Sort and score models
    optimal = []
    quantized = []
    suboptimal = []
    incompatible = []
    
    # Pre-calculated aliases to skip
    aliases = {"qwen", "deepseek", "phi", "mistral", "llama3", "llama70b", "gemma2:2b"}
    
    for key, info in PREDEFINED_MODELS.items():
        if key in aliases:
            continue
            
        task = info.get("task", "text")
        # Skip image generation models since their memory/speed scales very differently
        if task == "image":
            continue
            
        size_str = info.get("size", "N/A").upper()
        
        # Estimate parameter count in Billions
        params = 1.0 # fallback
        try:
            if "M" in size_str:
                params = float(size_str.replace("M", "").split()[0]) / 1000.0
            elif "B" in size_str:
                params = float(size_str.replace("B", "").split()[0])
        except Exception:
            pass
            
        # VRAM Requirements heuristics (in bytes)
        vram_16b = (params * 2.0 + 2.0) * (1024**3)
        vram_8b = (params * 1.1 + 1.5) * (1024**3)
        vram_4b = (params * 0.7 + 1.0) * (1024**3)
        
        speed_base = info.get("speed", "N/A")
        
        status = "incompatible"
        rec_cmd = ""
        est_speed = "N/A"
        
        if specs["gpu_available"]:
            free_vram = specs["free_vram"]
            # 1. Fits in 16-bit VRAM?
            if free_vram >= vram_16b:
                status = "optimal"
                est_speed = speed_base
                rec_cmd = f"openrun serve --model {key}"
            # 2. Fits in 8-bit VRAM?
            elif free_vram >= vram_8b:
                status = "quantized"
                est_speed = speed_base
                rec_cmd = f"openrun serve --model {key} --quantize 8bit"
            # 3. Fits in 4-bit VRAM?
            elif free_vram >= vram_4b:
                status = "quantized"
                est_speed = speed_base
                rec_cmd = f"openrun serve --model {key} --quantize 4bit"
            # 4. Exceeds VRAM, but fits in System RAM?
            elif specs["free_ram"] >= vram_4b:
                status = "suboptimal"
                est_speed = "~3-8 t/s (CPU offloaded)"
                rec_cmd = f"openrun serve --model {key} --low-cpu-mem"
            else:
                status = "incompatible"
        else:
            # CPU Only
            # Fits in System RAM?
            if specs["free_ram"] >= vram_4b:
                status = "suboptimal"
                # Estimate CPU token speeds
                if params <= 0.5:
                    est_speed = "~25-45 t/s"
                elif params <= 1.5:
                    est_speed = "~12-20 t/s"
                elif params <= 4.0:
                    est_speed = "~5-10 t/s"
                else:
                    est_speed = "~2-5 t/s"
                rec_cmd = f"openrun serve --model {key} --low-cpu-mem"
            else:
                status = "incompatible"
                
        row = {
            "key": key,
            "engine": info.get("engine", "transformers"),
            "size": info.get("size", "N/A"),
            "speed": est_speed,
            "rec_cmd": rec_cmd,
            "best_for": info.get("best_for", "N/A")
        }
        
        if status == "optimal":
            optimal.append(row)
        elif status == "quantized":
            quantized.append(row)
        elif status == "suboptimal":
            suboptimal.append(row)
        else:
            incompatible.append(row)
            
    # Print Compatibility Lists
    # Category 1: Optimal (Green)
    if optimal:
        print(f"\033[1;92m🟢 OPTIMAL PERFORMANCE (Runs fully accelerated on GPU)\033[0m")
        print("\033[90m" + "─" * 95 + "\033[0m")
        for r in optimal:
            print(f"  • \033[1m{r['key'].ljust(22)}\033[0m ({r['size'].rjust(6)}) │ \033[95mSpeed:\033[0m {r['speed'].ljust(12)} │ \033[90mCommand:\033[0m \033[94m{r['rec_cmd']}\033[0m")
        print()
        
    # Category 2: Quantized Optimal (Yellow)
    if quantized:
        print(f"\033[1;93m🟡 ACCELERATED WITH QUANTIZATION (Fits VRAM via 4-bit / 8-bit mode)\033[0m")
        print("\033[90m" + "─" * 95 + "\033[0m")
        for r in quantized:
            print(f"  • \033[1m{r['key'].ljust(22)}\033[0m ({r['size'].rjust(6)}) │ \033[95mSpeed:\033[0m {r['speed'].ljust(12)} │ \033[90mCommand:\033[0m \033[94m{r['rec_cmd']}\033[0m")
        print()
        
    # Category 3: Sub-optimal CPU Offload (Orange)
    if suboptimal:
        print(f"\033[1;38;5;208m🟠 CPU ONLY / PARTIAL OFFLOAD (Runs slower on CPU / System memory)\033[0m")
        print("\033[90m" + "─" * 95 + "\033[0m")
        for r in suboptimal:
            print(f"  • \033[1m{r['key'].ljust(22)}\033[0m ({r['size'].rjust(6)}) │ \033[95mSpeed:\033[0m {r['speed'].ljust(22)} │ \033[90mCommand:\033[0m \033[94m{r['rec_cmd']}\033[0m")
        print()
        
    # Category 4: Incompatible (Red)
    if incompatible:
        print(f"\033[1;91m🔴 INSUFFICIENT SYSTEM MEMORY (Exceeds combined hardware boundaries)\033[0m")
        print("\033[90m" + "─" * 95 + "\033[0m")
        print(f"  • Models: {', '.join([r['key'] for r in incompatible[:6]])}" + (f", and {len(incompatible)-6} others..." if len(incompatible) > 6 else "."))
        print("  \033[90mℹ Suggestion: Increase system RAM or upgrade GPU VRAM specs to run these models.\033[0m\n")
        
    print("\033[1m💡 Execution Tip:\033[0m")
    print("   To launch any recommended model, copy the blue command listed above and execute it in your terminal.\n")
