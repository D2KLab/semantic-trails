import csv
import requests

categories = {}


def navigate_cat(root):
    index = root['id']
    name = root['name']

    try:
        categories[index].append(name)
    except KeyError:
        categories[index] = [name]

    for child in root['categories']:
        navigate_cat(child)


url = 'https://api.foursquare.com/v2/venues/categories'

params = dict(
    v='20170211',
    oauth_token='QEJ4AQPTMMNB413HGNZ5YDMJSHTOHZHMLZCAQCCLXIX41OMP',
    includeSupportedCC=True
)

languages = ['en-US', 'fr-FR', 'it-IT']

for language in languages:
    headers = {"Accept-Language": language}

    resp = requests.get(url=url, params=params, headers=headers)
    data = resp.json()

    for root_cat in data['response']['categories']:
        navigate_cat(root_cat)

with open('categories.csv', 'w', encoding='utf-8', newline='') as fp:
    writer = csv.writer(fp)

    for index in categories:
        writer.writerow([index] + categories[index])
