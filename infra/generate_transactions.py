import json, sys
import datetime, time, random

from utils import generate_ibans

countries = ['HU', 'GB', 'GB', 'GB', 'NL', 'NL', 'AT', 'DE', 'DE', 'DE', 'RO', 'BG', 'SE']
alpha3 = {
    'HU': 'HUN',
    'GB': 'GBR',
    'NL': 'NLD',
    'AT': 'AUT',
    'DE': 'DEU',
    'RO': 'ROU',
    'BG': 'BGR',
    'SE': 'SWE'
}

ibans = list(generate_ibans(5000, countries))

random.seed(273)

start_time = datetime.datetime.now()
while True:
    event_time = datetime.datetime.now()
    delta_sec = random.gauss(0, 5)
    if delta_sec > 20:
        continue
    if random.randint(0,9) == 0 and event_time - datetime.timedelta(seconds=20) > start_time:
        delta_sec = delta_sec / 4 - 60
    event_time = event_time + datetime.timedelta(seconds=delta_sec - 10)

    from_iban = ibans[random.randint(0, len(ibans) - 1)]
    from_iban_country = from_iban[0:2]
    if random.randint(0, 100) == 0:
        from_country = countries[random.randint(0, len(countries) - 1)]
    else:
        from_country = from_iban_country

    while True:
        to_iban = ibans[random.randint(0, len(ibans) - 1)]
        to_iban_country = to_iban[0:2]
        if to_iban_country != from_iban_country:
            if random.randint(0,20) == 0:
                break
            else:
                continue
        break

    t = {
        'event_time': event_time.isoformat(),
        'iban_from': from_iban,
        'iban_to': to_iban,
        'country': from_country,
        'country_alpha': alpha3[from_country], 
        'amount_eur': random.randint(10, 100000)
    }

    print(json.dumps(t))
    time.sleep(0.05)
