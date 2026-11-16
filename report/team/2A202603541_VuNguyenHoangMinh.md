# Báo cáo cá nhân — 2A202603541_VuNguyenHoangMinh

## 1. Thông tin thành viên

- Họ tên: Vũ Nguyễn Hoàng Minh
- MSSV: 2A202603541
- Email: minhhoang6724@gmail.com
- GitHub: LufkyMama

## 2. Phần việc phụ trách

Người 3 — Orchestrator + bảo mật:

- Shape C `src/lab8/shapes/orchestrator.py` (CP2, CP3).
- Rà secret/PII và quyền investigator trên cả ba shape nhóm viết (CP4).
- Phần handoff, trace, bảo mật trong `report/team/group_report.md` (mục 3.C, CP5).

## 3. Đóng góp cụ thể

- `8cd902c` — submit cp2, cp3: viết shape orchestrator và `src/tests/test_orchestrator_handoff.py`.
- Commit CP4/CP5 (xem bảng đóng góp trong `TEAM.md`): sửa tên field trong trace (`refund_count`, `refunded_vnd`, `clause_ids`), thêm `src/tests/test_trace_privacy_all_shapes.py`, viết mục 3.C báo cáo nhóm.

Quyết định kỹ thuật:

- Handoff dùng `facts={}`: investigator tự đọc DB theo phạm vi principal, orchestrator không chuyển dữ liệu claim nào qua ranh giới. Ít field hơn thì ít chỗ rò hơn.
- Bỏ điểm yếu của swarm: không bao giờ lấy delay từ ticket. Tiền chỉ từ `compute_compensation` trên order row.
- Trace chỉ ghi field tóm tắt đã chọn, không ghi order/claim row, kể cả khi debug.
- Test bảo mật so với **giá trị thật** của PII trong world state thay vì chỉ marker `CANARY_*`, để bắt được cả SĐT/địa chỉ bị copy nhầm.

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k orchestrator` → 62 passed (gồm T11, T12).
- `python -m pytest -q tests/test_orchestrator_handoff.py` → 16 passed.
- `python -m pytest -q tests/test_trace_privacy_all_shapes.py` → 7 passed (3 shape × seed 11, 55, 0 rò rỉ).
- Benchmark thử orchestrator trên bộ public, seed 11–55: pass 1.000, pass^5 1.000, variance 0 (swarm cùng điều kiện: 0.986). Số chính thức nằm trong `src/reports/benchmark.json` do Người 4 chạy.
- Trace mẫu: `R-orchestrator-C-014-s11` (trích trong mục 3.C báo cáo nhóm).

## 5. Công cụ AI đã dùng

Claude Code: đọc starter, gợi ý cấu trúc shape dựa trên `swarm_reference.py`, viết test bảo mật. Tự kiểm tra bằng cách chạy ma trận student, cổng host, crash suite và đọc trực tiếp file trace để xác nhận không có PII.

## 6. Tự đánh giá

- Shape C qua đủ 62 test student và không phụ thuộc seed.
- Hạn chế: MockLLM không phản ánh model thật; bước `plan` hiện chỉ đọc ticket, chưa thực sự định tuyến investigator theo nội dung ticket.
