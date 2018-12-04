import requests


def print_cat(root):
    print(root['name'])

    for child in root['categories']:
        print_cat(child)


url = 'https://api.foursquare.com/v2/venues/categories'

params = dict(
    v='20170211',
    oauth_token='QEJ4AQPTMMNB413HGNZ5YDMJSHTOHZHMLZCAQCCLXIX41OMP',
    includeSupportedCC=True
)

resp = requests.get(url=url, params=params)
data = resp.json()

for root_cat in data['response']['categories']:
    print_cat(root_cat)
