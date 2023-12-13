import requests
import concurrent.futures
import re
import time
import psutil
import argparse
import os

API_KEY = ""   # Put your API key in here
CONCURRENT_DOWNLOADS = 12 #Max concurrent downloads == 20
home_directory = os.path.expanduser("~")
tool_directory = "Desktop/dataset_create_tool"


def check_disk_space():
    disk = psutil.disk_usage('/')
    available_space_gb = disk.free / (2**30)  # Convert bytes to GB
    return available_space_gb

def check_apk(file_path, file_type):

    with open(file_path, 'r') as file:
        content = file.read()
        
    if file_type == 'malware':
        sha256_list = re.findall(r"malware_([A-Fa-f0-9]{64})\.apk", content)
    elif file_type == 'benign':
        sha256_list = re.findall(r"benign_([A-Fa-f0-9]{64})\.apk", content)
    else:
        raise ValueError("Invalid file_type provided")

    return sha256_list
       
def download_apk(sha256, file_type):
    
   
    url = "https://androzoo.uni.lu/api/download"
    
    if file_type == 'benign':
        file_list_path = os.path.join(home_directory, tool_directory, 'text_csv_files', 'benign_apk_list.txt')
        download_path = os.path.join(home_directory, tool_directory, 'benign', 'benign_')
       
    elif file_type == 'malware':
        file_list_path = os.path.join(home_directory, tool_directory, 'text_csv_files', 'malware_apk_list.txt')
        download_path = os.path.join(home_directory, tool_directory, 'malware', 'malware_')
        
    else:
        raise ValueError("Invalid file_type provided")
    
    available_space_gb = check_disk_space()
    if available_space_gb < 5:  
        print("Waiting for more disk space...")
        while available_space_gb < 10:  
            print("Waiting for more disk space...")
            time.sleep(300)  
            available_space_gb = check_disk_space()
    
    already_downloaded = check_apk(file_list_path, file_type)
    if sha256 in already_downloaded:
        print(f"This file has already been downloaded for SHA256: {sha256}")
        return 0

    params = {
        "apikey": API_KEY,
        "sha256": sha256
    }

    try:
        response = requests.get(url, params=params, stream=True)
        response.raise_for_status()

        with open(f"{download_path}{sha256}.apk", 'wb') as apk_file:
            for chunk in response.iter_content(chunk_size=8192):
                apk_file.write(chunk)

        print(f"Downloaded APK for SHA256: {sha256}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading APK for SHA256 {sha256}: {e}")

def read_sha256_from_file(file_path):
    with open(file_path, 'r') as file:
        sha256_list = []
        for line in file:
            if "SHA256" in line:
                sha256 = line.split(":")[1].split(',')[0].strip()
                sha256_list.append(sha256)
            elif "SIZE" in line:
                size = line.split(":")[1].strip()
                print(f"Size for the current SHA256: {size}")  # You can use or store the size as needed
        return sha256_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download benign or malware APKs.')
    benign_file_path = os.path.join(home_directory, tool_directory, 'text_csv_files', 'random_benigns_2.txt')
    malware_file_path = os.path.join(home_directory, tool_directory, 'text_csv_files', 'random_viruses.txt')
    parser.add_argument('--benign', action='store_true', help='Download benign APKs')
    parser.add_argument('--malware', action='store_true', help='Download malware APKs')

    args = parser.parse_args()

    if args.benign:
        sha256_list = read_sha256_from_file(benign_file_path)
        file_type = 'benign'
    elif args.malware:
        sha256_list = read_sha256_from_file(malware_file_path)
        file_type = 'malware'
    else:
        print("Please provide either '--benign' or '--malware' argument.")
        exit()

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_DOWNLOADS) as executor:
        executor.map(download_apk, sha256_list, [file_type] * len(sha256_list))
