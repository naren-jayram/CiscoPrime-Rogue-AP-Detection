## Cisco Prime - Rogue Access Point Detection
Automation of the process to detect rogue access points by identifying all the foreign access points (*AP that does not belongs to organization's wireless network Infrastructure*) that resides in a given network for more than 24 hours,  followed by raising a JIRA ticket under a given project to the respective stakeholders.

### Prerequisites 
* You should have access to CISCO Prime infrastructure (at least to pull the report)
* You should have privilege to create tickets in JIRA
* Report configurations should exist in Cisco Prime to pull the rogue AP details from approprate locations /regions. If it doesn't exist, you should create one using GUI or else ask someone who has privilege
* *netrc* file should remain here: /~/.netrc
* Make sure "netrc" file has permission, *700*
* Both Cisco Prime and Jira credentials should reside in 'netrc' file. Refer the "netrc" file template
* Fill the respective details in *Configuration* section of the code in *rogueAPDetection.py*

### Usage
```
python rogueAPDetection.py
```
### Courtesy
Cisco Prime Infrastructure API

**Note:**
This code is written in Python v2.7