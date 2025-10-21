# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
import json
import os
from typing import Any
from unittest import mock

import boto3
import botocore
import moto
import pytest
from botocore.credentials import ReadOnlyCredentials

from datacube.testutils import write_files
from datacube.utils.aws import (
    _fetch_text,
    _s3_cache_key,
    auto_find_region,
    ec2_current_region,
    get_aws_settings,
    get_creds_with_retry,
    mk_boto_session,
    obtain_new_iam_auth_token,
    s3_client,
    s3_dump,
    s3_fetch,
    s3_fmt_range,
    s3_head_object,
    s3_url_parse,
)
from datacube.utils.aws.queue import get_queues, redrive_queue

ALIVE_QUEUE_NAME = "mock-alive-queue"
DEAD_QUEUE_NAME = "mock-dead-queue"


def _json(**kw):
    return json.dumps(kw)


def mock_urlopen(text: str, code: int = 200):
    m = mock.MagicMock()
    m.getcode.return_value = code
    m.read.return_value = text.encode("utf8")
    m.__enter__.return_value = m
    return m


def get_n_messages(queue) -> int:
    return int(queue.attributes.get("ApproximateNumberOfMessages"))


@pytest.fixture
def aws_env(monkeypatch) -> None:
    if "AWS_DEFAULT_REGION" not in os.environ:
        monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")


@moto.mock_aws
def test_redrive_to_queue(aws_env: None) -> None:
    resource = boto3.resource("sqs")

    dead_queue = resource.create_queue(QueueName=DEAD_QUEUE_NAME)
    alive_queue = resource.create_queue(
        QueueName=ALIVE_QUEUE_NAME,
        Attributes={
            "RedrivePolicy": json.dumps(
                {
                    "deadLetterTargetArn": dead_queue.attributes.get("QueueArn"),
                    "maxReceiveCount": 2,
                }
            ),
        },
    )

    # Test redriving to a queue without an alive queue specified
    dead_queue.send_message(MessageBody=json.dumps({"test": 1}))
    assert get_n_messages(dead_queue) == 1

    count = redrive_queue(DEAD_QUEUE_NAME, max_wait=0)
    assert count == 1

    # Test redriving to a queue that is specified
    dead_queue.send_message(MessageBody=json.dumps({"test": 2}))
    assert get_n_messages(dead_queue) == 1

    redrive_queue(DEAD_QUEUE_NAME, ALIVE_QUEUE_NAME, max_wait=0)
    assert get_n_messages(dead_queue) == 1
    assert get_n_messages(alive_queue) == 2

    # Test lots of messages:
    for i in range(35):
        dead_queue.send_message(MessageBody=json.dumps({"content": f"Something {i}"}))

    count = redrive_queue(DEAD_QUEUE_NAME, ALIVE_QUEUE_NAME, max_wait=0)
    assert count == 35

    assert get_n_messages(dead_queue) == 0


@moto.mock_aws
def test_get_queues(aws_env: None) -> None:
    resource = boto3.resource("sqs")

    resource.create_queue(QueueName="a_queue1")
    resource.create_queue(QueueName="b_queue2")
    resource.create_queue(QueueName="c_queue3")
    resource.create_queue(QueueName="d_queue4")

    queues = get_queues()

    assert len(list(queues)) == 4

    # Test prefix
    queues = get_queues(prefix="a_queue1")
    assert "queue1" in next(iter(queues)).url

    # Test prefix
    queues = get_queues(contains="2")
    assert "b_queue2" in next(iter(queues)).url

    # Test prefix and contains
    queues = get_queues(prefix="c", contains="3")
    assert "c_queue3" in next(iter(queues)).url

    # Test prefix and not contains
    queues = get_queues(prefix="d", contains="5")
    assert len(list(queues)) == 0

    # Test contains and not prefix
    queues = get_queues(prefix="q", contains="2")
    assert len(list(queues)) == 0

    # Test not found prefix
    queues = get_queues(prefix="fake_start")
    assert len(list(queues)) == 0

    # Test not found contains
    queues = get_queues(contains="not_there")
    assert len(list(queues)) == 0


@moto.mock_aws
def test_get_queues_empty(aws_env: None) -> None:
    queues = get_queues()
    assert list(queues) == []


def test_ec2_current_region() -> None:
    tests = [
        (None, None),
        (_json(region="TT"), "TT"),
        (_json(x=3), None),
        ("not valid json", None),
    ]

    for rv, expect in tests:
        with mock.patch("datacube.utils.aws._fetch_text", return_value=rv):
            assert ec2_current_region() == expect


