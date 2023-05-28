import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import IntVar
from tkinter import StringVar
import webbrowser
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

# Create an instance of tkinter
root = tk.Tk()

# Create the tab control
tabControl = ttk.Notebook(root)

# Create the configuration for each tab
timer = ttk.Frame(tabControl)
history = ttk.Frame(tabControl)
settings = ttk.Frame(tabControl)

# Add each tab to the tab control
tabControl.add(timer, text='Timer')
tabControl.add(history, text='History')
tabControl.add(settings, text='Settings')

# Define the list of ranks
ranks = ['Probationary Reserve Deputy', 'Reserve Deputy', 'Senior Reserve Deputy', 'Probationary Deputy',
         'Deputy I', 'Deputy II', 'Deputy III', 'Senior Deputy', 'Master Deputy', 'Corporal', 'Senior Corporal',
         'Sergeant', 'Staff Sergeant', 'Master Sergeant', 'Lieutenant', 'Captain', 'Sheriff Major', 'Sheriff Commander',
         'Sheriff Colonel', 'Chief Deputy', 'Sheriff']

# Create and add the input fields to the settings tab
email_label = ttk.Label(settings, text="Email: ")
email_label.grid(column=0, row=0)
email_entry = ttk.Entry(settings)
email_entry.grid(column=1, row=0)

name_callsign_label = ttk.Label(settings, text="Name and Callsign: ")
name_callsign_label.grid(column=0, row=1)
name_callsign_entry = ttk.Entry(settings)
name_callsign_entry.grid(column=1, row=1)

badge_label = ttk.Label(settings, text="Badge Number: ")
badge_label.grid(column=0, row=2)
badge_entry = ttk.Entry(settings)
badge_entry.grid(column=1, row=2)

rank_label = ttk.Label(settings, text="Rank: ")
rank_label.grid(column=0, row=3)
rank_combobox = ttk.Combobox(settings, values=ranks)
rank_combobox.grid(column=1, row=3)

timezone_label = ttk.Label(settings, text="Timezone: ")
timezone_label.grid(column=0, row=4)
timezone_entry = ttk.Entry(settings)
timezone_entry.grid(column=1, row=4)


def on_closing():
    settings_data = {
        'email': email_entry.get(),
        'name_and_callsign': name_callsign_entry.get(),
        'badge_number': badge_entry.get(),
        'rank': rank_combobox.get(),
        'timezone': timezone_entry.get()
    }

    with open('settings_data.json', 'w') as json_file:
        json.dump(settings_data, json_file)

    root.destroy()


# Section: Timer Functionality

# Define the timer variables
timer_running = False
timer_paused = False
timer_value = 0
start_time = None  # Declare the start_time variable
previous_subdivision = ""  # Store the previously selected subdivision

# Add label for current patrol time
current_time_label = ttk.Label(timer, text="YOUR CURRENT PATROL TIME")
current_time_label.pack()

# Define the timer label
timer_label = ttk.Label(timer, text="00:00:00", font=("Arial", 24))
timer_label.pack(pady=20)

# Define the timer buttons
start_button = ttk.Button(timer, text="Start")
start_button.pack(pady=10)

end_button = ttk.Button(timer, text="End")
end_button.pack(pady=10)

# Dictionary to store subdivision times
subdivision_times = {}


def start_timer():
    """
    Start or resume the timer.
    """
    global timer_running, timer_paused, timer_value, start_time, previous_subdivision

    if not timer_running:
        # Start the timer
        timer_running = True
        start_button.configure(text="Pause")
        start_time = datetime.now()  # Assign the current time to start_time
        timer_tick()
    elif timer_paused:
        # Resume the timer
        timer_paused = False
        start_button.configure(text="Pause")
        timer_tick()
    else:
        # Pause the timer
        timer_paused = True
        start_button.configure(text="Resume")

    # Check if the subdivision selection has changed
    current_subdivision = subdivision_combobox.get()
    if current_subdivision != previous_subdivision:
        update_subdivision_time(previous_subdivision)  # Pause the timer for the previous subdivision
        previous_subdivision = current_subdivision
        update_subdivision_time(current_subdivision)  # Start the timer for the current subdivision


