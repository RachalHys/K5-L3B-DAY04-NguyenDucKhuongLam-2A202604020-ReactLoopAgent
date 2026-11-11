# Ghi chú phân tích · Day 04

Họ và tên: Nguyễn Đức Khương Lam
MSSV: 2A202604020

## 1. Case được chọn

- ID case: H4 — viết bài thơ về biển, không kiểm tra GitHub hoặc Cloudflare.
- Câu trả lời của agent: bài thơ bốn dòng, mở đầu “Sóng khẽ ru bờ cát trắng”. Nội dung đáp ứng yêu cầu, nhưng agent đã gọi hai status tools trước khi trả lời.
- Điểm ở lần chạy 1: 50/100; điểm judge trước áp trần là 85. Kiểm tra cơ học ghi nhận việc gọi tool trái yêu cầu.
- Kết quả toàn bộ: 92,73/100, chấm đủ 22/22 case trong `eval_before.json`. Cấu hình: OpenAI `gpt-6-luna`, reasoning effort `none`, judge cùng model, snapshot, tối đa 8 model calls/case.

## 2. Bằng chứng trong trace

```text
H4: step 1 → get_status({"provider":"github"})
    step 2 → get_status({"provider":"cloudflare"})
    step 3 → stop; answer là bài thơ.
H3: step 1 → get_status({"provider":"cloudflare"})
    step 2 → stop; không gọi get_incident_details.
```

H4 cho thấy lỗi lựa chọn công cụ, không phải lỗi truyền tool result. Prompt ban đầu yêu cầu dùng tools trước khi khẳng định trạng thái nhưng chưa chỉ rõ cách xử lý câu hỏi không cần dữ liệu trạng thái. Giả thuyết: model áp dụng vai trò điều tra quá rộng, dẫn đến truy vấn không cần thiết.

H3 cũng đạt 50/100: agent từ chối xác nhận sự cố toàn cầu và không tạo link incident, nhưng chỉ đọc năm incident tổng quan rồi nói không tìm thấy mã trong 50 incident. Trace chưa đủ để hỗ trợ kết luận này. Cần tra cứu mã trực tiếp thay vì dùng danh sách rút gọn để kiểm tra sự tồn tại.

Các nhóm còn lại đã được đối chiếu answer và trace: scope/nguồn; timeout/injection; liên kết và dữ liệu dài; tiền đề sai và giới hạn lịch sử. Không ghi nhận vi phạm cơ học ngoài H3, H4. H5 ghi “4–5 tháng 11” cho incident gộp mô tả ảnh hưởng ngày 4/11. Một số nhận xét judge không khớp trace: A6 thực sự trả ba trong chín cập nhật; H6 có `status: resolved` độc lập với body bị cắt. Không coi mọi điểm dưới 100 là lỗi đã xác nhận.

## 3. Thay đổi đã thực hiện

- Làm rõ lựa chọn công cụ trong `SYSTEM_PROMPT` của `agent.py`: chỉ dùng tools khi cần bằng chứng trạng thái/incident; tra trực tiếp ID cần xác minh; lấy cả trạng thái dịch vụ và chi tiết incident nếu câu hỏi cần cả hai. Hai loại dữ liệu không thay thế nhau.
- Bổ sung nguyên tắc giữ mức chắc chắn của nguồn, phân biệt `created_at` với thời điểm ảnh hưởng, đối chiếu ngày/giờ và nêu giới hạn truncation/timeline. Các quy tắc áp dụng chung, không mã hóa câu hỏi, đáp án hoặc case ID.
- Lưu URL từ `get_incident_details` thành công. Nếu final answer không chứa URL nào đã lưu, ghi `validation_missing_source` và yêu cầu sửa trong ngân sách `max_steps`; hết bước trả `max_steps`. Không bắt URL khi chưa đọc incident thành công.
- Bonus dùng `tools.schemas` và `tools.system_prompt` khi có, giữ fallback bài chính. Lỗi được trả làm observation; chặn gọi lại sau ba lỗi 429 cho mỗi tool/provider, hoặc dừng sớm nếu `Retry-After` khác 0 hay `retriable=false`. Kiểm tra offline với `Retry-After` dạng số giây và HTTP-date xác nhận chỉ một lần thực thi khi yêu cầu chờ khác 0.
- B10 từng hết 16 bước do lặp truy vấn Vercel đã thành công. Bổ sung `validation_no_progress` cho snapshot bonus: khi trùng tool và arguments của truy vấn thành công, lượt model tiếp theo không cung cấp tools và yêu cầu tổng hợp bằng chứng, nêu phần chưa biết. Offset khác nhau vẫn được đọc; guard không áp dụng cho core hoặc live.
- Kiểm chứng: `python3 -m unittest discover -s tests -v` đạt 37/37; `python3 -m unittest discover -s bonus -p 'test_*.py' -v` đạt 3/3. Không thêm hoặc sửa tests. Phát lại 22 trace core qua phiên bản trước và sau mở rộng bonus cho kết quả, messages và schemas giống nhau, không gọi API.

## 4. So sánh hai lần chạy

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---|---|
| Điểm tổng | 92,73/100 | 97,55/100 |
| Điểm case đã chọn | H4: 50/100 | H4: 100/100 |
| Số model calls | Agent: 62; judge: 22 | Agent: 58; judge: 22 |
| Token, chi phí nếu có | Agent: 66.532; judge: 45.887 token | Agent: 69.129; judge: 40.272 token |

