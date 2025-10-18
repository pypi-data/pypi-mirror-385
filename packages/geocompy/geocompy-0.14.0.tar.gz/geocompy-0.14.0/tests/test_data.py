import math
from enum import Enum

import pytest
from pytest import approx

from geocompy.data import (
    get_enum,
    get_enum_parser,
    parse_string,
    parse_bool,
    Angle,
    Byte,
    Coordinate,
    Vector
)


class A(Enum):
    MEMBER = 1


class B(Enum):
    MEMBER = 1


class TestFunctions:
    def test_toenum(self) -> None:
        assert get_enum(A, "MEMBER") is A.MEMBER
        assert get_enum(A, A.MEMBER) is A.MEMBER

        with pytest.raises(KeyError):
            get_enum(A, "FAIL")

        with pytest.raises(ValueError):
            get_enum(A, B.MEMBER)

    def test_enumparser(self) -> None:
        assert callable(get_enum_parser(A))
        assert get_enum_parser(A)("1") is A.MEMBER

    def test_parsestr(self) -> None:
        assert parse_string("value") == "value"
        assert parse_string("\"value") == "\"value"
        assert parse_string("value\"") == "value\""
        assert parse_string("\"value\"") == "value"

    def test_parsebool(self) -> None:
        assert parse_bool("0") is False
        assert parse_bool("1") is True


