import os
import subprocess
import shutil
import concurrent.futures

def decompile_apk(file_path, output_dir):
    try:
        subprocess.run(["apktool", "d", file_path, "-o", output_dir], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error decompiling APK {file_path}: {e}")
        return False

def move_manifest(apk_file, decompiled_dir, output_dir):
    manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
    if os.path.exists(manifest_path):
        new_manifest_path = os.path.join(output_dir, f"AndroidManifest_{apk_file}.xml")
        shutil.move(manifest_path, new_manifest_path)
        print(f"Moved AndroidManifest.xml for {apk_file} to {new_manifest_path}")

        

        # Usuń plik .apk
        apk_path = os.path.join("/home/kali/Desktop/dataset_create_tool/benign", apk_file)
        os.remove(apk_path)
        print(f"Removed APK file: {apk_file}")
       
    else:
        print(f"No AndroidManifest.xml found for {apk_file}")

def decompile_and_move(apk_file, malware_path, manifests_dir, output_txt):
    apk_path = os.path.join(malware_path, apk_file)
    decompiled_dir = os.path.join(malware_path, f"{apk_file}_decompiled")

    success = decompile_apk(apk_path, decompiled_dir)

    if success:
        move_manifest(apk_file, decompiled_dir, manifests_dir)
        
        with open(output_txt, 'a') as txt_file:
            txt_file.write(f"{apk_file}\n")

def process_apk(apk_file):
    malware_path = "/home/kali/Desktop/dataset_create_tool/benign"
    manifests_dir = "/home/kali/Desktop/dataset_create_tool/manifests"

    apk_path = os.path.join(malware_path, apk_file)
    decompiled_dir = os.path.join(malware_path, f"{apk_file}_decompiled")

    success = decompile_apk(apk_path, decompiled_dir)

    if success:
        move_manifest(apk_file, decompiled_dir, manifests_dir)

        output_txt = "/home/kali/Desktop/dataset_create_tool/text_csv_files/benign_apk_list.txt"
        with open(output_txt, 'a') as txt_file:
            txt_file.write(f"{apk_file}\n")

def main():
    malware_path = "/home/kali/Desktop/dataset_create_tool/benign"

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        apk_files = [f for f in os.listdir(malware_path) if f.endswith(".apk")]

        if not apk_files:
            print("No more APK files found. Exiting.")
            return

        executor.map(process_apk, apk_files)

        print("Processed APK files. Continuing the search.")

if __name__ == "__main__":
    main()
