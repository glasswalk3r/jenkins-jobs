import xmltodict
import pytest


class Helpers:

    @staticmethod
    def xml_config(xml_filename):
        with open(f'tests/raw_data/{xml_filename}', 'r') as fp:
            config = xmltodict.parse(fp.read())

        return config


@pytest.fixture
def helpers():
    return Helpers
