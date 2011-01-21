import zmq

context = zmq.Context()

RESERVED_NAMES = set(["_stopserver", "_list", "_socket", "_funcs"])

try:
    unicode
except NameError:
    unicode = str
    
def asbytes(x):
    if isinstance(x, unicode):
        return x.encode("utf-8")
    return x

class Server(object):
    def __init__(self, endpoint):
        self.funcs = {}
        self.socket = context.socket(zmq.REP)
        self.socket.bind(endpoint)
    
    def expose(self, func):
        if func.__name__ in RESERVED_NAMES:
            raise KeyError("%s is a reserved name" % func.__name__)
        self.funcs[func.__name__] = func
        return func
    
    def expose_as(self, name):
        if name in RESERVED_NAMES:
            raise KeyError("%s is a reserved name" % name)
        def dec(func):
            self.funcs[name] = func
            return func
        return dec
    
    def run(self):
        while True:
            fname = self.socket.recv()
            print(fname)
            if fname == b"_stopserver":
                break
            elif fname == b"_list":
                self.socket.send_multipart([asbytes(f) for f in self.funcs])
            else:
                args, kwargs = self.socket.recv_pyobj()
                result = self.funcs[fname.decode("utf-8")](*args, **kwargs)
                self.socket.send_pyobj(result)


class RpcFunctionWrapper(object):
    def __init__(self, name, rpcsocket):
        self.name = name
        self.rpcsocket = rpcsocket
    
    def __call__(self, *args, **kwargs):
        self.rpcsocket.send(asbytes(self.name), flags=zmq.SNDMORE)
        self.rpcsocket.send_pyobj((args, kwargs))
        return self.rpcsocket.recv_pyobj()


class Client(object):
    _funcs = None    # Make this exist so __getattr__ doesn't recurse
    def __init__(self, endpoint):
        self._socket = context.socket(zmq.REQ)
        self._socket.connect(endpoint)
        self._socket.send(b"_list")
        self._funcs = set(f.decode("utf-8") for f in self._socket.recv_multipart())
        
    def __getattr__(self, name):
        if name in self._funcs:
            return RpcFunctionWrapper(name, self._socket)
        raise AttributeError
        
    def _stopserver(self):
        self._socket.send(b"_stopserver")
