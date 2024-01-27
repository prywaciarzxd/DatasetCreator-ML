import argparse
import csv
import os
from time import sleep

class VirusFinder:

    def __init__(self, input_csv, viruses_txt, benign_txt):
        self.input_csv = input_csv
        self.viruses_txt = viruses_txt
        self.benign_txt = benign_txt
        self.total_rows = 25000000 #too long to count number of rows every single time
        self.processed_rows = 0
        self.progress_callback = None

    def set_progress_callback(self, callback):
        self.progress_callback = callback
    
    def find_viruses(self):
        with open(self.input_csv, 'r', newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)    
            for row in csv_reader:
                vt_detection_value = row['vt_detection']
                if vt_detection_value and int(vt_detection_value) > 15:
                    self.processed_rows += 1
                    temp_dict = {'SHA256': row["sha256"], 'SIZE': row["dex_size"]}
                    with open(self.viruses_txt, 'a') as f:
                        f.write(f'{temp_dict}\n')
                elif vt_detection_value and int(vt_detection_value) == 0:
                    self.processed_rows += 1
                    temp_ben_dict = {'SHA256': row["sha256"], 'SIZE': row["dex_size"]}
                    with open(self.benign_txt, 'a') as f:
                        f.write(f'{temp_ben_dict}\n')
                progress_percentage = (self.processed_rows / self.total_rows) * 100
                if self.progress_callback:
                    self.progress_callback(progress_percentage)

def parse_arguments_1():
    parser = argparse.ArgumentParser(description='Find viruses in a CSV file.')
    
    default_input_csv = os.path.join(os.path.expanduser('~'),'DatasetCreator-ML','latest.csv') #Adjust here
    default_viruses_txt = os.path.join(os.path.expanduser('~'),'DatasetCreator-ML','viruses.txt') #Adjust here
    default_benign_txt = os.path.join(os.path.expanduser('~'),'DatasetCreator-ML','benign.txt')

    parser.add_argument('--input_csv', type=str, default=default_input_csv,
                        help=f'Path to the input CSV file, default={default_input_csv}')
    parser.add_argument('--viruses_txt', type=str, default=default_viruses_txt,
                        help=f'Path to the output text file, default={default_viruses_txt}')
    parser.add_argument('--benign_txt', type=str, default=default_benign_txt,
                        help=f'Path to the output text file, default={default_benign_txt}')
    
    if not os.path.exists(default_viruses_txt):
        with open(default_viruses_txt, 'w') as file:
            pass
    if not os.path.exists(default_benign_txt):
        with open(default_benign_txt, 'w') as file:
            pass

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments_1()
    virus_finder = VirusFinder(args.input_csv, args.viruses_txt, args.benign_txt)
    virus_finder.find_viruses()
    