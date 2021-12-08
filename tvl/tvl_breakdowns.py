import argparse
import datetime
import numpy as np
import pandas as pd

import plotly.figure_factory as ff
MIN_YEAR = 2016
MAX_YEAR = 2021


def parse_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--labeled_industry_articles_path', type=str, required=True)
    parser.add_argument('--industry_to_sector_map_path', type=str, required=False,
                        default='rights-colab-rk/tvl/TVL_Industry_Abbrev_to_Sector_Mapping.csv')
    parser.add_argument('--generate_merge', type=str, required=False, default=True)
    parser.add_argument('--generate_heatmap', type=str, required=False, default=False)
    parser.add_argument('--abbrev', type=str, required=False, default="TVLSuppChainMgmt")
    parser.add_argument('--article_level', type=int, required=True, default=1)
    return parser.parse_args()


def create_category_col(row, col_type):
    return row[f'{col_type.capitalize()} term'].split('_')[2]


def df_to_plotly(df):
    return {'z': df.values.tolist(),
            'x': df.columns.tolist(),
            'y': df.index.tolist()}


def get_industry_level_practice_breakdown(labeled_industry_articles, industry_to_sector_map, sector=0, industry=0,
                                          article_level=True, generate_merge=True, generate_heatmap=False):
    # Get totals for each practice term, regardless of industry
    if sector != 0:
        industries = industry_to_sector_map[industry_to_sector_map['SECTOR_FULL_NAME'] == sector][
            'TVL Industry Abbrev'].values.tolist()
        print(industries)
        df_sub = labeled_industry_articles[labeled_industry_articles['INDUSTRY'].isin(industries)]
    elif industry != 0:
        df_sub = labeled_industry_articles[labeled_industry_articles['INDUSTRY'].isin([industry])]
    else:
        df_sub = labeled_industry_articles

    # relevant_articles_or_events = set()
    dict_relevant_articles_or_events = {year: set() for year in range(MIN_YEAR, MAX_YEAR+1)}
    # practice_term_articles_or_events = {}
    dict_practice_term_articles_or_events = {year: dict() for year in range(MIN_YEAR, MAX_YEAR+1)}
    # practice_category_articles_or_events = {}
    ## dict_practice_category_articles_or_events = {year: dict() for year in range(MIN_YEAR, MAX_YEAR + 1)}

    for year in range(MIN_YEAR, MAX_YEAR+1):
        year_subset = df_sub[(df_sub['ANY_PRACTICE_AND_RISK'] == 1) & (df_sub['RELEVANT?'] == 'Yes') & (df_sub['year'] == year)]

        for practice_term_col in practice_term_cols:
            if practice_term_col not in dict_practice_term_articles_or_events[year]:
                dict_practice_term_articles_or_events[year][practice_term_col] = set()

        # assert year_subset.shape[0] > 0

        for i, row in year_subset.iterrows():

            if article_level:
                dict_relevant_articles_or_events[year].add(row['index'])  # different from article_idx (this one doible counts for multiple companies)
                # relevant_articles_or_events.add(row['index'])
            else:
                dict_relevant_articles_or_events[year].add(row['TVL ID'])
                # relevant_articles_or_events.add(row['TVL ID'])

            for practice_term_col in practice_term_cols:

                # if practice_term_col not in dict_practice_term_articles_or_events[year]:
                #     dict_practice_term_articles_or_events[year][practice_term_col] = set()
                # if practice_term_col not in practice_term_articles_or_events:
                #     practice_term_articles_or_events[practice_term_col] = set()

                # practice_category = practice_term_col.split('_')[2]
                # if practice_category not in dict_practice_category_articles_or_events[year]:
                #     dict_practice_category_articles_or_events[year][practice_category] = set()

                if row[practice_term_col] > 0:
                    if article_level:
                        dict_practice_term_articles_or_events[year][practice_term_col].add(row['index'])
                        # practice_term_articles_or_events[practice_term_col].add(row['index'])
                        ## dict_practice_category_articles_or_events[year][practice_term_col].add(row['index'])
                        # practice_category_articles_or_events[practice_category].add(row['index'])
                    else:
                        dict_practice_term_articles_or_events[year][practice_term_col].add(row['TVL ID'])
                        # practice_term_articles_or_events[practice_term_col].add(row['TVL ID'])
                        ## dict_practice_category_articles_or_events[year][practice_term_col].add(row['TVL ID'])
                        # practice_category_articles_or_events[practice_category].add(row['TVL ID'])

    col_name_relevant_articles_or_events = "Yearly LCSC Relevant Article count" if article_level else "Yearly LCSC Relevant Event count"
    df_relevant_articles_or_events = pd.DataFrame(columns=['Year', col_name_relevant_articles_or_events])
    for year in range(MIN_YEAR, MAX_YEAR + 1):
        df_relevant_articles_or_events = df_relevant_articles_or_events.append(
            {'Year': year,
             col_name_relevant_articles_or_events: len(dict_relevant_articles_or_events[year])}, ignore_index=True)
    # df_relevant_articles_or_events = df_relevant_articles_or_events.append(
    #     {col_name_relevant_articles_or_events: len(relevant_articles_or_events)}, ignore_index=True
    # )

    col_name_pterm_article_or_event = "Yearly Article count of practice term" if article_level else "Yearly Event count of practice term"
    df_practice_term_articles_or_events = pd.DataFrame(columns=['Year', 'Practice term', col_name_pterm_article_or_event])
    for year in range(MIN_YEAR, MAX_YEAR + 1):
        for p_term, set_IDs in dict_practice_term_articles_or_events[year].items():
            df_practice_term_articles_or_events = df_practice_term_articles_or_events.append(
                {'Year': year, 'Practice term': p_term, col_name_pterm_article_or_event: len(set_IDs)}, ignore_index=True
            )
    # df_practice_term_articles_or_events = df_practice_term_articles_or_events.sort_values(
    #     by=col_name_pterm_article_or_event, ascending=False)

    # col_name_pcat_article_or_event = "Article count of practice category" if article_level else "Event count of practice category"
    # df_practice_category_articles_or_events = pd.DataFrame(columns=['Practice category', col_name_pcat_article_or_event])
    # for year in range(MIN_YEAR, MAX_YEAR + 1):
    #     for p_term, set_IDs in dict_practice_category_articles_or_events[year].items():
    #         df_practice_category_articles_or_events = df_practice_category_articles_or_events.append(
    #             {'Year': year, 'Practice category': p_term, col_name_pcat_article_or_event: len(set_IDs)}, ignore_index=True
    #         )
    # df_practice_category_articles_or_events = df_practice_category_articles_or_events.sort_values(
    #     by=col_name_pterm_article_or_event, ascending=False)

    # Remove counts of terms containing another term from the term's category itself
    # TODO: Add to this dict as needed for future terms
    subterm_category_practice = {
        'wage': 'Wages',
        'lead time': 'Negative-Practices',
        'purchasing': 'Other',
        'representation': 'Other',
        'responsible exit': 'Good-Practices'
    }
    for subterm, category in subterm_category_practice.items():
        remove_dupe_counts_of_practice_term(subterm, category, col_name_pterm_article_or_event,
                                            df_practice_term_articles_or_events)

    # Get totals for each practice term's co-occurrences with a risk term, regardless of industry
    if sector != 0:
        industries = industry_to_sector_map[industry_to_sector_map['SECTOR_FULL_NAME'] == sector][
            'TVL Industry Abbrev'].values.tolist()
        print(industries)
        df_sub2 = labeled_industry_articles[labeled_industry_articles['INDUSTRY'].isin(industries)]
    elif industry != 0:
        df_sub2 = labeled_industry_articles[labeled_industry_articles['INDUSTRY'].isin([industry])]
    else:
        df_sub2 = labeled_industry_articles

    dict_practice_risk_articles_or_events = {year: dict() for year in range(MIN_YEAR, MAX_YEAR+1)}
    # dict_practice_cat_risk_articles_or_events = {year: dict() for year in range(MIN_YEAR, MAX_YEAR + 1)}
    # practice_risk_articles_or_events = {}
    for year in range(MIN_YEAR, MAX_YEAR + 1):
        year_subset = df_sub2[(df_sub2['ANY_PRACTICE_AND_RISK'] == 1) & (df_sub2['RELEVANT?'] == 'Yes') & (df_sub['year'] == year)]

        for practice_term_col in practice_term_cols:
            if practice_term_col not in dict_practice_risk_articles_or_events[year]:
                dict_practice_risk_articles_or_events[year][
                    practice_term_col] = dict()  # {'practice term': {'risk_term': set()}}

        # assert year_subset.shape[0] > 0

        for i, row in year_subset.iterrows():
            for practice_term_col in practice_term_cols:

                # if practice_term_col not in dict_practice_risk_articles_or_events[year]:
                #     dict_practice_risk_articles_or_events[year][practice_term_col] = dict()  # {'practice term': {'risk_term': set()}}

                # practice_category = practice_term_col.split('_')[2]
                # if practice_category not in dict_practice_cat_risk_articles_or_events[year]:
                #     dict_practice_cat_risk_articles_or_events[year][practice_category] = set()

                if row[practice_term_col] > 0:
                    for risk_term_col in risk_term_cols:

                        if risk_term_col not in dict_practice_risk_articles_or_events[year][practice_term_col].keys():
                            dict_practice_risk_articles_or_events[year][practice_term_col][risk_term_col] = set()
                        # if risk_term_col not in dict_practice_cat_risk_articles_or_events[year][practice_category].keys():
                        #     dict_practice_cat_risk_articles_or_events[year][practice_category][risk_term_col] = set()

                        if row[risk_term_col] > 0:
                            if article_level:
                                dict_practice_risk_articles_or_events[year][practice_term_col][risk_term_col].add(row['index'])
                                # dict_practice_cat_risk_articles_or_events[year][practice_category][risk_term_col].add(row['index'])
                            else:
                                dict_practice_risk_articles_or_events[year][practice_term_col][risk_term_col].add(row['TVL ID'])
                                # dict_practice_cat_risk_articles_or_events[year][practice_category][risk_term_col].add(
                                #     row['TVL ID'])

    col_name_pterm_rterm_article_or_event = "Yearly Article count of co-occurrence" if article_level else "Yearly Event count of co-occurrence"
    df_practice_risk_articles_or_events = pd.DataFrame(
        columns=['Year', 'Practice term', 'Risk term', col_name_pterm_rterm_article_or_event])
    for year in range(MIN_YEAR, MAX_YEAR + 1):
        for p_term, r_terms in dict_practice_risk_articles_or_events[year].items():
            for r_term, set_IDs in r_terms.items():
                df_practice_risk_articles_or_events = df_practice_risk_articles_or_events.append(
                    {'Year': year, 'Practice term': p_term, 'Risk term': r_term, col_name_pterm_rterm_article_or_event: len(set_IDs)},
                    ignore_index=True)

    # df_practice_cat_risk_articles_or_events = pd.DataFrame(
    #     columns=['Year', 'Practice category', 'Risk term', col_name_pterm_rterm_article_or_event])
    # for year in range(MIN_YEAR, MAX_YEAR + 1):
    #     for p_cat, r_terms in dict_practice_cat_risk_articles_or_events[year].items():
    #         for r_term, set_IDs in r_terms.items():
    #             df_practice_cat_risk_articles_or_events = df_practice_cat_risk_articles_or_events.append(
    #                 {'Year': year, 'Practice category': p_cat, 'Risk term': r_term,
    #                  col_name_pterm_rterm_article_or_event: len(set_IDs)},
    #                 ignore_index=True)  # TODO: Add this to the outputs!
    # df_practice_risk_articles_or_events = df_practice_risk_articles_or_events.sort_values(
    #     by=col_name_pterm_rterm_article_or_event, ascending=False)

    # TODO: Add to this dict as needed for future terms
    subterm_category_risk = {
        'disruption': 'Operational-Costs',
    }
    for subterm, category in subterm_category_risk.items():
        remove_dupe_counts_of_risk_term(
            subterm, category, col_name_pterm_rterm_article_or_event, df_practice_risk_articles_or_events)

    if not generate_merge:
        return df_relevant_articles_or_events, df_practice_term_articles_or_events, df_practice_risk_articles_or_events, None, None

    merge_practice_counts_with_risk_cooccurs = pd.merge(
        df_practice_term_articles_or_events, df_practice_risk_articles_or_events, how='left', on='Practice term')
    merge_practice_counts_with_risk_cooccurs[col_name_pterm_article_or_event] = merge_practice_counts_with_risk_cooccurs[
        col_name_pterm_article_or_event].astype(float)
    merge_practice_counts_with_risk_cooccurs[col_name_pterm_rterm_article_or_event] = merge_practice_counts_with_risk_cooccurs[
        col_name_pterm_rterm_article_or_event].astype(float)
    merge_practice_counts_with_risk_cooccurs['Co-occurrences over Total Practice count'] = 0
    merge_practice_counts_with_risk_cooccurs['Co-occurrences over Total Practice count'] = np.where(
        merge_practice_counts_with_risk_cooccurs[col_name_pterm_article_or_event] > 0,
        merge_practice_counts_with_risk_cooccurs[col_name_pterm_rterm_article_or_event] / merge_practice_counts_with_risk_cooccurs[
            col_name_pterm_article_or_event], 0)
    merge_practice_counts_with_risk_cooccurs = merge_practice_counts_with_risk_cooccurs.sort_values(
        by='Co-occurrences over Total Practice count', ascending=False)

    if not generate_heatmap:
        return df_relevant_articles_or_events, df_practice_term_articles_or_events, df_practice_risk_articles_or_events, merge_practice_counts_with_risk_cooccurs, None

    df4 = merge_practice_counts_with_risk_cooccurs.pivot_table(
        index='Practice term', columns='Risk term', values='Co-occurrences over Total Practice count')
    plotly_dict = df_to_plotly(df4)

    fig = ff.create_annotated_heatmap(z=plotly_dict['z'],
                                      x=plotly_dict['x'],
                                      y=plotly_dict['y'],
                                      annotation_text=plotly_dict['z'],
                                      colorscale='YlGnBu')

    # Make text size smaller
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 10
        fig.layout.annotations[i].text = str(round(float(fig.layout.annotations[i].text), 1))
        if fig.layout.annotations[i].text == '0.0':
            fig.layout.annotations[i].font.size = 1

    fig.update_layout(autosize=False,
        width=1600,
        height=5*df_practice_term_articles_or_events.shape[0] + 600)

    return df_relevant_articles_or_events, df_practice_term_articles_or_events, df_practice_risk_articles_or_events, merge_practice_counts_with_risk_cooccurs, fig