@mock.patch("datacube.utils.aws.botocore_default_region", return_value=None)
def test_auto_find_region(*mocks) -> None:
    with mock.patch("datacube.utils.aws._fetch_text", return_value=None):  # noqa: SIM117
        with pytest.raises(ValueError):
            auto_find_region()

    with mock.patch("datacube.utils.aws._fetch_text", return_value=_json(region="TT")):
        assert auto_find_region() == "TT"


@mock.patch(
    "datacube.utils.aws.botocore_default_region", return_value="tt-from-botocore"
)
def test_auto_find_region_2(*mocks) -> None:
    assert auto_find_region() == "tt-from-botocore"


def test_fetch_text() -> None:
    with mock.patch("datacube.utils.aws.urlopen", return_value=mock_urlopen("", 505)):
        assert _fetch_text("http://localhost:8817") is None

    with mock.patch(
        "datacube.utils.aws.urlopen", return_value=mock_urlopen("text", 200)
    ):
        assert _fetch_text("http://localhost:8817") == "text"

    def fake_urlopen(*args, **kw):
        raise OSError("Always broken")

    with mock.patch("datacube.utils.aws.urlopen", fake_urlopen):
        assert _fetch_text("http://localhost:8817") is None


def test_get_aws_settings(monkeypatch, without_aws_env) -> None:
    pp = write_files(
        {
            "config": """
[default]
region = us-west-2

[profile east]
region = us-east-1
[profile no_region]
""",
            "credentials": """
[default]
aws_access_key_id = AKIAWYXYXYXYXYXYXYXY
aws_secret_access_key = fake-fake-fake
[east]
aws_access_key_id = AKIAEYXYXYXYXYXYXYXY
aws_secret_access_key = fake-fake-fake
""",
        }
    )

    assert (pp / "credentials").exists()
    assert (pp / "config").exists()

    monkeypatch.setenv("AWS_CONFIG_FILE", str(pp / "config"))
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(pp / "credentials"))

    aws, creds = get_aws_settings()
    assert creds is not None
    assert aws["region_name"] == "us-west-2"
    assert aws["aws_access_key_id"] == "AKIAWYXYXYXYXYXYXYXY"
    assert aws["aws_secret_access_key"] == "fake-fake-fake"

    sess = mk_boto_session(
        profile="no_region", creds=creds.get_frozen_credentials(), region_name="mordor"
    )

    assert (
        sess.get_credentials().get_frozen_credentials()
        == creds.get_frozen_credentials()
    )

    aws, creds = get_aws_settings(profile="east")
    assert aws["region_name"] == "us-east-1"
    assert aws["aws_access_key_id"] == "AKIAEYXYXYXYXYXYXYXY"
    assert aws["aws_secret_access_key"] == "fake-fake-fake"

    aws, creds = get_aws_settings(aws_unsigned=True)
    assert creds is None
    assert aws["region_name"] == "us-west-2"
    assert aws["aws_unsigned"] is True

    aws, creds = get_aws_settings(
        profile="no_region", region_name="us-west-1", aws_unsigned=True
    )

    assert creds is None
    assert aws["region_name"] == "us-west-1"
    assert aws["aws_unsigned"] is True

    with mock.patch(
        "datacube.utils.aws._fetch_text", return_value=_json(region="mordor")
    ):
        aws, creds = get_aws_settings(profile="no_region", aws_unsigned=True)

        assert aws["region_name"] == "mordor"
        assert aws["aws_unsigned"] is True


@mock.patch("datacube.utils.aws.get_creds_with_retry", return_value=None)
def test_get_aws_settings_no_credentials(without_aws_env) -> None:
    # get_aws_settings should fail when credentials are not available
    with pytest.raises(ValueError, match="Couldn't get credentials"):
        _, _ = get_aws_settings(region_name="fake")


def test_creds_with_retry() -> None:
    session = mock.MagicMock()
    session.get_credentials = mock.MagicMock(return_value=None)

    assert get_creds_with_retry(session, 2, 0.01) is None
    assert session.get_credentials.call_count == 2


def test_s3_url_parsing() -> None:
    assert s3_url_parse("s3://bucket/key") == ("bucket", "key")
    assert s3_url_parse("s3://bucket/key/") == ("bucket", "key/")
    assert s3_url_parse("s3://bucket/k/k/key") == ("bucket", "k/k/key")

    with pytest.raises(ValueError):
        s3_url_parse("file://some/path")


