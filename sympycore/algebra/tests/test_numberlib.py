from sympycore.algebra.numberlib import *

def test_mpq():
    assert mpq(1) == 1
    assert mpq(1,1) == 1
    assert mpq(1,2) != 1
    assert mpq(1,2) == mpq(2,4)
    assert mpq(1,2) + mpq(5,6) == mpq(4,3)
    assert 2*mpq(1,2) == 1
    assert mpq(1,2)*2 == 1
    assert mpq(1,3) + mpq(2,3) == 1
    assert float(mpq(1,4)) == 0.25
    assert mpq(1,2) == mpq(-1,-2)
    assert mpq(-1,2) == mpq(1,-2)
    assert -mpq(2,3) == mpq(-2,3)
    assert +mpq(2,3) == mpq(2,3)
    assert mpq(1,2) - 1 == mpq(-1,2)
    assert 1 - mpq(1,2) == mpq(1,2)
    assert mpq(2,3)**0 == 1
    assert mpq(2,3)**1 == mpq(2,3)
    assert mpq(2,3)**2 == mpq(4,9)
    assert div(1,2) == mpq(1,2)
    assert div(3,mpq(1,2)) == 6
    assert div(mpq(1,2),mpq(3,2)) == mpq(1,3)
    assert mpq(1234,15) < 83
    assert mpq(1234,15) > 82
    assert mpq(2,3) < mpq(3, 4)

def test_mpf():
    assert mpf(2) != 3
    assert mpf(2) == 2
    assert mpf(1.1) == mpf('1.1')
    assert mpf(3) * mpf(4) == 12
    assert mpf(3) + mpf(4) == mpf(7)
    assert mpf(3) - mpf(4) == -1
    assert 4*mpf(3) == 12
    assert mpf(3)*4 == 12
    assert 2+mpf(5) == 7
    assert 0.5 + mpf(1) == 1.5
    assert mpf(1) + 0.5 == 1.5
    assert hash(mpf(3)) == hash(3)
    assert hash(mpf(1.5)) == hash(1.5)
    assert mpf(3) < mpf(4)
    assert mpf(3) > mpf(2)
    assert mpf(3) < 4
