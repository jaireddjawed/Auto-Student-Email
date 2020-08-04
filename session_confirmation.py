from pyicloud import PyiCloudService
import click
import json
import os

settings_file = open(os.path.join('./settings.json'), 'r')
SETTINGS = json.load(settings_file)

api = PyiCloudService(SETTINGS['icloud_email'], SETTINGS['icloud_password'])

# Authenticate into icloud account
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
    if api.validate_verification_code(device, code):
      break
    else:
      print('Invalid verification code.')

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

# permissions needed from google account to access spreadsheet
scope = [
  'https://spreadsheets.google.com/feeds',
  'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
client = authorize(creds)

# the student roster is the second sheet
ROSTER_SHEET = 1

sheet = client.open(SETTINGS['sheet_title']).worksheets()[ROSTER_SHEET]
students = array(sheet.get_all_values())

for i in range(len(events)):
  # we can check if its a bootcamp session depending on the event's title
  is_bootcamp_session = events[i]['title'].find('Tutorial Session') != -1
  # make sure that the session wasn't canceled
  is_event_canceled = events[i]['title'].find('Canceled') == 1

  # add the event to the events.txt file so we don't email the student again about the same session
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

    # change the time to the student's timezone
    session_date = events[i]['localStartDate']
    session_date = datetime.now().replace(year=session_date[1], month=session_date[2], day=session_date[3], hour=session_date[4], minute=session_date[5])
    session_date = session_date.astimezone(pytz.timezone('US/' + timezone))
    session_date = session_date.strftime('%a %b %d %I:%M %p') + ' ' + timezone + ' Time'

    email_body_file = open('./templates/session_confirmation.html')
    email_body = email_body_file.read()

    # replace the template with student and tutor info
    email_body = email_body.replace('{{name}}', student_first_name)
    email_body = email_body.replace('{{time}}', session_date)
    email_body = email_body.replace('{{zoom_link}}', SETTINGS['zoom_link'])
    email_body = email_body.replace('{{zoom_password}}', SETTINGS['zoom_password'])
    email_body = email_body.replace('{{tutor_name}}', SETTINGS['tutor_name'])

    import sendgrid
    from sendgrid.helpers.mail import *

    sg = sendgrid.SendGridAPIClient(api_key=SETTINGS['sendgrid_key'])
    from_email = Email(SETTINGS['email'], SETTINGS['tutor_name'])

    to_email = To(student_email)

    subject = "Coding Bootcamp: Tutorial Confirmation " + session_date
    content = Content("text/html", email_body)

    # Always CC central support when emailing students
    cc_email = Email('centraltutorsupport@bootcampspot.com')

    p = Personalization()
    p.add_to(to_email)
    p.add_cc(cc_email)

    # send the session confirmation email to the student
    mail = Mail(from_email, to_email, subject, content)
    mail.add_personalization(p)

    response = sg.client.mail.send.post(request_body=mail.get())

    print(email_body)
    print(response.status_code)
    print(response.body)
    print(response.headers)

    email_body_file.close()
