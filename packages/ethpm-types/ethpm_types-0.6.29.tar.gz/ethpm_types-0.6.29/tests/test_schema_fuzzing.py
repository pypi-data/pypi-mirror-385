import pytest
import requests
from hypothesis import HealthCheck, given, settings
from hypothesis_jsonschema import from_schema
from pydantic import ValidationError

from ethpm_types import PackageManifest

ETHPM_SCHEMA = "https://raw.githubusercontent.com/ethpm/ethpm-spec/master/spec/v3.spec.json"


@pytest.mark.xfail(reason="Official Schema is under-specified")
@pytest.mark.fuzzing
@given(manifest=from_schema(requests.get(ETHPM_SCHEMA).json()))
@settings(suppress_health_check=(HealthCheck.too_slow,))
def test_schema(manifest):
    try:
        assert PackageManifest.model_validate(manifest).model_dump() == manifest

    except (ValidationError, ValueError):
        pass  # Expect these kinds of errors
