import fitz
import pandas as pd


class PDFReader:
    def __init__(self, pdf, pdf_type):
        self.pdf_file = fitz.Document(pdf)
        self.page_count = len(self.pdf_file)
        self.page = None
        self.text = None
        self.text_page = None
        self.words = None
        self.pdf_type = pdf_type
        self.doc_type = None

    def load_page(self, page_num):
        self.page = self.pdf_file.load_page(page_num)
        self.text = self.page.get_text()
        if self.valid_pdf():
            self.text_page = self.page.get_textpage()
            self.words = self.text_page.extractWORDS()
            return True
        else:
            return False

    def valid_pdf(self):
        # TODO: Validation of provider or text validation
        # doc_type will be used
        if not chr(65533) in self.text:
            return True
        else:
            print("Cannot handle the selected pdf page fonts")
            return False

    def get_pdf_df(self):
        if self.pdf_type == "digital":
            return pd.DataFrame(self.words, columns=['x0', 'y0', 'x1', 'y1', 'word', 'block_no', 'line_no', 'word_no'])
        else:
            pass

    def get_text_page(self):
        return self.text_page
