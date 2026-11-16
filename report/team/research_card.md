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
| CÂU | R1 / R2 / R3 / R4 | R1 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research 2026, *Towards a Science of Scaling Agent Systems* — paper/benchmark, trích theo slide 68–69 của lab; tài liệu lab không cung cấp URL |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hiệu quả của việc thêm agent phụ thuộc vào cấu trúc task; thêm agent không tự động tăng độ chính xác và có thể làm tăng chi phí |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Benchmark của paper với model mạnh và task của họ; lab dùng MockLLM, 14 claim public tuần tự, 5 seed, giá mô phỏng |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Đổi A→C (thêm investigator) giữ pass rate 1.000 nhưng tăng cost/success và số bước |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định MockLLM, tools, seed 11/22/33/44/55, 14 claim public, pricing, evaluator; biến duy nhất là topology A (workflow) vs C (orchestrator) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Dự kiến orchestrator cost/success cao hơn workflow mà pass rate không đổi; đo pass rate, pass^5, variance, cost/success, mean/p95 steps từ `benchmark.json` |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `R-workflow-C-001-s11`, `R-orchestrator-C-001-s11`; `src/reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Workflow: pass 1.000, pass^5 1.000, variance 0.000000, cost/success 27.86 VND, mean 3.79 bước. Orchestrator: pass 1.000, pass^5 1.000, variance 0.000000, cost/success 57.19 VND, mean 4.71 bước. Thêm investigator không tăng pass rate nhưng tăng cost/success khoảng 2.05 lần và số bước khoảng 24%.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
