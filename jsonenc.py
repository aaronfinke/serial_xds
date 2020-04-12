from json import JSONEncoder
import pathlib

class JSONEnc(JSONEncoder):
        def default(self, o):
            if type(o) == pathlib.PosixPath:
                return o.__str__()
            else:
                return o.__dict__
