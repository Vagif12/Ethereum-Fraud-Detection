import csv
import numpy as np 
import pandas as pd 
from tqdm import tqdm
import multiprocessing
from base64 import encode
import requests,string,time
from statistics import mean
from datetime import datetime

class DataCollector:
    """
    This is the base class for collecting the required data. The data is obtained
    via REST API's

    This class obtains features for clean ehtereum accounts addresses, as well
    as scam ethereum account addresses, therefore the main() function must be ran twice
    to output two datasets
    """

    def __init__(self,inference=False):
        # Specify if the data we are obtaining is for Inference or not
        self.inference = inference

    def get_clean_account_adresses(self):
        '''
        This method gets the clean account addresses 
        '''
        print("Starting retrieval of clean accounts from Github")

        # Read CSV file on the Github repo
        clean_account_adresses = pd.read_csv('https://raw.githubusercontent.com/Vagif12/Ethereum-Fraud-Detection/master/datasets/clean_adresses.csv')
        # Print the number of unique and clean addresses
        print('Number of clean account adressess: ' + str(len(clean_account_adresses['Address'])))
        print('Number of unique clean account adressess: ' + str(len(np.unique(clean_account_adresses['Address']))))

        # Return a numpy array of addresses obtained
        return np.array(clean_account_adresses['Address'])

    def get_illicit_account_addresses(self):
        '''
        This method gets the illictit account addresses via the EtherscamDB API
        and a supplementary JSON File

        '''

        # Make the request, check + convert to JSON
        response = requests.get("https://etherscamdb.info/api/scams/")
        if response.status_code == 200:
            response = response.json()
            no_of_scams = len(response['result'])
            scam_id, scam_name, scam_status, scam_category, addresses = ([] for i in range(5))

            print("Starting retrieval of scams from EtherscamDB")

            for scam in range(no_of_scams):
                if 'addresses' in response['result'][scam]:
                    for i in response['result'][scam]['addresses']:
                        if i[:2] != '0x':
                            continue
                        addresses.append(i)

                        scam_id.append(response['result'][scam]['id'])
                        scam_name.append(response['result'][scam]['name'])
                        scam_status.append(response['result'][scam]['status'])

                        if 'category' in response['result'][scam]:
                            scam_category.append(response['result'][scam]['category'])
                        else:
                            scam_category.append('Null')
            # Basics Stats on the dataset
            print("file number of illicit accounts: ", len(addresses))
            print("Unique illicit accounts: ", len(np.unique(addresses)))

            # JSON File
            address_darklist = requests.get('https://raw.githubusercontent.com/MyEtherWallet/ethereum-lists/master/src/addresses/addresses-darklist.json').json()
            addresses_2 = []

            for item in address_darklist:
                addresses_2.append(item['address'])

            print("Number of illegal addresses: ", len(address_darklist))
            print("Number of unique illegal addresses in JSON file: ", len(np.unique(addresses_2)))

            all_addresses = []
            all_addresses = np.concatenate((addresses, addresses_2), axis=None)
            all_addresses = np.unique(np.char.lower(all_addresses))

            print("Final number of unique Addresses: ", len(np.unique(all_addresses)))
            return all_addresses
        
    def main(self,clean_addresses=True,name='clean_addresses',inference_addresses=[]):
        """
        Main function of the DataCollector Class.
        This function links together all the methods and processes together

        Parameters:
        clean_address = whether or not to obtain clean or illicit addresses
        inference_addresses = if inference=True, then the list of addresses to fetch data from
        name = the name of the csv file to be saved
        """
        addresses = []
        name = name
        flag = 0
        if self.inference == False:
            if clean_addresses == True:
                addresses = self.get_clean_account_adresses()
                flag = 0
            else:
                addresses = self.get_illicit_account_addresses()
                flag = 1
        else:
            name = 'inference'
            addresses = inference_addresses
        index = 1
        pbar = tqdm(total=len(addresses))
        for address in addresses:
            # Loop through addresses, and get data for each address 
            normal_tnxs = self.normal_transactions(index, address, flag=flag)
            token_transfer_tnxs = self.token_transfer_transactions(address)
            try:
                # Save obtained data to csv file
                all_tnxs = np.concatenate((normal_tnxs, token_transfer_tnxs), axis=None)
                with open(r'./{}.csv'.format(name), 'a', newline="") as f:
                    writer = csv.writer(f, delimiter=',')
                    writer.writerow(all_tnxs)
                    print(all_tnxs)
                index += 1
                pbar.update(1)
            except:
                continue

        pbar.close()
        if name == 'inference':
            df = pd.read_csv('inference.csv',header=None)
            return df


    def account_balance(self,address):
        """
        Function to obtain account balance

        Parameters:
        address: the address of an account

        Returns:
        balance: balance of given address
        """
        url = "https://api.etherscan.io/api?module=account&action=balance&address={address}" \
              "&tag=latest&apikey=1BDEBF8IZY2H7ENVHPX6II5ZHEBIJ8V33N".format(address=address)

        r = requests.get(url=url)
        data = r.json()
        balance = 0

        if data['status'] != 0:
            balance = int(data['result']) / 1000000000000000000

        return balance



    def get_total_number_of_normal_transactions(self,address):
        """
        Function to obtain total number of normal transactions

        Parameters:
        address: the address of an account

        Returns:
        num_normal_transactions = the number of normal transactions
        """

        url = "http://api.etherscan.io/api?module=account&action=txlist&address={address}" \
              "&startblock=0&endblock=99999999&sort=asc&apikey=1BDEBF8IZY2H7ENVHPX6II5ZHEBIJ8V33N".format(address=address)
        r = requests.get(url=url)
        data = r.json()
        num_normal_transactions = 0

        if data['status'] != 0:
            for tnx in range(len(data['result'])):
                num_normal_transactions += 1

        return num_normal_transactions



    def token_transfer_transactions(self,address):
        """
        Function to obtain data about an account's token transfer transactions

        Parameters:
        address: the address of an account

        Returns:
        ERC20_contract_tnx_fields = different features based on token transactions
        """
        URL = "http://api.etherscan.io/api?module=account&action=tokentx&address={address}" \
              "&startblock=0&endblock=999999999&sort=asc&apikey=1BDEBF8IZY2H7ENVHPX6II5ZHEBIJ8V33N".format(address=address)

        r = requests.get(url=URL)
        data = r.json()
        timestamp, recipients, timeDiffSent, timeDiffReceive, timeDiffContractTnx, receivedFromAddresses, receivedFromContractAddress, \
        sentToAddresses, sentToContractAddresses, sentToContracts, valueSent, valueReceived, valueSentContracts, \
        tokenReceivedName, tokenReceivedSymbol, tokenSentName, tokenSentSymbol, valueReceivedContract, sentToAddressesContract,\
        receivedFromAddressesContract, tokenSentNameContract, tokenSentSymbolContract = ([] for i in range(22))

        receivedTransactions, sentTransactions, minValReceived, tokenContractTnx, \
        maxValReceived, avgValReceived, minValSent, maxValSent, avgValSent, minValSentContract, \
        maxValSentContract, avgValSentContract = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ERC20_contract_tnx_fields = [0, 0, 0, 0, 0, 0,0, 0, 0,0, 0, 0,0, 0, 0,0, 0, 0,0, 0, 0,
                                      0, 0, 0,0]
        if data['status'] != '0':
            for tokenTnx in range(len(data['result'])):
                timestamp.append(data['result'][tokenTnx]['timeStamp'][0])

                # if receiving
                if data['result'][tokenTnx]['to'] == address:
                    receivedTransactions = receivedTransactions + 1
                    receivedFromAddresses.append(data['result'][tokenTnx]['from'])
                    receivedFromContractAddress.append(data['result'][tokenTnx]['contractAddress'])
                    valueReceived.append(int(data['result'][tokenTnx]['value']) / 1000000000000000000)

                    if data['result'][tokenTnx]['tokenName'] is not None:
                        tName = data['result'][tokenTnx]['tokenName']
                        tName.translate(str.maketrans('', '', string.punctuation))
                        tokenReceivedName.append(tName.encode("utf-8"))
                    tokenReceivedSymbol.append(data['result'][tokenTnx]['tokenSymbol'])
                    if receivedTransactions > 0:
                        timeDiffReceive.append((datetime.utcfromtimestamp(int(timestamp[tokenTnx])) - datetime.utcfromtimestamp(
                            int(timestamp[tokenTnx - 1]))).total_seconds() / 60)

                # if sending
                if data['result'][tokenTnx]['from'] == address:
                    sentTransactions = sentTransactions + 1
                    sentToAddresses.append(data['result'][tokenTnx]['to'])
                    sentToContractAddresses.append(data['result'][tokenTnx]['contractAddress'])
                    valueSent.append(int(data['result'][tokenTnx]['value']) / 1000000000000000000)
                    if data['result'][tokenTnx]['tokenName'] is not None:
                        tName = data['result'][tokenTnx]['tokenName']
                        tName.translate(str.maketrans('', '', string.punctuation))
                        tokenSentName.append(tName.encode("utf-8"))

                    tokenSentSymbol.append(data['result'][tokenTnx]['tokenSymbol'])
                    if sentTransactions > 0:
                        timeDiffSent.append((datetime.utcfromtimestamp(int(timestamp[tokenTnx])) - datetime.utcfromtimestamp(
                            int(timestamp[tokenTnx - 1]))).total_seconds() / 60)

                # if a contract
                if data['result'][tokenTnx]['contractAddress'] == address:
                    tokenContractTnx = tokenContractTnx + 1
                    valueReceivedContract.append(int(data['result'][tokenTnx]['value']) / 1000000000000000000)
                    sentToAddressesContract.append(data['result'][tokenTnx]['to'])
                    receivedFromAddressesContract.append(data['result'][tokenTnx]['from'])
                    if data['result'][tokenTnx]['tokenName'] is not None:
                        tokenSentNameContract.append((data['result'][tokenTnx]['tokenName']).encode("utf-8"))
                    tokenSentSymbolContract.append(data['result'][tokenTnx]['tokenSymbol'])
                    if tokenContractTnx > 0:
                        timeDiffContractTnx.append((datetime.utcfromtimestamp(int(timestamp[tokenTnx])) - datetime.utcfromtimestamp(
                            int(timestamp[tokenTnx - 1]))).total_seconds() / 60)

            totalTnx = receivedTransactions + sentTransactions + tokenContractTnx
            totalEtherRec = np.sum(valueReceived)
            totalEtherSent = np.sum(valueSent)
            totalEtherContract = np.sum(valueReceivedContract)
            uniqSentAddr, uniqRecAddr = self.uniq_addresses(sentToAddresses, receivedFromAddresses)
            uniqSentContAddr, uniqRecContAddr = self.uniq_addresses(sentToAddressesContract, receivedFromContractAddress)
            avgTimeBetweenSentTnx = self.avgTime(timeDiffSent)
            avgTimeBetweenRecTnx = self.avgTime(timeDiffReceive)
            avgTimeBetweenContractTnx = self.avgTime(timeDiffContractTnx)
            minValReceived, maxValReceived, avgValReceived = self.min_max_avg(valueReceived)
            minValSent, maxValSent, avgValSent = self.min_max_avg(valueSent)
            minValSentContract, maxValSentContract, avgValSentContract = self.min_max_avg(valueSentContracts)
            uniqSentTokenName = len(np.unique(tokenSentName))
            uniqRecTokenName = len(np.unique(tokenReceivedName))
            if len(tokenSentName) > 0:
                mostSentTokenType = self.most_frequent(tokenSentName)
            else:
                mostSentTokenType = "None"

            if len(tokenReceivedName) > 0:
                mostRecTokenType = self.most_frequent(tokenReceivedName)
            else:
                mostRecTokenType = "None"

            ERC20_contract_tnx_fields = [totalTnx, totalEtherRec, totalEtherSent, totalEtherContract, uniqSentAddr, uniqRecAddr,
                                         uniqSentContAddr, uniqRecContAddr, avgTimeBetweenSentTnx,
                                         avgTimeBetweenRecTnx, avgTimeBetweenRecTnx, avgTimeBetweenContractTnx,
                                         minValReceived, maxValReceived, avgValReceived,
                                         minValSent, maxValSent, avgValSent,
                                         minValSentContract, maxValSentContract, avgValSentContract,
                                         uniqSentTokenName, uniqRecTokenName, mostSentTokenType,
                                         mostRecTokenType]
        return ERC20_contract_tnx_fields

    def normal_transactions(self,index, address, flag):
        """
        Function to obtain data on normal_transactions

        Parameters:
        index: the index number to index the data
        address: the address of an account
        flag: whether the transactions are fraud(1) or not(0)

        Returns:
        transaction_fields = different features based on normal transactions
        """
        URL = "https://api.etherscan.io/api?module=account&action=txlist&address={address}" \
              "&startblock=0&endblock=99999999&page=1&offset=10000&sort=asc&apikey=1BDEBF8IZY2H7ENVHPX6II5ZHEBIJ8V33N".format(address=address)

        r = requests.get(url=URL)
        data = r.json()

        timestamp, recipients, timeDiffSent, timeDiffReceive, receivedFromAddresses, \
        sentToAddresses, sentToContracts, valueSent, valueReceived, valueSentContracts = ([] for i in range(10))
        receivedTransactions, sentTransactions, createdContracts, minValReceived, \
        maxValReceived, avgValReceived, minValSent, maxValSent, avgValSent, minValSentContract, \
        maxValSentContract, avgValSentContract = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        transaction_fields = [0, 0, 0 ,0, 0, 0,0,0, 0,0, 0, 0, 0, 0,
                             0, 0, 0,0, 0, 0,0, 0, 0, 0,0]

        if data['status'] != '0':
            for tnx in range(len(data['result'])):
                if data['result'][tnx]['isError'] == 1:
                    pass
                timestamp.append(data['result'][tnx]['timeStamp'])
                if data['result'][tnx]['to'] == address:
                    receivedTransactions = receivedTransactions + 1
                    receivedFromAddresses.append(data['result'][tnx]['from'])
                    valueReceived.append(int(data['result'][tnx]['value']) / 1000000000000000000)
                    if receivedTransactions > 0:
                        timeDiffReceive.append((datetime.utcfromtimestamp(int(timestamp[tnx])) - datetime.utcfromtimestamp(
                            int(timestamp[tnx - 1]))).total_seconds() / 60)
                if data['result'][tnx]['from'] == address:
                    sentTransactions = sentTransactions + 1
                    sentToAddresses.append(data['result'][tnx]['to'])
                    valueSent.append(int(data['result'][tnx]['value']) / 1000000000000000000)
                    if sentTransactions > 0:
                        timeDiffSent.append((datetime.utcfromtimestamp(int(timestamp[tnx])) - datetime.utcfromtimestamp(
                            int(timestamp[tnx - 1]))).total_seconds() / 60)

                if data['result'][tnx]['contractAddress'] != '':
                    createdContracts = createdContracts + 1
                    sentToContracts.append(data['result'][tnx]['contractAddress'])
                    valueSentContracts.append(int(data['result'][tnx]['value']) / 1000000000000000000)

            totalTnx = sentTransactions + receivedTransactions + createdContracts
            totalEtherReceived = np.sum(valueReceived)
            totalEtherSent = np.sum(valueSent)
            totalEtherSentContracts = np.sum(valueSentContracts)
            totalEtherBalance = totalEtherReceived - totalEtherSent - totalEtherSentContracts
            avgTimeBetweenSentTnx = self.avgTime(timeDiffSent)
            avgTimeBetweenRecTnx = self.avgTime(timeDiffReceive)
            numUniqSentAddress, numUniqRecAddress = self.uniq_addresses(sentToAddresses, receivedFromAddresses)
            minValReceived, maxValReceived, avgValReceived = self.min_max_avg(valueReceived)
            minValSent, maxValSent, avgValSent = self.min_max_avg(valueSent)
            minValSentContract, maxValSentContract, avgValSentContract = self.min_max_avg(valueSentContracts)
            timeDiffBetweenFirstAndLast = self.timeDiffFirstLast(timestamp)

            ILLICIT_OR_NORMAL_ACCOUNT_FLAG = flag

            transaction_fields = [index, address, ILLICIT_OR_NORMAL_ACCOUNT_FLAG ,avgTimeBetweenSentTnx, avgTimeBetweenRecTnx, timeDiffBetweenFirstAndLast,
                                  sentTransactions,
                                  receivedTransactions, createdContracts,
                                  numUniqRecAddress, numUniqSentAddress,
                                  minValReceived, maxValReceived, avgValReceived,
                                  minValSent, maxValSent, avgValSent,
                                  minValSentContract, maxValSentContract, avgValSentContract,
                                  totalTnx, totalEtherSent, totalEtherReceived, totalEtherSentContracts,
                                  totalEtherBalance]
        return transaction_fields


    def timeDiffFirstLast(self,timestamp):
        """
        This function calculates the time difference from last transaction

        Parameters:
        timestamp: the timestamp

        Returns:
        timeDiff: the calculated time difference
        """
        timeDiff = 0
        if len(timestamp)>0:
            timeDiff = "{0:.2f}".format((datetime.utcfromtimestamp(int(timestamp[-1])) - datetime.utcfromtimestamp(
                int(timestamp[0]))).total_seconds() / 60)
        return timeDiff


    def avgTime(self,timeDiff):
        """
        This function calculates the average time from the time difference

        Parameters:
        timestamp: the time difference of a transaction

        Returns:
        timeDiff: the calculated average time
        """
        timeDifference = 0
        if len(timeDiff) > 1:
            timeDifference =  "{0:.2f}".format(mean(timeDiff))
        return timeDifference

    def min_max_avg(self,value_array_tnxs):
        """
        This function calculates the minimum and maximum average time from the transactions

        Parameters:
        value_array_tnxs: an array of transactions

        Returns:
        the minimum, maximum and avg transaction time
        """
        minVal, maxVal, avgVal = 0, 0, 0
        if value_array_tnxs:
            minVal = min(value_array_tnxs)
            maxVal = max(value_array_tnxs)
            avgVal = mean(value_array_tnxs)
        return "{0:.6f}".format(minVal), "{0:.6f}".format(maxVal), "{0:.6f}".format(avgVal)

    def uniq_addresses(self,sent_addresses, received_addresses):
        """
        This method calculates the number of unique addresses sent and received

        Parameters:
        sent_addresses = an array of addresses that transactions were sent to
        received_addresses = an array of addreses that transactions were received from

        Returns:
        uniqSent = number of unique sent addresses
        uniqRec = numebr of unique received addresses
        """
        uniqSent, createdContrcts, uniqRec = 0, 0, 0
        if sent_addresses:
            uniqSent = len(np.unique(sent_addresses))

        if received_addresses:
            uniqRec = len(np.unique(received_addresses))
        return uniqSent, uniqRec

    def most_frequent(self,List):
        '''
        This method gets the most frequent value of a List

        Parameters:
        List = a list of values

        Returns:
        the mode of the list
        '''
        return max(set(List), key = List.count)
