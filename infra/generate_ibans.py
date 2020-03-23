import json, sys
import datetime, time, random
from itertools import chain

from utils import generate_ibans

countries = ['HU', 'GB', 'GB', 'GB', 'NL', 'NL', 'AT', 'DE', 'DE', 'DE', 'RO', 'BG', 'SE']

ibans_eu = generate_ibans(78, countries)
ibans_us = generate_ibans(10*1000*1000-78, ['US'], reset_seed=False)

rows = chain(
    map(lambda iban: '{{"iban": "{}", "european": true, "country": "{}"}}'.format(iban, iban[0:2]), ibans_eu),
    map(lambda iban: '{{"iban": "{}", "european": true, "country": "{}"}}'.format(iban, iban[0:2]), ibans_us))

for r in rows:
    print(r)