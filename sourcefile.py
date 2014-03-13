# XXX: move to models?

import tempfile
import subprocess
from collections import namedtuple

from models import Tag

CTAGS_BINARY = "/usr/local/bin/ctags"

class SourceFile:
    def __init__(self, filename):
        self.filename = filename

    def tags(self):
        tmpfile = tempfile.NamedTemporaryFile()
        proc = subprocess.Popen([CTAGS_BINARY, '-f', '-', self.filename],
                stdout = subprocess.PIPE)
        for line in proc.stdout:
            name, filename, address, _, = str(line).split('\\t')
            yield Tag(name=name, filename=filename, address=address)


if __name__ == "__main__":
    sf = SourceFile("hello.c")
    for tag in sf.tags():
        print(tag)

