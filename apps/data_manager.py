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
    
    def query(self,input_text):
        """This function searches in notificationlist data table for any data that has
        same notification number, meter account or contract account as input_text

        Args:
            input_text (string): what we want to search

        Returns:
            df: all matching data as dataframe type
        """
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
        """This function queries all data from certain datetime

        Args:
            start_date (datetime): starttime

        Returns:
            df: dataframe type of data
        """
        session = self.session
        df = pd.read_sql(session.query(Cell).filter(Cell.notification_date == start_date).statement, session.bind)
        return df
    
    def query_in_timeperiod(self,start,end):
        """This function fetch all data in a given time period from notificationlist data table

        Args:
            start (datetime): start time
            end (datetime): end time

        Returns:
            df: dataframe type of data
        """
        session = self.session
        df = pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date >= start, Cell.notification_date <= end)).statement,session.bind)
        return df
    
    def query_in_timeperiod_distinct_user(self,start,end):
        """This function is trying to query with CTE query but seems not very successful"""
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
        """This function get all data from notificationlist data table

        Returns:
            df: dataframe type of all data
        """
        session = self.session
        df = pd.read_sql(session.query(Cell).statement,session.bind)
        return df

    def find_max_date(self):
        """This function finds the latest date possible from all notifications in notificationlist data table.

        Returns:
            datetime: the latest datetime
        """
        session = self.session
        result = session.query(func.max(Cell.notification_date)).scalar()
        if result is None:
            result = dt.datetime.now()
        return result.date()

    def find_min_date(self):
        """This function finds the earliest date possible from all notifications in notificationlist data table.

        Returns:
            datetime: the earliest datetime
        """
        session = self.session
        result = session.query(func.min(Cell.notification_date)).scalar()
        if result is None:
            result = dt.datetime.now()
        return result.date()
    
    def get_shapley_value(self,input_text):
        """This function queries SHAP values from notificationlist data table

        Args:
            input_text (string): notification number

        Returns:
            dictionary: SHAP values read from jsonb
        """
        session = self.session
        input_text = input_text.strip()
        shap_json = session.query(Cell.shap).filter(Cell.notification_no == input_text).scalar()
        if shap_json is None:
            return None
        # print(type(shap_json))
        return json.loads(shap_json)



        


        
        