def remove_dupe_counts_of_practice_term(practice_term_to_check, category_practice_term_to_check,
                                        col_name_pterm_article_or_event, df_practice_articles_or_events):
    # Example: Remove counts of terms containing "wage" from "wage_PRACTICE_Wages" itself
    for year in range(MIN_YEAR, MAX_YEAR+1):
        all_pterms_containing_term = df_practice_articles_or_events[
            (df_practice_articles_or_events['Practice term'].str.contains(practice_term_to_check)) & (df_practice_articles_or_events['Year'] == year)]
        if all_pterms_containing_term.shape[0] > 0:
            count_to_subtract_from_term = 0
            for i, row in all_pterms_containing_term.iterrows():
                pterm = row['Practice term']
                if pterm.split('_')[0] == practice_term_to_check:
                    continue
                count_to_subtract_from_term += int(row[col_name_pterm_article_or_event])

            term_idx = \
                df_practice_articles_or_events.index[
                    (df_practice_articles_or_events[
                        'Practice term'] == f'{practice_term_to_check}_PRACTICE_{category_practice_term_to_check}') & (df_practice_articles_or_events['Year'] == year)].tolist()[
                    0]
            df_practice_articles_or_events.loc[term_idx][col_name_pterm_article_or_event] = \
                df_practice_articles_or_events.loc[term_idx][
                    col_name_pterm_article_or_event] - count_to_subtract_from_term


