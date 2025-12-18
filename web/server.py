from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

def configure_db() -> None:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS temperature "+
                   "(id num, temperature num, pressure num, humidity num, rain num, day num, month num, year num, hour num, minute num)")
    connection.commit()
    connection.close()

def get_index() -> int:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    num = cursor.execute('SELECT id FROM temperature ORDER BY id DESC').fetchone()
    connection.commit()
    connection.close()
    if num is None:
        return 0
    return int(num[0])+1

def save_to_db(temperature, pressure, humidity, rain) -> None:
    num = get_index()
    time = datetime.now() #.strftime('%d.%m.%Y %H:%M')
    print(time)
    day, month, year = time.strftime("%d"), time.strftime("%m"), time.strftime("%Y")
    hour, minute = time.strftime("%H"), time.strftime("%M")
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO temperature VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (num, temperature, pressure, humidity, rain, day, month, year, hour, minute))
    connection.commit()
    connection.close()

def get_db() -> dict:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    data = cursor.execute('SELECT * FROM temperature ORDER BY id DESC').fetchone()
    connection.close()
    return data

@app.route('/')
def index():
    data = get_db()
    date = f"{data[5]}.{data[6]}.{data[7]} {data[8]}:{data[9]}"
    is_raining = "Nie"
    if data[4] == 1:
        is_raining = "Tak"
    return render_template('index.html', date=date, temp=data[1], press=data[2], hum=data[3], rain=is_raining)

@app.route('/api/get1h')
def get1h():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    data = cursor.execute('SELECT * FROM temperature ORDER BY id DESC LIMIT 4').fetchall()
    connection.close()
    return data

@app.route('/api/send', methods=['POST'])
def send():
    data = request.json
    #data = request.get_data()
    #data = json.loads(data)
    temperature = round(data['temperature'], 2)
    pressure = round(data['pressure'], 1)
    humidity = round(data['humidity'], 1)
    rain = data['rain']
    save_to_db(temperature, pressure, humidity, rain)
    print( f"{temperature},  {pressure},  {humidity}, {rain}" )
    return f"{temperature},  {pressure},  {humidity}, {rain}"

if __name__ == '__main__':
    configure_db()
    app.run(debug=True,port=1111,host='0.0.0.0')
