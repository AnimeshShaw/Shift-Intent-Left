from sil.globs import any_match, glob_match, normalize


def test_recursive_directory_pattern():
    assert glob_match("services/payments/**", "services/payments/a/b.py")
    assert not glob_match("services/payments/**", "services/billing/x.py")


def test_double_star_prefix_matches_root_and_nested():
    assert glob_match("**/*.pem", "a.pem")
    assert glob_match("**/*.pem", "x/y/a.pem")
    assert glob_match("**/security/**", "security/x")
    assert glob_match("**/security/**", "a/security/x")


def test_single_star_does_not_cross_directories():
    assert glob_match("requirements*.txt", "requirements-dev.txt")
    assert not glob_match("requirements*.txt", "vendor/requirements.txt")


def test_bare_pattern_anchored_when_permitting():
    # A bare pattern in a permitting set must not authorise deep paths.
    assert not glob_match("requirements*.txt", "vendor/deep/requirements.txt", anywhere=False)


def test_bare_pattern_matches_anywhere_when_restricting():
    # ...but the same pattern in a restricting set must catch them.
    assert glob_match(".env*", "config/.env.local", anywhere=True)
    assert glob_match(".env*", ".env", anywhere=True)


def test_traversal_and_absolute_paths_escape_workspace():
    assert normalize("../etc/passwd") is None
    assert normalize("a/../../etc/passwd") is None
    assert normalize("/etc/passwd") is None
    assert normalize("C:\\Windows\\system32") is None
    assert normalize("./services//payments/../payments/a.py") == "services/payments/a.py"


def test_escaping_path_is_in_no_set():
    assert not any_match(["**"], None)
    assert not any_match([".env*"], None, anywhere=True)
