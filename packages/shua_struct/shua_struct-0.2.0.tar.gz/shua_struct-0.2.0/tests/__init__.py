# ruff: noqa: F403, F405
from shua.struct import BinaryStruct
from shua.struct.extensions import UInt8, UInt16, BytesField

def main():
    class SubHeader(BinaryStruct):
        version: UInt8

    class Header(BinaryStruct):
        sub_header: SubHeader
        length: UInt16
    
    def get_length(ctx:dict):
        _length = 8
        length = ctx['header']['length']
        print("="*_length+"get_length"+"="*_length)
        print(f"length is {object.__repr__(length)}")
        print(f"ctx: {ctx}")
        print("="*_length+"get_length"+"="*_length)
        return length
    
    class Packet(BinaryStruct):
        header: Header
        payload: BytesField = BytesField(length=get_length)

    payload = b"Hello World!"
    pkt = Packet(
        header=Header(sub_header=SubHeader(version=1),length=len(payload)),
        payload=payload
    )

    print("Original packet:")
    print(pkt)
    
    data = pkt.build()
    
    print("\nBuilt data:", data.hex())

    parsed_pkt = Packet.parse(data)
    print("\nParsed packet:")
    print(parsed_pkt)

    print("\nField values:")
    print("Version:", parsed_pkt.header.sub_header.version)
    assert parsed_pkt.header.sub_header.version == pkt.header.sub_header.version
    print("Length:", parsed_pkt.header.length)
    assert parsed_pkt.header.length == pkt.header.length
    print("Payload:", parsed_pkt.payload)
    assert parsed_pkt.payload == pkt.payload