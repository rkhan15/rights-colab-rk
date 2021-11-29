import argparse

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

    # Get dictionaries of practice/risk/supplier terms
    practice_terms_regex_dict = create_comprehensive_term_regex_cleaning_dict(
        term_type='practice',
        category_to_term_mapping_SIMPLE=practice_category_to_term_mapping_SIMPLE,
        category_to_term_mapping_COMPLEX=practice_category_to_term_mapping_COMPLEX)

    risk_terms_regex_dict = create_comprehensive_term_regex_cleaning_dict(
        term_type='risk',
        category_to_term_mapping_SIMPLE=risk_category_to_term_mapping_SIMPLE,
        category_to_term_mapping_COMPLEX=risk_category_to_term_mapping_COMPLEX)

    supplier_relship_regex_dict = create_comprehensive_term_regex_cleaning_dict(
        term_type='supplier-relship',
        category_to_term_mapping_SIMPLE=supplier_relship_category_to_term_mapping_SIMPLE,
        category_to_term_mapping_COMPLEX=supplier_relship_category_to_term_mapping_COMPLEX)

    # Adding extra cleaning terms here (during processing, any mentions of
    # practice/risk terms in the irrelevant contexts below will be excluded)

    # agent
    # practice_terms_regex_dict['Mdrn-Slav-Risk']['agent']['extra_cleaning'] = True
    # practice_terms_regex_dict['Mdrn-Slav-Risk']['agent']['terms_to_remove'] = ['recruitment agent']

    # third party
    # practice_terms_regex_dict['Mdrn-Slav-Risk']['third party']['extra_cleaning'] = True
    # practice_terms_regex_dict['Mdrn-Slav-Risk']['third party']['terms_to_remove'] = ['independent third party']

    # union
    practice_terms_regex_dict['Good-Practices']['union']['extra_cleaning'] = True
    practice_terms_regex_dict['Good-Practices']['union']['terms_to_remove'] = ['european union', 'customs union']

    # fine
    risk_terms_regex_dict['Financial-Loss']['fine']['extra_cleaning'] = True
    risk_terms_regex_dict['Financial-Loss']['fine']['terms_to_remove'] = ['finecast', 'fine fragrance', 'fine and tall',
                                                                          'driftable fine', 'fine chemical',
                                                                          'fine construction level', 'fine-grain',
                                                                          'fine partic', 'finergreen', 'fine molecular',
                                                                          'fine wine', 'fine product', 'fine paper',
                                                                          'fine balanc', 'fine-tun', 'fine fib',
                                                                          'finely', 'fine, sand', 'fine tea', 'finest',
                                                                          'finesse']

    # strike
    risk_terms_regex_dict['Worker-Protest']['strike']['extra_cleaning'] = True
    risk_terms_regex_dict['Worker-Protest']['strike']['terms_to_remove'] = ["disaster(s\b|\b) strike", 'strike deal',
                                                                            'weather strike', 'bridge strike']

    # reimbursement
    risk_terms_regex_dict['Financial-Loss']['reimburse']['extra_cleaning'] = True
    risk_terms_regex_dict['Financial-Loss']['reimburse']['terms_to_remove'] = ['tuition reimbursement']
    risk_terms_regex_dict['Remedy']['reimburse']['extra_cleaning'] = True
    risk_terms_regex_dict['Remedy']['reimburse']['terms_to_remove'] = ['tuition reimbursement']

    # block import
    risk_terms_regex_dict['Operational-Costs']['block import']['extra_cleaning'] = True
    risk_terms_regex_dict['Operational-Costs']['block import']['terms_to_remove'] = ['import bank']

    # pricing pressure
    practice_terms_regex_dict['Negative-Practices']['pricing pressure']['context_words'] = ['supplier', 'factory',
                                                                                            'manufactur', 'warehouse',
                                                                                            'workshop']

    # all supplier context words:
    relationship_words = ['relationship', 'purchaser', 'order', 'lead time', 'cancel([l]?(ed)|([l]?ing))? order',
                          'buyer', 'outsourc', 'subcontract']
    for core_term in supplier_relship_category_to_term_mapping_SIMPLE['Core']:
        supplier_relship_regex_dict['Core'][core_term]['context_words'] = relationship_words
    for core_term in supplier_relship_category_to_term_mapping_COMPLEX['Core']:
        supplier_relship_regex_dict['Core'][core_term]['context_words'] = relationship_words

    # Create indicators for all events and all terms
    industry_all_events_dict = label_all_industry_events_with_term_indicators(
        industry_files, args.tvl_raw_dir, args.gic_dir, practice_terms_regex_dict,
        risk_terms_regex_dict, supplier_relship_regex_dict)

    # Put all the Sup Chain events in one master df
    all_industries_events_master_df = pd.concat(
        [industry_df for industry_name, industry_df in industry_all_events_dict.items()], ignore_index=True)
    print(all_industries_events_master_df.shape)

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
    # all_industries_events_master_df.columns

    for i, col in enumerate(['ANY_PRACTICE_TERM',
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

    # Drop duplicate articles for within each industry, to count each article at the INDUSTRY level only ONCE
    # (Drop duplicates on ("INDUSTRY" and) "Primary Article Spotlight Headline" and "Primary Article Bullet Points" and "Spotlight Start Date")
    # (This is because we only care about each article at the INDUSTRY level, not the TVL ID level (company + event))
    all_industries_events_master_df = all_industries_events_master_df.drop_duplicates(
        ['INDUSTRY', 'Primary Article Spotlight Headline', 'Primary Article Bullet Points', 'Spotlight Start Date'],
        keep='first')
    print("Total articles:", all_industries_events_master_df.shape[0])
    print("Number of ARTICLES with a practice-risk co-occurrence:", all_industries_events_master_df['ANY_PRACTICE_AND_RISK'].sum())
    print("Total events:", all_industries_events_master_df['TVL ID'].nunique())
    print("Number of EVENTS with a practice-risk co-occurrence", all_industries_events_master_df.groupby(['INDUSTRY', 'TVL ID'])['ANY_PRACTICE_AND_RISK'].sum().reset_index()['ANY_PRACTICE_AND_RISK'].value_counts().reset_index().iloc[1:]['ANY_PRACTICE_AND_RISK'].sum())

    # SAVE ALL EVENTS WITH ALL INDICATORS
    all_industries_events_master_df.to_csv(
        f'{datetime.datetime.today().month}_{datetime.datetime.today().day}-{args.abbrev}-Industry_Article_Lvl.csv',
        index=False)