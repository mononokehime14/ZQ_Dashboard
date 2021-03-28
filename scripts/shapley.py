import sys
from dateutil.relativedelta import relativedelta
import json

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


if __name__ == "__main__":
    print(json.dumps(test_shap_value))
    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
    else:
        print('You did not specify the file path to load')
        sys.exit(1)

    try:
        df = pd.read_csv(
            input_file_path,
            sep=',',
            parse_dates=['notification_date'],
            dayfirst=True
        )
        print("sucessful")

        assert(
            len(df.columns) == len(Cell.__table__.columns.keys())
        )
    except Exception as e:
        print(e)
        sys.exit(2)

    #determine rows to update shap
    num_updated = 0
    for chunk in get_chunk(df, CHUNK_SIZE):
        for i, r in chunk.iterrows():
            print(r)
            if session.query(exists().where(Cell.notification_no == r['notification_no'])).scalar():
                _ = session.query(Cell).filter(Cell.notification_no == r['notification_no']).all()
                if len(_) > 1:
                    raise ValueError('duplicated primary key {}'.format(r['notification_no']))
                
                _[0].shap = json.dumps(test_shap_value)

                session.commit()
            
        try:
            session.commit()
            num_updated += len(chunk)
        except:
            session.rollback()
            print("We encouter unknown situation at chunk {} ({} - {})".format(ind, chunk_size*ind, (ind+1)*chunk_size-1))
            raise
        finally:
            session.close()
    print(num_updated)



    # calculate consecutive False for each meter
    # meter_ids = df.meter_no.unique()
    # results = session.query(ZQRaw).filter(
    #     ZQRaw.meter_no.in_(meter_ids)
    # ).all()

    # df1 = pd.DataFrame.from_records([ r.to_dict() for r in results])

    # group_dfs = []
    # for n, g in df1.groupby(['meter_no', 'contract_acct']):
    #     _  = find_consecutive_false_for_months(g)
    #     group_dfs.append(_)

    # print('num of groups: {}'.format(len(group_dfs)))

    # df2 = pd.concat(group_dfs)

    # ind = 0
    # num_inserted = 0
    # for chunk in get_chunk(df2, CHUNK_SIZE):
    #     summary = {
    #         'ignore': 0,
    #         'insert': 0,
    #         'update': 0,
    #     }

    #     for i, r in chunk.iterrows():
    #         _ = session.query(Cell).filter(Cell.notification_no == r['notification_no']).all()
    #         if len(_) > 1:
    #             raise ValueError('duplicated primary key {}'.format(r['notification_no']))
    #         if len(_) == 0:
    #             # insert
    #             obj = Cell(**r.to_dict())
    #             session.add(obj)
    #             session.commit()
    #             summary['insert'] += 1
    #         else:
    #             ignore = True
    #             # update
    #             if r['consecutive_false'] != _[0].consecutive_false :
    #                 _[0].consecutive_false = r['consecutive_false']
    #                 ignore = False
    #                 # session.commit()
    #             if r['consec_false_1month'] != _[0].consec_false_1month :
    #                 _[0].consec_false_1month = r['consec_false_1month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_2month'] != _[0].consec_false_2month:
    #                 _[0].consec_false_2month = r['consec_false_2month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_3month'] != _[0].consec_false_3month:
    #                 _[0].consec_false_3month = r['consec_false_3month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_4month'] != _[0].consec_false_4month:
    #                 _[0].consec_false_4month = r['consec_false_4month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_5month'] != _[0].consec_false_5month:
    #                 _[0].consec_false_5month = r['consec_false_5month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_6month'] != _[0].consec_false_6month:
    #                 _[0].consec_false_6month = r['consec_false_6month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_7month'] != _[0].consec_false_7month:
    #                 _[0].consec_false_7month = r['consec_false_7month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_8month'] != _[0].consec_false_8month:
    #                 _[0].consec_false_8month = r['consec_false_8month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_9month'] != _[0].consec_false_9month:
    #                 _[0].consec_false_9month = r['consec_false_9month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_10month'] != _[0].consec_false_10month:
    #                 _[0].consec_false_10month = r['consec_false_10month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_11month'] != _[0].consec_false_11month:
    #                 _[0].consec_false_11month = r['consec_false_11month']
    #                 ignore = False
    #                 #session.commit()
    #             if r['consec_false_12month'] != _[0].consec_false_12month:
    #                 _[0].consec_false_12month = r['consec_false_12month']
    #                 ignore = False
    #                 #session.commit()
    #             session.commit()
    #             if ignore:
    #                 summary['ignore'] += 1
    #                 #continue
    #             else:
    #                 summary['update'] += 1
    #                 #continue

    #     try:
    #         session.commit()
    #         num_inserted += len(chunk)
    #     except:
    #         session.rollback()
    #         print("We encouter unknown situation at chunk {} ({} - {})".format(ind, chunk_size*ind, (ind+1)*chunk_size-1))
    #         raise
    #     finally:
    #         session.close()

    #     print(ind, summary)
    #     ind += 1
    # print(num_inserted)
