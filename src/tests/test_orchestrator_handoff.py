"""Shape C: handoff stays on the allowlist, trace carries no parent context."""

import json

import pytest

from lab8.db import connect, init_store
from lab8.handoff import ALLOWED_FIELDS, READONLY_TOOLS
from lab8.metrics import trial_pass
from lab8.shapes.orchestrator import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD

FORBIDDEN = ("CANARY_SECRET_", "parent_secret", "raw_headers")


def _events(result):
    with open(result.trace_path, encoding="utf-8") as fh:
        doc = json.load(fh)
    assert doc["run_id"] == result.run_id
    return doc["events"]


def test_handoff_in_trace_is_allowlisted_and_read_only(public_db):
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    handoffs = [e["payload"] for e in _events(result) if e["kind"] == "handoff"]
    assert len(handoffs) == 1
    assert set(handoffs[0]) <= ALLOWED_FIELDS
    assert set(handoffs[0]["allowed_tools"]) <= READONLY_TOOLS


@pytest.mark.parametrize("claim_id", sorted(BY_ID))
def test_trace_has_no_parent_secret(public_db, claim_id):
    result = run_claim(claim_id, seed=11, store_path=str(public_db))
    with open(result.trace_path, encoding="utf-8") as fh:
        blob = fh.read()
    for marker in FORBIDDEN:
        assert marker not in blob, f"{marker} leaked in {claim_id} trace"


def test_ticket_delay_never_overrides_order_row(tmp_path):
    """Swarm pays C-002 on seed 55 by trusting the ticket. The orchestrator must not."""
    for seed in (11, 22, 33, 44, 55):
        store = tmp_path / f"c002-{seed}.sqlite"
        init_store(store, WORLD, CLAIMS).close()
        result = run_claim("C-002", seed=seed, store_path=str(store))
        conn = connect(store)
        try:
            passed, reason = trial_pass(result.as_dict(), BY_ID["C-002"]["expected"], conn)
        finally:
            conn.close()
        assert passed, f"seed {seed}: {reason}"
