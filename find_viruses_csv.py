import argparse
import csv
import os


def main(input_csv, output_txt):
    with open(input_csv, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            vt_detection_value = row['vt_detection']
            if vt_detection_value and int(vt_detection_value) > 25:
                temp_dict = {'SHA256': row["sha256"], 'SIZE': row["dex_size"]}
                with open(output_txt, 'a') as f:
                    f.write(f'{temp_dict}\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find viruses in a CSV file.')
    
    default_input_csv = os.path.join(os.path.expanduser('~'), 'Desktop', 'dataset_create_tool', 'text_csv_files', 'latest.csv') #Adjust here
    default_output_txt = os.path.join(os.path.expanduser('~'), 'Desktop', 'dataset_create_tool', 'text_csv_files', 'viruses.txt') #Adjust here
    
    parser.add_argument('--input_csv', type=str, default=default_input_csv,
                        help=f'Path to the input CSV file, default={default_input_csv}')
    parser.add_argument('--output_txt', type=str, default=default_output_txt,
                        help=f'Path to the output text file, default={default_output_txt}')
    
    args = parser.parse_args()
    main(args.input_csv, args.output_txt)

