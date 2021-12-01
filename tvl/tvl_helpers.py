import datetime
import numpy as np
import os
import pandas as pd
import re
from practice_risk_supplier_terms import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)


START_REGEX = '(?<![^ .,?!;])'


def gather_file_names_for_all_industries(
        tvl_raw_dir,  # Create shortcut for this folder in your personal drive: https://drive.google.com/drive/folders/1S9MvX0UI7hfrSxYi3DwnxD3QL7mK_s29?usp=sharing
        gic_dir,
        file_prefix='Truvalue_Spotlights_'):

    industry_files = {}  # "Industry": ["file1.csv", "file2.csv", ...]

    # Get all industries for which we have raw outputs
    for raw_output_file_name in os.listdir(tvl_raw_dir + gic_dir):
        if not raw_output_file_name.startswith(file_prefix):
            continue
        industry_file_name = raw_output_file_name[len(file_prefix):]
        next_underscore_idx = industry_file_name.find('_')
        industry_name = industry_file_name[:next_underscore_idx]
        industry_files[industry_name] = []

    # Get all raw file names by industry
    for industry_name in industry_files:
        industry_file_names = [file_name for file_name in os.listdir(tvl_raw_dir + gic_dir) if
                               industry_name == file_name.split("_")[2]]
        industry_files[industry_name] += industry_file_names

    return industry_files


# covid_lp_relevant_keywords = ['block', 'review', 'police', 'issue', r'licen[cs]e', 'wage', 'revoke', 'temporary'] as of 10/11
# pattern_covid_lp_relevant_keywords = '|'.join(covid_lp_relevant_keywords)

# Supply chain work involves a labor practice heuristic I created...
# No need to query for labor-practice keywords for other GIC work
def get_labor_indicator_v2(row, labor_keywords):
    """Applying this heuristic to generate indicator for mentions of
    at least 2 of the following labor-related keywords:
    ['labo[u]r', 'wage', 'worker'].
    (v1 included all words as well as "employee".) """
    cols = [f'{keyword}_ind' for keyword in labor_keywords]
    count_labor_term_inds_1 = 0
    for col in cols:
        if row[col] == 1:
            count_labor_term_inds_1 += 1
    if count_labor_term_inds_1 >= 2:
        return 1
    else:
        return 0


