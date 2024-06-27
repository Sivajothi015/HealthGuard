import serial
import time
import mysql.connector
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ser = serial.Serial('COM3', 9600)  

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'database_name'
}

heart_rate_data = []
temperature_data = []

pulse_value = None
temperature_value = None


def parse_serial(data):
    global pulse_value, temperature_value
    try:
        data_str = data.decode('utf-8').strip()
        if data_str.startswith("Pulse Value:"):
            try:
                pulse_value = int(data_str.split(":")[1])
                heart_rate_data.append(pulse_value)
                if len(heart_rate_data) > 10:
                    heart_rate_data.pop(0)  
            except ValueError:
                print("Invalid pulse value received:", data_str)
        elif data_str.startswith("Temperature:"):
            try:
                temperature_value = float(data_str.split(":")[1].split(" ")[1])
                temperature_data.append(temperature_value)
                if len(temperature_data) > 10:
                    temperature_data.pop(0)  
            except (ValueError, IndexError):
                print("Invalid temperature value received:", data_str)
                
        if pulse_value is not None and temperature_value is not None:
            insert_data_into_mysql(pulse_value, temperature_value)
            pulse_value = None
            temperature_value = None
                
    except UnicodeDecodeError:
        print("Error decoding data:", data)

def insert_data_into_mysql(pulse_value, temperature_value):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "INSERT INTO health_data (heart_rate, temperature) VALUES (%s, %s)"
        cursor.execute(query, (pulse_value, temperature_value))
        connection.commit()
        print("Data inserted into MySQL table successfully.")
    except mysql.connector.Error as error:
        print("Error inserting data into MySQL:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def show_report():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "SELECT * FROM health_data ORDER BY id DESC LIMIT 10"
        cursor.execute(query)
        rows = cursor.fetchall()

        report_window = tk.Toplevel()
        report_window.title("Health Data Report")

        table = tk.Label(report_window, text="Health Data Report")
        table.grid(row=0, column=0, columnspan=2)

        tk.Label(report_window, text="ID").grid(row=1, column=0)
        tk.Label(report_window, text="Timestamp").grid(row=1, column=1)
        tk.Label(report_window, text="Heart Rate").grid(row=1, column=2)
        tk.Label(report_window, text="Temperature").grid(row=1, column=3)

        for i, row in enumerate(rows, start=2):
            for j, value in enumerate(row):
                tk.Label(report_window, text=value).grid(row=i, column=j)

    except mysql.connector.Error as error:
        print("Error fetching data from MySQL:", error)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def show_dashboard():
    dashboard_window = tk.Toplevel()
    dashboard_window.title("Dashboard")

    fig = Figure(figsize=(8, 6))
    ax = fig.add_subplot(111)

    ax.plot(range(1, len(heart_rate_data) + 1), heart_rate_data, label='Heart Rate')

    ax.plot(range(1, len(temperature_data) + 1), temperature_data, label='Temperature')

    ax.set_xlabel('Data Points')
    ax.set_ylabel('Values')
    ax.set_title('Health Data')
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=dashboard_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

window = tk.Tk()
window.title("Health Monitor")

report_button = tk.Button(window, text="Show report", command=show_report)
report_button.pack(pady=10)

dashboard_button = tk.Button(window, text="Dashboard", command=show_dashboard)
dashboard_button.pack(pady=10)

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline()
            parse_serial(data)
            window.update_idletasks()  
            window.update()
except KeyboardInterrupt:
    ser.close()
    print("Serial connection closed.")

window.mainloop()  
