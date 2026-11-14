# Báo cáo Day 7 — Agentic RAG

**Họ tên:** Trần Thái Hưng  **MSSV:** 2A202603557  **Lớp:** K5-L3A  **Bài:** cá nhân (Day 7, Retrieval & Context Engineering)

## Dữ liệu và benchmark

- **Nguồn, quyền sử dụng, số trang và số chunk:** *International Debt Report 2026* (World Bank), chương 1–3, trang PDF 27–134 (103 trang nội dung, trên tổng 280 trang). Giấy phép CC BY 3.0 IGO. Nguồn: <https://hdl.handle.net/10986/45762> (DOI 10.1596/978-1-4648-2355-8). PDF 14 MB nằm ở `data/international-debt-report-2026.pdf` (sha256 được kiểm trong `src/config.py`). Chunk không vượt qua ranh giới trang. Hai index dùng chung corpus, đều tái dùng từ Day 6:
  - **A:** cửa sổ cố định 800 ký tự, overlap 100, **376 chunk**.
  - **B:** gom theo đoạn, tối đa 800 ký tự, **429 chunk**.
- **Vector store, embedding model, phiên bản và số chiều:** PostgreSQL 16 + pgvector 0.8.7 (`pgvector/pgvector:0.8.7-pg16`, Docker Compose, project `day7_retrieval`, `127.0.0.1:55434`, DB `day7_lab`). Tìm kiếm chính xác (không ANN), khoảng cách cosine (`<=>`). Embedding: OpenAI `text-embedding-3-small`, **1536 chiều**. Index lấy từ container Day 6 bằng `pg_dump`/restore; hash `md5(strategy, chunk_id, content_hash, embedding)` của hai DB trùng nhau nên không embed lại. Python 3.14.2, openai 3.51.0, psycopg 3.3.8, pypdf 6.21.4.
- **Agent model, cách chạy và phân chia dev/test:** OpenAI `gpt-4o-mini` (chat completions, tool calling, temperature 0), cấu hình trong `.env` (`AGENT_MODEL`), không commit khóa; mã ở `src/agent.py`, chạy bằng `src/run_agent.py`. Phân chia split:

  | Split | Có đáp án | Thiếu bằng chứng | Ghi chú |
  |---|---:|---:|---|
  | dev | 15 | 2 (`u01`, `u02`) | `q01`–`q15` lấy từ dev Day 6 |
  | test | 11 | 2 (`u03`, `u04`) | **5 câu dùng lại từ Day 6** (`q16`–`q20`) + **6 câu mới** (`s01`–`s04`, `n01`, `n02`) |

  Benchmark đã **đóng băng** (sha256 `5dbe8fe0…54060fa`, ghi ở `benchmark/FROZEN.json`; `run_retrieval` từ chối chạy nếu file đổi). Chi tiết ở [benchmark/README.md](../../benchmark/README.md). Test gồm hai phần và sẽ **báo riêng từng phần (dùng lại / mới) và gộp**. Phần dùng lại đã được chạy ở Day 6 và tác giả đã thấy kết quả, nên không còn độc lập; chỉ 6 câu mới + 2 câu thiếu evidence là chưa từng chạy.
- **Cách xác định câu có/thiếu evidence và tiêu chí chấm:**
  - *Có evidence:* mỗi câu ghi trang gold, câu evidence nguyên văn và `key_facts`; `verify_benchmark` kiểm chuỗi nằm trên trang gold và trong **một** chunk của cả A lẫn B.
  - *Hit* (giữ nguyên Day 6): chunk thuộc trang gold **và** chứa đủ mọi `key_facts` sau khi chuẩn hóa khoảng trắng/gạch nối. Không dùng `evidence in text` của starter vì PDF ngắt dòng làm lệch chuỗi.
  - *Thiếu evidence:* 4 câu gần chủ đề tài liệu; mỗi câu có regex được chạy trên **cả 280 trang PDF** và yêu cầu 0 trang khớp, cộng với đọc thủ công chỗ liên quan. Không dùng top-k để kết luận "không có". Không tính các câu này vào mẫu số retrieval.
  - *Nhãn:* các câu `n01`, `n02`, `u01`–`u04` do **trợ lý AI đề xuất, tác giả duyệt** (AI-proposed, author-reviewed). Nhãn context, grounded, citation và abstention ở test theo thang BENCHMARK.md, ghi ở `results/agent/test/review/review_labels.json`; bảng chấm ẩn tên cấu hình.

