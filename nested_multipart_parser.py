from rest_framework import parsers
import re

class NestedMultipartParser(parsers.MultiPartParser):
    """
    Parser for processing nested field values as well as multipart files.
    Author: Ahmed H. Ismail.
    """

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(stream=stream, media_type=media_type, parser_context=parser_context)
        data = {}
        for key, value in result.data.items():
            analyze_key(key, value, data)
        for key, value in result.files.items():
            analyze_key(key, value, data)

        print(data)
        return parsers.DataAndFiles(data, result.files)


def analyze_key(key: str, value, final_data):


    #All Cases:
    #   -  Only one key:
    #       "key"
    #   - Only one key in "[]":
    #       "[key]"
    #   - Two keys (or more). More must be in "[key]"
    #       "key[key2]..."
    #   - Two keys (or more) in "[]". More must be in "[key]"
    #       "[key][key2]..."
    #   - Two keys with array
    #       "key[array_index][key2]..."
    #   - Two keys with array in "[]"
    #       "[key][array_index][key2]..."


    #All regex:
    key_regex = "[a-zA-Z]+\w*"
    key_inside_brackets = "\[" + key_regex + "\]"
    array_index = "\[[0-9]+\]"
    case_1 = "^" + key_regex + "$"
    case_2 = "^" + key_inside_brackets + "$"
    case_3 = "^" + key_regex + key_inside_brackets
    case_4 = "^" + key_inside_brackets + key_inside_brackets
    case_5 = "^" + key_regex + array_index + key_inside_brackets
    case_6 = "^" + key_inside_brackets + array_index + key_inside_brackets


    # Check all cases:
    case_1_search = re.search(case_1, key)
    case_2_search = re.search(case_2, key)
    case_3_search = re.search(case_3, key)
    case_4_search = re.search(case_4, key)
    case_5_search = re.search(case_5, key)
    case_6_search = re.search(case_6, key)

    if case_1_search:
        final_data[key] = value
    elif case_2_search:
        final_data[key.replace("[", "").replace("]", "")] = value
    elif case_3_search:
        regex_first_bracket_index = key.index('[')
        regex_second_bracket_index = key.index(']')
        key_1 = key[:regex_first_bracket_index]
        final_data[key_1] = {}

        if key[regex_second_bracket_index + 1:] == "":
            key_2 = key[regex_first_bracket_index + 1: regex_second_bracket_index]
            final_data[key_1][key_2] = value
        else:
            analyze_key(key[regex_first_bracket_index:], value, final_data[key_1])

    elif case_4_search:
        open_brackets_indexes = [m.start() for m in re.finditer("\[", key)]
        close_brackets_indexes = [m.start() for m in re.finditer("]", key)]
        key_1 = key[open_brackets_indexes[0] + 1:close_brackets_indexes[0]]
        final_data[key_1] = {}

        if key[close_brackets_indexes[1] + 1:] == "":
            key_2 = key[open_brackets_indexes[1] + 1: close_brackets_indexes[1]]
            final_data[key_1][key_2] = value
        else:
            analyze_key(key[open_brackets_indexes[1]:], value, final_data[key_1])
    elif case_5_search:
        open_brackets_indexes = [m.start() for m in re.finditer("\[", key)]
        close_brackets_indexes = [m.start() for m in re.finditer("]", key)]
        key_1 = key[:open_brackets_indexes[0]]
        index = int(key[open_brackets_indexes[0] + 1:close_brackets_indexes[0]])
        try:
            final_data[key_1]
        except KeyError:
            final_data[key_1] = []

        if not isinstance(final_data[key_1], list):
            final_data[key_1] = []


        while len(final_data[key_1]) <= index:
            final_data[key_1].append({})
        if key[close_brackets_indexes[1] + 1:] == "":
            key_2 = key[open_brackets_indexes[1] + 1: close_brackets_indexes[1]]
            final_data[key_1][index][key_2] = value
        else:
            analyze_key(key[open_brackets_indexes[1]:], value, final_data[key_1][index])

    elif case_6_search:
        open_brackets_indexes = [m.start() for m in re.finditer("\[", key)]
        close_brackets_indexes = [m.start() for m in re.finditer("]", key)]
        key_1 = key[open_brackets_indexes[0] + 1:close_brackets_indexes[0]]
        index = int(key[open_brackets_indexes[1] + 1:close_brackets_indexes[1]])
        try:
            final_data[key_1]
        except KeyError:
            final_data[key_1] = []

        if not isinstance(final_data[key_1], list):
            final_data[key_1] = []

        while len(final_data[key_1]) <= index:
            final_data[key_1].append({})

        if key[close_brackets_indexes[2] + 1:] == "":
            key_2 = key[open_brackets_indexes[2] + 1: close_brackets_indexes[2]]
            final_data[key_1][index][key_2] = value
        else:
            analyze_key(key[open_brackets_indexes[2]:], value, final_data[key_1][index])