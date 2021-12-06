import socket
serverAddressPort= ('192.168.0.103', 60001)
bufferSize= 1024
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
def client_run():
    while True:
        data_to_send = '1, 1, 1, 1, 1, 1\n'
        bytes_to_send= str.encode(data_to_send)
        UDPClientSocket.sendto(bytes_to_send, serverAddressPort)

if __name__ == "__main__":
    client_run()