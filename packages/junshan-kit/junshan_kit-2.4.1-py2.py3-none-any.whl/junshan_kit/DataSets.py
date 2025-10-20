"""
----------------------------------------------------------------------
>>> Author       : Junshan Yin  
>>> Last Updated : 2025-10-16
----------------------------------------------------------------------
"""

import os, time
import pandas as pd
import junshan_kit.DataProcessor
import junshan_kit.kit
from sklearn.preprocessing import StandardScaler

#----------------------------------------------------------
def _download_data(data_name, data_type):
    allowed_types = ["binary", "multi"]
    if data_type not in allowed_types:
        raise ValueError(f"Invalid data_type: {data_type!r}. Must be one of {allowed_types}.")
    from junshan_kit.kit import JianguoyunDownloaderFirefox, JianguoyunDownloaderChrome

    # User selects download method
    while True:
        # User inputs download URL
        url = input("Enter the Jianguoyun download URL: ").strip()

        print("Select download method:")
        print("1. Firefox")
        print("2. Chrome")
        choice = input("Enter the number of your choice (1 or 2): ").strip()

        if choice == "1":
            JianguoyunDownloaderFirefox(url, f"./exp_data/{data_type}/{data_name}").run()
            print("✅ Download completed using Firefox")
            break
        elif choice == "2":
            JianguoyunDownloaderChrome(url, f"./exp_data/{data_type}/{data_name}").run()
            print("✅ Download completed using Chrome")
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.\n")

    # unzip file
    junshan_kit.kit.unzip_file(f'./exp_data/{data_type}/{data_name}/{data_name}.zip', f'./exp_data/{data_name}') 

def _export_csv(df, data_name):
    path = f'./exp_data/{data_name}/'
    os.makedirs(path, exist_ok=True)
    df.to_csv(path + f'{data_name}_num.csv')
    print(path + f'{data_name}.csv')


def _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, user_one_hot_cols = [], export_csv = False, time_info = None):
    if not os.path.exists(csv_path):
        print('\n' + '*'*60)
        print(f"Please download the data.")
        print(csv_path)
        _download_data(data_name, data_type=data_type)
        # junshan_kit.kit.unzip_file(f'./exp_data/{data_name}/{data_name}.zip', f'./exp_data/{data_name}')   
    
    cleaner = junshan_kit.DataProcessor.CSV_TO_Pandas()
    df = cleaner.preprocess_dataset(csv_path, drop_cols, label_col, label_map, data_name, user_one_hot_cols, print_info=print_info, time_info = time_info)

    if export_csv:
        _export_csv(df, data_name)

    return df


# ********************************************************************
"""
----------------------------------------------------------------------
                            Datasets
----------------------------------------------------------------------
"""

def credit_card_fraud_detection(data_name = "Credit Card Fraud Detection", print_info = False, export_csv=False):

    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/creditcard.csv'
    drop_cols = []
    label_col = 'Class' 
    label_map = {0: -1, 1: 1}
    

    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv)
    

    return df


def diabetes_health_indicators(data_name = "Diabetes Health Indicators", print_info = False, export_csv = False):
    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/diabetes_dataset.csv'
    drop_cols = []
    label_col = 'diagnosed_diabetes'
    label_map = {0: -1, 1: 1}
    

    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv)

    return df


def electric_vehicle_population(data_name = "Electric Vehicle Population", print_info = False, export_csv = False):

    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/Electric_Vehicle_Population_Data.csv'
    drop_cols = ['VIN (1-10)', 'DOL Vehicle ID', 'Vehicle Location']
    label_col = 'Electric Vehicle Type'
    label_map = {
    'Battery Electric Vehicle (BEV)': 1,
    'Plug-in Hybrid Electric Vehicle (PHEV)': -1
    }
    

    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv)

    return df

def global_house_purchase(data_name = "Global House Purchase", print_info = False, export_csv = False):

    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/global_house_purchase_dataset.csv'
    drop_cols = ['property_id']
    label_col = 'decision'
    label_map = {0: -1, 1: 1}
    

    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv)

    return df


def health_lifestyle(data_name = "Health Lifestyle", print_info = False, export_csv = False):

    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/health_lifestyle_dataset.csv'
    drop_cols = ['id']
    label_col = 'disease_risk'
    label_map = {0: -1, 1: 1}
    

    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv)

    return df


def medical_insurance_cost_prediction(data_name = "Medical Insurance Cost Prediction", print_info = False, export_csv = False):
    """
    1. The missing values in this dataset are handled by directly removing the corresponding column. Since the `alcohol_freq` column contains a large number of missing values, deleting the rows would result in significant data loss, so the entire column is dropped instead.

    2. There are several columns that could serve as binary classification labels, such as `is_high_risk`, `cardiovascular_disease`, and `liver_disease`. In this case, `is_high_risk` is chosen as the label column.
    """

    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/medical_insurance.csv'
    drop_cols = ['alcohol_freq']
    label_col = 'is_high_risk'
    label_map = {0: -1, 1: 1}
    

    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv)

    return df


def particle_physics_event_classification(data_name = "Particle Physics Event Classification", print_info = False, export_csv = False):

    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/Particle Physics Event Classification.csv'
    drop_cols = []
    label_col = 'Label'
    label_map = {'s': -1, 'b': 1}
    

    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv)

    return df



def adult_income_prediction(data_name = "Adult Income Prediction", print_info = False, export_csv=False):

    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/adult.csv'
    drop_cols = []
    label_col = 'income'
    label_map = {'<=50K': -1, '>50K': 1}
    

    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv)

    return df


def TamilNadu_weather_2020_2025(data_name = "TN Weather 2020-2025", print_info = False, export_csv = False):

    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/TNweather_1.8M.csv'
    drop_cols = ['Unnamed: 0']
    label_col = 'rain_tomorrow'
    label_map = {0: -1, 1: 1}

    # Extraction mode.
    # - 0 : Extract ['year', 'month', 'day', 'hour']
    # - 1 : Extract ['hour', 'dayofweek', 'is_weekend']
    time_info = {
        'time_col_name': 'time',
        'trans_type': 0
    }

    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv, time_info=time_info)


    return df

def YouTube_Recommendation(data_name = "YouTube Recommendation", print_info = False, export_csv = False):

    data_type = "binary"
    csv_path = f'./exp_data/{data_type}/{data_name}/youtube recommendation dataset.csv'
    drop_cols = ['user_id']
    label_col = 'subscribed_after'
    label_map = {0: -1, 1: 1}

    # Extraction mode.
    # - 0 : Extract ['year', 'month', 'day', 'hour']
    # - 1 : Extract ['hour', 'dayofweek', 'is_weekend']
    time_info = {
        'time_col_name': 'timestamp',
        'trans_type': 1
    }
    
    df = _run(csv_path, data_name, data_type, drop_cols, label_col, label_map, print_info, export_csv=export_csv, time_info=time_info)

    return df