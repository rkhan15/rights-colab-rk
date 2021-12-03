import argparse
import datetime
import pandas as pd


def parse_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--old_df_path', type=str, required=True)
    parser.add_argument('--new_df_path', type=str, required=True)
    parser.add_argument('--abbrev', type=str, required=False, default="TVLSuppChainMgmt")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_cmd_line_args()
    old_df = pd.read_excel(args.old_df_path)
    new_df = pd.read_csv(args.new_df_path)

    old_DO_NOT_DROP = ['INDUSTRY',
                       'Company',
                       'TVL ID',
                       'Category',
                       'Primary Article Spotlight Headline',
                       'Primary Article Bullet Points',
                       'Primary Article Source',
                       'Primary Article URL Link',
                       'Spotlight Volume', 'date',
                       'year', 'RELEVANT?']
    old_df_drop_cols = [col for col in list(old_df.columns) if col not in old_DO_NOT_DROP]
    old_df.drop(old_df_drop_cols, axis=1, inplace=True)
    merge_new_with_old = pd.merge(new_df, old_df, how='left',
                                  on=['INDUSTRY', 'Company', 'TVL ID', 'Category',
                                      'Primary Article Spotlight Headline',
                                      'Primary Article Bullet Points', 'Primary Article Source',
                                      'Primary Article URL Link', 'Spotlight Volume'])

    cols_to_drop = [col for col in list(merge_new_with_old.columns) if col.endswith('_y')]
    merge_new_with_old.drop(cols_to_drop, axis=1, inplace=True)
    rename_y_cols = {col: col[:-2] for col in list(merge_new_with_old.columns) if col.endswith('_x')}
    merge_new_with_old = merge_new_with_old.rename(columns=rename_y_cols)

    all_cols = list(merge_new_with_old.columns)
    cols_sub_v1 = ['RELEVANT?']
    cols_minus_sub_v1 = [i for i in all_cols if i not in cols_sub_v1]

    col_order_1 = ['INDUSTRY',
                   'Company',
                   'TVL ID',
                   'Category',
                   'ANY_PRACTICE_TERM',
                   'ANY_RISK_TERM',
                   'ANY_PRACTICE_AND_RISK',
                   'PRACTICE_TERMS_FOUND',
                   'RISK_TERMS_FOUND',
                   'ANY_RISK_AND_marked_labor_relevant',
                   'ANY_SUPPLIER_RELATIONSHIP_TERM',
                   'SUPPLIER_RELSHIP_TERMS_FOUND', ]
    col_order_1.extend(cols_sub_v1)
    col_order_1.extend(cols_minus_sub_v1[cols_minus_sub_v1.index('SUPPLIER_RELSHIP_TERMS_FOUND') + 1:])
    merge_new_with_old = merge_new_with_old[col_order_1]

    merge_new_with_old.to_csv(
        f'{datetime.datetime.today().month}_{datetime.datetime.today().day}-JOINED-WITH-{args.old_df_path.split("-")[1]}-{args.abbrev}-Industry_Article_Lvl.csv',
        index=False)
