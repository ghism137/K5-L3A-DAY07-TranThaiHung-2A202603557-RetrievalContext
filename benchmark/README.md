# Benchmark Day 7 — International Debt Report 2026

Corpus: chương 1–3 của *International Debt Report 2026* (World Bank, CC BY 3.0 IGO; trang PDF 27–134, 103 trang nội dung), giữ nguyên từ Day 6. Câu hỏi nằm ở [questions.json](questions.json); bản Day 6 gốc ở [day6_questions.json](day6_questions.json) (hash khớp [day6_FROZEN.json](day6_FROZEN.json)).

## Thành phần

| Split | Có đáp án | Thiếu bằng chứng | Nguồn gốc |
|---|---:|---:|---|
| dev | 15 | 2 (`u01`, `u02`) | 15 câu dev Day 6 (`q01`–`q15`); 2 câu thiếu evidence viết mới |
| test | 11 | 2 (`u03`, `u04`) | xem bên dưới |

Test gồm hai phần, **luôn báo kết quả riêng từng phần và gộp**:

| Phần test | Câu | Ghi chú |
|---|---|---|
| **Dùng lại từ Day 6** (`origin: day6_test_reused`) | `q16`–`q20` (5 câu có đáp án) | Đã chạy ở Day 6 (không dùng để chỉnh) và tác giả đã thấy kết quả. Dùng lại có chủ đích, ghi rõ để người chấm tự đánh giá. |
| **Mới** | `s01`–`s04` (`day6_spare_new`: câu dự phòng Day 6, chưa từng truy xuất), `n01`, `n02` (`day7_new`, viết mới) = 6 câu có đáp án; `u03`, `u04` = 2 câu thiếu evidence | Chưa từng chạy với bất kỳ hệ thống nào. Đủ tối thiểu (≥ 5 + ≥ 2) để đứng độc lập. |

Khi đã dùng test để chỉnh, phần test đó không còn độc lập (RULES.md): giữ test mới nguyên vẹn đến lần chạy cuối.

## Câu thiếu bằng chứng

Gần chủ đề tài liệu nhưng không có thông tin. Mỗi câu ghi `absence_reason` và `absence_check`. `verify_benchmark` chạy lại các regex trên **cả 280 trang PDF** (không chỉ 103 trang đã index) và yêu cầu 0 trang khớp. Ngoài regex, tác giả đọc thủ công các chỗ liên quan (ghi ở `absence_check.manual`). Không dùng kết quả top-k để kết luận "không có".

| ID | Split | Chủ đề gần | Vì sao không trả lời được |
|---|---|---|---|
| u01 | dev | vay bằng tiền mã hóa / stablecoin | PDF không có từ crypto, stablecoin, bitcoin, blockchain |
| u02 | dev | phát hành trái phiếu Panda | PDF không có "Panda"; đồng nhân dân tệ chỉ xuất hiện làm tiền định giá/đồng tiền trả nợ (p33, 71, 74) |
| u03 | test | dự báo dư nợ cuối 2028 | báo cáo chỉ phân tích 2025, không có dự báo dư nợ |
| u04 | test | giá vàng và tỷ lệ nợ/xuất khẩu | PDF không có từ "gold" |

## Câu hỏi mới có đáp án

- `n01` (p64): quốc gia phát hành trái phiếu lớn nhất Châu Phi cận Sahara năm 2025 — Kenya, 3,5 tỷ USD.
- `n02` (p100): nhóm thực phẩm có nguồn nhập khẩu đa dạng hơn khi nợ/xuất khẩu cao — dầu mỡ; đậu, hạt.

## Định nghĩa "hit" (giữ nguyên Day 6)

Một chunk là **hit** khi `page` thuộc trang gold **và** chunk chứa đủ mọi chuỗi trong `key_facts` (so khớp sau khi chuẩn hóa khoảng trắng/xuống dòng). Lý do không dùng `evidence in chunk['text']` của starter: câu evidence trích nguyên văn thường bị PDF ngắt dòng và dấu gạch nối làm lệch. Khớp bằng chuỗi vẫn chỉ là xấp xỉ; nhãn grounded/context do tác giả chấm tay theo BENCHMARK.md.

## Schema

Câu có đáp án: `id, split, origin, type, question, expected_answer, answerable: true, expected_behavior: "search_and_answer", gold: [{source_id, page, evidence}], key_facts, chapter_of_gold, filter`.
Câu thiếu evidence: `id, split, origin, type, question, answerable: false, expected_behavior: "search_and_abstain", absence_reason, absence_check, filter: null`.
`filter = {"chapter": n}` là input giả định do người dùng cung cấp trước (đang đọc chương n); không chứa trang hay đáp án. Câu có filter: `q03, q13, q14` (dev), `q17, s03` (test).

## Dựng và kiểm chứng

```bash
python -m src.build_benchmark        # dựng questions.json từ Day 6 + câu mới
python -m src.verify_benchmark       # kiểm chứng → results/benchmark_verification.txt
python -m src.verify_benchmark --freeze   # chỉ chạy khi đã duyệt xong; ghi sha256 vào FROZEN.json
```

`verify_benchmark` kiểm: evidence và key facts nằm trên trang gold; filter không loại trang gold; **mọi key fact nằm trong một chunk của cả index A và B** (nếu không, lỗi do chia chunk chứ không phải truy xuất); không có trang gold chung giữa dev và test; số câu theo BENCHMARK.md.

## Hạn chế

- Tác giả vừa soạn câu hỏi vừa chấm; câu mới `n01`, `n02`, `u01`–`u04` do trợ lý AI đề xuất, tác giả duyệt (ghi rõ trong báo cáo).
- n nhỏ: test 11 câu có đáp án, mỗi câu đổi ~9 điểm phần trăm; phần mới chỉ 6.
- Các câu `truc_tiep` trùng nhiều từ với nguồn nên Hit@k có thể cao hơn thực tế. Trang gold `p96` dùng cho hai câu test (`q18`, `s02`).
- Câu thiếu evidence chỉ kiểm bằng regex và đọc tay chỗ liên quan, không đọc hết 280 trang.