def end_timer():
    """
    Stop and reset the timer.
    """
    global timer_running, timer_paused, timer_value, previous_subdivision
    
    if timer_running:
        # End the timer
        timer_running = False
        timer_paused = False
        end_time = datetime.now()
        duration = timedelta(seconds=timer_value)
        # Calculate hours, minutes and seconds
        seconds = duration.total_seconds()
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Format as HH:MM:SS
        duration_formatted = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        
        start_button.configure(text="Start")
        timer_value = 0  # Reset the timer value to 0
        
        # Update the time for the current subdivision
        current_subdivision = subdivision_combobox.get()
        update_subdivision_time(current_subdivision)
        
        
        # Show the Patrol Log Details dialog
        show_patrol_log_details(start_time, end_time, duration_formatted, subdivision_times)
        
        # Clear the subdivision times and reset the previous subdivision
        subdivision_times.clear()
        previous_subdivision = ""
        

def timer_tick():
    """
    Update the timer label every second.
    """
    if timer_running and not timer_paused:
        global timer_value
        timer_value += 1
        hours = timer_value // 3600
        minutes = (timer_value % 3600) // 60
        seconds = (timer_value % 3600) % 60
        timer_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        update_subdivision_time(subdivision_combobox.get())  # Add one second to the selected subdivision
        timer_label.after(1000, timer_tick)


# Section: Patrol Log
patrol_log_file = 'patrol_log_data.json'


def show_patrol_log_details(start_time, end_time, duration, subdivision_times):
    """
    Show the Patrol Log Details dialog.
    """
    dialog_title = "Patrol Log Details"
    dialog_message = f"Your patrol time was: {duration}\n\n"
    
    for subdivision, time in subdivision_times.items():
        formatted_time = f"{time // 3600:02d}:{(time % 3600) // 60:02d}:{(time % 3600) % 60:02d}"
        dialog_message += f"{subdivision}: {formatted_time}\n"
        
    dialog_box = messagebox.askquestion(dialog_title, dialog_message, icon='info')
    if dialog_box == 'yes':
        patrol_log_dialog = simpledialog.Toplevel(root)
        patrol_log_dialog.title(dialog_title)
        
        # Add duration field
        ttk.Label(patrol_log_dialog, text="Start Date & Time:").grid(column=0, row=0, sticky="w")
        start_time_entry = ttk.Entry(patrol_log_dialog,width=15)
        start_time_entry.grid(column=0, row=0, padx=120, pady=5)
        start_time = start_time.replace(second=0, microsecond=0).isoformat()
        start_time= start_time.replace('T', ' ')
        start_time_entry.insert(0, start_time)
        
        # Add duration field
        ttk.Label(patrol_log_dialog, text="End Date & Time:").grid(column=0, row=1, sticky="w")
        start_time_entry = ttk.Entry(patrol_log_dialog,width=15)
        start_time_entry.grid(column=0, row=1, padx=120, pady=5)
        end_time = end_time.replace(second=0, microsecond=0).isoformat()
        end_time = end_time.replace('T', ' ')
        start_time_entry.insert(0, end_time)
        
        
        # Add duration field
        ttk.Label(patrol_log_dialog, text="Duration:").grid(column=0, row=2, sticky="w")
        duration_entry = ttk.Entry(patrol_log_dialog,width=7)
        duration_entry.grid(column=0, row=2, padx=10, pady=5)
        duration_entry.insert(0, duration)
        
        # Add label and checkboxes for comments
        ttk.Label(patrol_log_dialog, text="Comments:").grid(column=0, row=3, sticky="w")
        
        comments_frame = ttk.Frame(patrol_log_dialog)
        comments_frame.grid(column=0, row=4, columnspan=2, padx=10, pady=5, sticky="w")
        
        options = [
            "BCSO Continuing Education Training",
            "Subdivision Training",
            "SRU Training",
            "FTO LEO Training",
            "Beta Testing Hours"
        ]
        
        comment_vars = []
        
        for i, option in enumerate(options):
            var = IntVar()
            comment_vars.append(var)
            
            ttk.Checkbutton(comments_frame, text=option, variable=var).grid(column=0, row=i, sticky="w")
            
        # Add other field
        ttk.Label(comments_frame, text="Other:").grid(column=0, row=len(options), pady=5, sticky="w")
        other_entry = ttk.Entry(comments_frame, width=30)
        other_entry.grid(column=0, row=len(options)+1, padx=0, sticky="w")
        
        # Add label and entry boxes for subdivision times
        ttk.Label(patrol_log_dialog, text="Subdivision Times:").grid(column=0, row=len(options) + 1, sticky="w")
        
        subdivision_frame = ttk.Frame(patrol_log_dialog)
        subdivision_frame.grid(column=0, row=len(options) + 2, columnspan=2, padx=10, pady=5, sticky="w")
        
        subdivision_options = ['CID', 'TED', 'WLR', 'WSU','K9']
        subdivision_vars = []
        
        for i, subdivision in enumerate(subdivision_options):
            var = StringVar(value=format_time(subdivision_times.get(subdivision, 0)))
            subdivision_vars.append(var)
            
            ttk.Label(subdivision_frame, text=subdivision).grid(row=i, column=0, padx=5, pady=5)
            ttk.Entry(subdivision_frame, textvariable=var, width=7).grid(row=i, column=1, padx=5, pady=5)
            
        # Function to save the details entered by the user
        def save_comments():
            selected_comments = [option for i, option in enumerate(options) if comment_vars[i].get() == 1]
            other_comment = other_entry.get()
            
            if other_comment:
                selected_comments.append(other_comment)
                
            selected_subdivision_times = {}
            for i, subdivision in enumerate(subdivision_options):
                time_str = subdivision_vars[i].get()
                selected_subdivision_times[subdivision] = parse_time(time_str)
                
            # Retrieve the entered duration
            updated_duration = duration_entry.get()
            
            # Save the patrol log details
            save_patrol_log_details(start_time, end_time, updated_duration, selected_comments, selected_subdivision_times)
            
            patrol_log_dialog.destroy()
            
        # Add save button which calls save_comments function
        ttk.Button(patrol_log_dialog, text="Save", command=lambda: [save_comments(), show_popup_options()]).grid(column=0, row=len(options) + 3, pady=10)
        
