import blackboxprotobuf
import sys
import struct

def read7bit(f):
    more = True
    val = 0
    order = 0
    while more:
        num = int.from_bytes(f.read(1), 'big')
        more = ((num >> 7) & 0x01)
        val += ((num&0x7f) << (order*7))
        order += 1

    return val

with open("bigdata/bigfile.decomp", "rb") as f:
    total_chunks = struct.unpack('i', f.read(4))[0]
    print("Chunks: " + str(total_chunks))
    for i in range(total_chunks):
        s1len = read7bit(f)
        s1 = f.read(s1len)
        print(str(s1, 'UTF-8'))

        s2len = read7bit(f)
        s2 = f.read(s2len)
        print(str(s2, 'UTF-8'))

        protobuf_size = struct.unpack('i', f.read(4))[0]
        print("Size: " + str(protobuf_size) + " bytes")
        sys.stdout.flush()
        protobuf = f.read(protobuf_size)
        message,typedef = blackboxprotobuf.decode_message(protobuf)
        data = blackboxprotobuf.encode_message(message,typedef)
        print(str(message))
        print(str(typedef))
        print(str(data))

    print("Done")
