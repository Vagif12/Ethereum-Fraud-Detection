import pandas as pd

class Preprocessor:
    """
    This is the base Preprocessor class that will be using for 
    any data preprocessing required
    """
    def __init__(self,df):
        self.df = df

    def clean(self):
        self.remove_features()
        self.drop_duplicates()
    
    def add_columns(self,inference=0):
        """
        This method adds columns to the data fetched via the REST API

        Parameters:

        filename = the name of the file, without the .csv extension

        Returns:

        df = A DataFrame of the dataset with columns

        """
        # Define list of columns
        cols = ['Index',
                         'Address',
                         'FLAG',
                         'Avg min between sent tnx',
                         'Avg min between received tnx',
                         'Time Diff between first and last (Mins)',
                         'Sent tnx',
                         'Received Tnx',
                         'Number of Created Contracts',
                         'Unique Received From Addresses',
                         'Unique Sent To Addresses',
                         'min value received',
                         'max value received ',
                         'avg val received',
                         'min val sent',
                         'max val sent',
                         'avg val sent',
                         'min value sent to contract',
                         'max val sent to contract',
                         'avg value sent to contract',
                         'total transactions (including tnx to create contract',
                         'total Ether sent',
                        #  'total ether received',
                         'total ether sent contracts',
                         'total ether balance',
                         ' Total ERC20 tnxs',
                         ' ERC20 total Ether received',
                         ' ERC20 total ether sent',
                         ' ERC20 total Ether sent contract',
                         ' ERC20 uniq sent addr',
                         ' ERC20 uniq rec addr',
                         ' ERC20 uniq sent addr.1',
                         ' ERC20 uniq rec contract addr',
                         ' ERC20 avg time between sent tnx',
                         ' ERC20 avg time between rec tnx',
                         ' ERC20 avg time between rec 2 tnx',
                         ' ERC20 avg time between contract tnx',
                         ' ERC20 min val rec',
                         ' ERC20 max val rec',
                         ' ERC20 avg val rec',
                         ' ERC20 min val sent',
                         ' ERC20 max val sent',
                        #  ' ERC20 avg val sent',
                         ' ERC20 min val sent contract',
                         ' ERC20 max val sent contract',
                         ' ERC20 avg val sent contract',
                         ' ERC20 uniq sent token name',
                         ' ERC20 uniq rec token name',
                         ' ERC20 most sent token type',
                         ' ERC20_most_rec_token_type']

        # Read file,assign cols
        self.df.columns = cols

    def remove_features(self,inference=False):
        """
        This method removes unnecessary features

        Returns:
        
        df = a DataFrame without unneeded features
        """
        # Remove unnecessary fields
        self.df.drop(['Index','Address', ' ERC20 uniq sent token name',
 ' ERC20 uniq rec token name',
 ' ERC20 most sent token type',
 ' ERC20_most_rec_token_type',' ERC20 min val sent contract',' ERC20 max val sent contract',' ERC20 avg val sent contract','min value sent to contract','max val sent to contract','avg value sent to contract',' ERC20 avg time between sent tnx',' ERC20 avg time between rec tnx',' ERC20 avg time between rec 2 tnx','total ether sent contracts',' ERC20 avg time between contract tnx',' ERC20 total Ether sent contract',' ERC20 uniq sent addr.1'],axis=1,inplace=True)
    def drop_duplicates(self):
        self.df.drop_duplicates(inplace=True)