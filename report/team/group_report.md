# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

Người 2 phụ trách Single agent: đọc runtime và MockLLM ở CP1; triển khai `single.py` ở CP2; hoàn thiện retry/crash ở CP3; bàn giao kiểm thử, phân tích chi phí và giới hạn của phép đo cho nhóm ở CP4–CP5.

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

...

### Single agent — Người 2

Code lấy claim qua `get_claim_view`, trả `failed` khi claim không tồn tại và `needs_info` khi thiếu `order_id`. Vòng `run_react(max_steps=8, worker=True)` dùng `decide` chọn `lookup_order`, kiểm tra phạm vi principal, đọc policy rồi kết thúc. Không thấy đơn hoặc không có quyền xem đơn thì trả `escalated`.

Sau vòng đọc, `compute_compensation` tính tiền từ order view đã kiểm tra quyền và policy hiện hành. Ticket không được dùng để sửa số ngày trễ hay bỏ qua policy. Quote bằng 0 trả `denied`; quote dương được truyền đầy đủ vào `issue_refund`. Host kiểm approval, trần theo đơn, idempotency và ghi ledger. Kết quả trả bằng `finish()` để khớp ledger và trace contract.

MockLLM không có API tool-call có cấu trúc: `decide` là bộ điều phối bằng Python, gọi `complete` mỗi lượt để ghi nhận usage mô phỏng. Văn bản model không quyết định tool hoặc số tiền. Trace chỉ ghi các event `claim`, `read_tool`, `order_scope`, `policy`, `quote`, `refund_attempt`, `refund_outcome`, `decision`; không ghi ticket, secret, header hay order row thô.

Khi crash, `crash_at` được truyền nguyên vào host và `InjectedCrash` truyền ra ngoài. `refund_attempt` được lưu trước thao tác ghi; kết nối luôn đóng trong `finally`. Resume trên cùng DB với cùng claim, không truyền `crash_at`; host dùng khóa `refund:{claim_id}`, độc lập với seed, để giữ một refund và một audit committed.

### 3.C Orchestrator, handoff và bảo mật (Người 3)

**Luồng của shape C** (`src/lab8/shapes/orchestrator.py`):

1. Orchestrator đọc claim qua `get_claim_view`, chỉ lấy `claim_id, principal_id, order_id, ticket`, nên không bao giờ thấy `parent_secret` hay `raw_headers`.
2. Một lời gọi MockLLM `plan` đọc ticket. Ticket là dữ liệu người dùng: kế hoạch không được đặt số tiền hay số ngày trễ.
3. Thiếu `order_id` → `needs_info`, không ghi ledger.
4. Dựng handoff bằng `make_handoff` với `facts={}` và 4 tool chỉ đọc: `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`. Investigator không có registry ghi; `make_handoff` từ chối mọi tool ngoài `READONLY_TOOLS`.
5. `run_readonly_investigators` chạy tool theo phạm vi principal. Order không thuộc principal hoặc không tồn tại → `escalated`.
6. Tiền lấy từ `compute_compensation` trên order row trong DB. Delay ghi trong ticket bị bỏ qua, nên không mắc điểm yếu seed 55 của swarm (T02).
7. Quote ≤ 0 → `denied`, không gọi host. Quote > 0 → `durability.issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=crash_at)`; host kiểm approval, trần theo đơn, idempotency. `InjectedCrash` được ghi trace rồi `raise` lại.

**Ranh giới bảo mật:**

| Rủi ro | Cách chặn | Ai chặn |
| --- | --- | --- |
| Secret của parent đi qua handoff | Allowlist `ALLOWED_FIELDS` / `FACT_KEYS`, `sanitize` từ chối `CANARY_SECRET_`, `parent_secret`, `raw_headers` | Code (`lab8.handoff`) |
| Investigator ghi tiền | Chỉ nhận tool trong `READONLY_TOOLS`; `issue_refund` chỉ gọi ở orchestrator sau khi có quote | Code |
| PII (SĐT, địa chỉ, ghi chú nội bộ, tên hàng) vào trace | Trace chỉ ghi handoff đã sanitize và các field tóm tắt (`order_visible`, `refund_count`, `amount_vnd`, `clause_ids`); không ghi claim row hay order row | Code của shape |
| Ticket nói sai số ngày / "chưa nhận tiền" | Không đọc số từ ticket; tiền do `compute_compensation`, trần do host | Code + host |

Tóm tắt bằng LLM không được dùng làm redaction; chỉ allowlist trong code mới là ranh giới.

**Event trong trace** (ví dụ `R-orchestrator-C-014-s11`, T14 đơn đã hoàn 30.000): `claim` → `handoff` (đã sanitize) → `investigator` (`refund_count: 1`, `refunded_vnd: 30000`) → `quote` (`amount_vnd: 150000`, `clause_ids: [SHIP-LATE-03, DMG-04]`) → `decision` (`resolved`). Host tự trừ phần đã hoàn và ghi ledger 120.000.

