from tagdatabase import TagDatabase
from watchman import Watchman
from models import SourceFile
import os

CTAGS_WRITE_TIME = 10
TAGFILE = "tags.generated"

ctags_timer = None

def ctags_cb(watcher, revents):
    db.output_ctags(TAGFILE)

def files_cb(files):
    for f in files:
        if f.deleted:
            db.remove_tags_for_file(f.name)
        else:
            tags = SourceFile(f.name)
            db.update_tags_for_file(f.name, tags.tags())
    if not os.path.exists(TAGFILE):
        db.output_ctags(TAGFILE)
    else:
        if ctags_timer.remaining < 0.1:
            ctags_timer.set(CTAGS_WRITE_TIME, 0)
            ctags_timer.start()

db = TagDatabase("/some/path")

def start(loop):
    global ctags_timer

    ctags_timer = loop.timer(CTAGS_WRITE_TIME, 0, ctags_cb)

    watchman = Watchman(loop, "/Users/zacharyl/projects/sourceserver", files_cb)
    watchman.start()

    ctags_timer.start()
