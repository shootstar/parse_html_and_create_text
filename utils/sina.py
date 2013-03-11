# -*- coding: utf-8 -*-
import urllib2
from base import CreateTextBase

class CreateText(CreateTextBase):
    def __init__(self,*args,**kwargs):
        super(CreateText,self).__init__(*args,**kwargs)
        self.standard_url = "http://vip.book.sina.com.cn/book"
        self.contain_word = "chapter"
        self.contents_tag = 'p'

    def split_url_for_links(self,candidate):
        try:
            _,book_id,num = candidate.split('_')
            num = int(num.split('.')[0])
            return [book_id,num]
        except:
            pass

    def generate_url(self,num):
        url = self.standard_url + urllib2.quote('/' + self.contain_word + '_' + self.book_id + '_' + str(num) + '.html')
        return url