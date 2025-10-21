# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
"""
Test utility functions from :module:`datacube.utils`
"""

import os
from collections import OrderedDict
from collections.abc import Iterable
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import boto3
import moto
import numpy as np
import pytest
import toolz

from datacube.model import MetadataType
from datacube.model.utils import (
    dedup_lineage,
    flatten_datasets,
    remap_lineage_doc,
    traverse_datasets,
)
from datacube.testutils import (
    dataset_maker,
    gen_dataset_test_dag,
    make_graph_abcde,
    mk_sample_product,
)
from datacube.utils import InvalidDocException, SimpleDocNav, read_documents
from datacube.utils.changes import (
    MISSING,
    DocumentMismatchError,
    check_doc_unchanged,
    get_doc_changes,
)
from datacube.utils.documents import (
    DocReader,
    _open_from_s3,
    get_doc_offset,
    is_supported_document_type,
    metadata_subset,
    netcdf_extract_string,
    parse_yaml,
    transform_object_tree,
    without_lineage_sources,
)
from datacube.utils.serialise import jsonify_document
from datacube.utils.uris import as_url

doc_changes = [
    (1, 1, []),
    ({}, {}, []),
    ({"a": 1}, {"a": 1}, []),
    ({"a": {"b": 1}}, {"a": {"b": 1}}, []),
    ([1, 2, 3], [1, 2, 3], []),
    ([1, 2, [3, 4, 5]], [1, 2, [3, 4, 5]], []),
    (1, 2, [((), 1, 2)]),
    ([1, 2, 3], [2, 1, 3], [((0,), 1, 2), ((1,), 2, 1)]),
    ([1, 2, [3, 4, 5]], [1, 2, [3, 6, 7]], [((2, 1), 4, 6), ((2, 2), 5, 7)]),
    ({"a": 1}, {"a": 2}, [(("a",), 1, 2)]),
    ({"a": 1}, {"a": 2}, [(("a",), 1, 2)]),
    ({"a": 1}, {"b": 1}, [(("a",), 1, MISSING), (("b",), MISSING, 1)]),
    ({"a": {"b": 1}}, {"a": {"b": 2}}, [(("a", "b"), 1, 2)]),
    ({}, {"b": 1}, [(("b",), MISSING, 1)]),
    (
        {"a": {"c": 1}},
        {"a": {"b": 1}},
        [(("a", "b"), MISSING, 1), (("a", "c"), 1, MISSING)],
    ),
    # Test tuple vs list, for geometry coordinates handling and expect no changes
    (
        [[635235.0, -2930535.0], [635235.0, -2930535.0]],
        (
            (635235.0, -2930535.0),
            (635235.0, -2930535.0),
        ),
        [],
    ),
    (
        [[[635235.0, -2930535.0], [635235.0, -2930535.0]]],
        (((635235.0, -2930535.0), (635235.0, -2930535.0)),),
        [],
    ),
    (
        {"coordinates": [[[635235.0, -2930535.0], [635235.0, -2930535.0]]]},
        {"coordinates": (((635235.0, -2930535.0), (635235.0, -2930535.0)),)},
        [],
    ),
]


@pytest.mark.parametrize("v1, v2, expected", doc_changes)
def test_get_doc_changes(v1, v2, expected) -> None:
    rval = get_doc_changes(v1, v2)
    assert rval == expected


def test_get_doc_changes_w_baseprefix() -> None:
    rval = get_doc_changes({}, None, base_prefix=("a",))
    assert rval == [(("a",), {}, None)]


@pytest.mark.parametrize("v1, v2, expected", doc_changes)
def test_check_doc_unchanged(v1, v2, expected) -> None:
    if expected != []:
        with pytest.raises(DocumentMismatchError):
            check_doc_unchanged(v1, v2, "name")
    else:
        # No Error Raised
        check_doc_unchanged(v1, v2, "name")


