# -*- coding: utf-8 -*-

from pyPdf import PdfFileReader,PdfFileWriter

def main(output_file,input_files):
    print 'start'

    output = PdfFileWriter()
    total_pages = 0

    for f in input_files:
        if f[-4:] != '.pdf':
            print 'skip',f
            continue
        else:
            input = PdfFileReader(file(f,'rb'))
            num_pages = input.getNumPages()
            total_pages += num_pages

            for i in xrange(0,num_pages):
                output.addPage(input.getPage(i))

    outputStream = file(output_file,'wb')
    output.write(outputStream)
    outputStream.close()


if __name__ == "__main__":
    import argparse
    description = "concatinate input PDF files"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-o", "--output", default="output.pdf")
    parser.add_argument("-i", "--input", nargs='*', required=True)
    parser.add_argument("-v", "--version", action='version',
                        version="%(prog)s 1.0")
    args = vars(parser.parse_args())

    print "****** start concatination ******"
    main(args['output'], args['input'])