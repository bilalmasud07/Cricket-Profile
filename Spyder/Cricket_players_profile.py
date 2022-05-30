# -*- coding: utf-8 -*-
"""
Created on Sat May 17 16:39:11 2022

@author: bilal
"""


import pandas as pd
import numpy as np
from datetime import date


def read_file():
    
    try:
        #reading file from github
        url = 'https://raw.githubusercontent.com/bilalmasud07/Cricket-Profile/main/Data/cricket_data.csv'
        
        df = pd.read_csv(url, low_memory=False)
        
    except Exception as e:
        print("Something went wrong when reading the file:", e)
    
    return df

def from_dob_to_age(born):
    #calculating the age
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def splitting_column(data_Frame, col_split, new_col):

    try:
        
        if col_split == 'Born':
            place = 'Birthplace'
        else:
            place = 'Deathplace'
        
        #splitting the column into 3 columns.
        data_Frame[['Month_Date', 'Year', place]] = data_Frame[col_split].str.split(',|,', 2, expand =True) 
        
        #removing empty spaces from the column year
        data_Frame['Year'] = data_Frame['Year'].str.strip()
        
        #Checking if the year column contains non-numeric values(birth/death place) than store those values to column place.
        data_Frame[place] = np.where( data_Frame['Year'].str.isalpha() == True, data_Frame['Year'] + "," + data_Frame[place] , data_Frame[place] )
        
        #removing the non-numeric vlaues from column Year
        data_Frame['Year'] = np.where( data_Frame['Year'].str.isdigit() == True, data_Frame['Year'], "" )
        
        #combining columns Month_Date and Year to get 'DOB'(date of death) and 'DOD'(date of death)
        data_Frame[new_col] = data_Frame["Month_Date"].str.cat(data_Frame["Year"], sep=" ")
        
        #checking of the column new_col only has number values with out the Month and date then adding the default January 1
        # in the DOB, DOD
        data_Frame[new_col] = np.where( data_Frame[new_col].str.isdigit() == True, "January 1 " + data_Frame[new_col].astype(str) , data_Frame[new_col] )

        #removing empty spaces from column
        data_Frame[new_col] = data_Frame[new_col].str.strip()
        
        #converting the column DOB and DOD into date formate
        data_Frame[new_col] = pd.to_datetime(data_Frame[new_col], errors='coerce', format='%B %d %Y')
        
        #converting the column Month_Date and Year
        data_Frame.drop(['Month_Date','Year'], inplace=True, axis=1)
        
    except Exception as e:
        print("Something went wrong when splitting the column: ",col_split, e)

    return data_Frame

def positioning_column(df, col_name, p):
    try:
        #changing the position of cloumn in the data-frame
        col = df.pop(col_name)
        df = df.insert(p, col.name, col)
    except Exception as e:
        print("Something went wrong when positioning the column: ", col_name, e)
        
def filtering_data(data_Frame):
    
    try:

        #to infer better data type for input object column
        data_Frame = data_Frame.infer_objects()

        # dropping ALL duplicate values
        data_Frame.drop_duplicates(subset = "ID", keep = False, inplace = True)

        #removing empty spaces from column
        data_Frame['Born'] = data_Frame['Born'].str.strip()

        #calling the function splitting_column to split the column
        data_Frame = splitting_column(data_Frame, 'Born', 'DOB')
        data_Frame = splitting_column(data_Frame, 'Died', 'DOD')

        #Checking if the Died colums has values then replacing with 1 and 0 in case Died has no vlues.
        #Indicating Alive or Died
        data_Frame['Died'] = data_Frame['Died'].fillna('0')
        data_Frame.loc[data_Frame['Died'] != '0', 'Died'] = '1'

        #extracting the age from the column 'Deathplace' storing it in the column of 'Age_of_Dead'
        data_Frame["AGE_of_Dead"] = data_Frame["Deathplace"].str.extract('(aged\s\d+\syears)')
        data_Frame["AGE_of_Dead"] = data_Frame["AGE_of_Dead"].str.extract('(\d+)')

        #Checking the status of Dead if its '1' then place with nan else calculating the age from DOB and storing it in column Age
        data_Frame['Age'] = np.where(data_Frame['Died'] == '1', np.nan,
                data_Frame['DOB'].apply(lambda x: from_dob_to_age(x)))

        #replacing Age with -1 to and checking if teh Age is -1 then shift all the values from Age_of_Dead column to Age column
        data_Frame['Age'] = data_Frame['Age'].fillna(-1)
        data_Frame['Age'] = np.where( data_Frame['Age'] == -1, data_Frame['AGE_of_Dead'] , data_Frame['Age'] )

        #converting the age column type into integer
        data_Frame["Age"] = data_Frame["Age"].astype(float).astype('Int64')

        #changing the indexing of the columns
        positioning_column(data_Frame, 'DOB', 4)
        positioning_column(data_Frame, 'Birthplace', 5)
        positioning_column(data_Frame, 'Died', 6)
        positioning_column(data_Frame, 'DOD', 7)
        positioning_column(data_Frame, 'Age', 8)

        #droping unnecessary columns
        data_Frame.drop(['Deathplace', 'AGE_of_Dead', 'Current age','Born', 'Education','Height','Nickname','Relation','In a nutshell'], inplace=True, axis=1)
        
    except Exception as e:
        print("Something went wrong when splitting the column: ", e)
    
    return data_Frame

def changing_types(data_Frame):
    
    #replacing * with '' to clean values such as 11* --> 11, 400* to 400
    data_Frame['BATTING_Tests_HS'] = data_Frame['BATTING_Tests_HS'].str.replace('*','', regex=True)
    
    for col_name in data_Frame.columns:
        try:
            #list of columns which types needs to be changed
            columsList = ['_Ave','_SR','_Econ','_Mat','_Inns','_NO','Runs','_HS','_BF','_100','_50','_4s','_6s','_6s','_Ct','_St','_Balls','_Wkts','_4w','_5w','_10']
            
            #checking if the column name exists in above list then change its type to float
            if (any(ext in col_name for ext in columsList)):
                data_Frame[col_name] = pd.to_numeric(data_Frame[col_name], errors='coerce', downcast='float')

        except Exception as e:
            print("Something went wrong when changing the type of column: ", e)
            
    return data_Frame

def col_desc(data_Frame):
    mean_val_test = pd.to_numeric(data_Frame['BATTING_Tests_Runs'], errors='coerce').mean()
    print("Mean of BATTING_Tests_Runs: ", mean_val_test,'\n')
    std_val_test = pd.to_numeric(data_Frame['BATTING_Tests_Runs'], errors='coerce').std() 
    print("Standard Deviation of BATTING_Tests_Runs: ", std_val_test, '\n')
    freq = data_Frame['COUNTRY'].value_counts()
    print(freq)

if __name__ == "__main__":
   
    data_Frame = read_file()
   
    data_Frame = filtering_data(data_Frame)
    
    data_Frame = changing_types(data_Frame)
    
    col_desc(data_Frame)
    
    data_Frame.to_csv(r'D:\Final.csv', date_format='%Y-%b-%d')
    

   