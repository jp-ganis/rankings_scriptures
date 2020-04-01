from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
import random
import json
import csv
import re

if __name__ == '__main__':	
# Open a PDF file.
	fp = open('boc.pdf', 'rb')
# Create a PDF parser object associated with the file object.
	parser = PDFParser(fp)
# Create a PDF document object that stores the document structure.
# Supply the password for initialization.
	document = PDFDocument(parser)
# Check if the document allows text extraction. If not, abort.
	if not document.is_extractable:
		raise PDFTextExtractionNotAllowed
	
	
