# Ethereum Fraud Detection
In this project, I am at predicting the probability of an Ethereum account being fraud using XGBoost.

## Goal Defining
I was always interested in Fraud Detection, and I had noticed lately in the news about
many cryptocurrency frauds. So, I decided to build a binary classifier that can predict
whether an account in fraud or not based on different features.

### Q1: What are we trying to do?

Given the address of an account, we are trying to predict the probability of that account being fraudulent or not.

### Q2: How do we define success?

I used classification metrics, primarily the f1-score,preicision and recall, as the data is imbalanced, thus accuracy would produce
an overly positive outcome.

## Data Gathering
The `collector.py` file in the [data_collection](https://github.com/Vagif12/Ethereum-Fraud-Detection/blob/master/data_collection/collector.py) folder
cotains a DataCollector class, which can be used to obtain the data. 

The data obtaining process is done as follows:

### For obtaining non-fraudulent addresses:

1. The clean dataset containing the list of non-fraudulent addresses
2. For each address, several features are obtained via the [Etherscan API](https://etherscan.io/apis)
3. The output is outputted to a CSV file

### For obtaining fraudulent addresses:

1. The list of fraudulent addresses are obtained via the [ehterscamdb API](https://etherscamdb.info/api/scams/)
2. Additional fraud accounts are obtained via [this JSON file]('https://raw.githubusercontent.com/MyEtherWallet/ethereum-lists/master/src/addresses/addresses-darklist.json')
2. For each address, several features are obtained via the [Etherscan API](https://etherscan.io/apis)
3. The output is outputted to a CSV file

### **NOTE**: This data collection process can take some time. Therefore, I have created the [final dataset](https://github.com/Vagif12/Ethereum-Fraud-Detection/blob/master/datasets/final_combined_dataset.csv) for ease of access.


## Data Preprocessing
The `preprocessor.py` file located in the [data_preprocesing](https://github.com/Vagif12/Ethereum-Fraud-Detection/blob/master/data_preprocessing) folder contains the main Preprocessor class, which has the following methods:

1. `remove_features`: a method to remove unneeded features
2. `transform_data`: a method that applies box-cox transformations on given data
