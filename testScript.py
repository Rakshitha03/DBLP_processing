import openreview
import dblp
import json
# Let's start by initializing the Client with our username, password, and base URL
openreview_client = openreview.Client(username='aditya.srinivasan.is@gmail.com', password='12345678', baseurl='http://openreview.net')

# Get the list of accepted reviewers
reviewers = openreview_client.get_group('ICLR.cc/2017/conference/reviewers')
#print reviewers

reviewersInfo = {}

#reading csv file
fp = open("../data/iclr_accepted_reviewers.csv")
for eachLine in fp.readlines():
    firstName, lastName, emailID = eachLine.split(',')
    name = firstName+" "+lastName
    if name not in reviewersInfo:
	reviewersInfo[name] = {'emailID':emailID.strip()}
	authors = dblp.search(name)
	if authors:	
		reviewersInfo[name]['publications'] = authors[0].publications 

print reviewersInfo['Marc Lanctot']

 
