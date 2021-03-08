import sys


import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql import exists

from apps.models import Cell
from apps.models import ZQRaw
from apps.settings import DB_URI
from scripts.fixture import batch_insert
from apps.data_manager import find_consecutive_false


CHUNK_SIZE = 4000

engine = create_engine(DB_URI)
session = sessionmaker(bind=engine)()


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
            parse_dates=['notification_date'],
            dayfirst=True
        )

        assert(
            len(df.columns) == len(ZQRaw.__table__.columns.keys())
        )
    except Exception as e:
        print(e)
        sys.exit(2)

    to_be_inserted = []
    for i, r in df.iterrows():
        if session.query(exists().where(ZQRaw.notification_no == r['notification_no'])).scalar():
            continue
        to_be_inserted.append(ZQRaw(**r.to_dict()))

    if len(to_be_inserted):
        try:
            session.bulk_save_objects(to_be_inserted)
            session.commit()
            num_inserted += len(chunk)
        except:
            session.rollback()
            print("We encouter unknown situation at chunk {} ({} - {})".format(ind, chunk_size*ind, (ind+1)*chunk_size-1))
            raise
        finally:
            session.close()


    # calculate consecutive False for each meter
    meter_ids = df.meter_no.unique()
    results = session.query(ZQRaw).filter(
        ZQRaw.meter_no.in_(meter_ids)
    ).all()

    df1 = pd.DataFrame.from_records([ r.to_dict() for r in results])
    
    group_dfs = []
    for n, g in df1.groupby(['meter_no', 'contract_acct']):
        _  = find_consecutive_false(g)
        group_dfs.append(_)

    print('num of groups: {}'.format(len(group_dfs)))

    df2 = pd.concat(group_dfs)

    summary = {
        'ignore': 0,
        'insert': 0,
        'update': 0,
    }

    for i, r in df2.iterrows():

        _ = session.query(Cell).filter(Cell.notification_no == r['notification_no']).all()
        if len(_) > 1:
            raise ValueError('duplicated primary key {}'.format(r['notification_no']))
        if len(_) == 0:
            # insert
            obj = Cell(**r.to_dict())
            session.add(obj)
            session.commit()
            summary['insert'] += 1
        else:
            if r['consecutive_false'] != _[0].consecutive_false:
                # update
                _[0].consecutive_false = r['consecutive_false']
                session.commit()
                summary['update'] += 1
            else:
                summary['ignore'] += 1
                continue
    print(summary)
