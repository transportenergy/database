import json
import os


class CountryCodeManager:

    def __init__(self):
        main_path = "{}/{}".format(os.getcwd(), "util")
        self.iso_code_path = "{}/iso_codes.json".format(main_path)
        self.item_code_path = "{}/item_regions.json".format(main_path)

        with open(self.iso_code_path) as json_file:
            self.iso_codes = json.load(json_file)

        with open(self.item_code_path) as json_file:
            self.item_regions = json.load(json_file)

    def get_iso_code_for_country(self, country_name):
        country_name = country_name.capitalize()
        if country_name in self.iso_codes:
            return self.iso_codes[country_name]
        else:
            return "N/A"

    def get_item_region_for_iso_code(self, iso_code):
        iso_code = iso_code.upper()
        for region in self.item_regions:
            codes_for_region = self.item_regions[region]
            if iso_code in codes_for_region:
                return region

        return "N/A"

    def get_iso_codes(self):
        return self.iso_codes

    def get_item_regions(self):
        return self.item_regions
