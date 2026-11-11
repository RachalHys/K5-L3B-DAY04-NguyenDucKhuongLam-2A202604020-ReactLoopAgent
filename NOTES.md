# Ghi chú phân tích · Day 04

Họ và tên: Nguyễn Đức Khương Lâm
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

- Chưa thay đổi agent ở giai đoạn baseline.
- Dự kiến: làm rõ điều kiện sử dụng công cụ và tra cứu ID trong `SYSTEM_PROMPT`; bổ sung validation URL nguồn theo contract bắt buộc của Bài 4. Không mã hóa riêng câu hỏi, case ID hoặc incident ID.

## 4. So sánh hai lần chạy

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---|---|
| Điểm tổng | 92,73/100 | Chưa chạy |
| Điểm case đã chọn | H4: 50/100 | Chưa chạy |
| Số model calls | Agent: 62; judge: 22 | Chưa chạy |
| Token, chi phí nếu có | Agent: 66.532; judge: 45.887 token | Chưa chạy |

- Chưa đánh giá cải tiến; baseline giữ nguyên để so sánh.
- API trả token usage, không trả chi phí tiền tệ trong kết quả.

## 5. Giới hạn

Judge là phép đánh giá xấp xỉ và dùng cùng model với agent; một số giải thích không khớp hoàn toàn với trace. Snapshot ngày 09/11/2026 không xác nhận trạng thái thực tế tại thời điểm chạy. Danh sách incident và nội dung cập nhật đều có giới hạn; dữ liệu không đủ để chứng minh toàn bộ lịch sử hoặc quan hệ nhân quả. Một lần chạy mỗi phiên bản không chứng minh độ ổn định.
