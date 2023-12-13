import psutil
import subprocess
import os
import time

def check_and_run_python_script(script_path):
    script_basename = os.path.basename(script_path)
    
    while True:
        found = False

        # Sprawdzenie czy proces Pythona z podaną ścieżką jest uruchomiony
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
        
        time.sleep(60)  # Poczekaj 60 sekund przed ponownym sprawdzeniem

if __name__ == "__main__":
    script_path_to_check = '/home/kali/Desktop/dataset_create_tool/scripts/thebest.py'
    check_and_run_python_script(script_path_to_check)




