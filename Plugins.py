import sys
import re


class Functions:
    def __init__(self, debugger):
        self._debugger = debugger
        self.listOfChangesToHttp = []

    def HeaderChanger(self, header):
        pass

    def getHostname(self, header):
        if "CONNECT" in header:
            start = header.index("CONNECT ") + len("CONNECT ")
            end = header.index(" ", start)

            hostPort = header[start:end]
            hostname = hostPort.split(":")

            return hostname[0]

        start = header.index("Host: ") + len("Host: ")
        end = header.index("\r\n", start)
        hostPort = header[start:end]
        hostname = hostPort.split(":")

        return hostname[0]

    def changeAbsoluteToRelativeHostname(self, header):
        hostname = self.getHostname(header)

        fulldomain = "http://" + str(hostname)

        self._debugger.printMessage("[+] DEBUG " + str(fulldomain), "info")

        request = header.replace(fulldomain, "")

        return request

    def changeHTTP11to10(self, header):
        if "HTTP/1.1" in header:
            header = header.replace("HTTP/1.1", "HTTP/1.0")

        return header

    def changeEncoding(self, header):

        if "Accept-Encoding:" in header:
            start = header.index("Accept-Encoding: ") + len("Accept-Encoding: ")
            end = header.index("\r\n", start)

            encoding = header[start:end]
            header = header.replace(encoding, "")

        return header

    def changeConnectionType(self, header):
        if "Connection: keep-alive" in header:
            header = header.replace("Connection: keep-alive", "Connection: close")

        return header

    def changeResponseLinks(self, response):

        l = []
        response = self.changeFavIcon(response)

        '''Im header auf Location: https:// kontrollieren'''
        if "Location: https://" in response:
            response = response.replace("Location: https://", "Location: http://")
            start = response.index("Location: http://") + len("Location: ")
            end = response.index("\r\n", start)
            self.listOfChangesToHttp.append(response[start:end]) #adding changed link to list

        '''Im body auf <a href="https:// kontrollieren'''
        if '<a href="https://' in response:
            #Find all https:// links
            l = re.findall(r'https://[^\s<>"]+|www\.[^\s<>"]+', str(response))
            x = 0
            #replace links with http://
            for item in l:
                l[x] = item.replace("https://", "http://")
                if not item[len(item) - 1]  == "/":
                    l[x] += "/"

                #if not in list yet, safe it now to list
                if not any(l[x] in s for s in self.listOfChangesToHttp):
                    self._debugger.printMessage(str(l[x]) + " added to list", "debug")
                    self.listOfChangesToHttp.append(l[x])

                x += 1

            response = response.replace('<a href="https://', '<a href="http://')


        if not l == []:
            self._debugger.printMessage(l, "warning")


        return response


    def checkLinks(self, request):
        '''Check the GET request, when link is in the list, change it back to https'''
        getpost = ""
        request = self.changeFavIcon(request)

        if "GET " in self.getFirstLine(request):
            getpost = "GET "
        elif "POST " in request:
            getpost = "POST "
        else:
            return request


        #self._debugger.printMessage(str(getpost) + "FOUND", "warning")
        start = request.index(getpost) + len(getpost)
        end = request.index(" ", start)
        url = request[start:end]
        self._debugger.printMessage("OLD URL " + str(url), "warning")

        if any(url in s for s in self.listOfChangesToHttp):
            newurl = url.replace("http://", "https://")

            request = request.replace(url, newurl)
            self._debugger.printMessage("NEW URL " + str(newurl), "warning")

        return request


    def sslBuilder(self, request):
        '''Make a GET request to a CONNECT (SSL) request'''
        pass

    def noCookies(self, response):
        if "Set-Cookie:" in response:
            print("##### Deleting Set-Cookie #####")
            start = response.index("Set-Cookie: ")
            end = response.index("\r\n", start) + len("\r\n")
            cookie = response[start:end]
            response = response.replace(cookie, "")

        return response

    def getHeader(self, response):
        end = response.index("\r\n\r\n") + len("\r\n\r\n")
        header = response[0:end]

        return header

    def redirect(self, response):
        resp = response
        file = open("refresh.txt", "r")
        resp = file.read() + "\r\n\r\n"

        return resp

    def seperateHeaderBody(self, request):
        head = request.index("\r\n\r\n") + len("\r\n\r\n")
        b = request.index(head, "\r\n\r\n")
        header = request[0:head]
        body = request[head, b]

        req = [header, body]

        return req


    def getFirstLine(self, header):
        end = header.index("\r\n")
        first = header[:end]

        self._debugger.printMessage("GetFirstLine " + str(first), "warning")

        return first


    def changeFavIcon(self, request):
        if "Location: " in request:
            start = request.index("Location: ") + len("Location: ")
            end = request.index("\r\n")
            url = request[start:end]

            if "favicon.ico" in url:
                print("Fav Icon Found!")
                print("Changed: " + str(url) + " to ")
                newurl = "http://dchoa.org/images/icons/Lock.ico"
                print(str(newurl))
                request.replace(url, newurl)



        if "GET " in request[:4]:
            firstline = self.getFirstLine(request)
            if "favicon.ico" in firstline:
                start = firstline.index("GET ") + len("GET ")
                end = firstline.index(" ", start)
                url = firstline[start:end]
                print("Changed: " + str(url) + " to ")
                newurl = "http://dchoa.org/images/icons/Lock.ico"
                print(str(newurl))
                request.replace(url, newurl)


        return request