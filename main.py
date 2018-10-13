import mwparserfromhell
import pywikibot
import urlparse
import datrie
import string
import os
import sys
import datetime
import dateparser
import re

trie=datrie.Trie(string.printable)
site = pywikibot.Site()
debug =False

MIN_AGE=15 #days
WARN_FUZZY_DATE=False

BAD_PUBLISHER="WP:QUESTIONED"
SOCIAL="WP:UGC"
BREAKING_NEWS="WP:RSBREAKING"
FUZZY_DATE="Fuzzy Date"
UNPARSABLE_DATE="BAD Date"

#nothing before the year 1000 is a good secondary source
year_regex=re.compile('[1-9][0-9][0-9][0-9]$')

def safe_print(s):
    if sys.stdout.encoding is None:
        print(s.encode('utf-8'))
    else:
        print(s)

def parse(title):
    page = pywikibot.Page(site, title)
    while page.isRedirectPage():
        page=page.getRedirectTarget()
    try:
        text = page.get()
        return mwparserfromhell.parse(text)
    except pywikibot.exceptions.NoPage:
            return None



def check_citation(article_name,citation_node):
    for i in citation_node.params:
        if i.startswith('date='):
            try:
                date=i[5:len(i)].strip()
                
                #fuzzy dates
                # bad_words=["spring","summer","fall","winter","early","late"]
                # uncased=date.lower()
                # if any(x in uncased for x in bad_words):
                #     emit_warn_citation(article_name,citation_node,FUZZY_DATE)

                seasons=["spring","summer","fall","autumn","winter"]
                uncased=date.lower()
                for x in seasons:
                    if x in uncased:
                        date=uncased.replace(x,"").strip()
                if year_regex.match(date):
                    if WARN_FUZZY_DATE:
                        emit_warn_citation(article_name,citation_node,FUZZY_DATE)
                else:    
                    date=dateparser.parse(date)
                    delta=(datetime.datetime.now()-date).days
                    if delta<MIN_AGE:
                        emit_bad_citation(article_name,citation_node,BREAKING_NEWS)
            except:
                emit_bad_citation(article_name,citation_node,UNPARSABLE_DATE)

        if i.startswith('url='):
            url=i[4:len(i)].strip()
            if url.startswith("{{"):
                #template substitution currently unresolvable, but probably ok
                pass
            elif debug:
                safe_print(u"Good citation %s"%(url,))
            else:
                domain= urlparse.urlparse(url).hostname
                if not check_citation_url(domain):
                    reason=(u"Bad publisher url:%s"%(domain,))
                    emit_bad_citation(article_name,citation_node,reason)
            continue
        if i.startswith('archive-url='):
            url=i[12:len(i)].strip()
            domain= urlparse.urlparse(url).hostname
            if not check_citation_url(domain):
                reason= (u"Bad archive url:%s"%(domain,))
                emit_bad_citation(article_name,citation_node,reason)
            elif debug:
                safe_print(u"Good citation %s"%(url,))
            continue
        if i.startswith('conference-url='):
            url=i[len('conference-url='):len(i)].strip()
            domain= urlparse.urlparse(url).hostname
            if not check_citation_url(domain):
                reason= (u"Bad conference url:%s"%(domain,))
                emit_bad_citation(article_name,citation_node,reason)
            elif debug:
                safe_print(u"Good citation %s"%(url,))
            continue
   

def build_trie():
    for path in os.listdir(sys.argv[1]):
        with open(os.path.join(sys.argv[1],path),mode='r') as f:
            for l in f:
                url= l.split(" ")[0]
                d=unicode(urlparse.urlparse(url).hostname)
                trie[d]=d
    #load all bad domains

def check_citation_url(domain):
    if domain is not None:
        return not domain in trie
        

def emit_bad_citation(article_name,citation_node,reason):
    #log stuff here
    safe_print(u"BAD CITATION: %s\n%s\n"%(reason,citation_node))

def emit_warn_citation(article_name,citation_node,reason):
    safe_print(u"WARN: %s\n%s\n"%(reason,citation_node))

def main():
    verbose=True
    build_trie()
    for a in sys.stdin:
        title=a.strip()
        if verbose: safe_print(title)
        p = parse(title)
        if p is None:
            sys.stderr.write(u"NOT EXISTS %s"%(title,))
            continue
        for c in p.filter_templates():
            if c.name.startswith('cite'):
                check_citation(title,c)

if __name__ == "__main__":
    main()


def help():
    print("This utility is designed to find citations with suspicious properties in Wikipedia pages")
    print("Just because this utility finds a citation which it believes to be suspect, does not make the contents of the reference incorrect.")
    print("This utility checks publishers against a list of unscrupulous journals.  Legitimate athors may publish with thes journals, but the journals are known to have little or no review process, or may publish indescriminantly.")