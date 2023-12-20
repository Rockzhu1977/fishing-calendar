import calendar
import tkinter as tk
from lunar_python import Lunar
from datetime import datetime
from tkinter import *
import sqlite3
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import Slider
# import matplotlib.pyplot as plt

root = tk.Tk()

global_conn = None

x_values = np.array([])
y_values = np.array([])
date_labels = np.array([])
x_tags = np.array([])
x_labels = np.array([])

# Create a new figure
fig = Figure(figsize=(10, 3))
# Add a subplot to the figure - a new axes
ax = fig.add_subplot(111)
# Create a new canvas
canvas = FigureCanvasTkAgg(fig, master=root)

def init_database():
    # Connect to the SQLite database or create a new one if it doesn't exist
    conn = get_database_connection()

    # Create a cursor to interact with the database
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tidesdata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            month INTEGER, 
            day INTEGER, 
            lunar_year INTEGER, 
            lunar_month INTEGER, 
            lunar_day INTEGER,
            lunar_year_name TEXT, 
            lunar_month_name TEXT, 
            lunar_day_name TEXT, 
            lunar_yuexiang TEXT,
            tide_time TEXT,
            tide_value REAL
        )
    ''')

    conn.commit()

def get_database_connection():
    global global_conn

    # Check if the connection is already established
    if global_conn is None:
        # If the connection is not established, create one
        global_conn = sqlite3.connect("tidesdata.db")

    return global_conn

def close_database_connection():
    global global_conn

    # Check if the connection is established
    if global_conn is not None:
        # If the connection is established, close it
        global_conn.close()
        global_conn = None

def save_tides_data_to_sqlite(data_dict):
    conn = get_database_connection()

    # Create a cursor to interact with the database
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tidesdata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            month INTEGER, 
            day INTEGER, 
            lunar_year INTEGER, 
            lunar_month INTEGER, 
            lunar_day INTEGER,
            lunar_year_name TEXT, 
            lunar_month_name TEXT, 
            lunar_day_name TEXT, 
            lunar_yuexiang TEXT,
            tide_time TEXT,
            tide_value REAL
        )
    ''')

    # Insert data into the table
    for data_point in data_dict["values"]:
        time_str = data_point["time"]
        date = time_str.split("T")[0]
        dateArr = date.split("-")
        year = int(dateArr[0])
        month = int(dateArr[1])
        day = int(dateArr[2])

        calDate = datetime(year, month, day)
        lunarDate = Lunar.fromDate(calDate)
        lunar_year = lunarDate.getYear()
        lunar_month = lunarDate.getMonth()
        lunar_day = lunarDate.getDay()
        lunar_year_name = lunarDate.getYearInChinese()
        lunar_month_name = lunarDate.getMonthInChinese()
        lunar_day_name = lunarDate.getDayInChinese()
        lunar_yuexiang = lunarDate.getYueXiang()

        time = time_str.split("T")[1][:-1]
        value = data_point["value"]

        cursor.execute('''
            INSERT INTO tidesdata (year, month, day,  lunar_year, lunar_month, lunar_day,  lunar_year_name, lunar_month_name, lunar_day_name, lunar_yuexiang, tide_time, tide_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (year, month, day, lunar_year, lunar_month, lunar_day, lunar_year_name, lunar_month_name, lunar_day_name, lunar_yuexiang, time, value))

    # Commit the changes
    conn.commit()

def get_tides_data_by_year_and_date(year, month, day):
    conn = get_database_connection()

    # Create a cursor to interact with the database
    cursor = conn.cursor()

    # Query the database to get the values
    cursor.execute('''
        SELECT *
        FROM tidesdata
        WHERE year = ? AND month = ? AND day = ?
    ''', (year, month, day))

    # Fetch all the results
    results = cursor.fetchall()

    return results

def get_tides_data_by_year_and_month(year, month):
    conn = get_database_connection()

    # Create a cursor to interact with the database
    cursor = conn.cursor()

    # Query the database to get the values
    cursor.execute('''
        SELECT *
        FROM tidesdata
        WHERE year = ? AND month = ?
    ''', (year, month))

    # Fetch all the results
    results = cursor.fetchall()

    return results

def delete_tides_data_by_year_and_month(year, month):
    conn = get_database_connection()

    # Create a cursor to interact with the database
    cursor = conn.cursor()

    # Query the database to get the values
    cursor.execute('''
        DELETE FROM tidesdata
        WHERE year = ? AND month = ?
    ''', (year, month))

    # Commit the changes
    conn.commit()
    
def get_tides_data_from_api(year):
    # get the whole year data by using this API month by month
    for month in range(1, 13):
        # at first, check there is data in the database
        values = get_tides_data_by_year_and_month(year, month)
        if len(values) > 20:
            # if there is data in the database, skip this month
            continue
        else:
            # delete the data in the database
            delete_tides_data_by_year_and_month(year, month)
            
        startDate = datetime(year, month, 1).date().strftime('%Y-%m-%d')
        totalDays = str(calendar.monthrange(Year, Month)[1])
        requestUrl = "https://api.niwa.co.nz/tides/data?lat=-36.83265015797975&long=174.79550362542975&numberOfDays=" + totalDays + "&startDate=" + startDate + "&datum=LAT&apikey=h1A7ovvp55q3D9IVGgWHruEJbV7xfAHY"
        requestHeaders = {
            "x-apikey": "h1A7ovvp55q3D9IVGgWHruEJbV7xfAHY",
            "Accept": "application/json"
        }

        response = requests.get(requestUrl, headers=requestHeaders)

        if response.status_code == 200:
            data = response.json()
            
            # save the data to the database
            save_tides_data_to_sqlite(data)
        else:
            print('Failed to retrieve data' + str(response.status_code) + str(year) + str(month))

def label_calendar(Year, Month):
    label = tk.Label(root, text=str(Year) + "年")
    label.grid(row=0, column=2)
    label = tk.Label(root, text=str(Month) + "月")
    label.grid(row=0, column=4)

    for row in range(6):
        for col in range(7):
            # need added 6 row labels for showing data
            
            text_widget = tk.Text(root, height=7, width=20, wrap=tk.WORD, background="SystemTransparent", borderwidth=0)
            text_widget.grid(row=row+2, column=col, padx=5, pady=5)
            # Add different colors for each row in the cell
            for row_num in range(6):
                # color_code = "#{:02x}{:02x}{:02x}".format(row_num * 40, row_num * 40, row_num * 40)
                # text_widget.tag_configure(f"row_{row_num}", foreground="white", background=color_code, font=("Arial", 12, "bold"))
                text_widget.insert(tk.END, f"\n", f"row_{row_num}")

    # add week day labels
    weekDayLabels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i in range(7):
        label = tk.Label(root, width = 15, padx=2, pady=2, text=weekDayLabels[i])
        label.grid(row=1, column=i)

    labels = []

    MonthCal = calendar.monthcalendar(Year, Month)
    for i in range(len(MonthCal)):
        labels.append(MonthCal[i])
    for r in range(len(MonthCal)):
        for c in range(7):
            # need added 6 row labels for showing data
            text_widget = tk.Text(root, height=7, width=20, wrap=tk.WORD, background="SystemTransparent", borderwidth=0)
            text_widget.grid(row=r+2, column=c, padx=5, pady=5)
            # text_widget.bind('<Motion>', on_mousemove)
            # data = "Test"
            # text_widget.bind('<Button-1>', lambda event, arg=data: on_mouseclick(event, arg))

            if labels[r][c] > 0:
                Day = int(labels[r][c])
                # get the tides data from the database
                data = get_tides_data_by_year_and_date(Year, Month, Day)

                fgc = "Black"
                bgc = "SystemTransparent"
                # change the background color to green according date
                if (data[0][6] >= 1 and data[0][6] <= 3) or (data[0][6] >= 15 and data[0][6] <= 17):
                    fgc = "White"
                    bgc = "Green"
                elif (data[0][6] >= 7 and data[0][6] <= 9) or (data[0][6] >= 22 and data[0][6] <= 24):
                    fgc = "White"
                    bgc = "Blue"
                elif (data[0][6] == 29 or data[0][6] == 30 or data[0][6] == 4 or data[0][6] == 5 or data[0][6] == 13 or data[0][6] == 14 or data[0][6] == 18 or data[0][6] == 19):
                    fgc = "Black"
                    bgc = "LightYellow"
                else:
                    fgc = "Black"
                    bgc = "SystemTransparent"
                text_widget.configure(fg=fgc, bg=bgc)

                # Add different colors for each row in the cell
                for row_num in range(6):
                    bg = bgc
                    fg = fgc
                    
                    if row_num == 0:
                        dispText = str(labels[r][c])
                        text_widget.tag_configure(f"row_{row_num}", font=("Arial", 12, "bold"), justify='center')
                        text_widget.insert(tk.END, f"{dispText}\n", f"row_{row_num}")
                    elif row_num == 1:
                        # display the lunar date
                        if len(data) == 0:
                            dispText = ""
                        else:
                            dispText = data[0][8] + '月' + data[0][9] + ' ' + data[0][10]
                        text_widget.tag_configure(f"row_{row_num}", font=("Arial", 12, "bold"), justify='center')
                        text_widget.insert(tk.END, f"{dispText}\n", f"row_{row_num}")
                    elif row_num == 2:
                        # display the first tide time and value
                        if len(data) == 0:
                            dispText = ""
                        else:
                            dispText = data[0][11] + "  " + str(data[0][12])
                            # get the hour from data[0][11] which is "hh:mm:ss"
                            hour = int(data[0][11].split(":")[0])
                            if data[0][12] > 2.0 and hour >= 6 and hour <= 18:
                                bg = "Red"
                                fg = "White"
                                
                        text_widget.tag_configure(f"row_{row_num}", foreground=fg, background=bg, font=("Arial", 12, "bold"), justify='center')
                        text_widget.insert(tk.END, f"{dispText}\n", f"row_{row_num}")
                    elif row_num == 3:
                        # display the second tide time and value
                        # get the hour from data[0][11] which is "hh:mm:ss"
                        hour = int(data[1][11].split(":")[0])
                        if len(data) == 1:
                            dispText = ""
                        else:
                            dispText = data[1][11] + "  " + str(data[1][12])
                            # get the hour from data[0][11] which is "hh:mm:ss"
                            hour = int(data[1][11].split(":")[0])
                            if data[1][12] > 2.0 and hour >= 6 and hour <= 18:
                                bg = "Red"
                                fg = "White"
                        text_widget.tag_configure(f"row_{row_num}", foreground=fg, background=bg, font=("Arial", 12, "bold"), justify='center')
                        text_widget.insert(tk.END, f"{dispText}\n", f"row_{row_num}")
                    elif row_num == 4:
                        # display the third tide time and value
                        if len(data) == 2:
                            dispText = ""
                        else:
                            dispText = data[2][11] + "  " + str(data[2][12])
                            # get the hour from data[0][11] which is "hh:mm:ss"
                            hour = int(data[2][11].split(":")[0])
                            if data[2][12] > 2.0 and hour >= 6 and hour <= 18:
                                bg = "Red"
                                fg = "White"
                        text_widget.tag_configure(f"row_{row_num}", foreground=fg, background=bg, font=("Arial", 12, "bold"), justify='center')
                        text_widget.insert(tk.END, f"{dispText}\n", f"row_{row_num}")
                    elif row_num == 5:
                        # display the fourth tide time and value
                        if len(data) == 3:
                            dispText = ""
                        else:
                            dispText = data[3][11] + "  " + str(data[3][12])
                            # get the hour from data[0][11] which is "hh:mm:ss"
                            hour = int(data[3][11].split(":")[0])
                            if data[3][12] > 2.0 and hour >= 6 and hour <= 18:
                                bg = "Red"
                                fg = "White"
                        text_widget.tag_configure(f"row_{row_num}", foreground=fg, background=bg, font=("Arial", 12, "bold"), justify='center')
                        text_widget.insert(tk.END, f"{dispText}\n", f"row_{row_num}")
                    # elif row_num == 6:
                    #     # display the fourth tide time and value
                    #     if len(data) == 4:
                    #         dispText = ""
                    #     else:
                    #         dispText = data[4][11] + "  " + str(data[4][12])
                    #     text_widget.tag_configure(f"row_{row_num}", font=("Arial", 12, "bold"), justify='center')
                    #     text_widget.insert(tk.END, f"{dispText}\n", f"row_{row_num}")
                    else:
                        dispText = ""
                        text_widget.tag_configure(f"row_{row_num}", font=("Arial", 12, "bold"), justify='center')
                        text_widget.insert(tk.END, f"{dispText}\n", f"row_{row_num}")

def button_previous():
    global Year
    global Month
    if Month == 1:
        Month = 12
        Year -= 1
    else:
        Month -= 1
    label_calendar(Year, Month)

def button_next():
    global Year
    global Month
    if Month == 12:
        Month = 1
        Year += 1
    else:
        Month += 1
    label_calendar(Year, Month)

def on_mousemove(event):
    x = event.x
    y = event.y
    print(f"x: {x}, y: {y}")

def on_mouseclick(event, arg):
    x = event.x
    y = event.y
    print(f"x: {x}, y: {y}, arg: {arg}")
    # toplevel = Toplevel()
    # label1 = Label(toplevel, text="AAA", height=0, width=100)
    # label1.pack()
    # label2 = Label(toplevel, text="BBB", height=0, width=100)
    # label2.pack()

def calculate_chartdata(tide_data):
    global x_values, y_values, date_labels, x_tags, x_labels
    lenData = len(tide_data)
    x_tags = np.arange(1, lenData + 1, 5)

    # Generate x and y values for each pair of consecutive points
    for i in range(lenData - 1):
        # one data record is like this:
        # (1, 2023, 1, 1, 2022, 12, 1, '二零二二', '十二月', '初一', '小寒', '00:00:00', 0.8)
        # which is (id, year, month, day, lunar_year, lunar_month, lunar_day, lunar_year_name, lunar_month_name, lunar_day_name, lunar_yuexiang, tide_time, tide_value)
        x_segment = np.linspace(i+1, i+2, 100, endpoint=False)
        y_segment = float(tide_data[i][12]) + (float(tide_data[i + 1][12]) - float(tide_data[i][12])) * 0.5 * (1 - np.cos(np.pi * (x_segment - (i + 1))))
        
        # Append the segment values to the arrays
        x_values = np.append(x_values, x_segment)
        y_values = np.append(y_values, y_segment)

        strDate = str(tide_data[i][1]) + "-" + str(tide_data[i][2]) + "-" + str(tide_data[i][3]) + " " + tide_data[i][11]
        date_labels = np.append(date_labels, strDate)

    lastIndex = lenData - 1
    strDate = str(tide_data[lastIndex][1]) + "-" + str(tide_data[lastIndex][2]) + "-" + str(tide_data[lastIndex][3]) + " " + tide_data[lastIndex][11]
    date_labels = np.append(date_labels, strDate)

    x_labels = date_labels[::5]
    # for i in range(len(x_labels)):
    #     x_labels[i] = x_labels[i][:10]

def on_mouse_move(event, data):
    nLen = len(data)
    if event.xdata is not None and event.ydata is not None:
        if event.xdata < 1 or event.xdata > len(data):
            return
        # Draw a dot on the relevant line
        x_mouse = round(event.xdata, 2)
        first_occurrence_index = np.argmax(x_values == x_mouse)
        y_mouse = y_values[first_occurrence_index]

        tide_index = int(x_mouse)
        if tide_index <= 0:
            tide_index = 1
        elif tide_index >= nLen:
            tide_index = nLen - 1
        high_tide = float(data[tide_index][12])
        low_tide = float(data[tide_index - 1][12])
        if high_tide < low_tide:
            high_tide = float(data[tide_index - 1][12])
            low_tide = float(data[tide_index][12])

        if high_tide - low_tide <= 0:
            high_tide= low_tide + 0.1
        
        tide_percentage = (y_mouse - low_tide) / (high_tide - low_tide) * 100

        # according the tide_index to calculate the time on x axis
        # get the string of the time in the points array first, it should be between the current index and the next index
        # then convert the string to datetime object
        # finally, calculate the time difference and time the x_mouse to get the time on x axis
        time1 = datetime.strptime(date_labels[tide_index - 1], "%Y-%m-%d %H:%M:%S")
        time2 = datetime.strptime(date_labels[tide_index], "%Y-%m-%d %H:%M:%S")
        time_diff = time2 - time1
        time_mouse = time1 + time_diff * (x_mouse - tide_index)

        # Clear the previous scatter plot
        if hasattr(on_mouse_move, 'scatter'):
            on_mouse_move.scatter.remove()
            on_mouse_move.text.remove()

        # Create a new scatter plot for the dot and text, draw the dot and text on the canvas
        on_mouse_move.scatter = ax.scatter([x_mouse], [y_mouse], color='green', data=tide_percentage, s=100, zorder=5)
        str = time_mouse.strftime("%H:%M") + "--" + f" {round(tide_percentage, 2)}%"
        on_mouse_move.text = ax.text(x_mouse, y_mouse, str, ha='center', va='bottom', color='green', zorder=5)
        # Redraw the plot
        canvas.draw()

def on_slidebar_move(pos, showbars=8):
    ax.set_xlim(pos-1, pos+showbars+1)
    canvas.draw_idle()

init_database()

get_database_connection()

CurDate = datetime.now()
Year = CurDate.year
Month = CurDate.month

# get_tides_data_from_api(Year)
# get_tides_data_from_api(2024)

label_calendar(Year, Month)

button1 = tk.Button(root, text='Previous', command=button_previous)
button1.grid(row=8, column=0)

button2 = tk.Button(root, text='Next', command=button_next)
button2.grid(row=8, column=6)

# get the tides data from the database
TideData = get_tides_data_by_year_and_month(Year, Month)

calculate_chartdata(TideData)

# # set width and height of the chart
# plt.figure(figsize=(10, 5))

# # Plot the sine curve between consecutive points
# line, = plt.plot(x_values, y_values, label='Tide line', color='blue')

# # Plot the given points
# # scatter = plt.scatter(xtags, points[:, 1].astype(float), color='red', marker='o', label='Tide point')

# # Add title and labels
# plt.title('Sine Curve Between Given Points')
# plt.xlabel('Date and Time')
# plt.ylabel('y')
# plt.grid(True)

# # Format x-axis labels
# plt.xticks(rotation=45, ha='right')
# plt.xticks(xtags, labels)

# # Add legend
# plt.legend()
# # Display the plot
# plt.show()

# Plot the data
line, = ax.plot(x_values, y_values, label='Tide line', color='blue')
# Set the title
# ax.set_title("Tide Chart")
# Set the x-axis label
ax.set_xlabel("Date")
# Set the y-axis label
ax.set_ylabel("Tide Level")
# Set the x-axis ticks
ax.set_xticks(x_tags)
# Set the y-axis ticks
# ax.set_yticks(range(0, 5))
ax.set_xticklabels(x_labels)
# ax.set_yticklabels(range(0, 5))
# Set the x-axis limits
ax.set_xlim(0, 4)
# Set the y-axis limits
# ax.set_ylim(0, 5)
# Set the grid on
ax.grid(True)
# Set the legend
ax.legend(["Tide"])
# Set the x-axis tick labels at an angle
for tick in ax.get_xticklabels():
    tick.set_rotation(45)
# Set the y-axis tick labels at an angle
# for tick in ax.get_yticklabels():
#     tick.set_rotation(45)
# Clear the current figure
# plt.clf()

# add mouse move event
fig.canvas.mpl_connect('motion_notify_event', lambda event, data=TideData: on_mouse_move(event, data))

# Add a slider to the bottom of the plot
slider_ax = fig.add_axes([0.1, 0.01, 0.5, 0.03], facecolor="skyblue")
slider = Slider(slider_ax, 'Time', 0, len(TideData), valinit=0, valstep=1)
slider.on_changed(lambda pos, showbars=8: on_slidebar_move(pos, showbars))

canvas_widget = canvas.get_tk_widget()

# Pack the canvas widget to fill the entire window
canvas_widget.grid(row=9, column=0, columnspan=8)

root.mainloop()

close_database_connection()
