import mysql.connector

try:
    cnx = mysql.connector.connect(user='root',host='127.0.0.1',database='gmail')
    cursor=cnx.cursor()
    cursor.execute("SHOW DATABASES")
    for table_name in cursor:
         print(table_name)
    cnx.close()
except:
    print("didnt connect")
