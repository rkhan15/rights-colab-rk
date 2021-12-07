import argparse
import datetime
import numpy as np
import pandas as pd
import sys

from practice_risk_supplier_terms import *
from tvl_helpers import *


def parse_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tvl_raw_dir', type=str, required=False, default='tvl_downloads_raw/')
    parser.add_argument('--gic_dir', type=str, required=False, default='Supply Chain Management/')
    parser.add_argument('--abbrev', type=str, required=False, default="TVLSuppChainMgmt")
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_cmd_line_args()

    # Get all TVL files for each industry
    industry_files = gather_file_names_for_all_industries(tvl_raw_dir=args.tvl_raw_dir, gic_dir=args.gic_dir)

    # Create indicators for all events and all terms
    industry_all_events_dict = label_all_industry_events_with_term_indicators(
        industry_files, args.tvl_raw_dir, args.gic_dir,
        practice_terms_regex_dict,  # Created in practice_risk_supplier_terms.py
        risk_terms_regex_dict,  # Created in practice_risk_supplier_terms.py
        supplier_relship_regex_dict)  # Created in practice_risk_supplier_terms.py

    # Put all the Sup Chain events in one master df
    all_industries_events_master_df = pd.concat(
        [industry_df for industry_name, industry_df in industry_all_events_dict.items()], ignore_index=True)
    print(all_industries_events_master_df.shape)
    all_industries_events_master_df['INDUSTRY'] = all_industries_events_master_df['INDUSTRY'].str.strip()

    # Drop duplicate articles for within each industry, to count each article at the INDUSTRY level only ONCE
    # (Drop duplicates on ("INDUSTRY" and) "Primary Article Spotlight Headline" and "Primary Article Bullet Points" and "Spotlight Start Date")
    # (This is because we only care about each article at the INDUSTRY level, not the TVL ID level (company + event))
    ### 12/7/21 UPDATE: Keeping industry-level dupes
    # all_industries_events_master_df = all_industries_events_master_df.drop_duplicates(
    #     ['INDUSTRY', 'Primary Article Spotlight Headline', 'Primary Article Bullet Points', 'Spotlight Start Date'],
    #     keep='first')

    # TODO: Remove when done
    all_industries_events_master_df.to_csv('all_industries_events_master_df.csv', index=False)
    sys.exit(0)
    # TODO end

    # Creating an article ID to keep track of same articles across companies/industries
    cols_to_track_same_article = ['Primary Article Spotlight Headline',
                                  'Primary Article Bullet Points',
                                  'Spotlight Start Date',
                                  'Spotlight End Date',
                                  'Primary Article Source',
                                  'Primary Article URL Link'
                                  ]
    all_industries_events_master_df['article_idx_cols'] = tuple(zip(all_industries_events_master_df[col]
                                                                    for col in cols_to_track_same_article))
    article_to_idx_mapping = {article_info: idx
                              for idx, article_info in
                              enumerate(list(all_industries_events_master_df['article_idx_cols'].unique()))}
    all_industries_events_master_df['article_idx'] = all_industries_events_master_df['article_idx_cols'].map(
        article_to_idx_mapping)
    all_industries_events_master_df.drop('article_idx_cols', axis=1, inplace=True)

    # Adding indicators of having any practice term or risk term,
    # to quickly identify events with co-occurrences of practice and risk terms
    # indicator format: {term}_{PRACTICE/RISK}_{category}
    all_cols = list(all_industries_events_master_df.columns)
    practice_term_cols = []
    risk_term_cols = []
    supplier_relship_cols = []
    for col in all_cols:
        try:
            col_type = col.split('_')[1]
            if col_type == 'PRACTICE':
                practice_term_cols.append(col)
            elif col_type == 'RISK':
                risk_term_cols.append(col)
            elif col_type == 'supplier-relationship'.upper():
                supplier_relship_cols.append(col)
        except:
            continue

    all_industries_events_master_df['ANY_PRACTICE_TERM'] = 0
    for practice_term_col in practice_term_cols:
        all_industries_events_master_df['ANY_PRACTICE_TERM'] = np.where(
            all_industries_events_master_df[practice_term_col] == 1,
            1, all_industries_events_master_df['ANY_PRACTICE_TERM'])

    all_industries_events_master_df['ANY_RISK_TERM'] = 0
    for risk_term_col in risk_term_cols:
        all_industries_events_master_df['ANY_RISK_TERM'] = np.where(all_industries_events_master_df[risk_term_col] == 1,
                                                                    1, all_industries_events_master_df['ANY_RISK_TERM'])

    all_industries_events_master_df['ANY_PRACTICE_AND_RISK'] = np.where(
        (all_industries_events_master_df['ANY_PRACTICE_TERM'] == 1) & (
                all_industries_events_master_df['ANY_RISK_TERM'] == 1), 1, 0)
    all_industries_events_master_df['ANY_RISK_AND_marked_labor_relevant'] = np.where(
        (all_industries_events_master_df['marked_labor_relevant_ind'] == 1) & (
                all_industries_events_master_df['ANY_RISK_TERM'] == 1), 1, 0)

    all_industries_events_master_df['ANY_SUPPLIER_RELATIONSHIP_TERM'] = 0
    for supplier_relship_col in supplier_relship_cols:
        all_industries_events_master_df['ANY_SUPPLIER_RELATIONSHIP_TERM'] = np.where(
            all_industries_events_master_df[supplier_relship_col] == 1,
            1, all_industries_events_master_df['ANY_SUPPLIER_RELATIONSHIP_TERM'])

    # Creating columns to quickly see which practice/risk terms are in an article
    all_industries_events_master_df['PRACTICE_TERMS_FOUND'] = "None"
    all_industries_events_master_df['RISK_TERMS_FOUND'] = "None"
    all_industries_events_master_df['SUPPLIER_RELSHIP_TERMS_FOUND'] = "None"

    all_industries_events_master_df['PRACTICE_TERMS_FOUND'] = all_industries_events_master_df.apply(
        lambda row: list_terms_found(row, practice_term_cols), axis=1)

    all_industries_events_master_df['RISK_TERMS_FOUND'] = all_industries_events_master_df.apply(
        lambda row: list_terms_found(row, risk_term_cols), axis=1)

    all_industries_events_master_df['SUPPLIER_RELSHIP_TERMS_FOUND'] = all_industries_events_master_df.apply(
        lambda row: list_terms_found(row, supplier_relship_cols), axis=1)

    # Column cleanup:
    for i, col in enumerate(['article_idx',
                             'ANY_PRACTICE_TERM',
                             'ANY_RISK_TERM',
                             'ANY_PRACTICE_AND_RISK',
                             'PRACTICE_TERMS_FOUND',
                             'RISK_TERMS_FOUND',
                             'ANY_RISK_AND_marked_labor_relevant',
                             'ANY_SUPPLIER_RELATIONSHIP_TERM',
                             'SUPPLIER_RELSHIP_TERMS_FOUND']):
        mid = all_industries_events_master_df[col]
        all_industries_events_master_df.drop(labels=[col], axis=1, inplace=True)
        all_industries_events_master_df.insert(i + 4, col, mid)

    cols_to_drop = ['headline_lower', 'bullet_pts_lower']
    all_industries_events_master_df = all_industries_events_master_df.drop(cols_to_drop, axis=1)

    print("Total articles:", all_industries_events_master_df.shape[0])
    print("Number of ARTICLES with a practice-risk co-occurrence:",
          all_industries_events_master_df['ANY_PRACTICE_AND_RISK'].sum())
    print("Total events:", all_industries_events_master_df['TVL ID'].nunique())
    print("Number of EVENTS with a practice-risk co-occurrence",
          all_industries_events_master_df.groupby(['INDUSTRY', 'TVL ID'])['ANY_PRACTICE_AND_RISK'].sum().reset_index()[
              'ANY_PRACTICE_AND_RISK'].value_counts().reset_index().iloc[1:]['ANY_PRACTICE_AND_RISK'].sum())

    # SAVE ALL EVENTS WITH ALL INDICATORS
    all_industries_events_master_df.to_csv(
        f'{datetime.datetime.today().month}_{datetime.datetime.today().day}-{args.abbrev}-Industry_Article_Lvl.csv',
        index=False)
