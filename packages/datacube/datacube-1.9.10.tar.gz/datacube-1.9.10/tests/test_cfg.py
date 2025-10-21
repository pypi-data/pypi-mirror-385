# This file is part of the Open Data Cube, see https://opendatacube.org for more information
#
# Copyright (c) 2015-2025 ODC Contributors
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import MagicMock

import pytest

from datacube.testutils import suppress_deprecations


def test_smells_like_ini() -> None:
    from datacube.cfg.utils import smells_like_ini

    assert smells_like_ini("""[an_ini_file]
key: value
other-key: 12

""")
    assert smells_like_ini("""
; This is an ini comment
[an_ini_file]
key: value
other-key: 12

""")
    assert not smells_like_ini("""# This is a YAML comment

spagoots:
  four: score
  and: 7
  years: ago
""")
    assert not smells_like_ini("""{
"spagoots":{
  "four": "score",
  "and": 7,
  "years": "ago",
  # no comments in json!
  }
}
""")
    assert smells_like_ini("""[
    Looks ini-ish but
    :::is:::
    GIBBER-ish ..;';'@#$%^@#$%^#$^&$
\n  \n    \n \n  \t  \t  \n   \n
aasdfer\\faw043[]]][""")

    # Pure white space
    assert smells_like_ini("   \n  \n    \n \n  \t  \t  \n   \n")


@pytest.fixture
def simple_valid_ini() -> str:
    return """[foo]
bar: bell
bat: 7
baz: luhrmann
[goo]
bar: beque
bat: 2
baz: mckenzie
"""


@pytest.fixture
def simple_valid_yaml() -> str:
    return """foo:
    bar: bell
    bat: 7
    baz: luhrmann
goo:
    bar: beque
    bat: 2
    baz: mckenzie
"""


def test_parse_text(simple_valid_ini, simple_valid_yaml) -> None:
    from datacube.cfg import CfgFormat, ConfigException, parse_text

    ini = parse_text(simple_valid_ini)
    yaml = parse_text(simple_valid_yaml)
    assert ini["foo"]["bar"] == yaml["foo"]["bar"]
    assert ini["goo"]["baz"] == yaml["goo"]["baz"]
    assert int(ini["foo"]["bat"]) == int(yaml["foo"]["bat"])

    with pytest.raises(ConfigException):
        parse_text(simple_valid_ini, fmt=CfgFormat.YAML)

    with pytest.raises(ConfigException):
        parse_text(simple_valid_yaml, fmt=CfgFormat.INI)


def mk_single_env_config(connector: str) -> str:
    return f"""# Simple single environment config
new:
   index_driver: postgis
   db_url: postgresql{connector}://foo:bar@server.subdomain.domain/mytestdb
   db_iam_authentication: yes
"""


@pytest.fixture
def single_env_config():
    return mk_single_env_config("+psycopg2")


@pytest.fixture
def single_env_config_psycopg3():
    return mk_single_env_config("+psycopg")


@pytest.fixture
def single_env_config_no_connector():
    return mk_single_env_config("")


@pytest.fixture
def simple_config() -> str:
    return """# Simple but thorough test config
default:
   alias: legacy
postgres:
   alias: legacy
legacy:
   index_driver: default
   db_username: foo
   db_password: bar
   db_hostname: server.subdomain.domain
   db_port: 5433
   db_database: mytestdb
   db_connection_timeout: 20
new:
   index_driver: postgis
   db_url: postgresql+psycopg2://foo:bar@server.subdomain.domain/mytestdb
   db_iam_authentication: yes
postgis:
   alias: new
memory:
   index_driver: memory
   db_url: '@nota?valid:url//foo&bar%%%'
new2:
   index_driver: postgis
   db_url: postgresql+psycopg2://foo:bar@server.subdomain.domain/mytestdb
   db_database: not_read
   db_port: ignored
   db_iam_authentication: yes
   db_iam_timeout: 300
"""


