#!/usr/bin/env python
from datetime import datetime, date, timedelta
import pandas as pd

class Grab_Dates(object):
    """
    Obtains a Date Range for Scrape to use for Data Acquisition
    -------------------------------------------------------------
    INPUTS:
        initial = (str) Initial Date
        final = (str) Final Date
        gui = (bool) Optional argument, when True, will generate a Dash GUI for
        DateRangePicker selection
    """

    def __init__(self, initial, final, gui=False):
        self.initial = initial
        self.final = final
        self.gui = gui

    def validate_date(self, date, format):
        """
        Validates input and returns a LIST of Dates (Date Range)
        ---------------------------------------------------
        INPUTS:
            format = (str) Format that must be valid in order for the proper
            Date Range to be returned

        OUTPUTS:
            (list) List of dates in the Date Range

        """
        try:
            datetime.strptime(date, format)
            return True

        except ValueError:
            print(f'\nIncorrect String Format for {date}\n')
            return False

    def main(self):
        """
        Returns a Date Range in the form of DAYS
        ---------------------
        OUTPUTS:
            (list) Date Range (per Day)
        """
        
        if ((self.validate_date(self.initial, "%m-%d-%Y")& 
            (self.validate_date(self.final, "%m-%d-%Y")))):
             
            __initial = datetime.strptime(self.initial, "%m-%d-%Y")
            __final = datetime.strptime(self.final, "%m-%d-%Y")

            dates = pd.date_range(__initial, __final, freq='d')
            dates = dates.strftime("%m-%d-%Y") 

            return dates.tolist()

        else:
            print("\nLo Siento...\n")





#gd = Grab_Dates('1-22-2022', '3-22-2022')
#dates = gd.main()
# '1-22-2022'
# '3-22-2022'