def label_all_industry_events_with_term_indicators(
        industry_files, tvl_raw_dir, gic_dir, practice_terms_regex_dict,
        risk_terms_regex_dict, supplier_relship_regex_dict):

    industry_all_events_dict = {}

    # Supply chain work involves a labor practice heuristic I created...
    # No need to query for labor-practice keywords for other GIC work
    labor_keywords = [r'labo[u]r', 'wage', 'worker']
    covid_keywords = ['covid', 'coronavirus', 'pandemic']
    # TODO: TURNOVER_CHECK
    TURNOVER_keywords = ['high turnover', 'worker turnover', 'employee turnover', 'turnover rate', 'voluntary turnover',
                         'quit[s]? rate', 'rate of quit']
    pattern_covid = '|'.join(covid_keywords)

    # Get all events in one df, by industry
    for industry_name, file_names_lst in sorted(industry_files.items()):
        print(industry_name)
        for file_name in file_names_lst:
            print('\t' + file_name)
            sub_df = pd.read_csv(tvl_raw_dir + gic_dir + file_name)
            sub_df.dropna(axis=0, how='all', inplace=True)
            if sub_df.empty:
                continue
            all_are_scm = list(sub_df['Category'].unique()) == [gic_dir[:-1]]
            if not all_are_scm:
                print()
                print(f'NOT ALL ARTICLES ARE {gic_dir[:-1]}!!!')
                print(file_name)
                print(f'NOT ALL ARTICLES ARE {gic_dir[:-1]}!!!')
                print()
            if industry_name not in industry_all_events_dict:
                industry_all_events_dict[industry_name] = sub_df
            else:
                industry_all_events_dict[industry_name] = industry_all_events_dict[industry_name].append(sub_df,
                                                                                                         ignore_index=True)

        # Create some columns with cleaned text/dates
        industry_df = industry_all_events_dict[industry_name].copy()
        print(f'Before dropping dupes: {industry_df.shape}')

        # Drop duplicates for combos of company + TVL ID + article (repeating article pertaining to the same company)
        # Reasoning: TVL ID represents an identifier of a Spotlight Event for ONE company.
        # A Spotlight Event may be made up of several articles.
        # So we do not yet want to drop all the articles that comprise a single TVL ID by
        # doing a hard drop_duplicates on JUST TVL ID. So, we are dropping on a combination of
        # columns, to ensure that we only drop repeating articles for the same company.
        # Repeating articles may occur due to potential overlap of articles from the CSVs.
        drop_dupes_cols = ['Company', 'TVL ID', 'Primary Article Spotlight Headline',
                           'Primary Article Bullet Points', 'Spotlight Start Date']
        industry_df = industry_df.drop_duplicates(drop_dupes_cols, keep='first')
        print(f'After dropping dupes: {industry_df.shape}')
        industry_df['INDUSTRY'] = industry_name
        industry_df = industry_df[['INDUSTRY', 'Company', 'TVL ID', 'Category', 'Primary Article Spotlight Headline',
                                   'Primary Article Bullet Points', 'Primary Article Source',
                                   'Primary Article URL Link', 'Spotlight Start Date',
                                   'Spotlight End Date', 'Spotlight Volume']]

        industry_df['headline_lower'] = industry_df['Primary Article Spotlight Headline'].str.lower()
        industry_df['bullet_pts_lower'] = industry_df['Primary Article Bullet Points'].str.lower()
        industry_df['date'] = industry_df['Spotlight Start Date'].apply(
            lambda s_date: datetime.datetime.strptime(s_date, '%m/%d/%Y'))
        industry_df['year'] = industry_df['date'].dt.year

        # Apply general labor practice-relevance heuristic
        for keyword in labor_keywords:
            keyword_regex = re.compile(f'{START_REGEX}{keyword}')
            industry_df[f'{keyword}_ind'] = np.where(
                industry_df['headline_lower'].str.contains(keyword_regex) | industry_df[
                    'bullet_pts_lower'].str.contains(keyword_regex),
                1, 0)
        industry_df['labor_keyword_ind'] = industry_df.apply(lambda row: get_labor_indicator_v2(row, labor_keywords),
                                                             axis=1)
        industry_df['marked_labor_relevant_ind'] = industry_df['labor_keyword_ind']

        # TODO: TURNOVER_CHECK
        for keyword in TURNOVER_keywords:
            keyword_regex = re.compile(f'{START_REGEX}{keyword}')
            industry_df[f'{keyword}_ind'] = np.where(
                industry_df['headline_lower'].str.contains(keyword_regex) | industry_df[
                    'bullet_pts_lower'].str.contains(keyword_regex),
                1, 0)

        # Apply COVID-specific labor practice-relevance heuristic ONLY to articles marked as lp-relevant above
        mask_marked_as_lp_relevant = (industry_df['labor_keyword_ind'] == 1)
        mask_mentions_covid = (industry_df['headline_lower'].str.contains(pattern_covid) | industry_df[
            'bullet_pts_lower'].str.contains(pattern_covid))
        industry_df['covid_ind'] = np.where(mask_mentions_covid, 1, 0)
        industry_df['covid_and_labor_keyword_ind'] = np.where(mask_marked_as_lp_relevant & mask_mentions_covid, 1, 0)

        # covid_lp_relevant_subset = industry_df[industry_df['covid_and_labor_keyword_ind'] == 1]
        # if covid_lp_relevant_subset.empty:
        #     continue
        # covid_lp_relevant_subset['marked_labor_relevant_ind'] = np.where((covid_lp_relevant_subset['headline_lower'].str.contains(pattern_covid_lp_relevant_keywords) | covid_lp_relevant_subset['bullet_pts_lower'].str.contains(pattern_covid_lp_relevant_keywords)), 1, 0)

        # PRACTICE TERM INDICATORS CREATED HERE
        create_term_type_indicators(industry_df, 'practice', practice_terms_regex_dict)

        # RISK TERM INDICATORS CREATED HERE
        create_term_type_indicators(industry_df, 'risk', risk_terms_regex_dict)

        # SUPPLIER RELATIONSHIP INDICATORS CREATED HERE
        create_term_type_indicators(industry_df, 'supplier-relationship', supplier_relship_regex_dict)

        industry_all_events_dict[industry_name] = industry_df
    return industry_all_events_dict


def create_term_type_indicators(industry_df, term_type, terms_regex_dict):
    for cat, cat_terms in terms_regex_dict.items():
        for clean_term, term_dict in cat_terms.items():
            indicator_col_name = "{}_{}_{}".format(clean_term, term_type.upper(), cat)
            keyword_regexes = term_dict['regex_lst']
            industry_df[indicator_col_name] = 0

            pattern_terms_to_remove = re.compile('|'.join(term_dict.get('terms_to_remove', [])))
            pattern_context_words = re.compile('|'.join(term_dict.get('context_words', [])))

            # for keyword_regex_str in keyword_regexes:
            for keyword_regex in keyword_regexes:
                # keyword_regex = re.compile(keyword_regex_str)
                industry_df[indicator_col_name] = np.where((industry_df['headline_lower'].str.contains(
                    keyword_regex) | industry_df['bullet_pts_lower'].str.contains(keyword_regex)) & (
                                                                   industry_df['headline_lower'].str.contains(
                                                                       pattern_context_words) | industry_df[
                                                                       'bullet_pts_lower'].str.contains(
                                                               pattern_context_words)), 1,
                                                           industry_df[indicator_col_name])
            if term_dict.get('extra_cleaning'):
                industry_df[indicator_col_name] = np.where(
                    industry_df['headline_lower'].str.contains(pattern_terms_to_remove) | industry_df[
                        'bullet_pts_lower'].str.contains(pattern_terms_to_remove), 0,
                    industry_df[indicator_col_name])


def list_terms_found(row, term_cols):
    terms_found = ""

    for t_col in term_cols:
        if row[t_col] == 1:
            t_col_split = t_col.split('_')
            terms_found += f"{t_col_split[0]} ({t_col_split[2]}), "  # term (category)

    if terms_found == "":
        return "None"
    return terms_found
