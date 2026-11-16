# Phân tích Single agent và chi phí mô phỏng

Phần bàn giao của người phụ trách Single agent cho báo cáo nhóm. Commit `ab296cf` triển khai Single và các test ban đầu; commit `9a1e3d2` chứa phần bổ sung trace retry/crash, test mở rộng và report benchmark dẫn dưới đây. Tại lần đo ban đầu, phần bổ sung còn ở working tree; hiện code và report đã được lưu trong `9a1e3d2`. Khi chốt bài, nhóm cần chạy lại benchmark đủ bốn shape trên code cuối cùng và ghi commit chốt vào ADR.

## 1. Cách đo và bằng chứng

Chạy từ thư mục `src/`:

```powershell
python -m lab8.benchmark --shapes single,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark_single_cost.json
```

- Report gốc: [benchmark_single_cost.json](../../src/reports/benchmark_single_cost.json), do công cụ tạo, không sửa tay.
- Mỗi shape: 14 claim public × 5 seed = 70 trial. Mỗi trial dùng một SQLite mới, không hưởng kết quả refund của trial trước.
- Biến giữ cố định: corpus, seed `11,22,33,44,55`, MockLLM, tool của lab, evaluator, bảng giá và `as_of=2026-11-15`.
- Run id minh họa Single: `R-single-C-001-s11`. Trial swarm sai: `R-swarm-C-002-s55`.
- Report này phục vụ phân tích riêng Single, không thay thế `src/reports/benchmark.json` bắt buộc có đủ bốn shape.
- Kiểm chứng phần Single sau khi ghép code: `python -m pytest -q tests/test_single_agent.py` đạt 10 passed; `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` đạt 62 passed. Các lệnh đều chạy trong `src/`.

## 2. Kiến trúc Single hiện tại