def test_s3_fmt_range() -> None:
    from numpy import s_

    assert s3_fmt_range((0, 3)) == "bytes=0-2"
    assert s3_fmt_range(s_[4:10]) == "bytes=4-9"
    assert s3_fmt_range(s_[:10]) == "bytes=0-9"
    assert s3_fmt_range(None) is None

    for bad in (s_[10:], s_[-2:3], s_[:-3], (-1, 3), (3, -1), s_[1:100:3]):
        with pytest.raises(ValueError):
            s3_fmt_range(bad)


def test_s3_client(without_aws_env) -> None:
    from botocore.credentials import ReadOnlyCredentials

    creds = ReadOnlyCredentials("fake-key", "fake-secret", None)

    # Mock AWS to make the test run faster.
    # From ~5 seconds to ~ 0.3s
    with moto.mock_aws():
        assert (
            str(s3_client(region_name="kk")._endpoint)  # type: ignore[attr-defined]
            == "s3(https://s3.kk.amazonaws.com)"
        )
        assert (
            str(s3_client(region_name="kk", use_ssl=False)._endpoint)  # type: ignore[attr-defined]
            == "s3(http://s3.kk.amazonaws.com)"
        )

        s3 = s3_client(region_name="us-west-2", creds=creds)
        assert s3 is not None


def test_s3_io(monkeypatch, without_aws_env) -> None:
    from numpy import s_

    url = "s3://bucket/file.txt"
    bucket, _ = s3_url_parse(url)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "fake-key-id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "fake-secret")

    with moto.mock_aws():
        s3 = s3_client(region_name="kk")
        s3.create_bucket(  # type: ignore[attr-defined]
            Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "kk"}
        )
        assert s3_dump(b"33", url, s3=s3) is True
        assert s3_fetch(url, s3=s3) == b"33"

        meta = s3_head_object(url, s3=s3)
        assert meta is not None
        assert "LastModified" in meta
        assert "ContentLength" in meta
        assert "ETag" in meta
        assert meta["ContentLength"] == 2

        assert s3_head_object(url + "-nosuch", s3=s3) is None

        assert s3_dump(b"0123456789ABCDEF", url, s3=s3) is True
        assert s3_fetch(url, range=s_[:4], s3=s3) == b"0123"
        assert s3_fetch(url, range=s_[3:8], s3=s3) == b"34567"

        with pytest.raises(ValueError):
            s3_fetch(url, range=s_[::2], s3=s3)


def test_s3_unsigned(monkeypatch, without_aws_env) -> None:
    with moto.mock_aws():
        s3 = s3_client(aws_unsigned=True)
        assert s3._request_signer.signature_version == botocore.UNSIGNED  # type: ignore[attr-defined]

        monkeypatch.setenv("AWS_UNSIGNED", "yes")
        s3 = s3_client()
        assert s3._request_signer.signature_version == botocore.UNSIGNED  # type: ignore[attr-defined]


@mock.patch("datacube.utils.aws.ec2_current_region", return_value="us-west-2")
def test_s3_client_cache(monkeypatch, without_aws_env) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "fake-key-id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "fake-secret")

    # Mock AWS to make the test run faster.
    # From ~5 seconds to ~ 0.3s
    with moto.mock_aws():
        s3 = s3_client(cache=True)
        assert s3 is s3_client(cache=True)
        assert s3 is s3_client(cache="purge")
        assert s3_client(cache="purge") is None
        assert s3 is not s3_client(cache=True)

    opts: tuple[dict[str, Any], ...] = (
        {},
        {"region_name": "foo"},
        {"region_name": "bar"},
        {"profile": "foo"},
        {"profile": "foo", "region_name": "xxx"},
        {"profile": "bar"},
        {"creds": ReadOnlyCredentials("fake1", "...", None)},
        {"creds": ReadOnlyCredentials("fake1", "...", None), "region_name": "custom"},
        {"creds": ReadOnlyCredentials("fake2", "...", None)},
    )

    keys = {_s3_cache_key(**o) for o in opts}
    assert len(keys) == len(opts)


def test_obtain_new_iam_token(monkeypatch, without_aws_env) -> None:
    import moto
    from sqlalchemy.engine.url import URL

    url = URL.create(
        "postgresql",
        host="fakehost",
        database="fake_db",
        port=5432,
        username="fakeuser",
        password="definitely_a_fake_password",
    )

    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "fake-key-id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "fake-secret")
    with moto.mock_aws():
        token = obtain_new_iam_auth_token(url, region_name="us-west-1")
        assert isinstance(token, str)
