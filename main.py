import sys
import socket
import hashlib

MTU = 1500
PAYLOAD_SIZE = 1400

taro_addr = ('169.254.155.219', 60001)
hanako_addr = ('169.254.229.153', 60001)

class FragmentFileTransferPacket:

    file_num = 0
    fragment_index = 0
    payload = b'00'

    def __init__(self):
        pass

    def input_fields(self, file_num, fragment_index, payload):
        self.file_num = file_num
        self.fragment_index = fragment_index
        self.payload = payload

    def decode(self, bin):
        self.file_num = int.from_bytes(bin[0:3], 'little', signed=False)
        self.fragment_index = int.from_bytes(bin[4:7], 'little', signed=False)
        len = int.from_bytes(bin[7:11], 'little', signed=False)
        self.payload = bin[12:12+len].decode(encoding='ascii')

    def encode(self):
        field_file_num = (self.file_num).to_bytes(4, byteorder="little", signed=False)
        field_fragment_index = (self.fragment_index).to_bytes(4, byteorder="little", signed=False)
        field_payload = self.payload.encode(encoding='ascii')
        field_payload_len = len(field_payload).to_bytes(4, byteorder="little", signed=False)
        packet = field_file_num + field_fragment_index + field_payload_len + field_payload
        return packet

def read_file(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data

def append_file(path, data):
    f = open(path, 'a')
    f.write(data)
    f.close()

def taro():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(0,1000):
        print('Started sending file ' + str(i))
        data = read_file('/home/pi/robust/data/data' + str(i))
        data_len = len(data)
        for j in range(0, int(data_len/PAYLOAD_SIZE)):
            separated_data = data[j*PAYLOAD_SIZE:(j+1)*PAYLOAD_SIZE]
            pk = FragmentFileTransferPacket()
            pk.input_fields(i, j, separated_data)
            bin = pk.encode()

            send_len = sock.sendto(bin, hanako_addr)
def hanako():
    sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.bind(hanako_addr)
    while(True):
        msg, client_addr = sock.recvfrom(MTU)
        pk = FragmentFileTransferPacket()
        pk.decode(msg)
        #print(msg.hex())
        #print(pk.payload)
        append_file('data/data' + str(pk.file_num), pk.payload)

if __name__ == '__main__':

    args = sys.argv

    if 2 <= len(args) and sys.argv[1] == 'hanako':
        hanako()
    else:
        taro()
