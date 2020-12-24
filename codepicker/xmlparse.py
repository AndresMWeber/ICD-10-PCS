from typing import Dict, List
from pprint import pprint
import xmltodict
import json
import collections.abc
from tabulate import tabulate
import time


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class PCSTables:
    def __init__(self, data_set: List):
        self.merged_tables = {}
        self.tables = []
        self._data_set = data_set
        self.process_data_set()

    def process_data_set(self):
        total_data_sets = len(self._data_set)
        for (i, data_table) in enumerate(self._data_set):
            self.tables.append(PCSTable(data_table))
        self.set_merged_tables()

    def set_merged_tables(self):
        self.merged_tables = {}

        for t in self.tables:
            update(self.merged_tables, t.processed)

    def get_description(self, input_code):
        input_code = input_code.upper()
        print(
            '--------\nRetrieving description for code: "{}"\n--------\n'.format(
                input_code
            )
        )
        ptr = self.merged_tables
        parent_ptr = {}
        description = []
        # pprint(self.merged_tables[input_code[0]])

        for (i, char) in enumerate(input_code):
            # print("{}: Checking for character {} in {}".format(i, char, ptr.keys()))
            # i > 3 and pprint([ptr, parent_ptr])
            if len(ptr.keys()) != 1:
                parent_ptr = ptr
            else:
                ptr = parent_ptr["_options"]
                # print("the parent options might...", ptr.keys())
            ptr = ptr[char]
            description.append(
                [
                    char,
                    ptr.get("title"),
                    ptr.get("label"),
                    ptr.get("definition"),
                ]
            )
        return description

    def print_table(self, input_code):
        try:
            descr = self.get_description(input_code)
            print(
                tabulate(
                    descr,
                    headers=["code", "title", "description", "detail"],
                    tablefmt="orgtbl",
                )
            )
        except:
            print("Could not find a match for code: {}".format(input_code))


class PCSTable(object):
    def __init__(self, raw_data: Dict):
        self._raw = raw_data
        self.processed = {}
        self.process_raw_data()

    def process_raw_data(self):
        self.processed.clear()
        axes = self._raw["axis"]
        pcs_rows = self._raw["pcsRow"]
        axis_inner_ptr = self.process_axis(axes, self.processed)
        self.process_pcs_rows(pcs_rows, axis_inner_ptr)

    def process_axis(self, axes: List, sub_dict: Dict):
        sorted_axes = sorted(axes, key=lambda e: e["@pos"])

        for axis in sorted_axes:
            if isinstance(axis["label"], list):
                self.process_label_list(axis["label"], sub_dict)
                sub_dict["_options"] = sub_dict.get("_options", {})
                sub_dict = sub_dict["_options"]
            else:
                code = axis["label"]["@code"]
                sub_dict[code] = self.axis_to_entry(axis)
                sub_dict = sub_dict[code]

        return sub_dict

    def process_label_list(self, label_list: List, sub_dict: Dict):
        tmp = sub_dict
        for label in label_list:
            code = label["@code"]
            sub_dict[code] = {"title": label["#text"]}

    def process_pcs_rows(self, row: Dict, sub_dict: Dict):
        if not isinstance(row, list):
            row = [row]
        for column in row:
            self.process_axis(column["axis"], sub_dict)

    @staticmethod
    def axis_to_entry(axis: Dict):
        output = {}
        output["title"] = axis.get("title")
        output["definition"] = axis.get("definition")
        output["label"] = axis.get("label", {}).get("#text")
        return output


print("Reading/Parsing XML")
with open("data/icd10pcs_tables_2020.xml", "r") as file:
    data = xmltodict.parse(file.read())
    start = time.time()
    table = PCSTable(data["ICD10PCS.tabular"]["pcsTable"][20])
    tables = PCSTables(data["ICD10PCS.tabular"]["pcsTable"])
    print("Finished parsing in {} seconds".format(time.time() - start))
    codes = [
        "Bq0dzzz",
        "Bp2jyzz",
        "Bn25zzz",
        "Bw25zzz",
        "B54bzzz",
        "Bz25yzz",
        "Bw04zzz",
        "Bw03zzz",
        "b00bzzz",
    ]
    [tables.print_table(code) for code in codes]
