import requests
import concurrent.futures
import re
import time
import psutil
API_KEY = ""   # Put your API key in here
CONCURRENT_DOWNLOADS = 12 #Max concurrent downloads == 20

def check_disk_space():
    disk = psutil.disk_usage('/')
    available_space_gb = disk.free / (2**30)  # Convert bytes to GB
    return available_space_gb

def check_apk(file_path):

    with open(file_path, 'r') as file:
        content = file.read()
        
    sha256_list = re.findall(r"benign_([A-Fa-f0-9]{64})\.apk", content) #Change this when downloading malware/benign
    
    return sha256_list    

def download_apk(sha256):

    available_space_gb = check_disk_space()
    if available_space_gb < 5:  
        print("Waiting for more disk space...")
        while available_space_gb < 10:  
            print("Waiting for more disk space...")
            time.sleep(300)  
            available_space_gb = check_disk_space()
    
    already_downloaded = check_apk('/home/kali/Desktop/dataset_create_tool/text_csv_files/benign_apk_list.txt') #Change this when downloading malware/benign
    if sha256 in already_downloaded:
        print(f"This file has been already decompiled APK for SHA256: {sha256}")
        return 0
    url = "https://androzoo.uni.lu/api/download"
    params = {
        "apikey": API_KEY,
        "sha256": sha256
    }

    try:
        response = requests.get(url, params=params, stream=True)
        response.raise_for_status()

        with open(f"/home/kali/Desktop/dataset_create_tool/benign/benign_{sha256}.apk", 'wb') as apk_file: #Change this when downloading malware/benign
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
    file_path = "/home/kali/Desktop/dataset_create_tool/text_csv_files/random_benigns_2.txt" #Change this when downloading malware/benign
    sha256_list = read_sha256_from_file(file_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_DOWNLOADS) as executor:
        # Download APKs concurrently
        executor.map(download_apk, sha256_list)
