from models import WatchedFile
from whizzer.client import UnixClient
from whizzer.protocol import ProtocolFactory, Protocol
import json
import socket
import subprocess

class Unavailable(Exception):
    def __init__(self, msg, warn=True, invalidate=False):
        self.msg = msg
        self.warn = warn
        self.invalidate = invalidate
    def __str__(self):
        if self.warn:
            return 'warning: watchman unavailable: %s' % self.msg
        else:
            return 'watchman unavailable: %s' % self.msg

class WatchmanProtocol(Protocol):
    def __init__(self, loop):
        Protocol.__init__(self, loop)
        self.response_cb = None

    def connection_made(self, address):
        self.send_command("get-sockname")

    def data(self, data):
        data = data.decode("utf-8")
        nwl = data.find("\n")
        while nwl > 0:
            rsp = data[:nwl]
            data = data[nwl+1:]
            print(json.loads(rsp))
            self.handle_command(json.loads(rsp))
            nwl = data.find("\n")

    def send_command(self, *args):
        cmd = json.dumps(args) + "\n"
        self.transport.write(cmd.encode('utf-8'))

    def handle_command(self, cmd):
        if 'subscription' in cmd:
            self.response_cb(cmd)
        else:
            self.response_cb(cmd)

class Watchman(UnixClient):
    def __init__(self, loop, path, files_cb):
        factory = ProtocolFactory()
        factory.protocol = WatchmanProtocol
        UnixClient.__init__(self, loop, factory, path)
        self.factory = factory
        self.path = path
        self.loop = loop
        self.files_cb = files_cb

    def command(self, *args):
        try:
            return self._command(*args)
        except Unavailable:
            self._unavailable = True
            raise

    def connect(self, timeout=5.0):
        # query watchman over the command line for the socket name
        cmd = ['watchman', 'get-sockname']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        exitcode = p.poll()

        if exitcode:
            raise Unavailable('watchman exited with code %d' % exitcode)

        result = json.loads(stdout.decode('utf-8'))
        if 'error' in result:
            raise Unavailable('watchman socket discovery error: "%s"' %
                              result['error'])

        sockname = result['sockname']
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        return self._connect(sock, sockname, 5.0)

    def start(self):
        d = self.connect()
        d.add_callback(self.start_watch)

    def start_watch(self, protocol):
        protocol.send_command("watch", self.path)
        protocol.send_command("subscribe", self.path, "tagserver", {"expression": ["allof", ["type", "f"], ["not", "empty"], ["suffix", "php"]], "fields": ["name", "exists"]})
        protocol.response_cb = self.response_cb

    def response_cb(self, cmd):
        if 'files' in cmd:
            files = []
            for f in cmd['files']:
                name = f['name']
                exists = f['exists']
                files.append(WatchedFile(name, deleted=not exists))
            self.files_cb(files)

if __name__ == "__main__":
    import pyev
    import signal

    def sig_cb(watcher, revents):
        loop.stop(pyev.EVBREAK_ALL)

    loop = pyev.default_loop()
    watchman = Watchman(loop,
                    "/Users/zacharyl/projects/sourceserver",
                    files_cb)

    watchman.start()
    sig = loop.signal(signal.SIGINT, sig_cb)
    sig.start()

    loop.start()
