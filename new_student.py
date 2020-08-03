from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials
from numpy import array

scope = [
  'https://spreadsheets.google.com/feeds',
  'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
client = authorize(creds)

SHEET_TITLE = 'Tutor Tracking <Jaired Jawed>'
ROSTER_SHEET = 1
sheet = client.open(SHEET_TITLE).worksheets()[ROSTER_SHEET]
students = array(sheet.get_all_values())
new_student = students[len(students) - 1]

student_first_name = new_student[2].split(' ')[0]
student_email = new_student[3]

email_body = open('./templates/new_student.html').read()
email_body = email_body.replace('{{name}}', student_first_name)
email_body = email_body.replace('{{calendly_link}}', 'https://calendly.com/jairedjawed/tutorial-session')

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

sg = SendGridAPIClient(api_key='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')
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
