test_date_range = {
    'start_date': '2025-01-01',
    'end_date': '2025-01-31',
}

test_zone = {
    'center': {
        'latitude': 32.7157,
        'longitude': 117.1611,
    },
    'radius_min': 0.0,
    'radius_max': 10.0,
}

test_location = {
    'state': 'CA',
    'county': 'San Diego',
    'zone': test_zone,
}

test_job = {
    'classification': 'Welder',
    'subclassification': 'Plumber',
}

test_wage = {
    'currency': 'USD',
    'rate': '123.45',
    'fringe': {
        'fixed': '12.34',
        'percentage': '0.123',
        'holidays': [
            'New Year\'s Day',
            'Memorial Day',
            'Independence Day',
            'Labor Day',
            'Veterans Day',
            'Thanksgiving Day',
            'Day After Thanksgiving',
            'Christmas Day',
        ],
    },
}

test_wage_determination = {
    'decision_number': 'CA00000001',
    'modification_number': 0,
    'publication_date': '2025-01-01',
    'effective': test_date_range,
    'active': True,
    'location': test_location,
    'construction_type': 'building',
    'rate_identifier': 'SUCA2025-100',
    'survey_date': '2024-01-01',
    'job': test_job,
    'wage': test_wage,
    'notes': 'Extra context goes here',
}

bad_decision_numbers = (
    '0CA000001',
    '0CA0000001',
    '0CA00000001',
    'CA0000001',
    'CA000000001',
    'C00000001',
    'C000000001',
    'C0000000001',
    'CAA000001',
    'CAA0000001',
    'CAA00000001',
    0,
    10000000,
    None,
)

bad_modification_numbers = (-1, 1.1, None)

test_wage_determination_tuple = (
    'CA00000001',
    '0',
    '2025-01-01',
    '2025-01-01',
    '2025-01-31',
    'True',
    'building',
    'CA',
    'San Diego',
    '32.7157',
    '117.1611',
    '0.0',
    '10.0',
    '2024-01-01',
    'Welder',
    'Plumber',
    'USD',
    '123.45',
    '12.34',
    '0.123',
    '''['Christmas Day', 'Day After Thanksgiving', 'Independence Day', 'Labor Day', '''
    ''''Memorial Day', "New Year's Day", 'Thanksgiving Day', 'Veterans Day']''',
    'Extra context goes here',
)
