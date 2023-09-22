from collections import Counter
import math
import pandas as pd
import re
import numpy as np


OFFSET_TITLE_CONSTANT_Y = 0.75
OFFSET_TITLE_CONSTANT_X = 23.32


class ColumnDef:
    def __init__(self, title, x0, x1, exclude_regex=None):
        self.title = title
        self.x0 = x0
        self.x1 = x1
        self.exclude_regex = exclude_regex


class RowDef:
    def __init__(self, y0, y1):
        self.y0 = y0
        self.y1 = y1


class TableInfo:
    def __init__(self, name, titles, titles_dic, footer_delimiter, continue_delimiter, bottom_delimiter,
                 header_delimiter, column_pivot, column_index, column_align, row_top_offset_value,
                 row_bot_offset_value, complete_titles, default_title_configuration):
        self.name = name
        self.titles = titles
        self.missing_titles = None
        self.titles_dic = titles_dic
        self.missing_titles_dic = None
        self.footer_delimiter = footer_delimiter
        self.continue_delimiter = continue_delimiter
        self.bottom_delimiter = bottom_delimiter
        self.header_delimiter = header_delimiter
        self.column_pivot = column_pivot
        self.column_index = column_index
        self.column_align = column_align
        self.row_top_offset_value = row_top_offset_value
        self.row_bot_offset_value = row_bot_offset_value

        self.complete_titles = complete_titles
        self.default_title_configuration = default_title_configuration

        self.titles_df = None
        self.missing_titles_df = None
        self.title_index_dic = {}
        self.missing_title_index_dic = {}
        self.columns = []
        self.rows = []
        self.table_delimiter_y0 = 0
        self.table_delimiter_y1 = 0

        self.table_started = False
        self.table_continues = False
        self.table_df = pd.DataFrame


def get_index_words(section_df, words):
    words = words.upper()
    words_index = []
    words_dic = {word: False for word in words.split()}
    for word_index in range(len(words.split())):
        word = words.split()[word_index]
        mid_point_x = 0
        mid_point_y = 0
        if not words_dic[word]:
            if len(words.split()) != len(words_index):
                for current_index in section_df.index[section_df['word'] == word].tolist():
                    if section_df.at[current_index, 'found']:
                        continue
                    words_index += [current_index]
                    section_df.at[current_index, 'found'] = True
                    words_dic[word] = True
                    x0 = section_df.at[current_index, 'x0']
                    x1 = section_df.at[current_index, 'x1']
                    y0 = section_df.at[current_index, 'y0']
                    y1 = section_df.at[current_index, 'y1']
                    mid_point_x = (x1 + x0) / 2
                    mid_point_y = (y1 + y0) / 2
                    break
                if word_index != len(words.split()) - 1:
                    next_title_word = words.split()[word_index + 1]
                    prev_distance = 0
                    prev_index = 0
                    word_found = False
                    for current_index in section_df.index[section_df['word'] == next_title_word].tolist():
                        if section_df.at[current_index, 'found']:
                            continue
                        x0 = section_df.at[current_index, 'x0']
                        x1 = section_df.at[current_index, 'x1']
                        y0 = section_df.at[current_index, 'y0']
                        y1 = section_df.at[current_index, 'y1']
                        next_mid_point_x = (x1 + x0) / 2
                        next_mid_point_y = (y1 + y0) / 2
                        new_distance = math.sqrt(
                            pow(next_mid_point_x - mid_point_x, 2) + pow(next_mid_point_y - mid_point_y, 2))
                        new_index = current_index
                        if prev_distance == 0 or prev_distance > new_distance:
                            prev_distance = new_distance
                            prev_index = new_index
                        word_found = True
                    if word_found:
                        words_index += [prev_index]
                        section_df.at[prev_index, 'found'] = True
                        words_dic[next_title_word] = True
    return words_index


