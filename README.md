# ProxyTunnler

This tool is only for educational purpose. I am not responsible for damages 
that may arise if the program is used for not educational purposes.

###########################################################
Usage: python Main.py -i [IP] -p [PORT] -ssltrip [SSLSTRIP] -d [DEBUG]

-h Help
-i - Optional --> Default = localhost
-p - Optional --> Default = 8080
-sslstrip - Optional --> Default=False
-d - Optional --> Default = False (0)


-i [IP]
###########################################################
The ip the proxy is listening. By default it is 'localhost'


-p [PORT]
###########################################################
The port which the proxy is listening. By default it is 
'8080'

-sslstrip [SSLSTRIP]
###########################################################
Activate sslstrip

-d [DEBUG]
###########################################################
For printing debug messages. By default it is "False"



The logging happens at the moment in the "LogfileProxy.txt". It logs every
request and response.

Issues:

HSTS support isn't included yet. So "noname" webbrowser would be fine for 
testing purpose.
