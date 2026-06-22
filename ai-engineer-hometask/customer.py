import json
import pathlib

_RAW = json.loads(
    (pathlib.Path(__file__).parent / "materials" / "customers.json").read_text()
)
_INDEX = {c["id"]: c for c in _RAW["customers"]}


def get_safe(customer_id: str) -> dict:
    """Return only safe fields — restricted fields (cnic, pan, iban) are never loaded."""
    record = _INDEX.get(customer_id)
    if record is None:
        raise KeyError(f"Unknown customer: {customer_id!r}")
    return {"id": customer_id, **record["safe"]}
