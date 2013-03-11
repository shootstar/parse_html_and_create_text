# -*- coding: utf-8 -*-
import time
import os
import re
import urllib2
import codecs
import copy

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import BaseDocTemplate,SimpleDocTemplate, Paragraph, Spacer, Image,Frame,PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth

from itertools import groupby
from BeautifulSoup import BeautifulSoup,Comment,SoupStrainer

EXCLUDE = ['style','script','[document]','head','noscript','title','a','option']
USER_AGENT = 'Mozilla/5 (Solaris 10) Gecko'

class CreateTextBase(object):
    def __init__(self,book_name,url,author_name=None,encoding="gb18030",file_type=None,directory=None):
        headers = [('User-Agent',USER_AGENT)]
        self.opener = urllib2.build_opener()
        self.opener.addheaders = headers
        self.book_name = book_name
        self.author_name = author_name
        self.url = url
        self.encoding = encoding
        self.file_type = file_type or "txt"

        #TODO filepath
        self.directory = directory or os.path.join(os.path.dirname(__file__),'books')
        self.contain_word = None

        self._dispatch()

    def _dispatch(self):
            if self.file_type == "pdf":
                pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
                styles = getSampleStyleSheet()
                normal = copy.deepcopy(styles['Normal'])
                normal.fontName = 'STSong-Light'
                #normal.fontSize = letter
                self.pdf_style = normal
                pdf = BaseDocTemplate("{}/{}.pdf".format(self.directory,self.book_name),pagesize=A4)
                self.pdf_story = list()
                self.pdf = pdf

    def cleanSoup(self,soup):
        # get rid of javascript, noscript and css
        [[tree.extract() for tree in soup(elem)] for elem in EXCLUDE]
        # get rid of doctype
        subtree = soup.findAll(text=re.compile("DOCTYPE"))
        [tree.extract() for tree in subtree]
        # get rid of comments
        comments = soup.findAll(text=lambda text:isinstance(text,Comment))
        [comment.extract() for comment in comments]
        return soup

    def get_links_from_index(self):
        html = self.opener.open(self.url).read()
        links = SoupStrainer('a',href=re.compile(self.contain_word))
        tag = BeautifulSoup(html,fromEncoding=self.encoding,parseOnlyThese=links)
        return tag

    #TODO think logic
    def has_text_structure(self,texts):
        return True

    def get_text(self,soup):

        count = 0
        while True:
            count +=1
            #assume texts have their title on h-tag
            h_tag = 'h{}'.format(count)
            h = soup.find(h_tag)
            if h is None:
                return None
            text_candidate = list()
            h_area = h.parent
            child_list = [child for child in h_area.findChildren()]
            # print 'hhhhhh'
            # print h_area
            # print child_list
            for child in child_list:
                print 'ccc',child
                print '\n'
                child_tag=  [tag.name for tag in child.findChildren()]
                #assume there are texts if exist the text structure
                if self.has_text_structure(child_tag):
                    text_candidate.append([h,child])
            print 'tttttttttt',text_candidate
            return text_candidate

    def decide_the_best_text(self,text_candidate):
        content = sorted(text_candidate,key=lambda x:len(x[1].text),reverse=True)[0]
        return content

    def write_to_file(self,count,title,text):

        print title
        print self.book_name,type(self.book_name)

        #TODO pdf logic
        if self.file_type == "pdf":
            file_name = "{}/{}.pdf".format(self.directory,count)
            mode = 'wb+'
            # width,height = map(lambda x:x-4*inch,A4)
            #
            # if title:
            #     #shrink_font_size(width,height,title.string.encode('utf8'),self.pdf_style)
            #     self.pdf_story.append(Spacer(3, 12))
            #     self.pdf_story.append(Paragraph(title.string.encode('utf8'),self.pdf_style))
            #     self.pdf_story.append(Spacer(3, 12))
            # for t in text.findAll('p'):
            #     try:
            #         shrink_font_size(width,height,t.string.encode('utf8'),self.pdf_style)
            #         self.pdf_story.append(Paragraph(t.string.encode('utf8'),self.pdf_style))
            #         self.pdf_story.append(Spacer(1, 12))
            #     except AttributeError:
            #         pass

        elif self.file_type == "txt":
            #file_name = "{}/{}/{}.txt".format(self.directory,self.book_name,count)
            file_name = "{}/{}.txt".format(self.directory,count)
            mode = 'w+'

        with open(file_name,mode) as f:
            if title:
                f.write(title.string.encode('utf8'))
                f.write('\n')
            for t in text.findAll(self.contents_tag):
                try:
                    if self.contents_tag == 'br':
                        t = t.nextSibling
                    f.write(t.string.encode('utf8'))
                    f.write('\n')
                except AttributeError:
                    pass

    #TODO implement
    #use queue?
    def redo(self,num):
        pass

    def split_url_for_links(self,url):
        raise NotImplementedError

    def generate_url(self,num):
        raise NotImplementedError

    def main(self):

        #get every url candidates from the index page of the book
        tag = self.get_links_from_index()

        #generate urls from each candidates or exclude them if they don't match the condition
        result = map(self.split_url_for_links,[t['href'] for t in tag])
        result = filter(lambda x:x!= None,result)

        print result
        #decide book_id if any
        book_ids = map(lambda x:x[0],result)

        grouped_book_ids = [(i,len(list(x))) for i,x in groupby(sorted(book_ids))]
        self.book_id = sorted(grouped_book_ids,lambda x:x[1],reverse=True)[0][0]

        #decide every pages that contain relevant contents and should by parsed
        pages_list = [page_id for id,page_id in result if id==self.book_id]
        pages_list = sorted(pages_list)

        #get title and texts from each pages and write it in a file
        for i,num in enumerate(pages_list):
            try:
                url = self.generate_url(num)
                print url
                html = self.opener.open(url).read()

                soup = BeautifulSoup(html,fromEncoding=self.encoding,parseOnlyThese=SoupStrainer('body'))
                soup = self.cleanSoup(soup)

                texts_candidate = self.get_text(soup)

                if not texts_candidate:
                    continue

                print 'ttt',texts_candidate
                content = self.decide_the_best_text(texts_candidate)
                print 'cccccccc',content
                title = content[0]
                text = content[1]

                self.write_to_file(i,title,text)
                time.sleep(1)
            except Exception,e:
                print e
                self.redo(num)
                time.sleep(1)

        # if self.file_type == "pdf":
        #     frameCount = 1
        #     frameWidth = self.pdf.width/frameCount
        #     frameHeight = self.pdf.height-.05*inch
        #     frames = []
        #     #construct a frame for each column
        #     for frame in range(frameCount):
        #         leftMargin = self.pdf.leftMargin + frame*frameWidth
        #     column = Frame(leftMargin, self.pdf.bottomMargin, frameWidth, frameHeight)
        #     frames.append(column)
        #
        #     page_template = PageTemplate(frames=frames)
        #     self.pdf.addPageTemplates(page_template)
        #     self.pdf.build(self.pdf_story)


def shrink_font_size(aW, aH, text, style):

    """Shrinks font size by using pdfmetrics to calculate the height
    of a paragraph, given the font name, size, and available width."""
    def break_lines(text, aW):
        # simpleSplit calculates how reportlab will break up the lines for
        # display in a paragraph, by using width/fontsize.
        return simpleSplit(text, style.fontName, style.fontSize, aW)

    def line_wrap(lines, style):
        # Get overall width of text by getting stringWidth of longest line
        width = stringWidth(max(lines), style.fontName, style.fontSize)
        # Paragraph height can be calculated via line spacing and number of lines.
        height = style.leading * len(lines)
        return width, height

    print text, style.fontName, style.fontSize, aW
    lines = break_lines(text, aW)
    print 'bbbbb',lines
    width, height = line_wrap(lines, style)
    print lines,width,height
    while height > aH or width > aW:
        print width,height
        style.fontSize -= 1
        lines = break_lines(text, aW)
        width, height = line_wrap(lines, style)


