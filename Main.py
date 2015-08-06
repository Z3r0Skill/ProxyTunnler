from Proxy import ProxyWorker
import socket
import sys
from Logger import LoggerClass
from Plugins import Functions
from Debugger import Debugger
import argparse

DATASIZE = 8192

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Proxy Tunnler")
    parser.add_argument('-i', '--ip', default='', action='store', dest="ip", help="IP to listen")
    parser.add_argument('-p', '--port', type=int, action='store', dest="port", default=8080, help="Port for listening")
    parser.add_argument('-sslstrip', '--sslstrip', type=bool, action='store', dest='sslstrip', default=False, help="Activate sslstrip")
    parser.add_argument('-d', '-debug', type=bool, action='store', dest="debug", default=False, help="Activate debug information")


    args = parser.parse_args()

    print("Welcome to the ProxyTunnler")
    ip = args.ip
    port = args.port
    debug = args.debug
    plugins = args.sslstrip

    if not ip:
        print("Listening to: localhost" + ":" + str(port))
    else:
        print("Listening to: " + str(ip) + ":" + str(port))


    address = (ip,port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind(address)
    except socket.error as msg:
        print(msg)
        sys.exit()

    s.listen(5)
    print("Server is listening")
    threads = []

    #queue = Queue(maxsize=0)
    

    logFile = open("LogfileProxy.txt", "w")
    log = LoggerClass(logFile)

    errorLogFile = open("ErrorLog.txt", "w")
    errorlog = LoggerClass(errorLogFile)

    debugger = Debugger(debug, log, errorlog)

    #s.settimeout(10)
    functions = Functions(debugger)

    while True:
        try:
            conn, addr = s.accept()
            t = ProxyWorker(conn, port, debugger, functions, plugins)
            t.start()
            threads.append(t)
        except socket.error as msg:
            print(msg)
            continue
        except KeyboardInterrupt:
            print("\nShutting down proxy")
            break

    print("Wating for thread to complete")
    [t.join() for t in threads]
    print("Threads closed!")
    s.close()
    logFile.close()
    errorLogFile.close()
    print("Terminated successfully")