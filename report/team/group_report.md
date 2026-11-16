# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Nhóm ABC
- Thành viên: xem `TEAM.md`
  - Bùi Thế Anh — 2A202603546 — Người 1 (Workflow + tích hợp)
  - Vũ Nguyễn Hoàng Minh — 2A202603541 — Người 2 (Single agent)
  - Người 3 (Orchestrator + bảo mật) và Người 4 (Kiểm thử + đánh giá): xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `fc8633e`

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán là một quy trình xử lý claim hoàn phí vận chuyển có giao tiền thật trong môi trường giả lập: phải xác định đúng entitlement từ order row và policy hiện hành, kiểm approval, tránh ghi trùng khi retry/crash, không lộ secret/PII, và cuối cùng chọn kiến trúc **ít tự chủ nhất mà vẫn làm được việc** dựa trên số đo.

Cách chia việc bám theo bảng phân vai:

| Người | Phụ trách | Sản phẩm chính |
| --- | --- | --- |
| Người 1 | Shape A workflow + tích hợp | `src/lab8/shapes/workflow.py`, test workflow, `TEAM.md`, ghép bài |
| Người 2 | Shape B single agent | `src/lab8/shapes/single.py`, test single, phân tích cost |
| Người 3 | Shape C orchestrator + bảo mật | `src/lab8/shapes/orchestrator.py`, test handoff/trace |
| Người 4 | Ledger, crash, benchmark | test bổ sung, `benchmark.json`, `crash.json`, ADR |

Thứ tự làm: CP1 cài môi trường và đọc contract; CP2 viết ba shape; CP3 retry/crash/handoff; CP4 rà must-pass; CP5 benchmark và chốt kiến trúc. Nguyên tắc chung: **tiền và approval do code quyết**, model chỉ đọc dữ liệu và soạn câu chữ; `durability.issue_refund` là cửa ghi duy nhất.

## 3. Giải pháp

### Shape A — workflow

Luồng Python cố định, không gọi model. Đọc claim qua `get_claim_view`; thiếu `order_id` trả `needs_info`; `lookup_order` kiểm quyền sở hữu và trả `escalated` nếu ngoài phạm vi; `compute_compensation` tính quote từ order row; quote 0 trả `denied` mà không gọi host; quote dương gọi `issue_refund` với **quote đầy đủ**. Host tự trừ phần đơn đã hoàn và cap theo approval/paid. Trace có bốn event: `claim_view`, `order_view`, `quote`, `decision`.

### Shape B — single agent

Một vòng ReAct tối đa 8 bước bằng `run_react(..., worker=True)`. `decide` gọi MockLLM để mô phỏng bước lập kế hoạch, rồi chỉ chọn tool đọc: `lookup_order` → `lookup_policy`. Sau vòng lặp, code tính quote bằng `compute_compensation` và gọi host. Model không thể gọi `issue_refund` vì runtime chặn write tool cho worker. Trace ghi `claim`, `read_tool`, `order_scope`, `policy`, `quote`, `decision`.

### Shape C — orchestrator

Orchestrator lập kế hoạch, dựng handoff `handoff.v1` bằng `make_handoff` với bốn tool chỉ đọc: `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`. `run_readonly_investigators` chạy các tool này; orchestrator đọc order view và quote, rồi gọi host ghi refund. Handoff chỉ còn các field allowlist; trace ghi handoff đã sanitize, không ghi parent context.

### Shape D — swarm (đối chứng)

Có sẵn trong starter. Swarm gọi thêm model để peer/parse và có điểm yếu cố ý: ở seed chia hết cho 5, nó tin số ngày trong ticket thay vì cột `delay_days`. Nhóm dùng swarm để đo cost và variance, không coi là shape thắng sẵn.

### Ranh giới code / model

