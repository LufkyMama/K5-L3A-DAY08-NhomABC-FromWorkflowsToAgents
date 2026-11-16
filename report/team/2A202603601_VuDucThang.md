# Báo cáo cá nhân — Vũ Đức Thắng

## 1. Thông tin thành viên

- Họ tên: Vũ Đức Thắng.
- MSSV: 2A202603601.
- Email: `thangvu130604@gmail.com` — theo thông tin tác giả Git của các commit Single.
- Git author: `VUDUCTHANG130604`.
- GitHub: chưa xác nhận tên tài khoản; bổ sung khi nhóm chốt thông tin thành viên.
- Nhóm: Nhóm ABC, lớp L3A.
- Vai trò: Người 2 — Single agent, retry/crash của Single và phân tích chi phí.

## 2. Phần việc phụ trách

| Checkpoint | Phần việc | Sản phẩm / bằng chứng |
| --- | --- | --- |
| CP1 | Đọc runtime và MockLLM; xác định vòng ReAct, giới hạn bước, quyền tool và cách ghi usage | Phân tích `runtime.py`, `mock_llm.py`; smoke đã chạy pass trong phiên làm việc với Codex |
| CP2 | Triển khai Single agent cùng contract `run_claim` | [single.py](../../src/lab8/shapes/single.py); 62/62 test public Single pass |
| CP3 | Hoàn thiện retry/crash; kiểm tra ledger, audit, checkpoint và trace | [test_single_agent.py](../../src/tests/test_single_agent.py); 10 test bổ sung pass |
| CP4 | Bàn giao kiểm thử an toàn của Single cho nhóm | Kiểm thử ticket chứa chỉ dẫn giả, trace, step cap, crash ba thời điểm và 55 test approval |
| CP5 | Phân tích Single và cost; đóng góp nội dung báo cáo chung | [single_cost_analysis.md](single_cost_analysis.md), [group_report.md](group_report.md), dữ liệu Single trong [decision_adr.md](decision_adr.md) |

CP4–CP5 ở đây mô tả phần Single được bàn giao; nhóm còn phải tổng hợp crash suite 20/20, benchmark đủ bốn shape, quyết định kiến trúc và nghiên cứu/ablation chung.

## 3. Đóng góp cụ thể

### 3.1. Triển khai Single agent

`run_claim` đọc claim qua `get_claim_view`; claim không tồn tại trả `failed`, thiếu mã đơn trả `needs_info`. Với claim có mã đơn, vòng `run_react(max_steps=8, worker=True)` dùng `decide` chọn tool chỉ đọc. Agent kiểm tra đơn trong phạm vi principal, đọc policy và dừng. Nếu không thấy đơn hoặc không có quyền truy cập thì trả `escalated`.

Sau vòng lặp, code tính quote bằng `compute_compensation` từ order view đã kiểm tra quyền. Ticket là dữ liệu đầu vào không đáng tin để thay số ngày trễ hoặc bỏ qua policy. Quote bằng 0 trả `denied`; quote dương được truyền đầy đủ vào `durability.issue_refund`. Host chịu trách nhiệm kiểm approval, trần tiền theo đơn, idempotency và thao tác ghi. Kết quả dùng `finish()` để các field refund và audit khớp dữ liệu thật.

MockLLM trả văn bản theo quy tắc và cập nhật Budget. Vì backend này không có API tool-call có cấu trúc, lựa chọn hành động hiện được viết trong `decide` bằng Python dựa trên observation. Văn bản MockLLM không quyết định số tiền hoặc cấp quyền ghi.

### 3.2. Retry, crash và trace

- Truyền nguyên `crash_at` vào host, để `InjectedCrash` truyền ra ngoài.
- Đóng kết nối bằng `finally` ở cả lần chạy bình thường và lần bị ngắt.
- Lưu event `refund_attempt` trước thao tác ghi để lần crash có trace hiện tại. Event này chỉ xác nhận đã thử gọi host.
- Resume bằng cùng claim và cùng file SQLite, bỏ `crash_at`. Host dùng khóa `refund:{claim_id}` nên đổi seed vẫn giữ cùng khóa refund.
- Giữ quote đầy đủ khi retry, kể cả đơn đã có refund lịch sử; host tự tính phần chênh theo trần đơn.
- Quote mới làm số tiền được host chấp nhận khác số đã commit thì trả `failed` với `amount_conflict`, giữ refund và checkpoint cũ.
- Trace ghi dữ kiện được chọn lọc, không ghi ticket, secret, header hay row database thô.