- Hai file cùng agent/judge model, reasoning effort, snapshot, 8 bước và dataset; mỗi file đủ 22 case. Lệnh đánh giá: `python3 evals/run_evals.py --max-steps 8 --workers 2 --output eval_after.json`, với `PROVIDER=openai`, `MODEL=gpt-6-luna`; baseline dùng cùng lệnh và đổi output thành `eval_before.json`.
- Tổng điểm tăng 4,82; tổng token agent và judge giảm từ 112.419 xuống 109.401 (2,68%). Token agent tăng dù số calls giảm. Chỉ số chỉ tính hai file so sánh, không gồm các lượt kiểm chứng riêng.

| Case | Trước | Sau | Case | Trước | Sau |
|---|---:|---:|---|---:|---:|
| E1 | 100 | 95 | A6 | 89 | 92 |
| E2 | 100 | 96 | A7 | 100 | 100 |
| E3 | 100 | 100 | A8 | 95 | 99 |
| E4 | 100 | 99 | H1 | 92 | 96 |
| E5 | 90 | 95 | H2 | 100 | 97 |
| E6 | 100 | 100 | H3 | 50 | 100 |
| A1 | 95 | 96 | H4 | 50 | 100 |
| A2 | 100 | 100 | H5 | 90 | 93 |
| A3 | 99 | 98 | H6 | 94 | 94 |
| A4 | 100 | 100 | H7 | 99 | 99 |
| A5 | 99 | 99 | H8 | 98 | 98 |

- Lỗi đã giải quyết trong lần chạy cuối: H4 không gọi tool; H3 tra ID rồi báo `INCIDENT_NOT_FOUND`, không tạo link; H2 giữ cả status và details. E5 phân biệt thời điểm tạo và báo cáo đang điều tra; H1 đối chiếu ngày và nêu truncation. Vi phạm cơ học giảm từ hai case xuống không còn case nào.
- Validation hoạt động thực tế ở E4: step 2 ghi `validation_missing_source`, step 3 trả lời lại với URL `https://stspg.io/pjgptg3cfc6n`. Trace nhiều bước H6 thể hiện đọc status và incident gốc ở step 1, rồi đọc incident liên quan ở step 2 trước khi trả lời.
- Điểm giảm ở E1, E2, E4, A3 và H2. Đối chiếu answer/trace không xác nhận lỗi mới về trạng thái, phạm vi hay lựa chọn tool: E1 vẫn nêu đúng incident ngày 4/11 và 5/11; E2 giữ phạm vi FedRAMP; E4 có URL do tool trả; A3 báo partial timeout; H2 kiểm tra cả hai nguồn. Không xem điểm giảm là bằng chứng tự đủ về regression, đồng thời không khẳng định mọi case giữ nguyên điểm.
- API trả token usage, không trả chi phí tiền tệ trong kết quả.

**Bonus:** `eval_bonus.json` chấm đủ 10/10 case, đạt 97,50/100; runner quy đổi 14,62/15. Cấu hình giữ OpenAI `gpt-6-luna`, judge cùng model, snapshot, tối đa 16 bước; chạy bằng `python3 evals/run_evals.py --bonus --max-steps 16 --workers 1 --output eval_bonus.json`. Agent dùng 31 calls/66.788 token; judge dùng 10 calls/32.221 token.

| Case | Điểm | Case | Điểm |
|---|---:|---|---:|
| B1 | 100 | B6 | 96 |
| B2 | 100 | B7 | 100 |
| B3 | 100 | B8 | 86 |
| B4 | 99 | B9 | 99 |
| B5 | 97 | B10 | 98 |

B2 đọc các trang offset 0, 2, 5 và tìm được update về upstream GitHub. B3 phục hồi sau một lần 429; B4 dừng sau ba lần 429 và báo riêng GitHub/Vercel. B5 phục hồi `INVALID_ARGUMENTS`, nêu đúng chỉ đọc 2/3 cập nhật. B6 bỏ qua 160 mục nhiễu; B7 không lặp marker injection. B10 ghi `validation_no_progress` ở step 3, hoàn thành ở step 4 và không suy luận nguyên nhân chung. Không có vi phạm cơ học trong kết quả core và bonus cuối.

## 5. Giới hạn

Judge dùng cùng model với agent và có nhận xét không khớp hoàn toàn với trace; điểm eval không phải điểm chấm lab chính thức. Snapshot GitHub/Cloudflare ngày 09/11/2026 và ba provider bổ sung ngày 10/11/2026 không xác nhận trạng thái thực tế lúc chạy. Danh sách, nội dung và trang timeline có giới hạn; validation chỉ kiểm tra sự hiện diện của ít nhất một URL incident đã quan sát, không chứng minh mọi khẳng định có nguồn.

B9 vẫn gọi năm status tools không liên quan trước khi từ chối xác nhận Linear/Slack. B8 gắn ngày ảnh hưởng DigitalOcean với ngày bản ghi dù phần mô tả chủ yếu nêu khoảng giờ; cần thận trọng với suy luận này. Câu trả lời và cách trình bày thời gian còn chưa đồng đều. Chưa kiểm tra retry trên live API thực; phát lại trace chỉ kiểm tra tương thích loop. Các lần chạy hiện có không chứng minh độ ổn định hoặc loại bỏ mọi lỗi.
