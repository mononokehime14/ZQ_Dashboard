import pandas as pd
import numpy as np
from sqlalchemy import create_engine,String,Column,or_,and_,update
from sqlalchemy.orm import sessionmaker,Query
from sqlalchemy.types import Integer,String,Text,DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime as dt

conn_url = 'postgresql+psycopg2://postgres:1030@172.17.0.2/dash_db'
engine = create_engine(conn_url)

Base = declarative_base()

class Cell(Base):
    __tablename__ = 'notificationlist'
    notification_type = Column(Text,nullable =False)
    notification_no = Column(Text,nullable =False,primary_key= True)
    notification_date = Column(DateTime(timezone = False),nullable =False)
    contract_acct = Column(Text,nullable = False)
    cause_code = Column(Text,nullable = False)
    meter_no = Column(Text,nullable = False)
    prediction = Column(Text)
    consecutive_false = Column(Integer)

#Base.metadata.create_all(bind = engine,checkfirst = True)

    # def __repr__(self):
    #     return "type:{self.type},no:{self.number}, date:{self.date},contract:{self.contract_acct},cause_code:{self.cause_code},meter:{self.meter_no},prediction:{self.prediction},consecutive_false:{self.consecutive_false}"

def find_consecutive_false(group,consecutive_false_dic):
    if(len(group) > 1):
        #group.sort_values(by = 'notification_date',,ascending=True)
        false_count = 0
        for index,row2 in group.iterrows():
            if row2['prediction'] == 'False':
                false_count += 1
            elif row2['prediction'] == 'True':
                false_count = 0
            consecutive_false_dic[row2['notification_no']] = false_count
    else:
        for i in group['notification_no']:
            consecutive_false_dic[i] = 0
    return consecutive_false_dic

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
                Cell(notification_type = 'ZQ',notification_no = 'qwer3',notification_date = '2020-04-12 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= 'True'),
                Cell(notification_type = 'ZQ',notification_no = 'qwer4',notification_date = '2020-04-13 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= 'False'),
                Cell(notification_type = 'ZQ',notification_no = 'qwer1',notification_date = '2020-04-10 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= 'False'),
                Cell(notification_type = 'ZQ',notification_no = 'qwer2',notification_date = '2020-04-11 00:00:00',contract_acct = 'qwer',cause_code = 'Meter Stopped/Stuck',meter_no = 'qwer',prediction= 'False'),
            ])
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return 0
    
    def update_consecutive_false(self):
        session = self.session
        try:
            #new_data = session.query(Cell).filter(Cell.consecutive_false == None).all()
            df_nan_in_cf = pd.read_sql(session.query(Cell).filter(Cell.consecutive_false == None).statement, session.bind)
            acct_list = pd.concat([df_nan_in_cf['meter_no'], df_nan_in_cf['contract_acct']])
            acct_list = acct_list.tolist()
            #no_list = df_nan_in_cf['notification_no'].tolist()
            df = pd.read_sql(session.query(Cell).filter(or_(Cell.meter_no.in_(acct_list),Cell.contract_acct.in_(acct_list))).statement, session.bind)
            df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')
            consecutive_false_dic = {}
            #df['notification_date'] = df['notification_date'].dt.to_pydatetime()
            #df['notification_date'] = pd.to_datetime(df['notification_date'])
            df.sort_values(by = 'notification_date',ascending=True,inplace = True,axis =0)
            df.groupby(['meter_no','contract_acct']).apply(lambda x: find_consecutive_false(x,consecutive_false_dic))
            # for i in new_data:
            #     temp = consecutive_false_dic[i.notification_no]
            #     print(temp)
            #     i.consecutive_false = temp
            
            #session.commit()
            #     session.commit()
            
            #session.query(Cell).filter(Cell.consecutive_false == None).update(consecutive_false_dic,synchronize_session=False)
            for key,value in consecutive_false_dic.items():
                user = session.query(Cell).filter(Cell.notification_no == key).update({"consecutive_false":value})
                session.commit()
                #setattr(user,key,value)
            
            # session.commit()
            # df_check = pd.read_sql(session.query(Cell).filter(Cell.meter_no == 'qwer').statement, session.bind)
            # print(df_check)
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return 0
    
    def query(self,input_text):
        session = self.session
        df = pd.read_sql(session.query(Cell).filter(or_(Cell.notification_no == input_text, Cell.meter_no == input_text, Cell.contract_acct == input_text)).statement,session.bind)
        df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')
        return df

    def trace_records(self,start_date,end_date):
        session = self.session
        df_at_that_date = pd.read_sql(session.query(Cell).filter(Cell.notification_date == start_date).statement, session.bind)
        acct_list = pd.concat([df_at_that_date['meter_no'], df_at_that_date['contract_acct']])
        acct_list = acct_list.tolist()
        df= pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date <= start_date, Cell.notification_date >= end_date,Cell.consecutive_false > 0,(Cell.meter_no.in_(acct_list) | Cell.contract_acct.in_(acct_list)))).statement, session.bind)
        df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')
        consecutive_false_dic = {}
        #df['notification_date'] = df['notification_date'].dt.to_pydatetime()
        #df['notification_date'] = pd.to_datetime(df['notification_date'])
        df.sort_values(by = 'notification_date',ascending=True,inplace = True,axis =0)
        df.groupby(['meter_no','contract_acct']).apply(lambda x: find_consecutive_false(x,consecutive_false_dic))
        df['consecutive_false']= df['notification_no'].apply(lambda x: consecutive_false_dic[x])
        df = df[df['notification_date'] == start_date]
        df_sup = pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date == start_date, Cell.consecutive_false == 0)).statement,session.bind)
        df = pd.concat([df,df_sup])
        df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')  
        return df
    
    def query_in_timeperiod(self,start,end):
        session = self.session
        df = pd.read_sql(session.query(Cell).filter(and_(Cell.notification_date >= start, Cell.notification_date <= end)).statement,session.bind)
        df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')
        return df
    
    def fetch_all(self):
        session = self.session
        df = pd.read_sql_table('notificationlist',con = self.engine)
        df['prediction'] = df['prediction'].apply(lambda x : 'False' if ((x == 'FALSE')|(x == 'False')) else 'True')
        return df

        


        
        

# def try_add_multiple():

    
    



# def get_equipment_data():
#     eq_df = pd.read_csv('data/Preprocessed Data/equipment.csv')
#     eq_alarm_df = pd.read_csv('data/Assessed Data/equipment_alarm.csv')
#
#     df = eq_df.merge(eq_alarm_df, on="serialNo", how="left")
#     return df

# def get_dummy_data():
#     return pd.DataFrame()

# def get_engine(db, user, host, port, passwd):

#     url = 'postgresql+psycopg2:://{user}:{passwd}@{host}:{port}/{db}'.format(
#         user=user, passwd=passwd, host=host, port=port, db=db)
#     engine = sqlalchemy.create_engine(url)
#     return engine