1. Code gọi `get_claim_view`. Claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info` ngay.
2. Chạy `run_react(max_steps=8, worker=True)`. Bộ điều phối `decide` chọn `lookup_order`, quan sát quyền truy cập, rồi chọn `lookup_policy` và kết thúc. Đơn ngoài phạm vi principal trả `escalated`.
3. Sau vòng lặp, code gọi `compute_compensation` trên order view đã kiểm tra quyền. Quote dùng database và policy hiện hành; không lấy số ngày trễ hay chỉ dẫn từ ticket.
4. Quote bằng 0 trả `denied`. Quote dương được truyền đầy đủ vào `issue_refund`; host kiểm approval, áp trần theo đơn và chống ghi trùng.
5. Trace ghi các sự kiện đã chọn lọc. `refund_attempt` được lưu trước lời gọi ghi tiền. Khi host ném `InjectedCrash`, exception truyền ra ngoài và kết nối được đóng trong `finally`.

MockLLM không có API tool-call có cấu trúc. `decide` hiện là bộ điều phối bằng Python dựa trên observation; mỗi lượt gọi `complete` để ghi nhận usage mô phỏng. Văn bản trả về từ MockLLM không quyết định hành động hay số tiền. Vì vậy đây là phép đo triển khai Single trong lab; chưa đánh giá năng lực lập kế hoạch của LLM thật.

## 3. Kết quả đo

| Metric | Single | Swarm tham chiếu |
| --- | ---: | ---: |
| Trial pass / tổng trial | 70/70 | 69/70 |
| Pass rate | 100% | 98,57% |
| Pass^5 | 100% (14/14 claim) | 92,86% (13/14 claim) |
| Seed min–max | 100%–100% | 92,86%–100% |
| Seed variance | 0 | 0,00081633 |
| Tổng chi phí mô phỏng, VND | 2.637,30 | 3.420,12 |
| Cost per success, VND | 37,68 | 49,57 |
| Model call trung bình / trial | 2,7143 | 3,0000 |
| Tool call được ghi nhận trung bình / trial | 3,6429 | 4,6571 |
| Mean / p95 trace events | 7,7143 / 9 | 2,8 / 3 |

Single có cost per success thấp hơn swarm khoảng **23,99%** trong phép đo này. Swarm sai C-002 ở seed 55 vì lấy số ngày trong ticket thay cho dữ kiện đơn hàng; đây là điểm yếu cố ý của bản tham chiếu. Không suy ra từ kết quả này rằng mọi hệ thống swarm đều kém Single.

Success của metric là **trial được evaluator chấm đúng**, bao gồm từ chối đúng, yêu cầu bổ sung đúng và chuyển xử lý đúng. Trong 70 trial của Single chỉ có 35 trial mang trạng thái `resolved`; mẫu số cost per success vẫn là 70.

Mean/p95 steps của benchmark đếm event trong trace, khác số lượt ReAct. Do đó p95 = 9 event vẫn phù hợp giới hạn ReAct 8 bước. Không dùng chênh lệch số event giữa hai shape để kết luận tốc độ chạy: mức chi tiết trace khác nhau và latency được ghi là `unavailable`.

## 4. Công thức và phân rã chi phí

Giá từ `src/config/pricing.yaml`:

- Input: 20 VND / 1.000 token.
- Output: 80 VND / 1.000 token.
- Một tool call được ghi nhận: 10 VND.

```text
Cost = input_tokens × 0,02 + output_tokens × 0,08 + tool_calls × 10
Cost per success = tổng cost của mọi trial / số trial pass
```

Ví dụ chạy mới C-001, seed 11 (`R-single-C-001-s11`): 3 model call, 21 input token, 12 output token và 4 tool call được ghi nhận.

```text
Cost = 21 × 0,02 + 12 × 0,08 + 4 × 10 = 41,38 VND
```

Bốn tool call gồm đọc claim, đọc order, đọc policy và tính compensation. Số tool call này không đếm từng truy vấn SQLite; lời gọi host ghi refund và ghi trace không được tính thêm thành tool call trong triển khai hiện tại. Các truy vấn nội bộ của `compute_compensation` cũng không được tính riêng.

| Nhánh xử lý | Số trial | Model call / trial | Tool call / trial | Cost / trial, VND |
| --- | ---: | ---: | ---: | ---: |
| `needs_info` | 5 | 0 | 1 | 10,00 |
| `escalated` | 5 | 2 | 2 | 20,90 |
| `denied` | 25 | 3 | 4 | 41,38 |
| `resolved` | 35 | 3 | 4 | 41,38 |

Tổng cộng Single có 190 model call và 255 tool call được ghi nhận:

```text
Tool cost = 255 × 10 = 2.550,00 VND
Model cost = 2.637,30 − 2.550,00 = 87,30 VND
Tool chiếm 96,69%; model chiếm 3,31% tổng cost.
Cost per success = 2.637,30 / 70 = 37,675714... VND
```

Các nhánh kết thúc sớm làm chi phí trung bình thấp hơn cost của luồng đầy đủ 41,38 VND. Hai nhánh `denied` và `resolved` có cùng cost vì đều hoàn thành phần đọc và tính quote; cơ chế tính hiện tại không cộng phí riêng cho thao tác host ghi refund.

## 5. Nhận định và hướng cải thiện

- Single ổn định qua năm seed public trong phép đo này vì hành động và tính tiền do code quyết định; MockLLM chỉ thay đổi văn bản mô phỏng. Variance bằng 0 chưa chứng minh độ ổn định khi dùng model thật.
- Không có bằng chứng trong phép đo này rằng Single cần thêm agent. Chưa có số đo workflow và orchestrator trong report này để chọn kiến trúc cuối cùng cho nhóm.
- Có một lượt đọc policy có thể tối ưu: vòng ReAct gọi `lookup_policy`, trong khi `compute_compensation` sau đó lại đọc policy hiện hành bên trong. Có thể nghiên cứu giảm lượt đọc trùng và lượt model tương ứng. Đây là đề xuất chưa triển khai/chưa đo ablation; không ghi nhận thành mức tiết kiệm đã đạt.
- Giữ các nhánh kết thúc sớm và giới hạn 8 lượt; không giảm kiểm tra quyền, approval, idempotency hay trace để giảm cost.
- Retry dùng cùng claim và cùng DB sẽ tránh refund trùng, nhưng vẫn chạy lại phần đọc và model. Benchmark hiện tại dùng DB mới ở mọi trial nên chưa đo tổng cost khi có retry hoặc crash. Độ an toàn retry/crash được kiểm tra riêng trong `tests/test_single_agent.py` và T11/T12.
- Đây là chi phí mô phỏng của MockLLM, không phải hóa đơn API hay chi phí vận hành thực tế. Kết quả public chưa cho biết pass rate hidden; không suy rộng ngoài 14 claim đã đo.

## 6. Đoạn dùng cho báo cáo nhóm

Single agent sử dụng vòng ReAct giới hạn 8 bước với các tool đọc; code tính compensation từ dữ kiện đơn hàng và host chịu trách nhiệm kiểm approval, trần tiền, idempotency cùng ghi refund. Trên 14 claim public với năm seed cố định, Single đạt 70/70 trial pass, pass^5 = 1 và seed variance = 0. Tổng chi phí mô phỏng là 2.637,30 VND, tương đương 37,68 VND cho mỗi trial pass; trung bình 2,71 model call và 3,64 tool call mỗi trial. Chi phí tool chiếm 96,69% tổng cost. So với swarm tham chiếu trên cùng corpus và seed, cost per success thấp hơn 23,99%. Bằng chứng: `src/reports/benchmark_single_cost.json`, run id minh họa `R-single-C-001-s11`. Kết quả chỉ áp dụng cho MockLLM và bộ public; latency là `unavailable`, chưa kết luận về model thật hoặc bộ hidden.
