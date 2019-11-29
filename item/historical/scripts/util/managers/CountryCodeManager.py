import json
import os


class CountryCodeManager:

    def __init__(self):
        main_path = "{}/{}".format(os.getcwd(), "util/json")
        self.iso_code_path = "{}/iso_codes.json".format(main_path)
        self.item_code_path = "{}/item_regions.json".format(main_path)

        with open(self.iso_code_path) as json_file:
            self.iso_codes = json.load(json_file)

        with open(self.item_code_path) as json_file:
            self.item_regions = json.load(json_file)

    def get_iso_code_for_country(self, country_name):
        country_name = country_name.lower()
        if country_name in self.iso_codes:
            return self.iso_codes[country_name].upper()
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

    def get_list_of_countries_with_no_iso_code(self, list_of_country_names):
        # Variable for storing all the countries with no ISO code
        countries_with_no_ISO_code = []

        # For each country, get their ISO code
        for country in list_of_country_names:
            iso_code = self.get_iso_code_for_country(country)
            if iso_code == "N/A":
                countries_with_no_ISO_code.append(country)

        return countries_with_no_ISO_code

    def get_list_of_iso_for_countries(self, list_of_country_names):
        list_of_iso_codes = []
        for country in list_of_country_names:
            iso_code = self.get_iso_code_for_country(country)
            list_of_iso_codes.append(iso_code)

        # Assert the result list and passed list are the same size
        assert len(list_of_iso_codes) == len(list_of_country_names)

        return list_of_iso_codes

    def get_list_of_iso_codes_with_no_region(self, list_of_iso_codes):
        # ISO code with missing region
        iso_code_with_no_region = []

        # For each ISO code, find the ITEM region
        for code in list_of_iso_codes:
            region = self.get_item_region_for_iso_code(code)
            if region == "N/A":
                iso_code_with_no_region.append(code)

        return iso_code_with_no_region

    def get_list_of_regions_for_iso_codes(self, list_of_iso_codes):
        item_region = []

        # Getting the list of regions
        for code in list_of_iso_codes:
            region = self.get_item_region_for_iso_code(code)
            item_region.append(region)

        # Ensure the list of item_region and list iso codes are the same size
        assert len(item_region) == len(list_of_iso_codes)

        return item_region
