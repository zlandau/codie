import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import models
from models import Tag, SourceFile

Session = sessionmaker()

class TagDatabase:
    def __init__(self, dbpath):
        # XXX: probably support :memory: if no path is passed
        # Also.. you know.. use the path
        engine = create_engine('sqlite:///sourceserver.db', echo=True)
        Session.configure(bind=engine)
        self.session = Session()
        models.create_all(engine)

    def add_tags(self, tags):
        self.session.add_all(tags)
        self.session.commit()

    def remove_tags_for_file(self, filename):
        self.session.query(Tag).filter_by(filename=filename).delete()
        self.session.commit()

    def update_tags_for_file(self, filename, tags):
        # At least now we just drop and replace
        self.session.query(Tag).filter_by(filename=filename).delete()
        self.session.add_all(tags)
        self.session.commit()

    def output_ctags(self, filename):
        with open(filename, "w") as f:
            for t in self.tags():
                f.write(t.ctag() + "\n")

    def tags(self):
        for t in self.session.query(Tag).order_by(Tag.name):
            yield t

if __name__ == "__main__":
    db = TagDatabase("/some/path")
    sf = SourceFile("hello.c")
    db.add_tags(sf.tags())
    for t in db.tags():
        print(t)
    db.update_tags_for_file("hello.c", sf.tags())
    for t in db.tags():
        print(t)
    print(db.output_ctags("tags.generated"))


