import pytest

from sil import Action, admissible


def adm(action, contract):
    return admissible(action, contract)


# --- The three worked decisions from Section 6.4 / Appendix D of the paper ---------------

def test_paper_example_pytest_is_admissible(contract):
    assert adm(Action("shell", "execute", "pytest tests/payments"), contract).admissible


def test_paper_example_reading_env_fails_scope_and_data_class(contract):
    d = adm(Action("shell", "read", ".env"), contract)
    assert not d.admissible
    assert {"C2", "C5"} <= set(d.failed)


def test_paper_example_paste_site_fails_tool_and_egress(contract):
    d = adm(Action("http", "connect", "paste.example.net"), contract)
    assert not d.admissible
    assert set(d.failed) == {"C1", "C4"}


def test_paper_example_ci_write_fails_protected(contract):
    d = adm(Action("shell", "write", ".github/workflows/ci.yml"), contract)
    assert not d.admissible
    assert "C3" in d.failed


# --- Each condition in isolation ----------------------------------------------------------

def test_c1_unknown_tool_or_operation(contract):
    assert "C1" in adm(Action("browser", "read", "services/payments/a.py"), contract).failed
    assert "C1" in adm(Action("package", "read", "services/payments/a.py"), contract).failed


def test_c1_command_must_extend_allowlist_by_whole_arguments(contract):
    assert adm(Action("shell", "execute", "pytest -q tests/payments"), contract).admissible
    assert "C1" in adm(Action("shell", "execute", "pytestx"), contract).failed
    assert "C1" in adm(Action("shell", "execute", "rm -rf /"), contract).failed


def test_c1_install_registry_must_be_allowed(contract):
    ok = Action("package", "install", "requests", registry="pypi-internal-mirror")
    bad = Action("package", "install", "requests", registry="pypi.org")
    assert adm(ok, contract).admissible
    assert "C1" in adm(bad, contract).failed


def test_c2_read_outside_scope(contract):
    assert "C2" in adm(Action("shell", "read", "services/billing/x.py"), contract).failed


def test_c3_write_outside_writable_scope_but_inside_readable(contract):
    # tests/payments is readable but not writable.
    assert "C3" in adm(Action("shell", "write", "tests/payments/test_a.py"), contract).failed


def test_c3_protected_beats_writable(contract):
    # Inside W by pattern, but inside Pi too: Pi must win.
    assert "C3" in adm(Action("shell", "write", "services/payments/security/keys.py"), contract).failed


def test_c3_bare_protected_pattern_catches_nested_files(contract):
    # ".env*" has no slash, so as a restricting set it must match at any depth.
    d = adm(Action("shell", "write", "services/payments/.env.local"), contract)
    assert "C3" in d.failed


def test_c3_bare_writable_pattern_does_not_authorise_nested_files(contract):
    # "requirements*.txt" in W is anchored to the root as a permitting set, so a file of
    # that name under tests/ (readable, but outside W) must not be writable.
    d = adm(Action("shell", "write", "tests/payments/requirements.txt"), contract)
    assert "C3" in d.failed
    assert adm(Action("shell", "write", "requirements.txt"), contract).admissible


def test_c3_does_not_apply_to_reads(contract):
    assert adm(Action("shell", "read", "services/payments/security/keys.py"), contract).admissible is True


def test_c4_egress_is_exact_and_case_insensitive(contract):
    assert adm(Action("shell", "read", "requirements.txt"), contract).admissible
    ok = Action("shell", "connect", "PYPI-INTERNAL-MIRROR.CORP")
    # shell has no connect op in Theta, so only C1 fails; egress itself is satisfied.
    assert "C4" not in adm(ok, contract).failed
    assert "C4" in adm(Action("shell", "connect", "evil.example"), contract).failed
    assert "C4" in adm(Action("shell", "connect", "sub.pypi-internal-mirror.corp"), contract).failed


def test_c5_secret_class_denied_even_when_in_scope(contract):
    # A .pem under an in-scope directory is still class 'secrets'.
    d = adm(Action("shell", "read", "services/payments/tls/server.pem"), contract)
    assert "C5" in d.failed


def test_c6_confirmation_predicate_requires_recorded_confirmation(contract):
    base = dict(registry="pypi-internal-mirror", tags=("install_new_top_level_package",))
    unconfirmed = Action("package", "install", "left-pad", **base)
    confirmed = Action("package", "install", "left-pad", confirmation=True, **base)
    assert "C6" in adm(unconfirmed, contract).failed
    assert adm(confirmed, contract).admissible


def test_c6_ignores_unrelated_tags(contract):
    a = Action("shell", "read", "requirements.txt", tags=("some_other_tag",))
    assert adm(a, contract).admissible


def test_traversal_is_denied(contract):
    for target in ("../secrets.txt", "services/payments/../../.env", "/etc/passwd"):
        assert not adm(Action("shell", "read", target), contract).admissible


@pytest.mark.parametrize("op", ["read", "write"])
def test_windows_style_paths_are_normalised(contract, op):
    target = "services\\payments\\api.py"
    assert adm(Action("shell", op, target), contract).admissible
