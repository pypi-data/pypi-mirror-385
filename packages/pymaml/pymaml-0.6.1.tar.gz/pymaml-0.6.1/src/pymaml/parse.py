"""
Helper module to parse and check valid maml data structures.
"""

from pydantic_core import ValidationError

from .model_v1p0 import V1P0
from .model_v1p1 import V1P1
from .read import read_maml


MODELS = {
    "v1.0": V1P0,
    "v1.1": V1P1,
}


def _is_subsequence(sub: list, full: list) -> bool:
    """Check if `sub` is a subsequence of `full` (relative order preserved)."""
    it = iter(full)
    return all(any(s == f for f in it) for s in sub)


def check_order(data: dict, version: str) -> bool:
    """
    Recursively check that the order of keys in `data` is a subsequence
    of the schema order defined by the given model version.
    """
    _assert_version(version)
    schema = MODELS[version].with_defaults().model_dump(mode="json")

    def _check_recursive(d: dict, s: dict) -> bool:
        if not isinstance(d, dict) or not isinstance(s, dict):
            return True  # nothing to check here

        d_keys = list(d.keys())
        s_keys = list(s.keys())
        if not _is_subsequence(d_keys, s_keys):
            return False

        for k, dv in d.items():
            if k not in s:
                continue  # ignore unknown keys. Will crash when read in anyways.
            sv = s[k]
            if isinstance(dv, dict) and isinstance(sv, dict):
                if not _check_recursive(dv, sv):
                    return False
            elif isinstance(dv, list) and isinstance(sv, list):
                for d_item, s_item in zip(dv, sv):
                    if isinstance(d_item, dict) and isinstance(s_item, dict):
                        if not _check_recursive(d_item, s_item):
                            return False
        return True

    return _check_recursive(data, schema)


def _assert_version(version: str) -> None:
    """
    Determines if the version is supported and crashes if it isn't.
    """
    if version not in MODELS:
        raise ValueError(
            f"{version} is not a valid version. Supported MAML versions: {list(MODELS.keys())}"
        )


def valid_for(file_name: str) -> list[str]:
    """
    Reads in a file and determines if it is valid for versions of maml.
    """
    dictionary = read_maml(file_name)
    valid = []
    for version, model in MODELS.items():
        try:
            model(**dictionary)
            valid.append(version)
        except ValidationError:
            pass
    if not valid:
        return ["Not valid for any version of MAML"]
    return valid
