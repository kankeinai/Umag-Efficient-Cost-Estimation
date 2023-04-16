import sqlite3

mydb = sqlite3.connect("umag_hacknu.db")
mycursor = mydb.cursor()

with open('create_tables.sql', 'r') as sql_file:
    sql_script = sql_file.read()

mycursor.executescript(sql_script)
mydb.commit()

with open('insert_sales.sql', 'r') as sql_file:
    sql_script = sql_file.read()

mycursor.executescript(sql_script)
mydb.commit()

with open('insert_supplies.sql', 'r') as sql_file:
    sql_script = sql_file.read()

mycursor.executescript(sql_script)
mydb.commit()

mydb.close()