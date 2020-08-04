from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials
from numpy import array
import json
import os

# permissions needed from google account to access spreadsheet
scope = [
  'https://spreadsheets.google.com/feeds',
  'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
client = authorize(creds)

# open settings file
settings_file = open(os.path.join('./settings.json'), 'r')
SETTINGS = json.load(settings_file)

# find the worksheet in google drive by its name
# student roster is the second sheet
ROSTER_SHEET = 1
sheet = client.open(SETTINGS['sheet_title']).worksheets()[ROSTER_SHEET]

# get the most recent student on the roster
students = array(sheet.get_all_values())
new_student = students[len(students) - 1]

student_first_name = new_student[2].split(' ')[0]
student_email = new_student[3]

email_body_file = open(os.path.join('./templates/new_student.html'), 'r')
email_body = email_body_file.read()

# replace contents in template with student and tutor info
email_body = email_body.replace('{{name}}', student_first_name)
email_body = email_body.replace('{{calendly_link}}', SETTINGS['calendly_link'])
email_body = email_body.replace('{{tutor_name}}', SETTINGS['tutor_name'])

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

sg = SendGridAPIClient(api_key=SETTINGS['sendgrid_key'])
from_email = Email(SETTINGS['email'], SETTINGS['tutor_name'])
to_email = To(student_email)

subject = "Coding Bootcamp: Tutorial Available"
content = Content("text/html", email_body)

# Emails need to always CC centraltutorsupport
cc_email = Email('centraltutorsupport@bootcampspot.com')

p = Personalization()
p.add_to(to_email)
p.add_cc(cc_email)

# send an email to the new student
mail = Mail(from_email, to_email, subject, content)
mail.add_personalization(p)

response = sg.client.mail.send.post(request_body=mail.get())

print(email_body)
print(response.status_code)
print(response.body)
print(response.headers)

email_body_file.close()
settings_file.close()
