"""
Beating the Benchmark
West Nile Virus Prediction @ Kaggle
__author__ : Abhihsek
"""

import pandas as pd
import numpy as np
from sklearn import ensemble, preprocessing

from sklearn.model_selection import train_test_split
from random import randint
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from collections import Counter
from explainable_svm import svm_explain

def run_cv (train,labels,n=5):
    acc = [];p = [];r = []; f = []
    for i in xrange(n):
        X_train, X_test, y_train, y_test = train_test_split(train, labels,test_size=0.3,random_state=randint(0,100))
        clf = ensemble.RandomForestClassifier(n_jobs=-1, n_estimators=1000, min_samples_split=5)
        clf.fit(X_train, y_train)
        y_pred =  clf.predict(X_test)
        acc.append(accuracy_score(y_test,y_pred))
        p.append(precision_score(y_test,y_pred))
        r.append(recall_score(y_test,y_pred))
        f.append(f1_score(y_test,y_pred))
        print 'run: ', i+1
        print classification_report(y_test,y_pred)

    acc = np.array(acc)
    p = np.array(p)
    r = np.array(r)
    f = np.array(f)
    acc_mean = acc.mean()
    acc_std = acc.std()
    p_mean = p.mean()
    p_std = p.std()
    r_mean = r.mean()
    r_std = r.std()
    f_mean = f.mean()
    f_std = f.std()
    return acc_mean, acc_std, p_mean, p_std, r_mean, r_std, f_mean, f_std

# Load dataset
train = pd.read_csv('../input/train.csv')
test = pd.read_csv('../input/test.csv')
sample = pd.read_csv('../input/sampleSubmission.csv')
weather = pd.read_csv('../input/weather.csv')

# Get labels
labels = train.WnvPresent.values

# Not using codesum for this benchmark
weather = weather.drop('CodeSum', axis=1)

# Split station 1 and 2 and join horizontally
weather_stn1 = weather[weather['Station']==1]
weather_stn2 = weather[weather['Station']==2]
weather_stn1 = weather_stn1.drop('Station', axis=1)
weather_stn2 = weather_stn2.drop('Station', axis=1)
weather = weather_stn1.merge(weather_stn2, on='Date')

# replace some missing values and T with -1
weather = weather.replace('M', -1)
weather = weather.replace('-', -1)
weather = weather.replace('T', -1)
weather = weather.replace(' T', -1)
weather = weather.replace('  T', -1)

# Functions to extract month and day from dataset
# You can also use parse_dates of Pandas.
def create_month(x):
    return x.split('-')[1]

def create_day(x):
    return x.split('-')[2]

train['month'] = train.Date.apply(create_month)
train['day'] = train.Date.apply(create_day)
test['month'] = test.Date.apply(create_month)
test['day'] = test.Date.apply(create_day)

# Add integer latitude/longitude columns
train['Lat_int'] = train.Latitude.apply(int)
train['Long_int'] = train.Longitude.apply(int)
test['Lat_int'] = test.Latitude.apply(int)
test['Long_int'] = test.Longitude.apply(int)

# drop address columns
train = train.drop(['Address', 'AddressNumberAndStreet','WnvPresent', 'NumMosquitos'], axis = 1)
test = test.drop(['Id', 'Address', 'AddressNumberAndStreet'], axis = 1)

# Merge with weather data
train = train.merge(weather, on='Date')
test = test.merge(weather, on='Date')
train = train.drop(['Date'], axis = 1)
test = test.drop(['Date'], axis = 1)

# Convert categorical data to numbers
lbl = preprocessing.LabelEncoder()
lbl.fit(list(train['Species'].values) + list(test['Species'].values))
train['Species'] = lbl.transform(train['Species'].values)
test['Species'] = lbl.transform(test['Species'].values)

lbl.fit(list(train['Street'].values) + list(test['Street'].values))
train['Street'] = lbl.transform(train['Street'].values)
test['Street'] = lbl.transform(test['Street'].values)

lbl.fit(list(train['Trap'].values) + list(test['Trap'].values))
train['Trap'] = lbl.transform(train['Trap'].values)
test['Trap'] = lbl.transform(test['Trap'].values)

# drop columns with -1s
train = train.ix[:,(train != -1).any(axis=0)]
test = test.ix[:,(test != -1).any(axis=0)]

print 'dataset shape: ', train.shape
print 'label dist: ', Counter(labels)

# # Random Forest Classifier
# clf = ensemble.RandomForestClassifier(n_jobs=-1, n_estimators=1000, min_samples_split=5)
# clf.fit(train, labels)
#
# # create predictions and submission file
# predictions = clf.predict_proba(test)[:,1]
# sample['WnvPresent'] = predictions
# sample.to_csv('beat_the_benchmark.csv', index=False)


# print run_cv(train,labels)
svm_explain(train,labels)