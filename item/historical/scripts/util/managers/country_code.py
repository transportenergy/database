import pycountry
import yaml

from item.common import paths


class CountryCodeManager:
    def __init__(self):
        self.country_mapping = {}
        for country in pycountry.countries:
            code = country.alpha_3
            name = country.name.lower()
            official_name = (
                country.official_name.lower()
                if hasattr(country, "official_name")
                else ""
            )
            common_name = (
                country.common_name.lower() if hasattr(country, "common_name") else ""
            )

            self.country_mapping[name] = code
            if official_name:
                self.country_mapping[official_name] = code
            if common_name:
                self.country_mapping[common_name] = code

        regions_file = paths["data"] / "model" / "regions.yaml"
        with open(regions_file) as file:
            self.regions_list = yaml.load(file, Loader=yaml.FullLoader)

    def get_list_of_all_countries(self):
        return list(pycountry.countries)

    def get_iso_code_for_country(self, country_name):
        country_name = country_name.lower()
        iso_code = self.country_mapping.get(country_name)

        if iso_code:
            return iso_code
        else:
            return "N/A"

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

    def get_item_region_for_iso_code(self, iso_code):
        iso_code = iso_code.upper()

        for region in list(self.regions_list.keys()):
            countries_for_region = self.regions_list[region]["countries"]
            if iso_code in countries_for_region:
                return region

        return "N/A"

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
