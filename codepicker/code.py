import re


class Code:
    validation_regex = "^\w{7}$"

    def __init__(self):
        self._code = None

    @property
    def code(self, value):
        return self._code

    @code.setter
    def code(self, value):
        if self.validateCode(value):
            self._code = value
        else:
            raise ValueError("Incorrect code input: {}".format(value))

    def description(self):
        return "This is a default description of a code"

    @staticmethod
    def validateCode(code):
        return re.match(validation_regex, code)


scan_types = {"x-ray": 0, "ct": 2, "mri": 3}


class RadiologyCode(Code):
    validation_regex = "^B\w{6}$"

    def __init__(
        self,
        body_part=0,
        body_system=0,
        scan_type="x-ray",
        contrast_used=False,
    ):
        super().__init__()
        self.section = "B"
        self.body_part = body_part
        self.body_system = body_system
        self.scan_type = scan_type
        self.contrast_used = contrast_used
        self.qualifier_a = "Z"
        self.qualifier_b = "Z"

    @property
    def code(self, value):
        return "{SECTION}{PART}{SYSTEM}{SCAN}{CONTRAST}{Q1}{Q2}}".format(
            SECTION=self.section,
            SCAN=scan_types[self.scan_type],
            PART=self.body_part,
            SYSTEM=self.body_system,
            CONTRAST=int(self.contrast_used),
            Q1=self.qualifier_a,
            Q2=self.qualifier_b,
        )
