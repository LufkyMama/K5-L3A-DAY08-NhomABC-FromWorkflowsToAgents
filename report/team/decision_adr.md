# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: fc8633e
- Run id dẫn chứng: R-workflow-C-001-s11 (benchmark 4 shape × 14 claim × 5 seed, `src/reports/benchmark.json`)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (`src/reports/crash.json`)
- Secret leak / approval bypass: 0 / 0 trên public matrix và test CP4; hidden do giảng viên chấm

## Vì sao shape này

Trên cùng 14 claim public, cùng seed `11,22,33,44,55`, cùng MockLLM, cùng bảng giá và cùng evaluator, workflow đạt **pass rate 1.000, pass^5 1.000, seed variance 0.000000** với **cost/success 27.86 VND** — thấp nhất trong bốn shape. Single và orchestrator cũng đạt 1.000 nhưng cost/success lần lượt là 37.68 và 57.19 VND, tức cao hơn 35% và 105% mà không tăng pass rate. Swarm có pass rate 0.986, pass^5 0.929, variance 0.000816 vì ở seed 55 nó tin số ngày trong ticket thay vì cột `delay_days` (T02: ticket nói 5 ngày, order nói 2 ngày). Vì vậy nhóm chọn **workflow**: kiến trúc ít tự chủ nhất mà vẫn làm đúng toàn bộ public matrix, rẻ nhất và ổn định nhất.

## Có đáng đổi lấy multi-agent không

Không, trên corpus và seed của lab này. Thêm agent không cải thiện pass rate mà chỉ tăng cost/success và số bước: single 37.68 VND / 7.71 bước, orchestrator 57.19 VND / 4.71 bước, so với workflow 27.86 VND / 3.79 bước. Swarm còn làm giảm pass rate và tạo variance. Quyết định sẽ đảo lại nếu: (1) hidden set có nhiều claim cần đọc ticket mơ hồ hoặc hỏi thêm thông tin mà workflow cố định bỏ sót; (2) task có nhiều nhánh song song độc lập để investigator xử lý đồng thời; (3) yêu cầu giải thích/soạn câu trả lời khách hàng trở thành tiêu chí chấm. Khi đó single là bước tăng tự chủ tiếp theo nên thử trước vì rẻ hơn orchestrator.

## Trace và bằng chứng

Trace workflow ghi bốn event: `claim_view` (chỉ `found`, `claim_id`, `order_id`), `order_view` (các field allowlist của `lookup_order`), `quote` (amount, reason, clause_ids, parts) và `decision` (status, reason). Trace **cố ý không ghi**: nội dung ticket, `parent_secret`, `raw_headers`, SĐT, địa chỉ, `internal_note`, `item_name`. Lý do: ticket là dữ liệu người dùng có thể chứa PII hoặc câu injection; trace là một phần của ranh giới bảo mật vì grader quét `trace_path` và mọi file `<run_id>*` cùng thư mục. Mọi file shape ghi ra đều nằm cùng thư mục trace và bắt đầu bằng `run_id`, nên scanner đọc được toàn bộ; không có log nào được ghi ra stdout hay chỗ khác. Test `test_workflow_trace_has_no_forbidden_substrings` chạy toàn bộ 14 claim và quét đúng danh sách `forbid_substrings` của từng claim.

## Giới hạn

MockLLM không phải model sản xuất; latency là `unavailable` và không được bịa từ file replay. Benchmark chỉ chạy 14 claim public × 5 seed; hidden 40 claim × 5 seed do grader riêng của giảng viên chấm. Workflow không gọi model nên kết quả chỉ đo quyết định tiền và trace, không đo chất lượng câu trả lời khách. Không kết luận gì về model thật, task khác hoặc corpus lớn hơn. Không sửa JSON để đủ ngưỡng 0.75.
