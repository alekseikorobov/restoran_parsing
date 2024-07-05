import pandas as pd
import logging
import common.common as common
import numpy as np
from params import Params

class SelectBestZoonSearch:
    def __init__(self, params: Params) -> None:
        self.params = params

    def get_best_from_result(self, df:pd.DataFrame) -> pd.DataFrame:

        df_not_empty = df[df['z_status'] != 'empty']
        if len(df_not_empty) == 0:
            df['z_status_m'] = 'is_empty'
            return df

        # df_fix = df[df['is_fix'] == True]
        # if len(df_fix) > 0:
        #     df_match = df_fix[(df_fix['v_zoon_id'] == df_fix['z_id'])]
        #     logging.debug(f'find match - {df_match.shape=}')
        #     df_match['z_status_m'] = 'match_by_fix'
        #     return df_match

        if len(df) == 1:
            df['z_status_m'] = 'match_one'
            return df

            # if line['z_dist'] == 0:
            #     new_row_res.update(line)
            #     return new_row_res
        
        cols = ['z_similarity_title_with_tran2',
                'z_similarity_title_with_tran',
                'z_similarity_title2',
                'z_similarity_title',
                'z_similarity_address']
        
        df_z = df[df['z_dist'].notna()]
        if len(df_z) == 0:
            df_res = df.sort_values(by=cols).head(1)
            df_res['z_status_m'] = 'not_dist'
            return df_res
        
        df_res = df_z.sort_values(by=cols).head(1)
        df_res['z_status_m'] = 'more_one'
        
        return df_res

    def start(self, df_zoon_search:pd.DataFrame) -> pd.DataFrame:
        logging.debug(f'start')

        logging.info(f'{df_zoon_search.shape=}')

        fact_count = df_zoon_search['source_id'].nunique()
        #assert fact_count == control_count, f'not correct count before load  {fact_count} {control_count}'

        df_result = pd.DataFrame(columns=['v_zoon_id','source_id'])

        df_fix = df_zoon_search[(df_zoon_search['v_zoon_id'].notna()) & (df_zoon_search['is_fix'] == True)]
        #uniq_fix_count =  df_fix['source_id'].nunique()
        if len(df_fix) > 0:
            df_result = df_fix[(df_fix['v_zoon_id'] == df_fix['z_id'])]
            df_result['z_status_m'] = 'match_by_fix'
            logging.debug(f'find match - {df_result.shape=} and {df_fix.shape=}')

        df_fix_ulr = df_zoon_search[df_zoon_search['z_status'] == 'new_by_fix']
        if len(df_fix_ulr) > 0:
            df_fix_ulr['z_status_m'] = 'match_by_fix_url'
            df_result = pd.concat([df_result, df_fix_ulr]).drop_duplicates()
            logging.debug(f'find match by url - {df_result.shape=}')

        uniq_fix_count = pd.concat([df_fix_ulr[['source_id']],df_fix[['source_id']]])['source_id'].nunique()
        fix_source_id = set(df_fix['v_zoon_id'].values)
        for item in set(df_fix_ulr['v_zoon_id'].values):
            fix_source_id.add(item)
        if len(df_result)>0:
            fix_result_source_id = set(df_result['v_zoon_id'].values)

            fix_diff = fix_source_id - fix_result_source_id 
            
            uniq_fix_result_count = df_result['source_id'].nunique()
            #assert uniq_fix_count == uniq_fix_result_count, f'not correct count {uniq_fix_count=} {uniq_fix_result_count=}, {fix_diff=}'

        df_process = df_zoon_search[~df_zoon_search['source_id'].isin(df_result['source_id'])][['source_id','ya_id']].drop_duplicates()
        logging.debug(f'{df_zoon_search.columns=}')
        if 'z_title' in df_zoon_search.columns:
            df_zoon_search['z_title_n'] = df_zoon_search.apply(lambda row: common.normalize_company_name(row['z_title']),axis=1)
            #нам нужно найти либо минимальное расстояние двух точек, либо минимальную разность двух адресов.
            #а так как str_similarity возвращает схожесть от 0 до 1, где 1 это полностью одинаковое значение,
            #то необходимо сделать вычетание из 1
            df_zoon_search['z_similarity_title'] = df_zoon_search.apply(lambda row: common.str_similarity(row['ya_company_name_norm'],row['z_title_n']),axis=1)
            df_zoon_search['z_similarity_title2'] = df_zoon_search.apply(lambda row: common.str_similarity2(row['ya_company_name_norm'],row['z_title_n']),axis=1)
            df_zoon_search['z_similarity_title_with_tran'] = df_zoon_search.apply(lambda row: common.str_similarity(row['transaction_info_norm'],row['z_title_n']),axis=1)
            df_zoon_search['z_similarity_title_with_tran2'] = df_zoon_search.apply(lambda row: common.str_similarity2(row['transaction_info_norm'],row['z_title_n']),axis=1)
        if 'z_address_n' in df_zoon_search.columns:
            df_zoon_search['z_similarity_address'] = df_zoon_search.apply(lambda row: common.str_similarity2(row['ya_address_n'],row['z_address_n']),axis=1)
        

        logging.debug(f"{df_process['source_id'].nunique()=}")
        #return None

        for i, row in df_process.iterrows():
            
            if str(row['ya_id']) == str(np.nan):
                df_line = df_zoon_search[(df_zoon_search['source_id'] == row['source_id'])]
                #logging.debug(f"{row['source_id']=}, {df_line.shape=}")
                df_result = pd.concat([df_result,df_line])
                continue

            df_to = df_zoon_search[(df_zoon_search['source_id'] == row['source_id']) & (df_zoon_search['ya_id'] == row['ya_id'])]
            if len(df_to) == 0:
                logging.warning(f"NOT DATA - {row['source_id']=}, {row['ya_id']=}")
                break

            df_line = self.get_best_from_result(df_to)

            if len(df_line) == 0:
                logging.warning(f"NOT RESULT BY MATCH {row['source_id']=}")

            #logging.debug(f"{row['source_id']=}, {df_line.shape=}")

            df_result = pd.concat([df_result,df_line])
        
        fact_count = df_result['source_id'].nunique()
        #assert fact_count == control_count, f'not correct count after load {fact_count} {control_count}'
        
        logging.debug(f'{df_result.columns=}')

        return df_result