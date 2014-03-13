import pyev
import signal
import tagservice

def sib_cb(watcher, revents):
    loop.stop(pyev.EVBREAK_ALL)

loop = pyev.default_loop()

sig = loop.signal(signal.SIGINT, sib_cb)
sig.start()

tagservice.start(loop)
loop.start()
