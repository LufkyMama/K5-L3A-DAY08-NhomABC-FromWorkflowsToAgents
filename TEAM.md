# Team

## Thông tin nhóm

- Tên nhóm: Nhóm ABC
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-NhomABC-FromWorkflowsToAgents`
- URL repo: https://github.com/LufkyMama/K5-L3A-DAY08-NhomABC-FromWorkflowsToAgents
- Nhánh nộp: `main`
- Commit chốt: bb908c6

## Thành viên

Mỗi thành viên tự điền **Họ tên, MSSV, Email, GitHub** của mình; giữ nguyên vai trò đã chia.

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Bùi Thế Anh | 2A202603546 | theanh7888189@gmail.com | theahASR | Workflow + tích hợp |
|   2 | Vũ Đức Thắng | 2A202603601 | thangvu130604@gmail.com |VUDUCTHANG130604 |  Single agent |
|   3 | Vũ Nguyễn Hoàng Minh       |     2A202603541 |minhhoang6724@gmail.com       |LufkyMama        | Orchestrator + bảo mật |
|   4 | Nguyễn Khánh Duy | 2A202603575 | duynguyen77621@gmail.com | ZuyNoNguyen | Kiểm thử + đánh giá |



## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Bùi Thế Anh | Workflow + tích hợp | `e273e3b` CP2; `1498012` CP3; `fc8633e` CP4 + benchmark; `972f86a` CP5 báo cáo; `2d8f39b` merge | `src/tests/test_workflow_shape.py` (44 test: quote, PII, crash, retry, conflict, approval, trần tiền) |
| Vũ Đức Thắng | Single agent; retry/crash; phân tích cost | `ab296cf` triển khai Single và test; `9a1e3d2` bổ sung retry/crash và benchmark Single–swarm | `src/tests/test_single_agent.py`: crash ba thời điểm, retry cùng/khác seed, quote conflict, ticket injection, trace, step cap và model budget |
| Vũ Nguyễn Hoàng Minh | Orchestrator + bảo mật (handoff, trace, secret/PII) | `8cd902c` submit cp2, cp3 (shape orchestrator + test); `1e27b2b` submit cp4, cp5 (audit bảo mật 3 shape, mục 3.C báo cáo) | `src/tests/test_orchestrator_handoff.py` (16 test: handoff allowlist, trace không lộ secret, không tin delay ticket); `src/tests/test_trace_privacy_all_shapes.py` (7 test: quét PII/secret thật trên 3 shape) |
| Nguyễn Khánh Duy | Kiểm thử + đánh giá (crash, benchmark, ADR, research card) | `bb908c6` feat(eval): test biên, crash.json, benchmark.json, ADR, research card | `src/tests/test_member4_edge_cases.py` (3 test: idempotent retry, crash/resume, trace & không lộ CANARY_SECRET) |

### Bằng chứng phần Bùi Thế Anh

- CP1: cài Python 3.13.9 + venv trong `src/`; `python -m lab8.smoke` → `lab8.smoke pass`; baseline host **54 passed**, student **186 failed / 62 passed**; viết mục **Quy ước ghép code (CP1)** trong `TEAM.md`.
- CP2: hoàn thiện `src/lab8/shapes/workflow.py` theo contract (tiền do `compute_compensation`, host là cửa ghi duy nhất, trace sạch); **62/62** test student workflow pass; thêm 9 test đầu trong `src/tests/test_workflow_shape.py`.
- CP3: thêm 3 test retry/crash (crash trước khi ghi, retry cùng số tiền, retry quote thay đổi); crash suite **20/20**; T11/T12 xanh trên cả 4 shape; kiểm handoff orchestrator không lộ secret/PII.
- CP4: test approval thiếu / mượn claim khác / bị thu hồi / thấp hơn quote; trần theo đơn T13–T14; quét secret/PII trên **14 claim**; crash **20/20**.
- CP5: benchmark 4 shape × 14 claim × 5 seed; workflow **pass 1.000, pass^5 1.000, variance 0, cost/success 27.86 VND**; tổng hợp `group_report.md`; `check_submission` **0 FAIL, 0 WARN**.
- Commit: `e273e3b`, `1498012`, `fc8633e`, `972f86a`, `2d8f39b`. Báo cáo cá nhân: [2A202603546_BuiTheAnh.md](report/team/2A202603546_BuiTheAnh.md).

### Bằng chứng phần Vũ Đức Thắng

- CP1: đọc `src/lab8/runtime.py` và `src/lab8/mock_llm.py`; smoke đã chạy pass trong phiên kiểm chứng với Codex.
- CP2: `single.py` chạy ReAct tối đa 8 bước với tool chỉ đọc; code tính quote, host ghi refund; 62/62 test public Single pass.
- CP3: 10/10 test bổ sung Single pass, gồm ba cửa sổ crash, retry không ghi trùng và bảo toàn refund đã commit khi quote thay đổi.
- CP4 — approval: [test_single_approval.py](src/tests/test_single_approval.py) đạt 55/55 test: 10 tình huống approval không hợp lệ × 5 seed đều không ghi refund; 5 trial approval hợp lệ vẫn hoàn đúng tiền. Số trial bypass quan sát được là 0/50 trial không hợp lệ; mọi nhánh bị chặn có audit `policy_denied`.
- Phân tích cost: [single_cost_analysis.md](report/team/single_cost_analysis.md); [report đo Single–swarm](src/reports/benchmark_single_cost.json). Single pass 70/70 trial public; cost per success mô phỏng 37,68 VND.
- Lệnh kiểm riêng Single trong `src/`: `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"`. Bộ lọc này tránh chọn test của shape khác qua tên hàm `test_public_single_run_cases`.
- Các hash trên là commit chứa phần Single, có Git author `VUDUCTHANG130604`. Báo cáo cá nhân: [2A202603601_VuDucThang.md](report/team/2A202603601_VuDucThang.md).