## Retrieval và thử nghiệm

Kết quả **dev, n = 15 câu có đáp án**, query là câu hỏi gốc, không filter, top-10, cùng corpus/index/nhãn. Dense = cosine pgvector; BM25 = Okapi (k1 1,5; b 0,75; tự cài, tokenize `\w+`, không stemming); Hybrid = RRF (k = 60) trộn top-20 của dense và BM25. Thời gian là **trung vị mỗi truy vấn** (dense gồm cả gọi API embedding). Chi phí truy vấn embedding của cả lần chạy dev: 389 token ≈ 0,0000078 USD.

| Cấu hình | Phương pháp, top-k, filter, rerank, context budget | Giả thuyết / thay đổi | Split | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Thời gian / chi phí |
|---|---|---|---|---|---|---|---|
| **Baseline** = Dense, index A | cosine, top-10, không filter, không rerank | Hệ thống Day 6; dense A tái hiện đúng số Day 6 | dev | 9/15 (60%) | 12/15 (80%) | — (retrieval riêng, chưa có bước dựng context) | 238 ms |
| Phương pháp 2: BM25, index A | Okapi BM25, top-10 | Bắt từ khóa chính xác (số liệu, thuật ngữ) | dev | 8/15 (53%) | 12/15 (80%) | — (retrieval riêng, chưa có bước dựng context) | 2,5 ms |
| Phương pháp 3: Hybrid RRF, index A | RRF k = 60 trên top-20 dense + BM25 | Hai bên sai ở câu khác nhau (BM25 trượt q03, q04, q13; dense trượt q03, q11, q15) | dev | 7/15 (47%) | 14/15 (93%) | — (retrieval riêng, chưa có bước dựng context) | 242 ms |
| Dense, index B | cosine, top-10 | Chunk theo đoạn có ít mảnh vụn hơn A? | dev | 7/15 (47%) | 12/15 (80%) | — (retrieval riêng, chưa có bước dựng context) | 248 ms |
| BM25, index B | Okapi BM25, top-10 | như trên | dev | 8/15 (53%) | 12/15 (80%) | — (retrieval riêng, chưa có bước dựng context) | 2,8 ms |
| Hybrid RRF, index B | RRF k = 60 | như trên | dev | 11/15 (73%) | 13/15 (87%) | — (retrieval riêng, chưa có bước dựng context) | 257 ms |
| Cải thiện 1 (C1) | BASE + viết lại truy vấn (1 lần gọi LLM; thêm danh sách BM25 của truy vấn viết lại vào RRF; loại bản viết lại nếu thêm số hoặc từ viết tắt mới) | Nhóm lỗi "lệch từ vựng" (q03, q04, q07, q13 ở BM25) | dev (agent) | không chạy riêng | 12/15 (lượt tìm đầu, truy vấn do agent viết) | 13/15 (không đổi so với BASE; **không được nhận**) | 4,6 s; 0,0058 USD (cả 17 câu) |
| Cải thiện 2 (C2) | BASE + gộp chunk liền kề/trùng cùng trang, thêm chunk lân cận trong ngân sách 2400 ký tự | Nhóm lỗi "chunk gần trùng chen hạng" (q11, q15 ở dense) | dev (agent) | không chạy riêng | 12/15 | 13/15 (không đổi so với BASE; **không được nhận**) | 3,6 s; 0,0056 USD |
| Cấu hình đã chọn = BASE (Hybrid RRF, index B) | như dòng Hybrid B; context 2400 ký tự, không C1/C2 | Theo quy tắc ở docs/SELECTION_CRITERIA.md: cả hai cải thiện đều tăng ròng 0 < +2 câu | test, n = 11 (dùng lại 5 + mới 6) | 8/11 (dùng lại 4/5, mới 4/6) | 8/11 (dùng lại 4/5, mới 4/6); lượt tìm đầu của agent (truy vấn do agent viết): 8/11 | 8/11; dùng lại 4/5, mới 4/6 | 4,2 s; 0,0045 USD (13 câu) |
| Baseline = R0 (Dense, index A) | cosine, top-3, context 2400 ký tự | Hệ thống Day 6 | test, n = 11 | 6/11 (dùng lại 3/5, mới 3/6) | 8/11 (dùng lại 4/5, mới 4/6); lượt tìm đầu của agent (truy vấn do agent viết): 8/11 | 8/11; dùng lại 4/5, mới 4/6 | 4,0 s; 0,0045 USD (13 câu) |