def test_more_check_doc_unchanged() -> None:
    # No exception raised
    check_doc_unchanged({"a": 1}, {"a": 1}, "Letters")

    with pytest.raises(
        DocumentMismatchError, match=r"^Letters differs from stored.*a: 1!=2"
    ):
        check_doc_unchanged({"a": 1}, {"a": 2}, "Letters")

    with pytest.raises(
        DocumentMismatchError, match=r"^Letters differs from stored.*a.b: 1!=2"
    ):
        check_doc_unchanged({"a": {"b": 1}}, {"a": {"b": 2}}, "Letters")


def test_without_lineage_sources() -> None:
    def mk_sample(v):
        return {
            "lineage": {"source_datasets": v, "a": "a", "b": "b"},
            "aa": "aa",
            "bb": {"bb": "bb"},
        }

    spec = mk_sample_product("tt")

    x = {"a": 1}
    assert without_lineage_sources(x, spec) == x

    x = {"a": 1, "lineage": {}}
    assert without_lineage_sources(x, spec) == x

    x = mk_sample(1)
    assert without_lineage_sources(x, spec) != x
    assert x["lineage"]["source_datasets"] == 1

    assert mk_sample(10) != mk_sample({})
    assert without_lineage_sources(mk_sample(10), spec) == mk_sample({})

    # check behaviour when `sources` is defined for the type but lineage has not been remapped
    test_doc = {"lineage": {"a": ["a"], "b": ["b"]}, "aa": "aa", "bb": {"bb": "bb"}}
    assert without_lineage_sources(test_doc, spec) == {
        "lineage": {},
        "aa": "aa",
        "bb": {"bb": "bb"},
    }

    # check behaviour when `sources` is not defined for the type
    no_sources_type = MetadataType(
        {
            "name": "eo",
            "description": "Sample",
            "dataset": {
                "id": ["id"],
                "label": ["ga_label"],
                "creation_time": ["creation_dt"],
                "measurements": ["image", "bands"],
                "format": ["format", "name"],
            },
        },
    )

    test_doc = mk_sample(10)
    assert without_lineage_sources(test_doc, no_sources_type)["lineage"] == {}
    test_doc["lineage"] = {"a": "a", "b": "b"}
    assert without_lineage_sources(test_doc, no_sources_type)["lineage"] == {}


def test_parse_yaml() -> None:
    assert parse_yaml("a: 10") == {"a": 10}


def test_read_docs_from_local_path(sample_document_files) -> None:
    _test_read_docs_impl(sample_document_files)


def test_read_docs_from_file_uris(sample_document_files) -> None:
    uris = [("file://" + doc, ndocs) for doc, ndocs in sample_document_files]
    _test_read_docs_impl(uris)


def test_read_docs_from_s3(sample_document_files, monkeypatch) -> None:
    """
    Use a mocked S3 bucket to test reading documents from S3
    """
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "fake")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "fake")

    with moto.mock_aws():
        s3 = boto3.resource("s3", region_name="us-east-1")
        bucket = s3.create_bucket(Bucket="mybucket")

        mocked_s3_objs = []
        for abs_fname, ndocs in sample_document_files:
            if abs_fname.endswith("gz") or abs_fname.endswith("nc"):
                continue

            fname = Path(abs_fname).name
            bucket.upload_file(abs_fname, fname)

            mocked_s3_objs.append(("s3://mybucket/" + fname, ndocs))

        _test_read_docs_impl(mocked_s3_objs)

    with pytest.raises(RuntimeError):  # noqa: SIM117
        with _open_from_s3("https://not-s3.ga/file.txt"):
            pass


def test_read_docs_from_http(sample_document_files, httpserver) -> None:
    http_docs = []
    for abs_fname, ndocs in sample_document_files:
        if abs_fname.endswith("gz") or abs_fname.endswith("nc"):
            continue
        path = "/" + Path(abs_fname).name

        httpserver.expect_request(path).respond_with_data(open(abs_fname).read())
        http_docs.append((httpserver.url_for(path), ndocs))

    _test_read_docs_impl(http_docs)


