from pieraknet.core.serialization.data_types import (
    Byte,
    Integer,
    Long,
    Short,
    String,
    Boolean,
    AddressV4,
    AddressV6,
    AddressUnion,
    UnsignedInt24,
    UnsignedInteger,
    UnsignedShort,
    Magic,
    RakNetDataUnion,
)


class TestSerialization:
    def test_byte(self):
        assert Byte(42).serialize() == b"*"
        assert Byte.deserialize(b"*") == Byte(42)

    def test_integer(self):
        assert Integer(42).serialize() == b"*\x00\x00\x00"
        assert Integer.deserialize(b"*\x00\x00\x00") == Integer(42)

    def test_long(self):
        assert Long(42).serialize() == b"\x00\x00\x00\x00\x00\x00\x00*"
        assert Long.deserialize(b"\x00\x00\x00\x00\x00\x00\x00*") == Long(42)

    def test_short(self):
        assert Short(42).serialize() == b"\x00*"
        assert Short.deserialize(b"\x00*") == Short(42)

    def test_boolean(self):
        assert Boolean(True).serialize() == b"\x01"
        assert Boolean.deserialize(b"\x01") == Boolean(True)
        assert Boolean(False).serialize() == b"\x00"
        assert Boolean.deserialize(b"\x00") == Boolean(False)

    def test_string(self):
        assert String("Hello, world!").serialize() == b"\x00\rHello, world!"
        assert String.deserialize(b"\x00\rHello, world!") == String("Hello, world!")

    def test_address_v4(self):
        address = AddressV4.from_str("127.0.0.1", 19132)
        assert address.serialize() == b"\x04\x7f\x00\x00\x01J\xbc"
        assert AddressV4.deserialize(b"\x04\x7f\x00\x00\x01J\xbc") == address

    def test_address_v6(self):
        CONST_ENCODED_ADDRESSES = (
            b"\x06\x17\x00\x00\x00J\xbc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00",
            b"\x06\x17\x00\x00\x00J\xbc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b"\x06\x17\x00\x00\x00J\xbc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )
        assert (
            AddressV6.from_str("::1", 19132, 0).serialize()
            == CONST_ENCODED_ADDRESSES[0]
        )
        assert (
            AddressV6.from_str("::", 19132, 0).serialize() == CONST_ENCODED_ADDRESSES[1]
        )
        assert (
            AddressV6.from_str(
                "0000:0000:0000:0000:0000:0000:0000:0000", 19132, 0
            ).serialize()
            == CONST_ENCODED_ADDRESSES[2]
        )
        assert AddressV6.deserialize(CONST_ENCODED_ADDRESSES[0]) == AddressV6.from_str(
            "::1", 19132, 0
        )
        assert AddressV6.deserialize(CONST_ENCODED_ADDRESSES[1]) == AddressV6.from_str(
            "::", 19132, 0
        )
        assert AddressV6.deserialize(CONST_ENCODED_ADDRESSES[2]) == AddressV6.from_str(
            "0000:0000:0000:0000:0000:0000:0000:0000", 19132, 0
        )

    def test_address_union(self):
        address_v4 = AddressV4.from_str("127.0.0.1", 19132)
        address_v6 = AddressV6.from_str("::1", 19132, 0)
        address_union_v4 = AddressUnion(4, address_v4)
        address_union_v6 = AddressUnion(6, address_v6)
        assert address_union_v4.serialize() == address_v4.serialize()
        assert address_union_v6.serialize() == address_v6.serialize()
        assert AddressUnion.deserialize(address_v4.serialize()) == address_union_v4
        assert AddressUnion.deserialize(address_v6.serialize()) == address_union_v6
        assert AddressV4.deserialize(address_union_v4.serialize()) == address_v4
        assert AddressV6.deserialize(address_union_v6.serialize()) == address_v6
        assert (
            AddressUnion.deserialize(address_union_v4.serialize()) == address_union_v4
        )
        assert (
            AddressUnion.deserialize(address_union_v6.serialize()) == address_union_v6
        )

    def test_magic(self):
        assert (
            Magic().serialize()
            == b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx"
        )
        assert (
            Magic.deserialize(
                b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx"
            )
            == Magic()
        )

    def test_unsigned_int24(self):
        assert UnsignedInt24(42).serialize() == b"*\x00\x00"
        assert UnsignedInt24.deserialize(b"*\x00\x00") == UnsignedInt24(42)

    def test_unsigned_integer(self):
        assert UnsignedInteger(42).serialize() == b"*\x00\x00\x00"
        assert UnsignedInteger.deserialize(b"*\x00\x00\x00") == UnsignedInteger(42)

    def test_unsigned_short(self):
        assert UnsignedShort(42).serialize() == b"\x00*"
        assert UnsignedShort.deserialize(b"\x00*") == UnsignedShort(42)

    def test_unions(self):
        data_union = (
            Byte(1)
            + Integer(2)
            + Long(3)
            + Short(4)
            + Boolean(True)
            + String("Hello, world!")
            + AddressV4.from_str("127.0.0.1", 19132)
            + AddressV6.from_str("::1", 19132, 0)
            + AddressUnion(4, AddressV4.from_str("127.0.0.1", 19132))
            + AddressUnion(6, AddressV6.from_str("::1", 19132, 0))
            + Magic()
            + UnsignedInt24(42)
            + UnsignedInteger(42)
            + UnsignedShort(42)
        )
        type_union = (
            Byte
            + Integer
            + Long
            + Short
            + Boolean
            + String
            + AddressV4
            + AddressV6
            + AddressUnion
            + AddressUnion
            + Magic
            + UnsignedInt24
            + UnsignedInteger
            + UnsignedShort
        )
        serialized_data = data_union.serialize()
        repaired_union = RakNetDataUnion(
            RakNetDataUnion.deserialize(
                serialized_data,
                [
                    Byte,
                    Integer,
                    Long,
                    Short,
                    Boolean,
                    String,
                    AddressV4,
                    AddressV6,
                    AddressUnion,
                    AddressUnion,
                    Magic,
                    UnsignedInt24,
                    UnsignedInteger,
                    UnsignedShort,
                ],
            )
        )
        assert repaired_union == data_union
        assert RakNetDataUnion(type_union.deserialize(serialized_data)) == data_union
