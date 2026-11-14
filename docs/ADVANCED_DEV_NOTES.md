# Nhật ký dev — thử thách nâng cao

Ghi lại mọi lần chạy dev, lần bị hủy và lỗi kỹ thuật đã sửa, theo [ADVANCED_CRITERIA.md](ADVANCED_CRITERIA.md) (đã đóng băng).

| Thời điểm | Sự kiện |
|---|---|
| 2026-11-15 | Benchmark nâng cao đóng băng (sha256 `028f3055…b08021`). Trích xuất hình cho 280 trang bằng gpt-6.1-terra, prompt `v1`. |
| 2026-11-15 | Index dựng xong: 840 chunk văn bản + 597 chunk hình, 280 trang; 11 trang không có nội dung (2, 12, 16, 18, 22, 26, 106, 264, 266, 278, 279). Kiểm tra trích xuất so với ảnh gốc: 101/103 giá trị tìm thấy (sót "3.6%" và "2.0%" ở trang 136). |
| 2026-11-15 | Chạy thử 3 câu dev (d01–d03, cấu hình PAGES), kết quả bỏ đi, không tính điểm. Hai câu bị từ chối vì model ghi ID trong mảng `citations` kèm dấu ngoặc vuông (`[vis:…]`) dù câu trả lời đúng và citation trong văn bản đúng. **Lỗi kỹ thuật đã sửa**: chuẩn hóa chuỗi ID (bỏ ngoặc, khoảng trắng) trước khi kiểm tra; luật không đổi (ID phải có trong context và xuất hiện `[id]` trong câu trả lời). Sửa dựa trên định dạng, không dựa trên điểm dev. |
| 2026-11-15 | **Dev chính thức** (18 câu, 3 cấu hình, chạy một lần). pass_auto: TEXT 5/18, VISUAL 15/18, PAGES 15/18. Token đầu vào của agent: TEXT 174.824, VISUAL 76.643, PAGES 312.655. Không có lỗi hệ thống. Theo quy tắc ở ADVANCED_CRITERIA.md mục 4: VISUAL và PAGES hòa ở 15/18 (chênh ≤ 1), hòa thì chọn cấu hình ít token hơn → **VISUAL**. |
| 2026-11-15 | Ba câu không đạt ở cả VISUAL và PAGES (d04, d14, d15) được đọc tay: d04 và d15 trả lời đúng điều câu hỏi hỏi, nhưng `expected_answer` chứa chi tiết phụ không được hỏi ("(it was 214.6 in 2020)", "up 34.6 percent") nên bộ chấm hỗ trợ chấm hụt; d14 trả lời đúng (8,2 percent, nêu 1989) nhưng trích dẫn ở trang 51, nơi tài liệu nêu cùng sự kiện, còn gold chỉ ghi trang 20. Đây là hạn chế của benchmark (đáp án chuẩn dài hơn câu hỏi; một sự kiện xuất hiện ở hai trang), không phải lỗi của pipeline; benchmark đã đóng băng nên không sửa. Không có cấu hình IMPROVED. |
