import os
import sys
import sysconfig

def check_and_add_windows_path():
    """
    Checks if the directory containing openrun.exe is in the PATH environment variable on Windows.
    If it is not, it attempts to add it to the User's Environment variables in the registry.
    """
    if os.name != "nt":
        return

    # Get user and global scripts directories
    user_scripts = sysconfig.get_path('scripts', 'nt_user')
    global_scripts = sysconfig.get_path('scripts')

    target_dir = None
    for directory in [user_scripts, global_scripts]:
        if not directory:
            continue
        exe_path = os.path.join(directory, "openrun.exe")
        if os.path.exists(exe_path):
            target_dir = directory
            break

    # Fallback: if we can't find openrun.exe but are running inside the site-packages
    if not target_dir:
        # Let's see if one of the standard scripts paths exists
        if user_scripts and os.path.exists(user_scripts):
            target_dir = user_scripts
        elif global_scripts and os.path.exists(global_scripts):
            target_dir = global_scripts

    if not target_dir:
        return

    # Check if target_dir is in the current session's PATH
    current_path = os.environ.get("PATH", "")
    paths = [p.strip().rstrip("\\").lower() for p in current_path.split(";")]
    norm_target = target_dir.rstrip("\\").lower()

    if norm_target in paths:
        return

    # The directory is not in the current session's PATH. Let's try registry setup.
    try:
        import winreg
        
        # Open HKEY_CURRENT_USER\Environment
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                reg_path, reg_type = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                reg_path = ""
                reg_type = winreg.REG_EXPAND_SZ

            reg_paths = [p.strip().rstrip("\\").lower() for p in reg_path.split(";")]
            
            if norm_target not in reg_paths:
                # Append to existing registry path
                if reg_path:
                    new_path = reg_path.rstrip(";") + ";" + target_dir
                else:
                    new_path = target_dir

                winreg.SetValueEx(key, "Path", 0, reg_type, new_path)
                
                print("\n\033[92m[SUCCESS] OpenRun CLI configured automatically!\033[0m")
                print(f"\033[96m➤ Added scripts path to your User Environment Variables:\033[0m")
                print(f"  \033[90m{target_dir}\033[0m")
                print("\033[93m🚀 Please restart your terminal/editor to use the 'openrun' command directly.\033[0m\n")
            else:
                # It is already in the registry, but the current shell has a stale PATH
                print("\n\033[93m[INFO] OpenRun CLI is already in your Windows Environment Path.\033[0m")
                print("\033[96m🚀 Simply close and restart your terminal/editor to enable the 'openrun' command.\033[0m\n")
    except Exception:
        # Gracefully print a manual fallback instruction if registry access fails
        print("\n\033[93m[TIP] To run OpenRun directly, add this folder to your PATH environment variable:\033[0m")
        print(f"  \033[96m{target_dir}\033[0m\n")