**Bằng chứng kiểm tra bảo mật (CP4):**

- `src/tests/test_trace_privacy_all_shapes.py`: chạy workflow, single, orchestrator trên 14 claim public × seed 11 và 55; quét trace, `RunResult` và stdout theo **giá trị thật** của SĐT, địa chỉ, ghi chú nội bộ, tên hàng, `parent_secret`, cùng các marker `CANARY_*`. Kết quả: 0 rò rỉ.
- `src/tests/test_orchestrator_handoff.py`: handoff trong trace chỉ có field allowlist và tool chỉ đọc; trace mọi claim không có secret; C-002 pass trên cả 5 seed.
- Ma trận student cho ba shape nhóm viết (`-k "not swarm"`): 186 passed, gồm các nhánh approval sai claim / hết hạn / thiếu, đơn đã hoàn đủ (T13), trần theo đơn (T14), T11, T12.
- `python -m lab8.crash_test --count 20` → `crash_safety` 20/20.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

...

### Kết quả Single được bàn giao

Nguồn: [benchmark_single_cost.json](../../src/reports/benchmark_single_cost.json), 14 claim × 5 seed `11,22,33,44,55`, mỗi trial một DB mới. Run id minh họa: `R-single-C-001-s11`. Đây là phép đo riêng Single–swarm; bảng bốn shape và crash suite toàn nhóm do phần đánh giá tổng hợp.

| Metric | Single | Swarm tham chiếu |
| --- | ---: | ---: |
| Trial pass | 70/70 | 69/70 |
| Pass rate / pass^5 | 100% / 100% | 98,57% / 92,86% |
| Seed min–max / variance | 100%–100% / 0 | 92,86%–100% / 0,00081633 |
| Cost per success mô phỏng, VND | 37,68 | 49,57 |
| Model / tool call trung bình | 2,7143 / 3,6429 | 3,0000 / 4,6571 |
| Mean / p95 trace events | 7,7143 / 9 | 2,8 / 3 |

Single có tổng cost 2.637,30 VND, trong đó tool chiếm 96,69%; cost per success thấp hơn swarm tham chiếu 23,99%. Success bao gồm từ chối đúng và yêu cầu bổ sung đúng, không chỉ các trial `resolved`. P95 9 event không vi phạm giới hạn 8 lượt ReAct vì benchmark đếm event trace.

Kiểm chứng riêng Single: 62/62 test public và 10/10 test bổ sung pass. Test bổ sung kiểm tra ba cửa sổ crash, retry nhiều seed, trần theo đơn khi replay và conflict khi quote đổi. Kết quả này chưa thay thế crash suite 20/20 của nhóm. Chi tiết cách đo và công thức cost nằm trong [single_cost_analysis.md](single_cost_analysis.md).

Kiểm tra approval bổ sung qua `tests/test_single_approval.py` đạt 55/55 test: 10 tình huống không hợp lệ × 5 seed đều bị chặn, ledger không đổi và có audit `policy_denied` đúng lý do; 5 trial đối chứng hợp lệ vẫn hoàn 35.000 VND. Số trial approval bypass quan sát được là 0/50 trial không hợp lệ. Trường hợp được kiểm gồm thiếu/sai ID, approval thuộc claim khác, hết hạn, revoked/expired/pending, số tiền không dương và approval dự phòng không được claim trỏ tới. Kết quả kiểm tra riêng này chưa phải chỉ số hidden chính thức.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

Với phần Single, lệnh `-k single` còn chọn test của shape khác do tên hàm `test_public_single_run_cases`; dùng bộ lọc `-k "single and not workflow and not orchestrator and not swarm"` để kiểm đúng 62 test của Single. Môi trường `.venv` từng thiếu pytest; các kết quả kiểm chứng được chạy bằng lệnh `python` có sẵn pytest, không tự nhận là đã cài xong dependency trong `.venv`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

Người 2 bàn giao `src/lab8/shapes/single.py`, `src/tests/test_single_agent.py` và phân tích Single/cost. Commit chứa phần kỹ thuật: `ab296cf` và `9a1e3d2`; report đo nằm trong `src/reports/benchmark_single_cost.json`. Công cụ hỗ trợ là Codex; phần AI hỗ trợ triển khai và kiểm chứng được khai trong báo cáo cá nhân.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

Với Single, variance bằng 0 phản ánh điều phối bằng code và backend mô phỏng trong bộ public; chưa chứng minh độ ổn định của LLM thật hoặc pass rate hidden. Chi phí chỉ gồm token/tool được ghi nhận theo bảng giá lab, không phải chi phí vận hành đầy đủ. Benchmark DB mới chưa đo cost của retry/crash. Việc đọc policy ở vòng ReAct rồi đọc lại trong `compute_compensation` là hướng tối ưu chưa thử nghiệm; chưa báo cáo mức tiết kiệm cho thay đổi này.

## 8. Tài liệu tham khảo

...
