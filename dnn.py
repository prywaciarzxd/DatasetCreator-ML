from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
import csv
import time
import os

class HyperparameterGridSearch:

    def __init__(self, home_directory, tool_directory, data_path, results_file_path):
        self.data_path = data_path
        self.results_file_path = os.path.join(home_directory, tool_directory, results_file_path)
        self.data = None
        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None
        self.label_encoder = LabelEncoder()
        self.best_results = {}

    def load_data(self):
        self.data = pd.read_csv(self.data_path)
        if 'TelephonyManager.getSimCountryIso' in self.data.columns and not self.data['TelephonyManager.getSimCountryIso'].empty:
            self.data.dropna(subset=['TelephonyManager.getSimCountryIso'], inplace=True)
            self.data['TelephonyManager.getSimCountryIso'] = pd.to_numeric(self.data['TelephonyManager.getSimCountryIso'], errors='coerce')
            self.data['TelephonyManager.getSimCountryIso'] = self.data['TelephonyManager.getSimCountryIso'].fillna(0).astype(int)

    def preprocess_data(self):
        X = self.data.drop('class', axis=1)
        y = self.data['class']
        y = self.label_encoder.fit_transform(y)
        y = y.ravel()
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    def create_model(self, neurons):
        model = Sequential()
        model.add(Dense(neurons, activation='relu', input_shape=(self.X_train.shape[1],)))
        model.add(Dense(neurons // 2, activation='relu'))  # Half neurons in the next layer
        model.add(Dense(1, activation='sigmoid'))
        return model

    def train_model(self, model, optimizer, batch_size, epochs):
        model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])
        print(f"\nTraining model with optimizer={optimizer}, batch_size={batch_size}, epochs={epochs}...")
        history = model.fit(self.X_train, self.y_train, batch_size=batch_size, epochs=epochs,
                            validation_data=(self.X_test, self.y_test), verbose=1)
        return model, history

    def evaluate_model(self, model, optimizer, batch_size, epochs, neurons):
        y_pred = model.predict(self.X_test)
        y_pred_classes = (y_pred > 0.5).astype("int32")

        accuracy = accuracy_score(self.y_test, y_pred_classes)
        precision = precision_score(self.y_test, y_pred_classes)
        recall = recall_score(self.y_test, y_pred_classes)
        f1 = f1_score(self.y_test, y_pred_classes)
        auc = roc_auc_score(self.y_test, y_pred)

        cm = confusion_matrix(self.y_test, y_pred_classes)
        tn, fp, fn, tp = cm.ravel()
        weighted_tpr = tp / (tp + fn)
        weighted_fpr = fp / (fp + tn)

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "auc": auc,
            "weighted_tpr": weighted_tpr,
            "weighted_fpr": weighted_fpr,
            "elapsed_time": self.elapsed_time
        }

    def search_hyperparameters(self, optimizers, batch_sizes, epochs_values, neuron_values):
        with open(self.results_file_path, 'w') as file:
            for optimizer in optimizers:
                for batch_size in batch_sizes:
                    for epochs in epochs_values:
                        for neurons in neuron_values:
                            start_time = time.time()
                            model = self.create_model(neurons)
                            model, history = self.train_model(model, optimizer, batch_size, epochs)
                            self.elapsed_time = time.time() - start_time

                            results = self.evaluate_model(model, optimizer, batch_size, epochs, neurons)

                            key = (optimizer, batch_size, epochs, neurons)
                            if key not in self.best_results or results["accuracy"] > self.best_results[key]["accuracy"]:
                                self.best_results[key] = results

                            file.write(f"Optimizer: {optimizer}, Batch Size: {batch_size}, "
                                       f"Epochs: {epochs}, Neurons: {neurons} - "
                                       f"Test accuracy: {results['accuracy']}, Precision: {results['precision']}, "
                                       f"Recall: {results['recall']}, F1 Score: {results['f1']}, "
                                       f"AUC: {results['auc']}, Weighted TPR: {results['weighted_tpr']}, "
                                       f"Weighted FPR: {results['weighted_fpr']}, "
                                       f"Elapsed Time: {results['elapsed_time']} seconds\n")
                            file.write('######## \n')


if __name__ == "__main__":
    drebin_path = '/home/kali/Downloads/drebin-215-dataset-5560malware-9476-benign.csv'
    malgenome_path = '/home/kali/Downloads/5854590/malgenome-215-dataset-1260malware-2539-benign.csv'
    biggest_path = '/home/kali/Desktop/dataset_create_tool/text_csv_files/found_features_verified_all.csv'
    results_file_path = '/home/kali/Desktop/dataset_create_tool/text_csv_files/accuracy_results.txt'

    grid_search = HyperparameterGridSearch(biggest_path, results_file_path)
    grid_search.load_data()
    grid_search.preprocess_data()

    optimizers = ['adam', 'sgd', 'rmsprop', 'adamax']
    batch_sizes = [16, 32, 64]
    epochs_values = [5, 10, 15]
    neuron_values = [32, 64, 128]

    grid_search.search_hyperparameters(optimizers, batch_sizes, epochs_values, neuron_values)
