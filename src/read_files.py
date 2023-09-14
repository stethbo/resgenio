import PyPDF2

PDF_PATH = "data/files/Stefan Borek Resume - Dark.pdf"

def main():
    # creating a pdf file object
    pdfFileObj = open(PDF_PATH, 'rb')
    
    # creating a pdf reader object
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    
    # printing number of pages in pdf file
    print(len(pdfReader.pages))
    
    # creating a page object
    pageObj = pdfReader.pages[0]
    
    # extracting text from page
    print(pageObj.extract_text())
    
    # closing the pdf file object
    pdfFileObj.close()


if __name__ == "__main__":
    main()