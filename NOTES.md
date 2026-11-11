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

Các nhóm còn lại đã được đối chiếu answer và trace: scope/nguồn (A2, A8); timeout/injection (A3, A4, H5, H7); liên kết và dữ liệu dài (A6, H1, H6); tiền đề sai và giới hạn lịch sử (H2, H8). Không ghi nhận vi phạm cơ học ngoài H3, H4. H5 có cách ghi ngày “4–5 tháng 11” thiếu chính xác cho incident gộp mô tả hai khoảng ảnh hưởng ngày 4/11. Một số nhận xét của judge không đủ căn cứ: A1 có `captured_at` trong trace; A6 thực sự trả ba trong chín cập nhật; H1 phân biệt thời điểm tạo incident gốc với khoảng ảnh hưởng; H6 có trường `status: resolved` độc lập với phần body bị cắt. Không coi toàn bộ điểm dưới 100 là lỗi đã xác nhận.

## 3. Thay đổi đã thực hiện

- Làm rõ lựa chọn công cụ trong `SYSTEM_PROMPT` của `agent.py`: chỉ dùng tools khi cần bằng chứng trạng thái/incident; tra trực tiếp ID cần xác minh; lấy cả trạng thái dịch vụ và chi tiết incident nếu câu hỏi cần cả hai. Hai loại dữ liệu không thay thế nhau.
- Bổ sung nguyên tắc giữ mức chắc chắn của nguồn, phân biệt `created_at` với thời điểm ảnh hưởng, đối chiếu ngày/giờ và nêu giới hạn truncation/timeline. Các quy tắc áp dụng chung, không mã hóa câu hỏi, đáp án hoặc case ID.
- Lưu URL từ `get_incident_details` thành công. Nếu final answer không chứa URL nào đã lưu, ghi `validation_missing_source` và yêu cầu sửa trong ngân sách `max_steps`; hết bước trả `max_steps`. Không bắt URL khi chưa đọc incident thành công.
- Kiểm tra offline: 37/37 tests có sẵn đạt, gồm sửa câu trả lời thiếu URL, hết ngân sách và incident không tìm thấy; không thêm hoặc sửa tests.
- Hai thử nghiệm toàn bộ được giữ nguyên trong `evidence/core_candidate_1.json` và `core_candidate_2.json`. Lần đầu đạt 94,14 nhưng H2 thiếu `get_status`; lần tiếp đạt 96,41 nhưng H1 mâu thuẫn khi so sánh ngày và thiếu lưu ý truncation, E5 diễn đạt thời điểm tạo như lúc bắt đầu ảnh hưởng. Các quan sát này dẫn tới hai bổ sung quy tắc nêu trên.
- Kiểm chứng phiên bản cuối: 37/37 tests đạt; H4 chạy riêng đạt 100, E5 đạt 98, H1 đạt 93. Eval toàn bộ đạt 97,55/100; H3 và H4 đều 100, không có vi phạm cơ học. Đối chiếu answer/trace không phát hiện lại các regression đã nêu. Các kết quả thử nghiệm gốc được lưu trong `evidence/`.

## 4. So sánh hai lần chạy

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---|---|
| Điểm tổng | 92,73/100 | 97,55/100 |
| Điểm case đã chọn | H4: 50/100 | H4: 100/100 |
| Số model calls | Agent: 62; judge: 22 | Agent: 58; judge: 22 |
| Token, chi phí nếu có | Agent: 66.532; judge: 45.887 token | Agent: 69.129; judge: 40.272 token |

- Hai file dùng cùng cấu hình; kết quả toàn bộ đã được đối chiếu để kiểm tra Bài 4. Phân tích so sánh chi tiết được tổng hợp ở Bài 5.
- API trả token usage, không trả chi phí tiền tệ trong kết quả.

## 5. Giới hạn

Judge là phép đánh giá xấp xỉ và dùng cùng model với agent; một số giải thích không khớp hoàn toàn với trace. Snapshot ngày 09/11/2026 không xác nhận trạng thái thực tế tại thời điểm chạy. Danh sách incident và nội dung cập nhật đều có giới hạn; dữ liệu không đủ để chứng minh toàn bộ lịch sử hoặc quan hệ nhân quả. Một lần chạy mỗi phiên bản không chứng minh độ ổn định.
