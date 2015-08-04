from Proxy import ProxyWorker
import socket
import sys
from Logger import LoggerClass
from Plugins import Functions
from Debugger import Debugger
import argparse

DATASIZE = 4096

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Proxy Tunnler")
    parser.add_argument('-i', '--ip', default='', action='store', dest="ip", help="IP to listen")
    parser.add_argument('-p', '--port', type=int, action='store', dest="port", default=8080, help="Port for listening")
    parser.add_argument('-d', '--debug', action='store', dest="debug", default=0, type=int, help='Activate debug messages (0/1)')

    #TO-DO PARSER FOR PLUGIN FEATURES!

    args = parser.parse_args()

    ''' Plugin option activation. [SSLStrip, ChangetoHttp , NoCookies , Redirect] '''
    plugins = [True, False, False, False]

    print("Welcome to the ProxyTunnler")
    print("Options set: " + str(plugins))
    ip = args.ip
    port = args.port
    debug = args.debug

    if not ip:
        print("Listening to: localhost" + ":" + str(port))
    else:
        print("Listening to: " + str(ip) + ":" + str(port))


    address = (ip,port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind(address)
    except socket.error as msg:
        print msg
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
            print msg
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