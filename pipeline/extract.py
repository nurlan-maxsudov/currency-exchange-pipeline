import requests

def fetch_rates(base_currency='USD', target_currencies= ['EUR', 'RUB', 'UZS', 'GBP'], date=None):
    url = 'https://api.frankfurter.dev/v2/rates'

    params = {
        "base": base_currency,
        "quotes": ",".join(target_currencies)
    }
    if date:
        params['date'] = date

    response = requests.get(url=url, params=params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    latest = fetch_rates()
    print(latest)

    historical = fetch_rates(date='2026-01-16')
    print(f"Historical, {historical}")