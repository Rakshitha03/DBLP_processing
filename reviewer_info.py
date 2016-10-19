import dblp
import inspect
import json

# reading csv file containing the email id, first name, last name
fp = open("./iclr_accepted_reviewers.csv")
no_name = 0
more_than_one = 0
no_hits = 0
author_disambiguation = {}
no_hits_names = []
no_name_list = []
for eachLine in fp.readlines():
    emailId, firstName, lastName = eachLine.split(',')
    name = firstName + " " + lastName.strip()
    file_name = firstName + "_" + lastName.strip()
    if name == '' or name == ' ':
        print emailId
        no_name += 1
        no_name_list.append(emailId)
    else:
        try:
            authors = dblp.search(name)
        except Exception as e:
            authors = []
            print "DBLP parsing error for ", name
        if authors:
            if len(authors) > 1:
                print "More than one authors found! "
                more_than_one += 1
                author_disambiguation[name] = []
                for ath in authors:
                    author_disambiguation[name].append(ath)
                author = authors[0]
                print name + ' : ' + unicode(author.name).encode('utf-8')
                if len(author.publications) > 0:
                    print len(author.publications)
                    ''' There's something fishy about this publications.
                    When I extract their title, somehow it seems to give me DBLP parsing error.
                    Check the reviewer_info.txt file. For the same authors for
                    which it printed info that time, now it doesnt even detect
                    them :/ Very strange
                    '''
                    '''This is the part which might probably be giving an error.. '''
                    fp = open("./Reviewer_Info/" + file_name, 'a')
                    publications_set = set()
                    for publication in author.publications:
                        try:
                            pub_title = publication.title
                            publications_set.add(pub_title)
                        except Exception as e:
                            continue
                    for title in publications_set:
                        fp.write(title + '\n')
                    fp.close()
                    ''' Problematic code ends here'''
            else:
                author = authors[0]
                print name + ' : ' + unicode(author.name).encode('utf-8')
                if len(author.publications) > 0:
                    print len(author.publications)
                    fp1 = open("./Reviewer_Info/" + file_name, 'a')
                    publications_set = set()
                    for publication in author.publications:
                        try:
                            pub_title = publication.title
                            publications_set.add(pub_title)
                            # fp1.write(publication.title + '\n')
                            # print "Came here: ", file_name
                        except Exception as e:
                            continue
                    for title in publications_set:
                        fp1.write(title + '\n')
                    fp1.close()
        else:
            print "No hit in dblp for ", name
            no_hits_names.append(name)
            no_hits += 1

print "Stats: "
print "No names for: ", no_name
print "No names list: ", no_name_list
print "More than 1 author hits for ", more_than_one
print "No hits for ", no_hits
print "No hit list: ", no_hits_names
#             # These people with non ascii names -_-
#             try:
#                 file_pointer_2.write("\nAuthor:\t" + authors[
#                     0].name + "\nEmail:\t" + emailID + "Publication List:\n")
#             except:
#                 file_pointer_2.write(
#                     "\nAuthor:\t" + name + "\nEmail:\t" + emailID + "Publication List:\n")
#             reviewersInfo[name]['publications'] = authors[0].publications
#             count = 1
#             for publication in reviewersInfo[name]['publications']:
#                 # Please can you try solving ascii encoding error for other
#                 # authors and publication title and email id! Don't seem to have
#                 #  the patience to solve it now.
#                 # Skipping it for the time being.
#                 try:
#                     file_pointer_2.write(str(
#                         count) + ") " + publication.title + "\nAuthors:" + ','.join(
#                         publication.authors) + "\n")
#                     count += 1
#                 except Exception:
#                     pass
#                     # Need to fix this
#                     # print(publication.title+"\t"+','.join(publication.authors)+"\n")
#         else:
#             file_pointer_1.write("\n" + name)
# file_pointer_1.close()
# file_pointer_2.close()
# '''
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
'''
    #print eachAuthObject.name
    print "\n"
    break

'''
'''
for each in authors:
    #print(each.__dict__)
    #print(each.homepages)
    for eachPub in each.publications:
        #print dir(eachPub)
        print eachPub.data
'''