### Bằng chứng phần Vũ Nguyễn Hoàng Minh

- CP1: đọc `src/lab8/handoff.py`, mục Trace contract v1 trong `docs/contracts.md`, `src/lab8/shapes/swarm_reference.py`; smoke pass, host **54 passed**, student **186 failed / 62 passed** (Python 3.13.17).
- CP2: hoàn thiện `src/lab8/shapes/orchestrator.py`: đọc claim qua `get_claim_view` (không thấy `parent_secret`), handoff bằng `make_handoff` với `facts={}` và 4 tool chỉ đọc, tiền từ `compute_compensation` trên order row (bỏ qua delay trong ticket), truyền quote đầy đủ vào `issue_refund`, mọi nhánh return đi qua `finish()`; **62/62** test student orchestrator pass.
- CP3: truyền `crash_at` vào `durability.issue_refund`, ghi trace rồi `raise` lại `InjectedCrash`; T11, T12 xanh. Thêm [test_orchestrator_handoff.py](src/tests/test_orchestrator_handoff.py) (16 test), C-002 pass trên cả 5 seed (swarm fail ở seed 55).
- CP4 — bảo mật: thêm [test_trace_privacy_all_shapes.py](src/tests/test_trace_privacy_all_shapes.py) quét trace, `RunResult` và stdout của workflow, single, orchestrator trên 14 claim × seed 11, 55 theo **giá trị thật** của SĐT, địa chỉ, ghi chú nội bộ, tên hàng, `parent_secret` và marker `CANARY_*`: **0 rò rỉ**. Rà 3 shape: `issue_refund` chỉ gọi một chỗ mỗi shape, không có `append_audit`/SQL ghi/`print`; investigator chỉ nhận `READONLY_TOOLS`. Ma trận student 3 shape nhóm viết **186 passed**; crash **20/20**. Sửa trace orchestrator ghi đúng `refund_count`, `refunded_vnd`, `clause_ids`.
- CP5: viết mục **3.C Orchestrator, handoff và bảo mật** trong [group_report.md](report/team/group_report.md) (luồng shape C, bảng ranh giới bảo mật, trace mẫu `R-orchestrator-C-014-s11`). Trong [benchmark.json](src/reports/benchmark.json), orchestrator **pass 1.000, pass^5 1.000, variance 0, cost/success 57.19 VND, mean steps 4.71**.
- Commit: `8cd902c`, `1e27b2b` (GitHub `LufkyMama`). Báo cáo cá nhân: [2A202603541_VuNguyenHoangMinh.md](report/team/2A202603541_VuNguyenHoangMinh.md).

### Bằng chứng phần Nguyễn Khánh Duy

- CP1–CP2: đọc `docs/business_rules.md`, `docs/metrics.md`, `src/lab8/durability.py`, `src/lab8/policy.py`; chạy kiểm tra starter và bổ sung file test [test_member4_edge_cases.py](src/tests/test_member4_edge_cases.py) (3 test: idempotent retry, crash/resume `after_effect_before_checkpoint`, trace contract & không lộ `CANARY_SECRET`).
- CP3–CP4: kiểm tra chéo toàn bộ hệ thống sau khi ghép 3 shape (`workflow`, `single`, `orchestrator`):
  - Cổng host `python -m pytest -q`: **95 passed, 248 deselected**.
  - Ma trận student `python -m pytest -q -m student -o addopts=`: **248 passed, 95 deselected** (cả 4 shape đạt 62/62 test).
  - Crash suite `python -m lab8.crash_test --count 20 --out reports/crash.json`: **`20/20`** ([crash.json](src/reports/crash.json)).
- CP5 — benchmark & báo cáo: chạy `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` ([benchmark.json](src/reports/benchmark.json)), hoàn thiện [decision_adr.md](report/team/decision_adr.md) (chọn `workflow`: pass `1.000`, pass^5 `1.000`, variance `0.000000`, cost/success `27.86` VND) và [research_card.md](report/team/research_card.md) (câu R2 & kết quả ablation).
- Commit dẫn chứng: `bb908c6` (GitHub `ZuyNoNguyen`). Báo cáo cá nhân: [2A202603575_NguyenKhanhDuy.md](report/team/2A202603575_NguyenKhanhDuy.md).
