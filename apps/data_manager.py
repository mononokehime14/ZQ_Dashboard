from apps.models import Cell
import os
import json


import pandas as pd
import numpy as np
from sqlalchemy import create_engine, String, Column, or_, and_, update, asc
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.types import Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists, func
import datetime as dt
import timeit


from apps.models import Cell
from apps.settings import DB_URI

engine = create_engine(DB_URI)

Base = declarative_base()

class DBmanager:
    def __init__(self):
        self.engine = engine
        self.base = Base
        self.session = sessionmaker(bind = engine)()
    
    # def test_add_multiple(self):
    #     session = self.session
    #     try:
    #         session.add_all([
    #             Cell(notification_type = 'ZQ',notification_no = 'qwer3',notification_date = '2021-01-08 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= True,consecutive_false = 0),
    #             Cell(notification_type = 'ZQ',notification_no = 'qwer4',notification_date = '2021-01-09 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= False,consecutive_false = 1),
    #             Cell(notification_type = 'ZQ',notification_no = 'qwer1',notification_date = '2021-01-10 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= False,consecutive_false = 2),
    #             Cell(notification_type = 'ZQ',notification_no = 'qwer2',notification_date = '2021-01-11 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= False,consecutive_false = 3),
    #         ])
    #         session.commit()
    #     except:
    #         session.rollback()
    #         raise
    #     finally:
    #         session.close()
    #     return 0
    
    def query(self,input_text):
        session = self.session
        starttime = timeit.default_timer()
        input_text = input_text.strip()
        df = pd.read_sql(session.query(Cell).filter(or_(Cell.notification_no == input_text, Cell.meter_no == input_text, Cell.contract_acct == input_text)).statement,session.bind)
        # statement = select(Cell).where(or_(Cell.notification_no == input_text, Cell.meter_no == input_text, Cell.contract_acct == input_text))
        # conn = self.engine.connect()
        # result = conn.execute(statement)
        # df = pd.DataFrame(result.fetchall())
        # df.columns = result.keys()
        print("Searching done, used time:", timeit.default_timer() - starttime)
        return df

    def trace_records(self,start_date):
        session = self.session
        df = pd.read_sql(session.query(Cell).filter(Cell.notification_date == start_date).statement, session.bind)
        # statement = select(Cell).where(Cell.notification_date == start_date)
        # conn = self.engine.connect()
        # result = conn.execute(statement)
        # df = pd.DataFrame(result.fetchall())
        # df.columns = result.keys()

        # acct_list = pd.concat([df_at_that_date['meter_no'], df_at_that_date['contract_acct']])
        # acct_list = acct_list.tolist()
        # df= pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date <= start_date, Cell.notification_date >= end_date,Cell.consecutive_false > 0,(Cell.meter_no.in_(acct_list) | Cell.contract_acct.in_(acct_list)))).statement, session.bind)
        # #df['notification_date'] = df['notification_date'].dt.to_pydatetime()
        # #df['notification_date'] = pd.to_datetime(df['notification_date'])
        # df.sort_values(by = 'notification_date',ascending=True,inplace = True,axis =0)
        # group_dfs = []
        # for n, g in df.groupby(['meter_no', 'contract_acct']):
        #     _  = find_consecutive_false(g)
        #     group_dfs.append(_)
        # if not group_dfs:
        #     return None
        # df1 = pd.concat(group_dfs)
        # df1 = df1[df1['notification_date'] == start_date]
        # df_sup = pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date == start_date, Cell.consecutive_false == 0)).statement,session.bind)
        # df2 = pd.concat([df1,df_sup])
        return df
    
    def query_in_timeperiod(self,start,end):
        session = self.session
        df = pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date >= start, Cell.notification_date <= end)).statement,session.bind)
        # statement = select(Cell).where(Cell.notification_date.between(start,end))
        # conn = self.engine.connect()
        # result = conn.execute(statement)
        # df = pd.DataFrame(result.fetchall())
        # df.columns = result.keys()
        return df
    
    def query_in_timeperiod_distinct_user(self,start,end):
        within_range = select([
                        Cell
                        ]).where(Cell.notification_date.between(start,end)).cte("within_range")

        latest_distinct = select([
                            within_range.c.meter_no,
                            within_range.c.contract_acct,
                            func.max(within_range.c.notification_date).label("laterest_ticket")
                        ]).group_by(within_range.c.meter_no,within_range.c.contract_acct).cte("latest_distinct")
        
        statement = select(within_range).\
                where(and_(
                    within_range.c.meter_no.in_(select(latest_distinct.c.meter_no)),
                    within_range.c.contract_acct.in_(select(latest_distinct.c.contract_acct)),
                    within_range.c.notification_date.in_(select(latest_distinct.c.laterest_ticket)),
                ))

        conn = self.engine.connect()
        result = conn.execute(statement)
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()
        print(df)
        return df
    
    def fetch_all(self):
        session = self.session
        df = pd.read_sql(session.query(Cell).statement,session.bind)
        # statement = select(Cell)
        # conn = self.engine.connect()
        # result = conn.execute(statement)
        # df = pd.DataFrame(result.fetchall())
        # df.columns = result.keys()
        return df

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
    
    def get_shapley_value(self,input_text):
        session = self.session
        input_text = input_text.strip()
        shap_json = session.query(Cell.shap).filter(Cell.notification_no == input_text).scalar()
        if shap_json is None:
            return None
        # print(type(shap_json))
        return json.loads(shap_json)



        


        
        



