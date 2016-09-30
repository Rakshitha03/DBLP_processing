# import openreview
import dblp


# Let's start by initializing the Client with our username, password, and base URL
# openreview_client = openreview.Client(username='rbhat@cs.umass.edu', password='1234567890',
#                                       baseurl='http://openreview.net')
# Get the list of accepted reviewers
# reviewers = openreview_client.get_group('ICLR.cc/2017/conference/reviewers')
# print reviewers

# For the time being we are using the csv file given my melisa. Later we need
# to get reviewers from here.
reviewersInfo = {}

# reading csv file
fp = open("./iclr_accepted_reviewers.csv")
for eachLine in fp.readlines():
    firstName, lastName, emailID = eachLine.split(',')
    name = firstName + " " + lastName
    if name not in reviewersInfo:
        reviewersInfo[name] = {'emailID': emailID.strip()}
        authors = dblp.search(name)
        if authors:
            reviewersInfo[name]['publications'] = authors[0].publications

print reviewersInfo['Marc Lanctot']