def _test_read_docs_impl(sample_documents: Iterable[tuple[str, int]]) -> None:
    # Test case for returning URIs pointing to documents
    for doc_url, num_docs in sample_documents:
        all_docs = list(read_documents(doc_url, uri=True))
        assert len(all_docs) == num_docs

        for uri, doc in all_docs:
            assert isinstance(doc, dict)
            assert isinstance(uri, str)

        url = as_url(doc_url)
        expect_uris = (
            [url + f"#part={i}" for i in range(num_docs)] if num_docs > 1 else [url]
        )

        assert [f for f, _ in all_docs] == expect_uris


def test_dataset_maker() -> None:
    mk = dataset_maker(0)
    assert mk("aa") == mk("aa")

    a = SimpleDocNav(mk("A"))
    b = SimpleDocNav(mk("B"))

    assert a.id != b.id
    assert a.doc["creation_dt"] == b.doc["creation_dt"]
    assert isinstance(a.id, UUID)
    assert a.sources == {}

    a1, a2 = [dataset_maker(i)("A", product_type="eo") for i in (0, 1)]
    assert a1["id"] != a2["id"]
    assert a1["creation_dt"] != a2["creation_dt"]
    assert a1["product_type"] == "eo"

    c = SimpleDocNav(mk("C", sources={"a": a.doc, "b": b.doc}))
    assert c.sources["a"].doc is a.doc
    assert c.sources["b"].doc is b.doc


def test_traverse_datasets() -> None:
    """
    A -> B
    |    |
    |    v
    +--> C -> D
    |
    +--> E
    """

    def node(name: str, **kwargs):
        return SimpleNamespace(id=name, sources=kwargs)

    A, *_ = make_graph_abcde(node)

    def visitor(node, name: str | None = None, depth: int = 0, out=None) -> None:
        s = "{}:{}:{:d}".format(node.id, name if name else "..", depth)
        out.append(s)

    # Test that type errors raise exceptions.
    with pytest.raises(ValueError):
        traverse_datasets(A, visitor, mode="not-a-real-mode")  # type: ignore[arg-type]

    expect_preorder = """
A:..:0
B:ab:1
C:bc:2
D:cd:3
C:ac:1
D:cd:2
E:ae:1
""".lstrip().rstrip()

    expect_postorder = """
D:cd:3
C:bc:2
B:ab:1
D:cd:2
C:ac:1
E:ae:1
A:..:0
""".lstrip().rstrip()

    for mode, expect in zip(
        ["pre-order", "post-order"], [expect_preorder, expect_postorder]
    ):
        out: list[str] = []
        traverse_datasets(A, visitor, mode=mode, out=out)  # type: ignore[arg-type]
        assert "\n".join(out) == expect

    fv = flatten_datasets(A)
    assert isinstance(fv, dict)
    assert len(fv["A"]) == 1
    assert len(fv["C"]) == 2
    assert len(fv["E"]) == 1
    assert set(fv.keys()) == set("ABCDE")

    leaf = SimpleNamespace(id="N", sources=None)
    out = []
    # FIX;E: Dataset | SimpleDocNav expected.
    traverse_datasets(leaf, visitor, out=out)  # type: ignore[arg-type]
    assert out == ["N:..:0"]


