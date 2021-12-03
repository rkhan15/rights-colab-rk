import re

# FIND SUPPLY CHAIN MGMT-RELATED TERMS ONLY BELOW

START_REGEX = '(?<![^ .,?!;])'


def attach_regex_to_beginning_of_terms(terms_lst, regex=START_REGEX):
    if regex == '(?<![^ .,?!;])':
        return [regex + term for term in terms_lst]


def create_comprehensive_term_regex_cleaning_dict(
        term_type, category_to_term_mapping_SIMPLE, category_to_term_mapping_COMPLEX):
    # term_type_dict = {'term_type_cat': {'clean term': 'regex_lst': {['fmt1', 'fmt2']}, 'extra_cleaning': True}}
    term_type_regexes_cleaning = {}
    for term_cat, term_lst in category_to_term_mapping_SIMPLE.items():

        # Create dictionary for term type category
        if term_cat not in term_type_regexes_cleaning:
            term_type_regexes_cleaning[term_cat] = dict()

        # Variable for new category dict for `term_type_regexes_cleaning`
        term_cat_dict = term_type_regexes_cleaning[term_cat]

        term_cat_SIMPLE_lst = category_to_term_mapping_SIMPLE[term_cat]
        for term_SIMPLE in term_cat_SIMPLE_lst:
            # term_regex = re.compile(attach_regex_to_beginning_of_terms([term_SIMPLE])[0])
            term_regex_str_lst = attach_regex_to_beginning_of_terms([term_SIMPLE])
            # term_cat_dict[term_SIMPLE] = {'regex_lst': [re.compile(START_REGEX + regex) for regex in term_regex_str_lst], 'extra_cleaning': False, 'terms_to_remove': []}  # TODO: Create detailed function for examples of the term to ignore, wich will have extra_cleaning=True
            term_cat_dict[term_SIMPLE] = {'regex_lst': [re.compile(regex) for regex in term_regex_str_lst],
                                          'extra_cleaning': False, 'terms_to_remove': [],
                                          'context_words': []}  # TODO: Create detailed function for examples of the term to ignore, wich will have extra_cleaning=True

        term_cat_COMPLEX = category_to_term_mapping_COMPLEX[term_cat]
        for term_clean_COMPLEX, term_COMPLEX_regex_list in term_cat_COMPLEX.items():
            # term_regex_str_lst = attach_regex_to_beginning_of_terms(term_COMPLEX_dict)
            term_cat_dict[term_clean_COMPLEX] = {'regex_lst': [re.compile(regex) for regex in term_COMPLEX_regex_list],
                                                 'extra_cleaning': False, 'terms_to_remove': [], 'context_words': []}

        term_type_regexes_cleaning[term_cat] = term_cat_dict

    return term_type_regexes_cleaning


# Risk terms
risk_category_to_term_mapping_SIMPLE = {
    'Worker-Protest': ['strike', 'sit-in', 'operational disruption',
                       'protest', 'injury'],

    'Consumer-Protest': ['boycott', 'protest', 'social license'],

    'Operational-Costs': ['operational disruption', 'operating cost', 'delay',
                          'disruption'],

    'Financial-Loss': ['sanction', 'reimburse', 'restitution', 'fine',
                       'compensation', 'penalt', 'bankrupt', 'liabl', 'loss', 'lost'],

    'Legal-Risk': ['lawsuit', 'litigation', 'impoundment', 'detain',
                   'penalt', 'sanction', 'court'],

    'Reputational-Damage': ['brand damage', 'monetary damage',
                            'reputation', 'brand recognition',
                            'social license',
                            'decreased trust',
                            'decreased innovation',
                            'lost opportunit',
                            ],

    "Remedy": ['reimburse', 'compensation', 'divest', 'restitution'],

    "Modern-Slavery": ['modern slavery', 'debt bondage', 'human traffic'],

    'Other': ['alleg', 'accus', 'exploit', 'expose', 'investigat',
              'police', 'enforcement', 'security force', 'inspection', 'inspector',
              ],

    'Other-RK': ['scandal', 'government action', 'share price', 'share value',
                 'investment'
                 # 'sales'
                 ]
}

