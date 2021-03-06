import sys
from dateutil.relativedelta import relativedelta
import json
import pickle
import h5py

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql import exists

from apps.models import Cell
from apps.models import ZQRaw
from apps.settings import DB_URI
from scripts.fixture import get_chunk
#from apps.data_manager import find_consecutive_false

test_shap_value = {"Feature 1":0.94,"Feature 2":0.77, "Feature 3":0.45,"Feature 4":0.44,"Feature 5":-0.35,"Feature 6":-0.34,"Feature 7":0.22,"Feature 8":0.19,"Feature 9":0.13,"Feature 10":0.11}
CHUNK_SIZE = 4000

engine = create_engine(DB_URI)
session = sessionmaker(bind=engine)()

class StrToBytes:
    def __init__(self, fileobj):
        self.fileobj = fileobj
    def read(self, size):
        return self.fileobj.read(size).encode()
    def readline(self, size=-1):
        return self.fileobj.readline(size).encode()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
    else:
        print('You did not specify the file path to load')
        sys.exit(1)

    try:
        df = pd.read_csv(
            input_file_path,
            sep=',',
            # parse_dates=['notification_date'],
            # dayfirst=True
        )

    except Exception as e:
        print(e)
        sys.exit(2)
    df['notification_no'] = df['notification_no'].astype(str)
    print(df['shap_values'].dtype)
    #update shap for all rows in df
    num_updated = 0
    for chunk in get_chunk(df, CHUNK_SIZE):
        for i, r in chunk.iterrows():
            # we will first look into notificationlist table, to check whether the notification number is in the store
            #if it is already there, we can update the SHAP values
            if session.query(exists().where(Cell.notification_no == r['notification_no'])).scalar():
                _ = session.query(Cell).filter(Cell.notification_no == r['notification_no']).all()
                if len(_) > 1:
                    raise ValueError('duplicated primary key {}'.format(r['notification_no']))

                #update SHAP values
                if _[0].shap != r['shap_values']:
                    _[0].shap = r['shap_values']    
        try:
            session.commit()
            num_updated += len(chunk)
        except:
            session.rollback()
            print("We encouter unknown situation at chunk {} ({} - {})".format(ind, chunk_size*ind, (ind+1)*chunk_size-1))
            raise
        finally:
            session.close()
    print('num updated: '+ str(num_updated))