| Việc | Ai quyết |
| --- | --- |
| Lọc theo principal, policy hiện hành, trần tiền | Code |
| Đọc ticket mơ hồ, có nên hỏi thêm | Model, trong bound |
| Approval, idempotency, ghi refund | Code, một transaction |
| Trần theo đơn (trừ phần claim trước đã nhận) | Code, đọc lại tổng trong transaction ghi |
| Approval có thuộc đúng claim | Code (`claims.approval_id` → `approvals.claim_id`) |
| Retry sau crash | Ledger + idempotency key `refund:{claim_id}` |

### Trace và bảo mật

Cả ba shape chỉ ghi field đã qua allowlist. Trace **cố ý không ghi**: nội dung ticket, `parent_secret`, `raw_headers`, SĐT, địa chỉ, `internal_note`, `item_name`. Mọi file shape ghi ra nằm cùng thư mục trace và bắt đầu bằng `run_id`, để scanner của grader đọc được toàn bộ. Test `test_workflow_trace_has_no_forbidden_substrings` quét cả 14 claim public.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (14 claim × 5 seed = 70 trial mỗi shape), lấy từ `src/reports/benchmark.json`:

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND) | Mean steps | p95 steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 3.79 | 4.0 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 37.68 | 7.71 | 9.0 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 57.19 | 4.71 | 5.0 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 | 3.0 |

- **Crash safety:** 20/20 (`src/reports/crash.json`).
- **Approval bypass / secret leak:** 0 / 0 trên public matrix và test CP4; hidden do grader riêng của giảng viên chấm.
- **Swarm:** fail đúng một trial `C-002` ở seed 55 (`status resolved != denied`), do tin ticket "trễ 5 ngày" thay vì order row "2 ngày". Đây là variance được giữ lại có chủ đích để so sánh.
- **Hidden self-check:** chưa chạy vì chưa có `student_drop/`; điểm hidden chính thức do giảng viên chấm.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **Windows + pytest:** `python -m pytest -q` ban đầu lỗi `PermissionError` ở `%TEMP%\pytest-of-ThinkPad` (thư mục temp bị khoá quyền, không xoá được). Nhóm trỏ `PYTEST_DEBUG_TEMPROOT` sang một thư mục tạm mới; sau đó cổng host chạy bình thường. Đây là fix riêng của máy, không nằm trong repo.
- **Ghép code đồng thời:** bốn người cùng sửa repo. Nhóm giữ mỗi người một file shape riêng, pull/merge trước khi chạy lại cổng host, và chạy lại toàn bộ ma trận student sau mỗi lần merge để tránh regression.
- **Benchmark và crash suite:** chạy lại từ đầu sau khi merge; không sửa tay JSON trong `src/reports/`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`. Tóm tắt: Người 1 làm workflow + tích hợp + kiểm tra nộp; Người 2 làm single agent; Người 3 làm orchestrator + handoff/trace; Người 4 làm test ledger/crash và benchmark.

## 7. Hạn chế và hướng cải thiện

- MockLLM không phải model sản xuất; latency là `unavailable`, cost là giá mô phỏng chứ không phải hoá đơn API.
- Benchmark chỉ có 14 claim public × 5 seed; hidden 40 claim × 5 seed do giảng viên chấm. Kết luận không nên mở rộng ra ngoài corpus này.
- Workflow không gọi model nên nhóm chưa đo được chất lượng câu trả lời khách; chỉ đo quyết định tiền, trace và cost.
- Hướng cải thiện: chạy hidden self-check khi có `student_drop/`; thử single với model thật để đo trade-off giữa chất lượng câu trả lời và cost; bổ sung claim song song để kiểm tra giả thuyết scaling của R1.

## 8. Tài liệu tham khảo

- `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md` của lab.
- Google Research 2026, *Towards a Science of Scaling Agent Systems* (R1, theo slide 68–69).
- MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* (R2).
- AgentArch, AACL 2026 (R3); EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* (R4).
- Mã nguồn lab trong `src/lab8/`, test trong `src/tests/`, bằng chứng trong `src/reports/`.
