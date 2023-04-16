from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import pandas as pd
import numpy as np
from ast import literal_eval
import sqlite3
from datetime import datetime, timedelta
import json 


DATABASE = 'umag_hacknu.db'

app = Flask(__name__)
api = Api(app)

mydb = sqlite3.connect(DATABASE, check_same_thread=False)
mycursor = mydb.cursor()

def get_net_profit(barcode, start_time, end_time):

    mycursor.execute(f"Select price, quantity, margin from sale where barcode='{barcode}' and sale_time BETWEEN '{start_time}' and '{end_time}'")
    sales = mycursor.fetchall()

    if sales:
        sales = np.array(sales).T
        revenue = int(np.dot(sales[0], sales[1]))
        profit = int(np.sum(sales[2]))
        quantity = int(np.sum(sales[1]))

        return revenue, quantity, profit

def calculate_margin(sales, supply):

    sales = np.array(sales)
    supply = np.array(supply)

    time_sales = np.array([datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in sales.T[:][2]])
    time_supply = np.array([datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in supply.T[:][2]])

    time_array = np.arange(np.min(time_sales), np.max(time_sales) + timedelta(days = 1), timedelta(days = 1))

    supply_queue = list(supply[time_supply.argsort()].copy())

    margins = []
    transfer = []

    for j in range(len(time_array)-1):
    # find all sales for the time period
        sales_for_time_period = sales[((time_sales >= time_array[j]) & (time_sales <= time_array[j+1]))]

        if len(transfer):
            sales_for_time_period = np.vstack((sales_for_time_period, transfer))

        # if no entries, nothing to do
        if sales_for_time_period.shape[0]:

        # count inventory change:
            qty_sold = np.sum(np.array(sales_for_time_period[:, 0], dtype=int))

            if qty_sold <= int(supply_queue[0][0]):

                transfer = []
               

                # find the margin for each sale
                for sale in np.array(sales_for_time_period.T[[0,1,-1]].T, dtype=int):

                    quantity, price, id = sale
                    supply_queue[0][0] = int(supply_queue[0][0]) - quantity
                    margins.append([quantity*price - quantity*int(supply_queue[0][1]), id])

            #Case 2: inventory change does not fit into the current supply
            else:
                temp = np.array([datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in sales_for_time_period[:, 2]]).argsort()
                sorted_vals = sales_for_time_period[temp]
                i = 0

                while sorted_vals[i][0] < supply_queue[0][0]:

                    supply_queue[0][0] = int(supply_queue[0][0]) - int(sorted_vals[i][0])
                    margins.append([int(sorted_vals[i][0])*int(sorted_vals[i][1]) - int(sorted_vals[i][0])*int(supply_queue[0][1]), int(sorted_vals[i][-1])])
                    i += 1

                current_supply = supply_queue.pop(0)

                margins.append([int(current_supply[0])*int(sorted_vals[i][1]) - int(current_supply[0])*int(current_supply[1]), int(sorted_vals[i][-1])])
                sorted_vals[i][0] = int(sorted_vals[i][0]) - int(current_supply[0])
                
                margins[-1][0] += int(sorted_vals[i][0])*int(sorted_vals[i][1]) - int(sorted_vals[i][0])*int(current_supply[1])

                if len(supply_queue):
                    supply_queue[0][0] = int(supply_queue[0][0]) - int(sorted_vals[i][0])
                    i+=1
                    transfer = sorted_vals[i:]
                else:
                    break
    
    for m in margins:
        value, id = m
        mycursor.execute(f"UPDATE sale SET margin='{value}' where id ='{id}'")
        mydb.commit()

    

