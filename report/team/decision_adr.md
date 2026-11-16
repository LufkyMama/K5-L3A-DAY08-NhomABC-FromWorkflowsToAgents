# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn:
- Commit hash:
- Run id dẫn chứng:
- Pass rate / pass^5 / seed min-max / variance:
- Cost per success (mô phỏng, VND):
- Crash safety:
- Secret leak / approval bypass:

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Viết 1 đoạn. So cùng corpus và cùng seed, không so với một lần chạy lẻ.

### Dữ liệu Single do Người 2 bàn giao

Trên 14 claim public × 5 seed cố định, Single đạt 70/70 trial pass, pass^5 = 1, seed min–max = 1–1, variance = 0 và cost per success mô phỏng 37,68 VND. Swarm tham chiếu trên cùng phép đo đạt 69/70 trial pass và cost per success 49,57 VND; Single thấp hơn 23,99%. Nguồn: [benchmark_single_cost.json](../../src/reports/benchmark_single_cost.json), run id minh họa `R-single-C-001-s11`; code và report đã có trong commit `9a1e3d2`.

Đây là dữ liệu phục vụ quyết định chung. Nhóm cần đối chiếu thêm workflow, orchestrator, crash suite và kết quả hidden nếu có trước khi điền các dòng nhãn quyết định ở đầu file.

## Có đáng đổi lấy multi-agent không

Nếu pass nhỉnh hơn mà cost và variance cao hơn, nhóm giữ hay đổi? Điều kiện nào làm quyết định đảo lại?

## Trace và bằng chứng

Trace của nhóm ghi những event nào? Field nào cố ý **không** ghi, và vì sao? Nếu trace nằm ngoài chỗ scanner quét được, đội security chứng minh thế nào là hệ thống không lộ secret?

Single ghi các event `claim`, `read_tool`, `order_scope`, `policy`, `quote`, `refund_attempt`, `refund_outcome`, `decision`. Trace có `run_id` tương ứng `RunResult`, ghi trong `src/traces/` khi chạy từ `src/`; `finish()` ghi trace trên các nhánh return. Trước khi gọi host ghi tiền, trace được lưu với `refund_attempt`, vì vậy crash không để lại trace cũ được hiểu nhầm là lần chạy hiện tại. Event attempt không xác nhận tiền đã commit.

Single không ghi ticket, `parent_secret`, raw headers hoặc order row thô; trace chỉ giữ dữ kiện đã chọn lọc. `test_single_ticket_cannot_override_delay_or_leak_into_trace` kiểm ticket có canary/chỉ dẫn giả vẫn bị từ chối đúng và không đưa canary vào trace/kết quả. Kết quả evaluator của 70 trial public đều pass bao gồm kiểm trace và chuỗi cấm; chưa xác nhận các cổng hidden chưa chạy.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
