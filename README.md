# Semantic Trails Datasets

This repository contains the code used to generate the Semantic Trails Datasets (STDs).
You can download the actual datasets from [figshare](https://figshare.com/s/545ff3de8027b1639757).

## Cities

We first downloaded from [Wikidata](https://www.wikidata.org) the URIs of all the cities and the associated Countries available on [GeoNames](https://www.geonames.org), as well as their population, if available.
To this purpose, we exploited the `download_cities.py` script.
The input file `cities500.txt` can be obtained [here](http://download.geonames.org/export/dump/), while the output files `cities.csv` and `population.csv` are already available in the repository.
The format of `cities.csv` is the one required by the library [reverse_geocoder](https://github.com/thampiman/reverse-geocoder).

## Mapping

We mapped the categories of the [Foursquare taxonomy](https://developer.foursquare.com/docs/resources/categories) with the [Schema.org](https://schema.org) vocabulary.
The script `download_categories.py` was used to obtain such categories.
The result of the mapping process is available in the `mapping.csv` file.
The first column represents the Foursquare category, while the second one the corresponding URI.

## Datasets

We constructed the STDs by the means of the `create_std.py` script.
It requires two input files, `checkins.csv` and `venues.csv` in the same format of the [Global-Scale Check-in Dataset](https://sites.google.com/site/yangdingqi/home/foursquare-dataset).
The resulting datasets are available on [figshare](https://figshare.com/s/545ff3de8027b1639757), together with a description of the output format.

## Team

- Diego Monti <diego.monti@polito.it>
- Enrico Palumbo <palumbo@ismb.it>
- Giuseppe Rizzo <giuseppe.rizzo@ismb.it>
- Raphaël Troncy <troncy@eurecom.fr>
- Maurizio Morisio <maurizio.morisio@polito.it>