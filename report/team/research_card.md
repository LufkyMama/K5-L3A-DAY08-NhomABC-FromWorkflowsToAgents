# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST (NeurIPS 2025), *Why Do Multi-Agent LLM Systems Fail?* (tài liệu tham khảo slide 68–69, benchmark & failure taxonomy trên hệ thống multi-agent) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi ở hệ thống multi-agent thường bắt nguồn từ việc phối hợp, giao tiếp hoặc kiểm chứng thông tin giữa các agent hơn là lỗi cú pháp đơn lẻ. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Đo trên tập claim tổng hợp LogiX-VN (`public_claims.jsonl`, 14 claim) với `MockLLM`, bộ seed `11,22,33,44,55`, không phản ánh độ trễ và hành vi của LLM thương mại thực tế. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi chuyển từ `swarm` sang các kiến trúc kiểm soát chặt nguồn sự thật (`workflow`, `single`, `orchestrator`), lỗi tin ticket thay vì DB ở seed 55 (T02) sẽ biến mất: pass rate tăng từ ~0.986 lên 1.000, pass^5 tăng từ ~0.929 lên 1.000, seed variance giảm về 0. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: `MockLLM`, tập tools, bộ seed `11,22,33,44,55`, corpus `data/public_claims.jsonl`, bảng giá `config/pricing.yaml`, evaluator. Biến duy nhất được thay đổi: Topology/Shape (`workflow`, `single`, `orchestrator`, `swarm`). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi kiểm chứng/lệch nguồn sự thật (tin số ngày trễ trong ticket thay vì cột `delay_days` ở order row); đo bằng `pass_rate`, `pass^5`, `seed_variance` và `cost_per_success_vnd`. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json` (mẫu `R-workflow-C-001-s11`, `R-swarm-C-002-s55`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Trên cùng 14 claim × 5 seed (70 trial/shape): `swarm` đạt pass rate `0.986` (`69/70`), pass^5 `0.929`, variance `0.000816`, cost/success `49.57` VND (fail 1 trial ở seed 55 với lỗi `status resolved != denied`). Trong khi đó `workflow`, `single` và `orchestrator` đều đạt pass rate `1.000` (`70/70`), pass^5 `1.000`, variance `0.000000`, với cost/success lần lượt là `27.86`, `37.68` và `57.19` VND.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
