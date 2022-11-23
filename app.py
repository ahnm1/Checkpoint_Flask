from flask import Flask, render_template, request
from datetime import datetime
import psycopg2

def db_connection():
    conn = psycopg2.connect(   
        host     = "localhost",
        port     = "5432",
        database = "phonedb",
        user     = "postgres",
        password = "********"
    )
    return conn

def read_phonelist():
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonelist;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def read_phone(name):
    conn = db_connection()
    cur = conn.cursor()
    print(f"SELECT phone FROM phonelist WHERE name = '{name}';")
    cur.execute(f"SELECT phone FROM phonelist WHERE name = '{name}';")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def read_name(phone):
    conn = db_connection()
    cur = conn.cursor()
    print(f"SELECT phone FROM phonelist WHERE phone = '{phone}';")
    cur.execute(f"SELECT name FROM phonelist WHERE phone = '{phone}';")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def add_phone(name, phone):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO phonelist VALUES ('{name}', '{phone}');")
    cur.execute("COMMIT;")
    cur.close()
    conn.close()

def delete_phone(name):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM phonelist WHERE name = '{name}';")
    cur.execute("COMMIT;")
    cur.close()
    conn.close()

app = Flask(__name__)

@app.route("/")
def start():
    now   = datetime.now()
    today = [str(now.year%100), str(now.month), str(now.day)]
    if len(today[1])<2:
        today[1] = '0'+today[1]
    if len(today[2])<2:
        today[2] = '0'+today[2]
    result = read_phonelist()
    return render_template('list.html', list=result, date=today)

@app.route("/delete")
def delete_func():
    name=request.args['name']

    # Check if name exists
    for contact in read_phonelist():
        if name in contact:
            delete_phone(name)
            contact_name = f"Deleted {name}"
            
        else:
            contact_name = f"{name} not found"

    return render_template('delete.html', name=contact_name)
    
@app.route("/insert")
def insert_func():
    name  = request.args['name']
    phone = request.args['phone']
    add_phone(name, phone)
    return render_template('insert.html', name = name, phone = phone)

@app.route("/api")
def api_func():
    args=request.args
   
    action = args.get('action', default="Bad action", type=str)
    if action == "Bad action":
        return render_template('api_usage.html', action = action)
    
    if action == 'phone': # Search with name
        name = args.get('name', default = "No name", type = str)
        if name == "No name":
            return render_template('api_usage.html', action = action)

        phone = read_phone(name)
        if len(phone) < 1:
            return f"not found {name}"
    
        return phone[0][0]
    
    elif action == "name": # Search with phone
        phone = args.get('phone', default = "No name", type = str)
        if phone == "No name":
            return render_template('api_usage.html', action=action)

        name = read_name(phone)
        if len(name) < 1:
            return f"not found {phone}"
    
        return name[0][0]

    else:
        return f"Unknown action: '{action}'"


