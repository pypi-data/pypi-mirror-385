import pytest

import dotenv_utils as du
from dotenv_utils.casts import str2int


@pytest.fixture
def clean_env(monkeypatch):
    """Provide a clean environment mapping for each test.

    This isolates tests from the real OS environment and from each other.
    """
    import dotenv_utils as du_pkg
    import dotenv_utils.__init__ as du_init
    env: dict[str, str] = {}
    # Replace the module-level environ used by the functions under test
    monkeypatch.setattr(du_init, "environ", env)
    monkeypatch.setattr(du_pkg, "environ", env)
    return env


def test_get_var_missing_raises(clean_env):
    with pytest.raises(RuntimeError) as exc:
        du.get_var("MISSING_VAR")
    assert "MISSING_VAR" in str(exc.value)


def test_get_var_with_default_when_missing(clean_env):
    # When env is missing and default is provided, it should return the default as-is
    assert du.get_var("MY_INT", default=42) == 42
    assert isinstance(du.get_var("MY_STR", default="abc"), str)


def test_get_var_casts_value_when_present(clean_env):
    clean_env["PORT"] = "  8080  "
    assert du.get_var("PORT", cast=str2int) == 8080


def test_get_var_list_missing_default(clean_env):
    default_list = [1, 2, 3]
    # Should return the provided default list verbatim when missing
    assert du.get_var_list("NUMBERS", default=default_list) is default_list
    assert du.get_var_list("NUMBERS", default=default_list) == [1, 2, 3]


def test_get_var_list_split_and_cast(clean_env):
    clean_env["IDS"] = "1; 2 ;3"
    assert du.get_var_list("IDS", cast=str2int) == [1, 2, 3]


def test_get_var_list_sep_none(clean_env):
    clean_env["RAW"] = "a;b;c"
    # No splitting when sep=None; result is a single-item list
    assert du.get_var_list("RAW", sep=None) == ["a;b;c"]


def test_get_var_list_trims_whitespace(clean_env):
    clean_env["USERS"] = " alice ; bob;  carol "
    assert du.get_var_list("USERS") == ["alice", "bob", "carol"]


def test_get_var_list_missing_raises(clean_env):
    with pytest.raises(RuntimeError):
        du.get_var_list("UNSET_LIST")
