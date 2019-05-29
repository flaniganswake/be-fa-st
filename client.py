#!/usr/bin/env python3
#
# BFS directory walk of server
# best 100 subdirs: 0m48.116s
# without stdout: 0m13.373s
# flaniganswake@protonmail.com
#

from collections import deque
import socket

_fast = True


def send_request(sock, req, show=True):
    ''' send request to server '''
    m = f"DIRLIST /{req}\r\n"
    try:
        m = str.encode(m)
        if show and not _fast:
            print(f'\rsend: {m}', sep=' ', end='', flush=True)
        sock.sendall(m)
    except Exception as e:
        print(f"send exception: {e}")
        raise


def extract_responses(arr, begin, end, f):
    ''' extract responses from lines '''
    results = []
    for elem in arr:
        # handle line fragments
        if not elem.startswith(begin) and f:
            elem = f+elem
            f = ""
        elif not elem.endswith(end):
            f = elem
            continue
        results.append(elem.split())
    return (results, f)


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
        return extract_responses(lines, "BEGIN", "\n", f)


if __name__ == "__main__":

    BUFFER_SIZE = 1024
    HOST = '127.0.0.1'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((HOST, PORT))

        path_que = deque([""])
        resp_que = deque()
        dirs, files = 0, 0
        frag = ""

        # start with root
        sends, pending = 0, 1
        send_request(s, "")
        while path_que:
            try:
                # handle recv
                responses, frag = process_recv(s, frag)
                resp_que += deque(responses)

                # process response/requests blocks
                while resp_que and sends <= pending:
                    resp = resp_que.popleft()
                    path = path_que.popleft()
                    for node in resp:
                        if "/" in node:
                            dirs += 1
                            next_path = path+node
                            path_que.append(next_path)
                            send_request(s, next_path)
                            sends += 1
                        elif node not in ('BEGIN', 'END'):
                            files += 1
                pending = sends
                sends = 0

            except Exception as e:
                print(f"recv exception: {e}")
                raise

        # notify server we are done
        send_request(s, "QUIT", False)
        print(f"\ntotal dirs: {dirs}")
        print(f"total files: {files}")

