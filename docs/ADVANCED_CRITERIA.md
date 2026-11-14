# Tiêu chí chọn pipeline — thử thách nâng cao

Tác giả: Trần Thái Hưng (2A202603557). Viết ngày 2026-11-15, **trước khi chạy agent trên dev và trước khi chạy test**. Đóng băng bằng sha256 ở [ADVANCED_CRITERIA_FROZEN.json](ADVANCED_CRITERIA_FROZEN.json).

**Thứ tự thực hiện (công khai):** (1) benchmark nâng cao được soạn từ ảnh trang gốc rồi đóng băng ([benchmark/advanced/FROZEN.json](../benchmark/advanced/FROZEN.json)); (2) trích xuất hình bằng model vision cho cả 280 trang và dựng index, không dùng câu hỏi nào; (3) tiêu chí này được viết và đóng băng; (4) chạy dev; (5) chốt pipeline; (6) chạy test một lần. Ngoại lệ đã ghi ở benchmark/advanced/README.md: 5 trang mẫu (28, 46, 132, 136, 141) được trích xuất thử để kiểm tra prompt trước khi soạn câu hỏi.

## 1. Cố định ở mọi cấu hình

| Mục | Giá trị |
|---|---|
| Tài liệu và index | 280 trang; chunk văn bản (đoạn ≤ 800 ký tự) + một chunk cho mỗi hình, bảng, sơ đồ (`src/adv_index.py`); embedding `text-embedding-3-small` |
| Model | `gpt-6.1-terra` cho trích xuất, agent và bộ chấm hỗ trợ; Responses API, reasoning mặc định (model không nhận `temperature`), nên các lần chạy không lặp lại hoàn toàn |
| Truy xuất | hybrid RRF (k = 60), độ sâu 30 mỗi bên, top-6 chunk mỗi lượt tìm |
| Agent | tool `search_documents`, `answer`, `abstain`; tối đa 3 lượt tìm; yêu cầu lượt tìm thứ 4 hoặc citation không hợp lệ (ID phải có trong context và xuất hiện `[id]` trong câu trả lời) → từ chối |
| Context | ngân sách 9000 ký tự (chunk dài bị cắt có đánh dấu) |
| Ảnh trang | cấu hình PAGES: ảnh gốc của tối đa 3 trang đầu trong kết quả mỗi lượt tìm, render ở scale 2,0 |
| Prompt | `src/adv_agent.py`, `SYSTEM_PROMPT`; cùng nội dung ở mọi cấu hình |
| Dữ liệu cấm | gold, đáp án và evidence không vào agent; agent chỉ nhận câu hỏi |

## 2. Ứng viên (chạy trên dev, 18 câu)

| ID | Mô tả | Giả thuyết |
|---|---|---|
| TEXT | Chỉ chunk văn bản, không ảnh | Mốc của pipeline cơ bản mở rộng ra 280 trang; chữ trong biểu đồ vector vẫn nằm trong lớp văn bản |
| VISUAL | Chunk văn bản + chunk hình do model vision trích xuất | Mô tả hình giúp tìm đúng hình/bảng/sơ đồ và đọc cấu trúc |
| PAGES | VISUAL + ảnh gốc của các trang đầu | Model nhìn trực tiếp hình nên đọc đúng trục, chú giải, nhãn nhỏ, mũi tên |

Được thêm **tối đa một** cấu hình cải thiện (IMPROVED) sau khi phân tích lỗi dev. Cấu hình đó và giả thuyết phải được ghi vào `docs/ADVANCED_DEV_NOTES.md` **trước khi** chạy nó, chạy trên dev và chọn bằng cùng quy tắc ở mục 4. Không chạm test.

## 3. Chỉ số trên dev

- **pass_auto** (mỗi câu): câu có đáp án đạt khi agent *trả lời*, bộ chấm hỗ trợ (cùng model, chấm nghiêm theo đáp án chuẩn, đơn vị và dung sai) cho là đúng, **và** các chunk được trích dẫn bao phủ mọi trang gold. Câu thiếu bằng chứng đạt khi agent từ chối. Lỗi hệ thống, timeout hoặc không có kết quả tính là không đạt và vẫn nằm trong mẫu số.
- Báo `n/18` tổng và theo nhóm; số lượt tìm; ngữ cảnh có chứa trang gold; token đầu vào, đầu ra, reasoning; thời gian trung vị. **Chi phí báo bằng token** vì đơn giá của `gpt-6.1-terra` chưa rõ.
- Bộ chấm hỗ trợ dùng cùng model với agent nên có thể thiên lệch; các câu dev không đạt được đọc tay, và test được đọc tay từng câu (mục 5).

## 4. Quy tắc chọn (áp theo thứ tự)

1. Số câu pass_auto trên dev cao hơn thắng; **chênh ≤ 1 câu coi là hòa**.
2. Hòa → tổng token đầu vào + đầu ra của agent ít hơn thắng.
3. Vẫn hòa → cấu hình đơn giản hơn (TEXT < VISUAL < PAGES).

Không dò thêm trên dev: top-k, độ sâu, RRF k, ngân sách context, số trang ảnh và nội dung system prompt. Chỉ sửa **lỗi kỹ thuật** (không dựa vào điểm dev), và mỗi lần sửa ghi vào `docs/ADVANCED_DEV_NOTES.md` cùng số lần chạy dev bị hủy.

## 5. Quy trình test

1. Chốt cấu hình trên dev, ghi vào `docs/ADVANCED_DEV_NOTES.md`.
2. Chạy **toàn bộ 30 câu test một lần** (`--final-test`), lưu trace retrieval, context, tool call, câu trả lời, citation, thời gian, token và lỗi từng câu. Không sửa mã hoặc prompt sau khi đã nhìn test; nếu lỗi hệ thống buộc chạy lại, ghi nguyên nhân và không đổi cấu hình.
3. **Đọc và ghi nhãn từng câu** đạt/không đạt kèm lý do, đối chiếu với ảnh trang gốc (bảng chấm `src/adv_review.py`); bộ chấm hỗ trợ chỉ là lượt đầu và không thay việc đối chiếu này.
4. Tỷ lệ đạt = số câu đạt / 30, **không làm tròn**; cần ≥ 27/30. Báo theo từng nhóm, số lỗi hệ thống, thời gian và token. Nếu dưới ngưỡng thì báo đúng kết quả, không chọn câu.
