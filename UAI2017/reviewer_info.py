# import dblp
import inspect
import json
import os
from time import sleep

import requests
from lxml import etree
from collections import namedtuple

DBLP_BASE_URL = 'http://dblp.uni-trier.de/'
DBLP_AUTHOR_SEARCH_URL = DBLP_BASE_URL + 'search/author'

DBLP_PERSON_URL = DBLP_BASE_URL + 'pers/xk/{urlpt}'
DBLP_PUBLICATION_URL = DBLP_BASE_URL + 'rec/bibtex/{key}.xml'

class LazyAPIData(object):
    def __init__(self, lazy_attrs):
        self.lazy_attrs = set(lazy_attrs)
        self.data = None

    def __getattr__(self, key):
        if key in self.lazy_attrs:
            if self.data is None:
                self.load_data()
            return self.data[key]
        raise AttributeError, key

    def load_data(self):
        pass

class Author(LazyAPIData):
    """
    Represents a DBLP author. All data but the author's key is lazily loaded.
    Fields that aren't provided by the underlying XML are None.

    Attributes:
    name - the author's primary name record
    publications - a list of lazy-loaded Publications results by this author
    homepages - a list of author homepage URLs
    homonyms - a list of author aliases
    """
    def __init__(self, urlpt):
        self.urlpt = urlpt
        self.xml = None
        super(Author, self).__init__(['name','publications','homepages',
                                      'homonyms'])

    def load_data(self):
        resp = requests.get(DBLP_PERSON_URL.format(urlpt=self.urlpt))
        # TODO error handling
        xml = resp.content
        self.xml = xml
        root = etree.fromstring(xml)
        data = {
            'name':root.attrib['name'],
            'publications':[Publication(k) for k in
                            root.xpath('/dblpperson/dblpkey[not(@type)]/text()')],
            'homepages':root.xpath(
                '/dblpperson/dblpkey[@type="person record"]/text()'),
            'homonyms':root.xpath('/dblpperson/homonym/text()')
        }

        self.data = data

def first_or_none(seq):
    try:
        return next(iter(seq))
    except StopIteration:
        pass

Publisher = namedtuple('Publisher', ['name', 'href'])
Series = namedtuple('Series', ['text','href'])
Citation = namedtuple('Citation', ['reference','label'])

class Publication(LazyAPIData):
    """
    Represents a DBLP publication- eg, article, inproceedings, etc. All data but
    the key is lazily loaded. Fields that aren't provided by the underlying XML
    are None.

    Attributes:
    type - the publication type, eg "article", "inproceedings", "proceedings",
    "incollection", "book", "phdthesis", "mastersthessis"
    sub_type - further type information, if provided- eg, "encyclopedia entry",
    "informal publication", "survey"
    title - the title of the work
    authors - a list of author names
    journal - the journal the work was published in, if applicable
    volume - the volume, if applicable
    number - the number, if applicable
    chapter - the chapter, if this work is part of a book or otherwise
    applicable
    pages - the page numbers of the work, if applicable
    isbn - the ISBN for works that have them
    ee - an ee URL
    crossref - a crossrel relative URL
    publisher - the publisher, returned as a (name, href) named tuple
    citations - a list of (text, label) named tuples representing cited works
    series - a (text, href) named tuple describing the containing series, if
    applicable
    """
    def __init__(self, key):
        self.key = key
        self.xml = None
        super(Publication, self).__init__( ['type', 'sub_type', 'mdate',
                'authors', 'editors', 'title', 'year', 'month', 'journal',
                'volume', 'number', 'chapter', 'pages', 'ee', 'isbn', 'url',
                'booktitle', 'crossref', 'publisher', 'school', 'citations',
                'series'])

    def load_data(self):
        resp = requests.get(DBLP_PUBLICATION_URL.format(key=self.key))
        xml = resp.content
        self.xml = xml
        root = etree.fromstring(xml)
        publication = first_or_none(root.xpath('/dblp/*[1]'))
        if publication is None:
            raise ValueError
        data = {
            'type':publication.tag,
            'sub_type':publication.attrib.get('publtype', None),
            'mdate':publication.attrib.get('mdate', None),
            'authors':publication.xpath('author/text()'),
            'editors':publication.xpath('editor/text()'),
            'title':first_or_none(publication.xpath('title/text()')),
            'year':int(first_or_none(publication.xpath('year/text()'))),
            'month':first_or_none(publication.xpath('month/text()')),
            'journal':first_or_none(publication.xpath('journal/text()')),
            'volume':first_or_none(publication.xpath('volume/text()')),
            'number':first_or_none(publication.xpath('number/text()')),
            'chapter':first_or_none(publication.xpath('chapter/text()')),
            'pages':first_or_none(publication.xpath('pages/text()')),
            'ee':first_or_none(publication.xpath('ee/text()')),
            'isbn':first_or_none(publication.xpath('isbn/text()')),
            'url':first_or_none(publication.xpath('url/text()')),
            'booktitle':first_or_none(publication.xpath('booktitle/text()')),
            'crossref':first_or_none(publication.xpath('crossref/text()')),
            'publisher':first_or_none(publication.xpath('publisher/text()')),
            'school':first_or_none(publication.xpath('school/text()')),
            'citations':[Citation(c.text, c.attrib.get('label',None))
                         for c in publication.xpath('cite') if c.text != '...'],
            'series':first_or_none(Series(s.text, s.attrib.get('href', None))
                      for s in publication.xpath('series'))
        }

        self.data = data

def search(author_str):
    resp = requests.get(DBLP_AUTHOR_SEARCH_URL, params={'xauthor':author_str})
    try:
        root = etree.fromstring(resp.content)
    except:
        print resp.content
        import pdb
        pdb.set_trace()
        print 'z'
    return [Author(urlpt) for urlpt in root.xpath('/authors/author/@urlpt')]
'''
So I copied the dblp code into this file. I wanted to check what was going
wrong. It was a protected file and it was some archived file and so on.
Didnt have the patience to extract, find file and edit, instead copied
everything here. Will clean up code when we have to :P Till then let it be xD
'''

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
    if os.path.isfile("/home/rakshitha03/OpenReview/DBLP_processing/Reviewer_Info/"+file_name):
        print file_name + " Exists"
        continue


    if name == '' or name == ' ':
        print emailId
        no_name += 1
        no_name_list.append(emailId)
    else:
        try:
            sleep(3)
            authors = search(name)
        except Exception as e:
            modified_name = name + ' '
            authors = search(modified_name)
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
                        sleep(1)
                        try:
                            pub_title = publication.title
                            publications_set.add(pub_title)
                        except Exception as e:
                            continue
                    for title in publications_set:
                        title = unicode(title).encode('utf-8')
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
                        sleep(1)
                        try:
                            pub_title = publication.title
                            publications_set.add(pub_title)
                            # fp1.write(publication.title + '\n')
                            # print "Came here: ", file_name
                        except Exception as e:
                            continue
                    for title in publications_set:
                        title = unicode(title).encode('utf-8')
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
