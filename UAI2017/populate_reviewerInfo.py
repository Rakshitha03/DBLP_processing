from time import sleep

import openreview
# import dblp
import inspect
import json
import os
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
                try:
                    self.load_data()
                except Exception as e:
                    import pdb
                    pdb.set_trace()
                    print "Here"
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
        super(Author, self).__init__(['name', 'publications', 'homepages',
                                      'homonyms'])

    def load_data(self):
        resp = requests.get(DBLP_PERSON_URL.format(urlpt=self.urlpt))
        # TODO error handling
        xml = resp.content
        self.xml = xml
        try:
            root = etree.fromstring(xml)
        except Exception as e:
            import pdb
            pdb.set_trace()
            print xml
        data = {
            'name': root.attrib['name'],
            'publications': [Publication(k) for k in
                             root.xpath('/dblpperson/dblpkey[not(@type)]/text()')],
            'homepages': root.xpath(
                '/dblpperson/dblpkey[@type="person record"]/text()'),
            'homonyms': root.xpath('/dblpperson/homonym/text()')
        }

        self.data = data


def first_or_none(seq):
    try:
        return next(iter(seq))
    except StopIteration:
        pass


Publisher = namedtuple('Publisher', ['name', 'href'])
Series = namedtuple('Series', ['text', 'href'])
Citation = namedtuple('Citation', ['reference', 'label'])


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
        super(Publication, self).__init__(['type', 'sub_type', 'mdate',
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
            'type': publication.tag,
            'sub_type': publication.attrib.get('publtype', None),
            'mdate': publication.attrib.get('mdate', None),
            'authors': publication.xpath('author/text()'),
            'editors': publication.xpath('editor/text()'),
            'title': first_or_none(publication.xpath('title/text()')),
            'year': int(first_or_none(publication.xpath('year/text()'))),
            'month': first_or_none(publication.xpath('month/text()')),
            'journal': first_or_none(publication.xpath('journal/text()')),
            'volume': first_or_none(publication.xpath('volume/text()')),
            'number': first_or_none(publication.xpath('number/text()')),
            'chapter': first_or_none(publication.xpath('chapter/text()')),
            'pages': first_or_none(publication.xpath('pages/text()')),
            'ee': first_or_none(publication.xpath('ee/text()')),
            'isbn': first_or_none(publication.xpath('isbn/text()')),
            'url': first_or_none(publication.xpath('url/text()')),
            'booktitle': first_or_none(publication.xpath('booktitle/text()')),
            'crossref': first_or_none(publication.xpath('crossref/text()')),
            'publisher': first_or_none(publication.xpath('publisher/text()')),
            'school': first_or_none(publication.xpath('school/text()')),
            'citations': [Citation(c.text, c.attrib.get('label', None))
                          for c in publication.xpath('cite') if c.text != '...'],
            'series': first_or_none(Series(s.text, s.attrib.get('href', None))
                                    for s in publication.xpath('series'))
        }

        self.data = data


def search(author_str):
    resp = requests.get(DBLP_AUTHOR_SEARCH_URL, params={'xauthor': author_str})
    try:
        root = etree.fromstring(resp.content)
    except:
        print resp.content
        import pdb
        pdb.set_trace()
        print 'z'
    return [Author(urlpt) for urlpt in root.xpath('/authors/author/@urlpt')]


# reviewersInfo = {}
# initializing openreview_client to post notes.
username = 'OpenReview.net'  # fill in your email address that you use to log in to OpenReview
password = '1234567890'  # fill in your password
baseurl = 'http://localhost:3000'  # fill in your desired baseurl (e.g. 'http://localhost:3000', or 'http://dev.openreview.net', etc.)

# openreview_client = openreview.Client(username=username, password=password, baseurl=baseurl)
# reading the reviewer info from csv file and obtaining information about the user
fp = open("./UAI_2017_reviewers.csv")
no_name = 0
more_than_one = 0
no_hits = 0
no_match = 0
no_pub = 0
author_disambiguation = {}
no_hits_names = []
no_name_list = []
no_matched_author = []
no_pub_list = []
notes_count = 0

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
            authors = search(name)
        except Exception as e:
            sleep(2)
            authors = search(name)
        if authors:
            if len(authors) > 1:
                print "More than one authors found! "
                more_than_one += 1
                author_disambiguation[name] = []
                author = None
                for ath in authors:
                    author_disambiguation[name].append(ath.name)
                    if name.lower() == ath.name.lower():
                        author = ath
                # print name + ' : ' + unicode(author.name).encode('utf-8')
                if not author:
                    no_matched_author.append(name)
                    print "No perfect match found for: ", name
                    print author_disambiguation[name]
                    no_match += 1
                if author and len(author.publications) == 0:
                    print "No publications found for ", name
                    no_pub += 1
                    no_pub_list.append(name)
                    continue
                if author and len(author.publications) > 0:
                    print len(author.publications)
                    publications_set = set()
                    for publication in author.publications:
                        try:
                            pub_title = publication.title
                        except:
                            sleep(2)
                            pub_title = publication.title
                        if pub_title in publications_set:
                            continue
                        note = openreview.Note()
                        publications_set.add(pub_title)
                        ath_ids = []
                        for ath_name in publication.authors:
                            if ath_name.lower() == author.name.lower():
                                ath_ids.append(emailId)
                            else:
                                ath_ids.append('_')

                                # note.content = {
                                #     'abstract': '',
                                #                'school': publication.school ,
                                #                'publisher':publication.publisher ,
                                #                'chapter': publication.chapter,
                                #                'crossref': publication.crossref,
                                #                'pages': publication.pages,
                                #                'volume': publication.volume,
                                #                'journal': publication.journal,
                                #                'type': publication.type,
                                #                'sub_type': publication.sub_type,
                                #                'editors': ','.join(publication.editors),
                                #                'booktitle': publication.booktitle,
                                #                'year': publication.year,
                                #                'month': publication.month,
                                #                'mag_number': publication.number,
                                #                'series': publication.series,
                                #                'ee': publication.ee,
                                #                'isbn': publication.isbn,
                                #                'DBLP_url': 'publication.url',
                                #                'authorids': ath_ids,
                                #                'authors': publication.authors,
                                #                'title': publication.title,
                                # }
                                # note.invitation = 'DBLP.org/-/paper'
                                # note.signatures = ['DBLP.org/upload']
                                # note.writers = note.signatures
                                # note.readers = ['everyone']
                                # note.cdate = 1234
                                # note.to_json()
                                # try:
                                #     openreview_client.post_note(note)
                                #     notes_count += 1
                                # except Exception as e:
                                #     print "EXCEPTION !!", e
                                # for title in publications_set:
                                #     title = unicode(title).encode('utf-8')

            else:
                author = authors[0]
                if len(author.publications) == 0:
                    print "No publications found for ", name
                    no_pub += 1
                    no_pub_list.append(name)
                if len(author.publications) > 0:
                    print len(author.publications)
                    publications_set = set()
                    for publication in author.publications:
                        try:
                            pub_title = publication.title
                        except Exception as e:
                            sleep(2)
                            pub_title = publication.title
                        if pub_title in publications_set:
                            continue
                        note = openreview.Note()
                        publications_set.add(pub_title)
                        ath_ids = []
                        for ath_name in publication.authors:
                            if ath_name.lower() == author.name.lower():
                                ath_ids.append(emailId)
                            else:
                                ath_ids.append('_')

                                # note.content = {
                                #     'abstract': '',
                                #     'school': publication.school,
                                #     'publisher': publication.publisher,
                                #     'chapter': publication.chapter,
                                #     'crossref': publication.crossref,
                                #     'pages': publication.pages,
                                #     'volume': publication.volume,
                                #     'journal': publication.journal,
                                #     'type': publication.type,
                                #     'sub_type': publication.sub_type,
                                #     'editors': ','.join(publication.editors),
                                #     'booktitle': publication.booktitle,
                                #     'year': publication.year,
                                #     'month': publication.month,
                                #     'mag_number': publication.number,
                                #     'series': publication.series,
                                #     'ee': publication.ee,
                                #     'isbn': publication.isbn,
                                #     'DBLP_url': 'publication.url',
                                #     'authorids': ath_ids,
                                #     'authors': publication.authors,
                                #     'title': publication.title,
                                # }
                                # note.invitation = 'DBLP.org/-/paper'
                                # note.signatures = ['DBLP.org/upload']
                                # note.writers = note.signatures
                                # note.readers = ['everyone']
                                # note.cdate = 1234
                                # note.to_json()
                                # try:
                                #     openreview_client.post_note(note)
                                #     notes_count += 1
                                # except Exception as e:
                                #     print "EXCEPTION !!", e
                                # for title in publications_set:
                                #     title = unicode(title).encode('utf-8')
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
print "No matches count ", no_match
print "No matches list", no_matched_author
print "No publications: ", no_pub
print "No publications list: ", no_pub_list
print "No. of notes created are: ", notes_count
