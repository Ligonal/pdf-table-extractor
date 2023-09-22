import re


class RegexFieldInfo:
    def __init__(self, look_up_word, location, find_regex_word):
        self.look_up_word = look_up_word
        self.location = location
        self.find_regex_word = find_regex_word
        self.found_words = []
        self.words_pages = {}


class GeneralRegexInfo:
    def __init__(self, look_up_field, regex_search):
        self.look_up_field = look_up_field
        self.regex_search = regex_search
        self.found_matches = []
        self.words_pages = {}


class RegexTableExtractor:
    def __init__(self, pdf_df, text_page, text):
        self.pdf_df = pdf_df
        self.text_page = text_page
        self.text = text
        self.y0_offset = 0.5
        self.y1_offset = 0.5

    def get_regex_word(self, look_up_word, location, find_regex_word):
        look_up_squares = self.text_page.search(look_up_word)
        found_word = ''
        for look_up_square in look_up_squares:
            x0 = look_up_square.ul.x
            y0 = look_up_square.ul.y
            x1 = look_up_square.lr.x
            y1 = look_up_square.lr.y

            if location == 'right':
                y0 -= self.y0_offset
                y1 += self.y0_offset
                search_df = self.pdf_df[(self.pdf_df['x0'] > x1) & (self.pdf_df['x1'] < 9999) &
                                        (self.pdf_df['y0'] > y0) & (self.pdf_df['y0'] < y1)]
                search_df = search_df.sort_values(by=['x0'], ascending=True)
                #  Check if empty
                if not search_df.empty:
                    word = search_df['word'].iloc[0]
                    if re.match(find_regex_word, word):
                        found_word = re.match(find_regex_word, word)[0]
                else:
                    found_word = 'Not Found...'

            elif location == 'left':
                y0 -= self.y0_offset
                y1 += self.y0_offset
                search_df = self.pdf_df[(self.pdf_df['x0'] > 0) & (self.pdf_df['x1'] < x0) &
                                        (self.pdf_df['y0'] > y0) & (self.pdf_df['y0'] < y1)]
                search_df = search_df.sort_values(by=['x0'], ascending=True)
                # for ind in search_df.index:
                #  Check if empty
                if not search_df.empty:
                    word = search_df['word'].iloc[-1]
                    if re.match(find_regex_word, word):
                        found_word = re.match(find_regex_word, word)[0]
                else:
                    found_word = 'Not Found...'

            elif location == 'down':
                search_df = self.pdf_df[((((x0 <= self.pdf_df['x0']) & (self.pdf_df['x0'] <= x1)) |
                                          ((x0 <= self.pdf_df['x1']) & (self.pdf_df['x1'] <= x1))) & (
                                                     self.pdf_df['y0'] > y0)) |
                                        (((self.pdf_df['x0'] <= x0) & (x0 <= self.pdf_df['x1'])) | (
                                                (self.pdf_df['x0'] <= x1) & (x1 <= self.pdf_df['x1']))) &
                                        (self.pdf_df['y0'] > y0)]
                search_df = search_df.sort_values(by=['y0'], ascending=True)
                if not search_df.empty:
                    word = search_df['word'].iloc[0]
                    if re.match(find_regex_word, word):
                        found_word = re.match(find_regex_word, word)[0]
                else:
                    found_word = 'Not Found...'

            elif location == 'top':
                search_df = self.pdf_df[((((x0 <= self.pdf_df['x0']) & (self.pdf_df['x0'] <= x1)) |
                                          ((x0 <= self.pdf_df['x1']) & (self.pdf_df['x1'] <= x1))) & (
                                                     self.pdf_df['y0'] < y0)) |
                                        (((self.pdf_df['x0'] <= x0) & (x0 <= self.pdf_df['x1'])) | (
                                                (self.pdf_df['x0'] <= x1) & (x1 <= self.pdf_df['x1']))) &
                                        (self.pdf_df['y0'] < y0)]
                search_df = search_df.sort_values(by=['y0'], ascending=True)
                if not search_df.empty:
                    word = search_df['word'].iloc[-1]
                    if re.match(find_regex_word, word):
                        found_word = re.match(find_regex_word, word)[0]
                else:
                    found_word = 'Not Found...'
        return found_word

    def get_general_regex_matches(self, look_up_field, regex_search):
        if re.search(regex_search, self.text):
            found_word = re.search(regex_search, self.text)[0]
        else:
            found_word = 'Not Found...'
        return found_word


