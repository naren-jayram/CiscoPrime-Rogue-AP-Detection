import json
import commands
import datetime
import time
import sys
import csv
import re
import netrc
from jira import JIRA

# Configuration
cisco_prime_ip = '' #Cisco Prime IP or Hostname
jira_host_name = '' #JIRA IP or Hostname
jira_project = '' # JIRA project name
# End of Configuration

#Cisco Prime URL
url = "https://%s/webacs/api/v2/op/reportService/report.json?reportTitle=<report_title_name>" %cisco_prime_ip
secrets = netrc.netrc()
username,password,account = secrets.authenticators('myCiscoPrime')
auth = "authorization: Basic %s"%password
cache = "cache-control: no-cache"

#Below is a plain text authorization (alternative for above authentication/ authorization), which is bad from security perspective
#auth = "authorization: Basic <base64 encoded 'username:password'>"


# To get today's date
now = datetime.datetime.now()
today = now.strftime('%Y%m%d')
jiraDate = now.strftime('%Y-%m-%d')

curlCmd = "curl -k -X GET \'%s\' -H \'%s\' -H \'%s\' > %s.json" %(url, auth, cache, today)

output = commands.getoutput(curlCmd)

with open("%s.json" %today, 'r') as dataFile:
    jsonToday = json.load(dataFile)

# To get yesterday's date
curTime = datetime.datetime.now()
lastDayTime = curTime - datetime.timedelta(days = 1)
yesterday = lastDayTime.strftime('%Y%m%d')


with open("%s.json" %yesterday, 'r') as dataFile1:
    jsonYesterday = json.load(dataFile1)

# Troubleshooting purpose
tshoot = open("troubleshoot.txt", "a+")

reportDataDTO = jsonToday['mgmtResponse']['reportDataDTO']
reportDataDTO1 = jsonYesterday['mgmtResponse']['reportDataDTO']


macValue = {}
for dto in reportDataDTO:
    dataRowList = dto['dataRows']['dataRow']
    if not dataRowList:
        print "Today's JSON is empty"
        tshoot.write("Today's JSON is empty! : %s\r\n" %today)
        tshoot.close()
        sys.exit()
    for drow in dataRowList:
        datavalues = []
        for entry in drow['entries']['entry']:
            datavalues.append(entry['dataValue'])
        macValue.update({drow['entries']['entry'][1]['dataValue']: datavalues})

macValue1 = {}
for dto1 in reportDataDTO1:
    dataRowList1 = dto1['dataRows']['dataRow']
    if not dataRowList1:
        print "Yesterday's JSON is empty"
        tshoot.write("Yesterday's JSON is empty! : %s\r\n" %today)
        tshoot.close()
        sys.exit()
    for drow1 in dataRowList1:
        datavalues1 = []
        for entry in drow1['entries']['entry']:
            datavalues1.append(entry['dataValue'])
        macValue1.update({drow1['entries']['entry'][1]['dataValue']: datavalues1})


# Below code will be used for CSV output
with open('PersistentAccessPoints.csv', 'w+') as persistent_AP:
    csvwriter = csv.writer(persistent_AP)
    headerList = ['Last Seen Time','Rogue MAC Address','Detecting AP Name','Radio Type','Controller IP Address','Detecting AP Map Location','SSID','Severity Score','Classification Name','Alarm State','Classification Type','On Network', 'Encryption','Switch IP Address','Switch Name','Port Description']
    csvwriter.writerow(headerList)

    MACS =[]
    for key, val in macValue.items():
        if key in macValue1:
            print (key)
            csvwriter.writerow(macValue[key])
            MACS.append(key)


# Exit if no persistent APs found. Below logic is based on MAC
if not MACS:
        print "No matching MACs"
        tshoot.write("No matching MACs found! : %s\r\n" %today)
        tshoot.close()
        sys.exit()


# Below code will be used for JIRA ticket creation 

jira_url = {'server': 'https://%s/jira' %jira_host_name}
secrets = netrc.netrc()
username,password,account = secrets.authenticators('myJira')
jira = JIRA(jira_url, basic_auth=('%s'%username,'%s'%password))


#Below code is an alternative for above authentication. This is poor from security perspective due to credential leakage.
#options = {'server': 'https://<Jira_Hostname/jira'}
#jira = JIRA(options, basic_auth=('username','password'))

issueDict = {
        'project': {'key': '%s' %jira_project},
        'summary': "Persistent Rogue Access Points: %s" %jiraDate,
        'description': 'Please open the attached spreadsheet to find Persistent Rogue Access Points',
        'issuetype': {'name': 'Investigation'},
        'labels': ["Persistent-Rogue-APs"]
        }

newIssue = jira.create_issue(fields=issueDict)
print (newIssue)


# upload file from `/some/path/attachment.txt`
jira.add_attachment(issue=newIssue, attachment='PersistentAccessPoints.csv')
