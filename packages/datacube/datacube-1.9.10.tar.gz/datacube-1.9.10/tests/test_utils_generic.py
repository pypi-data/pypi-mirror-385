# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
from queue import Queue

from datacube.utils.generic import (
    it2q,
    map_with_lookahead,
    qmap,
    thread_local_cache,
)


def test_map_with_lookahead() -> None:
    def if_one(x) -> str:
        return "one" + str(x)

    def if_many(x) -> str:
        return "many" + str(x)

    assert list(map_with_lookahead(iter([]), if_one, if_many)) == []
    assert list(map_with_lookahead(iter([1]), if_one, if_many)) == [if_one(1)]
    assert list(map_with_lookahead(range(5), if_one, if_many)) == list(
        map(if_many, range(5))
    )
    assert list(map_with_lookahead(range(10), if_one=if_one)) == list(range(10))
    assert list(map_with_lookahead(iter([1]), if_many=if_many)) == [1]


def test_qmap() -> None:
    q: Queue = Queue(maxsize=100)
    it2q((i for i in range(10)), q)
    rr = list(qmap(str, q))
    assert rr == [str(x) for x in range(10)]
    q.join()  # should not block


def test_thread_local_cache() -> None:
    name = "test_0123394"
    v: dict = {}

    assert thread_local_cache(name, v) is v
    assert thread_local_cache(name) is v
    assert thread_local_cache(name, purge=True) is v
    assert thread_local_cache(name, 33) == 33
    assert thread_local_cache(name, purge=True) == 33

    assert thread_local_cache("no_such_key", purge=True) is None
    assert thread_local_cache("no_such_key", 111, purge=True) == 111
