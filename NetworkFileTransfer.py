#!/usr/bin/env python
import socket, os, threading
import netifaces as ni

def Main():
    host_server = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
    host_client = ""
    port = 5000
    ue = "[-] Unknown error"
    se = "[-] Server is not running"
    try:
        opt = raw_input("Do you want to (S)end or (R)ecive file? -> ")
    except:
        print ue
    if opt in ("S", "s"):
        try:
            s = server(host_server, port)
            s.main()
        except:
            print ue
    elif opt in ("R", "r"):
        try:
            host_client = raw_input("Server IP (e.g. 0.0.0.0) -> ")
            c = client(host_client, port)
            c.main()
        except:
            print se

class client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
    def main(self):
        s = socket.socket()
        s.connect((self.host, self.port))
        print "----------------------------------------------------\n" + s.recv(1024) +" | '!/q' for quit" 
        while True:
            print "----------------------------------------------------"
            filename = raw_input("File name? -> ")
            if filename == "!/q":
                break
            packet_counter = 1
            s.send(filename)
            data = s.recv(1024)
            if data[:1] == '1':
                filesize = long(data[1:])
                print "[+] File exists | " + str(filesize) + "Bytes | Downloading"
                s.send("1")
                f = open("downloaded_" + filename, "wb")
                data = s.recv(1024)
                t_recv = len(data)
                f.write(data)
                while t_recv < filesize:
                    data = s.recv(1024)
                    t_recv += len(data)
                    f.write(data)
                    packet_counter += 1
                print "[+] Download complete | {} packets received".format(packet_counter)
                f.close()
            elif data[:1] == '0':
                print "[-]File does not exist!"
        s.close()

class server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def retr(self, name, soc):
        soc.send(" | ".join(os.listdir(".")))
        try:
            while True:
                filename = soc.recv(1024)
                if os.path.isfile(filename):
                    soc.send("1" + str(os.path.getsize(filename)))
                    user_response = soc.recv(1024)
                    if user_response == "1":
                        with open(filename, 'rb') as f:
                            bytes_to_send = f.read(1024)
                            soc.send(bytes_to_send)
                            while bytes_to_send != "":
                                bytes_to_send = f.read(1024)
                                soc.send(bytes_to_send)
                        print "[+] File {} sent".format(filename)
                else:
                    soc.send("0")
        except:
            print "[-] Connection lost"
        soc.close()

    def main(self):
        s = socket.socket()
        s.bind((self.host,self.port))
        s.listen(5)
        print "Server Started! | IP: {}\n--------------------------------------------------------".format(self.host)
        while True:
            c, addr = s.accept()
            print "[+] Client connedted ip: <" + str(addr) + ">"
            t = threading.Thread(target=self.retr, args=("retrThread", c))
            t.start()
        s.close()

if __name__ == '__main__':
    Main()
