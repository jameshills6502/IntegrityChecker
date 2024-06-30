import sys
import hashlib
import pandas
import sqlite3
import mysql.connector
import datetime 
import time 

buffer_size = 65536 #runs better with a buffer

md5 = hashlib.md5()
sha1 = hashlib.sha1()



mydb = mysql.connector.connect(host ="localhost", db ="hashtable", user="app", password="ForensicApp@018")
mycursor = mydb.cursor()



def file_name():
    user_input = input("Please input filename:")
    logic(user_input)
def logic(filename):
    print(filename)
    try:
        f = open(filename, "rb")
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
            searching(filename, md5.hexdigest(), sha1.hexdigest())
    except FileNotFoundError:
        print("File not found!")
    
def storing(filename, md5hash, sha1hash):
    sql = "INSERT INTO forensic_app(`date_of_scan`, `file_name`, `md5_sum`, `sha1_sum`) VALUES(%s, %s, %s, %s);"
    date_of_scan = datetime.datetime.now()
    val = (date_of_scan, filename, md5hash, sha1hash)
    mycursor.execute(sql, val)
    mydb.commit()

def searching(filename, md5_hash, sha1_hash):
    print("Checking database...")
    hashes = str(md5_hash)
    sql = "SELECT * FROM forensic_app WHERE md5_sum = %s;"
    val = (hashes, )
    mycursor.execute(sql, val)
    data = mycursor.fetchall()
    
    if data == None:
        print("File not found in database, adding")
        storing(filename, md5_hash, sha1_hash)
        #stores the file and its data
    else:
        print("File exists in database!")
        print()
    

file_name()


