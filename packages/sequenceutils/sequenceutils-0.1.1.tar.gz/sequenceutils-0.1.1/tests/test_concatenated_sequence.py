from sequenceutils import ConcatenatedSequence
import pytest
import sys


@pytest.mark.parametrize("sequences", [
    [],
    [[]],
    [()],
    [[], []],
    [(), []],
    [(), ()],
    [[], [], []],
])
def test_empty_sequences(sequences):
    cs = ConcatenatedSequence(sequences)
    assert len(cs) == 0
    with pytest.raises(IndexError):
        cs[0]
    with pytest.raises(IndexError):
        cs[1]
    with pytest.raises(IndexError):
        cs[-1]
    assert list(cs) == []


@pytest.mark.parametrize("length, split_sequence", [
    (1, False),
    (1, True),
    (2, False),
    (2, True),
    (3, False),
    (3, True),
])
def test_single_element_sequences(length, split_sequence):
    elements = [object() for _ in range(length)]
    if split_sequence:
        cs = ConcatenatedSequence([[e] for e in elements])
    else:
        cs = ConcatenatedSequence([elements])
    assert len(cs) == length
    assert list(cs) == elements
    with pytest.raises(IndexError):
        cs[length]
    for i in range(length):
        assert len(cs) == length
        assert cs[i] is elements[i]
        assert cs[-1 - i] is elements[-1 - i]
        assert list(cs[i:]) == elements[i:]
        assert list(cs[:-i]) == elements[:-i]


def test_huge_sequence():
    cs = ConcatenatedSequence([range(1, 10**15 + 1), range(1, 10**15 + 1)])
    assert len(cs) == 2 * 10**15
    assert cs[0] == 1
    assert cs[1] == 2
    assert cs[::-1][-1] == 1
    assert cs[-1] == 10**15
    assert cs[10**15] == 1
    assert cs[10**15 + 1] == 2
    assert cs[::10][10**14] == 1


def test_humongous_sequence():
    cs = ConcatenatedSequence([range(i, sys.maxsize + i) for i in range(3)])
    expected_length = sys.maxsize * 3
    assert cs.__len__() == expected_length
    assert cs[0] == 0
    assert cs[1] == 1
    assert cs[::-1][-1] == 0
    assert cs[-1] == (sys.maxsize - 1) + 2
