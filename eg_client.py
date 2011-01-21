import zerorpc

rpcclient = zerorpc.Client("ipc://zerorpc.ipc")

print(rpcclient.product(5, 7))
print(rpcclient.addtogether(12, 15))

rpcclient._stopserver()
