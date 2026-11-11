# Trạng thái thực hiện lab

- Phạm vi: hoàn thành bài chính và bonus; kiểm tra, commit và push sau từng bài.
- Ràng buộc: không thêm/sửa tests, fixtures, bộ eval hay grading; không ghi credentials. Báo cáo theo năm mục của `NOTES.md`, chỉ dùng kết quả thực tế.
- Cấu hình cố định bài chính: OpenAI `gpt-6-luna`, `reasoning_effort=none`, judge cùng model, snapshot, 8 bước, 22 case.
- Bài 1–2: code hiện có đáp ứng loop và xử lý lỗi. Kiểm tra `python3 -m unittest discover -s tests -v`: 35/37 pass; hai lỗi thuộc validation nguồn của Bài 4.
- Thay đổi chuẩn bị: `providers.py` đặt reasoning effort cho Luna; `.env` giữ ngoài Git.
- Tiếp theo: chạy baseline Bài 3, phân tích câu trả lời và trace, ghi `NOTES.md`, commit và push trước khi sửa agent.
- Mục tiêu cải tiến: xử lý đầy đủ một lỗi có bằng chứng; kiểm tra toàn bộ để phát hiện regression. Không suy diễn điểm hoặc độ ổn định từ một lần chạy.