def remove_dupe_counts_of_risk_term(risk_term_to_check, category_risk_term_to_check, col_name_pterm_rterm_article_or_event,
                                    df_practice_risk_articles_or_events):
    # Same as above function but for risk terms
    for year in range(MIN_YEAR, MAX_YEAR + 1):
        all_rterms_containing_term = df_practice_risk_articles_or_events[
            (df_practice_risk_articles_or_events['Risk term'].str.contains(risk_term_to_check)) & (df_practice_risk_articles_or_events['Year'] == year)]
        if all_rterms_containing_term.shape[0] > 0:
            count_to_subtract_from_term = 0
            for i, row in all_rterms_containing_term.iterrows():
                rterm = row['Risk term']
                if rterm.split('_')[0] == risk_term_to_check:
                    continue
                count_to_subtract_from_term += int(row[col_name_pterm_rterm_article_or_event])

            term_idx = \
                df_practice_risk_articles_or_events.index[
                    (df_practice_risk_articles_or_events[
                        'Risk term'] == f'{risk_term_to_check}_RISK_{category_risk_term_to_check}') & (df_practice_risk_articles_or_events['Year'] == year)].tolist()[
                    0]
            df_practice_risk_articles_or_events.loc[term_idx][col_name_pterm_rterm_article_or_event] = \
                df_practice_risk_articles_or_events.loc[term_idx][
                    col_name_pterm_rterm_article_or_event] - count_to_subtract_from_term


