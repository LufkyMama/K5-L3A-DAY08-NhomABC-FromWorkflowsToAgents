# Team

## Thông tin nhóm

- Tên nhóm: Nhóm ABC
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-NhomABC-FromWorkflowsToAgents`
- URL repo: https://github.com/LufkyMama/K5-L3A-DAY08-NhomABC-FromWorkflowsToAgents
- Nhánh nộp: `main`
- Commit chốt: (điền ở CP5, trùng `report/team/decision_adr.md`)

## Thành viên

Mỗi thành viên tự điền **Họ tên, MSSV, Email, GitHub** của mình; giữ nguyên vai trò đã chia.

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Bùi Thế Anh | 2A202603546 | theanh7888189@gmail.com | theahASR | Người 1 — Workflow + tích hợp |
|   2 | Vũ Đức Thắng | 2A202603601 | thangvu130604@gmail.com (theo Git author) | Chưa xác nhận | Người 2 — Single agent |
|   3 |        |      |       |        | Người 3 — Orchestrator + bảo mật |
|   4 |        |      |       |        | Người 4 — Kiểm thử + đánh giá |

Người 2 đã xác nhận họ tên và MSSV. Tên Git author của phần Single là `VUDUCTHANG130604`; nhóm bổ sung tài khoản GitHub của Thắng khi xác nhận. Thông tin Hoàng Minh vốn có ở dòng Người 2 được giữ để nhóm cập nhật đúng vị trí: Vũ Nguyễn Hoàng Minh, MSSV `2A202603541`, email `minhhoang6724@gmail.com`, GitHub `LufkyMama`; vai trò đang chờ nhóm xác nhận.


## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Người 1 | Workflow + tích hợp | `e273e3b` feat(workflow) CP2; `1498012` test(workflow) CP3 | `src/tests/test_workflow_shape.py` (12 test: quote, PII, crash, retry, conflict) |
| Vũ Đức Thắng — Người 2 | Single agent; retry/crash; phân tích cost | `ab296cf` triển khai Single và test; `9a1e3d2` bổ sung retry/crash và benchmark Single–swarm | `src/tests/test_single_agent.py`: crash ba thời điểm, retry cùng/khác seed, quote conflict, ticket injection, trace, step cap và model budget |
| | | | |

### Bằng chứng phần Người 2

- CP1: đọc `src/lab8/runtime.py` và `src/lab8/mock_llm.py`; smoke đã chạy pass trong phiên kiểm chứng với Codex.
- CP2: `single.py` chạy ReAct tối đa 8 bước với tool chỉ đọc; code tính quote, host ghi refund; 62/62 test public Single pass.
- CP3: 10/10 test bổ sung Single pass, gồm ba cửa sổ crash, retry không ghi trùng và bảo toàn refund đã commit khi quote thay đổi.
- CP4 — approval: [test_single_approval.py](src/tests/test_single_approval.py) đạt 55/55 test: 10 tình huống approval không hợp lệ × 5 seed đều không ghi refund; 5 trial approval hợp lệ vẫn hoàn đúng tiền. Số trial bypass quan sát được là 0/50 trial không hợp lệ; mọi nhánh bị chặn có audit `policy_denied`.
- Phân tích cost: [single_cost_analysis.md](report/team/single_cost_analysis.md); [report đo Single–swarm](src/reports/benchmark_single_cost.json). Single pass 70/70 trial public; cost per success mô phỏng 37,68 VND.
- Lệnh kiểm riêng Single trong `src/`: `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"`. Bộ lọc này tránh chọn test của shape khác qua tên hàm `test_public_single_run_cases`.
- Các hash trên là commit chứa phần Single, có Git author `VUDUCTHANG130604`. Báo cáo cá nhân: [2A202603601_VuDucThang.md](report/team/2A202603601_VuDucThang.md).

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
