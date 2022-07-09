# Corona Tracker

# Description of Problem:

"Application to acquire the CDC's Raw Data for given *State* (or more specific location via *Coordinates*) and implements a *Time Series Analysis*, storing the Raw Data in a *Data Base*.  The final result for the *User* should be a graph showing the *rate of infection, death and recoveries*.  The Date-Range should be specified by the User via a *GUI*."

## **NOUNS**:
- Raw Data
    - Acquired via *WEB SCRAPING*
    - Adjusting for changes in data or typos:
        - Headers, cells, columns, etc.
    - LIBRARIES:
        - Pandas
        - Numpy
        - StringIO
        - datetime
        - pyautogui or dash

- Data Frame
    - Storing the Raw Data for Analysis
- Data Base
    - To Store the Data Frames
    - Connecting to some Data Base (SQL, MySQL, MongoDB, etc.)
    - An affordable and large enough to handle the data
- Graph
    - The finished product (Visualization)
    - Matplotlib or seaborn libraries
- Web site
    - Where the Web Scraping will happen via URL
    - WEB SCRAPING:
        - Clicking
        - going BACK
        - Adjusting for Raw Data Locations being changed in the future
- Dates
    - User defined Dates in which to obtain Data for
    - GUI for data-range selection
    - Date VALIDATION
- Location (coorindates, State, County, etc.)
    - Also dictated by the user
    - GUI


