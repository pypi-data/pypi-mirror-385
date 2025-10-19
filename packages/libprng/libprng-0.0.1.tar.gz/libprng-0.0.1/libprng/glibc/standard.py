# Copyright (C) 1995-2025 Free Software Foundation, Inc.
#
# The GNU C Library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# The GNU C Library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with the GNU C Library; if not, see
# <https://www.gnu.org/licenses/>.
#
#
# Copyright (C) 1983 Regents of the University of California.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 4. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# This is a derivative from the GNU C Library:
# - stdlib/rand.c
# - stdlib/random.c
# - stdlib/random_r.c
# It was rewritten for Python by Jayson Fong, 2025.
#
# The overall file is licensed under the GNU Lesser General Public version 2.1,
# or (at your option), any later version. Contributions by Jayson Fong explicitly
# noted may be licensed under the MIT License, at your choosing.

from array import array
from dataclasses import dataclass
from typing import Optional, Tuple, Generator


@dataclass(slots=True, frozen=True)
class RandomType:
    typ: int
    brk: int
    deg: int
    sep: int


RANDOM_TYPES: Tuple[RandomType, ...] = (
    RandomType(0, 8, 0, 0),
    RandomType(1, 32, 7, 3),
    RandomType(2, 64, 15, 1),
    RandomType(3, 128, 31, 3),
    RandomType(4, 256, 63, 1),
)


@dataclass(slots=True)
class RandomData:
    state: Optional[array] = None
    rand_type: int = 0
    rand_deg: int = 0
    rand_sep: int = 0
    f_index: int = 0
    r_index: int = 0


RANDOM_DATA: RandomData = RandomData()


def _lcg(seed: int) -> int:
    seed: int = 16807 * (seed % 127773) - 2836 * (seed // 127773)
    return seed + 2147483647 if seed < 0 else seed


def random_r(buf: RandomData) -> int:
    """
    Returns a 31-bit random integer.

    :param buf: `RandomData` instance.
    :return: 31-bit random integer.
    """

    if buf.state is None:
        raise ValueError("Random data state is not initialized")

    val: int
    state: array = buf.state
    if buf.rand_type == 0:
        val = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
        state[0] = val

        return val

    val = (state[buf.f_index] + state[buf.r_index]) & 0xFFFFFFFF
    state[buf.f_index] = val
    result: int = val >> 1

    buf.f_index = (buf.f_index + 1) % buf.rand_deg
    buf.r_index = (buf.r_index + 1) % buf.rand_deg

    return result


# noinspection SpellCheckingInspection
def srandom_r(seed: int, buf: RandomData) -> None:
    """
    Initializes the PRNG with the given seed.

    :param seed: 32-bit integer seed.
    :param buf: Random data object to update.
    :return: None.
    """

    if buf.rand_type >= len(RANDOM_TYPES):
        raise ValueError("Invalid state buffer")

    seed = max(seed, 1)

    deg = buf.rand_deg
    state = array("I", [0] * max(deg, 1))
    state[0] = seed

    if buf.rand_type == 0:
        buf.state = state
        return

    # Fill with LCG
    word = seed
    for i in range(1, deg):
        word = _lcg(word)
        state[i] = word

    buf.state = state
    buf.f_index = buf.rand_sep
    buf.r_index = 0

    # Warm up
    for _ in range(deg * 10):
        random_r(buf)


# noinspection SpellCheckingInspection
def initstate_r(seed: int, nbytes: int, buf: RandomData):
    """
    Initialize the internal state based on the array size.

    :param seed: 32-bit integer seed.
    :param nbytes: Array size to use.
    :param buf: Random data object to update.
    :return: None.
    """

    # Choose a type based on the number of bytes
    for t in reversed(RANDOM_TYPES):
        if nbytes >= t.brk:
            buf.rand_type = t.typ
            buf.rand_deg = t.deg
            buf.rand_sep = t.sep
            break
    else:
        raise ValueError("Not enough bytes")

    srandom_r(seed, buf)


def setstate_r(new_state: array, buf: RandomData) -> None:
    """
    Sets the state of the random data.

    :param new_state: State to set - an array of 32-bit integers.
    :param buf: Random data object to update.
    :return: None.
    """

    buf.state = new_state
    buf.rand_deg = len(new_state)
    buf.f_index = buf.rand_sep if buf.rand_deg > 0 else 0
    buf.r_index = 0


initstate_r(seed=1, nbytes=128, buf=RANDOM_DATA)


def rand() -> int:
    """
    Returns a 31-bit random integer.

    :return: 31-bit random integer.
    """

    return random_r(RANDOM_DATA)


def srand(seed: int) -> None:
    """
    Initializes the PRNG with the given seed.

    :param seed: 32-bit integer seed.
    :return: None.
    """

    initstate_r(seed, nbytes=128, buf=RANDOM_DATA)


# The source below is an original contribution by Jayson Fong, 2025.
# It may be redistributed independently under the MIT License.


class GlibcRandom:

    __slots__: Tuple[str, ...] = ("random_data",)

    # noinspection SpellCheckingInspection
    def __init__(self, seed: int = 1, nbytes: int = 128) -> None:
        self.random_data: RandomData = RandomData()
        initstate_r(seed, nbytes, self.random_data)

    def generate(self) -> int:
        return random_r(self.random_data)

    def __iter__(self) -> Generator[int, None, None]:
        while True:
            yield self.generate()


# noinspection SpellCheckingInspection
__all__: Tuple[str, ...] = (
    "GlibcRandom",
    "random_r",
    "initstate_r",
    "setstate_r",
    "rand",
    "srand",
)
