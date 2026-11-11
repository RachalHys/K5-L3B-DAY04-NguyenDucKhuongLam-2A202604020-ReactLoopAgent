# Trạng thái thực hiện lab

- Phạm vi: hoàn thành bài chính và bonus; kiểm tra, commit và push sau từng bài.
- Ràng buộc: không thêm/sửa tests, fixtures, bộ eval hay grading; không ghi credentials. Báo cáo theo năm mục của `NOTES.md`, chỉ dùng kết quả thực tế.
- Cấu hình cố định bài chính: OpenAI `gpt-6-luna`, `reasoning_effort=none`, judge cùng model, snapshot, 8 bước, 22 case.
- Bài 1–2: code hiện có đáp ứng loop và xử lý lỗi. Kiểm tra `python3 -m unittest discover -s tests -v`: 35/37 pass; hai lỗi thuộc validation nguồn của Bài 4.
- Thay đổi chuẩn bị: `providers.py` đặt reasoning effort cho Luna; `.env` giữ ngoài Git.
- Bài 3: `eval_before.json` đủ 22 case, 92,73/100; cấu hình đúng như trên. Agent 62 calls/66.532 token, judge 22 calls/45.887 token.
- Đã kiểm tra answer/trace: H4 gọi tool trái yêu cầu, H3 chưa tra cứu ID trực tiếp; cả hai 50 điểm. Chọn H4 làm case chính, làm rõ lựa chọn công cụ trong prompt; hoàn thành validation nguồn bắt buộc. Một số nhận xét judge khác không khớp trace, đã phân biệt trong `NOTES.md`.
- Bài 3 đã push tại `a9a140a`. Tên đúng: Nguyễn Đức Khương Lam, đã sửa trong `NOTES.md`.
- Bài 4 đang kiểm chứng, chưa commit: `agent.py` bổ sung hai quy tắc chọn tool và validation URL; 37/37 tests pass. Hai eval riêng H3/H4 đạt 100/100; kết quả nguyên gốc ở `evidence/`.
- Full candidate đầu: 94,14/100, H3/H4 100 nhưng H2 bỏ get_status (50 điểm). Kết quả giữ nguyên ở `evidence/core_candidate_1.json`; chưa commit phiên bản này.
- Đã làm rõ trong cùng quy tắc chọn tool: trạng thái dịch vụ và trạng thái incident cần hai nguồn khác nhau khi câu hỏi cần cả hai. Tests vẫn 37/37; eval riêng H2/H3/H4 đều 100 (`evidence/bai4_h2.json`, `bai4_h3_final.json`, `bai4_h4_final.json`).
- Full candidate 2: 96,41/100; H4/H2 100, không vi phạm cơ học. H1 có mâu thuẫn so sánh ngày và thiếu cảnh báo truncation; E5 coi created_at như thời điểm bắt đầu ảnh hưởng. Kết quả gốc ở `evidence/core_candidate_2.json`.
- Bổ sung quy tắc bám sát mức chắc chắn của nguồn, phân biệt created_at, đối chiếu thời gian và nêu truncation. Kiểm chứng riêng: H1 93, E5 98, H4 100; đọc answer/trace xác nhận các lỗi vừa nêu không xuất hiện trong các lần kiểm chứng này. Tests 37/37.
- Full core cuối đã hoàn tất: `eval_after.json` 97,55/100, đủ 22 case; H3/H4 100, không vi phạm cơ học. Đã đọc answer/trace các case: không thấy tái diễn regression H2/H1/E5. Điểm giảm E1/E2/E4/A3/H2 được phân biệt với lỗi thực tế; chưa có bảo đảm ổn định nhiều lần.
- Bài 4 đã commit/push tại `86a796d`. Bài 5 đã đối chiếu đầy đủ 22 case, cùng config; 97,55 so với 92,73 (+4,82). Agent 58 calls/69.129 token; judge 22 calls/40.272 token; tổng token giảm 2,68%. URL gate hoạt động thực tế ở E4.
- Chuẩn bị commit/push Bài 5 (`eval_after.json`, `NOTES.md`); không còn eval đang chạy. Tiếp theo bonus: hỗ trợ schemas/system prompt từ tools, giới hạn retry và Retry-After, tests bonus có sẵn, eval 10 case và ghi kết quả.
- Người thực hiện yêu cầu mở rộng cải tiến cho các lỗi có bằng chứng để hướng tới gần 100, nhưng giữ nguyên nội dung mặc định của bộ đánh giá. Phạm vi sửa hiện chỉ agent và cấu hình tương thích Luna đã push.
- Mục tiêu cải tiến: xử lý đầy đủ một lỗi có bằng chứng; kiểm tra toàn bộ để phát hiện regression. Không suy diễn điểm hoặc độ ổn định từ một lần chạy.
