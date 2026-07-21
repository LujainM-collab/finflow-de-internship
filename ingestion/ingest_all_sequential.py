# importing raw csv file using the pandas library which will read and store the data in a DataFrame 
import pandas as pd
import os
import time 
import logging
from fredapi import Fred

class PaysimIngestionError(Exception):
    pass

class FredIngestionError(Exception):
    pass

class ComplaintsIngestionError(Exception):
    pass


def ingest_paysim():

    try:

        df= pd.read_csv("/Users/lujainmalash/finflow-de-internship/ingestion/paysim.csv")
        # validating the dtypes (snake case)
        #step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud

        df= df.rename(columns={"nameOrig": "name_orig", "oldbalanceOrg": 
                       "old_balance_org", "newbalanceOrig": "new_balance_orig","nameDest": "name_dest","oldbalanceDest":"old_balance_dest",
                       "newbalanceDest": "new_balance_dest",
                       "isFraud": "is_fraud", "isFlaggedFraud":"is_flagged_fraud"})

        print(df.dtypes)
        # change data type of is_fraud and is_flagged_fraud since in the output it shows that it is of type int64 but doesn't make sense since it is supposed to be of type boolean (true or false)
        df["is_fraud"]= df["is_fraud"].astype(bool)
        df["is_flagged_fraud"]= df["is_flagged_fraud"].astype(bool)
        
        print("shape:",(df.shape))
        print("head:", df.head(10))
        print("columna:", df.columns)
        df.info()


        #saving into a parquet file    
        df.to_parquet("data/processed/transactions.parquet")
        return df
        

    except FileNotFoundError as file_error:
        print("ERROR: file csv.paysim not found",file_error)
        return None
    except PermissionError as parquet_error:
        print("ERROR: coudn't save to parquet ", parquet_error)
        return None
    except PaysimIngestionError as paysim_error :
        print("ERROR: Paysim ingestion error", paysim_error)
    except Exception as error:
        print("ERROR:", error)
        return None
        

def ingest_fred():
   
    try:
        
        fred = Fred(api_key= "fc0793239579da3494583c938fc9138b")
        #saving each in a data/raw/macro 

        os.makedirs("data/raw/macro", exist_ok=True)
        ids= ['CPIAUCSL', 'UNRATE','DEXUSEU']
        result= {}
        for series_id in ids:
            data= fred.get_series(series_id)
            
            print("shape:", data.shape)
            print("head:", data.head(3))
            data.info()
            # save each in a Csv "data/raw/macro" file
            data.to_csv("data/raw/macro/" + series_id + ".csv")
            result[series_id]= data 
        
        return result 
    
    except ConnectionError as connection_error:
        print("ERROR: failed to connect to FRED", connection_error)
        return None
    except FredIngestionError as fred_error:
        print('ERROR: Fred ingestion error:', fred_error)
  
    except Exception as error:
        print("ERROR:", error)
        return None
        
#def ingest_complaints():
    #try:

        #df= pd.read_csv("url")

        #os.makedirs("data/processed", exist_ok=True)
        #df.to_parquet("data/processed/complaints.parquet")
    
        #return df
    #except ComplaintsIngestionError as complaints_error:
        #print ("ERROR: failed complaints ingestion:", complaints_Error)

    #except Exception as error:
        #print("ERROR:", error)

def run_sequential():

    t1= time.perf_counter()
    ingest_paysim()
    ingest_fred()
    #ingest_complaints()
    t2= time.perf_counter()
    duration= t2-t1
    print("sequential_Duration:", duration)

run_sequential()
#try0= ingest_paysim()
#print(try0)
#try1= ingest_fred()
#print(try1)



