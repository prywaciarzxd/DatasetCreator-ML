import psutil
import subprocess
import os
import time
import argparse

def check_and_run_python_script(script_path):
    script_basename = os.path.basename(script_path)
    
    while True:
        found = False

        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'python':
                try:
                    cmdline = proc.cmdline()
                    if len(cmdline) >= 2 and os.path.basename(cmdline[1]) == script_basename:
                        found = True
                        print('The script is already running!')
                        break
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

        if not found:
            # Uruchomienie skryptu w nowym terminalu
            subprocess.Popen(['x-terminal-emulator', '-e', 'python', script_path])
        
        time.sleep(60) 

if __name__ == "__main__":
    home_dir = os.path.expanduser('~')
    tool_dir = "Desktop/dataset_create_tool/scripts"
    parser = argparse.ArgumentParser(description='Check and run Python script')
    parser.add_argument('script_name', nargs='?', default='thebest.py', type=str, help='Name of the Python script to check and run')

    args = parser.parse_args()
    script_path_to_check = os.path.join(home_dir, tool_dir, args.script_name)
    
    check_and_run_python_script(script_path_to_check)




