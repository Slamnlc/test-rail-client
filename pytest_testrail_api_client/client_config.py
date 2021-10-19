TR_PREFIX = '@C'
SECTIONS_SEPARATOR = ' - '

PRIORITY_REPLACE = {
    'Critical': ['regression'],
    'High': ['sanity'],
    'Medium': ['smoke'],
    'Low': []
}

REPLACE_TAGS = {
    'to be automated': 'to_automate',
}


# ------Validate features--------

VALIDATE_FEATURES = True
NO_TAG_IN_FEATURE_HEADER = True
ONE_OF_TAGS = [
    ['@to_automate', '@automated', '@manual'],
    ['@smoke', '@critical', '@regression']
]
AT_LEAST_ONE = [
    ['@phone', '@tablet']
]
