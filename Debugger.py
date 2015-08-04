

class Debugger:
    def __init__(self, active, logfile, errorlogfile):
        self._active = active
        self._logfile = logfile
        self._errorlogfile = errorlogfile


    def printMessage(self, msg, type):

        if type == "error":
            print('\033[1;31;m %s \033[0;m' % msg)

        elif type == "info" and self._active:
            print('\033[0;34;m %s \033[0;m' % msg)

        elif type == "warning" and self._active:
            print('\033[0;33;m %s \033[0;m' % msg)

        elif type =="important" and self_active:
            print('\033[0;33;m %s \033[0;m' % msg)

        elif type==None:
            print msg


    def log(self, msg):
        self._logfile.log(msg)

    def errorlog(self, msg):
        self._errorlogfile.log(msg)