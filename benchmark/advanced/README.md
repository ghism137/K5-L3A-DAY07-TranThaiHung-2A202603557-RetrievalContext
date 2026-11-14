# Benchmark nâng cao — International Debt Report 2026 (280 trang)

Tài liệu: *International Debt Report 2026*, World Bank, 280 trang PDF (cả phần mở đầu, 3 chương, hồ sơ quốc gia và vùng, phụ lục), giấy phép CC BY 3.0 IGO; nguồn <https://hdl.handle.net/10986/45762>. Cùng tài liệu với bài cơ bản, nhưng **bộ câu hỏi mới hoàn toàn** và **index phủ cả 280 trang** (bài cơ bản chỉ index trang 27–134). Câu hỏi nằm ở [questions.json](questions.json); hash đóng băng ở [FROZEN.json](FROZEN.json).

## Thành phần

| Nhóm chính | Dev (có đáp án) | Test (có đáp án) | Tối thiểu của đề (test) |
|---|---:|---:|---:|
| Bảng | 4 | 6 | 6 |
| Ảnh, sơ đồ | 3 | 5 | 5 |
| Biểu đồ | 4 | 5 | 5 |
| Multi-hop | 2 | 4 | 4 |
| Text | 2 | 4 | 4 |
| **Có đáp án** | **15** | **24** | 24 |
| Thiếu bằng chứng | 3 | 6 | 6 |
| **Tổng** | **18** | **30** | 30 |

Mỗi câu thuộc đúng **một** nhóm chính. Dev và test **không dùng chung trang gold nào** (`adv_verify_benchmark` kiểm tra). Dev dùng trang 20, 28, 37, 88, 150, 202; test dùng trang 19, 21, 63, 110, 111, 113, 132, 136, 137, 138, 142, 143, 175, 200, 230, 262, 267, 269.

## Cách phân nhóm (và một hạn chế cần nói rõ)

Tài liệu **không có ảnh chụp** nào có nội dung; ảnh nhúng duy nhất là nền trang bìa (trang trí, không dùng). Vì vậy nhóm "Ảnh, sơ đồ" gồm các hình có ý nghĩa không gian:

- **Sơ đồ kiến trúc ba tầng** (Figure 3B.1, trang 132): ba hộp, mũi tên và vòng phản hồi nét đứt (test, 3 câu).
- **Trang hướng dẫn đọc hồ sơ** (trang 136): khung mẫu hồ sơ Belize có chú thích đánh số (test, 2 câu).
- **Sơ đồ khối phân cấp "Figure 2"** trên trang hồ sơ quốc gia (Azerbaijan, Kenya): chiều rộng khối tỷ lệ với số tiền, hàng dưới chia nhỏ hàng trên (dev, 3 câu).

Điểm yếu: loại sơ đồ khối của dev khác loại sơ đồ của test, và người chấm có thể xếp các khối phân cấp vào nhóm biểu đồ. Nhóm biểu đồ chỉ dùng biểu đồ thống kê (cột, cột chồng, waterfall) đọc theo trục, chú giải hoặc nhãn số in sẵn.

Bảng: chỉ có hai bảng đánh số (Table 1.1 ở trang 28, Table 1.2 ở trang 63) và danh sách nhóm nước (trang 269). Dev dùng Table 1.1; test dùng Table 1.2 và danh sách nhóm nước, để hai split không dùng chung trang.

## Định dạng và nguồn gốc

Câu có đáp án: `id, split, group, tags, question, expected_answer, tolerance, gold[{page, kind, locator, evidence}], checks, why`. Câu thiếu bằng chứng: `absence_reason, absence_check{regexes_over_all_pages, visual_note}`. `gold`, `expected_answer` và `checks` **không** vào pipeline: bộ chạy chỉ đọc `id`, `question` và `split`.

Câu hỏi và đáp án do **trợ lý AI soạn từ ảnh trang gốc và lớp văn bản PDF, tác giả duyệt** (AI-proposed, author-review). Đã soạn *trước khi* xem kết quả trích xuất của pipeline, với một ngoại lệ cần nêu: để kiểm tra prompt trích xuất, mình đã chạy thử trên 5 trang mẫu (28, 46, 132, 136, 141) và đọc kết quả của các trang 28 và 132 trước khi soạn câu hỏi. Hai trang đó có trong benchmark (Table 1.1 ở dev, Figure 3B.1 ở test). Đáp án vẫn lấy từ ảnh gốc, nhưng đây là sự tiếp xúc có thật giữa pipeline và việc soạn câu hỏi. Các số được đối chiếu với ảnh trang gốc: Bảng 1.1 và 1.2, Figure 3B.1, các biểu đồ ở trang 37, 88, 110, 111, 113, ô chỉ số của các trang hồ sơ, và khung mẫu ở trang 136.

## Kiểm chứng (`python -m src.adv_verify_benchmark`)

- Số câu và số câu mỗi nhóm đạt ngưỡng của ADVANCED.md; dev và test không chung trang gold; id và câu hỏi không trùng.
- 35 chuỗi kiểm tra có trong lớp văn bản của đúng trang gold (số bảng, số ô chỉ số, câu text).
- Câu thiếu bằng chứng: mỗi regex được chạy trên **cả 280 trang** và phải khớp **0 trang** (Ireland, Switzerland, Norway, "Figure 2.30", "Figure 3.7", "end-2022", "inflation rate"...). Hai câu thiếu bằng chứng dựa vào nội dung hình (t26: Figure 3.3 chỉ có End-2021, End-2023, End-2024; t29: thẻ Figure 4 của Azerbaijan ghi ".." vì không có cam kết mới) được kiểm bằng ảnh gốc và ghi trong `visual_note`.

## Cách chấm test (theo ADVANCED.md)

Mỗi câu **đạt hoặc không đạt**. Câu có đáp án đạt khi trả lời đúng và đủ (đúng đơn vị, điều kiện, phép tính), citation xác định được trang và vùng evidence, và evidence hỗ trợ toàn bộ câu trả lời. Đúng một phần, sai citation hoặc từ chối đều không đạt. Câu thiếu bằng chứng đạt khi từ chối hoặc nêu rõ không đủ bằng chứng, không thêm khẳng định thiếu căn cứ. Lỗi hệ thống, timeout hoặc không có kết quả tính là không đạt và vẫn nằm trong mẫu số. Đáp án đọc từ biểu đồ không có nhãn số (t09, t10, t11) có dung sai ghi ở `tolerance` hoặc `expected_answer`.

## Hạn chế

- Một tài liệu, 24 câu có đáp án ở test: mỗi câu đổi ≈ 3,3 điểm phần trăm tổng (1/30); ngưỡng 90% nghĩa là tối đa 3 câu không đạt.
- Nhiều giá trị ở nhóm "biểu đồ" và "sơ đồ" cũng có trong lớp văn bản của PDF (nhãn vẽ bằng chữ), nên một pipeline chỉ đọc chữ vẫn trả lời được một phần; nhóm này kiểm tra khả năng đọc cấu trúc hình hơn là khả năng đọc điểm ảnh. Câu t11 (đọc độ cao cột) và t16 (chữ nhỏ trong khung mẫu) cần nhìn ảnh.
- Tác giả vừa soạn vừa chấm; câu và đáp án do trợ lý AI đề xuất và chưa được đối chiếu độc lập bởi người thứ hai.
