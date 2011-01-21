import zerorpc

rpcserver = zerorpc.Server("ipc://zerorpc.ipc")

@rpcserver.expose
def addtogether(a, b):
    return a + b
    
@rpcserver.expose_as("product")
def multiplytogether(a, b):
    return a * b
    
rpcserver.run()
