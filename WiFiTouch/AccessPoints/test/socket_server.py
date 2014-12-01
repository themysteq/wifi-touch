__author__ = 'bopablog'

import socket

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
print host
port = 8728                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port
s.listen(5)                 # Now wait for client connection.
while True:
   print "Serwer start"
   c, addr = s.accept()     # Establish connection with client.
   print 'Got connection from', addr
   c.send('Conected')
   c.close()                # Close the connection