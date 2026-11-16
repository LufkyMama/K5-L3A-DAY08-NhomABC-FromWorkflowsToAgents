# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash:
- Run id dẫn chứng: R-workflow-C-001-s11 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

So sánh trên cùng tập 14 claim public (`data/public_claims.jsonl`) và 5 seed (`11, 22, 33, 44, 55`) trong `src/reports/benchmark.json`, cả ba shape `workflow`, `single`, `orchestrator` đều đạt pass rate `1.000` (`70/70`), pass^5 `1.000` và seed variance `0.000000`, vượt trội so với `swarm` (`0.986` / `0.929` / `0.000816`). Nhóm chọn `workflow` vì đây là kiến trúc **ít tự chủ nhất** nhưng đáp ứng trọn vẹn bài toán, không gọi `MockLLM` để suy luận tool nên có chi phí mô phỏng thấp nhất (`27.86` VND/success, so với `37.68` của `single` và `57.19` của `orchestrator`) và số bước trung bình thấp (`3.79` steps, p95 `4.0`).

## Có đáng đổi lấy multi-agent không

Không đáng đổi trong phạm vi bài toán LogiX-VN hiện tại: `orchestrator` tốn chi phí gấp hơn 2 lần `workflow` (`57.19` vs `27.86` VND/success) nhưng không cải thiện thêm pass rate trên tập kiểm thử; `swarm` thậm chí có variance khác 0 (`0.000816`) và tốn `49.57` VND/success. Quyết định này chỉ đảo lại khi bài toán phát sinh dữ liệu đầu vào phi cấu trúc (ví dụ cần phân loại/trích xuất thông tin từ văn bản tự do chưa chuẩn hóa) mà luồng tất định không xử lý được, khiến pass rate của `workflow` tụt xuống dưới ngưỡng hoặc thấp hơn đáng kể so với `single`/`orchestrator`.

## Trace và bằng chứng

Trace của `workflow` ghi các event theo chuẩn v1: `claim_view` (chỉ các field allowlist `found`, `claim_id`, `order_id`), `order_view`, `quote`, `crash` (khi có `InjectedCrash`), và `decision`. Nhóm cố ý **không** ghi nguyên văn `ticket`, `parent_secret`, `raw_headers_json`, SĐT, địa chỉ, tên hàng hay ghi chú nội bộ vào trace hoặc stdout. Nếu trace nằm ngoài vùng quét tự động, tính an toàn vẫn được kiểm chứng bằng cách chỉ truyền dữ liệu qua `get_claim_view` / `lookup_order` (allowlist ở tầng host) và các test tự động kiểm tra không xuất hiện `CANARY_SECRET_*` hay PII trong output và file trace.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