Hit@1 và Evidence Hit@3 ở dòng test là retrieval riêng (truy vấn = câu hỏi gốc, top-10, không filter), chạy một lần bằng `python -m src.run_retrieval --final-test` sau khi chốt cấu hình. Lệnh này tính cả 6 tổ hợp phương pháp × index trên test; bảng chỉ nêu hai dòng R0 và BASE, các dòng còn lại nằm ở `results/retrieval/summary_test.json` và không được dùng để chọn lại. Cả hai cấu hình trượt cùng 3 câu ở top-3 (q17, n02, s04).

Lưu ý khi đọc bảng (dev, n = 15, chênh 1–2 câu chỉ là gợi ý):

- Hybrid A có Evidence Hit@3 cao nhất (14/15) nhưng Hit@1 thấp hơn dense (7 so với 9); hybrid B có Hit@1 và MRR@10 tốt nhất (11/15; 0,813). Index A và B khác nhau cả cách chunk, nên đừng gán lợi thế của hybrid cho một nguyên nhân duy nhất.
- Kết quả có filter (người dùng đang đọc chương n) chỉ có **n = 3** (`q03`, `q13`, `q14`), không so sánh trực tiếp với các dòng n = 15; xem `results/retrieval/summary_dev.json`.
- Context Evidence Rate chưa đo vì chưa có bước chọn context và ngân sách context.

**Phân tích lỗi dev (đọc từ trace; chỉ dùng dev, không dùng test để tìm lỗi):**

1. **q13 — lệch từ vựng.** Câu hỏi nói "home-market (local) debt … governments' total borrowing … developing economies"; chunk đúng (p117) viết "domestic public debt … 40–60 percent of total public debt". Trong câu hỏi chỉ các từ phổ biến (`debt`, `total`, `many`, `of`) có trong chunk đúng. Retrieval dev (không filter, truy vấn = câu hỏi): BM25 không có chunk đúng trong top-10 (kéo về trái phiếu nội tệ của Uzbekistan), dense hạng 3, hybrid hạng 9; với filter chương 3 (đầu vào người dùng) dense hạng 1. Trên cả 15 câu dev, 5 câu có tỷ lệ từ trùng (trọng số IDF) với chunk đúng < 0,35 và BM25 kém ở 4/5, nên đây là nhóm lỗi chứ không riêng q13. *Thử:* C1 (viết lại truy vấn). *Kết quả:* ở lần chạy agent (có filter chương 3), cả 4 cấu hình đều đưa p117 vào context, nên q13 không còn là chỗ C1 cải thiện; C1 cho Context Evidence Rate 13/15, bằng BASE (tăng ròng 0). Bộ kiểm tra "không thêm số/từ viết tắt" loại 3 bản viết lại (q05, q10, q11), q11 là cảnh báo nhầm ("third quarter" bị viết thành "Q3", số 3 không có trong truy vấn gốc), q10 bị loại vì thêm từ viết tắt "GDP"; bộ kiểm tra này bảo thủ và làm C1 mất tác dụng ở 3 câu.
2. **q11, q15 — chunk gần trùng chen hạng (index A, overlap 100 ký tự).** Overlap sao chép phần đuôi chunk trước vào đầu chunk sau. Ở q11, dense (index A) xếp hạng 1 chunk `p0075:003` (bắt đầu giữa từ: "tween the third quarter of 2024 and …, nearly twice its COVID-19 peak"), chunk này **không chứa** "more than fivefold"; chunk đúng `p0075:002` ở hạng 7. q15 tương tự (dense hạng 4). *Thử:* C2 (gộp chunk liền kề, bỏ phần trùng). *Kết quả:* ở lần chạy agent, R0 (dense, index A) thiếu evidence trong context ở cả q11 và q15, còn BASE (hybrid, index B) có đủ ở cả hai; nhưng **C2 trên BASE không thêm gì** (13/15 = 13/15). Vậy cải thiện đến từ việc chuyển sang index B (không overlap) kèm hybrid, không phải từ C2; hai yếu tố (index và phương pháp) bị trộn nên không tách được. Cũng thấy hồi quy: q04 R0 có evidence, còn BASE, C1, C2 không có (BASE tìm 2 lượt và model từ chối).
3. **Lỗi agent chiếm phần lớn từ chối nhầm: citation sai định dạng, không phải retrieval.** Ở BASE (dev), 6 câu có đáp án bị từ chối, trong đó 4 là `invalid_or_missing_citations` (q01, q09, q11, q12) dù context có evidence; ở q09, q11 và q12 câu trả lời nháp khớp đáp án mong đợi ("11 out of 68", "more than fivefold", "887 PPAs"); q01 mình chưa đối chiếu. Nguyên nhân: model ghi ID vào mảng `citations` nhưng không đặt `[id]` trong nội dung (hoặc ghi ID kèm dấu `]` thừa, q12), nên bộ kiểm tra của starter (citation phải có trong context **và** xuất hiện dạng `[id]` trong câu trả lời) từ chối. Hai câu còn lại (q03, q04) là model từ chối vì context thiếu evidence. Giữ nguyên luật của starter và coi đây là kết quả; hệ quả là retriever tốt hơn (BASE) lại có nhiều lần từ chối hơn R0 (6 so với 3 trên dev). Kết quả lệch này nằm trong nhiễu: ở q11, BASE và C1 có cùng truy vấn và cùng context nhưng khác kết quả (temperature 0 không đảm bảo xác định).
4. **q03 — hạn chế của nhãn, không phải lỗi retrieval.** Chunk `p0033:000` (dense hạng 3) có câu "for every $1.00 of financing received … securities worth approximately $1.33 to $1.98", tức là **trả lời đúng**, nhưng benchmark chỉ ghi p32 là gold nên bị tính là trượt. Hit@k và Context Evidence Rate vì vậy đánh giá thấp ở q03; chấm tay context 0/1/2 phản ánh đúng hơn. Benchmark đã đóng băng nên không sửa.

