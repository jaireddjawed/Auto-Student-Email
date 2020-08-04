from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

# permissions needed from google account to access spreadsheet
scope = [
  'https://spreadsheets.google.com/feeds',
  'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join('credentials.json'), scope)
client = authorize(creds)

# open settings file
settings_file = open(os.path.join('settings.json'), 'r')
SETTINGS = json.load(settings_file)

# find the worksheet in google drive by its name
SHEET_TITLE = SETTINGS['sheet_title']

# student roster is the second sheet
ROSTER_SHEET = 1
sheet = client.open(SHEET_TITLE).worksheets()[ROSTER_SHEET]

from numpy import array

students = array(sheet.get_all_values())

# students are listed starting in the third row of the sheet
START_ROW = 2

for i in range(START_ROW, len(students)):
  # the column of the name of the student is the third column
  NAME_INDEX = 2
  student_name = students[i][NAME_INDEX].split(' ')[0]

  # student email is fourth column
  EMAIL_INDEX = 3
  student_email = students[i][EMAIL_INDEX]

  email_body_file = open(os.path.join('./templates/weekly_email.html'), 'r')
  email_body = email_body_file.read()

  # replace contents in template with student and tutor info
  email_body = email_body.replace('{{name}}', student_name)
  email_body = email_body.replace('{{calendly_link}}', SETTINGS['calendly_link'])
  email_body = email_body.replace('{{tutor_name}}', SETTINGS['tutor_name'])

  import sendgrid
  from sendgrid.helpers.mail import *

  sg = sendgrid.SendGridAPIClient(api_key=SETTINGS['sendgrid_key'])
  from_email = Email(SETTINGS['email'], SETTINGS['tutor_name'])
  to_email = To(student_email)

  subject = "Coding Bootcamp: Tutorial Available"
  content = Content("text/html", email_body)

  # Emails need to always CC centraltutorsupport
  cc_email = Email('centraltutorsupport@bootcampspot.com')

  p = Personalization()
  p.add_to(to_email)
  p.add_cc(cc_email)

  # send out the weekly email to the student
  mail = Mail(from_email, to_email, subject, content)
  mail.add_personalization(p)

  response = sg.client.mail.send.post(request_body=mail.get())

  # print out whether the email was sent successfully
  print(email_body)

  print(response.status_code)
  print(response.body)
  print(response.headers)

  settings_file.close()
  email_body_file.close()