### 3.3. Commit và test

Các commit chứa phần kỹ thuật đã có trong lịch sử repo:

| Commit | Nội dung |
| --- | --- |
| `ab296cf` — `Single agent` | Triển khai Single và các test ban đầu |
| `9a1e3d2` — `update` | Bổ sung trace retry/crash, mở rộng test và lưu report benchmark Single–swarm |

Cả hai commit có Git author `VUDUCTHANG130604`. Tài liệu Markdown được hoàn thiện trong đợt này cần được đưa vào commit tài liệu tiếp theo; không dùng hash của commit code để nhận là đã chứa tài liệu mới.

Các test bổ sung trong `test_single_agent.py`:

| Test | Nội dung kiểm tra |
| --- | --- |
| `test_single_resume_at_each_crash_window` | Ba điểm crash: trước effect, sau effect trước checkpoint, sau checkpoint; kiểm trạng thái bền vững trước và sau resume |
| `test_single_repeated_retries_keep_one_refund_across_seeds` | Retry cùng/khác seed; kiểm cả refund đầy đủ và refund phần chênh |
| `test_single_retry_changed_amount_preserves_committed_refund` | Quote thay đổi sau commit tạo conflict và giữ số đã hoàn |
| `test_single_ticket_cannot_override_delay_or_leak_into_trace` | Ticket chứa canary/chỉ dẫn giả không thay logic tiền và không lọt vào trace/kết quả |
| `test_single_unknown_claim_writes_valid_trace` | Claim không tồn tại trả failed với trace hợp lệ |
| `test_single_step_cap_cannot_commit_refund` | Vòng đọc bị ép chạy hết giới hạn vẫn không ghi refund |
| `test_single_accounts_for_each_model_decision` | Mọi lượt quyết định model được tính usage; hành động không gọi tool ghi |

Bảy hàm test được tham số hóa thành 10 trường hợp kiểm thử.

### 3.4. Kiểm tra approval không hợp lệ

File bổ sung [test_single_approval.py](../../src/tests/test_single_approval.py) kiểm trực tiếp toàn bộ luồng Single tới host với claim có quote dương 35.000 VND. Mỗi trường hợp dùng một DB tạm mới; chỉ dữ liệu trong DB test được thay đổi, không sửa fixture chính thức.

Mười tình huống được kiểm trên năm seed `11,22,33,44,55`: thiếu `approval_id`; ID không tồn tại; approval của claim khác; ngày hết hạn đã qua; trạng thái revoked, expired hoặc pending; số tiền duyệt bằng 0 hoặc âm; approval được claim trỏ tới đã revoked dù có một approval dự phòng valid cho cùng claim.

Kết quả: 50/50 trial không hợp lệ trả `denied`, giữ `proposal_amount=35000`, không ghi thêm ledger, không tạo checkpoint hay audit `refund_committed`, và có audit `policy_denied` đúng lý do. Toàn bộ ledger được so với baseline để phát hiện cả refund ghi dưới claim khác. Năm trial đối chứng với approval hợp lệ trả `resolved`, hoàn 35.000 VND và có đúng một audit committed. Số approval bypass quan sát được là **0/50 trial không hợp lệ**; chưa suy rộng thành kết quả hidden.

Test cũng chạy evaluator `trial_pass` để đối chiếu kết quả, ledger, audit và trace. File test approval được bổ sung trong lượt kiểm này, chưa nằm trong hai commit code đã liệt kê ở trên.

## 4. Bằng chứng và cách tái lập

Các lệnh dưới đây chạy trong `src/`. Kết quả được kiểm chứng trong phiên làm việc có Codex hỗ trợ; thành viên có thể chạy lại trên máy để đối chiếu.

```powershell
python -m lab8.smoke
python -m pytest -q tests/test_single_agent.py
python -m pytest -q tests/test_single_approval.py
python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"
```

