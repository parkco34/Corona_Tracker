#!/usr/bin/env python
from tkinter import *
from tkcalendar import Calendar
from datetime import date, datetime, timedelta

# Create The Gui Object
tk = Tk()

# Set the geometry of the GUI Interface
tk.geometry("700x700")

cal = Calendar(
    tk,
    selectmode = 'day', 
    year = date.today().year,
    month = date.today().month,
    day = date.today().day
)

cal.pack(pady = 20, fill="both", expand=True)
breakpoint()
# Select date
def grad_date():
    date.config(text = "Selected Date is: " + cal.get_date())

tk.mainloop()


breakpoint()

