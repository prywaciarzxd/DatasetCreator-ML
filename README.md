# Dataset Creator

## Prerequisites
Before running the program, make sure you have the following prerequisites:

1. **Latest CSV File**: Download the latest CSV file from [Androzoo](https://androzoo.uni.lu/lists) (e.g., `latest.csv`) and place it in the `/root/DatasetCreator-ML` directory.

2. **API Key from AndrozooDataset**: Obtain an API key from AndrozooDataset to enable downloading. You can get the API key [here](https://androzoo.uni.lu/documentation#section/Obtaining-the-API-key). Set the API key as an environment variable:

    ```bash
    export ZooDataSet=YOUR_API_KEY
    ```

3. **Java 8 and apktool**: To decompile apk files we use apktool which requires min java 8 installed.

4. **Python Libraries**: Scikit-learn, tensorflow.
   > Note: You can also set the API key in the GUI by clicking on "Enter your API key."

## Running the Program
1. Clone or place the entire project in the `/root/DatasetCreator-ML` directory.

    ```bash
    git clone https://github.com/YOUR_USERNAME/DatasetCreator-ML.git
    ```

2. Open the terminal and navigate to the project directory:

    ```bash
    cd /root/DatasetCreator-ML
    ```

3. Run the program using the following command:

    ```bash
    python main.py
    ```

4. Optionally, set the API key through the GUI by clicking on "Enter your API key."

## Optional Functionality
Enhance performance by utilizing the Command-Line Interface (CLI) version. This version enables faster execution through parallel downloading of APKs and decompilation. Access the CLI version [here](https://github.com/prywaciarzxd/DataSetCreator-ML-CLI).

## Program Functions

### `find_specific_files_from_csv`
This function allows you to create files containing viruses or applications, depending on your preferences. It processes the CSV file and extracts the specified files.

### `download_files`
Initiates the downloading process based on the created lists. Specify whether you want to download malicious or benign applications.

### `change_number_of_downloads`
Change the number of parallel downloads to control the download speed and system resource utilization.

### `decompile_apks`
Decompile the downloaded APK files using apktool. Specify whether you want to decompile benign or malware applications.

### `remove_dirs`
Removes decompiled directories based on the specified category (benign or malware).

### `extract_features`
This function is a placeholder for extracting static features from the decompiled APKs.

> **Note:** You can conveniently set the environment variable using the GUI by clicking on "Enter your API key."

Please ensure that all files and the program are located in the `/root/DatasetCreator-ML` directory for proper functionality.
