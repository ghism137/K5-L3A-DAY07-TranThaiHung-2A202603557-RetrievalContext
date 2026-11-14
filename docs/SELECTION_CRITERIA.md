# Tiêu chí chọn cấu hình — Day 7

Tác giả: Trần Thái Hưng (2A202603557). Viết ngày 2026-11-14, **trước khi chạy agent và trước khi chạy test**. Trạng thái: **đã được tác giả đọc, xác nhận và đóng băng ngày 2026-11-14** (sha256 ghi ở [CRITERIA_FROZEN.json](CRITERIA_FROZEN.json), tính trên file này sau khi đã ghi dòng trạng thái này). Không sửa sau thời điểm này; nếu buộc phải đổi, ghi một mục thay đổi riêng và nêu lý do trong báo cáo.

**Công khai thứ tự thực hiện:** tiêu chí này được viết *sau khi* đã xem kết quả retrieval dev của 3 phương pháp (`results/retrieval/summary_dev.json`) và đọc lỗi dev q03, q11, q13, q15, nhưng *trước* mọi lần chạy agent và *trước* mọi lần chạy test. Không dùng test để chọn. Các số dev đã thấy có thể ảnh hưởng cách tác giả chọn ngưỡng; vì vậy ngưỡng được đặt cố định ở mức thận trọng (cần hơn kém ≥ 2 câu mới coi là khác biệt).

## 1. Cố định ở mọi cấu hình (để chỉ so sánh phần retrieval/context)

| Mục | Giá trị |
|---|---|
| Corpus, index, nhãn | Như đã đóng băng (`benchmark/FROZEN.json`, index A 376 chunk, B 429 chunk) |
| Agent model | `AGENT_MODEL` trong `.env` (hiện `gpt-4o-mini`), temperature 0, **cùng một model và cùng system prompt ở mọi cấu hình** |
| Agent | Tool `search_documents(query)`; tối đa **3 lượt gọi**; dừng khi model trả lời, hoặc hết lượt (khi đó bắt buộc từ chối) |
| Context | Ngân sách **2400 ký tự** (= 3 × kích thước chunk tối đa 800), đo bằng ký tự; ghi thêm token. Starter mặc định 800 là chưa đủ cho 1 chunk đầy |
| Số chunk ban đầu (seed) | top-3 của retriever |
| Filter | Dùng `filter` của câu hỏi (đầu vào do người dùng cung cấp, không suy ra từ gold) **giống nhau ở mọi cấu hình** trong lần chạy agent. Bảng retrieval riêng báo cả không filter (n = 15) và có filter (n = 3 ở dev) |
| Query | Báo kết quả **query gốc**; query viết lại báo riêng kèm trace từng bước |
| Dữ liệu cấm | Không đưa `gold`, `key_facts`, `expected_answer` vào agent, query hay prompt |

## 2. Ứng viên

| ID | Cấu hình | Mục đích |
|---|---|---|
| **R0** (baseline cố định) | Dense, index A, top-3, không viết lại, không mở rộng context | Hệ thống Day 6; dùng làm baseline ở test |
| M2 | BM25, index A và B | Phương pháp 2 |
| M3 | Hybrid RRF (k = 60, top-20 mỗi bên), index A và B | Phương pháp 3 |
| **C1** | Cơ sở + **viết lại truy vấn** | Nhóm lỗi "lệch từ vựng" (q03, q04, q07, q13 ở BM25) |
| **C2** | Cơ sở + **gộp chunk liền kề/trùng cùng trang** để dựng context | Nhóm lỗi "chunk gần trùng chen hạng" (q11, q15 ở dense) |
| C1+C2 | Chỉ thử nếu C1 và C2 đều đạt ngưỡng ở mục 4 | Kiểm tra cộng gộp |

