#!/bin/python
import socket, subprocess, shlex, ssl
HOST = ""
PORT = 59999
server_cert = '/home/k8s/multi-cluster-controller/server.crt'
server_key = '/home/k8s/multi-cluster-controller/server.key'
client_certs = '/home/k8s/multi-cluster-controller/client.crt'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)

print("Listening ...")

while True:

    conn, addr = s.accept()
    print("[+] Client connected: ", addr)
    conn = context.wrap_socket(conn, server_side=True)
    print("SSL established. Peer: {}".format(conn.getpeercert()))

    JOIN = False
    while True:
        data = conn.recv(4096)
        if not data:
            print('finished transmission')
            break
        elif data.endswith(b'//stop'):
            print('Detected stop flag')
            data = data.replace(b'//stop', b'')
            break
        elif data.endswith(b'request-join-command'):
            JOIN = True
            print("Asking for join_cmd {}".format(data))
    print("[+] Request complete!")
    if JOIN == True:
        cmd='kubeadm token create --print-join-command'
        join_cmd=subprocess.check_output(shlex.split(cmd), universal_newlines=True)
        print('cmd sent with {}'.format(join_cmd))
        conn.send(join_cmd)
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()
