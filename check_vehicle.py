'''
open excel file by pandas   
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import time
import datetime
import re


def get_file_path():
    '''
    get file path
    '''
    file_path = input('Please input file path:')
    if os.path.exists(file_path):
        return file_path
    else:
        print('File path is not exist!')
        sys.exit()

def get_file_name():
    '''
    get file name
    '''
    file_name = input('Please input file name:')
    if os.path.exists(file_name):
        return file_name
    else:
        print('File name is not exist!')
        sys.exit()

# read xlsx pandas  

def read_xlsx(file_path):
    '''
    read xlsx file by pandas
    '''
    file_path = file_path 
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    return df
file_name = 'vehicle_data.xlsx'
df = read_xlsx(file_path = file_name)

print("-" * 40)
print('Vehicle data:')
print(df.head())

#get 
current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year

# compare expiry date with current date
def compare_date(df):
    '''
    compare expiry date with current date
    '''
    df['expiry_date'] = pd.to_datetime(df['expiry_date'])
    df['current_date'] = datetime.datetime.now()
    df['diff'] = df['expiry_date'] - df['current_date']
    df['diff'] = df['diff'].dt.days
    return df
df = compare_date(df)

print("-" * 40)
print('calculate data differ in month:')
print(df.head())

# get vehicle data which is diff less than 30 days

def get_vehicle_data(df):
    '''
    get vehicle data which is diff less than 30 days
    '''
    df = df[df['diff'] < 30]
    return df

print("-" * 40)
print('get vehicle data which is diff less than 30 days')
df = get_vehicle_data(df)
print(df.head())

# get vehicle number which is diff less  than 30 days
def get_vehicle_number(df):
    '''
    get vehicle number which is diff less  than 30 days
    '''
    df = df['vehicle number']
    return df

print("-" * 40)
print('get vehicle number which is diff less than 30 days')
df = get_vehicle_number(df)
print(df.head())

# send sms to vehicle owner
def send_sms(df):
    '''
    send sms to vehicle owner
    '''
    for i in df:
        print('send sms to vehicle owner:{}'.format(i))
print("-" * 40)
print('Send Sms')
send_sms(df)