risk_category_to_term_mapping_COMPLEX = {
    'Worker-Protest': {'walkout': attach_regex_to_beginning_of_terms(['walk[- ]?out'])},
    'Consumer-Protest': {'social license': attach_regex_to_beginning_of_terms(['social licen[cs]e'])},
    'Operational-Costs': {
        'withhold release order': attach_regex_to_beginning_of_terms(['withhold release order', 'wro[s]?\W']),
        'block import': attach_regex_to_beginning_of_terms(['block(.*)import', 'ban(.*)import', 'import(.*)ban',
                                                            'prohibit(.*)import', 'import(.*)prohibit',
                                                            'block(.*)entry', 'entry(.*)block',
                                                            'seiz(.*)product', 'product(.*)seiz']), },
    'Financial-Loss': {'pay damages': attach_regex_to_beginning_of_terms(['pay(.*)damage']),
                       'seizure of assets': attach_regex_to_beginning_of_terms(['seiz(.*)asset']), },
    'Legal-Risk': {},
    'Reputational-Damage': {
        'workplace shutdown': attach_regex_to_beginning_of_terms(['workplace shutdown', 'shutdown']),
        'social license': attach_regex_to_beginning_of_terms(['social licen[cs]e'])},
    "Remedy": {},
    "Modern-Slavery": {
        'forced labor': attach_regex_to_beginning_of_terms(['(forced|slave) labo[u]?r']),
        'child labor': attach_regex_to_beginning_of_terms(['child labo[u]?r', 'child slave']),
    },
    'Other': {
            'turnover': attach_regex_to_beginning_of_terms(
                ['high turnover', 'worker turnover', 'employee turnover', 'turnover rate',
                 'voluntary turnover',  # because of START_REGEX, "involuntary turnover" is automatically left out
                 'quit[s]? rate', 'rate of quit'
                 ]
            ),
        },
    'Other-RK': {'negative return': attach_regex_to_beginning_of_terms(['negative(.*)return']),
                 'long-term': attach_regex_to_beginning_of_terms(['long[- ]?term'])}
}

# Practice terms
practice_category_to_term_mapping_SIMPLE = {
    'Wages': [
        'wage',
        'wage theft', 'stolen wage',
        'living wage'],
    'Immigrants': [],
    'Precarious-Work': [
        'precarity',
        'gig work',
        'alternative work',
        'alternate work',
        'contingent work',
        # 'migrant',
        'informal work',
        'casual work',
        'hazardous work'
    ],
    'Mdrn-Slav-Risk': [  # 'broker', 'agent',
        'confinement', 'document retention',
        'restriction of movement',
        'delayed wage',
        'pay manipulation',
        'punishment', 'poor food', 'retaliat',
        'sexual violence', 'sexual harassment', 'sex abuse',
        'deprivation',
        'unpaid wage',
        'delayed payment', 'wage violation'
    ],

    'Work-Conditions': [
        # 'reprisal', # reprisals
        # 'health and safety',
        # 'lockout',
        'employee morale',
        'freedom of association',
        'collective bargaining',
        'work stoppage',
        'hotline',
        'worker retention'
    ],
    'Good-Practices': ['code of conduct', 'due diligence',
                       'ethical recruit',  # ethical recruitment
                       'handbook',  # supplier handbook
                       'supplier remediation',
                       'social audit',
                       # 'risk assessment',
                       'worker engagement',
                       'transparency', 'traceability', 'visibility',
                       'supply chain map',
                       'timely payments',
                       'fair terms of payment',  # Added 11/28
                       # 'training',  # TODO: GET BACK TO THIS AFTER THE FALL # Added 11/28
                       # 'contract',  # TODO: GET BACK TO THIS AFTER THE FALL # Added 11/28
                       'union', 'worker committee'
                       ],
    'Neutral-Practices': [
        # 'sourcing',
        'outsourc',  # Kept based on Joanne's feedback
        # 'raw material', # raw materials,
        # 'subcontracting',
        'small-holder supply chain',
        # 'overtime',
        'demand volatility',
    ],
    'Negative-Practices': [
        # 'conflict',
        'order delay',
        'lead time',  # previously 'short lead time'
        'unplanned shipment',
        'corruption',
        # 'fraud',
        'quota system', 'delayed payment',
        'weak governance', 'wage violation',
        'informal supply chain', 'last-minute order modification',
        'unfair timing demand', 'pricing pressure',
        'poor forecasting',
        'cancellation'  # Added 11/28
    ],
    'Other': ['labor rights violation',
              'worker representation', 'representation',  # Added 11/28
              'purchasing', 'purchasing practices',  # Added 11/28
              ]
}