def test_simple_doc_nav() -> None:
    """
    A -> B
    |    |
    |    v
    +--> C -> D
    |
    +--> E
    """
    nu_map = {n: uuid4() for n in ["A", "B", "C", "D", "E"]}
    un_map = {u: n for n, u in nu_map.items()}

    def node(name: str, **kwargs):
        return {"id": nu_map[name], "lineage": {"source_datasets": kwargs}}

    A, _, C, _, _ = make_graph_abcde(node)  # noqa: N806
    rdr = SimpleDocNav(A)

    assert rdr.doc == A
    assert rdr.doc_without_lineage_sources == node("A")
    assert isinstance(rdr.sources["ae"], SimpleDocNav)
    assert rdr.sources["ab"].sources["bc"].doc == C
    assert rdr.doc_without_lineage_sources is rdr.doc_without_lineage_sources
    assert rdr.sources is rdr.sources
    assert isinstance(rdr.sources_path, tuple)

    def visitor(node, name: str | None = None, depth: int = 0, out=None) -> None:
        s = "{}:{}:{:d}".format(un_map[node.id], name if name else "..", depth)
        out.append(s)

    expect_preorder = """
A:..:0
B:ab:1
C:bc:2
D:cd:3
C:ac:1
D:cd:2
E:ae:1
""".lstrip().rstrip()

    expect_postorder = """
D:cd:3
C:bc:2
B:ab:1
D:cd:2
C:ac:1
E:ae:1
A:..:0
""".lstrip().rstrip()

    for mode, expect in zip(
        ["pre-order", "post-order"], [expect_preorder, expect_postorder]
    ):
        out: list = []
        traverse_datasets(rdr, visitor, mode=mode, out=out)  #  type: ignore[arg-type]
        assert "\n".join(out) == expect

    fv = flatten_datasets(rdr)
    assert isinstance(fv, dict)
    assert len(fv[nu_map["A"]]) == 1
    assert len(fv[nu_map["C"]]) == 2
    assert len(fv[nu_map["E"]]) == 1
    assert set(fv.keys()) == set(un_map.keys())

    fv, dg = flatten_datasets(rdr, with_depth_grouping=True)
    assert isinstance(fv, dict)
    assert len(fv[nu_map["A"]]) == 1
    assert len(fv[nu_map["C"]]) == 2
    assert len(fv[nu_map["E"]]) == 1
    assert set(fv.keys()) == set(un_map.keys())
    assert isinstance(dg, list)
    assert len(dg) == 4
    assert [len(dss) for dss in dg] == [1, 3, 2, 1]

    def to_set(xx):
        return {x.id for x in xx}

    assert [{nu_map[n] for n in s} for s in ("A", "BCE", "CD", "D")] == [
        to_set(xx) for xx in dg
    ]

    # Test that type errors result in exceptions.
    with pytest.raises(ValueError):
        SimpleDocNav([])  # type: ignore[arg-type]


def test_dedup() -> None:
    ds0 = SimpleDocNav(gen_dataset_test_dag(1, force_tree=True))

    # make sure ds0 has duplicate C nodes with equivalent data
    assert ds0.sources["ab"].sources["bc"].doc is not ds0.sources["ac"].doc
    assert ds0.sources["ab"].sources["bc"].doc == ds0.sources["ac"].doc

    ds = SimpleDocNav(dedup_lineage(ds0))
    assert ds.sources["ab"].sources["bc"].doc is ds.sources["ac"].doc
    assert (
        ds.sources["ab"].sources["bc"].sources["cd"].doc
        is ds.sources["ac"].sources["cd"].doc
    )

    # again but with raw doc
    ds = SimpleDocNav(dedup_lineage(ds0.doc))
    assert ds.sources["ab"].sources["bc"].doc is ds.sources["ac"].doc
    assert (
        ds.sources["ab"].sources["bc"].sources["cd"].doc
        is ds.sources["ac"].sources["cd"].doc
    )

    # Test that we detect inconsistent metadata for duplicate entries (test 1)
    # test: different values in the same spot
    ds0 = SimpleDocNav(gen_dataset_test_dag(3, force_tree=True))
    ds0.sources["ac"].doc["label"] = "Modified"
    ds0 = SimpleDocNav(ds0.doc)
    assert ds0.sources["ab"].sources["bc"].doc != ds0.sources["ac"].doc

    with pytest.raises(InvalidDocException, match=r"Inconsistent metadata .*"):
        dedup_lineage(ds0)

    # Test that we detect inconsistent metadata for duplicate entries (test 2)
    # test: different sources structure
    ds0 = SimpleDocNav(gen_dataset_test_dag(3, force_tree=True))
    ds0.sources["ac"].doc["lineage"]["source_datasets"]["extra"] = ds0.sources[
        "ae"
    ].doc.copy()
    assert ds0.sources["ab"].sources["bc"].doc != ds0.sources["ac"].doc

    ds0 = SimpleDocNav(ds0.doc)

    with pytest.raises(InvalidDocException, match=r"Inconsistent lineage .*"):
        dedup_lineage(ds0)

    # Test that we detect inconsistent lineage subtrees for duplicate entries

    # Subtest 1: different set of keys
    ds0 = SimpleDocNav(gen_dataset_test_dag(7, force_tree=True))
    srcs = toolz.get_in(ds0.sources_path, ds0.sources["ac"].doc)

    assert "cd" in srcs
    srcs["cd"] = {}
    ds0 = SimpleDocNav(ds0.doc)

    with pytest.raises(InvalidDocException, match=r"Inconsistent lineage .*"):
        dedup_lineage(ds0)

    # Subtest 2: different values for "child" nodes
    ds0 = SimpleDocNav(gen_dataset_test_dag(7, force_tree=True))
    srcs = toolz.get_in(ds0.sources_path, ds0.sources["ac"].doc)

    assert "cd" in srcs
    srcs["cd"]["id"] = "7fe57724-ed44-4beb-a3ab-c275339049be"
    ds0 = SimpleDocNav(ds0.doc)

    with pytest.raises(InvalidDocException, match=r"Inconsistent lineage .*"):
        dedup_lineage(ds0)

    # Subtest 3: different name for child
    ds0 = SimpleDocNav(gen_dataset_test_dag(7, force_tree=True))
    srcs = toolz.get_in(ds0.sources_path, ds0.sources["ac"].doc)

    assert "cd" in srcs
    srcs["CD"] = srcs["cd"]
    del srcs["cd"]
    ds0 = SimpleDocNav(ds0.doc)

    with pytest.raises(InvalidDocException, match=r"Inconsistent lineage .*"):
        dedup_lineage(ds0)


