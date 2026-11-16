# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

...

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

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