practice_category_to_term_mapping_COMPLEX = {
    'Wages': {
        # 'pricing': attach_regex_to_beginning_of_terms(['pricing', 'price']),
        'low wages': attach_regex_to_beginning_of_terms(['low wage', 'poverty-level wage']),
        'underpay': attach_regex_to_beginning_of_terms(['underpay', 'underpaid', '(inadequate|reduced|no) pay'])},
    'Immigrants': {
        'visa worker': attach_regex_to_beginning_of_terms(['visa work', 'work(er)? visa'])
    },
    'Precarious-Work': {
        'temporary worker-employee': attach_regex_to_beginning_of_terms(['temporary(.*)work', 'temporary(.*)employ',
                                                                         'temporary(.*)contract',
                                                                         'non(- )?permanent contract']),
        'contract labor': attach_regex_to_beginning_of_terms(['contract labo[u]?r', 'contract work']),
        'precarious work': attach_regex_to_beginning_of_terms(['precarious work', 'precarious job']), },
    'Mdrn-Slav-Risk': {
        # 'third party': attach_regex_to_beginning_of_terms(['third[- ]party'])
        'coercive labor': attach_regex_to_beginning_of_terms(['coercive labo[u]?r']),
        'prison labor': attach_regex_to_beginning_of_terms(['prison labo[u]?r']),
        'recruitment fee': attach_regex_to_beginning_of_terms(['recruitment(.*)fee']),
        'withhold wage': attach_regex_to_beginning_of_terms(['withh[oe]ld(ing)? wage']),
        'passport retention': attach_regex_to_beginning_of_terms(
            ['passport retention', 'retention of passport', 'withh[oe]ld(ing)? passport'])
    },
    'Work-Conditions': {'collective bargaining agreement': attach_regex_to_beginning_of_terms(
        ['collective bargaining agreement', 'cba[s]?\W']),
                        'unsafe conditions': attach_regex_to_beginning_of_terms(
                            ['unsafe(.*)condition', 'hazard(.*)condition', 'working conditions',
                             'deteriorating(.*)condition']),
                        'grievance mechanism': attach_regex_to_beginning_of_terms(
                            ['grievance[s]?', '(grievance|complaint) (mechanism|system|procedure|handl)', 'handl(.*)grievance', 'anonymous complaint'])},
    'Good-Practices': {'code of conduct negative': attach_regex_to_beginning_of_terms(
        ['code of conduct(.*)breach', 'breach(.*)code of conduct',
         'violat(.*)code of conduct', 'code of conduct(.*)violat',
         'non[- ]?compliance(.*)code of conduct', 'code of conduct(.*)non[- ]?compliance',
         'break(.*)code of conduct',
         'broken(.*)code of conduct', 'code of conduct(.*)broken',
         'fail(.*)code of conduct']),
        'responsible exit': attach_regex_to_beginning_of_terms(['responsibl[e|y](.*)exit', 'exit(.*)responsibl[e|y]'])
                       },
    'Neutral-Practices': {'corrective action': attach_regex_to_beginning_of_terms(
        ['corrective(.*)action', 'corrective(.*)plan', 'corrective(.*)measure'])
    },
    'Negative-Practices': {
        # 'piece work': attach_regex_to_beginning_of_terms(['piece work', 'piece[- ]rate']),
        'production target': attach_regex_to_beginning_of_terms(['production target', 'production quota', 'strict quota']),
        'hour violation': attach_regex_to_beginning_of_terms(['hour (law )?violation']),
        'canceled order': attach_regex_to_beginning_of_terms(['cancel([l]?(ed)|([l]?ing))? order',
                                                              'order cancellation']),  # <- Added 11/28
        'overtime NEGATIVE': attach_regex_to_beginning_of_terms(
            ['(forced|unpaid|chronic|mandatory|illegal) overtime', 'long hours', 'overwork', 'off the clock']),
        'lead time NEGATIVE': attach_regex_to_beginning_of_terms(['short lead time', 'inadequate lead time']),
        'irresponsible exit': attach_regex_to_beginning_of_terms(['irresponsibl[e|y](.*)exit', 'exit(.*)irresponsibl[e|y]'])
    },
    'Other': {
        'ringfence labor': attach_regex_to_beginning_of_terms(['ringfence labo[u]?r']),  # Added 11/28
        'labor costs': attach_regex_to_beginning_of_terms(['labo[u]?r cost']),  # Added 11/28
    }
}

