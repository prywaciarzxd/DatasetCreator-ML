import os
import subprocess
import shutil
import time

class ApkProcessor:
    def __init__(self, tool_directory, manifests_dir, decompile_dir, decompiled_apks_list):
        self.tool_directory = tool_directory
        self.manifests_dir = os.path.join(tool_directory, manifests_dir)
        self.decompile_dir = os.path.join(tool_directory, decompile_dir)
        self.decompiled_apks_list = os.path.join(tool_directory, decompiled_apks_list)
        
    
    def decompile_apk(self, apk_file, decompiled_dir):
        try:
            if os.path.exists(decompiled_dir):
                shutil.rmtree(decompiled_dir)
            subprocess.run(["apktool", "d", apk_file, "-o", decompiled_dir], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error decompiling APK {apk_file}: {e}")
            os.remove(apk_file)
            print(f"Removed APK file: {apk_file}")
            return False
    
    def move_manifests(self, apk_file, decompiled_dir, manifests_dir):
        manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
        if os.path.exists(manifest_path):
            new_manifest_path = os.path.join(manifests_dir, f"AndroidManifest_{apk_file}.xml")
            shutil.move(manifest_path, new_manifest_path)
            print(f"Moved AndroidManifest.xml for {apk_file} to {new_manifest_path}")

            apk_path = os.path.join(self.decompile_dir, apk_file)
            os.remove(apk_path)
            print(f"Removed APK file: {apk_file}")
       
        else:
            print(f"No AndroidManifest.xml found for {apk_file}")
        return 
    
    def process(self):
        os.makedirs(self.manifests_dir, exist_ok=True)

        while True:
            apk_files = [f for f in os.listdir(self.decompile_dir) if f.endswith(".apk")]

            if not apk_files:
                print("No more APK files found. Exiting.")
                break

            for apk_file in apk_files:
                apk_path = os.path.join(self.decompile_dir, apk_file)
                decompiled_dir = os.path.join(self.decompile_dir, f"{apk_file}_decompiled")

                success = self.decompile_apk(apk_path, decompiled_dir)

                if success:
                    self.move_manifests(apk_file, decompiled_dir, self.manifests_dir)
            
                    with open(self.decompiled_apks_list, 'a') as txt_file:
                        txt_file.write(f"{apk_file}\n")

            print("Processed APK files. Continuing the search.")

if __name__ == "__main__":
    apk_processor = ApkProcessor(
        home_directory=os.path.expanduser("~"),
        tool_directory='DatasetCreator-ML',
        manifests_dir="manifests",
        decompile_dir="benign",
        decompiled_apks_list="decompiled_apks.txt"
    )
    apk_processor.process()