def add_missing_titles(default_title_configuration, titles_df):
    column_number = default_title_configuration["column_number"]
    left_offset = default_title_configuration["left_offset"]
    left_offset_value = default_title_configuration["left_offset_value"]
    right_offset = default_title_configuration["right_offset"]
    right_offset_value = default_title_configuration["right_offset_value"]
    exclude_regex = default_title_configuration["exclude_regex"]
    max_space_distance = default_title_configuration["max_space_distance"]
    titles_df = titles_df.reset_index(drop=True)
    temp_title = ""
    missing_titles_dic = {}
    title_configuration = {
        "column_number": column_number,
        "left_offset": left_offset,
        "left_offset_value": left_offset_value,
        "right_offset": right_offset,
        "right_offset_value": right_offset_value,
        "exclude_regex": exclude_regex
    }

    for ind in titles_df.index:
        if not titles_df['found'][ind]:
            if temp_title == "":
                temp_title += " " + titles_df['word'][ind]
            else:
                curr_x0 = titles_df['x0'][ind]
                prev_x1 = titles_df['x1'][ind-1]
                space_distance = abs(curr_x0-prev_x1)
                if space_distance <= max_space_distance:
                    temp_title += " " + titles_df['word'][ind]
                    if ind == titles_df.shape[0] - 1:

                        missing_titles_dic[temp_title] = title_configuration.copy()
                        temp_title = titles_df['word'][ind]
                else:
                    missing_titles_dic[temp_title] = title_configuration.copy()
                    temp_title = titles_df['word'][ind]
        else:
            if temp_title != "":
                missing_titles_dic[temp_title] = title_configuration.copy()
                temp_title = ""

    return missing_titles_dic


def rearrange_titles_dic(titles_dic, missing_titles_dic, title_index_dic, titles_df):
    all_titles_dic = titles_dic.update(missing_titles_dic)
    titles_x0_dic = {key: titles_df[titles_df.index.isin(indexes)]['x0'].min() for key, indexes in
                    title_index_dic.items()}
    sorted_titles_x0_dic = dict(sorted(titles_x0_dic.items(), key=lambda item: item[1]))
    rearranged_titles_dic = {key: titles_dic[key] for key in sorted_titles_x0_dic.keys()}
    index = 0
    for key in rearranged_titles_dic.keys():
        rearranged_titles_dic[key]['column_number'] = index
        index += 1
    return rearranged_titles_dic


def unify_titles(titles_df, titles):
    mod_df = titles_df.sort_values(by=['x0'], ascending=True)
    mod_df = mod_df.drop(columns=['found'])
    mod_df.insert(0, "found", False)
    # mod_df['word'].apply(lambda x: x.upper())
    mod_df['word'] = mod_df['word'].str.upper()

    titles = [title.upper() for title in titles]
    title_index_dic = {}

    for title in titles:
        title_index_dic[title] = []
        title_index_dic[title] = get_index_words(mod_df, title)

    return title_index_dic


def define_columns_width(titles_dic, titles_df, title_index_dic):
    columns = []
    titles_list = list(titles_dic)
    titles_list = [title.upper() for title in titles_list]
    for title_index in range(len(titles_list)):
        title = titles_list[title_index]
        left_offset = titles_dic[title]["left_offset"]
        left_offset_value = titles_dic[title]["left_offset_value"]
        right_offset = titles_dic[title]["right_offset"]
        right_offset_value = titles_dic[title]["right_offset_value"]
        exclude_regex = titles_dic[title]["exclude_regex"]

        if left_offset == 'left':
            if title_index == 0:
                x0 = 0
            else:
                prev_title = titles_list[title_index - 1]
                x0 = titles_df[titles_df.index.isin(title_index_dic[prev_title])]['x1'].max() + 1
        elif left_offset == 'center':
            if title_index == 0:
                x0 = 0
            else:
                prev_title = titles_list[title_index - 1]
                prev_x1 = titles_df[titles_df.index.isin(title_index_dic[prev_title])]['x1'].max()
                act_x0 = titles_df[titles_df.index.isin(title_index_dic[title])]['x0'].min()
                x0 = (prev_x1 + act_x0) / 2
        elif left_offset == 'right':
            if title_index == 0:
                x0 = 0
            else:
                x0 = titles_df[titles_df.index.isin(title_index_dic[title])]['x0'].min() - 1
        elif left_offset == 'fixed':
            if title_index == 0:
                x0 = 0
            else:
                x0 = titles_df[titles_df.index.isin(title_index_dic[title])]['x0'].min() - \
                     left_offset_value
        else:
            x0 = 0

        if right_offset == 'left':
            if title_index == len(titles_list) - 1:
                # Get the edge of the pdf
                x1 = 9999
            else:
                x1 = titles_df[titles_df.index.isin(title_index_dic[title])]['x1'].max() + 1
        elif right_offset == 'center':
            if title_index == len(titles_list) - 1:
                # Get the edge of the pdf
                x1 = 9999
            else:
                next_title = titles_list[title_index + 1]
                next_x0 = titles_df[titles_df.index.isin(title_index_dic[next_title])]['x0'].min()
                act_x1 = titles_df[titles_df.index.isin(title_index_dic[title])]['x1'].max()
                x1 = (next_x0 + act_x1) / 2
        elif right_offset == 'right':
            if title_index == len(titles_list) - 1:
                # Get the edge of the pdf
                x1 = 9999
            else:
                next_title = titles_list[title_index + 1]
                x1 = titles_df[titles_df.index.isin(title_index_dic[next_title])]['x0'].min() - 1
        elif right_offset == 'fixed':
            if title_index == len(titles_list) - 1:
                # Get the edge of the pdf
                x1 = 9999
            else:
                x1 = titles_df[titles_df.index.isin(title_index_dic[title])]['x1'].max() + \
                     right_offset_value
        else:
            if title_index == len(titles_list) - 1:
                # Get the edge of the pdf
                x1 = 9999
            else:
                x1 = 9999

        if exclude_regex != 'N/A':
            current_column = ColumnDef(title=title, x0=x0, x1=x1, exclude_regex=exclude_regex)
        else:
            current_column = ColumnDef(title=title, x0=x0, x1=x1)
        columns.append(current_column)

    return columns


