# import openreview
import dblp
import inspect
import json
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
'''
fp = open("./iclr_accepted_reviewers.csv")
file_pointer_1 = open("nilDBLPInfo.txt", "wb")
file_pointer_2 = open("ReviewerInfo", "wb")
for eachLine in fp.readlines():
    firstName, lastName, emailID = eachLine.split(',')
    name = firstName + " " + lastName
    if name not in reviewersInfo:
        reviewersInfo[name] = {'emailID': emailID.strip()}
        authors = dblp.search(name)
        if authors:
            file_pointer_2.write("*" * 15)
            # These people with non ascii names -_-
            try:
                file_pointer_2.write("\nAuthor:\t" + authors[
                    0].name + "\nEmail:\t" + emailID + "Publication List:\n")
            except:
                file_pointer_2.write(
                    "\nAuthor:\t" + name + "\nEmail:\t" + emailID + "Publication List:\n")
            reviewersInfo[name]['publications'] = authors[0].publications
            count = 1
            for publication in reviewersInfo[name]['publications']:
                # Please can you try solving ascii encoding error for other
                # authors and publication title and email id! Don't seem to have
                #  the patience to solve it now.
                # Skipping it for the time being.
                try:
                    file_pointer_2.write(str(
                        count) + ") " + publication.title + "\nAuthors:" + ','.join(
                        publication.authors) + "\n")
                    count += 1
                except Exception:
                    pass
                    # Need to fix this
                    # print(publication.title+"\t"+','.join(publication.authors)+"\n")
        else:
            file_pointer_1.write("\n" + name)
file_pointer_1.close()
file_pointer_2.close()
'''
authorData = dblp.search('Andrew McCallum')
for eachAuthObject in authorData:
    print eachAuthObject.__dict__
    print eachAuthObject.xml
    print eachAuthObject.urlpt
    print eachAuthObject.name
    print "Len of publications ", len(eachAuthObject.publications)
    count = 0
    publication_set = set()
    for publication in eachAuthObject.publications:
        try:

            publication_set.add(publication.title)
# print publication.title
        except:
            print publication.isbn
            print publication.data
        count += 1
    print "*"*10
    print "total count",count
    print len(publication_set)
    # print eachAuthObject.publications[2].isbn
    # print "----------------------------------------"
    # '''
    # for eachPub in eachAuthObject.publications:
    #     print eachPub.__dict__
    #     break
    # '''
    # print eachAuthObject.publications[2].data
    # print "----------------------------------------"
    # print eachAuthObject.publications[2].data.keys()

    #print eachAuthObject.name
    print "\n"
    break

'''
for each in authors:
    #print(each.__dict__)
    #print(each.homepages)
    for eachPub in each.publications:
        #print dir(eachPub)
        print eachPub.data
'''
