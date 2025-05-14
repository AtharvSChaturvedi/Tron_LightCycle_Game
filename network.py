#Connects CLU and User
import json
import struct

def send_json(conn, data):
    message = json.dumps(data).encode()
    conn.sendall(struct.pack('>I', len(message)) + message)

def recv_json(conn):
    raw_msglen = recvall(conn, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    return json.loads(recvall(conn, msglen).decode())

def recvall(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
