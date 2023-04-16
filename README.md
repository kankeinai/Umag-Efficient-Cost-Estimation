# Umag Efficient Cost Estimation

Requirements = flask, flask_restful, numpy

## Пример создания report
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
