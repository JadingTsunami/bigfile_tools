import blackboxprotobuf
import sys
import struct

def read7bit(f):
    more = True
    val = 0
    order = 0
    while more:
        num = int.from_bytes(f.read(1), 'little')
        more = ((num >> 7) & 0x01)
        val += ((num&0x7f) << (order*7))
        order += 1

    return val

def write7bit(val, of):
    while val:
        b = (val & 0x7F)
        val >>= 7
        if val:
            b |= 0x80
        of.write(b.to_bytes(1,"little"))

with open("bigdata/bigfile.decomp", "rb") as f, open("bigdata/bigcopy", "wb") as of:
    total_chunks = struct.unpack('i', f.read(4))[0]
    print("Chunks: " + str(total_chunks))
    of.write(total_chunks.to_bytes(4,"little"))
    for i in range(total_chunks):
        s1len = read7bit(f)
        s1 = f.read(s1len)
        write7bit(s1len, of)
        of.write(s1)

        s2len = read7bit(f)
        s2 = f.read(s2len)
        write7bit(s2len, of)
        of.write(s2)

        protobuf_size = struct.unpack('i', f.read(4))[0]
        protobuf = f.read(protobuf_size)


        if i == 1:
            message,typedef = blackboxprotobuf.decode_message(protobuf)
            msg = blackboxprotobuf.encode_message(message,typedef)

            of.write(len(msg).to_bytes(4,"little"))
            of.write(msg)
        else:
            of.write(protobuf_size.to_bytes(4,"little"))
            of.write(protobuf)
    print("Done")
