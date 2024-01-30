import requests
import concurrent.futures
import os
import psutil
import time
import argparse

class APKDownloader:
    def __init__(self, api_key, concurrent_downloads, tool_directory):
        self.api_key = api_key
        self.concurrent_downloads = concurrent_downloads
        self.tool_directory = tool_directory
        self.session = requests.Session()  # Now use a session for multiple requests
        self.create_lists()
        self.malware_len = 0
        self.benign_len = 0
        self.last_update_time = time.time()  # Added initialization
        self.load_lengths()
        

    def create_lists(self):

        if not os.path.exists(os.path.join(self.tool_directory, 'benign_apk_list.txt')):
            with open(os.path.join(self.tool_directory, 'benign_apk_list.txt'), 'w') as file:
                pass
        if not os.path.exists(os.path.join(self.tool_directory, 'malware_apk_list.txt')):
            with open(os.path.join(self.tool_directory, 'malware_apk_list.txt'), 'w') as file:
                pass
                
        self.benign_sha256_list = self.read_sha256_from_file(os.path.join(self.tool_directory, 'benign.txt'))
        self.malware_sha256_list = self.read_sha256_from_file(os.path.join(self.tool_directory, 'viruses.txt'))
        self.benign_list_path = self.read_sha256_from_file(os.path.join(self.tool_directory, 'benign_apk_list.txt'))
        self.malware_list_path = self.read_sha256_from_file(os.path.join(self.tool_directory, 'malware_apk_list.txt'))

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def check_disk_space(self):
        disk = psutil.disk_usage('/')
        available_space_gb = disk.free / (2 ** 30)  # Convert bytes to GB
        return available_space_gb

    def load_lengths(self):
        self.benign_len = len(self.benign_sha256_list)
        self.malware_len = len(self.malware_sha256_list)

    def calculate_progress(self, list_path, file_type):
        current_time = time.time()
        time_diff = current_time - self.last_update_time

        if time_diff >= 60:  # 5 minutes in seconds
            self.last_update_time = current_time

            if file_type == 'benign':
                progress = (len(list_path) / self.benign_len) * 100
            elif file_type == "malware":
                progress = (len(list_path) / self.malware_len) * 100

            return progress

        return None

    def download_apk(self, sha256, file_type):
        url = "https://androzoo.uni.lu/api/download"

        if file_type == 'benign':
            download_path = os.path.join(self.tool_directory, 'benign', 'benign_')
            list_path = self.benign_list_path
        elif file_type == 'malware':
            download_path = os.path.join(self.tool_directory, 'malware', 'malware_')
            list_path = self.malware_list_path
        else:
            raise ValueError("Invalid file_type provided")

        available_space_gb = self.check_disk_space()
        if available_space_gb < 5:
            print("Waiting for more disk space...")
            while available_space_gb < 10:
                print("Waiting for more disk space...")
                time.sleep(300)
                available_space_gb = self.check_disk_space()

        if sha256 in list_path:
            print(f"This file has already been downloaded for SHA256: {sha256}")

        progress = self.calculate_progress(list_path, file_type)

        if progress is not None and self.progress_callback:
            self.progress_callback(progress)

       
        params = {
            "apikey": self.api_key,
            "sha256": sha256
        }

        try:
            response = requests.get(url, params=params, stream=True)
            response.raise_for_status()

            with open(f"{download_path}{sha256}.apk", 'wb') as apk_file:
                for chunk in response.iter_content(chunk_size=8192):
                    apk_file.write(chunk)

            print(f"Downloaded APK for SHA256: {sha256}")
            with open(list_path, 'a') as list_file:
                list_file.write(f"{sha256}\n")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading APK for SHA256 {sha256}: {e}")
    
    def read_sha256_from_file(self, file_path):
        with open(file_path, 'r') as file:
            sha256_list = []
            for line in file:
                if "SHA256" in line:
                    sha256 = line.split(":")[1].split(',')[0].strip().strip('')
                    sha256_list.append(sha256)
                elif "SIZE" in line:
                    size = line.split(":")[1].strip()
                    print(f"Size for the current SHA256: {size}")  # You can use or store the size as needed
            sha256_list = [item.replace("'", "") for item in sha256_list]

        return sha256_list

    def run(self, malicious=False, benign=True):
        if benign:
            sha256_list = self.benign_sha256_list
            file_type = 'benign'
        elif malicious:
            sha256_list = self.malware_sha256_list
            file_type = 'malware'
        else:
            print("Please provide either '--benign' or '--malware' argument.")
            exit()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrent_downloads) as executor:
            executor.map(self.download_apk, sha256_list, [file_type] * len(sha256_list))

