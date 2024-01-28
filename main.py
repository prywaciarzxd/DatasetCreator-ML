#!/usr/bin/env python3
import tkinter as tk
from tkinter import simpledialog, ttk
import argparse
import os
import subprocess
import sys
import time

from download_apks import APKDownloader
from find_viruses_csv import VirusFinder, parse_arguments_1
from decompile import *
from remove_decompiled_dirs import FolderManager
from extract_features import ManifestProcessor
from dnn import HyperparameterGridSearch

class PrepareApksGUI:

    def __init__(self, master):
        self.master = master
        master.title("DataSet Creator")
        
        window_width = 500
        window_height = 500
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        master.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.button_get_api_key = tk.Button(master, text="Enter your api key", command=self.enter_api_key)
        self.button_get_api_key.pack(pady=10)

        self.button_find_files = tk.Button(master, text="Find specific files from CSV", command=self.find_files)
        self.button_find_files.pack(pady=10)

        self.button_download = tk.Button(master, text="Download files", command=self.ask_download_type)
        self.button_download.pack(pady=10)

        self.button_downloads_number = tk.Button(master, text="Change number of downloads", command=self.change_workers)
        self.button_downloads_number.pack(pady=10)

        self.button_decompile = tk.Button(master, text="Decompile APK files", command=self.ask_dir_decompile)
        self.button_decompile.pack(pady=10)

        self.button_remove_dirs = tk.Button(master, text="Remove decompiled dirs", command=self.remove_dirs)
        self.button_remove_dirs.pack(pady=10)

        self.button_extract = tk.Button(master, text="Extract static features", command=self.extract_features)
        self.button_extract.pack(pady=10)

        self.button_dnn_model = tk.Button(master, text="Build DNN model", command=self.dnn)
        self.button_dnn_model.pack(pady=10)

        self.button_quit = tk.Button(master, text="Quit", command=master.quit)
        self.button_quit.pack(pady=10)

        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.concurrent_downloads = 1
    
    def remove_dirs(self):
        removing_dir = simpledialog.askstring("Directory to delete decompiled folders", "Enter benign or malware: ", parent=self.master)
        if removing_dir:
            folder_manager = FolderManager(base_path=f'/root/DatasetCreator-ML/{removing_dir}')
            folder_manager.delete_unused_decompiled_folders()
        self.show_notification(f'Decompiled dirs has been removed!')

    def enter_api_key(self):
        api_key = simpledialog.askstring("API KEY", "Enter correct api key:", parent=self.master)

        os.environ["ZooDataSet"] = api_key

        self.show_notification(f"Your env variable has been set: {os.environ['ZooDataSet']}")
    
    def dnn(self):
        dataset_path = simpledialog.askstring("DataSetPath", "Enter dataset absolute path", parent=self.master)
        dnn_model = HyperparameterGridSearch(
            data_path=dataset_path,
            home_directory=os.path.expanduser("~"), 
            tool_directory="DatasetCreator-ML",
            results_file_path="dnn_results"
        )
        dnn_model.load_data()
        dnn_model.preprocess_data()

        optimizers = ['adam', 'sgd', 'rmsprop', 'adamax']
        batch_sizes = [16, 32, 64]
        epochs_values = [5, 10, 15]
        neuron_values = [32, 64, 128]

        dnn_model.search_hyperparameters(optimizers, batch_sizes, epochs_values, neuron_values)

    def change_workers(self):
        self.concurrent_downloads =  int(simpledialog.askstring("Concurrent downloads", "Enter int number (max 20):", parent=self.master))
        self.show_notification(f"Your concurrent downloads has been changed to {self.concurrent_downloads} !")
        
    def extract_features(self):
        dir_to_extract_features_from = simpledialog.askstring("Directory for features extraction", "Enter 'malicious' or 'benign':", parent=self.master)
        manifest_processor = ManifestProcessor(
            home_directory=os.path.expanduser("~"),
            tool_directory="DatasetCreator-ML",
            manifests_directory="manifests",
            extracted_csv='found_features_verified_all.csv',
            extraction_dir=dir_to_extract_features_from
        )

        manifest_processor.process_manifests()
        self.show_notification("Static features has been extracted!")

    def ask_download_type(self):
        download_type = simpledialog.askstring("Download Type", "Enter 'malicious' or 'benign':", parent=self.master)
        if download_type:
            self.download_files(download_type.lower())
    
    def ask_dir_decompile(self):
        decompile_dir = simpledialog.askstring("Directory to decompile", "Enter benign or malware: ", parent=self.master)
        if decompile_dir:
            self.decompile_apks(decompile_dir.lower())
    

    def download_files(self, download_type):

        apk_downloader = APKDownloader(
            api_key=os.environ['ZooDataSet'],
            concurrent_downloads=self.concurrent_downloads,
            home_directory=os.path.expanduser("~"),
            tool_directory="DatasetCreator-ML"
        )

        def update_progress(progress):
            print(f"Progress: {progress:.2f}%")
            if progress % 5 == 0:
                self.progress_bar["value"] = progress
                self.master.update_idletasks()
        
        apk_downloader.set_progress_callback(update_progress)

        if download_type == 'malicious':
            apk_downloader.run(malicious=True, benign=False)
        elif download_type == 'benign':
            apk_downloader.run()
        else:
            print("Invalid download_type. Please enter 'malicious' or 'benign'.")
            return

        self.progress_bar.stop()
        self.progress_bar.destroy()

    def find_files(self):
        args = parse_arguments_1()
        virus_finder = VirusFinder(args.input_csv, args.viruses_txt, args.benign_txt)

        def update_progress(progress):
            print(f"Progress: {progress:.2f}%")
            if progress % 1 == 0:
                self.progress_bar["value"] = progress
                self.master.update_idletasks()

        virus_finder.set_progress_callback(update_progress)
        virus_finder.find_viruses()

        self.progress_bar.stop()
        self.progress_bar.destroy()

        self.show_notification(f'Viruses saved to: {args.output_viruses}\nBenign apps saved to: {args.output_benign_txt}')

    def show_notification(self, message):
        notification_window = tk.Toplevel(self.master)
        notification_window.title("Notification")

        notification_label = tk.Label(notification_window, text=message)
        notification_label.pack()

        window_width = notification_window.winfo_reqwidth()
        window_height = notification_window.winfo_reqheight()
        screen_width = notification_window.winfo_screenwidth()
        screen_height = notification_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        notification_window.geometry(f"+{x}+{y}")

        # Dodaj zamknięcie okna komunikatu po kliknięciu przycisku "OK"
        ok_button = tk.Button(notification_window, text="OK", command=notification_window.destroy)
        ok_button.pack(pady=10)


    def decompile_apks(self, decompile_dir):
        apk_processor = ApkProcessor(
        home_directory=os.path.expanduser("~"),
        tool_directory='DatasetCreator-ML',
        manifests_dir="manifests",
        decompile_dir=decompile_dir,
        decompiled_apks_list="decompiled_apks.txt"
    )
        apk_processor.process()
    

        
if __name__ == "__main__":
    root = tk.Tk()
    app = PrepareApksGUI(root)
    root.mainloop()