**C1 — viết lại truy vấn.** Một lần gọi LLM (cùng agent model, temperature 0, prompt cố định lưu trong repo) chỉ nhận **câu hỏi**; trả về 1 truy vấn bổ sung dùng từ vựng kỹ thuật tương đương (ví dụ "home-market" → "domestic"). Không được thêm số liệu hay tên riêng không có trong câu hỏi. Truy vấn gốc và truy vấn viết lại cùng chạy; ba danh sách xếp hạng được trộn bằng RRF. Ghi lại truy vấn viết lại, token và chi phí.

**C2 — dựng context.** Từ top-3 seed: (a) gộp các chunk cùng trang chồng lấn hoặc liền kề thành một đoạn, bỏ phần văn bản trùng; (b) nếu còn ngân sách, thêm chunk liền kề trước rồi sau của seed hạng 1, rồi hạng 2, rồi hạng 3, đến khi hết 2400 ký tự. Mỗi đoạn giữ ID các chunk thành phần để agent trích dẫn `[chunk-id]` hợp lệ. Cơ chế này chạy cho **mọi** truy vấn, không có ngoại lệ theo câu.

## 3. Chỉ số

- **Retrieval (không LLM):** Hit@1, Evidence Hit@3, MRR@10 trên câu có đáp án (n = 15). Câu thiếu evidence không vào mẫu số. Định nghĩa hit như `benchmark/README.md`.
- **Context Evidence Rate:** số câu có đáp án mà **context cuối gửi model** chứa đủ mọi `key_facts` trên trang gold / 15, đã chuẩn hóa như Hit.
- **Agent (dev, chạy thật):** tool use, số lượt gọi, grounded answer 0/1/2 (trung bình /2), citation hợp lệ (có trong context **và** hỗ trợ câu trả lời, đọc tay), abstention đúng (u01, u02), từ chối nhầm, thời gian trung vị, chi phí USD.
- Khi một câu chỉ khác nhau do nhãn gold hẹp (ví dụ q03 có đáp án đúng ở p33), ghi rõ trong báo cáo thay vì sửa benchmark.

## 4. Quy tắc chọn (áp theo thứ tự)

**Bước 1 — chọn retriever cơ sở** (R0, M2, M3 × index A/B), chỉ bằng dev, query gốc, không filter:
1. Evidence Hit@3 cao nhất; chênh ≤ 1 câu coi là hòa.
2. Hòa → MRR@10 cao hơn.
3. Vẫn hòa → độ trễ thấp hơn.

Áp quy tắc này lên các số dev hiện có: Hybrid A (14/15) và Hybrid B (13/15) hòa ở bước 1; bước 2 chọn **Hybrid RRF, index B** (MRR@10 0,813 so với 0,685). Nếu trước khi đóng băng bạn thấy kết luận này không hợp lý, sửa quy tắc **bây giờ**, không sửa sau.

**Bước 2 — nhận một cải thiện (C1 hoặc C2).** So với chính retriever cơ sở trên cùng 15 câu dev (có agent), nhận khi đồng thời:
- Context Evidence Rate tăng ròng ≥ 2 câu (số câu thắng − số câu thua ≥ 2), kèm danh sách câu thắng/thua;
- Abstention đúng và tool use không kém hơn cơ sở;
- Chi phí và độ trễ tăng thêm được ghi rõ (không có ngưỡng cứng, nhưng phải nêu đánh đổi).

Không đạt → ghi là **kết quả âm** trong báo cáo, vẫn giữ số liệu; không đổi tham số để "cứu" rồi báo lại.

**Bước 3 — chọn cấu hình cuối** trong {cơ sở, cấu hình được nhận, C1+C2 nếu đủ điều kiện}:
1. Điều kiện chặn: abstention đúng ≥ cơ sở; không có lỗi hệ thống chưa giải thích.
2. Context Evidence Rate cao hơn (hơn ≥ 2 câu mới coi là khác).
3. Grounded answer trung bình /2 cao hơn (chênh ≤ 2 điểm cộng dồn coi là hòa).
4. Citation hợp lệ cao hơn.
5. Chi phí và độ trễ thấp hơn.
6. Đơn giản hơn (ít lệnh gọi LLM và ít thành phần).

