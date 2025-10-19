# Reentrant random function from POSIX.1c.
# Copyright (C) 1996-2025 Free Software Foundation, Inc.
# This file is a derivative work from the GNU C Library.
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
# This is a derivative from the GNU C Library:
# - stdlib/rand_r.c
# It was rewritten for Python by Jayson Fong, 2025.
#
# The overall file is licensed under the GNU Lesser General Public version 2.1,
# or (at your option), any later version. Contributions by Jayson Fong explicitly
# noted may be licensed under the MIT License, at your choosing.

from dataclasses import dataclass
from typing import Tuple, Generator, Union, overload


def _rand_r(seed: int) -> Tuple[int, int]:
    next_val: int = seed & 0xFFFFFFFF

    next_val = (next_val * 1103515245 + 12345) & 0xFFFFFFFF
    result: int = (next_val >> 16) % 2048

    next_val = (next_val * 1103515245 + 12345) & 0xFFFFFFFF
    result = ((result << 10) ^ ((next_val >> 16) % 1024)) & 0xFFFFFFFF

    next_val = (next_val * 1103515245 + 12345) & 0xFFFFFFFF
    result = ((result << 10) ^ ((next_val >> 16) % 1024)) & 0xFFFFFFFF

    return result, next_val


@dataclass(slots=True)
class Seed:
    value: int


@overload
def rand_r(seed: Seed) -> int: ...


@overload
def rand_r(seed: int) -> Tuple[int, int]: ...


def rand_r(seed: Union[int, Seed]) -> Union[int, Tuple[int, int]]:
    if isinstance(seed, Seed):
        result, next_seed = _rand_r(seed.value)
        seed.value = next_seed

        return result

    return _rand_r(seed)


# The source below is an original contribution by Jayson Fong, 2025.
# It may be redistributed independently under the MIT License.


class GlibcReentrantRandom:

    __slots__: Tuple[str, ...] = ("seed",)

    def __init__(self, seed: Union[int, Seed]) -> None:
        if isinstance(seed, Seed):
            self.seed: int = seed.value
        else:
            self.seed: int = seed

    def generate(self) -> int:
        result, next_seed = _rand_r(self.seed)
        self.seed = next_seed

        return result

    def __iter__(self) -> Generator[int, None, None]:
        while True:
            yield self.generate()


__all__: Tuple[str, ...] = ("rand_r", "Seed", "GlibcReentrantRandom", "Seed")
