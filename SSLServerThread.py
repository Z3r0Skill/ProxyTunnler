from threading import Thread
import socket
import errno

DATASIZE = 4096

class ProxyWorkerServerSSL(Thread):
    def __init__(self, server_sock, client_sock, debugger):
        Thread.__init__(self)
        self._server_sock = server_sock
        self._client_sock = client_sock
        self._debugger = debugger


    def run(self):

        rep = ""
        while True:
            response = self._server_sock.recv(DATASIZE)

            if not response or response == "stop":
                break;

            rep += response

            try:
                self._client_sock.sendall(bytes(response))
            except socket.error, e:
                if e.errno == errno.EPIPE:
                    self._debugger.printMessage("[-] Broken pipe - Error Server -> Client - 'tls/ssl thread'", "error")
                    break

        self._debugger.printMessage("[+] +++++ DEBUG END SSL THREAD +++++", "info")
        self._debugger.log(rep)
        return