**Lý do chọn cấu hình** (theo [docs/SELECTION_CRITERIA.md](../../docs/SELECTION_CRITERIA.md), viết **trước** khi chạy agent và test, đã được tác giả xác nhận và đóng băng ngày 2026-11-14, sha256 `012941b6…18423623`, ghi ở [docs/CRITERIA_FROZEN.json](../../docs/CRITERIA_FROZEN.json)):

- *Bước 1 (retriever cơ sở, chỉ dev, truy vấn gốc):* Hybrid A (14/15) và Hybrid B (13/15) hòa ở Hit@3 (chênh ≤ 1 câu); tiêu chí hòa xét MRR@10 → **Hybrid RRF, index B** (0,813 so với 0,685).
- *Bước 2 (nhận cải thiện nếu tăng ròng ≥ 2 câu Context Evidence Rate trên dev):* C1 13/15 và C2 13/15, cùng bằng BASE → **cả hai không được nhận, ghi là kết quả âm**; C1+C2 không chạy vì điều kiện chưa đủ.
- *Bước 3:* cấu hình cuối = **BASE (Hybrid RRF, index B)**; test chạy một lần cho BASE và baseline R0 (dense, index A).
- *Công khai:* tiêu chí được viết sau khi đã thấy kết quả retrieval dev (không phải kết quả agent). Quy tắc chọn không xét R0 là ứng viên cuối, dù trên dev R0 trả lời được nhiều câu hơn BASE (12/15 so với 9/15, chưa có nhãn đúng/sai).
- *Lần chạy dev thứ nhất bị hủy:* ví dụ trong system prompt dùng ID `para:…` của index B nên ở R0 model chép nhầm tiền tố (13 lần citation không hợp lệ), và output sai định dạng của model bị tính nhầm là lỗi nhà cung cấp. Đã sửa (ví dụ ID theo đúng tiền tố của index; output sai định dạng tính là từ chối) rồi chạy lại một lần. Lần đầu lưu ở `results/discarded/dev_run1_prompt_example_bias/`. Lỗi được sửa là lỗi của harness, không chỉnh theo điểm.

## Agent và đánh giá

