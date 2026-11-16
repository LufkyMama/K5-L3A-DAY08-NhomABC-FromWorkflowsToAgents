# Báo cáo cá nhân — 2A202603575_NguyenKhanhDuy

## 1. Thông tin thành viên

- Họ tên: Nguyễn Khánh Duy
- MSSV: 2A202603575
- Email: duynguyen77621@gmail.com
- GitHub: ZuyNoNguyen

## 2. Phần việc phụ trách

- **Vai trò:** Người 4 — Kiểm thử + đánh giá (Ledger, crash, benchmark, ADR & research card).
- Kiểm tra chéo hệ thống test cho cả 4 kiến trúc (`workflow`, `single`, `orchestrator`, `swarm`).
- Viết test bổ sung kiểm tra tính idempotent, crash/resume và trace contract.
- Chạy crash suite, benchmark 4 shape × 5 seed và tổng hợp số liệu vào `decision_adr.md`, `research_card.md`.

## 3. Đóng góp cụ thể

- Bổ sung file test `src/tests/test_member4_edge_cases.py` với 3 test case:
  - `test_swarm_retry_same_claim_is_idempotent`: kiểm tra gọi lại cùng claim chỉ ghi đúng 1 dòng `refund_ledger` và 1 audit `refund_committed`.
  - `test_swarm_crash_after_effect_and_resume`: kiểm tra crash tại `after_effect_before_checkpoint` và resume lại không tạo refund trùng.
  - `test_swarm_trace_contract_and_no_canary_leak`: kiểm tra trace tồn tại, khớp `run_id` và không lộ `CANARY_SECRET`.
- Chạy kiểm tra toàn bộ cổng host (`python -m pytest -q`) và ma trận student (`python -m pytest -q -m student -o addopts=`).
- Chạy `lab8.crash_test` tạo `src/reports/crash.json` (`20/20`) và `lab8.benchmark` tạo `src/reports/benchmark.json` (4 shape × 14 claim × 5 seed).
- Điền số liệu thực nghiệm và phân tích vào `report/team/decision_adr.md` và `report/team/research_card.md`.

## 4. Bằng chứng

- File test đã thêm: `src/tests/test_member4_edge_cases.py`.
- Kết quả chạy test:
  - `python -m pytest -q`: `95 passed, 248 deselected`.
  - `python -m pytest -q -m student -o addopts=`: `248 passed, 95 deselected`.
- Kết quả crash suite (`src/reports/crash.json`): `crash_safety = 20/20`.
- Kết quả benchmark (`src/reports/benchmark.json`, `run_id` mẫu `R-workflow-C-001-s11`):
  - `workflow`: pass `1.000`, pass^5 `1.000`, variance `0.000000`, cost/success `27.86` VND, mean steps `3.79`.
  - `single`: pass `1.000`, pass^5 `1.000`, variance `0.000000`, cost/success `37.68` VND, mean steps `7.71`.
  - `orchestrator`: pass `1.000`, pass^5 `1.000`, variance `0.000000`, cost/success `57.19` VND, mean steps `4.71`.
  - `swarm`: pass `0.986`, pass^5 `0.929`, variance `0.000816`, cost/success `49.57` VND, mean steps `2.80`.
- Commit hash: [điền mã commit sau khi push]

## 5. Công cụ AI đã dùng

- Dùng trợ lý AI (Antigravity) để gợi ý cấu trúc test biên (`test_member4_edge_cases.py`) và tổng hợp số liệu báo cáo.
- Đã tự chạy lại toàn bộ lệnh `pytest`, `lab8.crash_test`, `lab8.benchmark` trong `.venv` trên máy cá nhân và đối chiếu trực tiếp kết quả với `src/reports/benchmark.json` và `src/reports/crash.json`.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các đầu việc được phân công từ CP1 đến CP5, đảm bảo 3 điều kiện must-pass và giữ bộ test cổng host + ma trận student xanh hoàn toàn.
