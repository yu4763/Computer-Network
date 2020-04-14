from socket import *
import threading
import pickle
import random
import time

serverPort = 10080
packetreceiver = []

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


class packetReceiver:

    def __init__(self, file_num, serverSocket):
        self.expected = 0
        self.file_num = file_num
        self.file_name = None
        self.file = None
        self.logfile = None
        self.serverSocket = serverSocket
        self.packets = []
        self.start_time = None
        self.clientAddress = None
        self.last = -1

    def get_filenum(self):
        return self.file_num

    def storeData (self, packet, clientAddress):

        try:
            seq, data = packet.get_data()
            serverSocket = self.serverSocket

            if seq==0:

                self.start_time = time.time()
                self.file_name = data
                self.clientAddress = clientAddress
                self.file = open(self.file_name, "wb")
                self.last = packet.get_last()
                log_file_name = self.file_name + "__receiving__log.txt"
                self.logfile = open(log_file_name, "w")

                timestamp = format(time.time() - self.start_time, '.3f')
                self.logfile.write(timestamp + " pkt: " + str(seq)+ " | received\n")

                packet = Packet(seq, "ACK", self.file_num)
                serverSocket.sendto(pickle.dumps(packet), self.clientAddress)
                self.expected = self.expected + 1

                timestamp = format(time.time() - self.start_time, '.3f')
                self.logfile.write(timestamp + " ACK: " + str(seq)+ " | sent\n")


            else :

                timestamp = format(time.time() - self.start_time, '.3f')
                self.logfile.write(timestamp + " pkt: " + str(seq)+ " | received\n")

                random_number = random.random()
                if random_number < float(packet_loss) :
                    self.logfile.write(timestamp + " pkt: " + str(seq)+ " | dropped\n")


                elif seq == self.expected :

                    self.file.write(data)
                    self.expected = self.expected + 1

                    if len(self.packets) > 0 :
                        self.arrangeData()
                        packet = Packet(self.expected-1, "ACK", self.file_num)
                        serverSocket.sendto(pickle.dumps(packet), self.clientAddress)
                        timestamp = format(time.time() - self.start_time, '.3f')
                        self.logfile.write(timestamp + " ACK: " + str(self.expected-1)+ " | sent\n")

                    else :
                        packet = Packet(seq, "ACK", self.file_num)
                        serverSocket.sendto(pickle.dumps(packet), self.clientAddress)
                        timestamp = format(time.time() - self.start_time, '.3f')
                        self.logfile.write(timestamp + " ACK: " + str(seq)+ " | sent\n")


                else:

                    self.packets.append(packet)
                    packet = Packet(self.expected-1, "ACK", self.file_num)
                    serverSocket.sendto(pickle.dumps(packet), self.clientAddress)
                    timestamp = format(time.time() - self.start_time, '.3f')
                    self.logfile.write(timestamp + " ACK: " + str(self.expected-1)+ " | sent\n")


            if self.last == self.expected - 1 :

                end_time = time.time()
                self.logfile.write("\nFile transfer is finished.\n")

                throughput = format( self.expected /(end_time - self.start_time), '.2f')
                self.logfile.write("Throughput: " + throughput + "pkts / sec" )
                self.logfile.close()
                self.file.close()
                
        except:
            pass



    def arrangeData(self):

        while True :

            found = 0
            n = len(self.packets)

            if n == 0:
                break

            for i in range(n):

                seq, data = self.packets[i].get_data()
                if seq == self.expected :
                    self.file.write(data)
                    self.expected = self.expected + 1
                    del self.packets[i]
                    found = 1
                    break

            if found == 0:
                break



if __name__ == "__main__":

    packet_loss = input("packet loss probability: ")

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))

    buf = serverSocket.getsockopt(SOL_SOCKET, SO_RCVBUF)
    print("socket recv buffer size: " + str(buf))

    if buf < 10000000:
        serverSocket.setsockopt(SOL_SOCKET, SO_RCVBUF, 10000000)
        buf = serverSocket.getsockopt(SOL_SOCKET, SO_RCVBUF)
        print("socket recv buffer size updated: "+ str(buf))

    packets = []

    print("receiver program starts...")

    while True:


        pkt, clientAddress = serverSocket.recvfrom(2048)
        packet = pickle.loads(pkt)
        seq, file_name = packet.get_data()
        file_num = packet.get_filenum()

        if seq == 0:
            lock.acquire()
            receiver = packetReceiver(file_num, serverSocket)
            packetreceiver.append(receiver)
            lock.release()

        n = len(packetreceiver)
        for i in range(n):
            if packetreceiver[i].get_filenum() == file_num :
                packetreceiver[i].storeData(packet, clientAddress)
                break