- Smoke: `lab8.smoke pass` trong lần kiểm chứng môi trường.
- Test bổ sung Single: **10 passed** trong lần kiểm tra lại phục vụ báo cáo.
- Test approval Single: **55 passed**, gồm 50 trial không hợp lệ bị chặn và 5 trial hợp lệ đối chứng.
- Ma trận public riêng Single: **62 passed** trong lần kiểm tra lại phục vụ báo cáo, gồm T11 retry và T12 crash/resume.
- Bộ lọc cần loại workflow/orchestrator/swarm vì tên hàm `test_public_single_run_cases` cũng chứa chữ `single`.

Lệnh benchmark đã chạy:

```powershell
python -m lab8.benchmark --shapes single,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark_single_cost.json
```

Nguồn số liệu là [benchmark_single_cost.json](../../src/reports/benchmark_single_cost.json), được công cụ sinh và đã lưu trong `9a1e3d2`. Run id minh họa: `R-single-C-001-s11`.

| Chỉ số Single | Kết quả |
| --- | ---: |
| Số trial pass | 70/70 |
| Pass rate / pass^5 | 1 / 1 |
| Seed min–max / variance | 1–1 / 0 |
| Tổng cost mô phỏng | 2.637,30 VND |
| Cost per success | 37,68 VND |
| Model / tool call trung bình mỗi trial | 2,7143 / 3,6429 |
| Mean / p95 trace events | 7,7143 / 9 |

Với bảng giá lab, cost = input token × 0,02 + output token × 0,08 + tool call × 10 VND. Single có 190 model call và 255 tool call trên 70 trial; tool chiếm 96,69% tổng cost. Ví dụ C-001 seed 11 có 21 input token, 12 output token, 4 tool call, tương đương 41,38 VND. Các nhánh kết thúc sớm làm cost trung bình toàn bộ thấp hơn luồng đầy đủ.

So với swarm tham chiếu trên cùng corpus/seed, cost per success của Single thấp hơn 23,99%: 37,68 so với 49,57 VND. Đây là so sánh hai triển khai trong lab, chưa phải kết luận chọn kiến trúc cho cả nhóm. Success được tính theo trial đúng, bao gồm từ chối hoặc yêu cầu bổ sung đúng.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc repo, giải thích runtime/MockLLM, triển khai Single, bổ sung test retry/crash, chạy kiểm chứng, đọc benchmark và soạn bản báo cáo này. Có sử dụng nội dung do AI đề xuất trong code, test và tài liệu; không khai là toàn bộ phần triển khai được viết thủ công.

Cách kiểm chứng trong phiên làm việc: đối chiếu `docs/business_rules.md` và `docs/contracts.md`; chạy smoke, test public Single, test bổ sung; kiểm ledger/audit/checkpoint trực tiếp qua SQLite trong test; lấy số liệu từ report do benchmark sinh. Không sửa host, policy, metric, config hoặc JSON report để đạt kết quả mong muốn.

Thành viên cần tự chạy lại và giải thích được `decide`, giới hạn 8 bước, ranh giới code/model, quote đầy đủ, khóa idempotency và các field trace đã loại. Báo cáo này không tự khẳng định mức độ hiểu hoặc thao tác kiểm tra độc lập của thành viên khi chưa có xác nhận.

## 6. Tự đánh giá theo bằng chứng

Phần kỹ thuật Single đã có sản phẩm triển khai, test và số liệu đối chiếu: 62 test public và 10 test bổ sung pass; retry/crash được kiểm ở ba thời điểm với một refund và một audit committed sau resume. Các thay đổi thuộc phạm vi shape/test, giữ nguyên các file thước đo.

Giới hạn: Single hiện dùng điều phối bằng code với MockLLM; variance bằng 0 trên public chưa chứng minh khả năng của model thật hoặc bộ hidden. Cost là mô phỏng, latency là `unavailable`; benchmark DB mới chưa đo cost khi retry/crash. Lượt đọc policy trùng là hướng tối ưu chưa làm ablation.

Việc còn lại khi nhóm chốt bài: xác nhận tài khoản GitHub, commit tài liệu, ghép benchmark bốn shape và quyết định chung. Nhận xét chủ quan về mức độ hiểu, khó khăn cá nhân và bài học cần do chính thành viên bổ sung sau khi tự đối chiếu; không suy diễn từ kết quả test do Codex chạy.
