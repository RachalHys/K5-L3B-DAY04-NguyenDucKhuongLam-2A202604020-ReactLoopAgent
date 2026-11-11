# Trạng thái thực hiện lab

- Phạm vi: hoàn thành bài chính và bonus; kiểm tra, commit và push sau từng bài.
- Ràng buộc: không thêm/sửa tests, fixtures, bộ eval hay grading; không ghi credentials. Báo cáo theo năm mục của `NOTES.md`, chỉ dùng kết quả thực tế.
- Cấu hình cố định bài chính: OpenAI `gpt-6-luna`, `reasoning_effort=none`, judge cùng model, snapshot, 8 bước, 22 case.
- Bài 1–2: code hiện có đáp ứng loop và xử lý lỗi. Kiểm tra `python3 -m unittest discover -s tests -v`: 35/37 pass; hai lỗi thuộc validation nguồn của Bài 4.
- Thay đổi chuẩn bị: `providers.py` đặt reasoning effort cho Luna; `.env` giữ ngoài Git.
- Bài 3: `eval_before.json` đủ 22 case, 92,73/100; cấu hình đúng như trên. Agent 62 calls/66.532 token, judge 22 calls/45.887 token.
- Đã kiểm tra answer/trace: H4 gọi tool trái yêu cầu, H3 chưa tra cứu ID trực tiếp; cả hai 50 điểm. Chọn H4 làm case chính, làm rõ lựa chọn công cụ trong prompt; hoàn thành validation nguồn bắt buộc. Một số nhận xét judge khác không khớp trace, đã phân biệt trong `NOTES.md`.
- Tiếp theo: commit/push Bài 3, sau đó triển khai Bài 4; chạy tests có sẵn và H3/H4 trước full eval Bài 5. Chưa sửa agent baseline.
- Mục tiêu cải tiến: xử lý đầy đủ một lỗi có bằng chứng; kiểm tra toàn bộ để phát hiện regression. Không suy diễn điểm hoặc độ ổn định từ một lần chạy.
