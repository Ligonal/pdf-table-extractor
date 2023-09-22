import tkinter.filedialog
from tkinter import *
from PIL import Image, ImageTk
from get_files import GetFiles
import os
from pdf_reader import PDFReader
from table_extractor import PDFTableExtractor, unify_titles, define_columns_width, TableInfo, add_missing_titles, rearrange_titles_dic
from regex_extractor import RegexTableExtractor, RegexFieldInfo, GeneralRegexInfo
import pandas as pd
import json

PICTON_BLUE = '#00A6FB'
STEEL_BLUE = '#0582CA'
LAPIS_LAZULI = '#006494'
PRUSSIAN_BLUE = '#003554'
RICH_BLACK = '#051923'
WHITE = "#f8f9fa"
RED = 'f95738'
FONT_NAME = 'Courier bold'
PDF_IMAGE_PATH = 'Resources/pdf/steel_blue-pdf-100.png'
FOLDER_IMAGE_PATH = 'Resources/folder/steel_blue-folder-100.png'
JSON_IMAGE_PATH = 'Resources/json/steel_blue-json-100.png'


class PDFInterface:
    def __init__(self):
        self.pdfs_path = ''
        self.excels_path = ''
        self.json_path = ''

        self.is_loaded_pdf_path = False
        self.is_loaded_excel_path = False
        self.is_loaded_json_path = False

        self.window = Tk()
        self.window.title("PDF Information Extractor")
        self.window.config(padx=20, pady=20, bg=PRUSSIAN_BLUE)
        self.title_lb = Label(text="PDF Information Extractor",
                              font=(FONT_NAME, 14),
                              fg=WHITE,
                              bg=PRUSSIAN_BLUE,
                              highlightthickness=0, justify="center", anchor="w")
        self.title_lb.grid(column=0, row=0, columnspan=5, pady=10)
        self.path_pdfs_lb = Label(text="PDF Path...",
                                  font=(FONT_NAME, 10),
                                  fg=WHITE,
                                  bg=PRUSSIAN_BLUE,
                                  highlightthickness=00,
                                  width=30,
                                  justify="left",
                                  anchor="w")
        self.path_pdfs_lb.grid(column=1, row=1, columnspan=2)
        self.path_pdfs_cb = Entry(width=40)
        self.path_pdfs_cb.grid(column=1, row=2, pady=5, columnspan=2)
        self.image_pdf = Image.open(PDF_IMAGE_PATH)
        self.image_pdf = self.image_pdf.resize((30, 30))
        self.pdf_img = ImageTk.PhotoImage(self.image_pdf)
        self.path_pdf_button = Button(image=self.pdf_img, highlightthickness=0, bg=RICH_BLACK, height=38, width=38,
                                      command=self.load_pdf_path)
        self.path_pdf_button.grid(column=0, row=1, padx=5, pady=5, rowspan=2)

        self.path_json_lb = Label(text="JSON Path...",
                                  font=(FONT_NAME, 10),
                                  fg=WHITE,
                                  bg=PRUSSIAN_BLUE,
                                  highlightthickness=00,
                                  width=30,
                                  justify="left",
                                  anchor="w")
        self.path_json_lb.grid(column=1, row=3, columnspan=2)
        self.path_json_cb = Entry(width=40)
        self.path_json_cb.grid(column=1, row=4, pady=5, columnspan=2)
        self.image_json = Image.open(JSON_IMAGE_PATH)
        self.image_json = self.image_json.resize((30, 30))
        self.json_img = ImageTk.PhotoImage(self.image_json)
        self.path_json_button = Button(image=self.json_img, highlightthickness=0, bg=RICH_BLACK, height=38, width=38,
                                       command=self.load_json_path)
        self.path_json_button.grid(column=0, row=3, padx=5, pady=5, rowspan=2)

        self.path_folder_lb = Label(text="Folder Path...",
                                    font=(FONT_NAME, 10),
                                    fg=WHITE,
                                    bg=PRUSSIAN_BLUE,
                                    highlightthickness=00,
                                    width=30,
                                    justify="left",
                                    anchor="w")
        self.path_folder_lb.grid(column=1, row=5, columnspan=2)
        self.path_folder_cb = Entry(width=40)
        self.path_folder_cb.grid(column=1, row=6, pady=5, columnspan=2)
        self.image_folder = Image.open(FOLDER_IMAGE_PATH)
        self.image_folder = self.image_folder.resize((30, 30))
        self.folder_img = ImageTk.PhotoImage(self.image_folder)
        self.path_folder_button = Button(image=self.folder_img, highlightthickness=0, bg=RICH_BLACK, height=38,
                                         width=38,
                                         command=self.load_folder_path)
        self.path_folder_button.grid(column=0, row=5, padx=5, pady=5, rowspan=2)

        self.image_folder2 = Image.open(FOLDER_IMAGE_PATH)
        self.image_folder2 = self.image_folder2.resize((80, 80))
        self.pdf_img2 = ImageTk.PhotoImage(self.image_folder2)
        self.generate_pdf_button = Button(image=self.pdf_img2, highlightthickness=0, bg=RICH_BLACK, width=100,
                                          height=100,
                                          state="disabled", command=self.extract_pdf_information)
        self.generate_pdf_button.grid(column=3, row=2, padx=20, rowspan=6, columnspan=2)

        self.window.mainloop()

    def load_pdf_path(self):
        folder = tkinter.filedialog.askdirectory(title="Selecciona el folder de PDFs...")
        if folder:
            self.is_loaded_pdf_path = True
            self.path_pdfs_cb.insert(END, string=folder)
            self.pdfs_path = folder
        if self.is_loaded_excel_path and self.is_loaded_pdf_path and self.is_loaded_json_path:
            self.generate_pdf_button.config(state="active")

    def load_json_path(self):
        json_file = tkinter.filedialog.askopenfilename(title="Selecciona el archivo json de configuracion...",
                                                       filetypes=(('json files', '*.json'),))
        if json_file:
            self.is_loaded_json_path = True
            self.path_json_cb.insert(END, string=json_file)
            self.json_path = json_file
        if self.is_loaded_excel_path and self.is_loaded_pdf_path and self.is_loaded_json_path:
            self.generate_pdf_button.config(state="active")

    def load_folder_path(self):
        folder = tkinter.filedialog.askdirectory(title="Selecciona el folder para resultados...")
        if folder:
            self.is_loaded_excel_path = True
            self.path_folder_cb.insert(END, string=folder)
            self.excels_path = folder
        if self.is_loaded_excel_path and self.is_loaded_pdf_path and self.is_loaded_json_path:
            self.generate_pdf_button.config(state="active")

    def extract_pdf_information(self):
        json_file = open(self.json_path)
        json_data = json.load(json_file)
        json_file.close()
        tables = {}
        regex_fields = {}
        general_regexes = {}

        file_type = ".pdf"
        file_getter = GetFiles(path=self.pdfs_path, file_type=file_type)
        pdf_files = file_getter.get_files()
        full_pdf_files = [os.path.join(self.pdfs_path, pdf) for pdf in pdf_files]
        for pdf_file in full_pdf_files:
            for pdf_file_data in json_data.keys():
                for table_name in json_data[pdf_file_data]["tables"].keys():
                    if len(json_data[pdf_file_data]["tables"][table_name]) == 0:
                        continue
                    # titles = list(json_data[pdf_file_data]["tables"][table_name]["titles"])
                    titles = [value["name"] for value in json_data[pdf_file_data]["tables"][table_name]["titles"].items()]
                    titles_dic = {key.upper(): value for (key, value) in
                                  json_data[pdf_file_data]["tables"][table_name]["titles"].items()}
                    footer_delimiter = json_data[pdf_file_data]["tables"][table_name]["footer_delimiter"]
                    continue_delimiter = json_data[pdf_file_data]["tables"][table_name]["continue_delimiter"]
                    bottom_delimiter = json_data[pdf_file_data]["tables"][table_name]["bottom_delimiter"]
                    header_delimiter = json_data[pdf_file_data]["tables"][table_name]["header_delimiter"]
                    column_pivot = json_data[pdf_file_data]["tables"][table_name]["row_definition_column"][
                        "column_pivot"]
                    column_index = json_data[pdf_file_data]["tables"][table_name]["row_definition_column"][
                        "column_index"]
                    column_align = json_data[pdf_file_data]["tables"][table_name]["row_definition_column"][
                        "column_align"]
                    row_top_offset_value = json_data[pdf_file_data]["tables"][table_name]["row_definition_column"][
                        "row_top_offset_value"]
                    row_bot_offset_value = json_data[pdf_file_data]["tables"][table_name]["row_definition_column"][
                        "row_bot_offset_value"]

                    complete_titles = json_data[pdf_file_data]["tables"][table_name]["complete_titles"]
                    default_title_configuration = json_data[pdf_file_data]["tables"][table_name][
                        "default_title_configuration"]

                    table = TableInfo(name=table_name, titles=titles, titles_dic=titles_dic,
                                      footer_delimiter=footer_delimiter,
                                      continue_delimiter=continue_delimiter,
                                      bottom_delimiter=bottom_delimiter, header_delimiter=header_delimiter,
                                      column_pivot=column_pivot, column_index=column_index,
                                      column_align=column_align, row_top_offset_value=row_top_offset_value,
                                      row_bot_offset_value=row_bot_offset_value,
                                      complete_titles=complete_titles,
                                      default_title_configuration=default_title_configuration)
                    tables[table_name] = table

                for field in json_data[pdf_file_data]["specific_fields"].keys():
                    look_up_word = json_data[pdf_file_data]["specific_fields"][field]["look_up_word"]
                    location = json_data[pdf_file_data]["specific_fields"][field]["location"]
                    find_regex_word = json_data[pdf_file_data]["specific_fields"][field]["find_regex_word"]
                    regex_field = RegexFieldInfo(look_up_word=look_up_word, location=location,
                                                 find_regex_word=find_regex_word)
                    regex_fields[field] = regex_field

                for general_regex_name, general_regex in json_data[pdf_file_data]["general_regex"].items():
                    general_regexes[general_regex_name] = GeneralRegexInfo(general_regex_name, general_regex)

            pdf = PDFReader(pdf_file, "digital")
            for page_num in range(pdf.page_count):
                if pdf.load_page(page_num):
                    pdf_df = pdf.get_pdf_df()
                    raw_pdf_df = pdf_df.copy()
                    for table in tables.values():
                        table_extraction = PDFTableExtractor(raw_pdf_df, pdf_df)
                        table.titles_df, table.missing_titles_df = table_extraction.locate_titles(titles=table.titles,
                                                                                                  complete_titles=table.complete_titles)
                        titles_found = False
                        if table.titles_df.empty:
                            if not table.table_continues:
                                continue
                        else:
                            table.title_index_dic = unify_titles(titles_df=table.titles_df, titles=table.titles)
                            if not table.complete_titles:
                                table.missing_titles_dic = add_missing_titles(
                                    default_title_configuration=table.default_title_configuration,
                                    titles_df=table.missing_titles_df)
                                table.missing_titles = [key for key in table.missing_titles_dic.keys()]
                                table.missing_title_index_dic = unify_titles(titles_df=table.missing_titles_df,
                                                                             titles=table.missing_titles)
                                table.title_index_dic.update(table.missing_title_index_dic)
                                table.titles_df = pd.concat([table.titles_df, table.missing_titles_df])
                                table.titles_df = table.titles_df.sort_values(by=['x0'], ascending=True)
                                #     re-arrange missing_titles_dic with titles_dic and rewrite titles_dic
                                table.titles_dic = rearrange_titles_dic(titles_dic=table.titles_dic,
                                                                        missing_titles_dic=table.missing_titles_dic,
                                                                        title_index_dic=table.title_index_dic,
                                                                        titles_df=table.titles_df)
                            table.columns = define_columns_width(titles_dic=table.titles_dic, titles_df=table.titles_df,
                                                                 title_index_dic=table.title_index_dic)
                            titles_found = True

                            end_of_table_result = table_extraction.get_table_delimiters(
                                footer_delimiter=table.footer_delimiter,
                                continue_delimiter=table.continue_delimiter,
                                bottom_delimiter=table.bottom_delimiter,
                                titles_df=table.titles_df,
                                header_delimiter=table.header_delimiter,
                                titles_found=titles_found)
                            table.table_delimiter_y0 = end_of_table_result[0]
                            table.table_delimiter_y1 = end_of_table_result[1]
                            table.table_continues = end_of_table_result[2]

                            table.rows = table_extraction.define_rows_width(column_pivot=table.column_pivot,
                                                                            column_index=table.column_index,
                                                                            column_align=table.column_align,
                                                                            row_top_offset_value=table.row_top_offset_value,
                                                                            row_bot_offset_value=table.row_bot_offset_value,
                                                                            columns=table.columns,
                                                                            table_delimiter_y0=table.table_delimiter_y0,
                                                                            table_delimiter_y1=table.table_delimiter_y1)
                            if table.table_started:
                                section_table_df = table_extraction.create_extracted_table(rows=table.rows,
                                                                                           columns=table.columns,
                                                                                           page=page_num)
                                table.table_df = pd.concat([table.table_df, section_table_df], ignore_index=True,
                                                           sort=False)
                            else:
                                table.table_df = table_extraction.create_extracted_table(rows=table.rows,
                                                                                         columns=table.columns,
                                                                                         page=page_num)
                                table.table_started = True

                    pdf_text_page = pdf.get_text_page()
                    regex_extraction = RegexTableExtractor(raw_pdf_df, pdf_text_page, pdf.text)

                    for regex_field in regex_fields.values():
                        found_word = regex_extraction.get_regex_word(regex_field.look_up_word,
                                                                     regex_field.location,
                                                                     regex_field.find_regex_word)
                        regex_field.found_words += [found_word]

                        if found_word in regex_field.words_pages:
                            regex_field.words_pages[found_word] += "," + str(page_num)
                        else:
                            regex_field.words_pages[found_word] = str(page_num)

                    for general_regex in general_regexes.values():
                        found_word = regex_extraction.get_general_regex_matches(general_regex.look_up_field,
                                                                                general_regex.regex_search)

                        general_regex.found_matches += [found_word]

                        if found_word in general_regex.words_pages:
                            general_regex.words_pages[found_word] += "," + str(page_num)
                        else:
                            general_regex.words_pages[found_word] = str(page_num)
                else:
                    print("Error...")
                print(f"Page processed: {page_num}")

            pdf_name = os.path.basename(pdf_file).split('/')[-1]
            pdf_name = os.path.splitext(pdf_name)[0] + '.xlsx'
            with pd.ExcelWriter(os.path.join(self.excels_path, pdf_name)) as writer:
                unique_found_words = []
                found_regex_fields = []
                unique_found_words_pages = []
                for regex_field, regex_field_values in regex_fields.items():
                    set_found_words = set(regex_field_values.found_words)
                    list_found_words = (list(set_found_words))
                    unique_found_words += list_found_words
                    found_regex_fields += [regex_field for word in list_found_words]
                    unique_found_words_pages += regex_field_values.words_pages.values()
                regex_dic = {'specific_fields': found_regex_fields,
                             'result': unique_found_words,
                             'pages': unique_found_words_pages}
                regex_df = pd.DataFrame(regex_dic)

                unique_found_words = []
                found_regex_fields = []
                unique_found_words_pages = []
                for general_regex_field, general_regex_field_values in general_regexes.items():
                    set_found_words = set(general_regex_field_values.found_matches)
                    list_found_words = (list(set_found_words))
                    unique_found_words += list_found_words
                    found_regex_fields += [general_regex_field for word in list_found_words]
                    unique_found_words_pages += general_regex_field_values.words_pages.values()
                general_regex_dic = {'specific_fields': found_regex_fields,
                             'result': unique_found_words,
                             'pages': unique_found_words_pages}
                general_regex_df = pd.DataFrame(general_regex_dic)

                regex_df.to_excel(writer, sheet_name='Specific Fields')
                general_regex_df.to_excel(writer, sheet_name='General Regex')
                for table_name, table in tables.items():
                    if not table.table_df.empty:
                        df_to_excel = table.table_df.copy()
                        df_to_excel.to_excel(writer, sheet_name=table.name)
                        table.table_df = None
