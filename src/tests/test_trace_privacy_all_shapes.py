"""CP4 security audit: no shape the team wrote leaks secret or PII anywhere.

Checks the trace file, the RunResult and stdout against the real sensitive
values in the public world (order phone/address/internal note/item name,
claim parent_secret/raw_headers), not only the CANARY markers.
"""

import json

import pytest

from lab8.db import init_store
from lab8.shapes import orchestrator, single, workflow
from tests.conftest import CLAIMS, WORLD

SHAPES = {"workflow": workflow.run_claim, "single": single.run_claim, "orchestrator": orchestrator.run_claim}
MARKERS = ("CANARY_SECRET_", "CANARY_INTERNAL_", "parent_secret", "raw_headers")


def _sensitive_values() -> set[str]:
    values = set()
    for order in WORLD["orders"]:
        for key in ("phone", "address", "internal_note", "item_name"):
            values.add(str(order.get(key) or ""))
    for claim in CLAIMS:
        values.add(str(claim.get("parent_secret") or ""))
        headers = claim.get("raw_headers")
        if isinstance(headers, dict):
            values.update(str(v) for v in headers.values())
        elif headers:
            values.add(str(headers))
    # Very short values (empty, "{}") would match by accident.
    return {v for v in values if len(v) >= 6}


SENSITIVE = sorted(_sensitive_values())


@pytest.mark.parametrize("seed", [11, 55])
@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_no_secret_or_pii_in_trace_result_or_stdout(tmp_path, capsys, shape, seed):
    store = tmp_path / f"{shape}-{seed}.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    leaks = []
    for claim in CLAIMS:
        result = SHAPES[shape](claim["claim_id"], seed=seed, store_path=str(store))
        with open(result.trace_path, encoding="utf-8") as fh:
            blob = fh.read()
        blob += json.dumps(result.as_dict(), ensure_ascii=False)
        blob += capsys.readouterr().out
        for needle in (*MARKERS, *SENSITIVE):
            if needle in blob:
                leaks.append((claim["claim_id"], needle[:24]))
    assert not leaks, f"{shape} seed {seed} leaked: {leaks}"


def test_audit_covers_real_values():
    """Guard: the audit is meaningless if the sensitive set came out empty."""
    assert any("CANARY_SECRET_" in v for v in SENSITIVE)
    assert len(SENSITIVE) >= len(WORLD["orders"])
