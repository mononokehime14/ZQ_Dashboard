import sys
from dateutil.relativedelta import relativedelta

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql import exists
import datetime as dt
from dateutil.relativedelta import relativedelta

from apps.models import Cell
from apps.models import ZQRaw
from apps.settings import DB_URI
from scripts.fixture import get_chunk
#from apps.data_manager import find_consecutive_false


CHUNK_SIZE = 4000

engine = create_engine(DB_URI)
session = sessionmaker(bind=engine)()

#month_list = ['one_month','two_month','three_month','four_month','five_month','six_month','seven_month', 'eight_month','nine_month','ten_month','eleven_month','twelve_month','whole']

def find_consecutive_false_for_months(gdf):

    # consecutive_false_dict = {
    #     'whole':{},
    #     'one_month':{},
    #     'two_month':{},
    #     'three_month':{},
    #     'four_month':{},
    #     'five_month':{},
    #     'six_month':{},
    #     'seven_month':{},
    #     'eight_month':{},
    #     'nine_month':{},
    #     'ten_month':{},
    #     'eleven_month':{},
    #     'twelve_month':{},
    # }
    print("New grp start ---------")
    consecutive_false_dict = {}
    gdf = gdf.sort_values(by='notification_date', ascending=True)
    # date_ruler = []
    # for i in range(12):
    #     current_date += relativedelta(months=-1)
    #     date_ruler.append(current_date)
    # print(date_ruler)

    #false_count = [0] * 13
    mem_list = [0] * 13
    date_buoy = gdf['notification_date'].iloc[0]
    first = True
    for i, r in gdf.iterrows():
        # if r['prediction'] == False:
        #     false_count += 1
        # elif r['prediction'] == True:
        #     false_count = 0
        point_pred = r['prediction']
        point_pos = r['notification_date']
        print(i)
        print(dt.datetime.strftime(point_pos,"%Y-%m-%d") + " " + str(point_pred))
        if first:
            first = False
            if not point_pred:
                mem_list = [1] * 13
            #date_buoy = point_pos
        else:
            loop_date = date_buoy + relativedelta(months=+1)
            loop_count = 0
            while (loop_date <= point_pos) & (loop_count < 12):
                loop_count += 1
                loop_date += relativedelta(months=+1)

            if loop_count == 0:
                if not point_pred:
                    for i in mem_list:
                        i += 1
                print("less than 1 month")
            elif loop_count >= 12:
                if point_pred:
                    mem_list[12] = 0
                else:
                    mem_list[12] += 1
                print("more than 12 month")
            else:
                if point_pred:
                    for temp in range(i,13):
                        mem_list[temp] = 0
                else:
                    for temp in range(i,13):
                        mem_list[temp] += 1
                print("before month: " + str(i+1))

            date_buoy = point_pos

        print(mem_list)      
        consecutive_false_dict[r['notification_no']] = mem_list
                    
            # loop_flag = False
            # for i in range(13):
            #     if i == 0:
            #         if point_pos >= date_ruler[i]:
            #             loop_flag = True
            #             if point_pred:
            #                 mem_list = 0
            #             else:
            #                 mem_list += 1
            #             #print("less than 1 month")
            #             #print(mem_list)
            #     elif i == 12:
            #         if point_pred:
            #             mem_list[i] = 0
            #         else:
            #             mem_list[i] += 1
            #             #print("more than 12 month")
            #             #print(mem_list)
            #     else:
            #         if (point_pos < date_ruler[i-1]) & (point_pos >= date_ruler[i]):
            #             loop_flag = True
            #             if point_pred:
            #                 for temp in range(i,13):
            #                     mem_list[temp] = 0
            #             else:
            #                 for temp in range(i,13):
            #                     mem_list[temp] += 1
            #             #print("before month: " + str(i+1))
            #             #print(mem_list)

            #     if loop_flag:
            #         break
            
            

        #print(dt.datetime.strftime(point_pos,"%Y-%m-%d") + " " + str(point_pred))
        # loop_flag = False
        # for i in range(13):
        #     if i == 0:
        #         if point_pos >= date_ruler[i]:
        #             loop_flag = True
        #             if point_pred:
        #                 mem_list = 0
        #             else:
        #                 mem_list += 1
        #             #print("less than 1 month")
        #             #print(mem_list)
        #     elif i == 12:
        #         if point_pred:
        #             mem_list[i] = 0
        #         else:
        #             mem_list[i] += 1
        #             #print("more than 12 month")
        #             #print(mem_list)
        #     else:
        #         if (point_pos < date_ruler[i-1]) & (point_pos >= date_ruler[i]):
        #             loop_flag = True
        #             if point_pred:
        #                 for temp in range(i,13):
        #                     mem_list[temp] = 0
        #             else:
        #                 for temp in range(i,13):
        #                     mem_list[temp] += 1
        #             #print("before month: " + str(i+1))
        #             #print(mem_list)

        #     if loop_flag:
        #         break
        # consecutive_false_dict[r['notification_no']] = mem_list

        # if pointer_pos >= date_ruler[0]:
        #     if false_count != mem_list[0]:
        #         mem_list = false_count
        #     # consecutive_false_dict[i][pointer_name] = false_count for i in month_list
        # elif (pointer_pos < date_ruler[0]) & (pointer_pos >= date_ruler[1]):
        #     if false_count != mem_list[1]:
        #         mem_list[1:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count for i in month_list[1:]
        # elif (pointer_pos < date_ruler[1]) & (pointer_pos >= date_ruler[2]):
        #     if false_count != mem_list[2]:
        #         mem_list[2:] = false_count
        #     # consecutive_false_dict[i][pointer_name] = false_count
        # elif (pointer_pos < date_ruler[2]) & (pointer_pos >= date_ruler[3]):
        #     if false_count != mem_list[3]:
        #         mem_list[3:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count
        # elif (pointer_pos < date_ruler[3]) & (pointer_pos >= date_ruler[4]):
        #     if false_count != mem_list[4]:
        #         mem_list[4:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count
        # elif (pointer_pos < date_ruler[4]) & (pointer_pos >= date_ruler[5]):
        #     if false_count != mem_list[5]:
        #         mem_list[5:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count
        # elif (pointer_pos < date_ruler[5]) & (pointer_pos >= date_ruler[6]):
        #     if false_count != mem_list[6]:
        #         mem_list[6:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count
        # elif (pointer_pos < date_ruler[6]) & (pointer_pos >= date_ruler[7]):
        #     if false_count != mem_list[7]:
        #         mem_list[7:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count
        # elif (pointer_pos < date_ruler[7]) & (pointer_pos >= date_ruler[8]):
        #     if false_count != mem_list[8]:
        #         mem_list[8:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count
        # elif (pointer_pos < date_ruler[8]) & (pointer_pos >= date_ruler[9]):
        #     if false_count != mem_list[9]:
        #         mem_list[9:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count
        # elif (pointer_pos < date_ruler[9]) & (pointer_pos >= date_ruler[10]):
        #     if false_count != mem_list[10]:
        #         mem_list[10:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count
        # elif (pointer_pos < date_ruler[10]) & (pointer_pos >= date_ruler[11]):
        #     if false_count != mem_list[11]:
        #         mem_list[11:] = false_count
        #     #consecutive_false_dict[i][pointer_name] = false_count
        # else:
        #     if false_count != mem_list[12]:
        #         mem_list[12] = false_count
            #consecutive_false_dict['whole'][pointer_name] = false_count
    gdf['consecutive_false'] = gdf['notification_no'].apply(lambda x: consecutive_false_dict.get(x)[12])
    for i in range(12):
        gdf['consec_false_{}month'.format(str(i + 1))] = gdf['notification_no'].apply(lambda x: consecutive_false_dict.get(x)[i])
    # gdf['consec_false_1month'] = mem_list[0]
    # gdf['consec_false_2month'] = mem_list[1]
    # gdf['consec_false_3month'] = mem_list[2]
    # gdf['consec_false_4month'] = mem_list[3]
    # gdf['consec_false_5month'] = mem_list[4]
    # gdf['consec_false_6month'] = mem_list[5]
    # gdf['consec_false_7month'] = mem_list[6]
    # gdf['consec_false_8month'] = mem_list[7]
    # gdf['consec_false_9month'] = mem_list[8]
    # gdf['consec_false_10month'] = mem_list[9]
    # gdf['consec_false_11month'] = mem_list[10]
    # gdf['consec_false_12month'] = mem_list[11]

    # gdf['consecutive_false'] = gdf['notification_no'].apply(lambda x: consecutive_false_dict.get(x))
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
        _  = find_consecutive_false_for_months(g)
        group_dfs.append(_)

    print('num of groups: {}'.format(len(group_dfs)))

    df2 = pd.concat(group_dfs)

    ind = 0
    num_inserted = 0
    for chunk in get_chunk(df2, CHUNK_SIZE):
        summary = {
            'ignore': 0,
            'insert': 0,
            'update': 0,
        }

        for i, r in chunk.iterrows():
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
                ignore = True
                # update
                if r['consecutive_false'] != _[0].consecutive_false :
                    _[0].consecutive_false = r['consecutive_false']
                    ignore = False
                    # session.commit()
                if r['consec_false_1month'] != _[0].consec_false_1month :
                    _[0].consec_false_1month = r['consec_false_1month']
                    ignore = False
                    #session.commit()
                if r['consec_false_2month'] != _[0].consec_false_2month:
                    _[0].consec_false_2month = r['consec_false_2month']
                    ignore = False
                    #session.commit()
                if r['consec_false_3month'] != _[0].consec_false_3month:
                    _[0].consec_false_3month = r['consec_false_3month']
                    ignore = False
                    #session.commit()
                if r['consec_false_4month'] != _[0].consec_false_4month:
                    _[0].consec_false_4month = r['consec_false_4month']
                    ignore = False
                    #session.commit()
                if r['consec_false_5month'] != _[0].consec_false_5month:
                    _[0].consec_false_5month = r['consec_false_5month']
                    ignore = False
                    #session.commit()
                if r['consec_false_6month'] != _[0].consec_false_6month:
                    _[0].consec_false_6month = r['consec_false_6month']
                    ignore = False
                    #session.commit()
                if r['consec_false_7month'] != _[0].consec_false_7month:
                    _[0].consec_false_7month = r['consec_false_7month']
                    ignore = False
                    #session.commit()
                if r['consec_false_8month'] != _[0].consec_false_8month:
                    _[0].consec_false_8month = r['consec_false_8month']
                    ignore = False
                    #session.commit()
                if r['consec_false_9month'] != _[0].consec_false_9month:
                    _[0].consec_false_9month = r['consec_false_9month']
                    ignore = False
                    #session.commit()
                if r['consec_false_10month'] != _[0].consec_false_10month:
                    _[0].consec_false_10month = r['consec_false_10month']
                    ignore = False
                    #session.commit()
                if r['consec_false_11month'] != _[0].consec_false_11month:
                    _[0].consec_false_11month = r['consec_false_11month']
                    ignore = False
                    #session.commit()
                if r['consec_false_12month'] != _[0].consec_false_12month:
                    _[0].consec_false_12month = r['consec_false_12month']
                    ignore = False
                    #session.commit()
                session.commit()
                if ignore:
                    summary['ignore'] += 1
                    continue
                else:
                    summary['update'] += 1
                    continue

        try:
            session.commit()
            num_inserted += len(chunk)
        except:
            session.rollback()
            print("We encouter unknown situation at chunk {} ({} - {})".format(ind, chunk_size*ind, (ind+1)*chunk_size-1))
            raise
        finally:
            session.close()

        print(ind, summary)
        ind += 1
    print(num_inserted)