@app.route("/api/sales")
def get_sales_list():

    barcode = int(request.args.get('barcode', type=str))
    start_time = request.args.get('fromTime', type=str)
    end_time = request.args.get('toTime', type=str)

    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time, '%Y-%m-%d  %H:%M:%S')

    mycursor.execute(f"Select id, barcode, price, quantity, sale_time from sale where barcode='{barcode}' and sale_time BETWEEN '{start_time}' and '{end_time}' ")
    result = mycursor.fetchall()

    if result:
        keys  = ['id', 'barcode', 'price', 'quantity','saleTime']

        return  json.dumps([dict(zip(keys, row)) for row in result], indent=4)
    else:

        return '', 404

@app.route("/api/sales/<id>")
def get_sale(id):
    id = int(id)
    mycursor.execute(f"Select id, barcode, price, quantity, sale_time from sale where id='{id}'")
    result = mycursor.fetchone()

    if result:

        keys  = ['id', 'barcode', 'price', 'quantity','saleTime']

        if result:
            result = list(result)
            return json.dumps(dict(zip(keys, result)), indent=4)
    else:

        return '', 404


@app.route("/api/sales", methods=['POST'])
def create_sale():

    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):

        data = literal_eval(request.data.decode('utf-8'))

        if data:
            mycursor.execute(f"INSERT INTO sale(barcode, quantity, price, sale_time) VALUES('{data['barcode']}', '{data['price']}', '{data['quantity']}', '{data['saleTime']}')")
            mydb.commit()

            mycursor.execute(f"Select quantity, price, sale_time, id from sale where barcode='{data['barcode']}'")
            sales = mycursor.fetchall()

            mycursor.execute(f"Select quantity, price, supply_time, id from supply where barcode = '{data['barcode']}'")
            supply = mycursor.fetchall()

            calculate_margin(sales, supply)

            return json.dumps({'id':mycursor.lastrowid}, indent=4)

@app.route("/api/sales/<id>", methods=['PUT'])
def update_sale(id):

    id = int(id)

    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):

        print(request.data)

        data = literal_eval(request.data.decode('utf-8'))
        if data:

            mycursor.execute(f"Select * from sale where id='{id}'")
            result = mycursor.fetchone()

            if result:

                mycursor.execute(f"UPDATE sale SET barcode='{data['barcode']}', quantity='{data['quantity']}', price='{data['price']}', sale_time='{data['saleTime']}' where id='{id}'")
                mydb.commit()

                mycursor.execute(f"Select quantity, price, sale_time, id from sale where barcode='{data['barcode']}'")
                sales = mycursor.fetchall()

                mycursor.execute(f"Select quantity, price, supply_time, id from supply where barcode = '{data['barcode']}'")
                supply = mycursor.fetchall()

                calculate_margin(sales, supply)

    return '', 204

@app.route("/api/sales/<id>", methods=['DELETE'])
def delete_sale(id):

    id = int(id)

    mycursor.execute(f"Select barcode from sale where id='{id}'")
    result = mycursor.fetchone()


    if result:

        barcode = result[0]

        mycursor.execute(f"Delete from sale where id='{id}'")
        mydb.commit()

        mycursor.execute(f"Select quantity, price, sale_time, id from sale where barcode='{barcode}'")
        sales = mycursor.fetchall()

        mycursor.execute(f"Select quantity, price, supply_time, id from supply where barcode = '{barcode}'")
        supply = mycursor.fetchall()

        calculate_margin(sales, supply)

    return '', 204


@app.route("/api/supplies")
def get_supply_list():

    barcode = request.args.get('barcode', type=str)
    start_time = request.args.get('fromTime', type=str)
    end_time = request.args.get('toTime', type=str)

    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time, '%Y-%m-%d  %H:%M:%S')
    
    mycursor.execute(f"Select id, barcode, price, quantity, supply_time from supply where barcode='{barcode}' and supply_time BETWEEN '{start_time}' and '{end_time}' ")
    result = mycursor.fetchall()

    if result:
        keys  = ['id', 'barcode', 'price', 'quantity','supplyTime']

        return  json.dumps([dict(zip(keys, row)) for row in result], indent=4)
    else:

        return '', 404