def test_remap_lineage_doc() -> None:
    def mk_node(ds, sources):
        return dict(id=ds.id, **sources)

    ds = SimpleDocNav(gen_dataset_test_dag(3, force_tree=True))
    xx = remap_lineage_doc(ds, mk_node)
    assert xx["id"] == ds.id
    assert xx["ac"]["id"] == ds.sources["ac"].id

    xx = remap_lineage_doc(ds.doc, mk_node)
    assert xx["id"] == ds.id
    assert xx["ac"]["id"] == ds.sources["ac"].id


def test_merge() -> None:
    from datacube.model.utils import merge

    assert merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}
    assert merge({"a": 1, "b": 2}, {"b": 2}) == {"a": 1, "b": 2}

    with pytest.raises(ValueError):
        merge({"a": 1, "b": 2}, {"b": 3})


@pytest.mark.xfail(
    True, reason="Merging dictionaries with content of NaN doesn't work currently"
)
def test_merge_with_nan() -> None:
    from datacube.model.utils import merge

    _nan = float("nan")
    assert _nan != _nan
    xx = merge(
        {"a": _nan}, {"a": _nan}
    )  # <- fails here because of simple equality check
    assert xx["a"] != xx["a"]


@pytest.fixture
def sample_document_files(data_folder):
    files = [
        ("multi_doc.yml", 3),
        ("multi_doc.yml.gz", 3),
        ("multi_doc.nc", 3),
        ("single_doc.yaml", 1),
        ("sample.json", 1),
    ]

    return [(str(os.path.join(data_folder, f)), num_docs) for f, num_docs in files]


def test_jsonify() -> None:
    from datetime import datetime
    from decimal import Decimal
    from uuid import UUID

    assert sorted(
        jsonify_document(
            {
                "a": (1.0, 2.0, 3.0),
                "b": float("inf"),
                "c": datetime(2016, 3, 11),
                "d": np.dtype("int16"),
            }
        ).items()
    ) == [
        ("a", (1.0, 2.0, 3.0)),
        ("b", "Infinity"),
        ("c", "2016-03-11T00:00:00"),
        ("d", "int16"),
    ]

    # Converts keys to strings:
    assert sorted(jsonify_document({1: "a", "2": Decimal(2)}).items()) == [
        ("1", "a"),
        ("2", "2"),
    ]

    assert jsonify_document({"k": UUID("1f231570-e777-11e6-820f-185e0f80a5c0")}) == {
        "k": "1f231570-e777-11e6-820f-185e0f80a5c0"
    }