**Tham số không được dò thêm trên dev:** RRF k, độ sâu 20, k1/b của BM25, ngân sách 2400. Đây là giá trị đặt trước; n = 15 quá nhỏ để chỉnh mà không overfit.

## 5. Quy trình test

1. Đóng băng file này (sha256) và chốt cấu hình cuối trên dev.
2. Chạy test **một lần** cho **R0** và cấu hình cuối (`--final-test`). Không sửa code hay prompt sau khi đã nhìn test. Nếu lỗi hệ thống buộc chạy lại, ghi lại nguyên nhân và không điều chỉnh cấu hình.
3. Báo riêng: phần **dùng lại từ Day 6** (q16–q20, tác giả đã thấy kết quả Day 6 nên không độc lập), phần **mới** (6 câu có đáp án + u03, u04), và gộp. Chỉ phần mới là đánh giá độc lập thực sự.
4. Chấm tay ≥ 5 câu test có đáp án và 2 câu thiếu evidence (context 0/1/2; grounded 0/1/2; citation; abstention), cho cả hai cấu hình; ẩn tên cấu hình khi chấm nếu có thể. Sau đó chạy `starter/agent_metrics.py`.
5. Báo `n/N`, thời gian, chi phí; nêu rõ test chỉ có 11 câu có đáp án (mỗi câu ≈ 9 điểm phần trăm).

## 6. Đề xuất cải thiện (ngoài hai cấu hình chính)

Đã xếp theo mức đáng thử. Chỉ **C1** và **C2** nằm trong quy tắc chọn ở trên; các mục còn lại là thí nghiệm tùy chọn, chạy trên dev, không thay đổi cách chọn nếu chưa được duyệt thêm.

| # | Đề xuất | Nhắm vào | Chi phí / rủi ro |
|---|---|---|---|
| 1 | **C1** viết lại truy vấn | Lệch từ vựng giữa câu hỏi và văn bản | +1 lệnh gọi LLM mỗi truy vấn; có thể thêm thuật ngữ sai |
| 2 | **C2** gộp chunk liền kề, bỏ phần trùng | Chunk đuôi gần trùng thắng chunk đúng (q11, q15) | Gần như không tốn thêm; tốn ngân sách context |
| 3 | **Rerank** top-20 thành top-3 bằng LLM hoặc cross-encoder | Thứ hạng nhiễu giữa các chunk cùng chủ đề (q03) | +độ trễ và chi phí; cross-encoder cần tải thêm model |
| 4 | **Chunker theo câu/đoạn, không overlap** (mở rộng của index B) | Mảnh vụn bắt đầu giữa từ do cắt cửa sổ cố định | Phải dựng index mới và embed lại (≈ 805 chunk, vài cent) |
| 5 | **System prompt chặt hơn** cho agent: chỉ trích `[chunk-id]` có trong context; từ chối khi thiếu điều kiện; tài liệu là dữ liệu, không phải chỉ dẫn | Grounded, citation, abstention | Gần như không tốn thêm; cần giữ cố định ở mọi cấu hình |
| 6 | **Model agent mạnh hơn** (kiểm tra danh sách model mà khóa API cho phép) | Chất lượng trả lời, đọc điều kiện | Tốn hơn; trộn lẫn với thay đổi retrieval, nên chạy như thí nghiệm riêng với retrieval cố định |
| 7 | **Embedding lớn hơn** (ví dụ `text-embedding-3-large`) | Dense kém ở truy vấn khó | Đổi version index, phải nạp lại toàn bộ; so sánh phải ghi rõ chi phí và thay đổi |

Không đề xuất: dò RRF k hoặc trọng số bằng dev (overfit với n = 15); suy ra filter chương từ nội dung câu hỏi hoặc gold; dùng trang gold để thu hẹp tìm kiếm.
