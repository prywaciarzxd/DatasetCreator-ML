import os
import psutil
import shutil
import re
import time

class FolderManager:
    def __init__(self, home_directory, tool_directory, base_path):
        self.base_path = os.path.join(home_directory, tool_directory, base_path)
        self.users_choice = base_path

    def is_folder_in_use(self, folder_path):
        for proc in psutil.process_iter(['pid', 'open_files']):
            try:
                for file in proc.open_files():
                    if folder_path in file.path:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def delete_unused_decompiled_folders(self):
        for folder_name in os.listdir(self.base_path):
            if self.users_choice == "benign" and re.match(r'^benign_[\w\d]+\.apk_decompiled$', folder_name):
                folder_path = os.path.join(self.base_path, folder_name)
                if not self.is_folder_in_use(folder_path):
                    try:
                        shutil.rmtree(folder_path)
                        print(f"Removed folder: {folder_path}")
                    except Exception as e:
                        print(f"Error removing folder {folder_path}: {e}")
                else:
                    print(f"Folder {folder_path} is in use. Skipping removal.")
            elif self.users_choice == "malware" and re.match(r'^malware_[\w\d]+\.apk_decompiled$', folder_name):
                folder_path = os.path.join(self.base_path, folder_name)
                if not self.is_folder_in_use(folder_path):
                    try:
                        shutil.rmtree(folder_path)
                        print(f"Removed folder: {folder_path}")
                    except Exception as e:
                        print(f"Error removing folder {folder_path}: {e}")
                else:
                    print(f"Folder {folder_path} is in use. Skipping removal.")
if __name__ == "__main__":
    benign_path = "/root/DatasetCreator-ML/benign"
    folder_manager = FolderManager(benign_path)
    folder_manager.delete_unused_decompiled_folders()
    