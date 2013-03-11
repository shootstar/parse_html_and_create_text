#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import argparse
from __init__ import import_module

URL_TYPE = ['sina','qq']

def main():
    parser = argparse.ArgumentParser(description='想探索文学的深处吗？')
    parser.add_argument('--url',dest='url',help='index page of the book')
    parser.add_argument('--book',dest='book',help='book name')
    parser.add_argument('--author',dest='author',help='author')
    parser.add_argument('--directory',dest='directory',help='directory')
    parser.add_argument('--file_type',dest='file_type',help='file_type')

    args = parser.parse_args()

    if not args.url:
        print >> sys.stderr,'require:--url=xxx'
        sys.exit(1)

    u = args.url.split('.')
    for u_type in URL_TYPE:
        if u_type in u:
            break
    else:
        print >> sys.stderr,'check the url again please'
        sys.exit(1)

    try:
        create_text = import_module('utils.{}'.format(u_type))
        print u_type
        print create_text
        return create_text.CreateText(url=args.url,book_name=args.book,file_type=args.file_type,directory=args.directory).main()
    except Exception,e:
        print e
        return False

if __name__ == "__main__":
    main()

