#!/home/hadoop/ops_scripts/ops_python2.7/bin/python

# This script was written to check if the CHANNEL_PANEL_4M jobs # have completed. It sends a mail everyday at 9:30am PST to indicate success # or failure.
#
# last update: February 6, 2018

import MySQLdb
import sys
from datetime import datetime, time, date, timedelta, tzinfo; import smtplib


####### for testing purposes
#test = 'y'
test = 'n'

 
###### define some variables
sender = 'hadoop@ip-172-34-26-17.com'


# a job only needs to be defined here; no other variables need to be set in order to add another job for monitoring #job = "'UPLOAD_CHANNEL_PANEL_4M_CP_V1_PANEL', 'UPLOAD_4MCHANNEL_PANEL', 'UPLOAD_5MV1_PANEL'"

job = "'UPLOAD_CHANNEL_PANEL_4M_CP_V1_BANK_PANEL', 'UPLOAD_CHANNEL_PANEL_4M_CP_V1_CARD_PANEL', 'UPLOAD_4MCHANNEL_PANEL'"
title = "Channel Panel - Delayed 4M Upload Status"

###### print statements for the log file
print "Starting check_channel_panel.py...\n"
print "The date is", now_time.strftime('%Y-%m-%d %H:%M:%S') print "yesterday's date is", yesterday print "\n"

###### database connection and query
print "Starting DB query...\n"

db = MySQLdb.connect(user='panelgen', passwd='p@nelgen2015', host='127.0.0.1', db='PANEL_CONSOLIDATION') cur = db.cursor()

query = "select WTD.CONTAINER,TSK.PANEL_DATE,TSK.STATUS,WTD.WORKFLOW_TASK_NAME,TSK.START_TIME,TSK.END_TIME \ FROM DAILY_WORKFLOW_TASKS TSK JOIN WORKFLOW_TASK_DETAILS WTD ON WTD.WORKFLOW_TASK_ID = TSK.WORKFLOW_TASK_ID \ WHERE PANEL_IDENTIFIER = 'MPANEL' and WORKFLOW_NAME = 'MPANEL_SLICING' AND PANEL_DATE = '" + yesterday + "' AND \ WORKFLOW_TASK_NAME in (" + job + ") ;"

print query
print "\n"

cur.execute(query)

for row in cur.fetchall():
        key_name = row[3] + '.' + row[0]
        # key_name will look like UPLOAD_5MV1_PANEL.BANK, for example
        WF_jobs[key_name] = list(row)
        if row[2] == 'SUCCESS' and row[4] and row[5]:
                WF_jobs[key_name][4] = row[4].strftime('%H:%M:%S')
                WF_jobs[key_name][5] = row[5].strftime('%H:%M:%S')
                WF_jobs[key_name].append('normal_font_color')
        else:
                WF_jobs[key_name][4] = 'N/A'
                WF_jobs[key_name][5] = 'N/A'
                WF_jobs[key_name].append('alert_font_color')

cur.close()


print "\nclosed DB connection\n" 

###### set mail fields based on success or failure for k, v in WF_jobs.items():
#       print k, v
        if v[2] == 'SUCCESS':
                print k, "completed successfully\n"
                recip = 'dataops-panels-core@yodlee.com'
#               recip = 'cpedro@yodlee.com'
                cc = 'cpedro@yodlee.com'
                subject = "Channel Panel - Delayed 4M Upload Status - Success"
                end_msg = "Both BANK and CARD jobs have completed successfully."
        else:
                print k, "did not complete successfully\n"
                recip = 'ydo@yodlee.com'
                cc = 'cpedro@yodlee.com,RMalla@yodlee.com,skoshy@yodlee.com'
                subject = "Channel Panel - Delayed 4M Upload Status - ALERT - Not Completed"
                end_msg = "One or both jobs have not completed. Please check!"
                break

print 'Loop thru again to verify all fields'


for k, v in WF_jobs.items():
        print k, v

###### for testing purposes
if test == 'y':
        recip = 'cpedro@yodlee.com'
        cc = 'cpedro@yodlee.com'

###### print some variables to verify

print "\nPrinting the mail fields...\n"
print recip
print cc
print subject
print end_msg

print "\nGot the main variables set; moving on\n"

###### define html headers and email body

msg_body = """From: PC Cluster <hadoop@ip-172-31-16-11.com>
To: <""" + recip + """>
CC: <""" + cc + """>
MIME-Version: 1.0
Content-type: text/html
Subject: """
msg_body += subject
msg_body += """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
   <style type="text/css">
        a {color: #d80a3e;}
        body, #header h1, #header h2, p {margin: 0; padding: 0;}
        #main {border: 1px solid #cfcece;}
        #header h1 {color: #ffffff !important; font-family: "Lucida Grande", sans-serif; font-size: 24px; margin-bottom: 0!important; padding-bottom: 0; }
        #header p {color: #ffffff !important; font-family: "Lucida Grande", "Lucida Sans", "Lucida Sans Unicode", sans-serif; font-size: 12px;  }
        h5 {margin: 0 0 0.8em 0;}
        h5 {font-size: 18px; color: #444444 !important; font-family: Arial, Helvetica, sans-serif; }
        p {font-size: 12px;  font-family: "Lucida Grande", "Lucida Sans", "Lucida Sans Unicode", sans-serif; line-height: 1.5;}
        tr.alert_font_color { color: #ff0000 }
        tr.normal_font_color { color: #19191a }
   </style>
</head>

<body>

<br><br>

<table id="main" width="1000" align="center" cellpadding="0" cellspacing="15" bgcolor="ffcc99">
    <tr>
      <td>
        <table id="header" cellpadding="10" cellspacing="0" align="center" bgcolor="8fb3e9">
          <tr>
            <td width="570" align="center"  bgcolor="#3399ff"><h1>""" + title + """</h1></td>
          </tr>
        </table>
      </td>
    </tr>

    <tr>
      <td>
        <table cellpadding="0" cellspacing="0" align="center">
          <tr>
            <td width="120">
              <p>Container</p>
            </td>
            <td width="120">
              <p>Panel Date</p>
            </td>
            <td width="120">
              <p>Status</p>
            </td>
            <td width="400">
              <p>Workflow</p>
            </td>
            <td width="170">
              <p>Start Time (UTC)</p>
            </td>
            <td width="170">
              <p>End Time (UTC)</p>
            </td>
          </tr>"""

# this goes through the dict values and prints each line of the table # v[6] is the font color - red if it didn't succeed, black otherwise for k, v in sorted(WF_jobs.items()):

        msg_body += '<tr class=' + '"' + v[6] + '">'
        msg_body += '<td><p>' + v[0] + '</p></td>'
        msg_body += '<td><p>' + v[1] + '</p></td>'
        msg_body += '<td><p>' + v[2] + '</p></td>'
        msg_body += '<td><p>' + v[3] + '</p></td>'
        msg_body += '<td><p>' + v[4] + '</p></td>'
        msg_body += '<td><p>' + v[5] + '</p></td>'
        msg_body += '</tr>'
        msg_body += "\n"
msg_body += """</table>
      </td>
    </tr>
</td></tr></table><!-- wrapper -->
<br><br> <p>"""

msg_body += end_msg
msg_body += """</p><br><p>Thanks,<br>Data Ops</p>"""
msg_body += """</body>
</html>
"""

# use this for troubleshooting purposes

print msg_body

try:
   smtpObj = smtplib.SMTP('localhost')
   smtpObj.sendmail(sender, recip, msg_body)
   print "Successfully sent email\n"
except smtplib.SMTPException:
   print "Error: unable to send email"


print "End of script output."