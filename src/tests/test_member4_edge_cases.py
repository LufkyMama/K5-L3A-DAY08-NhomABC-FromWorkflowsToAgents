from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count
from lab8.shapes.swarm_reference import run_claim as run_swarm


def test_swarm_retry_same_claim_is_idempotent(public_db: Path) -> None:
    """Gọi lại cùng một claim nhiều lần chỉ tạo đúng 1 dòng ledger và 1 audit."""
    first = run_swarm("C-001", seed=11, store_path=str(public_db))
    second = run_swarm("C-001", seed=11, store_path=str(public_db))

    conn = connect(public_db)
    try:
        rows = conn.execute(
            "SELECT amount_vnd FROM refund_ledger WHERE claim_id = 'C-001'"
        ).fetchall()
        audits = committed_audit_count(conn, "C-001")
    finally:
        conn.close()

    assert first.status == "resolved"
    assert second.status == "resolved"
    assert len(rows) == 1
    assert int(rows[0]["amount_vnd"]) == 35000
    assert audits == 1


def test_swarm_crash_after_effect_and_resume(public_db: Path) -> None:
    """Crash sau khi ghi effect nhưng trước checkpoint, resume lại không ghi trùng."""
    with pytest.raises(InjectedCrash):
        run_swarm(
            "C-001",
            seed=11,
            store_path=str(public_db),
            crash_at="after_effect_before_checkpoint",
        )

    resumed = run_swarm("C-001", seed=11, store_path=str(public_db))

    conn = connect(public_db)
    try:
        rows = conn.execute(
            "SELECT amount_vnd FROM refund_ledger WHERE claim_id = 'C-001'"
        ).fetchall()
        audits = committed_audit_count(conn, "C-001")
    finally:
        conn.close()

    assert resumed.status == "resolved"
    assert len(rows) == 1
    assert audits == 1


def test_swarm_trace_contract_and_no_canary_leak(public_db: Path) -> None:
    """Trace phải tồn tại, khớp run_id và không chứa CANARY_SECRET."""
    res = run_swarm("C-001", seed=11, store_path=str(public_db))
    trace_file = Path(res.trace_path)
    assert trace_file.exists()

    raw = trace_file.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert data["run_id"] == res.run_id
    assert isinstance(data["events"], list)
    assert "CANARY_SECRET" not in raw