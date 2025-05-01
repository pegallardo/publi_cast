import os
import sys
import subprocess
import time
import win32file
import pywintypes

def list_all_pipes():
    """List all named pipes in the system"""
    print("Listing all available named pipes...")
    
    try:
        cmd = "powershell -Command \"[System.IO.Directory]::GetFiles('\\\\.\\pipe\\') | ForEach-Object { $_.Substring(9) }\""
        result = subprocess.run(cmd, capture_output=True, text=True)
        pipes = result.stdout.strip().split('\n')
        print(f"Found {len(pipes)} pipes:")
        for pipe in pipes:
            print(f"  - {pipe}")
        return pipes
    except Exception as e:
        print(f"Error listing pipes: {e}")
        return []

def check_audacity_running():
    """Check if Audacity is running"""
    print("Checking if Audacity is running...")
    
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'audacity' in proc.info['name'].lower():
                    print(f"Audacity is running (PID: {proc.info['pid']})")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        print("Audacity is NOT running")
        return False
    except Exception as e:
        print(f"Error checking if Audacity is running: {e}")
        return False

def check_mod_script_pipe():
    """Check if mod-script-pipe is enabled in Audacity"""
    print("Checking if mod-script-pipe is enabled...")
    
    try:
        appdata = os.getenv('APPDATA')
        config_path = os.path.join(appdata, "audacity", "audacity.cfg")
        
        if os.path.exists(config_path):
            print(f"Found Audacity config file: {config_path}")
            with open(config_path, 'r') as f:
                for line in f:
                    if "mod-script-pipe" in line:
                        print(f"Found mod-script-pipe configuration: {line.strip()}")
                        if "enabled=1" in line:
                            print("mod-script-pipe is ENABLED")
                            return True
                        else:
                            print("mod-script-pipe is NOT enabled")
                            return False
            print("Could not find mod-script-pipe configuration in Audacity config file")
        else:
            print(f"Audacity config file not found at {config_path}")
        
        return False
    except Exception as e:
        print(f"Error checking if mod-script-pipe is enabled: {e}")
        return False

def try_connect_to_pipes():
    """Try to connect to Audacity pipes"""
    print("Trying to connect to Audacity pipes...")
    
    # Define possible pipe names
    pipe_names = [
        (r'\\.\pipe\ToSrvPipe', r'\\.\pipe\FromSrvPipe'),
        (r'\\.\pipe\audacity_script_pipe.to', r'\\.\pipe\audacity_script_pipe.from')
    ]
    
    # Add Windows 11 specific pipe names
    import getpass
    username = getpass.getuser()
    pipe_names.append((
        fr'\\.\pipe\audacity_script_pipe.to.{username}',
        fr'\\.\pipe\audacity_script_pipe.from.{username}'
    ))
    
    # Try each pipe pair
    for to_pipe, from_pipe in pipe_names:
        print(f"Trying pipe pair: {to_pipe}, {from_pipe}")
        
        # Check if pipes exist
        to_exists = os.path.exists(to_pipe)
        from_exists = os.path.exists(from_pipe)
        
        print(f"  To pipe exists: {to_exists}")
        print(f"  From pipe exists: {from_exists}")
        
        if to_exists and from_exists:
            try:
                print("  Attempting to connect to pipes...")
                pipe_in = win32file.CreateFile(
                    to_pipe,
                    win32file.GENERIC_WRITE,
                    0, None, win32file.OPEN_EXISTING, 0, None
                )
                pipe_out = win32file.CreateFile(
                    from_pipe,
                    win32file.GENERIC_READ,
                    0, None, win32file.OPEN_EXISTING, 0, None
                )
                
                print("  Successfully connected to pipes!")
                
                # Try to send a command
                print("  Sending test command to Audacity...")
                win32file.WriteFile(pipe_in, b'GetInfo: Type=Tracks\n')
                
                # Wait for response
                print("  Waiting for response...")
                time.sleep(1)
                
                # Read response
                result, data = win32file.ReadFile(pipe_out, 4096)
                if result == 0:
                    response = data.decode().strip()
                    print(f"  Received response: {response}")
                else:
                    print(f"  Error reading response: {result}")
                
                # Close pipes
                win32file.CloseHandle(pipe_in)
                win32file.CloseHandle(pipe_out)
                
                return True
            except pywintypes.error as e:
                print(f"  Error connecting to pipes: {e}")
    
    print("Failed to connect to any Audacity pipes")
    return False

def main():
    """Run diagnostic tests"""
    print("=== Audacity Pipe Diagnostic Tool ===")
    print()
    
    # Check if Audacity is running
    audacity_running = check_audacity_running()
    print()
    
    # Check if mod-script-pipe is enabled
    mod_script_pipe_enabled = check_mod_script_pipe()
    print()
    
    # List all pipes
    all_pipes = list_all_pipes()
    print()
    
    # Try to connect to pipes
    if audacity_running:
        connection_successful = try_connect_to_pipes()
    else:
        print("Skipping pipe connection test because Audacity is not running")
        connection_successful = False
    
    print()
    print("=== Diagnostic Summary ===")
    print(f"Audacity running: {'YES' if audacity_running else 'NO'}")
    print(f"mod-script-pipe enabled: {'YES' if mod_script_pipe_enabled else 'NO'}")
    print(f"Pipe connection successful: {'YES' if connection_successful else 'NO'}")
    
    if not audacity_running:
        print("\nRecommendation: Start Audacity and run this diagnostic again")
    elif not mod_script_pipe_enabled:
        print("\nRecommendation: Enable mod-script-pipe in Audacity preferences")
    elif not connection_successful:
        print("\nRecommendation: Try the following:")
        print("1. Restart Audacity after enabling mod-script-pipe")
        print("2. Run Audacity and this application with administrator privileges")
        print("3. Check if your antivirus or firewall is blocking pipe communication")
        print("4. Try using an older version of Audacity (some newer versions may have issues with pipes)")
    else:
        print("\nAll tests passed! Pipe communication with Audacity should work.")

if __name__ == "__main__":
    main()