@app.route("/api/supplies/<id>")
def get_supply(id):
    id = int(id)
    mycursor.execute(f"Select id, barcode, price, quantity, supply_time from supply where id='{id}'")
    result = mycursor.fetchone()

    if result:

        keys  = ['id', 'barcode', 'price', 'quantity','supplyTime']

        if result:
            result = list(result)
            
            return json.dumps(dict(zip(keys, result)), indent=4)
    else:

        return '', 404


@app.route("/api/supplies", methods=['POST'])
def create_supply():

    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):

        data = literal_eval(request.data.decode('utf-8'))

        if data:
            mycursor.execute(f"INSERT INTO supply(barcode, quantity, price, supply_time) VALUES('{data['barcode']}', '{data['price']}', '{data['quantity']}', '{data['supplyTime']}')")
            mydb.commit()

            
            mycursor.execute(f"Select quantity, price, sale_time, id from sale where barcode='{data['barcode']}'")
            sales = mycursor.fetchall()

            mycursor.execute(f"Select quantity, price, supply_time, id from supply where barcode = '{data['barcode']}'")
            supply = mycursor.fetchall()
            
            calculate_margin(sales, supply)


            return json.dumps({'id':mycursor.lastrowid}, indent=4)

@app.route("/api/supplies/<id>", methods=['PUT'])
def update_supply(id):

    id = int(id)

    content_type = request.headers.get('Content-Type')

    if (content_type == 'application/json'):
        
        data = literal_eval(request.data.decode('utf-8'))
        if data:

            mycursor.execute(f"Select * from supply where id='{id}'")
            result = mycursor.fetchone()

            if result:

                mycursor.execute(f"UPDATE supply SET barcode='{data['barcode']}', quantity='{data['quantity']}', price='{data['price']}', supply_time='{data['supplyTime']}' where id='{id}'")
                mydb.commit()

                mycursor.execute(f"Select quantity, price, sale_time, id from sale where barcode='{data['barcode']}'")
                sales = mycursor.fetchall()

                mycursor.execute(f"Select quantity, price, supply_time, id from supply where barcode = '{data['barcode']}'")
                supply = mycursor.fetchall()
                calculate_margin(sales, supply)

    return '', 204

@app.route("/api/supplies/<id>", methods=['DELETE'])
def delete_supply(id):

    id = int(id)

    mycursor.execute(f"Select barcode from supply where id='{id}'")
    result = mycursor.fetchone()

    if result:

        barcode = result[0]

        mycursor.execute(f"Delete from supply where id='{id}'")
        mydb.commit()

        mycursor.execute(f"Select quantity, price, sale_time, id from sale where barcode='{barcode}'")
        sales = mycursor.fetchall()

        mycursor.execute(f"Select quantity, price, supply_time, id from supply where barcode = '{barcode}'")
        supply = mycursor.fetchall()


        calculate_margin(sales, supply)

    return '', 204

@app.route("/api/reports")
def get_report():

    barcode = int(request.args.get('barcode', type=str))
    start_time = request.args.get('fromTime', type=str)
    end_time = request.args.get('toTime', type=str)

    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time, '%Y-%m-%d  %H:%M:%S')

    mycursor.execute(f"Select margin from sale where barcode='{barcode}'")
    sales = mycursor.fetchall()

    if sales:
        sales = np.array(sales)
        if np.sum(sales[:,-1]) == 0:

            mycursor.execute(f"Select quantity, price, sale_time, id from sale where barcode='{barcode}'")
            sales = mycursor.fetchall()

            mycursor.execute(f"Select quantity, price, supply_time, id from supply where barcode = '{barcode}'")
            supply = mycursor.fetchall()

            calculate_margin(sales, supply)

        revenue, quantity, netprofit = get_net_profit(barcode, start_time, end_time)
        return  json.dumps({'barcode':barcode, 'revenue': revenue, 'quantity':quantity, 'netProfit':netprofit})
    
    else:

        return '', 404

   
    

if __name__ == '__main__':
    app.run()  # run our Flask app
