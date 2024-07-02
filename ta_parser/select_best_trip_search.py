import pandas as pd
import numpy as np
import ta_parser.load_data as load_data
import common.common as common
import importlib
importlib.reload(load_data)
from tqdm import tqdm
import logging



def get_location_id_from_url(row)->str:
    if row['ta_status'] == 'new_by_fix':
        # если идем по фиксированной ссылке, то нужно получить location_id из этой страницы
        row['ta_location_id'] = load_data.get_location_id_from_url(row['ta_link'])
    return row['ta_location_id']

def df_first_and_count(df_new, group_by = ['col1','col2'], order_by = ['ser','ser1']):
    df_new_res = df_new.sort_values(by=[*group_by,*order_by]).groupby(group_by).first().reset_index()

    #df_new.groupby(group_by).agg({'col1':'count'})#.reset_index()

    df1 = df_new[group_by]\
            .groupby(group_by)\
            .agg({
                    group_by[0]:['count']
                    })\
            .reset_index()
    df1.columns = ['_'.join(filter(lambda l: l != '',list(x))) for x in df1.columns]
    df1 = df1.rename_axis(None,axis=1)

    return df_new_res.merge(df1,how='inner',on=group_by)

def get_except(df_all:pd.DataFrame,df_except:pd.DataFrame,cols:list):
    cols_select = df_all.columns 
    df_left = df_all.merge(df_except,how='left',on=cols,indicator=True,suffixes=(None,'____y'))
    df_left = df_left[df_left['_merge']=='left_only']
    return df_left[cols_select].drop_duplicates()


