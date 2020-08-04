# Auto Student Email

Automatically and easily send out session confirmation emails, new student emails, and session confirmation emails to students.

# Prerequisites
* [iCloud](https://icloud.com) Account
* [Calendly](https://calendly.com) Account
* [Google](https://google.com) Account
* [Sendgrid](https://www.sendgrid.com) Account
* Have [Python 3](https://www.python.org/) and [Pip](https://pip.pypa.io/en/stable) Installed

# Setup
### Connect your iCloud Account to Calendly
* Go to your Calendly Account
* On the ```Account``` tab, click ```Calendar Connections```
* Connect your iCloud Calendar to Calendly

### Clone Project and Install Required Libraries
* Clone this project to your machine
* Run this command in your terminal
```
pip3 install pyicloud numpy gspread oauth2client
```

### Create Google Cloud Platform Project

* Create a [Google Cloud Platform Project](https://console.cloud.google.com/) and enable the Google Drive and Google Sheets APIs
* Create A [Service Account Key](https://console.cloud.google.com/apis/credentials/serviceaccountkey)
* From the Service account list, click ```New Service Account```
* Enter a service account name and select "Owner" as the role
* Click ```Create```
* A JSON file should download to your computer. Change the name of the file to ```credentials.json``` and put it inside the top level of your project folder
* Share your Tutor Tracking spreadsheet with the ```client_email``` that's inside of ```credentials.json```

### Create Sendgrid API Key
* On the Sendgrid dashboard, click "Settings" and then click "API Keys"
* Create an API key and save it in ```settings.json```
* To prevent your messages from being sent into spam, [verify your domain](https://sendgrid.com/docs/ui/account-and-settings/how-to-set-up-domain-authentication/)

### Settings.json
* Change the default settings in ```settings.json``` to your custom settings

# Usage
* To send an email to a new student, add them to the last row of your roster and run the following command in your terminal
```
python3 new_student.py
```
* To send out your weekly email blast, run the following command in your terminal
```
python3 weekly_email.py
```
* To send out your session emails for the following day, run the following command in your terminal
```
python3 session_confirmation.py
```

* When you run the script for the first time, it will ask to send a code to the phone number associated with your iCloud account.
Select your phone number and wait until Apple calls you and gives you the code. **Do not enter the code that was given to you from your Apple device. It will not work.**

* The script will automatically adjust the session time to the student's time zone.

# Automatically Run Scripts (macOS Only)

* Open the ```Calendar``` Application
* Create a new event
* Name the event and click under ```alert```, select ```Open File```
* Choose the ```Automator``` File