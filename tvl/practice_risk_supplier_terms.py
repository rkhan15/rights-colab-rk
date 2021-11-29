# SUPPLY CHAIN MGMT-RELATED TERMS ONLY

START_REGEX = '(?<![^ .,?!;])'


def attach_regex_to_beginning_of_terms(terms_lst, regex=START_REGEX):
    if regex == '(?<![^ .,?!;])':
        return [regex + term for term in terms_lst]


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
                 'investment',
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
    'Other': {},
    'Other-RK': {'negative return': attach_regex_to_beginning_of_terms(['negative(.*)return'])}
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
                       'training',  # Added 11/28
                       'contract',  # Added 11/28
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
                        'turnover': attach_regex_to_beginning_of_terms(
                            ['high turnover', 'worker turnover', 'employee turnover', 'turnover rate']),
                        'unsafe conditions': attach_regex_to_beginning_of_terms(
                            ['unsafe(.*)condition', 'hazard(.*)condition', 'working conditions',
                             'deteriorating(.*)condition']),
                        'grievance mechanism': attach_regex_to_beginning_of_terms(
                            ['grievance mechanism', 'grievance system'])},
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