if __name__ == '__main__':
    args = parse_cmd_line_args()
    labeled_industry_articles = pd.read_csv(args.labeled_industry_articles_path)
    industry_to_sector_map = pd.read_csv(args.industry_to_sector_map_path)
    dict_industry_to_sector_map = dict(
        zip(industry_to_sector_map['TVL Industry Abbrev'], industry_to_sector_map.SECTOR_FULL_NAME))
    print('Total industries:', len(dict_industry_to_sector_map))

    # Print stats related to labor heuristic
    # The labor keyword indicators (a heuristic built in early Oct) pick up 164/215 relevant articles (77%)
    print(labeled_industry_articles[labeled_industry_articles['RELEVANT?'] == 'Yes'].shape)
    print(labeled_industry_articles[
              (labeled_industry_articles['labo[u]r_ind'] == 1) | (labeled_industry_articles['worker_ind'] == 1) | (
                      labeled_industry_articles['wage_ind'] == 1)]['RELEVANT?'].value_counts())

    # Get lists of practice/risk term cols
    unwanted_cols = ['ANY_PRACTICE_AND_RISK', 'ANY_PRACTICE_TERM', 'PRACTICE_TERMS_FOUND', 'ANY_RISK_TERM',
                     'RISK_TERMS_FOUND', 'ANY_RISK_AND_marked_labor_relevant']
    practice_term_cols = [col for col in list(labeled_industry_articles.columns) if
                          'PRACTICE' in col and col not in unwanted_cols]
    risk_term_cols = [col for col in list(labeled_industry_articles.columns) if
                      'RISK' in col and col not in unwanted_cols]

    # # Create index column at the Company-Industry-TVL_ID level
    # labeled_industry_articles = labeled_industry_articles.set_index(
    #     ['Company', 'INDUSTRY', 'TVL ID']).reset_index().reset_index()

    # The articles do not contain duplicates at the industry level (from tvl_run.py)
    # (this way, we don't double-count an article within the same industry)
    # So, we're creating an index for each article here, since each article is already unique:
    labeled_industry_articles = labeled_industry_articles.reset_index()

    # Initialize dataframe for all GIC articles/events by industry/sector
    col_name_relevant_articles_or_events = "Yearly LCSC Relevant Article count" if args.article_level else "Yearly LCSC Relevant Event count"
    df_all_industry_relevant = pd.DataFrame(
        columns=['SECTOR', 'INDUSTRY', 'Year', col_name_relevant_articles_or_events]
    )

    # Initialize dataframe for practice terms by industry/sector
    col_name_pterm_article_or_event = "Yearly Article count of practice term" if args.article_level else "Yearly Event count of practice term"
    df_all_industry_practices = pd.DataFrame(
        columns=['SECTOR', 'INDUSTRY', 'Year', 'Practice term', col_name_pterm_article_or_event])

    # Initialize dataframe for practice-risk co-occurrences by industry/sector
    col_name_pterm_rterm_article_or_event = "Yearly Article count of co-occurrence" if args.article_level else "Yearly Event count of co-occurrence"
    df_all_industry_cooccurs = pd.DataFrame(
        columns=['SECTOR', 'INDUSTRY', 'Year', 'Practice term', 'Risk term', col_name_pterm_rterm_article_or_event])

    for industry, sector in dict_industry_to_sector_map.items():
        # print('Industry:', industry)
        df_relevant_articles_or_events, df_practice_term_articles_or_events, df_practice_risk_articles_or_events, merge_practice_counts_with_risk_cooccurs, fig = get_industry_level_practice_breakdown(
            labeled_industry_articles, industry_to_sector_map, article_level=args.article_level,
            generate_merge=args.generate_merge, generate_heatmap=args.generate_heatmap, industry=industry)

        df_relevant_articles_or_events.insert(loc=0, column='INDUSTRY', value=industry)
        df_relevant_articles_or_events.insert(loc=0, column='SECTOR', value=sector)
        df_all_industry_relevant = df_all_industry_relevant.append(df_relevant_articles_or_events, ignore_index=True)
        # print(df_all_industry_relevant['INDUSTRY'].nunique())

        df_practice_term_articles_or_events.insert(loc=0, column='INDUSTRY', value=industry)
        df_practice_term_articles_or_events.insert(loc=0, column='SECTOR', value=sector)
        df_all_industry_practices = df_all_industry_practices.append(df_practice_term_articles_or_events, ignore_index=True)
        # print(df_all_industry_practices['INDUSTRY'].nunique())

        df_practice_risk_articles_or_events.insert(loc=0, column='INDUSTRY', value=industry)
        df_practice_risk_articles_or_events.insert(loc=0, column='SECTOR', value=sector)
        df_all_industry_cooccurs = df_all_industry_cooccurs.append(df_practice_risk_articles_or_events,
                                                                   ignore_index=True)
        # print(df_all_industry_cooccurs['INDUSTRY'].nunique())
        # print()

    article_level_abbrev = "Article_Level" if args.article_level else "Event_Level"
    df_all_industry_relevant.to_csv(
        f'{datetime.datetime.today().month}_{datetime.datetime.today().day}-{args.abbrev}-Total_Relevant_{article_level_abbrev}_Breakdown.csv',
        index=False)
    df_all_industry_practices.to_csv(
        f'{datetime.datetime.today().month}_{datetime.datetime.today().day}-{args.abbrev}-Practice_{article_level_abbrev}_Breakdown.csv',
        index=False)
    df_all_industry_cooccurs.to_csv(
        f'{datetime.datetime.today().month}_{datetime.datetime.today().day}-{args.abbrev}-Practice_Risk_Cooccurrences_{article_level_abbrev}_Breakdown.csv',
        index=False)
    # if args.generate_merge:
    #     merge_practice_counts_with_risk_cooccurs.to_csv(
    #         f'{datetime.datetime.today().month}_{datetime.datetime.today().day}-{args.abbrev}-Practice_Cooccurs_Merge_{article_level_abbrev}_Breakdown.csv',
    #         index=False)
    # if args.generate_heatmap:
    #     fig.write_image(f"{datetime.datetime.today().month}_{datetime.datetime.today().day}-{args.abbrev}-Practice_Cooccurs_Merge_{article_level_abbrev}_Breakdown.png")