class PDFTableExtractor:
    def __init__(self, raw_pdf_df, pdf_df):
        self.raw_pdf_df = raw_pdf_df
        self.pdf_df = pdf_df

    def locate_titles(self, titles, complete_titles):
        titles = [title.upper() for title in titles]
        self.pdf_df['word'] = self.pdf_df['word'].str.upper()
        titles_y0 = []
        titles_y1 = []
        new_found_titles_bounded_df = pd.DataFrame()
        titles_count = 0
        for title in titles:
            for title_word in title.split():
                if len(list(self.pdf_df.loc[self.pdf_df['word'] == title_word, 'y0'].values)) == 0:
                    return pd.DataFrame(columns=titles), new_found_titles_bounded_df
                titles_y0 += list(self.pdf_df.loc[self.pdf_df['word'] == title_word, 'y0'].values)
                titles_y1 += list(self.pdf_df.loc[self.pdf_df['word'] == title_word, 'y1'].values)

        most_common_y0 = Counter(titles_y0).most_common(1)[0][0]
        most_common_y1 = Counter(titles_y1).most_common(1)[0][0]
        top_bound_offset = most_common_y0 - abs(most_common_y1 - most_common_y0) * 2 - OFFSET_TITLE_CONSTANT_Y
        bottom_bound_offset = most_common_y1 + abs(most_common_y1 - most_common_y0) * 2 + OFFSET_TITLE_CONSTANT_Y
        bounded_titles_y0 = [y0 for y0 in titles_y0 if y0 > top_bound_offset]
        bounded_titles_y1 = [y1 for y1 in titles_y1 if y1 < bottom_bound_offset]

        top_bound_titles = min(bounded_titles_y0)
        bottom_bound_titles = max(bounded_titles_y1)

        titles_y_bounded_df = self.pdf_df[(self.pdf_df['y0'] >= top_bound_titles) &
                                          (self.pdf_df['y1'] <= bottom_bound_titles)]
        titles_y_bounded_df.reset_index()

        titles_x0 = []
        titles_x1 = []
        for title in titles:
            for title_word in title.split():
                titles_x0 += list(titles_y_bounded_df.loc[self.pdf_df['word'] == title_word, 'x0'].values)
                titles_x1 += list(titles_y_bounded_df.loc[self.pdf_df['word'] == title_word, 'x1'].values)

        titles_width = [abs(titles_x1[i] - titles_x0[i]) for i in range(len(titles_x1))]
        max_title_width = max(titles_width)

        left_bound_offset = min(titles_x0) - max_title_width - OFFSET_TITLE_CONSTANT_X
        right_bound_offset = max(titles_x1) + max_title_width + OFFSET_TITLE_CONSTANT_X
        bounded_titles_x0 = [x0 for x0 in titles_x0 if x0 > left_bound_offset]
        bounded_titles_x1 = [x1 for x1 in titles_x1 if x1 < right_bound_offset]
        left_bound_titles = min(bounded_titles_x0)
        right_bound_titles = max(bounded_titles_x1)

        titles_y_bounded_df = titles_y_bounded_df[
            (titles_y_bounded_df['x0'] >= left_bound_titles) & (titles_y_bounded_df['x1'] <= right_bound_titles)]

        titles_y_bounded_df = titles_y_bounded_df.iloc[(titles_y_bounded_df['y0'] - most_common_y0).abs().argsort()]
        titles_y_bounded_df = titles_y_bounded_df.reset_index(drop=True)

        titles_y_bounded_df.insert(0, 'found', False)
        for title in titles:
            for title_word in title.split():
                for current_index in titles_y_bounded_df.index[titles_y_bounded_df['word'] == title_word].tolist():
                    if titles_y_bounded_df.at[current_index, 'found']:
                        continue
                    titles_y_bounded_df.at[current_index, 'found'] = True
                    break

        titles_y_bounded_df = titles_y_bounded_df[titles_y_bounded_df['found'] == True]
        # titles_y_bounded_df = titles_y_bounded_df.drop(columns=['found'])
        titles_y_bounded_df = titles_y_bounded_df.sort_values(by=['y0'], ascending=True)
        existing_titles_bounded_df = titles_y_bounded_df.copy()
        existing_titles_bounded_df = existing_titles_bounded_df.reset_index(drop=True)


        if not complete_titles:
            top_bound_offset = most_common_y0
            bottom_bound_offset = most_common_y1
            left_bound_titles = 0
            right_bound_titles = 99999
            most_common_title_df = self.pdf_df[(self.pdf_df['y0'] >= top_bound_offset) &
                                               (self.pdf_df['y1'] <= bottom_bound_offset) &
                                               (self.pdf_df['x0'] >= left_bound_titles) &
                                               (self.pdf_df['x1'] <= right_bound_titles)]
            most_common_title_df = most_common_title_df.sort_values(by=['x0'], ascending=True)
            most_common_title_df.insert(0, 'found', False)
            new_found_titles_bounded_df = pd.concat([most_common_title_df, titles_y_bounded_df], axis=0)
            new_found_titles_bounded_df = new_found_titles_bounded_df.drop_duplicates(
                subset=['x0', 'y0', 'x1', 'y1', 'word', 'block_no', 'line_no', 'word_no'], keep=False)
            new_found_titles_bounded_df = new_found_titles_bounded_df.reset_index(drop=True)
            new_found_titles_bounded_df.index = range(len(existing_titles_bounded_df),
                                                      len(new_found_titles_bounded_df) + len(existing_titles_bounded_df))
        return existing_titles_bounded_df, new_found_titles_bounded_df

    def get_table_delimiters(self, footer_delimiter, continue_delimiter, bottom_delimiter, titles_df,
                             header_delimiter, titles_found):
        footer_delimiter = footer_delimiter.upper()
        footer_delimiter_found = False

        bottom_delimiter = bottom_delimiter.upper()
        bottom_delimiter_found = False

        header_delimiter = header_delimiter.upper()

        continue_delimiter = continue_delimiter.upper()
        continue_delimiter_found = False

        mod_df = self.pdf_df
        mod_df['word'] = mod_df['word'].str.upper()
        mod_df = mod_df.sort_values(by=['y0'], ascending=True)
        mod_df.insert(0, 'found', False)

        if titles_found:
            table_delimiter_y0 = titles_df['y1'].max()
        else:
            header_delimiter_indexes = get_index_words(mod_df, header_delimiter)
            table_delimiter_y0 = mod_df[mod_df.index.isin(header_delimiter_indexes)]['y1'].max()

        mod_df = mod_df[mod_df['y0'] >= table_delimiter_y0]

        bottom_delimiter_indexes = get_index_words(mod_df, bottom_delimiter)
        if len(bottom_delimiter.split()) == len(bottom_delimiter_indexes):
            bottom_delimiter_found = True

        mod_df = mod_df.sort_values(by=['y1'], ascending=False)
        mod_df['found'] = False

        footer_delimiter_indexes = get_index_words(mod_df, footer_delimiter)
        if len(footer_delimiter.split()) == len(footer_delimiter_indexes):
            footer_delimiter_found = True

        continue_delimiter_indexes = get_index_words(mod_df, continue_delimiter)
        if len(continue_delimiter.split()) == len(continue_delimiter_indexes):
            continue_delimiter_found = True

        if continue_delimiter_found:
            table_delimiter_y1 = self.pdf_df[self.pdf_df.index.isin(continue_delimiter_indexes)]['y0'].min()
            return [table_delimiter_y0, table_delimiter_y1, True]
        elif bottom_delimiter_found:
            table_delimiter_y1 = self.pdf_df[self.pdf_df.index.isin(bottom_delimiter_indexes)]['y0'].min()
            return [table_delimiter_y0, table_delimiter_y1, False]
        elif footer_delimiter_found:
            table_delimiter_y1 = self.pdf_df[self.pdf_df.index.isin(footer_delimiter_indexes)]['y0'].min()
            return [table_delimiter_y0, table_delimiter_y1, True]
        else:
            table_delimiter_y1 = 9999
            return [table_delimiter_y0, table_delimiter_y1, False]

    def define_rows_width(self, column_pivot, column_index, column_align, row_top_offset_value,
                          row_bot_offset_value, columns, table_delimiter_y0, table_delimiter_y1):
        column_pivot = column_pivot.upper()
        rows = []
        col_x0 = columns[column_index].x0
        col_x1 = columns[column_index].x1
        column_df = self.pdf_df[(self.pdf_df['x0'] > col_x0) &
                                (self.pdf_df['x0'] < col_x1) &
                                (self.pdf_df['y0'] > table_delimiter_y0) &
                                (self.pdf_df['y0'] < table_delimiter_y1)]
        # column_df['word'].apply(lambda x: x.upper())
        column_df['word'] = column_df['word'].str.upper()
        column_df = column_df.sort_values(by=['y0'], ascending=True).reset_index()
        column_df.insert(0, 'y0_round', column_df['y0'].apply(np.floor))
        column_df = column_df.drop_duplicates(subset=['y0_round'])
        column_df = column_df.reset_index()
        # prev_y0 = -1

        for ind in column_df.index:
            if column_align == 'top':
                if ind == 0:
                    y0 = table_delimiter_y0
                else:
                    y0 = column_df['y0'][ind]
                if ind == len(column_df.index) - 1:
                    y1 = table_delimiter_y1
                else:
                    y1 = column_df['y0'][ind + 1]

            elif column_align == 'mid':
                if ind == 0:
                    y0 = table_delimiter_y0
                    mid_distance = column_df['y0'][ind] - table_delimiter_y0
                else:
                    y0 = rows[-1].y1
                    mid_distance = column_df['y0'][ind] - rows[-1].y1
                if ind == len(column_df.index) - 1:
                    y1 = table_delimiter_y1
                else:
                    y1 = column_df['y1'][ind] + mid_distance
            elif column_align == 'bot':
                if ind == 0:
                    y0 = table_delimiter_y0
                else:
                    y0 = column_df['y1'][ind - 1]
                if ind == len(column_df.index) - 1:
                    y1 = table_delimiter_y1
                else:
                    y1 = column_df['y1'][ind]
            elif column_align == 'fixed':
                if ind == 0:
                    y0 = table_delimiter_y0
                else:
                    y0 = column_df['y0'][ind] + row_top_offset_value
                if ind == len(column_df.index) - 1:
                    y1 = table_delimiter_y1
                else:
                    y1 = column_df['y1'][ind] + row_bot_offset_value
            else:
                y0 = 0
                y1 = 0

            # if prev_y0 - 2 >= y0 or y0 >= prev_y0 + 2:
            current_row = RowDef(y0=y0, y1=y1)
            rows.append(current_row)
                # prev_y0 = y0

        return rows

    def get_text_from_coordinates(self, x0, y0, x1, y1, exclude_regex):
        section_df = self.raw_pdf_df[(self.raw_pdf_df['x0'] >= x0) &
                                     (self.raw_pdf_df['x0'] < x1) &
                                     (self.raw_pdf_df['y0'] >= y0) &
                                     (self.raw_pdf_df['y0'] < y1)]
        section_df = section_df.sort_values(by=['block_no', 'line_no', 'word_no'],
                                            ascending=[True, True, True], na_position='first').reset_index()
        text_in_section = ''
        prev_y = 0
        for ind in section_df.index:
            curr_y = section_df['y0'][ind]
            curr_text = section_df['word'][ind]
            exclude_text = False
            if exclude_regex:
                for regex in exclude_regex:
                    for word_regex in regex.split():
                        if re.match(word_regex, str(curr_text)):
                            exclude_text = True
            if not exclude_text:
                if text_in_section == '':
                    text_in_section += section_df['word'][ind]
                else:
                    if prev_y - 1 <= curr_y <= prev_y + 1:
                        text_in_section += " " + section_df['word'][ind]
                    else:
                        text_in_section += "\n" + section_df['word'][ind]
                prev_y = curr_y
        return text_in_section

    def create_extracted_table(self, rows, columns, page):
        data = {}
        for row in rows:
            y0 = row.y0
            y1 = row.y1
            for column in columns:
                title = column.title
                x0 = column.x0
                x1 = column.x1
                exclude_regex = column.exclude_regex
                cell_text = self.get_text_from_coordinates(x0=x0, y0=y0, x1=x1, y1=y1, exclude_regex=exclude_regex)
                if title in data.keys():
                    data[title].append(cell_text)
                else:
                    data[title] = [cell_text]
            if "page" in data.keys():
                data["page"].append(page)
            else:
                data["page"] = [page]

        table_df = pd.DataFrame(data)
        return table_df