def show_popup_options():
    """
    Show a popup with the following options: auto submission, prefilled submission, and exit.
    """
    popup = tk.Toplevel(root)
    popup.title("Select an option")
    
    def on_auto_submission():
        # Load JSON data from file
        with open('settings_data.json') as f:
            settings = json.load(f)
        with open('patrol_log_data.json') as f:
            patrol = json.load(f)
        if any(time != "00:00:00" for time in subdivision_times.values()):
            link = "https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/viewform?emailAddress={}&entry.970139392={}&entry.525828639={}&entry.802789954={}&entry.812379661={}&entry.1193847989={}&entry.1990843866={}&entry.2017153381={}&entry.975477614=Yes&entry.1780407366={}&entry.155790891={}&entry.239103213={}&entry.1234850748={}&entry.394082834={}".format(
            #"https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/viewform?emailAddress={}&entry.1019179407={}&entry.805651499={}&entry.214679648={}&entry.243689543={}&entry.1076382024={}&entry.324817261={}&entry.980582373={}&entry.1610264503=Yes&entry.1284273733={}&entry.1548375218={}&entry.313224238={}&entry.1471195366={}&entry.1881504976={}".format(
                settings['email'],
                settings["badge_number"],
                settings["name_and_callsign"],
                settings["rank"],
                patrol["start_time"],
                patrol["end_time"],
                settings["timezone"],
                patrol["duration"],
                patrol["subdivision_times"]["WSU"],
                patrol["subdivision_times"]["WLR"],
                patrol["subdivision_times"]["CID"],
                patrol["subdivision_times"]["TED"],
                patrol["subdivision_times"]["K9"]
            )
            pass
        else:
            # Format the link using the JSON elements
            link = "https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/viewform?emailAddress={}&entry.1019179407={}&entry.805651499={}&entry.214679648={}&entry.243689543={}&entry.1076382024={}&entry.324817261={}&entry.980582373={}entry.1610264503=No".format(
                settings['email'],
                settings["badge_number"],
                settings["name_and_callsign"],
                settings["rank"],
                patrol["start_time"],
                patrol["end_time"],
                settings["timezone"],
                patrol["duration"],
            )
            
            # Set up Chrome driver
            chrome_options = Options()
            chrome_options.binary_location = '/Users/danielnephew/Downloads/chromedriver_mac_arm64/chromedriver'  # Replace with the actual path to the Chrome binary
            driver = webdriver.Chrome(options=chrome_options, executable_path='/Users/danielnephew/Downloads/chromedriver_mac_arm64/chromedriver')  # Replace with the actual path to the ChromeDriver executable
            # Remove the "--headless" option to show the browser window
            driver = webdriver.Chrome(options=chrome_options)
            chrome_options.add_argument("--no-sandbox")
            
            
            
            # Open the Google Form
            driver.get(link)
            
            # Find and fill the email address field
            email_field = driver.find_element_by_name("email address")  # Replace with the actual field name
            email_field.send_keys("dnephew@pm.me")
            
            # Wait for the code to appear and copy it
            time.sleep(5)  # Adjust the wait time as needed
            code_element = driver.find_element_by_xpath("//span[contains(text(), 'Type this code:')]/following-sibling::code")
            code = code_element.text
            
            # Find and fill the code field
            code_field = driver.find_element_by_name("Type this code:")  # Replace with the actual field name
            code_field.send_keys(code)
            
            # Click the "Next" button twice
            next_button = driver.find_element_by_xpath("//span[text()='Next']")
            next_button.click()
            time.sleep(1)  # Wait for the page to load
            next_button.click()
            time.sleep(1)  # Wait for the page to load
            
            # Submit the form
            submit_button = driver.find_element_by_xpath("//span[text()='Submit']")
            submit_button.click()
            
            # Close the browser
            driver.quit()
            
        pass
        
    def on_prefilled_submission():
        # Load JSON data from file
        with open('settings_data.json') as f:
            settings = json.load(f)
        with open('patrol_log_data.json') as f:
            patrol = json.load(f)
            
        subdivision_times = patrol.get("subdivision_times", {})
        
        # Check if any subdivision time is not "00:00:00"
        if any(time != "00:00:00" for time in subdivision_times.values()):
            link = "https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/viewform?emailAddress={}&entry.1019179407={}&entry.805651499={}&entry.214679648={}&entry.243689543={}&entry.1076382024={}&entry.324817261={}&entry.980582373={}&entry.1610264503=Yes&entry.1284273733={}&entry.1548375218={}&entry.313224238={}&entry.1471195366={}&entry.1881504976={}".format(
                settings['email'],
                settings["badge_number"],
                settings["name_and_callsign"],
                settings["rank"],
                patrol["start_time"],
                patrol["end_time"],
                settings["timezone"],
                patrol["duration"],
                patrol["subdivision_times"]["WSU"],
                patrol["subdivision_times"]["WLR"],
                patrol["subdivision_times"]["CID"],
                patrol["subdivision_times"]["TED"],
                patrol["subdivision_times"]["K9"]
            )
            pass
        else:
            # Format the link using the JSON elements
            link = "https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/viewform?emailAddress={}&entry.1019179407={}&entry.805651499={}&entry.214679648={}&entry.243689543={}&entry.1076382024={}&entry.324817261={}&entry.980582373={}entry.1610264503=No".format(
                settings['email'],
                settings["badge_number"],
                settings["name_and_callsign"],
                settings["rank"],
                patrol["start_time"],
                patrol["end_time"],
                settings["timezone"],
                patrol["duration"],
            )
            # ... Continue with the rest of your code ...
            
        print(link)
        webbrowser.open(link, new=2)
        #https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/viewform?entry.1019179407=107423&entry.805651499=Daniel%20N.%203C-415&entry.214679648=Deputy%20I&entry.243689543=2023-05-23+19:30:00&entry.1076382024=2023-05-23+21:00:00&entry.324817261=EST&entry.980582373=01:30:00&entry.1767583356=Austin%20S.%203C-49&entry.1610264503=No
        #https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/viewform?entry.1019179407=107423&entry.805651499=Daniel%20N.%203C-415&entry.214679648=Deputy%20I&entry.243689543=2023-05-23+19:30:00&entry.1076382024=2023-05-23+21:00:00&entry.324817261=EST&entry.980582373=01:30:00&entry.1767583356=Austin%20S.%203C-49&entry.1610264503=Yes&entry.1284273733=&entry.1548375218=&entry.313224238=01:30:00&entry.1471195366=&entry.1881504976=
        
    def on_exit():
        popup.destroy()
        
    auto_submission_button = ttk.Button(popup, text="Auto Submission", command=on_auto_submission)
    auto_submission_button.pack(padx=20, pady=10)
    
    prefilled_submission_button = ttk.Button(popup, text="Prefilled Submission", command=on_prefilled_submission)
    prefilled_submission_button.pack(padx=20, pady=10)
    
    exit_button = ttk.Button(popup, text="Exit", command=on_exit)
    exit_button.pack(padx=20, pady=10)


