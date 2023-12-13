# DatasetCreator-ML
This repo contains scripts to create dataset using AndroZoo and machine learning algorithms.

Installation Guide.

1.git clone https://github.com/prywaciarzxd/DatasetCreator-ML.git
2.cd DatasetCreator-ML
3.python find_viruses_csv.py --input_csv --output_txt 
4.python download_apks.py
5.python check_script.py
6.python extract_features

Explaining every module.

find_viruses_csv.py - looks for files with score higher then 25, clasiffied as malware (U can adjust it to find benign files)
download_apks.py - downloads files from txt file list
check_script.py - executing decompyiling script 
extract_features - script to extract permissions and intents

In download_apks.py file u can change number of files being downloaded to up maximum 20 per user.
In thebest.py u can  change number of threats that are used for decompilying file.
