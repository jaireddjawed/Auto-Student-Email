from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = [
  'https://spreadsheets.google.com/feeds',
  'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.

SHEET_TITLE = 'Tutor Tracking <Jaired Jawed>'
ROSTER_SHEET = 1
sheet = client.open(SHEET_TITLE).worksheets()[ROSTER_SHEET]

from numpy import array

students = array(sheet.get_all_values())

NAME_INDEX = 2
EMAIL_INDEX = 3

for i in range(2, len(students)):
  student_name = students[i][NAME_INDEX].split(' ')[0]
  student_email = students[i][EMAIL_INDEX]

  email_body = open('./templates/weekly_email.html').read()
  email_body = email_body.replace('{{name}}', student_name)
  email_body = email_body.replace('{{calendly_link}}', 'https://calendly.com/jairedjawed/tutorial-session')

  import sendgrid
  from sendgrid.helpers.mail import *

  sg = sendgrid.SendGridAPIClient(api_key='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')
  from_email = Email("me@jairedjawed.com", "Jaired Jawed")
  to_email = To(student_email)

  subject = "Coding Bootcamp: Tutorial Available"
  content = Content("text/html", email_body)

  cc_email = Email('centraltutorsupport@bootcampspot.com')

  p = Personalization()
  p.add_to(to_email)
  p.add_cc(cc_email)

  mail = Mail(from_email, to_email, subject, content)
  mail.add_personalization(p)

  response = sg.client.mail.send.post(request_body=mail.get())

  print(email_body)

  print(response.status_code)
  print(response.body)
  print(response.headers)