def format_time(seconds):
    """
    Format the time in seconds to HH:MM:SS.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 3600) % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def parse_time(time_str):
    """
    Parse the time string in HH:MM:SS format and return the time in seconds.
    """
    try:
        hours, minutes, seconds = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        return 0
    

def save_patrol_log_details(start_time, end_time, duration, comments, subdivision_times):
    formatted_duration = str(duration)[:-2] + "00"
    
    formatted_subdivision_times = {
        subdivision: format_time(time)[:-2] + "00"
        for subdivision, time in subdivision_times.items()
    }
    
    timer_data = {
        'start_time': start_time,
        'end_time': end_time,
        'duration': formatted_duration,
        'comments': comments,
        'subdivision_times': formatted_subdivision_times
    }
    
    try:
        with open(patrol_log_file, 'w') as json_file:
            json.dump(timer_data, json_file, separators=(',', ':'))
            json_file.write('\n')
    except IOError:
        print("Error: Unable to save patrol log details.")
        

        
        
        
        
# Section: History


# Add the subdivision patrol section
subdivision_label = ttk.Label(timer, text="ACTIVE SUBDIVISION")
subdivision_label.pack()

subdivision_options = ['CID', 'TED', 'WLR', 'WSU','K9',' ']
subdivision_combobox = ttk.Combobox(timer, values=subdivision_options,width=8)
subdivision_combobox.pack()
subdivision_combobox.set("")  # Set default selection as blank

# Define the subdivision times label
subdivision_times_label = ttk.Label(timer, text="Subdivision Times:")
subdivision_times_label.pack()


def update_subdivision_time(subdivision):
    """
    Update the subdivision time based on the current subdivision selection.
    """
    if subdivision and timer_running:
        subdivision_time = subdivision_times.get(subdivision, 0)
        subdivision_time += 1
        subdivision_times[subdivision] = subdivision_time

        # Update the subdivision times label
        subdivision_times_text = "\n".join([f"{subdivision}: {time // 3600:02d}:{(time % 3600) // 60:02d}:{(time % 3600) % 60:02d}"
                                            for subdivision, time in subdivision_times.items()])
        subdivision_times_label.configure(text=f"Subdivision Times:\n{subdivision_times_text}")



# Configure button commands
start_button.configure(command=start_timer)
end_button.configure(command=end_timer)
subdivision_combobox.bind("<<ComboboxSelected>>", lambda event: update_subdivision_time(subdivision_combobox.get()))

# End of Timer Functionality section

# Load the settings data if it exists
if os.path.exists('settings_data.json'):
    with open('settings_data.json', 'r') as json_file:
        settings_data = json.load(json_file)

    email_entry.insert(0, settings_data.get('email', ''))
    name_callsign_entry.insert(0, settings_data.get('name_and_callsign', ''))
    badge_entry.insert(0, settings_data.get('badge_number', ''))
    rank_combobox.set(settings_data.get('rank', ''))

root.protocol("WM_DELETE_WINDOW", on_closing)
tabControl.pack(expand=1, fill="both")  # Pack to make visible


root.mainloop()
                    
#import requests
#from bs4 import BeautifulSoup
#import json
#
#def extract_captcha_code(soup):
#   captcha_span = soup.find('span', {'class': 'M7eMe'})
#   captcha_text = captcha_span.text  # Get the full text "Type this code: 76ISUS"
#   captcha_code = captcha_text.split(': ')[1]  # Split the text and get the second part which is the captcha code
#   return captcha_code
#
#def submit_form(page, captcha_code, settings_data):
#   if page == 1:
#       form_data = {
#           'emailAddress': settings_data['email'],
#           'entry.2092678553': captcha_code,  # Put the captcha code here
#           # Continue with the rest of your form fields
#       }
#   elif page == 2:
#       form_data = {
#           'entry.214679648': settings_data['rank'],
#           'entry.805651499': settings_data['name_and_callsign'],
#           'entry.1019179407': settings_data['badge_number'],
#           # Continue with the rest of your form fields
#       }
#   elif page == 3:
#           form_data = {
#               'entry.243689543_year': patrol_log_data['start_time']['year'],
#               'entry.243689543_month': patrol_log_data['start_time']['month'],
#               'entry.243689543_day': patrol_log_data['start_time']['day'],
#               'entry.243689543_hour': patrol_log_data['start_time']['hour'],
#               'entry.243689543_minute': patrol_log_data['start_time']['minute'],
#               'entry.324817261': settings_data['timezone'],  # From your settings_data.json
#               'entry.980582373_hour': patrol_log_data['duration']['hours'],
#               'entry.980582373_minute': patrol_log_data['duration']['minutes'],
#               'entry.1076382024_year': patrol_log_data['end_time']['year'],
#               'entry.1076382024_month': patrol_log_data['end_time']['month'],
#               'entry.1076382024_day': patrol_log_data['end_time']['day'],
#               'entry.1076382024_hour': patrol_log_data['end_time']['hour'],
#               'entry.1076382024_minute': patrol_log_data['end_time']['minute'],
#               'entry.1610264503': has_subdivision(patrol_log_data['subdivision_times']),
#               **generate_subdivision_times(patrol_log_data['subdivision_times'])
#           }
#           response = requests.post('https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/formResponse', data=form_data)
#   elif page == 4:
#               # Submitting the form without any additional data
#               response = requests.post('https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/formResponse', data={})
#   return response
#   def generate_subdivision_times(subdivision_times):
#       # The order of subdivisions as they appear in the form
#       subdivisions_order = ['WSU', 'WLR', 'CID', 'TED']
#                   
#       # The name attributes of the corresponding form fields
#       subdivisions_entry_ids = [
#           'entry.1284273733',
#           'entry.1548375218',
#           'entry.313224238',
#           'entry.1471195366',
#           'entry.1881504976',
#       ]
#                   
#       subdivision_time_data = {}
#       for idx, subdivision in enumerate(subdivisions_order):
#           if subdivision_times[subdivision] != "00:00:00":
#               hours, minutes, seconds = subdivision_times[subdivision].split(':')
#                   
#               subdivision_time_data[f"{subdivisions_entry_ids[idx]}_hour"] = hours
#               subdivision_time_data[f"{subdivisions_entry_ids[idx]}_minute"] = minutes
#               subdivision_time_data[f"{subdivisions_entry_ids[idx]}_second"] = seconds
#                   
#       return subdivision_time_data  
#       response = requests.post('https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/formResponse', data=form_data)
#   return response
#
#def handle_captcha(settings_data, max_retries=2):
#   for page in range(1, 3):  # Loop over the two pages
#       for _ in range(max_retries):
#           response = requests.get('https://docs.google.com/forms/d/e/1FAIpQLSecJZZIkatFAGCOrKws0HvTLJfVfLiTT9vcs3EyWjt8NpA_Vw/viewform')
#           soup = BeautifulSoup(response.text, 'html.parser')
#           captcha_code = extract_captcha_code(soup)
#           response = submit_form(page, captcha_code, settings_data)
#           
#           if response.status_code == 200:
#               print("Page {} submitted successfully".format(page))
#               break
#           else:
#               print("Error submitting page {}, retrying...".format(page))
#       else:
#           print("Failed to submit page {} after {} tries".format(page, max_retries))
#           
#def parse_time(time_string):
#   dt = datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S')
#   return {
#       'year': str(dt.year),
#       'month': str(dt.month).zfill(2),
#       'day': str(dt.day).zfill(2),
#       'hour': str(dt.hour).zfill(2),
#       'minute': str(dt.minute).zfill(2),
#   }
#   
#def calculate_duration(duration_string):
#   hours, minutes, _ = duration_string.split(':')
#   return {
#       'hours': str(int(hours)).zfill(2),
#       'minutes': str(int(minutes)).zfill(2),
#   }
#   
#def has_subdivision(subdivision_times):
#   for time in subdivision_times.values():
#       if time != '00:00:00':
#           return 'Yes'
#   return 'No'
#   
## Load your JSON data
#with open('settings_data.json') as f:
#   settings_data = json.load(f)
#
#with open('patrol_log_data.json') as f:
#   patrol_log_data = json.load(f)
#   
## Process your JSON data
#patrol_log_data['start_time'] = parse_time(patrol_log_data['start_time'])
#patrol_log_data['end_time'] = parse_time(patrol_log_data['end_time'])
#patrol_log_data['duration'] = calculate_duration(patrol_log_data['duration'])
#   
#handle_captcha(settings_data)
#

    
# Run the instance in a loop