class TestAngle:
    def test_init(self) -> None:
        assert float(Angle(1)) == approx(float(Angle(1, 'rad')))
        assert Angle(100, 'gon').asunit('deg') == approx(90)
        assert Angle.parse("120.0", 'deg').asunit('deg') == approx(120)

        with pytest.raises(ValueError):
            Angle(1, 'A')  # type: ignore[arg-type]

    def test_asunit(self) -> None:
        value = Angle(180, 'deg')
        assert value.asunit('deg') == approx(180)
        assert value.asunit() == value.asunit('rad')
        assert value.asunit('gon') == approx(200)

        with pytest.raises(ValueError):
            value.asunit("a")  # type: ignore[arg-type]

    def test_normalize(self) -> None:
        assert (
            Angle(
                370,
                'deg',
                normalize=True,
                positive=True
            ).asunit('deg')
            == approx(10)
        )
        assert (
            Angle(
                -10,
                'deg',
                normalize=True,
                positive=True
            ).asunit('deg')
            == approx(350)
        )
        assert (
            Angle(
                -370,
                'deg',
                normalize=True,
                positive=True
            ).asunit('deg')
            == approx(350)
        )
        assert (
            Angle(
                -370,
                'deg',
                normalize=True,
                positive=False
            ).asunit('deg')
            == approx(-10)
        )
        assert (
            Angle(370, 'deg', normalize=True).asunit('deg')
            == approx(Angle(370, 'deg').normalized().asunit('deg'))
        )
        assert abs(Angle(-10, 'deg')).asunit('deg') == approx(350)

    def test_relative(self) -> None:
        a1 = Angle(355, 'deg')
        a2 = Angle(5, 'deg')
        a3 = Angle(175, 'deg')
        a4 = Angle(195, 'deg')

        a_10 = float(Angle(10, 'deg'))
        a_170 = float(Angle(170, 'deg'))

        assert float(a1.relative_to(a2)) == approx(-a_10)
        assert float(a2.relative_to(a1)) == approx(a_10)
        assert float(a3.relative_to(a2)) == approx(a_170)
        assert float(a2.relative_to(a3)) == approx(-a_170)
        assert float(a4.relative_to(a2)) == approx(-a_170)
        assert float(a2.relative_to(a4)) == approx(a_170)

    def test_printing(self) -> None:
        a = Angle(10, 'deg')
        assert str(a) == "10.0000 DEG"
        assert repr(a) == "Angle(10-00-00)"
        assert f"{Angle(180, 'deg'):.0f}" == "3"

    def test_arithmetic(self) -> None:
        a1 = Angle(90, 'deg')
        a2 = Angle(90, 'deg')
        a3 = Angle(100, 'deg')
        assert (
            float(a1 + a2)
            == approx(float(Angle(180, 'deg')))
        )
        assert a1 + a3 == a3 + a1
        assert (
            float(a1 - a2)
            == approx(float(Angle(0, 'deg')))
        )
        assert (
            float(a1 * 2)
            == approx(float(Angle(180, 'deg')))
        )
        assert a1 * 2 == 2 * a1
        assert (
            float(a1 / 2)
            == approx(float(Angle(45, 'deg')))
        )
        a1 += math.pi
        assert a1.asunit("deg") == 270

        a1 -= math.pi
        assert float(a1) == approx(math.pi / 2)

        a1 *= 2
        assert float(a1) == approx(math.pi)

        a1 /= 2
        assert float(a1) == approx(math.pi / 2)

        assert math.pi / a1 == approx(2)

        assert (math.pi + a1).asunit("deg") == approx(270)
        assert (math.pi - a1).asunit("deg") == approx(90)

        assert float(a1 // 1) == approx(1)
        assert 1 // a1 == approx(0)
        a2 //= 1
        assert float(a2) == approx(1)

        assert a1 == Angle(100, 'gon')
        assert a1 != "a"

        assert a1 < a3
        assert a1 <= a3
        assert a3 > a1
        assert a3 >= a1

        assert a1 == +a1
        assert a1 != -a1

        with pytest.raises(TypeError):
            a1 + "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            "a" + a1  # type: ignore[operator]

        with pytest.raises(TypeError):
            a1 - "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            "a" - a1  # type: ignore[operator]

        with pytest.raises(TypeError):
            a1 * "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            "a" * a1  # type: ignore[operator]

        with pytest.raises(TypeError):
            a1 / "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            "a" / a1  # type: ignore[operator]

        with pytest.raises(TypeError):
            a1 // "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            "a" // a1  # type: ignore[operator]

        with pytest.raises(TypeError):
            a1 > "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            a1 >= "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            a1 < "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            a1 <= "a"  # type: ignore[operator]

    def test_dms(self) -> None:
        a1 = Angle.from_dms("-180-00-00.5")
        assert a1.asunit('deg') == approx(-180)
        assert a1.to_dms() == "-180-00-00"
        assert a1.to_dms(1) == "-180-00-00.5"

        a2 = Angle.from_dms("180-00-00")
        assert a2.asunit('deg') == approx(180)

        with pytest.raises(ValueError):
            Angle.from_dms("A")


class TestByte:
    def test_init(self) -> None:
        with pytest.raises(ValueError):
            Byte(-1)

        with pytest.raises(ValueError):
            Byte(256)

    def test_str(self) -> None:
        value = Byte(12)
        assert int(value) == 12
        assert str(value) == "'0C'"
        assert repr(value) == str(value)

    def test_parse(self) -> None:
        assert int(Byte.parse("0C")) == 12
        assert int(Byte.parse("'0C'")) == 12


class TestVector:
    def test_init(self) -> None:
        value = Vector(1, 2, 3)
        assert value.x == 1
        assert value.y == 2
        assert value.z == 3

    def test_arithmetic(self) -> None:
        v1 = Vector(1, 1, 1)
        v2 = Vector(1, 2, 3)

        assert v1 + v2 == Vector(2, 3, 4)
        assert v1 + 1 == Vector(2, 2, 2)
        assert v1 - v2 == Vector(0, -1, -2)
        assert v1 - 1 == Vector(0, 0, 0)
        assert isinstance(+v1, Vector)

        assert v1 is not +v1
        assert v1 != "a"
        assert v1 is not +v1
        assert v1 is not -v1

        v4 = Vector(2, 2, 2)

        assert (v1 * 2) == (2 * v1) == v4
        assert (v4 / 2) == v1

        assert v1 * v2 == v2
        assert v2 / v1 == v2

        v2 *= v1
        assert v2 == Vector(1, 2, 3)

        v2 /= v1
        assert v2 == Vector(1, 2, 3)

        v1 += 1
        assert v1 == v4

        v1 -= 1
        assert v1 == Vector(1, 1, 1)

        with pytest.raises(TypeError):
            v1 + "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            v1 - "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            v1 * "a"  # type: ignore[operator]

        with pytest.raises(TypeError):
            v1 / "a"  # type: ignore[operator]

        v5 = Vector(1, 1, 1)
        assert v5.length() == approx(math.sqrt(3))
        assert v5.normalized().length() == approx(1)
        assert Vector(0, 0, 0).normalized().length() == approx(0)

        with pytest.raises(TypeError):
            v1.dot(2)  # type: ignore[arg-type]

        assert Vector(1, 1, 0).cross(Vector(-1, -1, 0)) == Vector(0, 0, 0)
        assert Vector(1, 1, 0).dot(Vector(1, 1, 0)) == 2

        with pytest.raises(TypeError):
            v1.cross(2)  # type: ignore[arg-type]

    def test_properties(self) -> None:
        v1 = Vector(1, 2, 3)
        x, y, z = v1
        assert v1.x == v1[0]
        assert v1.x == x

        with pytest.raises(ValueError):
            v1[3]

    def test_swizzle(self) -> None:
        v1 = Vector(1, 2, 3)
        assert v1.swizzle('z', 'y', 'x') == Vector(3, 2, 1)
        assert v1.swizzle('x', 'x', '0') == Vector(1, 1, 0)

        with pytest.raises(ValueError):
            v1.swizzle('x', 'y', 'a')  # type: ignore[arg-type]

    def test_printing(self) -> None:
        v1 = Vector(1, 2, 3)
        assert str(v1) == repr(v1)


class TestCoordinate:
    def test_properties(self) -> None:
        c1 = Coordinate(1, 2, 3)

        c1.e = 4
        c1.n = 5
        c1.h = 6

        assert c1.x == c1.e == c1[0] == 4
        assert c1.y == c1.n == c1[1] == 5
        assert c1.z == c1.h == c1[2] == 6

    def test_polar(self) -> None:
        c1 = Coordinate(-1, -1, -1)
        p1 = c1.to_polar()

        assert float(p1[0]) == approx(math.radians(225))
        assert float(p1[1]) == approx(math.radians(125.2643897))
        assert p1[2] == approx(math.sqrt(3))

        c2 = Coordinate.from_polar(*p1)

        assert c1.x == approx(c2.x)
        assert c1.y == approx(c2.y)
        assert c1.z == approx(c2.z)

    def test_utility(self) -> None:
        c1 = Coordinate(1, 2, 3)
        assert c1.to_2d() == Coordinate(1, 2, 0)
