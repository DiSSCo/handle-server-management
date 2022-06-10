# Overview

This repository contains scripts for managing handle records in the DiSSCo Test Handle Server. This code is based off of examples provided by Alan Smith: https://github.com/theNBS/handleserver-samples. 

## Authentication

Authentication is done either per operation, using an authenticated admin key every time, or by establishing an authenticated session with the admin key once. When a handle server is created, its keys are in generated .bin format. In order to use the this code, you must convert your private key to PEM format using the hdl-convert-key tool. This will convert your key to an RSA PEM. 

```
handle-9.3.0/bin/hdl-convert-key handle_svr/admpriv.bin
```
Where the first argument is the handle.net software directory (and the location of the key converting tool), and the second argument is the key to be converted. 

## Connection Values (connection_values.py)

This file contains variables necessary for the connection to a specific server. 

* key_file: location of private key (adminpriv.pem)
* admin_id: administrative handle
* prefix: Prefix granted by CNRI or another MPA
* ip: public IP address to which the server binds

## Handle Manager (handle_manager.py)

This file provides examples on how to interface with the handle server using the handle API. Operations are either authenticated using sessions (sessions_mode = True) or by key authentication (sessions_mode = False) 

* gen_basic_record(): generate a record for testing purposes
* create_handle_record()
* get_handle_record() 
* update_handle_record()
* delete_handle_record()


# Server Overview
This section provides more information on managing the handle server. The handle server DiSSCo is deployed in an AWS EC2 Server. The server contains the admin keys needed for these operations. Some basic specifications about the server follows. 

* Handle prefix: 20.5000.1025
* Admin ID: 0.NA/20.5000.1025
* Not dual-stack (i.e. accessible only via IPv4)
* HTTP interface: Port 8000
* Public IP address: 35.178.174.137

## Handle Server Requirements

Handle.net software version 9.3.0 will run on most platforms with Java 8 or higher. Some functionality, such as the admintool (a GUI that provides basic admin functions to the handle server), must be run from an X11 environment. This means a headless version of Java is insufficient. If you're accessing the server remotely, you must include the "-X" tag when you ssh in.

```
ssh -X hostname
```

## Batch File Operations

Along with python script provided in this repository, it is possible to manage handles using batch files. The structure of the commands is as follows. Note that each batch file must contain an "AUTHENTICATE" operation as its header.

```
AUTHENTICATE PUBKEY:300:0.NA/20.5000.1025
/home/ubuntu/hs/handle_svr/admpriv.bin

CREATE 20.5000.1025/123
100 HS_ADMIN 86400 011111110011 ADMIN 300:110011111111:0.NA/20.5000.1025
1 NAME 86400 1110 UTF8 Soulaine
2 URL 86400 1110 UTF8 https://sandbox.dissco.tech/

ADD 20.5000.1025/123
3 INSTITUTE_CODE 86400 1110 UTF8 Naturalist
4 INSTITUTE_ID 86400 1110 UTF8 https://ror.org/0566bfb96

MODIFY 20.5000.1025/123
3 INSTITUTE_CODE 86400 1110 UTF8 Naturalis

DELETE 20.5000.1025/123

```

## More Information
Handle.net Software Technical Manual (Version 9): http://www.handle.net/tech_manual/HN_Tech_Manual_9.pdf



