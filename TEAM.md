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
|   2 | Vũ Nguyễn Hoàng Minh | 2A202603541 | minhhoang6724@gmail.com | lufkymama | Người 2 — Single agent |
|   3 |        |      |       |        | Người 3 — Orchestrator + bảo mật |
|   4 |        |      |       |        | Người 4 — Kiểm thử + đánh giá |

## Quy ước ghép code (CP1)

Thống nhất trước khi viết shape, để bốn người ghép được vào cùng một `main` mà không lệch contract.

### 1. Phạm vi file được sửa

- **Được sửa:** `src/lab8/shapes/workflow.py`, `single.py`, `orchestrator.py`; thêm test trong `src/tests/`; code bonus trong `src/bonus/`.
- **Không sửa (file thước đo):** `src/lab8/metrics.py`, `src/lab8/durability.py`, `src/lab8/policy.py`, `src/config/*.yaml`, `src/data/*`.
- **Không commit:** `.venv/`, `src/traces/`, `src/*.sqlite`, `student_drop/`.
- Không sửa `src/lab8/shapes/__init__.py`; shape bonus đăng ký bằng `--extra-shape` khi chạy benchmark.

### 2. Hợp đồng chung của mọi shape

- Giữ nguyên chữ ký: `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`.
- Trả kết quả bằng `lab8.shapes.common.finish()`; không tự điền `refund_effects` hay `committed_audit_count`.
- `proposal_amount` là **quote đầy đủ** từ `compute_compensation` (số nguyên VND). Truyền đúng quote đầy đủ vào `durability.issue_refund`; host tự trừ phần đơn đã được hoàn (T13, T14).
- Tiền và approval do **code** quyết; model chỉ đọc dữ liệu và soạn câu chữ.
- Ghi trace contract v1 ở **mọi nhánh return** (kể cả `needs_info`, `escalated`, `denied`); `run_id = make_run_id(shape, claim_id, seed)`.
- Không ném exception; truyền `crash_at` thẳng vào `durability.issue_refund` và không bắt `InjectedCrash`.
- Không ghi secret, SĐT, địa chỉ, ghi chú nội bộ, tên hàng vào trace/stdout.

### 3. Quy ước git

- Mỗi người một nhánh: `feat/workflow`, `feat/single`, `feat/orchestrator`, `feat/eval`; mở PR vào `main`, cần ít nhất 1 người review.
- Commit message: `feat(workflow): ...`, `test(workflow): ...`, `docs(team): ...`.
- Mỗi người có ít nhất **1 commit có nội dung** và **1 test đã thêm hoặc sửa** (điều kiện C8).
- Không force-push `main`; không commit file sinh ra (`reports/*.json` chỉ commit khi là bằng chứng CP5).

### 4. Definition of Done cho một shape

- `python -m pytest -q -m student -o addopts= -k <shape>` → **62 passed**.
- `python -m pytest -q` (cổng host) vẫn xanh.
- T11 (gọi lại) và T12 (crash rồi resume) xanh.
- Không lộ `CANARY_SECRET_*`/PII; trace đúng contract v1.

### 5. Lệnh chuẩn (chạy trong `src/`)

```text
python -m lab8.smoke
python -m pytest -q
python -m pytest -q -m student -o addopts=
python -m pytest -q -m student -o addopts= -k workflow
```

### 6. Bằng chứng CP1 trên máy Người 1

- `python -m lab8.smoke` → `lab8.smoke pass` (Python 3.13.9, Windows AMD64).
- `python -m pytest -q` → **54 passed, 248 deselected**, không có `failed`.
- `python -m pytest -q -m student -o addopts=` → **186 failed, 62 passed** (đúng baseline: 62 test swarm xanh, 3 shape stub đỏ).
- Mỗi thành viên còn lại chạy lại 3 lệnh trên ở máy mình và xác nhận trong nhóm trước khi sang CP2.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| | | | |

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
