import socket
import paramiko
import selectors
from time import monotonic as _time

__all__ = ["ssh"]

# Tunable parameters
DEBUGLEVEL = 0

if hasattr(selectors, 'PollSelector'):
    _SshSelector = selectors.PollSelector
else:
    _SshSelector = selectors.SelectSelector


class ssh:

    """ssh interface class.
    An instance of this class represents a connection to a ssh
    server.  The instance is initially not connected; the open()
    method must be used to establish a connection.  Alternatively, the
    host name and optional port number can be passed to the
    constructor, too.
    Don't try to reopen an already connected instance.
    This class has many read_*() methods.  Note that some of them
    raise EOFError when the end of the connection is read, because
    they can return an empty string for other reasons.  See the
    individual doc strings.
    read_until(expected, [timeout])
            Read until the expected string has been seen, or a timeout is
            hit (default is no timeout); may block.
    read_all()
            Read all data until EOF; may block.
    read_some()
            Read at least one byte or EOF; may block.
    read_very_eager()
            Read all data available already queued or on the socket,
            without blocking.
    read_eager()
            Read either data already queued or some data available on the
            socket, without blocking.
    read_lazy()
            Read all data in the raw queue (processing it first), without
            doing any socket I/O.
    read_very_lazy()
            Reads all data in the cooked queue, without doing any socket
            I/O.
    """

    def __init__(self, host=None, port=22, username='test', password='test', compress=False,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """
        Constructor.
        When called without arguments, create an unconnected instance.
        With a hostname argument, it connects the instance; port number
        and timeout are optional.
        """
        self.debuglevel = DEBUGLEVEL
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.compress = compress
        self.timeout = timeout
        self.sock = None
        self.rawq = b''
        self.cookedq = b''
        self.eof = 0
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.host:
            self.open(host, port, username, password, compress, timeout)

    def open(self, host, port, username, password, compress, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """
        Connect to a host.
        Don't try to reopen an already connected instance.
        """
        self.ssh_client.connect(host, port, username,
                                password, compress=compress, timeout=timeout)
        self.channel = self.ssh_client.invoke_shell(width=65278, height=65278)
        self.ssh_fileno = self.fileno()

    def sftp(self):
        tran = self.client.get_transport()
        sftp = paramiko.SFTPClient.from_transport(tran)
        return sftp

    def __del__(self):
        """Destructor -- close the connection."""
        self.close()

    def msg(self, msg, *args):
        """Print a debug message, when the debug level is > 0.
        If extra arguments are present, they are substituted in the
        message using the standard string formatting operator.
        """
        if self.debuglevel > 0:
            print('ssh(%s,%s):' % (self.host, self.port), end='')
            if args:
                print(msg % args)
            else:
                print(msg)

    def set_debuglevel(self, debuglevel):
        """
        Set the debug level.
        The higher it is, the more debug output you get (on sys.stdout).
        """
        self.debuglevel = debuglevel

    def close(self):
        """Close the connection."""
        self.eof = 1
        self.ssh_client.close()

    # def get_socket(self):
        # """Return the socket object used internally."""
        # return self.sock

    def fileno(self):
        """Return the fileno() of the socket object used internally."""
        return self.channel.fileno()

    def write(self, buffer):
        """
        Write a string to the socket.
        Can block if the connection is blocked.  May raise
        socket.error if the connection is closed.
        """
        self.msg("send %r", buffer)
        self.channel.sendall(buffer.decode())

    def read_until(self, match, timeout=None):
        """Read until a given string is encountered or until timeout.

        When no match is found, return whatever is available instead,
        possibly the empty string.  Raise EOFError if the connection
        is closed and no cooked data is available.
        """
        n = len(match)
        self.process_rawq()
        i = self.cookedq.find(match)
        if i >= 0:
            i = i+n
            buf = self.cookedq[:i]
            self.cookedq = self.cookedq[i:]
            return buf
        if timeout is not None:
            deadline = _time() + timeout
        with _SshSelector() as selector:
            selector.register(self, selectors.EVENT_READ)
            while not self.eof:
                if selector.select(timeout):
                    i = max(0, len(self.cookedq)-n)
                    self.fill_rawq()
                    self.process_rawq()
                    i = self.cookedq.find(match, i)
                    if i >= 0:
                        i = i+n
                        buf = self.cookedq[:i]
                        self.cookedq = self.cookedq[i:]
                        return buf
                    if timeout is not None:
                        timeout = deadline - _time()
                        if timeout < 0:
                            break
        return self.read_very_lazy()

    def read_all(self):
        """Read all data until EOF; block until connection closed."""
        self.process_rawq()
        while not self.eof:
            self.fill_rawq()
            self.process_rawq()
        buf = self.cookedq
        self.cookedq = b''
        return buf

    def read_some(self):
        """
        Read at least one byte of cooked data unless EOF is hit.
        Return '' if EOF is hit.  Block if no data is immediately
        available.
        """
        self.process_rawq()
        while not self.cookedq and not self.eof:
            self.fill_rawq()
            self.process_rawq()
        buf = self.cookedq
        self.cookedq = b''
        return buf

    def read_very_eager(self):
        """Read everything that's possible without blocking in I/O (eager).
        Raise EOFError if connection closed and no cooked data
        available.  Return '' if no cooked data available otherwise.
        Don't block unless in the midst of an IAC sequence.
        """
        self.process_rawq()
        while not self.eof and self.sock_avail():
            self.fill_rawq()
            self.process_rawq()
        return self.read_very_lazy()

    def read_eager(self):
        """
        Read readily available data.
        Raise EOFError if connection closed and no cooked data
        available.  Return '' if no cooked data available otherwise.
        Don't block unless in the midst of an IAC sequence.
        """
        self.process_rawq()
        while not self.cookedq and not self.eof and self.sock_avail():
            self.fill_rawq()
            self.process_rawq()
        return self.read_very_lazy()

    def read_lazy(self):
        """
        Process and return data that's already in the queues (lazy).
        Raise EOFError if connection closed and no data available.
        Return '' if no cooked data available otherwise.  Don't block
        unless in the midst of an IAC sequence.
        """
        self.process_rawq()
        return self.read_very_lazy()

    def read_very_lazy(self):
        """
        Return any data available in the cooked queue (very lazy).
        Raise EOFError if connection closed and no data available.
        Return '' if no cooked data available otherwise.  Don't block.
        """
        buf = self.cookedq
        self.cookedq = b''
        if not buf and self.eof and not self.rawq:
            raise EOFError('ssh connection closed')
        return buf

    def process_rawq(self):
        """
        Transfer from raw queue to cooked queue.
        Set self.eof when connection is closed.
        """
        self.cookedq = self.cookedq + self.rawq
        self.rawq = b''

    def fill_rawq(self):
        """
        Fill raw queue from exactly one recv() system call.
        Block if no data is immediately available.  Set self.eof when
        connection is closed.
        """
        # The buffer size should be fairly small so as to avoid quadratic
        # behavior in process_rawq() above

        buf = self.channel.recv(50)
        self.msg("recv %r", buf)
        self.eof = (not buf)
        self.rawq = self.rawq + buf

    def sock_avail(self):
        """Test whether data is available on the socket."""
        return self.channel.recv_ready()

    def expect(self, list, timeout=None):
        """
        Read until one from a list of a regular expressions matches.
        The first argument is a list of regular expressions, either
        compiled (re.RegexObject instances) or uncompiled (strings).
        The optional second argument is a timeout, in seconds; default
        is no timeout.
        Return a tuple of three items: the index in the list of the
        first regular expression that matches; the match object
        returned; and the text read up till and including the match.
        If EOF is read and no text was read, raise EOFError.
        Otherwise, when nothing matches, return (-1, None, text) where
        text is the text received so far (may be the empty string if a
        timeout happened).
        If a regular expression ends with a greedy match (e.g. '.*')
        or if more than one expression can match the same input, the
        results are undeterministic, and may depend on the I/O timing.
        """
        re = None
        list = list[:]
        indices = range(len(list))
        for i in indices:
            if not hasattr(list[i], "search"):
                if not re:
                    import re
                list[i] = re.compile(list[i])
        if timeout is not None:
            deadline = _time() + timeout
        with _SshSelector() as selector:
            selector.register(self, selectors.EVENT_READ)
            while not self.eof:
                self.process_rawq()
                for i in indices:
                    m = list[i].search(self.cookedq)
                    if m:
                        e = m.end()
                        text = self.cookedq[:e]
                        self.cookedq = self.cookedq[e:]
                        return (i, m, text)
                if timeout is not None:
                    ready = selector.select(timeout)
                    timeout = deadline - _time()
                    if not ready:
                        if timeout < 0:
                            break
                        else:
                            continue
                self.fill_rawq()
        text = self.read_very_lazy()
        if not text and self.eof:
            raise EOFError
        return (-1, None, text)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
