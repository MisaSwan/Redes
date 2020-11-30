import selectors
import socket

HOST = '0.0.0.0' # Symbolic name meaning all available interfaces
PORT = 50007 # Arbitrary non-privileged port

commando = "dir"
sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('Connected by', addr)
    conn.send(commando.encode('utf-8'))
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    if data:
        print('Receiving: ', str(data.decode('cp1252')))
        #conn.send(data)  # Hope it won't block
    else:
        sel.unregister(conn)
        conn.close()


sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