@pytest.fixture
def simple_dict() -> dict[str, dict[str, str | int]]:
    legacy: dict[str, str | int] = {
        "index_driver": "default",
        "db_username": "foo",
        "db_password": "bar",
        "db_hostname": "server.subdomain.domain",
        "db_port": 5433,
        "db_database": "mytestdb",
        "db_connection_timeout": 20,
    }
    postgis: dict[str, str | int] = {
        "index_driver": "postgis",
        "db_url": "postgresql+psycopg2://foo:bar@server.subdomain.domain/mytestdb",
        "db_iam_authentication": "yes",
    }
    d: dict[str, dict[str, str | int]] = {
        "default": {"alias": "legacy"},
        "postgres": {"alias": "legacy"},
        "legacy": legacy,
        "new": postgis,
        "postgis": {"alias": "new"},
        "memory": {"index_driver": "memory", "db_url": "@nota?valid:url//foo&bar%%%"},
        "new2": {
            "index_driver": "postgis",
            "db_url": "postgresql+psycopg2://foo:bar@server.subdomain.domain/mytestdb",
            "db_database": "not_read",
            "db_port": "ignored",
            "db_iam_authentication": "yes",
            "db_iam_timeout": 300,
        },
        # No upper case and no kind of separator like _/+ permitted in names, so
        # number drivers using psycopg3 in sequence.
        "datacube3": legacy.copy(),
        "postgis3": postgis.copy(),
    }
    # Use identical configs for postgres/postgis drivers with psycopg3, just patch
    # them up with the psycopg3 specific parts.
    for k in ["datacube3", "postgis3"]:
        d[k]["psycopg_version"] = 3
        db_url = d[k].get("db_url")
        if isinstance(db_url, str):
            d[k]["db_url"] = db_url.replace("psycopg2://", "psycopg://")
    return d


def test_invalid_env() -> None:
    from datacube.cfg import ConfigException, ODCConfig

    with pytest.raises(ConfigException):
        ODCConfig(
            text="""
default:
    alias: royale_avec_fromage
            """
        )
    with pytest.raises(ConfigException):
        ODCConfig(
            text="""
default:
    alias: legit00
non_legit:
    index_driver: null
        """
        )


def test_oldstyle_cfg() -> None:
    from datacube.cfg import ODCConfig

    with pytest.warns(UserWarning, match=r"default_environment.*no longer supported"):
        cfg = ODCConfig(
            text="""
        default:
            index_driver: memory
        env2:
            index_driver: memory
        env3:
            index_driver: memory
        user:
            default_environment: env3
        """
        )
        assert cfg[None]._name == "default"


def test_invalid_option() -> None:
    from datacube.cfg import ConfigException, ODCOptionHandler

    mockenv = MagicMock()
    with pytest.raises(ConfigException):
        ODCOptionHandler("NO_CAPS", mockenv)


def test_single_env(
    single_env_config, single_env_config_psycopg3, single_env_config_no_connector
) -> None:
    from datacube.cfg import ODCConfig

    db_urls = []
    for cfg in [
        ODCConfig(text=single_env_config),
        ODCConfig(text=single_env_config_psycopg3),
        ODCConfig(text=single_env_config_no_connector),
    ]:
        assert cfg["new"].index_driver == "postgis"
        db_urls.append(cfg["new"].db_url)
        assert cfg["new"].db_username == "foo"
        with pytest.raises(AttributeError):
            assert cfg["new"].not_an_option
        assert cfg["new"]["db_iam_authentication"]
        assert cfg["new"].db_iam_timeout == 600
        assert cfg["new"]["db_connection_timeout"] == 60
    assert db_urls == [
        "postgresql+psycopg2://foo:bar@server.subdomain.domain/mytestdb",
        "postgresql+psycopg://foo:bar@server.subdomain.domain/mytestdb",
        "postgresql://foo:bar@server.subdomain.domain/mytestdb",
    ]


def assert_simple_aliases(cfg) -> None:
    assert cfg["default"]._name == "legacy"
    assert cfg["postgres"]._name == "legacy"
    assert cfg["legacy"]._name == "legacy"
    assert cfg["postgis"]._name == "new"
    assert cfg["new"]._name == "new"
    assert cfg["memory"]._name == "memory"
    assert cfg["new2"]._name == "new2"
    assert cfg["dynamic"]._name == "dynamic"
    assert cfg[None]._name == "legacy"


