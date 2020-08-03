from pyicloud import PyiCloudService
import click

api = PyiCloudService('jairedjawed@icloud.com', '&WOMEfF$k7I36z4^9g')

if api.requires_2sa:
  print('Two-factor authentication is required. Please select a device.')

  devices = api.trusted_devices

  for i in range(len(devices)):
    print(str(i) + '. ' + devices[i]['phoneNumber'])

  deviceId = int(input('Enter the device id: '))
  device = devices[deviceId]

  if not api.send_verification_code(device):
    print('Failed to send verification code.')
    exit(1)

  while True:
    code = click.prompt('Enter the verification code: ')
    if not api.validate_verification_code(device, code):
      break

from datetime import datetime, timedelta
from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials
from numpy import array
import pytz

# how to change day for next month
next_day = datetime.now()
next_day = datetime.now() + timedelta(days=1)

# get all events for the next day from icloud calendar
events = api.calendar.events(next_day, next_day) or []

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

for i in range(len(events)):
  is_bootcamp_session = events[i]['title'].find('Tutorial Session') != -1
  is_event_canceled = events[i]['title'].find('Canceled') == 1

  events_file = open('events.txt', 'r')
  already_emailed = events_file.read().find(events[i]['guid']) != -1

  if is_bootcamp_session and not is_event_canceled and not already_emailed:
    events_file.close()

    # Save the session's event id to make sure we don't email them again
    events_file = open('events.txt', 'a')
    events_file.write(events[i]['guid'] + '\n')
    events_file.close()

    description_lines = events[i]['description'].splitlines()

    # get the name and email from the description
    student_first_name = description_lines[1].split(' ')[1]
    student_email = description_lines[2].split('Invitee Email: ')[1]

    timezone = None
    for j in range(len(students)):
      if student_email == students[j][3]:
        timezone = students[j][5]

    session_date = events[i]['localStartDate']
    session_date = datetime.now().replace(year=session_date[1], month=session_date[2], day=session_date[3], hour=session_date[4], minute=session_date[5])
    session_date = session_date.astimezone(pytz.timezone('US/' + timezone))
    session_date = session_date.strftime('%a %b %d %I:%M %p') + ' ' + timezone + ' Time'

    read_email_body = open('./templates/session_confirmation.html')
    email_body = read_email_body.read()
    email_body = email_body.replace('{{name}}', student_first_name)
    email_body = email_body.replace('{{time}}', session_date)
    email_body = email_body.replace('{{zoom_link}}', 'https://zoom.us/j/5291031083?pwd=WWJBWndUM0tTWVIyejZmaGNPQUZXUT09')

    import sendgrid
    from sendgrid.helpers.mail import *

    sg = sendgrid.SendGridAPIClient(api_key='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')
    from_email = Email("me@jairedjawed.com", "Jaired Jawed")
    to_email = To(student_email)
    subject = "Coding Bootcamp Tutorial Confirmation " + session_date
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

    read_email_body.close()