- **Tool, số lượt gọi, điều kiện dừng, cách chọn context và xử lý lỗi:** OpenAI `gpt-4o-mini` (chat completions, tool calling, temperature 0), mã ở `src/agent.py`. Ba tool: `search_documents(query)`, `answer(answer, citations)`, `abstain(reason)`; model bắt buộc gọi một tool mỗi lượt. Tối đa 3 lượt tìm; yêu cầu lượt tìm thứ 4 hoặc câu trả lời không có citation hợp lệ (ID phải nằm trong context **và** xuất hiện dạng `[id]` trong câu trả lời) → từ chối, theo luật của `starter/agentic.py`. Context 2400 ký tự (đo trên văn bản đoạn, không tính tiêu đề), top-3 chunk mỗi lượt tìm, gộp tích lũy các lượt; chỉ giữ context mới nhất trong prompt. Prompt nêu rõ "dùng câu hỏi gốc làm truy vấn đầu"; thực tế model chỉ làm vậy ở 5/17 câu dev, nên truy vấn của agent khác truy vấn của bảng retrieval. Hệ thống không có logic ngoài lệnh gọi model và tích hợp RAG (không ép truy vấn). Output sai định dạng của model tính là từ chối (có log); lỗi nhà cung cấp ghi riêng (`status: error`), không có lỗi nào ở các lần chạy chính thức.

