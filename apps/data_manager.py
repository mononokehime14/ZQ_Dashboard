import os


import pandas as pd
import numpy as np
from sqlalchemy import create_engine,String,Column,or_,and_,update,asc
from sqlalchemy.orm import sessionmaker,Query
from sqlalchemy.types import Integer,String,Text,DateTime,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists, func
import datetime as dt
import timeit
from pandarallel import pandarallel


from apps.models import Cell
from apps.settings import DB_URI

# conn_url = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
# conn_url = os.environ.get('DB_URI', "postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db")
engine = create_engine(DB_URI)

Base = declarative_base()

def find_consecutive_false(gdf):

    consecutive_false_dict = {}
    gdf = gdf.sort_values(by='notification_date', ascending=True)
    # global false_count
    false_count = 0 
    for i, r in gdf.iterrows():
        if r['prediction'] == False:
            false_count += 1
        elif r['prediction'] == True:
            false_count = 0
        consecutive_false_dict[r['notification_no']] = false_count

    gdf['consecutive_false'] = gdf['notification_no'].apply(lambda x: consecutive_false_dict.get(x))
    return gdf

class DBmanager:
    #conn = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
    #Base = declarative_base()
    def __init__(self):
        self.engine = engine
        self.base = Base
        self.session = sessionmaker(bind = engine)()
        # self.engine = create_engine(conn)
        # Base = declarative_base(self.engine)
        # self.base = Base
        # session = sessionmaker(self.engine)()
        # self.session = session
    
    def test_add_multiple(self):
        session = self.session
        try:
            session.add_all([
                Cell(notification_type = 'ZQ',notification_no = 'qwer3',notification_date = '2021-01-08 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= True,consecutive_false = 0),
                Cell(notification_type = 'ZQ',notification_no = 'qwer4',notification_date = '2021-01-09 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= False,consecutive_false = 1),
                Cell(notification_type = 'ZQ',notification_no = 'qwer1',notification_date = '2021-01-10 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= False,consecutive_false = 2),
                Cell(notification_type = 'ZQ',notification_no = 'qwer2',notification_date = '2021-01-11 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= False,consecutive_false = 3),
            ])
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return 0
    
    # def update_consecutive_false(self):
    #     session = self.session
    #     starttime = timeit.default_timer()
    #     column_exist = session.query(session.query(Cell.consecutive_false).exists()).scalar()
    #     if column_exist:
    #         #new_data = session.query(Cell).filter(Cell.consecutive_false == None).all()
    #         df_nan_in_cf = pd.read_sql(session.query(Cell).filter(Cell.consecutive_false == None).statement, session.bind)
    #         print("Getting target list, used time:", timeit.default_timer() - starttime)
    #         if not df_nan_in_cf.empty:
    #             acct_list = pd.concat([df_nan_in_cf['meter_no'], df_nan_in_cf['contract_acct']])
    #             acct_list = acct_list.tolist()
    #             #no_list = df_nan_in_cf['notification_no'].tolist()
    #             df = pd.read_sql(session.query(Cell).filter(or_(Cell.meter_no.in_(acct_list),Cell.contract_acct.in_(acct_list))).statement, session.bind)
    #             print("Loading done, used time:", timeit.default_timer() - starttime)
    #             # df.sort_values(by = 'notification_date',ascending=True,inplace = True,axis =0)
    #             group_dfs = []
    #             for n, g in df.groupby(['meter_no', 'contract_acct']):
    #                 _  = find_consecutive_false(g)
    #                 group_dfs.append(_)
    #             df = pd.concat(group_dfs)
    #             print("Calculation done, used time:", timeit.default_timer() - starttime)
                # try:
                #     for key,value in consecutive_false_dic.items():
                #         user = session.query(Cell).filter(Cell.notification_no == key).update({"consecutive_false":value})
                #     # for row in session.query(Cell).filter(Cell.notification_no.in_(consecutive_false_dic.keys())).all():
                #     #     row.consecutive_false = consecutive_false_dic[row.notification_no]
                #     session.commit()
                # except:
                #     session.rollback()
                #     print("We encouter unknown situation")
                #     raise
                # finally:
                #     session.close()
                # print("Uploading done, used time:", timeit.default_timer() - starttime)
        # else:
        #     self.update_consecutive_false_for_whole()
        # return 0

    # def update_consecutive_false_for_whole(self):
    #     engine = self.engine
    #     print("Whole table update")
    #     starttime = timeit.default_timer()
    #     cwd = os.getcwd()  # Get the current working directory (cwd)
    #     files = os.listdir(cwd)  # Get all the files in that directory
    #     print("Files in %r: %s" % (cwd, files))
    #     df = pd.read_csv('apps/data/test_incremental.csv',parse_dates=['notification_date'],dayfirst=True)
    #     #df = pd.read_sql_table('notificationlist',con = engine)
    #     df['notification_date'] = pd.to_datetime(df['notification_date'])
    #     print("Loading target list done, used time:", timeit.default_timer() - starttime)
    #     starttime = timeit.default_timer()
    #     group_dfs = []
    #     for n, g in df.groupby(['meter_no', 'contract_acct']):
    #         _  = find_consecutive_false(g)
    #         group_dfs.append(_)
    #     df = pd.concat(group_dfs)
    #     print("Calculation done, used time:", timeit.default_timer() - starttime)

    #     starttime = timeit.default_timer()
    #     session = self.session
    #     try:
    #         for row in session.query(Cell).all():
    #             row.consecutive_false = consecutive_false_dic[row.notification_no]
    #         session.commit()
    #     except:
    #         session.rollback()
    #         print("We encouter unknown situation")
    #         raise
    #     finally:
    #         session.close()
    #     print("Uploading done, used time:", timeit.default_timer() - starttime)

    #     return df
    
    def query(self,input_text):
        session = self.session
        starttime = timeit.default_timer()
        df = pd.read_sql(session.query(Cell).filter(or_(Cell.notification_no == input_text, Cell.meter_no == input_text, Cell.contract_acct == input_text)).statement,session.bind)
        print("Searching done, used time:", timeit.default_timer() - starttime)
        return df

    def trace_records(self,start_date,end_date):
        session = self.session
        df_at_that_date = pd.read_sql(session.query(Cell).filter(Cell.notification_date == start_date).statement, session.bind)
        acct_list = pd.concat([df_at_that_date['meter_no'], df_at_that_date['contract_acct']])
        acct_list = acct_list.tolist()
        df= pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date <= start_date, Cell.notification_date >= end_date,Cell.consecutive_false > 0,(Cell.meter_no.in_(acct_list) | Cell.contract_acct.in_(acct_list)))).statement, session.bind)
        #df['notification_date'] = df['notification_date'].dt.to_pydatetime()
        #df['notification_date'] = pd.to_datetime(df['notification_date'])
        df.sort_values(by = 'notification_date',ascending=True,inplace = True,axis =0)
        group_dfs = []
        for n, g in df.groupby(['meter_no', 'contract_acct']):
            _  = find_consecutive_false(g)
            group_dfs.append(_)
        if not group_dfs:
            return None
        df1 = pd.concat(group_dfs)
        df1 = df1[df1['notification_date'] == start_date]
        df_sup = pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date == start_date, Cell.consecutive_false == 0)).statement,session.bind)
        df2 = pd.concat([df1,df_sup])
        return df2
    
    def query_in_timeperiod(self,start,end):
        session = self.session
        df = pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date >= start, Cell.notification_date <= end)).statement,session.bind)
        return df
    
    def fetch_all(self):
        session = self.session
        df = pd.read_sql_table('notificationlist',con = self.engine)
        return df

    def start_over(self):
        session = self.session
        try:
            # session.query(Cell).update({'consecutive_false':None})
            session.query(Cell.consecutive_false).delete()
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return 0

    def count_false(self):
        session = self.session
        return len(session.query(Cell).filter(Cell.prediction == False).all())

    def find_max_date(self):
        session = self.session
        result = session.query(func.max(Cell.notification_date)).scalar()
        if result is None:
            result = dt.datetime.now()
        return result.date()

    def find_min_date(self):
        session = self.session
        result = session.query(func.min(Cell.notification_date)).scalar()
        if result is None:
            result = dt.datetime.now()
        return result.date()

        


        
        



