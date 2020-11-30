import selectors
import socket
import threading

HOST = '0.0.0.0'  # Symbolic name meaning all available interfaces
PORT = 50007  # Arbitrary non-privileged port

commando = "dir"
sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('Conectado por ', addr)
    conn.send(commando.encode('utf-8'))
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    if data:
        print('Recebendo: ', str(data))
        # conn.send(data)  # Hope it won't block
    else:
        sel.unregister(conn)
        conn.close()

def listenCommand():
    while True:
        global commando;

        commando = input("Digite a qualquer momento o novo comando:\n")
        print('Novo comando é: ',commando)

def ServerJobs():
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

lc = threading.Thread(target=listenCommand)
sj = threading.Thread(target=ServerJobs)

lc.start()
sj.start()