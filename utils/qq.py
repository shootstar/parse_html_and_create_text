# -*- coding: utf-8 -*-
import urllib2
import copy
from base import CreateTextBase

class CreateText(CreateTextBase):

    #TODO implement
    def __init__(self,*args,**kwargs):
        super(CreateText,self).__init__(*args,**kwargs)
        url = self.url.split('/')[0:-1]
        self.standard_url = '/'.join(url)
        self.contain_word = "shtml"
        self.contents_tag = 'br'

    def split_url_for_links(self,candidate):
        print candidate,type(candidate)
        try:
            candidate = candidate.split('(')[1]
            candidate = candidate.split(')')[0]
            candidate_list = candidate.split('/')
            book_id = int(candidate_list[-2])
            num = int(candidate_list[-1].split('.')[0])
            return [book_id,num]
        except Exception,e:
            print e


    def generate_url(self,num):
        url = self.standard_url + urllib2.quote('/' + str(num) + '.shtml')
        return url