def test_netcdf_strings() -> None:
    assert netcdf_extract_string(np.asarray([b"a", b"b"])) == "ab"
    txt = "some string"
    assert netcdf_extract_string(txt) is txt


def test_doc_reader() -> None:
    # FIXME: Field expected in doc Mapping.
    d = DocReader({"lat": ["extent", "lat"]}, {}, doc={"extent": {"lat": 4}})  # type: ignore[dict-item]
    assert hasattr(d, "lat")
    assert d.lat == 4
    assert d.doc == {"extent": {"lat": 4}}

    d.lat = 5
    assert d.lat == 5
    assert d.doc == {"extent": {"lat": 5}}

    assert d.search_fields == {}

    assert not hasattr(d, "no_such")
    with pytest.raises(AttributeError):
        _ = d.no_such

    with pytest.raises(AttributeError):
        d.no_such = 0

    assert dir(d) == ["lat"]

    d = DocReader({"platform": ["platform", "code"]}, {}, doc={})
    assert d.platform is None


def test_is_supported_doc_type() -> None:
    assert is_supported_document_type(Path("/tmp/something.yaml"))
    assert is_supported_document_type(Path("/tmp/something.YML"))
    assert is_supported_document_type(Path("/tmp/something.yaml.gz"))
    assert not is_supported_document_type(Path("/tmp/something.tif"))
    assert not is_supported_document_type(Path("/tmp/something.tif.gz"))


def test_doc_offset() -> None:
    assert get_doc_offset(["a"], {"a": 4}) == 4
    assert get_doc_offset(["a", "b"], {"a": {"b": 4}}) == 4
    assert get_doc_offset(["a"], {}) is None
    assert get_doc_offset(["a", "b", "c"], {"a": {"b": {}}}, 10) == 10
    assert get_doc_offset(["a", "b", "c"], {"a": {"b": []}}, 11) == 11


def test_transform_object_tree() -> None:
    def add_one(a):
        return a + 1

    assert transform_object_tree(add_one, [1, 2, 3]) == [2, 3, 4]
    assert transform_object_tree(add_one, {"a": 1, "b": 2, "c": 3}) == {
        "a": 2,
        "b": 3,
        "c": 4,
    }
    assert transform_object_tree(add_one, {"a": 1, "b": (2, 3), "c": [4, 5]}) == {
        "a": 2,
        "b": (3, 4),
        "c": [5, 6],
    }
    assert transform_object_tree(
        add_one, {1: 1, "2": 2, 3.0: 3}, key_transform=float
    ) == {1.0: 2, 2.0: 3, 3.0: 4}
    # Order must be maintained
    assert transform_object_tree(
        add_one, OrderedDict([("z", 1), ("w", 2), ("y", 3), ("s", 7)])
    ) == OrderedDict([("z", 2), ("w", 3), ("y", 4), ("s", 8)])


def test_document_subset() -> None:
    # metadata_subset should emulate behaviour of postgres "contains" (@>) operator.
    assert metadata_subset(37, 37)
    assert metadata_subset(37, [1, 111, 37])
    assert metadata_subset(37, [1, 37, 444])
    assert not metadata_subset(37, {"b": 37})
    assert not metadata_subset(37, {"b": "foo", "a": {"d": 37}})
    assert not metadata_subset(37, {"b": [56, 36, 37]})
    assert not metadata_subset(37, {"b": [56, 36, 57]})

    assert metadata_subset(
        {"a": "foo"}, {"b": "blob", "a": "foo", "d": [76, 345, 34, 54]}
    )
    assert not metadata_subset(
        {"a": "foo"}, {"b": "blob", "d": [{"b": "glue", "a": "nope"}, {"a": "foo"}, 54]}
    )
    assert not metadata_subset(
        {"a": "foo"}, {"g": "goo", "h": {"f": "foo", "j": {"w": "who", "a": "foo"}}}
    )
    assert not metadata_subset(
        {"a": "foo", "k": {"b": [34, 11]}},
        {"g": "goo", "h": {"a": "foo", "k": {"b": [11, 234, 34, 35]}, "d": "doop"}},
    )
    assert metadata_subset(
        {"a": "foo", "k": {"b": [34, 11]}},
        {"a": "foo", "k": {"b": [11, 234, 34, 35]}, "d": "doop"},
    )
    assert not metadata_subset(
        {"a": "foo", "k": {"b": [34, 11]}},
        {
            "g": "goo",
            "h": {"a": "foo", "b": [11, 34], "k": {"b": [11, 234, 35]}, "d": "doop"},
        },
    )
    assert not metadata_subset(
        {"a": "foo", "k": {"b": [34, 11]}},
        {"a": "foo", "b": [11, 34], "k": {"b": [11, 234, 35]}, "d": "doop"},
    )

    assert metadata_subset([35, 47, 58], [0, 35, 47, 58, 102])
    assert not metadata_subset([35, 47, 58], {"a": "foo", "b": [35, 47, 52, 58]})


