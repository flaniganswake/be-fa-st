#!/usr/bin/env python3
#
# BFS directory walk of server
# best 100 subdirs: 0m48.116s
# without stdout: 0m13.373s
# flaniganswake@protonmail.com
#

import os
import socket
import sys

def send_response(sock, m):
    ''' send response to client '''
    try:
        m = str.encode(m)
        sock.sendall(m)
    except Exception as e:
        print(f"send exception: {e}")
        raise


def extract_requests(arr, begin, end, f):
    ''' extract requests from lines '''
    # DIRLIST dir_00/ dir_01/\r\n
    results = []
    for elem in arr:
        # handle line fragments
        if not elem.startswith(begin) and f:
            elem = f+elem
            f = ""
        elif not elem.endswith(end):
            f = elem
            continue
        results.append(elem.replace(begin, ""))
    return results, f


def extract_lines(d):
    ''' extract lines from recv data '''
    results, begin = [], 0
    while begin < len(d):
        end = d.find("\n", begin)
        if end == -1:
            # line fragment in data
            results.append(d[begin:])
            break
        results.append(d[begin:end+1])
        begin = end+1
    return results


def recv_all(sock, buffer_size):
    ''' call recv until complete '''
    result = ""
    buf = sock.recv(buffer_size).decode()
    while buf:
        result += buf
        if len(buf) < buffer_size:
            break
        buf = sock.recv(buffer_size).decode()
    return result


def process_recv(sock, f):
    ''' process recv data '''
    data = recv_all(sock, BUFFER_SIZE)
    if data:
        lines = extract_lines(data)
        return extract_requests(lines, "DIRLIST", "\n", f)


if __name__ == "__main__":

    if len(sys.argv) == 1:
        DIRS = 100
    elif len(sys.argv) == 2:
        DIRS = int(sys.argv[1])
    else:
        print("format: server.py <number of subdirs>")
        sys.exit()
    print(f"PID: {os.getpid()}")

    FILES, MAX_DEPTH = 3, 4
    TOTAL_FILES = (DIRS**3)*FILES
    DIR_PACK = ("BEGIN " +
                " ".join(["dir_{:02d}/".format(x) for x in range(DIRS)]) +
                " END\r\n")
    FILE_PACK = ("BEGIN " +
                 " ".join(["file_{:02d}".format(x) for x in range(FILES)]) +
                 " END\r\n")

    BUFFER_SIZE = 1024
    HOST = '127.0.0.1'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("server socket created")
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"server socket listening at ip {HOST} port {PORT}")

        while True:
            # accept loop
            try:
                conn, addr = s.accept()
                with conn:
                    print('connected by', addr)
                    client_quit = False
                    frag = ""

                    while True:
                        try:
                            # handle recv
                            requests, frag = process_recv(conn, frag)

                            # process requests/responses
                            for req in requests:

                                if "QUIT" in req:
                                    client_quit = True
                                    break

                                # count request depth
                                count = req.count("/")
                                if count < MAX_DEPTH:
                                    resp = DIR_PACK
                                elif count == MAX_DEPTH:
                                    resp = FILE_PACK
                                else:
                                    # invalid client request
                                    send_response(conn, "ERROR")
                                    break
                                send_response(conn, resp)

                            if client_quit:
                                print(f"client disconnected")
                                break

                        except (BrokenPipeError, ConnectionResetError) as e:
                            break  # graceful close

            except (OSError, KeyboardInterrupt) as e:
                print('server stopped')
                if s:
                    s.close()
                sys.exit()

