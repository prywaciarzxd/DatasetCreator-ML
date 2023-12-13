from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
import csv
import time 

drebin_path = '/home/kali/Downloads/drebin-215-dataset-5560malware-9476-benign.csv' 
malgenome_path = '/home/kali/Downloads/5854590/malgenome-215-dataset-1260malware-2539-benign.csv'
biggest_path = '/home/kali/Desktop/dataset_create_tool/text_csv_files/found_features_verified_all.csv'

# Load data
data = pd.read_csv(biggest_path)


if 'TelephonyManager.getSimCountryIso' in data.columns and not data['TelephonyManager.getSimCountryIso'].empty:
    # Drop rows with NaN values in 'TelephonyManager.getSimCountryIso' column
    data.dropna(subset=['TelephonyManager.getSimCountryIso'], inplace=True)
    
    # Convert column values to numeric, filling NaNs with 0, and then converting to integers
    data['TelephonyManager.getSimCountryIso'] = pd.to_numeric(data['TelephonyManager.getSimCountryIso'], errors='coerce')
    data['TelephonyManager.getSimCountryIso'] = data['TelephonyManager.getSimCountryIso'].fillna(0).astype(int)




# Separate features (X) and labels (y)
X = data.drop('class', axis=1)
y = data['class']

# Convert labels from text to numerical values
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Reshape labels
y = y.ravel()

# Split data into training and testing sets (70% / 30%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Define grid of hyperparameters
batch_sizes = [16, 32, 64]
epoch_values = [5, 10, 15]
optimizers = ['adam', 'sgd', 'rmsprop', 'adamax']  # Add more optimizers as needed
neuron_values = [32, 64, 128]  # Neuron counts to test

# Create a dictionary to store the best results for each pair of hyperparameters and optimizer
best_results = {}

# Create a file to store results
with open('/home/kali/Desktop/dataset_create_tool/text_csv_files/accuracy_results.txt', 'w') as file:
    # Iterate over different batch sizes, epochs, optimizers, and neuron counts
    for optimizer in optimizers:
        for batch_size in batch_sizes:
            for epochs in epoch_values:
                for neurons in neuron_values:
                    start_time = time.time()  # Record start time
                    # Prepare model
                    model = Sequential()
                    model.add(Dense(neurons, activation='relu', input_shape=(X_train.shape[1],)))
                    model.add(Dense(neurons // 2, activation='relu'))  # Half neurons in the next layer
                    model.add(Dense(1, activation='sigmoid'))

                    # Compile model with the current optimizer
                    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

                    # Train model
                    print(f"\nTraining model with optimizer={optimizer}, batch_size={batch_size}, epochs={epochs}, neurons={neurons}...")
                    history = model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs,
                                        validation_data=(X_test, y_test), verbose=1)

                    # Predictions and metrics calculation
                    y_pred = model.predict(X_test)
                    y_pred_classes = (y_pred > 0.5).astype("int32")  # Thresholding at 0.5

                    # Metrics calculation
                    accuracy = accuracy_score(y_test, y_pred_classes)
                    precision = precision_score(y_test, y_pred_classes)
                    recall = recall_score(y_test, y_pred_classes)
                    f1 = f1_score(y_test, y_pred_classes)

                    # AUC calculation
                    auc = roc_auc_score(y_test, y_pred)

                    # Confusion matrix to calculate weighted TPR and FPR
                    cm = confusion_matrix(y_test, y_pred_classes)
                    tn, fp, fn, tp = cm.ravel()

                    weighted_tpr = tp / (tp + fn)  # Weighted True Positive Rate
                    weighted_fpr = fp / (fp + tn)  # Weighted False Positive Rate

                    end_time = time.time()  # Record end time
                    elapsed_time = end_time - start_time  # Calculate elapsed time

                    # Check if the accuracy for this iteration is the best so far
                    key = (optimizer, batch_size, epochs, neurons)
                    if key not in best_results or accuracy > best_results[key]["accuracy"]:
                        best_results[key] = {
                            "accuracy": accuracy,
                            "precision": precision,
                            "recall": recall,
                            "f1": f1,
                            "auc": auc,
                            "weighted_tpr": weighted_tpr,
                            "weighted_fpr": weighted_fpr,
                            "elapsed_time": elapsed_time
                        }

                    # Write results to the file along with elapsed time
                    file.write(f"Optimizer: {optimizer}, Batch Size: {batch_size}, Epochs: {epochs}, Neurons: {neurons} - Test accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1 Score: {f1}, AUC: {auc}, Weighted TPR: {weighted_tpr}, Weighted FPR: {weighted_fpr}, Elapsed Time: {elapsed_time} seconds\n")
                    file.write('######## \n')