# Supplier relationship terms
supplier_relship_category_to_term_mapping_SIMPLE = {
    'Core': ['supplier', 'sourcing', 'manufactur', 'factory', 'mining', 'raw material', 'workshop', 'warehouse']
}

supplier_relship_category_to_term_mapping_COMPLEX = {
    'Core': {'sweatshop': attach_regex_to_beginning_of_terms(['sweatshop', 'sweat factory'])}
}

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
                                                                        'weather strike', 'bridge strike',
                                                                        'joint strike fighter']

# reimbursement
risk_terms_regex_dict['Financial-Loss']['reimburse']['extra_cleaning'] = True
risk_terms_regex_dict['Financial-Loss']['reimburse']['terms_to_remove'] = ['tuition reimbursement']
risk_terms_regex_dict['Remedy']['reimburse']['extra_cleaning'] = True
risk_terms_regex_dict['Remedy']['reimburse']['terms_to_remove'] = ['tuition reimbursement']

# block import
risk_terms_regex_dict['Operational-Costs']['block import']['extra_cleaning'] = True
risk_terms_regex_dict['Operational-Costs']['block import']['terms_to_remove'] = ['import bank']

# court
risk_terms_regex_dict['Legal-Risk']['court']['extra_cleaning'] = True
risk_terms_regex_dict['Legal-Risk']['court']['terms_to_remove'] = ['courtyard']

# pricing pressure
practice_terms_regex_dict['Negative-Practices']['pricing pressure']['context_words'] = ['supplier', 'factory',
                                                                                        'manufactur', 'warehouse',
                                                                                        'workshop']
# contract
# practice_terms_regex_dict['Good-Practices']['contract']['context_words'] = ['supplier']

# all supplier context words:
relationship_words = ['relationship', 'purchaser', 'order', 'lead time',
                      'cancel([l]?(ed)|([l]?ing))? order', 'cancellation',
                      'buyer', 'outsourc', 'subcontract']
for core_term in supplier_relship_category_to_term_mapping_SIMPLE['Core']:
    supplier_relship_regex_dict['Core'][core_term]['context_words'] = relationship_words
for core_term in supplier_relship_category_to_term_mapping_COMPLEX['Core']:
    supplier_relship_regex_dict['Core'][core_term]['context_words'] = relationship_words
