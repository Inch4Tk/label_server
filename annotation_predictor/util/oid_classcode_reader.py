import json

from settings import oid_classcodes, oid_classcodes_inverted

class OIDClassCodeReader:
    def __init__(self):
        """
        Initiate an object representing a json-file which maps class-codes to human readable objects
        """
        with open(oid_classcodes, 'r') as f:
            self.cc_to_human_readable_dict = json.load(f)

        with open(oid_classcodes_inverted, 'r') as f:
            self.human_readable_to_cc_dict = json.load(f)

    def __enter__(self):
        return self

    def get_human_readable_label_for_code(self, classcode: str) -> str:
        """
        Get human readable object name from a classcode of OID dataset
        Args:
            classcode: code from OID Dataset

        Returns: Human readable class name
        """
        if classcode in self.cc_to_human_readable_dict:
            return self.cc_to_human_readable_dict[classcode]
        else:
            return ''

    def get_code_for_human_readable_class(self, cls: str) -> str:
        """
        Get class code of OID from a human readable label
        Args:
            cls: human readable class name

        Returns: class code of given class in OID
        """
        if cls in self.human_readable_to_cc_dict:
            return self.human_readable_to_cc_dict[cls]
        else:
            return ''