**Dev (n = 15 + 2; lần chạy chính thức #2; chỉ số tự động; chưa chấm tay):**

| Cấu hình | Tool use | Context Evidence Rate | Lượt tìm đầu có hit@3 (truy vấn do agent viết) | Agent trả lời / từ chối nhầm (trên 15) | Từ chối 2 câu thiếu evidence (chưa xác nhận đúng) | Trung vị thời gian | Chi phí 17 câu |
|---|---|---|---|---|---|---|---|
| R0 (dense, A) | 17/17 | 12/15 | 12/15 | 12 / 3 | 2/2 | 2,9 s | 0,0052 USD |
| BASE (hybrid, B) | 17/17 | 13/15 | 12/15 | 9 / 6 | 2/2 | 3,2 s | 0,0052 USD |
| BASE + C1 | 17/17 | 13/15 | 12/15 | 11 / 4 | 2/2 | 4,6 s | 0,0058 USD |
| BASE + C2 | 17/17 | 13/15 | 12/15 | 9 / 6 | 2/2 | 3,6 s | 0,0056 USD |

**Test (một lần, n = 11 câu có đáp án + 2 câu thiếu evidence; số lượt gọi, tool use, từ chối nhầm là chỉ số tự động; grounded, citation hợp lệ, abstention đúng là theo nhãn chấm tay ở `results/agent/test/review/`):**

| Cấu hình / split | Tool use | Số lượt gọi (1 / 2 / 3) | Grounded answer 0/1/2 và trung bình | Citation hợp lệ | Câu có citation | Abstention đúng | Từ chối nhầm |
|---|---|---|---|---|---|---|---|
| R0 / test | 13/13 | 11 / 0 / 2 | 0: 6, 1: 0, 2: 5; trung bình 0,91/2 (dùng lại 0,80; mới 1,00) | 5/6 | 6/6 câu đã trả lời | 2/2 | 5/11 |
| BASE / test | 13/13 | 10 / 1 / 2 | 0: 4, 1: 0, 2: 7; trung bình 1,27/2 (dùng lại 1,20; mới 1,33) | 10/12 | 8/8 câu đã trả lời | 2/2 | 3/11 |

| Test, theo phần | R0 | BASE |
|---|---|---|
| Context Evidence Rate, dùng lại từ Day 6 (5 câu) | 4/5 | 4/5 |
| Context Evidence Rate, mới (6 câu) | 4/6 | 4/6 |
| Context Evidence Rate, gộp (11 câu) | 8/11 | 8/11 |
| Agent trả lời (dùng lại / mới / gộp) | 2/5 · 4/6 · 6/11 | 3/5 · 5/6 · 8/11 |
| Context chấm tay 0/1/2 (gộp 11 câu) | 2 / 0 / 9 | 2 / 0 / 9 |

Context chấm tay (9/11) cao hơn Context Evidence Rate tự động (8/11) ở cả hai cấu hình vì s04: sự kiện "DRS lập năm 1951" cũng nằm ở p28 (chunk được trích), còn benchmark chỉ ghi p114 là gold. Hai câu context bằng 0 ở cả hai cấu hình là q17 và n02 (đoạn gold không vào top-3).

Phần "dùng lại" đã chạy ở Day 6 và tác giả đã thấy kết quả nên không độc lập; chỉ phần "mới" là đánh giá độc lập thực sự, và phần này chỉ có 6 câu có đáp án.

**Nhãn từng câu test (13 câu × 2 cấu hình; ctx = context 0/1/2, ans = grounded 0/1/2; câu bị từ chối chấm ans 0). Nhãn từng citation, văn bản câu trả lời và context nằm ở `results/agent/test/review/`:**

| Query ID | Loại câu | R0 (dense, A) | BASE (hybrid, B) | Ghi chú nhãn |
|---|---|---|---|---|
| q16 | dùng lại Day 6 (evidence trang 38) | R0: 1 lượt tìm; từ chối: citation sai định dạng; ctx 2, ans 0 | BASE: 1 lượt tìm; từ chối: citation sai định dạng; ctx 2, ans 0 | R0: Từ chối vì citation sai định dạng; bản nháp bị loại khớp đáp án (7,0% lên 1,4 nghìn tỷ USD). BASE: Như q16#1: từ chối vì citation sai định dạng (có dấu ngoặc thừa); bản nháp khớp đáp án. |
| q17 | dùng lại Day 6 (evidence trang 90) | R0: 1 lượt tìm; từ chối: model nói thiếu bằng chứng; ctx 0, ans 0 | BASE: 1 lượt tìm; từ chối: model nói thiếu bằng chứng; ctx 0, ans 0 | R0: Như q17#1. BASE: Context không có đoạn gold (p90); model từ chối vì thiếu bằng chứng. |
| q18 | dùng lại Day 6 (evidence trang 96) | R0: 1 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | BASE: 1 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | R0: 150% xuất khẩu, ngưỡng HIPC; đủ. BASE: Đúng; câu trả lời viết 'is 150 percent', bỏ 'at least'. |
| q19 | dùng lại Day 6 (evidence trang 109) | R0: 1 lượt tìm; từ chối: citation sai định dạng; ctx 2, ans 0 | BASE: 1 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | R0: Từ chối vì citation sai định dạng; bản nháp bị loại đúng (36 nước, 47%). BASE: 36 nước, 47% của 76. |
| q20 | dùng lại Day 6 (evidence trang 119) | R0: 1 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | BASE: 1 lượt tìm; trả lời, 3 citation; ctx 2, ans 2 | R0: Giao thức tháng 7/2026, điều khoản chia sẻ và quy tắc bảo mật, chỉ dùng cho đối chiếu dữ liệu. BASE: Đúng phần giao thức; thêm thông tin dự án thí điểm Indonesia (761 khoản vay) có nguồn nhưng không trả lời trực tiếp câu hỏi. |
| s01 | mới (dự phòng Day 6) (evidence trang 40) | R0: 1 lượt tìm; từ chối: citation sai định dạng; ctx 2, ans 0 | BASE: 1 lượt tìm; trả lời, 2 citation; ctx 2, ans 2 | R0: Từ chối vì citation sai định dạng; bản nháp bị loại nêu 80,8% thay vì 75,2%, nên sẽ sai nếu được tính. BASE: 75,2% đúng. $251,1 tỷ là khối lượng cho vay của chủ nợ tư nhân, cách viết 'which amounted to' hơi mơ hồ; phần 80,8% và $358,3 tỷ (không tính Trung Quốc) có trong nguồn. |
| s02 | mới (dự phòng Day 6) (evidence trang 96) | R0: 1 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | BASE: 1 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | Dầu mỡ, 63,6%. |
| s03 | mới (dự phòng Day 6) (evidence trang 126) | R0: 1 lượt tìm; từ chối: model nói thiếu bằng chứng; ctx 2, ans 0 | BASE: 1 lượt tìm; từ chối: model nói thiếu bằng chứng; ctx 2, ans 0 | R0: Như s03#1. BASE: Từ chối nhầm: context có câu p126 định nghĩa accrual-based và cash basis. |
| s04 | mới (dự phòng Day 6) (evidence trang 114) | R0: 1 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | BASE: 2 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | R0: 1951; xem ghi chú s04#1. BASE: 1951. Gold ghi p114 nhưng chunk p28 được trích cũng nêu 'DRS, instituted in 1951'. |
| n01 | mới (viết mới) (evidence trang 64) | R0: 1 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | BASE: 1 lượt tìm; trả lời, 1 citation; ctx 2, ans 2 | R0: Lõi đúng (Kenya, 3,5 tỷ USD). Ý 'phần lớn tiền dùng cho quản lý nợ' trong nguồn nói về hai nước (Kenya và Côte d'Ivoire) nhưng câu trả lời gán cho Kenya. BASE: Kenya, 3,5 tỷ USD; ý về trả nợ trước hạn 2027/2028 có trong chunk. |
| n02 | mới (viết mới) (evidence trang 100) | R0: 3 lượt tìm; trả lời, 1 citation; ctx 0, ans 0 | BASE: 3 lượt tìm; trả lời, 2 citation; ctx 0, ans 0 | R0: Nêu dầu mỡ nhưng dựa trên chỉ số phụ thuộc nhập khẩu (63%), không phải đa dạng nguồn; thiếu nhóm đậu/hạt; con số 63% không có trong chunk được trích; context không có đoạn gold. BASE: Không nêu nhóm thực phẩm nào; context không có đoạn gold (p100, đa dạng nguồn nhập). Hai citation nói về phụ thuộc nhập khẩu và khái niệm đa dạng nói chung, không hỗ trợ kết luận. |
| u03 | thiếu evidence (không có trong tài liệu) | R0: 3 lượt tìm; từ chối: model nói thiếu bằng chứng; từ chối đúng: có | BASE: 3 lượt tìm; từ chối: model nói thiếu bằng chứng; từ chối đúng: có | Từ chối, không thêm khẳng định. |
| u04 | thiếu evidence (không có trong tài liệu) | R0: 1 lượt tìm; từ chối: model nói thiếu bằng chứng; từ chối đúng: có | BASE: 1 lượt tìm; từ chối: model nói thiếu bằng chứng; từ chối đúng: có | Từ chối, không thêm khẳng định. |

- **Đường dẫn trace, nhãn, lệnh chạy, thời gian và chi phí:**
  - Retrieval dev: `results/retrieval/traces_dev.jsonl`, `summary_dev.json`; lệnh `python -m src.run_retrieval`.
  - Agent dev: `results/agent/dev/<cấu hình>/{traces,summary}.json`; lệnh `python -m src.run_agent --config R0,BASE,BASE+C1,BASE+C2`; log `results/agent_dev_run.log`.
  - Agent test: `results/agent/test/{R0,BASE}/{traces,summary}.json`; lệnh `python -m src.run_agent --config R0,BASE --final-test`; log `results/agent_test_run.log`. Script từ chối chạy nếu benchmark hoặc tiêu chí đã đổi sau khi đóng băng, và từ chối chạy test lần hai.
  - Chấm tay: `python -m src.make_review_sheet` (dựng bảng ẩn tên, xáo trộn thứ tự bằng seed cố định), điền nhãn, rồi `python -m src.finish_review` (gọi `starter/agent_metrics.py`).
  - Kiểm thử offline (không đo chất lượng): `PYTHONUTF8=1 python tests/test_src_agent.py`.
  - Chi phí là **ước tính** từ số token đo được và đơn giá niêm yết giả định (gpt-4o-mini 0,15/0,60 USD mỗi triệu token vào/ra; embedding 0,02 USD mỗi triệu), cần đối chiếu bảng giá trước khi trích dẫn.
- **Kết quả trước/sau, đánh đổi và giới hạn:**
  - *Trước/sau (dev, retrieval, query gốc):* chuyển từ dense index A sang hybrid index B tăng Hit@3 từ 12/15 lên 13/15 và MRR@10 từ 0,732 lên 0,813; ở agent, Context Evidence Rate 12/15 → 13/15, nhưng số lần từ chối nhầm tăng từ 3 lên 6 (chủ yếu do citation sai định dạng, xem lỗi 3). C1 và C2 không tạo cải thiện đo được.
  - *Giới hạn:* n = 15 ở dev và 11 ở test, mỗi câu ≈ 7–9 điểm phần trăm, nên chênh 1–3 câu là nhiễu; temperature 0 không xác định hoàn toàn (q11); truy vấn của agent khác truy vấn của bảng retrieval; index và phương pháp bị trộn trong so sánh R0/BASE; Context Evidence Rate và Hit@k dựa vào trang gold hẹp (q03); nhãn câu mới do trợ lý AI đề xuất, tác giả duyệt, và tác giả vừa soạn vừa chấm; giá chi phí là giả định; đánh giá riêng C1/C2 với truy vấn gốc (không qua agent) chưa chạy.


## Thử thách nâng cao (nếu thực hiện)

Chưa thực hiện (không bắt buộc).