def test_document_subset_full_recursion() -> None:
    # metadata_subset should emulate behaviour of postgres "contains" (@>) operator.
    assert metadata_subset(37, 37, full_recursion=True)
    assert metadata_subset(37, [1, 111, 37], full_recursion=True)
    assert metadata_subset(37, [1, 37, 444], full_recursion=True)
    assert metadata_subset(37, {"b": 37}, full_recursion=True)
    assert metadata_subset(37, {"b": "foo", "a": {"d": 37}}, full_recursion=True)
    assert metadata_subset(37, {"b": [56, 36, 37]}, full_recursion=True)
    assert not metadata_subset(37, {"b": [56, 36, 57]}, full_recursion=True)

    assert metadata_subset(
        {"a": "foo"},
        {"b": "blob", "a": "foo", "d": [76, 345, 34, 54]},
        full_recursion=True,
    )
    assert metadata_subset(
        {"a": "foo"},
        {"b": "blob", "d": [{"b": "glue", "a": "nope"}, {"a": "foo"}, 54]},
        full_recursion=True,
    )
    assert metadata_subset(
        {"a": "foo"},
        {"g": "goo", "h": {"f": "foo", "j": {"w": "who", "a": "foo"}}},
        full_recursion=True,
    )
    assert metadata_subset(
        {"a": "foo", "k": {"b": [34, 11]}},
        {"g": "goo", "h": {"a": "foo", "k": {"b": [11, 234, 34, 35]}, "d": "doop"}},
        full_recursion=True,
    )
    assert metadata_subset(
        {"a": "foo", "k": {"b": [34, 11]}},
        {"a": "foo", "k": {"b": [11, 234, 34, 35]}, "d": "doop"},
        full_recursion=True,
    )
    assert not metadata_subset(
        {"a": "foo", "k": {"b": [34, 11]}},
        {
            "g": "goo",
            "h": {"a": "foo", "b": [11, 34], "k": {"b": [11, 234, 35]}, "d": "doop"},
        },
        full_recursion=True,
    )
    assert not metadata_subset(
        {"a": "foo", "k": {"b": [34, 11]}},
        {"a": "foo", "b": [11, 34], "k": {"b": [11, 234, 35]}, "d": "doop"},
        full_recursion=True,
    )

    assert metadata_subset([35, 47, 58], [0, 35, 47, 58, 102], full_recursion=True)
    assert metadata_subset(
        [35, 47, 58], {"a": "foo", "b": [35, 47, 52, 58]}, full_recursion=True
    )


def test_documents_equal() -> None:
    from datacube.utils.documents import documents_equal

    assert not documents_equal(7, "seven")
    assert not documents_equal(
        {"a": "ok", "b": "mediocre"}, {"c": "great", "b": "mediocre", "a": "ok"}
    )
    assert not documents_equal([0, 1, 2], [0, 1, 2, 3])
    assert not documents_equal([0, 1, 2], [0, 2, 1])
    assert not documents_equal(0.5, 0.50001)
    assert documents_equal(0.5, 0.50000000001)
