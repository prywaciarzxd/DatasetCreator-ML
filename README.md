DatasetCreator-ML

This repository contains scripts designed to create datasets using AndroZoo in conjunction with machine learning algorithms.
Installation Guide

    Clone the repository:

    bash

git clone https://github.com/prywaciarzxd/DatasetCreator-ML.git

Navigate to the cloned directory:

bash

cd DatasetCreator-ML

Execute script to find viruses and generate a CSV file:

css

python find_viruses_csv.py --input_csv --output_txt

Download APKs using the generated text file list:

python download_apks.py

Run a script to check and execute the decompiling process:

python check_script.py

Extract features such as permissions and intents:

    python extract_features

Module Explanation

    find_viruses_csv.py: Searches for files with a score higher than 25, classified as malware. You can adjust it to find benign files.
    download_apks.py: Downloads files from a text file list.
    check_script.py: Executes the decompiling script.
    extract_features: Extracts permissions and intents from APK files.

Customization Notes

    In download_apks.py, you can modify the number of files being downloaded to a maximum of 20 per user.
    In thebest.py, you can adjust the number of threats used for the decompiling process.
