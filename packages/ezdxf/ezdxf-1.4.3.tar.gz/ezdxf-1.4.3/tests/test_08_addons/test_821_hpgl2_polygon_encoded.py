#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons.hpgl2.tokenizer import pe_encode, pe_decode, fractional_bits


class TestPolylineEncoding:
    def test_8_bit(self):
        s = pe_encode(10525)
        assert s[0] == 121
        assert s[1] == 71
        assert s[2] == 196

    def test_7_bit(self):
        s = pe_encode(10525, base=32)
        assert s[0] == 89
        assert s[1] == 80
        assert s[2] == 115


class TestPolylineDecoding:
    def test_8_bit(self):
        s = pe_encode(10525) + pe_encode(-10525)
        values, index = list(pe_decode(s))
        assert values[0] == 10525
        assert values[1] == -10525
        assert index == len(s)

    def test_7_bit(self):
        s = pe_encode(10525, base=32) + pe_encode(-10525, base=32)
        values, index = pe_decode(s, base=32)
        assert values[0] == 10525
        assert values[1] == -10525
        assert index == len(s)

    def test_8_bit_float(self):
        n = fractional_bits(3)
        s = pe_encode(10.525, frac_bits=n) + pe_encode(-10.525, frac_bits=n)
        values, index = list(pe_decode(s, frac_bits=n))
        assert round(values[0], 3) == 10.525
        assert round(values[1], 3) == -10.525
        assert index == len(s)


if __name__ == "__main__":
    pytest.main([__file__])