def test_aliases(simple_config) -> None:
    from datacube.cfg import ConfigException, ODCConfig

    cfg = ODCConfig(text=simple_config)
    assert_simple_aliases(cfg)
    with pytest.raises(ConfigException) as e:
        cfg = ODCConfig(
            raw_dict={
                "default": {"alias": "main", "invalid_option": True},
                "main": {"index_driver": "memory"},
            }
        )
    assert "invalid_option" in str(e.value)


def assert_simple_options(cfg) -> None:
    assert cfg["default"]["index_driver"] == "default"
    assert cfg["default"].db_username == "foo"
    assert not cfg["default"]["db_iam_authentication"]
    with pytest.raises(KeyError):
        assert cfg["default"]["db_iam_timeout"]

    assert (
        cfg["new2"].db_url
        == "postgresql+psycopg2://foo:bar@server.subdomain.domain/mytestdb"
    )
    assert cfg["new2"].db_username == "foo"
    with pytest.raises(AttributeError):
        assert cfg["new2"].not_an_option
    assert cfg["new2"]["db_iam_authentication"]
    assert cfg["new2"].db_iam_timeout == 300
    assert cfg["new2"]["db_connection_timeout"] == 60


def test_options(simple_config) -> None:
    from datacube.cfg import ODCConfig

    cfg = ODCConfig(text=simple_config)
    assert_simple_options(cfg)


def test_rawdict(simple_dict) -> None:
    from datacube.cfg import ODCConfig

    cfg = ODCConfig(raw_dict=simple_dict)
    assert_simple_aliases(cfg)
    assert_simple_options(cfg)


def test_noenv_overrides_in_text(simple_config, monkeypatch) -> None:
    monkeypatch.setenv("ODC_LEGACY_DB_USERNAME", "bar")
    monkeypatch.setenv("ODC_NEW_DB_USERNAME", "bar")
    from datacube.cfg import ODCConfig

    cfg = ODCConfig(text=simple_config)

    assert cfg["legacy"].db_username != "bar"
    assert cfg["new"].db_username != "bar"


@pytest.fixture
def path_to_yaml_config():
    import os.path

    return os.path.join(os.path.dirname(__file__), "cfg", "simple_cfg.yaml")


@pytest.fixture
def path_to_ini_config():
    import os.path

    return os.path.join(os.path.dirname(__file__), "cfg", "simple_cfg.ini")


@pytest.fixture
def path_to_different_config():
    import os.path

    return os.path.join(os.path.dirname(__file__), "cfg", "different_cfg.yaml")


def test_yaml_from_path(path_to_yaml_config) -> None:
    from datacube.cfg import ODCConfig

    cfg = ODCConfig(paths=path_to_yaml_config)
    assert_simple_aliases(cfg)
    assert_simple_options(cfg)


def test_ini_from_path(path_to_ini_config) -> None:
    from datacube.cfg import ODCConfig

    cfg = ODCConfig(paths=path_to_ini_config)
    assert_simple_aliases(cfg)
    assert_simple_options(cfg)


def test_ini_from_paths(
    path_to_ini_config, path_to_yaml_config, path_to_different_config, monkeypatch
) -> None:
    from datacube.cfg import ConfigException, ODCConfig

    cfg = ODCConfig(
        paths=[
            "/non/existent/path.yml",
            path_to_yaml_config,
            path_to_different_config,
            path_to_ini_config,
        ]
    )
    assert cfg[None]._name == "legacy"

    cfg = ODCConfig(
        paths=[
            path_to_different_config,
            "/non/existent/path.yml",
            path_to_yaml_config,
        ]
    )
    assert cfg[None]._name == "new"

    with pytest.raises(ConfigException):
        cfg = ODCConfig(
            paths=[
                "/non/existent/path.yml",
                "/another/nonexistent/path.yml",
                "/etc",
            ]
        )

    with monkeypatch.context() as mp:
        mp.setattr(
            "datacube.cfg.cfg._DEFAULT_CONFIG_SEARCH_PATH",
            [
                "/non/existent/path.yml",
                "/another/nonexistent/path.yml",
                "/etc",
                path_to_yaml_config,
            ],
        )
        cfg = ODCConfig()
        assert cfg[None]._name == "legacy"

    with monkeypatch.context() as mp:
        mp.setattr(
            "datacube.cfg.cfg._DEFAULT_CONFIG_SEARCH_PATH",
            [
                "/non/existent/path.yml",
                "/etc",
                "/another/nonexistent/path.yml",
            ],
        )
        cfg = ODCConfig()
        assert cfg[None]._name == "default"

    with monkeypatch.context() as mp:
        mp.setenv(
            "ODC_CONFIG_PATH",
            f"/non/existent/path.yml:{path_to_yaml_config}:{path_to_different_config}",
        )
        cfg = ODCConfig()
        assert cfg[None]._name == "legacy"

    with suppress_deprecations():  # noqa: SIM117
        with monkeypatch.context() as mp:
            mp.setenv(
                "DATACUBE_CONFIG_PATH",
                f"/non/existent/path.yml:{path_to_yaml_config}:{path_to_different_config}",
            )
            cfg = ODCConfig()
            assert cfg[None]._name == "legacy"


