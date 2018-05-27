# Tiny FTP Server/Client
A simple FTP implementation using basic socket interface 

#### How to use
On you server, please run

```python
.../tinyftp$ python server.py
```
On the client side, please run

```python
.../tinyftp$ python client.py [server_ip]
```
When connected, subcommand on the client side might be like {list,get,put,cd,lcd,pwd,lpwd} [fileordirectory]

Some examples may be

```
Tinyftp>>>list
Tinyftp>>>get a.txt
Tinyftp>>>put a.txt
```

#### TODO
* sub thread handling
* connection reset handling
