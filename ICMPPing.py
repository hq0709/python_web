#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import select
import socket
import struct
import time
from socket import *

ICMP_ECHO_REQUEST = 8  # ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0  # ICMP type code for echo reply messages
ID = 0  # ID of icmp_header
SEQUENCE = 0  # sequence of ping_request_msg


def checksum(str):
    csum = 0
    countTo = (len(str) / 2) * 2
    count = 0
    while count < countTo:
        thisVal = str[count + 1] * 256 + str[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
    if countTo < len(str):
        csum = csum + str[len(str) - 1].decode()
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(icmpSocket, destinationAddress, ID, timeout):
    # 1. Wait for the socket to receive a reply
    # while True:
    timeBeginReceive = time.time()
    whatReady = select.select([icmpSocket], [], [], timeout)
    timeInRecev = time.time() - timeBeginReceive
    if not whatReady[0]:
        print("none")
        return -1
    timeReceived = time.time()
    # 2. Once received, record time of receipt, otherwise, handle a timeout
    recPacket, addr = icmpSocket.recvfrom(1024)
    # 3. Compare the time of receipt to time of sending, producing the total network delay
    byte_in_double = struct.calcsize("!d")
    timeSent = struct.unpack("!d", recPacket[28: 28 + byte_in_double])[0]
    totalDelay = timeReceived - timeSent
    # 4. Unpack the packet header for useful information, including the ID
    rec_header = recPacket[20:28]
    replyType, replyCode, replyCkecksum, replyId, replySequence = struct.unpack('!bbHHh', rec_header)
    # 5. Check that the ID matches between the request and reply
    if ID == replyId and replyType == ICMP_ECHO_REPLY:
        # 6. Return total network delay
        return totalDelay
    if timeInRecev > timeout:
        print('overtime')
        return -1


def sendOnePing(icmpSocket, destinationAddress, ID):
    icmp_checksum = 0
    # 1. Build ICMP header
    icmp_header = struct.pack('!bbHHh', ICMP_ECHO_REQUEST, 0, icmp_checksum, ID, SEQUENCE)
    time_send = struct.pack('!d', time.time())
    # 2. Checksum ICMP packet using given function
    icmp_checksum = checksum(icmp_header + time_send)
    # icmp_checksum = checksumByTeacher(icmp_header + time_send)
    # 3. Insert checksum into packet
    icmp_header = struct.pack('!bbHHh', ICMP_ECHO_REQUEST, 0, icmp_checksum, ID, SEQUENCE)
    # 4. Send packet using socket
    icmp_packet = icmp_header + time_send
    icmpSocket.sendto(icmp_packet, (destinationAddress, 80))
    #  5. Record time of sending


def doOnePing(destinationAddress, timeout):
    # 1. Create ICMP socket
    icmpName = socket.getprotobyname('icmp')
    icmp_Socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmpName)
    # 2. Call sendOnePing function
    sendOnePing(icmp_Socket, destinationAddress, ID)
    # 3. Call receiveOnePing function
    totalDelay = receiveOnePing(icmp_Socket, destinationAddress, ID, timeout)
    # 4. Close ICMP socket
    icmp_Socket.close()
    # 5. Return total network delay
    return totalDelay


def ping(host, timeout=1):
    send = 0
    lost = 0
    receive = 0
    maxTime = 0
    minTime = 1000
    sumTime = 0
    # 1. Look up hostname, resolving it to an IP address
    desIp = socket.gethostbyname(host)
    global ID
    ID = os.getpid()
    for i in range(0, 4):
        global SEQUENCE
        SEQUENCE = i
        # 2. Call doOnePing function, approximately every second
        delay = doOnePing(desIp, timeout) * 1000
        send += 1
        if delay > 0:
            receive += 1
            if maxTime < delay:
                maxTime = delay
            if minTime > delay:
                minTime = delay
            sumTime += delay
            # 3. Print out the returned delay
            print("Receive from: " + str(desIp) + ", delay = " + str(int(delay)) + "ms")
        else:
            lost += 1
            print("Fail to connect.")
        time.sleep(1)
    # 4. Continue this process until stopped
    avgTime = sumTime / receive
    recvRate = receive / send * 100.0
    print("\nSend: " + str(send) + ", success: " + str(receive) + ", lost: " + str(lost) +
          ", rate of success: " + str(recvRate) + "%.")
    print(
        "MaxTime = " + str(int(maxTime)) + "ms, MinTime = " + str(int(minTime)) + "ms, AvgTime = " + str(int(avgTime)))


ping("baidu.com")