def start(df_trip_search:pd.DataFrame) -> pd.DataFrame:
    logging.debug('start')
    fact_count_unique_source_id = df_trip_search["source_id"].nunique()
    logging.info(f'{df_trip_search.shape=}, {fact_count_unique_source_id=}')

    df_result = pd.DataFrame()

    if 'v_ta_id' in df_trip_search.columns:
        df_fix = df_trip_search[(df_trip_search['v_ta_id'].notna()) & (df_trip_search['is_fix'] == True)]
        #uniq_fix_count =  df_fix['source_id'].nunique()
        if len(df_fix) > 0:
            df_result = df_fix[(df_fix['v_ta_id'].astype('float64') == df_fix['ta_location_id'].astype('float64'))]
            df_result['ta_status_m'] = 'match_by_fix'
            logging.debug(f'find match - {df_result.shape=}, {df_result["source_id"].nunique()=}, {df_result["ta_link"].nunique()=}')

    df_fix_ulr = df_trip_search[df_trip_search['ta_status'] == 'new_by_fix']
    if len(df_fix_ulr) > 0:
        df_fix_ulr['ta_status_m'] = 'match_by_fix_url'
        df_result = pd.concat([df_result, df_fix_ulr])
        logging.debug(f'find match by url - {df_result.shape=}, {df_result["source_id"].nunique()=},{df_result["ta_link"].nunique()=}')


    df_result = pd.concat([df_result,
                           df_trip_search[df_trip_search['ya_id'].isna()]
                           ])
    logging.debug(f'added ya_id is nan {df_result.shape=}, {df_result["source_id"].nunique()=},{df_result["ta_link"].nunique()=}')

    df_trip_search = df_trip_search[~df_trip_search['source_id'].isin(df_result['source_id'])]
    
    logging.debug(f'{df_trip_search.shape=}, {df_trip_search["source_id"].nunique()=},{df_trip_search["ta_link"].nunique()=}')
    
    logging.debug('load ta_name_n...')
    df_trip_search['ta_name_n'] = df_trip_search.apply(lambda row: common.normalize_company_name(row['ta_name'], is_translit=True),axis=1)
    logging.debug('load ta_similarity_address...')
    df_trip_search['ta_similarity_address'] = df_trip_search.apply(lambda row: common.str_similarity(row['ya_address_n'],row['ta_address_n']),axis=1)
    logging.debug('load ta_similarity_address2...')
    df_trip_search['ta_similarity_address2'] = df_trip_search.apply(lambda row: common.str_similarity2(row['ya_address_n'],row['ta_address_n']),axis=1)
    logging.debug('load ta_similarity_title...')
    df_trip_search['ta_similarity_title'] = df_trip_search.apply(lambda row: common.str_similarity(row['ya_company_name_norm'],row['ta_name_n']),axis=1)
    logging.debug('load ta_similarity_title2...')
    df_trip_search['ta_similarity_title2'] = df_trip_search.apply(lambda row: common.str_similarity2(row['ya_company_name_norm'],row['ta_name_n']),axis=1)
    logging.debug('load ta_similarity_title_with_tran...')
    df_trip_search['ta_similarity_title_with_tran'] = df_trip_search.apply(lambda row: common.str_similarity(row['transaction_info_norm'],row['ta_name_n']),axis=1)
    logging.debug('load ta_similarity_title_with_tran2...')
    df_trip_search['ta_similarity_title_with_tran2'] = df_trip_search.apply(lambda row: common.str_similarity2(row['transaction_info_norm'],row['ta_name_n']),axis=1)

    logging.debug('filter from df_trip_search')


    col_sum = ['ta_similarity_address','ta_similarity_address2', 'ta_similarity_title',
        'ta_similarity_title2', 'ta_similarity_title_with_tran',
        'ta_similarity_title_with_tran2']
    df_trip_search['ta_similarity_mean'] = 0
    for col in col_sum:
        df_trip_search['ta_similarity_mean'] += df_trip_search[col]

    df_trip_search['ta_similarity_mean'] /= len(col_sum)


    # filter_by_sim =((df_trip_search['ta_similarity_address'] < 0.8) & ((df_trip_search['ta_similarity_title'] < 0.8) | (df_trip_search['ta_similarity_title2'] < 0.8)))\
    #     & (
    #         (df_trip_search['ta_similarity_address'] <= 0.5)
    #         | (df_trip_search['ta_similarity_title'] <= 0.5)
    #         | (df_trip_search['ta_similarity_title2'] <= 0.5)
    #         | (df_trip_search['ta_similarity_title_with_tran'] <= 0.5)
    #         | (df_trip_search['ta_similarity_title_with_tran2'] <= 0.5)
    #     )
    filter_by_sim = (df_trip_search['ta_similarity_mean'] <= 0.49) & (df_trip_search['ta_similarity_address'] <= 0.6)
    is_ya_match = df_trip_search['ta_status'] == 'new'
    is_ta_name_not_na = df_trip_search['ta_name'].notna()

    df_trip_search_to = df_trip_search[filter_by_sim & is_ya_match & is_ta_name_not_na]

    logging.debug(f'{df_trip_search_to.shape=}, {df_trip_search_to["source_id"].nunique()=},{df_trip_search_to["ta_link"].nunique()=}')

    df_trip_search_not = get_except(df_all = df_trip_search,df_except=df_trip_search_to,cols = ['source_id','ya_id'])
    #df_trip_search_not = df_trip_search[~df_trip_search.index.isin(df_trip_search_to.index)]

    logging.debug(f'{df_trip_search_not.shape=}, {df_trip_search_not["source_id"].nunique()=},{df_trip_search_not["ta_link"].nunique()=}')
    cols = [
         'ta_similarity_title_with_tran2'
        ,'ta_similarity_title_with_tran'
        ,'ta_similarity_title2'
        ,'ta_similarity_title'
        ,'ta_similarity_address']
    
    df_trip_search_not['ta_status_m'] = 'all_not_match'

    df_trip_search_not = df_first_and_count(df_trip_search_not,group_by=['source_id','ya_id'],order_by=cols)

    logging.debug(f'first {df_trip_search_not.shape=}, {df_trip_search_not["source_id"].nunique()=},{df_trip_search_not["ta_link"].nunique()=}')

    df_result_filter = df_first_and_count(df_trip_search_to,group_by=['source_id','ya_id'],order_by=cols)
    df_result_filter['ta_status_m']='new'
    is_one = df_result_filter['source_id_count'] == 1
    df_result_filter.loc[is_one,'ta_status_m'] = 'match_one_condition'

    is_more_one = df_result_filter[df_result_filter['source_id_count'] > 1].index
    df_result_filter.loc[is_more_one,'ta_status_m'] = 'more_one'

    logging.debug(f'first {df_result_filter.shape=}, {df_result_filter["source_id"].nunique()=}')

    df_result = pd.concat([
        df_result,
        df_result_filter,
        df_trip_search_not
    ])
    actual_count_unique_source_id = df_result['source_id'].nunique()
    logging.debug(f"{df_result.shape=}, {actual_count_unique_source_id=}")

    assert fact_count_unique_source_id == actual_count_unique_source_id,f'{actual_count_unique_source_id=} and {fact_count_unique_source_id=} not equal!'
    
    df_result['ta_location_id'] = df_result.apply(get_location_id_from_url, axis=1)

    df_result.drop(columns=['source_id_count'],inplace=True)

    logging.debug(f"{df_result['source_id'].nunique()=},{df_result['ta_link'].nunique()=}")
    
    logging.debug(f'{df_result.columns=}')

    logging.debug(df_result['ta_status_m'].value_counts())

    return df_result