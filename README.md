# Introduction

This is repository for computer network programming excercises.

<b>professor</b>: Yusung Kim<br>
<b>covered class</b>: Introduction to Computer Network 

<br>

# Assignment1
<b>File Copy Program</b> <br>
1. goal : Copy files with different names

2. Development environments <br>
	 1) version of OS : Ubuntu 16.04.4 LTS<br>
	 2) programming language: C

3. How to test 
	 1) make the executable( gcc -o ass1 ass1.c )
	 2) run it ( ./ass1 ) <br>
	 3) write two input strings; one for the existing file name and the other for the new copy version file name.
	 4) you can also check log files ( log.txt )
<br>

# Assignment2
<b>Concurrent File Copies</b> <br>
1. goal 
	 1) Copy multiple files confurrently
	 2) Be able to receive new copy requests while copying files

2. Development environments <br>
	 1) version of OS : Ubuntu 16.04.4 LTS<br>
	 2) programming language: C

3. How to test 
	 1) make the executable( gcc -o ass2 ass2.c -pthread)
	 2) run it ( ./ass2 ) <br>
	 3) write two input strings; one for the existing file name and the other for the new file name to be copied
	 4) you can also check log files ( log.txt )



<br>

# Assignment3
<b> My Own Web Server </b>
1. goal : Develop a sipmle web server using socket programming

2. Development environments <br>
	 1) version of OS : Ubuntu 16.04.4 LTS<br>
	 2) programming language: Python
	 3) compilers/interpreter version: python 3.5.2

3. How to test 
	 1) run wev server program ( python3 webserver.py ) <br>
	 -> the web server program runs with the port number of 10080, and waits to receive HTTP requests from web browsers that run on another end system. 
	 2) write a URL in the browser address bar; ( http://server_IP:10080 )
	 3) you should login first. ( any ID & password are possible. )
	 4) without the login process, you cannot access any URL directly.
	 5) when accessing "cookie.html", you can check how many seconds left before the cookie expires

<br>

# Assignment4
<b> Pipelined Reliable Data Transfer over UDP </b>
1. goal 
 	 1) Develop a pipelined reliable data transfer protocol using UDP socket programming
	 2) Generate packet losses at a receiver program

2. Development environments <br>
	 1) version of OS : Ubuntu 16.04.4 LTS<br>
	 2) programming language: Python
	 3) compilers/interpreter version: python 3.5.2

3. How to test 
	 1) run sender program and receiver program <br>
	 sender: python3 sender.py receiver_IP_address timeout window_size <br>
	 receiver: python3 receiver.py <br>
	 *when starting a receiver, it askes you "packet loss prabability" 
	 2) enter a file name to send at the sender program <br>
	 *concurrent file transfer is possible. you cna send new file while processing existing file transfer
	 3) you can check sending log and receiving log (with packet drops) 
	 4) you can also check the throughput (goodput) in the log file after the file transfer is finished.
	 
	 
	 
