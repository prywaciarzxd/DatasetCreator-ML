import os
import psutil
import shutil
import re
import time

def is_folder_in_use(folder_path):
    for proc in psutil.process_iter(['pid', 'open_files']):
        try:
            for file in proc.open_files():
                if folder_path in file.path:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def delete_unused_decompiled_folders(base_path):
    for folder_name in os.listdir(base_path):
        if re.match(r'^benign_[\w\d]+\.apk_decompiled$', folder_name):
            folder_path = os.path.join(base_path, folder_name)
            if not is_folder_in_use(folder_path):
                try:
                    shutil.rmtree(folder_path)
                    print(f"Removed folder: {folder_path}")
                except Exception as e:
                    print(f"Error removing folder {folder_path}: {e}")
            else:
                print(f"Folder {folder_path} is in use. Skipping removal.")

if __name__ == "__main__":
    benign_path = "/home/kali/Desktop/dataset_create_tool/benign"
    start_time = time.time()

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > 60:  # Sprawdź, czy minęła minuta
            delete_unused_decompiled_folders(benign_path)
            start_time = time.time()  # Zresetuj czas rozpoczęcia
        time.sleep(10)
