# Umag Efficient Cost Estimation

Detailed information about the case can be read here:
https://github.com/khangroupkz/HackNU

## Expected performance

> We expect average performance to be as θ(n+m), where n is number of supplies and m is number of sales for a given period. A formal proof can be attached later on.

## Repository structure

* server.py – Contains Flask web application along with our algorith for efficient cost estimation

* database.py – We modified database a little bit, so at first you need to run this file (simply by calling in terminal 'python database.py'). In order to code work, you also need to place .sql scripts from this repository (we modified them also).

### Important functions
* get_net_profit(barcode, start_time, end_time) - считает net-profit за период
* calculate_margin(sales, supply) – пересчитывают маржу

## Innitial settings

Requirements = flask, flask_restful, numpy

## Пример вывода одной записи из sales/supply
```
    http://127.0.0.1:5000/api/sales/18
```

## Пример вывода списка записей за период из sales/supply
```
    http://127.0.0.1:5000/api/sales/18](http://127.0.0.1:5000/api/sales?barcode=4870204391510&fromTime=2022-10-25%2016%3A39%3A22&toTime=2022-10-25%2016%3A39%3A22)
```

## Пример создания report за период
```
http://127.0.0.1:5000/api/reports?barcode=4680036912629&fromTime=2022-01-01%2009%3A35%3A31&toTime=2022-10-25%2016%3A39%3A22
```

## Пример добавления записи в sales/supply
```
import json 
import requests

values = {
    "barcode": 4870204391510,
    "price": 100,
    "quantity": 1,
    "saleTime": "2022-12-28 11:00:02"
  }

headers = {
  'Content-Type': 'application/json'
}

response = requests.post('http://127.0.0.1:5000/api/sales', headers=headers, json=values)
```

## Пример удаления записи из sales/supply
```
response = requests.delete('http://127.0.0.1:5000/api/sales/4870204391510')
```

## Пример обновления записи из sales/supply
```
values = {
    "barcode": 4870204391510,
    "price": 150,
    "quantity": 20,
    "saleTime": "2022-12-28 11:00:02"
  }

headers = {
  'Content-Type': 'application/json'
}

response = requests.('http://127.0.0.1:5000/api/sales/4870204391510', headers=headers, json=values)
```
