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
        return len(self.getvalue()[self.tell():]) == 0

    def read_packet_id(self):  # Read Packet ID
        return self.read_byte()

    def write_packet_id(self, data):
        self.write_byte(data)

    def read_byte(self):
        return struct.unpack('B', self.read(1))[0]

    def write_byte(self, data):
        self.write(struct.pack('B', data))
        
    def read_bits(self, num_bits):
        # Calculate the number of bytes needed
        num_bytes = (num_bits + 7) // 8
        # Read the bytes from the stream
        byte_data = self.read(num_bytes)
        
        if len(byte_data) < num_bytes:
            raise ValueError("Not enough data to read the required number of bits")

        bits = []
        # Extract bits from each byte
        for byte in byte_data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)

        # Return only the requested number of bits
        return bits[:num_bits]

    def write_bits(self, bit_array):
        # Ensure the input array contains only 0s and 1s
        if not all(bit in (0, 1) for bit in bit_array):
            raise ValueError("bit_array must contain only 0s and 1s")

        num_bits = len(bit_array)
        num_bytes = (num_bits + 7) // 8
        byte_data = bytearray(num_bytes)
        
        # Construct the byte data
        for i, bit in enumerate(bit_array):
            byte_index = i // 8
            bit_index = 7 - (i % 8)
            if bit:
                byte_data[byte_index] |= (1 << bit_index)

        # Write the bytes to the stream
        self.write(byte_data)

    def read_ubyte(self):
        return struct.unpack('B', self.read(1))[0]

    def write_ubyte(self, data):
        self.write(struct.pack('B', data))

    def read_short(self):
        shrt = self.read(2)
        return struct.unpack('!h', shrt)[0]

    def write_short(self, data):
        self.write(struct.pack('!h', data))

    def read_unsigned_short(self):
        ushrt = self.read(2)
        return struct.unpack('!H', ushrt)[0]

    def write_unsigned_short(self, data):
        if not isinstance(data, int):
            raise ValueError(f"Expected an integer, got {type(data).__name__}")
        self.write(struct.pack('!H', data))

    def read_magic(self):
        return self.read(16)

    def write_magic(self, data=b'00ffff00fefefefefdfdfdfd12345678'):
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        if len(data) != 16:
            raise ValueError("Data must be exactly 16 bytes long.")
        self.write(data)

    def read_long(self):
        return struct.unpack('!q', self.read(8))[0]

    def write_long(self, data):
        if not isinstance(data, int):
            raise TypeError("Data must be an integer.")
        if not -2**63 <= data < 2**63:
            raise ValueError("Data must be within the range of a 64-bit signed integer.")
        self.write(struct.pack('!q', data))

    def read_ulong(self):
        return struct.unpack('!Q', self.read(8))[0]

    def write_ulong(self, data):
        if not isinstance(data, int):
            raise TypeError("Data must be an integer.")
        if not 0 <= data < 2**64:
            raise ValueError("Data must be within the range of a 64-bit unsigned integer.")
        self.write(struct.pack('!Q', data))

    def read_int(self):
        dat = self.read(4)
        return struct.unpack("!i", dat)[0]

    def write_int(self, data):
        if not isinstance(data, int):
            raise TypeError("Data must be an integer.")
        if not -2**31 <= data < 2**31:
            raise ValueError("Data must be within the range of a 32-bit signed integer.")
        self.write(struct.pack('!i', data))

    def read_uint(self):
        return struct.unpack("!I", self.read(4))[0]

    def write_uint(self, data):
        if not isinstance(data, int):
            raise TypeError("Data must be an integer.")
        if not 0 <= data < 2**32:
            raise ValueError("Data must be within the range of a 32-bit unsigned integer.")
        self.write(struct.pack('!I', data))

    def read_bool(self):
        return struct.unpack('?', self.read(1))[0]

    def write_bool(self, data):
        if not isinstance(data, bool):
            raise TypeError("Data must be a boolean value.")
        self.write(struct.pack('?', data))

    def read_uint24le(self):
        uint24le = self.read(3) + b'\x00'
        return struct.unpack("<I", uint24le)[0]

    def write_uint24le(self, data):
        if not isinstance(data, int):
            raise TypeError("Data must be an integer.")
        if not 0 <= data < 2**24:
            raise ValueError("Data must be within the range of a 24-bit unsigned integer.")
        self.write(struct.pack("<I", data)[:3])

    def read_string(self):
        length = self.read_short()
        if length < 0 or length > 65535:
            raise ValueError("String length out of range for a 16-bit length field.")
        string = self.read(length).decode('ascii')
        return string

    def write_string(self, data):
        if isinstance(data, str):
            data = data.encode('ascii')
        elif not isinstance(data, bytes):
            raise TypeError("Data must be a string or bytes.")
        if len(data) > 65535:
            raise ValueError("String data is too long for a 16-bit length field.")
        self.write_short(len(data))
        self.write(data)

    def read_address(self):
        ipv = self.read_byte()
        if ipv == 4:  # IPv4
            octets = [self.read_byte() for _ in range(4)]
            hostname = '.'.join(map(str, octets))
            port = self.read_unsigned_short()
            return hostname, port
        elif ipv == 6:  # IPv6
            hextets = [self.read_byte() << 8 | self.read_byte() for _ in range(8)]
            hostname = ':'.join(format(hextet, 'x') for hextet in hextets)
            port = self.read_unsigned_short()
            return hostname, port
        else:
            raise UnsupportedIPVersion('IP version is not supported')

    def write_address(self, address: tuple):
        if not isinstance(address, tuple) or len(address) != 2:
            raise TypeError("Address must be a tuple with (hostname, port).")
        
        hostname, port = address

        if not isinstance(hostname, str):
            raise TypeError("Hostname must be a string.")
        if not isinstance(port, int) or not (0 <= port <= 65535):
            raise ValueError("Port must be an integer between 0 and 65535.")
        
        if ':' in hostname:  # IPv6
            self.write_byte(6)
            hextets = hostname.split(':')
            if len(hextets) != 8:
                raise ValueError("Invalid IPv6 address format.")
            for hextet in hextets:
                self.write_byte(int(hextet, 16) >> 8)
                self.write_byte(int(hextet, 16) & 0xFF)
        else:  # IPv4
            self.write_byte(4)
            octets = hostname.split('.')
            if len(octets) != 4:
                raise ValueError("Invalid IPv4 address format.")
            for octet in octets:
                self.write_byte(int(octet))
        
        self.write_unsigned_short(port)


    def read_var_int(self):
        value: int = 0
        for i in range(0, 35, 7):
            number = self.read_ubyte()
            value |= ((number & 0x7f) << i)
            if (number & 0x80) == 0:
                return value
        raise BuffError("VarInt is too big")

    def write_var_int(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Value must be an integer.")
        if not (0 <= value < 2**32):
            raise ValueError("Value must be within the range of a 32-bit unsigned integer.")
        
        value &= 0xffffffff
        while True:
            to_write = value & 0x7f
            value >>= 7
            if value:
                self.write_ubyte(to_write | 0x80)
            else:
                self.write_ubyte(to_write)
                break

    def read_remaining(self):
        return self.read(self.remaining())  # Lee todos los bytes restantes en el búfer

    def remaining(self):
        return len(self.getvalue()) - self.tell()

    def read_flags(self):
        flags_byte = self.read_byte()
        reliability_type = (flags_byte >> 5) & 0b111  # Top 3 bits
        is_fragmented = (flags_byte & 0b00001000) != 0  # Fourth bit
        return reliability_type, is_fragmented

    def write_flags(self, reliability_type, is_fragmented):
        if not (0 <= reliability_type <= 7):
            raise ValueError("Reliability type must be between 0 and 7.")
        
        flags_byte = (reliability_type << 5) | (0b00001000 if is_fragmented else 0)
        self.write_byte(flags_byte)
