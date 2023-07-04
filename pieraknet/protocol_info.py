class ProtocolInfo:
    ONLINE_PING = 0x00
    OFFLINE_PING = 0x01
    OFFLINE_PING_OPEN_CONNECTIONS = 0x02
    ONLINE_PONG = 0x03
    OFFLINE_PONG = 0x1c
    OPEN_CONNECTION_REQUEST_1 = 0x05
    OPEN_CONNECTION_REPLY_1 = 0x06
    OPEN_CONNECTION_REQUEST_2 = 0x07
    OPEN_CONNECTION_REPLY_2 = 0x08
    CONNECTION_REQUEST = 0x09
    CONNECTION_REQUEST_ACCEPTED = 0x10
    NEW_INCOMING_CONNECTION = 0x13
    DISCONNECT = 0x15
    INCOMPATIBLE_PROTOCOL_VERSION = 0x19
    FRAME_SET = 0x80
    NACK = 0xa0
    ACK = 0xc0