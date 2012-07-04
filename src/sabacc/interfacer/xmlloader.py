# TODO: Fix (or replace) xml_tools so we don't need this

from cStringIO import StringIO
import sys

from old_sabacc.back import xml_tools


class XMLToolsError(Exception):

    pass


def load_file(filename):
    real_stderr = sys.stderr
    fake_stderr = StringIO()
    try:
        sys.stderr = fake_stderr
        output = xml_tools.load_file(filename)
    finally:
        sys.stderr = real_stderr
        fake_stderr.seek(0)
    if output:
        return xml_tools.doc
    raise XMLToolsError(fake_stderr.read())