def test_envvar_overrides(path_to_yaml_config, monkeypatch) -> None:
    monkeypatch.setenv("ODC_LEGACY_DB_USERNAME", "bar")
    monkeypatch.setenv("ODC_NEW_DB_USERNAME", "bar")
    monkeypatch.setenv("ODC_NEW2_DB_CONNECTION_TIMEOUT", "20")
    monkeypatch.setenv("DATACUBE_IAM_AUTHENTICATION", "yes")

    from datacube.cfg import ODCConfig

    with suppress_deprecations():
        cfg = ODCConfig(paths=path_to_yaml_config)
        assert cfg["legacy"].db_username == "bar"
        assert cfg["legacy"].db_iam_authentication
        assert cfg["new"].db_iam_authentication
        assert cfg["new2"].db_iam_authentication
        assert cfg["new2"].db_connection_timeout == 20
        assert cfg["new"].db_username != "bar"


def test_intopt_validation() -> None:
    from datacube.cfg import ConfigException, ODCConfig

    cfg = ODCConfig(
        text="""
env1:
    db_hostname: localhost
    db_port: seven
"""
    )
    with pytest.raises(ConfigException):
        assert cfg["env1"].db_hostname == "localhost"
    cfg = ODCConfig(
        text="""
env1:
    db_hostname: localhost
    db_port: -7
"""
    )
    with pytest.raises(ConfigException):
        assert cfg["env1"].db_hostname == "localhost"
    cfg = ODCConfig(
        text="""
env1:
    db_hostname: localhost
    db_port: 4425542239934
"""
    )
    with pytest.raises(ConfigException):
        assert cfg["env1"].db_hostname == "localhost"
    cfg = ODCConfig(
        text="""
env1:
    db_hostname: localhost
    db_port: 0
"""
    )
    with pytest.raises(ConfigException):
        assert cfg["env1"].db_hostname == "localhost"


def test_invalid_idx_driver() -> None:
    from datacube.cfg import ConfigException, ODCConfig

    cfg = ODCConfig(
        raw_dict={
            "default": {"alias": "foo"},
            "foo": {
                "index_driver": "phillips_head",
            },
        }
    )
    with pytest.raises(ConfigException) as e:
        _ = cfg["default"].index_driver
    estr = str(e.value)
    assert "Unknown index driver" in estr
    assert "phillips_head" in estr
    assert "legacy" in estr


def test_invalid_pg_url() -> None:
    from datacube.cfg import ConfigException, ODCConfig

    cfg = ODCConfig(
        raw_dict={
            "default": {"alias": "foo"},
            "foo": {"index_driver": "postgres", "db_url": "https://www.google.com"},
        }
    )
    with pytest.raises(ConfigException):
        assert cfg["default"].index_driver == "postgres"


