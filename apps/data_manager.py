import dash_core_components as dcc
import pandas as pd
import numpy as np
import os
import json


# def get_equipment_data():
#     eq_df = pd.read_csv('data/Preprocessed Data/equipment.csv')
#     eq_alarm_df = pd.read_csv('data/Assessed Data/equipment_alarm.csv')
#
#     df = eq_df.merge(eq_alarm_df, on="serialNo", how="left")
#     return df

def get_dummy_data():
    return pd.DataFrame()
