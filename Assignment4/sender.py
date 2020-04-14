from socket import *
import threading
import os
import pickle
import time
import sys


serverPort = 10080

serverIP = sys.argv[1]
time_out = sys.argv[2]
window = sys.argv[3]
timeout = float(time_out)
window_size = int(window)

buf = 1208;
file_num = 0
packetsender = []
lock = threading.Lock()

class Packet:

    def __init__(self, seq, data, file_num):
        self.__seq = seq
        self.__last = -1
        self.__data = data
        self.__received = 0
        self.__start_time = -1
        self.__file_num = file_num

    def set_start_time(self, start_time):
        self.__start_time = start_time

    def get_start_time(self):
        return self.__start_time

    def set_received(self):
        self.__received = 1

    def get_received(self):
        return self.__received

    def set_last(self, index):
        self.__last = index

    def get_last(self):
        return self.__last

    def get_filenum(self):
        return self.__file_num

    def get_data(self):
        return self.__seq, self.__data


class packetSender:

    def __init__(self, file_name, file, file_num, clientSocket):
        self.file_name = file_name
        self.file = file
        self.file_num = file_num
        self.clientSocket = clientSocket
        self.seq = 0
        self.send = 0
        self.received = 0
        self.duplicated = 0
        self.packets = []
        self.logfile = None
        self.start_time = None

    def makePacket(self):

        file = self.file

        self.seq = 0
        self.packets = []
        packet = Packet(self.seq, self.file_name, self.file_num)
        self.packets.append(packet)
        self.seq = self.seq+1

        while True:

            data = file.read(buf)
            if data:
                packet = Packet(self.seq, data, file_num)
                self.packets.append(packet)
                self.seq = self.seq+1

            else:
                break

        self.packets[0].set_last(self.seq-1)

        file.close()


    def startTimer(self, i, timer_start):

        try:

            if self.packets[i].get_received() == 0:
                timestamp = format(time.time() - self.start_time, '.3f')
                self.logfile.write(timestamp + " pkt: " + str(i)+ " | timeout since " + timer_start + "\n")

                self.clientSocket.sendto(pickle.dumps(self.packets[i]), (serverIP, serverPort))
                self.packets[i].set_start_time(time.time())
                self.logfile.write(timestamp + " pkt: " + str(i)+ " | retransmitted\n")

                timer = threading.Timer(timeout, self.startTimer, (i, timestamp)).start()

            else:
                timeout_value = timeout - (time.time()-self.packets[self.received].get_start_time())
                timestamp = format(self.packets[self.received].get_start_time() - self.start_time, '.3f')
                timer = threading.Timer(timeout_value, self.startTimer, (self.received, timestamp)).start()

        except:
            pass



    def sendPacket(self):

        clientSocket = self.clientSocket
        tt = clientSocket.getsockopt(SOL_SOCKET, SO_RCVBUF)

        if tt < 10000000:
            clientSocket.setsockopt(SOL_SOCKET, SO_RCVBUF, 10000000)


        log_file_name = self.file_name + "_sending_log.txt"
        self.logfile = open(log_file_name, "w")


        self.makePacket()


        self.start_time = time.time()
        start_time = self.start_time


        for i in range (window_size) :

            if self.send >= self.seq:
                break;


            clientSocket.sendto(pickle.dumps(self.packets[self.send]), (serverIP, serverPort))
            self.packets[self.send].set_start_time(time.time())

            self.send = self.send+1
            timestamp = format(time.time() - start_time, '.3f')
            self.logfile.write(timestamp + " pkt: " + str(self.send-1)+ " | sent\n")

            if self.send-1 == 0:
                timer = threading.Timer(timeout, self.startTimer, (0 , timestamp)).start()


    def slideWindow(self, packet) :

        seq_received, ack = packet.get_data()

        timestamp = format(time.time() - self.start_time, '.3f')
        self.logfile.write(timestamp + " ACK: " + str(seq_received)+ " | received\n")

        if seq_received >= self.received:
            for i in range (self.received, seq_received+1) :
                self.packets[i].set_received()

                if self.send < self.seq:
                    clientSocket.sendto(pickle.dumps(self.packets[self.send]), (serverIP, serverPort))
                    self.packets[self.send].set_start_time(time.time())

                    self.send = self.send+1
                    timestamp = format(time.time() - self.start_time, '.3f')
                    self.logfile.write(timestamp + " pkt: " + str(self.send-1)+ " | sent\n")

            self.received = seq_received+1
            self.duplicated = 0

        else:
            self.duplicated = self.duplicated+1
            if self.duplicated >= 3:
                clientSocket.sendto(pickle.dumps(self.packets[seq_received+1]), (serverIP, serverPort))
                self.packets[seq_received+1].set_start_time(time.time())

                timestamp = format(time.time() - self.start_time, '.3f')
                self.logfile.write(timestamp + " ACK: " + str(seq_received)+ " | 3 duplicated ACKs\n")
                self.logfile.write(timestamp + " pkt: " + str(seq_received+1)+ " | sent\n")


        if self.received >= self.seq :
            end_time = time.time()
            self.logfile.write("\nFile transfer is finished.\n")

            throughput = format( self.seq /(end_time - self.start_time), '.2f')
            self.logfile.write("Throughput: " + throughput + "pkts / sec" )
            self.logfile.close()


def receiveACK(clientSocket):


    while True:
        try:

            pkt, serverAddress = clientSocket.recvfrom(2048)
            packet = pickle.loads(pkt)
            filenum = packet.get_filenum()

            packetsender[filenum].slideWindow(packet)

        except:
            pass





if __name__ == "__main__":

    print("Receiver IP address: " + serverIP)
    print("window size: " + window)
    print("timeout (sec): " + time_out)

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    clientSocket.bind(('', 0))

    thread = threading.Thread(target=receiveACK, args = (clientSocket, )).start()

    while True:

        file_name = input("file_name: ")

        try :
            file = open(file_name, "rb")

        except FileNotFoundError:
            print("File doesn't exist")
            continue


        sender = packetSender(file_name, file, file_num, clientSocket)
        sender.sendPacket()

        packetsender.append(sender)
        file_num = file_num+1
