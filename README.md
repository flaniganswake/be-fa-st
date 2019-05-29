BeFaSt
============
BeFaSt is a client/server implementation using loopback/localhost TCP. It is a BFS directory structure query searching for the total number of files.

### Server

The server.py process sends simulated directory listings over a TCP socket. Only one concurrent TCP connection is necessary (the server must not fork, use threads, or use select() to multiplex connections). When the client disconnects, the server must close the socket and wait for another connection.

The simulated root directory ("/") contains 100 subdirectories, which will be referred to as "level 1 subdirectories". Each "level 1 subdirectory" contains 100 subdirectories, aka "level 2". Each "level 2 subdirectory" contains 100 subdirectories, aka "level 3". Each "level 3 subdirectory" contains 3
files. Thus, there are 1 million (100 * 100 * 100) "level 3 subdirectories", and 3 million total files.

The files and directories are named as follows:

```
/dir\_00/dir\_00/dir\_00/file\_00

/dir\_00/dir\_00/dir\_00/file\_01

/dir\_00/dir\_00/dir\_00/file\_02

...

/dir\_99/dir\_99/dir\_99/file\_00

/dir\_99/dir\_99/dir\_99/file\_01

/dir\_99/dir\_99/dir\_99/file\_02
```

### Client

The client.py process connects to the server and scans the entire directory structure, starting at "/". It prints out the total number of files found. The client MUST use pipelining; up to 20 DIRLIST commands must be in the pipeline to the server when possible, to avoid network or CPU latency. Note that the client can not assume any prior knowledge of the simulated directory structure; it has to start with "/" and take action based on the server responses.

### Protocol

The protocol is line based, and each line is ended by a "\r\n" sequence (for simplicity the protocol assumes that sequence will not exist in a path name).

The DIRLIST command lists a single directory, which may be the root ("/") or one of the subdirectories, e.g. "/dir_99/". The directory must start and end with a '/' character. Paths are case sensitive.

The syntax is __DIRLIST \<space\> \<directory\>__

A command line of __DIRLIST /__ or __DIRLIST /dir\_00/dir\_23/__ will return:

```
BEGIN dir\_00/ dir\_01/ ... dir\_99/ END
```

A command line of __DIRLIST /dir\_00/dir\_00/dir\_00/__ will return:

```
BEGIN file\_00 file\_01 file\_02 END
```

A successful response is a "BEGIN" line, 0 or more path lines that each start with a space, and a final "END" line. Subdirectories in a response path have a trailing "/" (that is the only place a "/" is allowed).

### Remarks

The intention is accuracy and speed. A successful run will take less than 2 minutes. This implementation takes about 13 seconds. For this test case number subdirectories = 100.

```
./server.py \<number subdirectories\>
```

```
time ./client.py
```

### Test Runs

```
s(subdirs), d(depth), f(files)
total_dirs = lambda s,d: sum([s**n for n in range(1,d)])
total_files = lambda s,d,f: f*(s**(d-1))
```
```
subdirs -> total_dirs, total_files
3   -> 39, 81
4   -> 84, 192
5   -> 155, 375
10  -> 1110, 3000
20  -> 8420, 24000
30  -> 27930, 81000
40  -> 65640, 192000
60  -> 219660, 648000
80  -> 518480, 1536000
100 -> 1010100, 3000000
```
