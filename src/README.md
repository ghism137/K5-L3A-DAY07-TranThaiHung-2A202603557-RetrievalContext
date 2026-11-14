# Code Day 7

Code dùng lại từ Day 6 (`store`, `embeddings`, `chunking`, `ingestion`, `corpus`, `textutil`, `models`) được copy nguyên, chỉ sửa `config.py` (đường dẫn theo repo Day 7) và một thông báo lỗi trong `embeddings.py`. Chỉ mục (index) `A` = cửa sổ cố định 800/100 ký tự (376 chunk), `B` = gom đoạn tối đa 800 ký tự (429 chunk), cùng model `text-embedding-3-small` (1536 chiều) như Day 6.

| File | Công dụng |
|---|---|
| `config.py` | Đường dẫn, phạm vi corpus, giới hạn chunk (giữ nguyên Day 6) |
| `store.py` | pgvector: `search(strategy, query_vector, top_k, filters)`, filter SQL trên `chapter`/`section`/`chapter_title` |
| `embeddings.py` | `OpenAIEmbedder.embed_query/embed_documents`, đếm token và chi phí |
| `corpus.py`, `chunking.py`, `ingestion.py`, `textutil.py`, `models.py` | PDF → trang → chunk (tái tạo index khi cần) |
| `export_chunks.py` | Xuất chunk từ DB sang schema Day 7 → `data/index/chunks_{A,B}.json` (cho retriever lexical) |
| `build_benchmark.py`, `verify_benchmark.py` | Dựng và kiểm chứng benchmark ([benchmark/README.md](../benchmark/README.md)) |
| `check_setup.py` | Kiểm tra DB, key và một truy vấn thật |
| `retrieval.py` | Ba phương pháp retrieval: dense (pgvector), BM25 (tự cài), hybrid RRF |
| `run_retrieval.py` | So sánh 3 phương pháp × index A/B, chỉ retrieval (không LLM); mặc định chỉ dev |
| `run_retrieval_variants.py` | Đánh giá riêng C1 (viết lại truy vấn) và C2 (gộp chunk) ở mức retrieval, kèm đối chứng; chỉ dev, phân tích bổ sung |
| `agent.py` | Agent OpenAI tool calling (`search_documents`, `answer`, `abstain`), dựng context, cấu hình R0 / BASE / C1 / C2 |
| `run_agent.py` | Chạy agent trên benchmark, ghi trace và tổng hợp tự động; `--final-test` chỉ chạy một lần |
| `make_review_sheet.py`, `finish_review.py` | Dựng bảng chấm tay ẩn tên cấu hình; tổng hợp nhãn bằng `starter/agent_metrics.py` |

## Chạy lần đầu

```bash
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt   # Windows; Linux/macOS: .venv/bin/python
cp .env.example .env            # tự điền OPENAI_API_KEY (và AGENT_MODEL); không commit .env
docker compose up -d            # vector store Day 7: 127.0.0.1:55434
python -m src.check_setup
```

**File PDF nguồn không được commit** (14 MB, CC BY 3.0 IGO; đã ghi trong `.gitignore`). Tải *International Debt Report 2026* từ <https://hdl.handle.net/10986/45762>, lưu thành `data/international-debt-report-2026.pdf` và kiểm tra sha256 trùng `PDF_SHA256` trong `src/config.py`. Cần PDF để chạy `verify_benchmark` (kiểm tra câu thiếu evidence trên cả 280 trang) và để tái tạo index; chạy retrieval trên index đã nạp thì không cần. Chunk đã xuất (`data/index/chunks_{A,B}.json`) được commit để chạy BM25.

Dữ liệu vector được chuyển từ container Day 6 bằng `pg_dump --table=chunks` rồi restore; hash `md5(strategy, chunk_id, content_hash, embedding)` của hai DB trùng nhau, nên đây chính là index Day 6 (không embed lại). Nếu DB rỗng, tái tạo từ PDF cần thêm bước nạp (code `ingest` của Day 6 trong `run.py` chưa được copy; `corpus.build_chunks` + `store.upsert` + `embeddings.embed_documents` là đủ, chi phí ≈ 0,002 USD).

Chạy test của giảng viên trên Windows cần `PYTHONUTF8=1`: một test dùng `read_text()` không chỉ định encoding.
