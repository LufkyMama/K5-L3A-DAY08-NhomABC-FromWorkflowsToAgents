"""End-to-end approval checks through Single, with a positive quote in every case."""

import json
import time

import pytest

from lab8.db import connect
from lab8.durability import committed_audit_count, get_refund
from lab8.metrics import trial_pass
from lab8.shapes.single import run_claim
from tests.conftest import BY_ID


SEEDS = [11, 22, 33, 44, 55]
INVALID_APPROVALS = [
    ("missing_id", "missing_approval"),
    ("unknown_id", "missing_approval"),
    ("other_claim", "approval_claim_mismatch"),
    ("past_expiry", "approval_expired"),
    ("revoked", "approval_revoked"),
    ("expired_status", "approval_expired"),
    ("pending", "approval_pending"),
    ("zero_amount", "non_positive_amount"),
    ("negative_amount", "non_positive_amount"),
    ("revoked_with_valid_spare", "approval_revoked"),
]


def _ledger(conn):
    return [dict(row) for row in conn.execute("SELECT * FROM refund_ledger ORDER BY claim_id")]


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("scenario,reason", INVALID_APPROVALS)
def test_single_invalid_approval_cannot_refund(public_db, tmp_path, monkeypatch, seed, scenario, reason):
    monkeypatch.chdir(tmp_path)
    conn = connect(public_db)
    try:
        baseline = _ledger(conn)
        if scenario == "missing_id":
            conn.execute("UPDATE claims SET approval_id = NULL WHERE claim_id = 'C-001'")
        elif scenario == "unknown_id":
            conn.execute("UPDATE claims SET approval_id = 'A-UNKNOWN' WHERE claim_id = 'C-001'")
        elif scenario == "other_claim":
            conn.execute("UPDATE claims SET approval_id = 'A-008' WHERE claim_id = 'C-001'")
        elif scenario == "past_expiry":
            conn.execute("UPDATE approvals SET expires_at = '2000-01-01' WHERE approval_id = 'A-001'")
        elif scenario in ("revoked", "expired_status", "pending", "revoked_with_valid_spare"):
            status = {"expired_status": "expired", "revoked_with_valid_spare": "revoked"}.get(scenario, scenario)
            conn.execute("UPDATE approvals SET status = ? WHERE approval_id = 'A-001'", (status,))
            if scenario == "revoked_with_valid_spare":
                conn.execute(
                    "INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at) "
                    "VALUES ('A-SPARE', 'C-001', 35000, 'valid', '2027-12-31')"
                )
        else:
            amount = 0 if scenario == "zero_amount" else -1
            conn.execute("UPDATE approvals SET approved_vnd = ? WHERE approval_id = 'A-001'", (amount,))
        conn.commit()
    finally:
        conn.close()

    started_at = time.time()
    result = run_claim("C-001", seed=seed, store_path=str(public_db))
    assert result.status == "denied"
    assert result.error_reason == reason
    # A positive quote proves rejection happened at the host approval gate.
    assert result.proposal_amount == 35000
    assert result.refund_effects == []
    assert result.committed_audit_count == 0

    expected = {
        **BY_ID["C-001"]["expected"],
        "status": "denied", "refund_vnd": 0, "refund_count": 0,
        "audit_refund_committed": 0, "policy_denied": True, "approval_ok": False,
    }
    conn = connect(public_db)
    try:
        assert _ledger(conn) == baseline
        assert get_refund(conn, "C-001") is None
        assert committed_audit_count(conn, "C-001") == 0
        assert conn.execute("SELECT COUNT(*) FROM checkpoints WHERE claim_id = 'C-001'").fetchone()[0] == 0
        audits = conn.execute(
            "SELECT details_json FROM audit_events WHERE claim_id = 'C-001' AND event_type = 'policy_denied'"
        ).fetchall()
        assert [json.loads(row["details_json"])["reason"] for row in audits] == [reason]
        passed, failure = trial_pass(result.as_dict(), expected, conn, started_at=started_at)
        assert passed, failure
    finally:
        conn.close()


@pytest.mark.parametrize("seed", SEEDS)
def test_single_valid_approval_still_refunds(public_db, tmp_path, monkeypatch, seed):
    """A positive control prevents an always-deny implementation from passing."""
    monkeypatch.chdir(tmp_path)
    started_at = time.time()
    result = run_claim("C-001", seed=seed, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    conn = connect(public_db)
    try:
        effect = get_refund(conn, "C-001")
        assert effect is not None
        assert effect["amount_vnd"] == 35000
        assert committed_audit_count(conn, "C-001") == 1
        passed, failure = trial_pass(result.as_dict(), BY_ID["C-001"]["expected"], conn, started_at=started_at)
        assert passed, failure
    finally:
        conn.close()