def test_pgurl_from_config(simple_dict) -> None:
    from datacube.cfg import ODCConfig, psql_url_from_config

    cfg = ODCConfig(raw_dict=simple_dict)
    assert (
        psql_url_from_config(cfg["legacy"])
        == "postgresql+psycopg2://foo:bar@server.subdomain.domain:5433/mytestdb"
    )
    assert (
        psql_url_from_config(cfg["new"])
        == "postgresql+psycopg2://foo:bar@server.subdomain.domain/mytestdb"
    )
    assert (
        psql_url_from_config(cfg["datacube3"])
        == "postgresql+psycopg://foo:bar@server.subdomain.domain:5433/mytestdb"
    )
    assert (
        psql_url_from_config(cfg["postgis3"])
        == "postgresql+psycopg://foo:bar@server.subdomain.domain/mytestdb"
    )
    with pytest.raises(AttributeError):
        psql_url_from_config(cfg["memory"])
    assert (
        cfg["new2"].db_url
        == "postgresql+psycopg2://foo:bar@server.subdomain.domain/mytestdb"
    )
    assert cfg["new2"].db_username == "foo"
    assert cfg["new2"].db_password == "bar"
    assert cfg["new2"].db_hostname == "server.subdomain.domain"
    assert not cfg["new2"].db_port
    assert cfg["new2"].db_database == "mytestdb"

    cfg = ODCConfig(
        raw_dict={
            "foo": {
                "db_hostname": "remotehost.local",
                "db_username": "penelope",
                "db_database": "mydb",
                "db_port": 5544,
            }
        }
    )
    assert (
        psql_url_from_config(cfg["foo"])
        == "postgresql+psycopg2://penelope@remotehost.local:5544/mydb"
    )
    cfg = ODCConfig(
        raw_dict={
            "foo": {
                "db_hostname": "remotehost.local",
                "db_username": "penelope",
                "db_port": 5544,
            }
        }
    )


def test_multiple_sourcetypes(simple_config, path_to_ini_config, simple_dict) -> None:
    from datacube.cfg import ConfigException, ODCConfig

    with pytest.raises(ConfigException) as e:
        ODCConfig(paths=path_to_ini_config, raw_dict=simple_dict, text=simple_config)
    assert "Can only supply one of" in str(e.value)
    with pytest.raises(ConfigException) as e:
        ODCConfig(raw_dict=simple_dict, text=simple_config)
    assert "Can only supply one of" in str(e.value)
    with pytest.raises(ConfigException) as e:
        ODCConfig(paths=path_to_ini_config, text=simple_config)
    assert "Can only supply one of" in str(e.value)
    with pytest.raises(ConfigException) as e:
        ODCConfig(paths=path_to_ini_config, raw_dict=simple_dict)
    assert "Can only supply one of" in str(e.value)


def test_get_environment(simple_config) -> None:
    from datacube.cfg import ConfigException, ODCConfig

    cfg = ODCConfig(text=simple_config)
    with pytest.raises(ConfigException) as e:
        ODCConfig.get_environment(config=cfg, raw_config=simple_config)
    assert "Cannot specify both" in str(e.value)
    env = ODCConfig.get_environment(config=cfg, env="default")
    assert env is cfg[None]


def test_raw_by_environment(simple_config, monkeypatch) -> None:
    from datacube.cfg import ODCConfig

    monkeypatch.setenv(
        "ODC_CONFIG",
        '{"default":{"alias": "foo"},"foo":{"index_driver":"postgis","db_url":"postgresql+psycopg2:///mydb"}}',
    )
    cfg = ODCConfig()
    assert cfg[None]._name == "foo"


def test_default_environment(simple_config, monkeypatch) -> None:
    from datacube.cfg import ODCConfig

    with suppress_deprecations():
        cfg = ODCConfig(text=simple_config)
        assert cfg[None]._name == "legacy"
        monkeypatch.setenv("ODC_ENVIRONMENT", "new2")
        assert cfg[None]._name == "new2"
        monkeypatch.setenv("ODC_ENVIRONMENT", "")
        monkeypatch.setenv("DATACUBE_ENVIRONMENT", "postgis")
        assert cfg[None]._name == "new"
        cfg = ODCConfig(raw_dict={"datacube": {"index_driver": "memory"}})
        monkeypatch.setenv("DATACUBE_ENVIRONMENT", "")
        assert cfg[None]._name == "datacube"
        cfg = ODCConfig(
            raw_dict={
                "weirdname": {"index_driver": "memory"},
                "stupidenv": {"index_driver": "null"},
            }
        )
        assert cfg[None]._name == "default"
