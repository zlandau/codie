from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import tempfile
import subprocess

CTAGS_BINARY = "/usr/local/bin/ctags"

Base = declarative_base()

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    filename = Column(String)
    address = Column(String)

    def ctag(self):
        return "\t".join([self.name, self.filename, self.address])

    def __repr__(self):
        return "<Tag(name='%s', filename='%s', address'%s')>" % (
            self.name, self.filename, self.address)

class WatchedFile:
    def __init__(self, name, deleted=False):
        self.name = name
        self.deleted = deleted

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

def create_all(engine):
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    tag = Tag(name='somename', filename='/path/to', address='/hey/')
