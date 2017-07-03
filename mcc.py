#! /usr/bin/env python3
#
# multicast chat
#
# usage:
#   mcc [-bs4] myname
#     -4 use IPv4 (default: IPv6)
#     mode: default receiver mode
#           -s sender mode
#           -b bot mode

import pickle
import struct
import socket
import sys
import subprocess
import random
import unicodedata

MYPORT = 8123
MYGROUP_4 = '225.0.0.250'
MYGROUP_6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
MYTTL = 1

def main():
    ipv4 = False
    bot = False
    issender = False
    myname = ''

    while len(sys.argv) > 1:
        if sys.argv[1].startswith('-'):
            if sys.argv[1] == '-b':
                bot = True
            elif sys.argv[1] == '-s':
                issender = True
            elif sys.argv[1] == '-4':
                ipv4 = True
            else:
                break
        else:
            myname = sys.argv[1]
        del sys.argv[1]

    if len(myname) == 0:
        usage()
        return

    sprint('My name is ' + myname)

    if ipv4:
        group = MYGROUP_4
    else:
        group = MYGROUP_6

    if issender:
        sender(myname, group, bot)
    else:
        receiver(myname, group, bot, ipv4)

def usage():
    sprint('usage: mcc [-4] [-s] [-b] myname')

def sprint(s):
    # https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
    s1 = "".join(ch for ch in s if unicodedata.category(ch)[0] != 'C')
    print(s1)

def sender(myname, group, bot):
    addrinfo = socket.getaddrinfo(group, None)[0]
    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
#    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ttl_bin = struct.pack('@i', MYTTL)
    if addrinfo[0] == socket.AF_INET: # IPv4
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
    else:
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)

    # send join message
    if not bot:
        s.sendto(pickle.dumps(['J', myname.encode('utf-8')]), (addrinfo[4][0], MYPORT))

    while True:
        try:
            b0 = input('>>> ')
            s.sendto(pickle.dumps(['S', myname.encode('utf-8'), b0.encode('utf-8')]), (addrinfo[4][0], MYPORT))
        except EOFError as eof:
            if not bot:
                # send leave message and quit
                s.sendto(pickle.dumps(['L', myname.encode('utf-8')]), (addrinfo[4][0], MYPORT))
                print('bye')
            return

def receiver(myname, group, bot, ipv4):
    addrinfo = socket.getaddrinfo(group, None)[0]
    s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # works on macOS. how about Linux?
    s.bind(('', MYPORT))
    group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
    if addrinfo[0] == socket.AF_INET:
        # IPv4
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    else:
        mreq = group_bin + struct.pack('@I', 0)
        s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

    while True:
        (data, sender) = s.recvfrom(1500)
        buffer = pickle.loads(data)
        yourname = buffer[1].decode('utf-8')

        if bot and (yourname == myname):
            continue

        if buffer[0] == 'J':
            if bot:
                msg = yourname + '君、こんにちは'
            else:
                sprint('(' + sender[0] + ') ' + yourname + ' joins')
        elif buffer[0] == 'L':
            if bot:
                msg = buffer[1].decode('utf-8') + '君、さようなら。また会う日まで'
            else:
                sprint('(' + sender[0] + ') ' + yourname + ' leaves')
        elif buffer[0] == 'S':
            if bot:
                msg = fortune(yourname, buffer[2].decode('utf-8'))
            else:
                sprint('(' + sender[0] + ') ' + yourname + ' says ' + buffer[2].decode('utf-8'))

        if bot and (len(msg) > 0):
            sprint(msg)
            if ipv4:
                cmd = [sys.argv[0], "-s", "-b", "-4", myname]
            else:
                cmd = [sys.argv[0], "-s", "-b", myname]
            sp = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
            (stdout_data, stderr_data) = sp.communicate(input=msg.encode('utf-8'))
#            sprint(str(sender[0]) + ' ' + str(pickle.loads(data)))

def fortune(yourname, message):
    keyword = '数学'
    oracle = ['難しい', '楽しい', '苦しい', '美しい']
    n = len(oracle) - 1

    if message.find(keyword) >= 0:
        r = random.randint(0, n)
        f = yourname + '君、' + keyword + 'は' + oracle[r] + 'ね'
#        sprint(r, n, f)
    else:
        f = ''
    return f

if __name__ == '__main__':
    main()
