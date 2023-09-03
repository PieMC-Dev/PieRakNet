#
#
# //--------\\    [----------]   ||--------]   ||\      /||    ||----------]
# ||        ||         ||        ||            ||\\    //||    ||
# ||        //         ||        ||======|     || \\  // ||    ||
# ||-------//          ||        ||            ||  \\//  ||    ||
# ||                   ||        ||            ||   —–   ||    ||
# ||              [----------]   ||--------]   ||        ||    ||----------]
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# @author PieMC Team
# @link http://www.PieMC-Dev.github.io/
#
#
#

import struct
from io import BytesIO

class UnsupportedIPVersion(Exception):
    pass


class EOSError(Exception):
    pass


class BuffError(Exception):
    pass


class Buffer(BytesIO):
    def feos(self):
        if len(self.getvalue()[self.tell():]) == 0:
            return True
        else:
            return False

    def read_packet_id(self):  # Read Packet ID
        return self.read_byte()

    def write_packet_id(self, data):
        self.write_byte(str(data))

    def read_byte(self):
        return struct.unpack('B', self.read(1))[0]

    def write_byte(self, data):
        if not isinstance(data, bytes):
            data = str(data).encode()
        self.write(struct.pack('B', int(data)))
        
    def read_bits(self, num_bits):
        byte_data = self.read((num_bits + 7) // 8)
        bits = []
        for byte in byte_data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits[:num_bits]
    
    def write_bits(self, bit_array):
        num_bits = len(bit_array)
        num_bytes = (num_bits + 7) // 8
        byte_data = bytearray(num_bytes)
        for i, bit in enumerate(bit_array):
            byte_index = i // 8
            bit_index = 7 - (i % 8)
            if bit:
                byte_data[byte_index] |= (1 << bit_index)
        self.write(byte_data)
        
    def read_ubyte(self):
        return struct.unpack('<B', self.read(1))[0]

    def write_ubyte(self, data):
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        self.write(struct.pack('<B', data))

    def read_short(self):
        shrt = self.read(2)
        print(shrt)
        return struct.unpack('>h', shrt)[0]

    def write_short(self, data):
        self.write(struct.pack('>h', data))

    def read_unsigned_short(self):
        ushrt = self.read(2)
        return struct.unpack('>H', ushrt)[0]

    def write_unsigned_short(self, data):
        self.write(struct.pack('>H', data))

    def read_magic(self):
        return self.read(16)

    def write_magic(self, data=b'00ffff00fefefefefdfdfdfd12345678'):
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        self.write(data)

    def read_long(self):
        return struct.unpack('>q', self.read(8))[0]

    def write_long(self, data):
        self.write(struct.pack('>q', data))

    def read_ulong(self):
        return struct.unpack('>Q', self.read(8))[0]

    def write_ulong(self, data):
        self.write(struct.pack('>Q', data))

    def read_int(self):
        dat = self.read(4)
        print(dat)
        return struct.unpack(">i", dat)[0]

    def write_int(self, data):
        self.write(struct.pack('>i', data))

    def read_uint(self):
        return struct.unpack(">I", self.read(4))[0]

    def write_uint(self, data):
        self.write(struct.pack('>I', data))

    def read_bool(self):
        return struct.unpack('?', self.read(1))[0]

    def write_bool(self, data):
        self.write(struct.pack('?', data))

    def read_uint24le(self):
        uint24le = self.read(3) + b'\x00'
        return struct.unpack("<I", uint24le)[0]

    def write_uint24le(self, data):
        self.write(struct.pack("<I", data)[:3])

    def read_string(self):
        length = self.read_short()
        string = self.read(length).decode('ascii')
        return string

    def write_string(self, data):
        self.write_short(len(data))
        if not isinstance(data, bytes):
            data = data.encode('ascii')
        self.write(data)

    def read_address(self):
        ipv = self.read_byte()
        if ipv == 4:
            hostname_parts = []
            for part in range(4):
                hostname_parts.append(str(~self.read_byte() & 0xff))
            hostname = ".".join(hostname_parts)
            port = self.read_unsigned_short()
            return hostname, port
        else:
            raise UnsupportedIPVersion('IP version is not 4')

    def write_address(self, address: tuple):
        self.write_byte(4)
        hostname_parts: list = address[0].split('.')
        for part in hostname_parts:
            self.write_byte(~int(part) & 0xff)
        self.write_unsigned_short(address[1])

    def read_var_int(self):
        value: int = 0
        for i in range(0, 35, 7):
            number = self.read_ubyte()
            value |= ((number & 0x7f) << i)
            if (number & 0x80) == 0:
                return value
        raise BuffError("VarInt is too big")

    def write_var_int(self, value: int) -> None:
        value &= 0xffffffff
        for i in range(0, 5):
            to_write: int = value & 0x7f
            value >>= 7
            if value != 0:
                self.write_ubyte(to_write | 0x80)
            else:
                self.write_ubyte(to_write)
                break
