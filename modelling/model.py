import sys
sys.path.append("..")

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold,cross_val_score
from sklearn.metrics import f1_score,classification_report,confusion_matrix

from data_preprocessing.preprocessor import Preprocessor

class FraudDetector:
    def __init__(self,df):
        self.df = df.copy()
        self.X_nan = None
        self.y_nan = None
        self.df_dropped = None
        self.X,self.y = None,None
        self.X_train,self.X_test,self.y_train,self.y_test = None,None,None,None
        self.xgb = None
        self.skf = StratifiedKFold(n_splits=5,random_state=42,shuffle=True)
        
    def preprocess(self):
        preprocessor = Preprocessor(self.df)
        preprocessor.clean()
        
    def extract_nan_features(self):
        self.X_nan = self.df[self.df.isnull().T.any()].drop('FLAG',axis=1)
        self.y_nan = self.df[self.df.isnull().T.any()]['FLAG']
        
    def define_features_labels(self):
        self.df_dropped = self.df.dropna()
        self.X,self.y = self.df_dropped.drop('FLAG',axis=1),self.df_dropped['FLAG']
        
    def split_data(self):
        for train_index,test_index in self.skf.split(self.X,self.y):
            self.X_train,self.X_test = self.X.iloc[train_index],self.X.iloc[test_index],
            self.y_train,self.y_test = self.y.iloc[train_index],self.y.iloc[test_index]
            
    def combine_features(self):
        y_train_combined = np.concatenate([self.y_train,self.y_nan])
        X_train_combined = pd.concat([self.X_train,self.X_nan])
        return X_train_combined, y_train_combined
    
    def train_model(self):
        self.preprocess()
        self.extract_nan_features()
        self.define_features_labels()
        self.split_data()
        self.X_train_combined,self.y_train_combined = self.combine_features()
        
        self.xgb = XGBClassifier(n_estimators=100,max_depth=4,random_state=42)
        self.xgb.fit(self.X_train_combined,self.y_train_combined)
        
    def evaluate(self):
        predictions = self.xgb.predict(self.X_test)
        print(cross_val_score(self.xgb,self.X_train_combined,self.y_train_combined,cv=self.skf,scoring='f1').mean())
        print(f1_score(self.y_test,predictions))
        return f1_score(self.y_test,predictions)