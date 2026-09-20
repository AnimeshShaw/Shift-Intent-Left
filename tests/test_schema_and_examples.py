import json
import pathlib

import jsonschema
import pytest
import yaml

from sil import load_contract
from conftest import FIXTURES, ROOT

SCHEMA = json.loads((ROOT / "schema" / "intent-contract.schema.json").read_text(encoding="utf-8"))
VALID = sorted((ROOT / "examples").glob("*.yaml")) + [FIXTURES / "appendix_d.yaml"]


def test_schema_is_a_valid_json_schema():
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.name)
def test_valid_contracts_conform_and_load(path):
    jsonschema.validate(yaml.safe_load(path.read_text(encoding="utf-8")), SCHEMA)
    c = load_contract(path)
    assert c.digest.startswith("sha256:")
    assert c.theta                       # Theta is non-empty


def test_digest_is_stable_and_content_sensitive():
    a = load_contract(FIXTURES / "appendix_d.yaml")
    b = load_contract(FIXTURES / "appendix_d.yaml")
    assert a.digest == b.digest
    other = load_contract(ROOT / "examples" / "iac-change.yaml")
    assert a.digest != other.digest
