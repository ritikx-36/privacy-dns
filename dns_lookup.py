# it coverts domain to ip and stores the ip

import socket #used to communicate over networks

domain = input("Enter domain: ")

try:
    ip = socket.gethostbyname(domain) 
    print("Domain:", domain)
    print("IP:", ip)

except socket.gaierror:
    print("Could not resolve domain")    


