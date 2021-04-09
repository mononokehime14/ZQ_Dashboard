import sys


import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Query


from apps.models import ZQRaw
from apps.settings import DB_URI

CHUNK_SIZE = 4000

engine = create_engine(DB_URI)
session = sessionmaker(bind=engine)()

def get_chunk(df, n):
    if n < 1:
        raise ValueError('Minimum chunk size is 1')

    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(df), n):
        yield df[i:i + n]

def batch_insert(df, chunk_size, session):

    ind = 0
    num_inserted = 0
    for chunk in get_chunk(df, chunk_size):
        try:
            session.bulk_save_objects(
                    [ ZQRaw(**d.to_dict()) for r, d in chunk.iterrows() ]
                )
            session.commit()
            num_inserted += len(chunk)
        except:
            session.rollback()
            print("We encouter unknown situation at chunk {} ({} - {})".format(ind, chunk_size*ind, (ind+1)*chunk_size-1))
            raise
        finally:
            session.close()

        ind += 1

    return num_inserted


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
    df['notification_no'] = df['notification_no'].astype(str)
    num_inserted = batch_insert(df, CHUNK_SIZE, session)
    print(num_inserted, len(df))
    assert(num_inserted == len(df))


