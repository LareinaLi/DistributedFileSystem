# DistributedFileSystem
for class CS7NS1

Student: Xuan Li

Student ID: 17303493

run 'file_server.py' before running 'file_client.py'

the default root directory called 'FileSystemDirectory', in the same directory of all the python files.

Instrunctions:
1. ls   -  list everything in the current directory
2. cd PATH  -  change directory to PATH
3. up   -  move up one directory
4. read FILENAME  -  read the content of the file FINENAME
5. write FILENAME CONTENT   -  write CONTENT to the file FILENAME, if the file do not exist, it will create a new file
6. delete FILENAME  -  delete the file FILENAME
7. lock FILENAME  -  lock the file FILENAME
8. release FILENAME   -  release the file FILENAME, only the user who lock it can release it
9. mkdir DIRECTORY  -  create a new directory DIRECTORY in current directory
10. rmdir DIRECTORY  -  delete the directory DIRECTORY in current directory
11. pwd   -  get the path of current directory
12. exit  -  exit the connection

Components:
1. Lock Service
2. Caching
3. Directory Service
4. Distributed Transparent File Access
