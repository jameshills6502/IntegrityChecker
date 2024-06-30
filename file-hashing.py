import sys
import hashlib
import mysql.connector
from mysql.connector import errorcode
import datetime 
import ttkbootstrap as ttk 


buffer_size = 65536 #runs better with a buffer

md5 = hashlib.md5()
sha1 = hashlib.sha1()

def initial_setup():
    global mycursor
    global mydb
    # not defining these across the program
    try:
        mydb = mysql.connector.connect(host ="localhost", db ="hashtable", user="app", password="ForensicApp@018")
        ## HOW CAN I MAKE THIS MORE SECURE?
        mycursor = mydb.cursor()
        window_create()
    except mysql.connector.Error:
        print("Error! Database not found! \nExiting program")
        quit()
    
#### CREATE STARTING WINDOW ####
def window_create():
    app = ttk.Window(themename="solar")
    app.geometry("800x300")
    label = ttk.Label(app, text="FILE INTEGRITY CHECKER")
    entry1label = ttk.Label(app, text="Enter your username:")
    entry2label = ttk.Label(app, text="Enter your password:")
    entry1label.grid(row=1, column=0, pady=2)
    entry2label.grid(row=2, column=0, pady=2)
    username_entry = ttk.Entry(app)
    password_entry = ttk.Entry(app, show="*")
    login_error = ttk.Label(app, text="Error!\nPassword or username is incorrect")
    submit_button = ttk.Button(app, text="Submit", command= lambda: login(username_entry, password_entry, login_error))
    account_button = ttk.Button(app, text="Create account", command= create_account_page)
    quit_button = ttk.Button(app, text="Quit", command= lambda: destroy(app))
    label.grid(row=0, column = 1, pady = 1)
    username_entry.grid(row=1, column=1,pady=1)
    password_entry.grid(row=2, column=1,pady=1)
    quit_button.grid(row=3, column = 2, pady =2)
    submit_button.grid(row=3, column =1, pady= 1)
    account_button.grid(row=3, column =0, pady=1)
    app.mainloop()

def destroy(app):
    app.destroy()



#### TTK CODE FOR CREATE ACCOUNT PAGE ####
def create_account_page():
    top = ttk.window.Toplevel()
    top.title('Create Account')
    top.grab_set()
    l1 = ttk.Label(top, text="Enter Username:")
    l4 = ttk.Label(top, text="Enter Password:")
    l5 = ttk.Label(top, text="Confirm Password:")
    username = ttk.Entry(top, width=50)
    password = ttk.Entry(top, width=50, show="*")
    confirm_password = ttk.Entry(top, width=50, show="*")
    error = ttk.Label(top, text="Passwords don't match!")
    success = ttk.Label(top, text="Account Created!")
    submit = ttk.Button(top, text="Create Account", command= lambda: store_account(username, password, confirm_password, error, success))
    l1.grid(row=0,column=0, pady=2)
    l4.grid(row=1, column=0, pady=2)
    l5.grid(row=2, column=0, pady=2)
    username.grid(row=0, column=1, pady=2)
    password.grid(row=1, column=1, pady=2)
    confirm_password.grid(row=2, column=1, pady=2)
    submit.grid(row=3, column=1, pady=1)


#### SEARCHING FOR USERNAME PRESENCE BEFORE ADDING TO DATABASE, STORING USER_ID FOR LATER USE ####
def search_acc(username):
    sql = "SELECT user_id FROM user_accounts WHERE username = %s"
    user = (username, )
    mycursor.execute(sql, user)
    data = mycursor.fetchall()
    if len(data) == 0:
        return None
    else:
        return data
        ## USE THIS FOR LATER!

#### LOGIN FUNCTION ####
def login(username_entry, password_entry, error):
    username = username_entry.get()
    password = password_entry.get()
    sql = "SELECT * FROM user_accounts WHERE username = %s AND password = %s;"
    val = (username, password)
    mycursor.execute(sql, val)
    data = mycursor.fetchall()
    if len(data) == 0:
        error.grid(row=4, column=1, pady=1)
    else:
        user_id = data[0][0] #first column
        home_page(user_id)

#### STORE USER ACCOUNT FUNCTION ####
def store_account(username_entry, password_entry, confirm_password_entry, error, success):
    username = username_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()
    if password == confirm_password:
        does_account_exist = search_acc(username)
        if does_account_exist == None:
            sql = "INSERT INTO user_accounts(`username`, `password`) VALUES(%s, %s);"
            val = (username, password)
            mycursor.execute(sql, val)
            mydb.commit()
            success.grid(row=4,column=1, pady=1)
        else:
            print(does_account_exist)
            for i in does_account_exist:
                print(i)
    else:
        error.grid(row=4, column=1, pady=1)

#### STORE FILE HASHES FUNCTION ####
def store_file_data(filename, md5hash, sha1hash, user_id):
    sql = "INSERT INTO forensic_app(`date_of_scan`, `file_name`, `md5_sum`, `sha1_sum`, `user_id`) VALUES(%s, %s, %s, %s, %s);"
    date_of_scan = datetime.datetime.now()
    val = (date_of_scan, filename, md5hash, sha1hash, user_id)
    mycursor.execute(sql, val)
    mydb.commit()

#### SEARCHING ####
def searching(filename, md5_hash, sha1_hash, user_id):
    print("Checking database...")
    hashes = str(md5_hash)
    sql = "SELECT * FROM forensic_app WHERE md5_sum = %s;"
    val = (hashes, )
    mycursor.execute(sql, val)
    data = mycursor.fetchall()
    if len(data) == 0:
        print("File not found in database, adding")
        store_file_data(filename, md5_hash, sha1_hash, user_id)
        #stores the file and its data
    else:
        print("File exists in database!")
        print(data)
#### FILE HANDLING AND HASHING ####
def logic(filename_entry, user_id):
    filename = filename_entry.get()
    try:
        f = open(filename, "rb")
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
            searching(filename, md5.hexdigest(), sha1.hexdigest(), user_id)
    except FileNotFoundError:
        print("File not found!")
#### MAIN PAGE ####
def home_page(user_id):
    top = ttk.window.Toplevel()
    top.title('File Integrity Checker')
    top.grab_set()
    l1 = ttk.Label(top, text="Enter Filename:")
    submit = ttk.Button(top, text="Submit", command= lambda: logic(filename, user_id))
    show_list = ttk.Button(top, text="Show List", command= lambda: show_hash_list(user_id, top))
    ## ENTER FILE PATH WOULD BE BEST
    filename = ttk.Entry(top, width=50)
    l1.grid(row=0,column=0, pady=2)
    filename.grid(row=0, column=1, pady=1)
    submit.grid(row=0, column=2, pady=1)
    show_list.grid(row=1, column=1, pady=1)


def show_hash_list(user_id, top):
    sql = "SELECT * FROM forensic_app WHERE user_id = %i;"
    val = (user_id, )
    mycursor.execute(sql, val)
    data = mycursor.fetchall()
    l1 = ttk.Label(top, text="Stored file hashes:")
    l1.grid(row=0, column=0, pady=1)
    for x in data:
        loop = 4
        print(x)
        ## THIS NEEDS FIXING, OUTPUT CONTENTS OF DATABASE ##
        file_name_label = ttk.Label(top, text="D")
        sha1_sum_label = ttk.Label(top, text="D")
        md5_sum_label = ttk.Label(top, text="D")
        md5_sum_label.grid(row=loop, column=1, pady=1)
        sha1_sum_label.grid(row=loop, column=2, pady=2)
        file_name_label.grid(row=loop, column=0, pady=1)
        loop += 1
        
initial_setup()


