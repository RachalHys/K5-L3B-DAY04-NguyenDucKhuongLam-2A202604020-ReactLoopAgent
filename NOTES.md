# Ghi chú phân tích · Day 04

Họ và tên: Nguyễn Đức Khương Lam

MSSV: 2A202604020

## 1. Case được chọn

Case được chọn là H4. Người dùng yêu cầu viết thơ về biển và nói rõ không kiểm tra GitHub hay Cloudflare, nhưng agent vẫn gọi status tools của cả hai provider trước khi trả bài thơ. H4 chỉ đạt **50/100** sau khi áp trần, dù điểm judge là 85. Điểm toàn bộ lần đánh giá đầu là **92,73/100**. Mục tiêu cải tiến là loại bỏ những lần gọi tool không cần thiết này.

## 2. Bằng chứng trong trace

```text
Trước cải tiến — H4:
  Step 1: get_status(provider=github)
  Step 2: get_status(provider=cloudflare)
  Step 3: stop; trả lời bằng bài thơ.

Sau cải tiến — H4:
  Step 1: stop; trả lời bằng bài thơ, không gọi tool.
```

Trace cho thấy agent đã lấy dữ liệu status dù không cần để trả lời. Nguyên nhân có thể là prompt ban đầu chưa nêu rõ khi nào cần bỏ qua tool, đặc biệt khi người dùng đã yêu cầu không tra cứu.

Ở H3, người dùng cung cấp ID incident nhưng agent chỉ tra danh sách gần đây bằng `get_status`. Danh sách bị rút gọn không đủ để xác minh ID; agent cần gọi `get_incident_details`. H3 cũng chỉ đạt 50 ở lần đầu.

## 3. Thay đổi đã thực hiện

Prompt trong `agent.py` yêu cầu chỉ dùng tool khi cần dữ liệu status hoặc incident. Với ID cụ thể, agent tra trực tiếp bằng `get_incident_details`. Các hướng dẫn bổ sung yêu cầu phân biệt status trong snapshot với incident lịch sử, tách `overall` khỏi `component` và không dùng `created_at` hay `updated_at` làm thời điểm ảnh hưởng.

Agent lưu URL của các incident đã đọc thành công. Nếu câu trả lời thiếu URL, vòng lặp ghi `validation_missing_source` và yêu cầu model sửa trong số bước còn lại. Link không có trong tool output tạo event `validation_unobserved_source` và phải được bỏ hoặc sửa. Khi tra cứu thất bại, agent không bắt buộc dẫn URL incident.

Với snapshot, agent theo dõi các truy vấn đã thành công. Nếu một lượt chỉ lặp lại các truy vấn này, agent ngừng gửi tool schemas và yêu cầu model trả lời từ dữ liệu đã có. Lượt có truy vấn mới hoặc lỗi cần xử lý vẫn được tiếp tục trong `max_steps`. Cơ chế này không áp dụng khi chạy live.

Phần bonus sử dụng `tools.schemas` và `tools.system_prompt` do bộ tools cung cấp. Agent dừng sau tối đa ba lỗi 429 cho cùng tool và provider, hoặc dừng sớm theo `Retry-After` và `retriable`. Arguments cùng số lần lỗi được trả lại cho model để retry đúng truy vấn và báo rõ phần chưa xác minh được.

Sau khi hoàn thiện, **37 tests trong `tests/` và 3 tests trong `bonus/` đều đạt**.

## 4. So sánh hai lần chạy

Hai lần đánh giá bài chính đều dùng OpenAI `gpt-6-luna` cho agent và judge, với `reasoning_effort=none`, cùng snapshot, dataset và `max_steps=8`. Bộ bonus giữ model này và dùng `max_steps=16`. Cả 32 case đều hoàn thành, có điểm và không vi phạm các điều kiện kiểm tra tự động của bộ eval.

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---:|---:|
| Điểm tổng | 92,73/100 | 98,64/100 |
| H4 | 50/100 | 100/100 |
| Số lần gọi model (agent / judge) | 62 / 22 | 57 / 22 |
| Số token (agent / judge) | 66.532 / 45.887 | 73.107 / 39.329 |
| Chi phí ước tính, gồm judge | 0.016348 USD | 0.013358 USD |

| Case | Trước | Sau | Case | Trước | Sau |
|---|---:|---:|---|---:|---:|
| E1 | 100 | 100 | A6 | 89 | 95 |
| E2 | 100 | 100 | A7 | 100 | 100 |
| E3 | 100 | 100 | A8 | 95 | 100 |
| E4 | 100 | 98 | H1 | 92 | 96 |
| E5 | 90 | 97 | H2 | 100 | 100 |
| E6 | 100 | 100 | H3 | 50 | 97 |
| A1 | 95 | 97 | H4 | 50 | 100 |
| A2 | 100 | 100 | H5 | 90 | 96 |
| A3 | 99 | 98 | H6 | 94 | 100 |
| A4 | 100 | 99 | H7 | 99 | 99 |
| A5 | 99 | 99 | H8 | 98 | 99 |

Điểm bài chính tăng **5,91 điểm**. H4 tăng từ 50 lên 100 sau khi bỏ hai tool calls không cần thiết. H3 đã tra đúng ID, bỏ URL không có trong tool output và tăng lên 97. H6 đọc tiếp incident được dẫn trong thông báo, nêu rõ nội dung bị cắt và đạt 100. Tuy vậy, E4, A3 và A4 giảm 1–2 điểm; kết quả chưa cho thấy cải thiện đồng đều ở mọi case.

Bộ bonus đạt **99,10/100**, tương ứng **14,86/15 điểm**. Agent dùng **40 lần gọi model, 104.205 token**; judge dùng **10 lần gọi, 33.577 token**.

| Case | Điểm | Case | Điểm |
|---|---:|---|---:|
| B1 | 100 | B6 | 96 |
| B2 | 100 | B7 | 100 |
| B3 | 100 | B8 | 100 |
| B4 | 100 | B9 | 99 |
| B5 | 100 | B10 | 96 |

Ở B2, agent đọc ba trang với offset 0, 3 và 6 để tìm thông báo về GitHub upstream. B3 retry thành công sau một lần gặp 429. B4 dừng sau ba lần lỗi 429 và báo rõ chưa xác minh được Vercel, trong khi vẫn trả kết quả GitHub. B5 xử lý được lỗi format giả lập rồi gọi lại thành công. B6 chọn đúng thông tin giữa các mục nhiễu; B7 không làm theo prompt injection trong tool output.

Chi phí được ước tính từ usage của agent và judge theo [giá Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), với giá Standard và [cache-write 30 phút](https://developers.openai.com/api/docs/guides/prompt-caching). Chi phí của bộ bonus khoảng **0.009114 USD**. Các số liệu này chỉ tính các file eval nộp kèm, không bao gồm toàn bộ quá trình thực hiện lab.

Chạy `python3 demo.py` để xem trace nhiều bước của H6 và so sánh H4 trước, sau cải tiến. Demo đọc các file eval đã lưu nên không cần gọi API.

## 5. Giới hạn

Điểm judge chỉ là kết quả đánh giá gần đúng. Việc dùng cùng model cho agent và judge có thể gây thiên lệch; một bộ kết quả cho mỗi phiên bản chưa đủ để kết luận hệ thống hoạt động ổn định. Kiểm tra URL cũng chỉ xác nhận link đã xuất hiện trong tool output, chưa chứng minh mọi nội dung trong câu trả lời đều có căn cứ.

Agent vẫn còn truy vấn không cần thiết. Ở B9, agent gọi năm status tools dù không có tool cho các provider được hỏi. Ở B4, agent đọc thêm timeline GitHub ngoài yêu cầu kiểm tra status. B8 đạt 100 nhưng vẫn gọi mốc thông báo điều tra Vercel là lúc bắt đầu sự cố, trong khi dữ liệu không xác nhận thời điểm bắt đầu ảnh hưởng. Kết quả B8 cho thấy judge vẫn có thể bỏ sót sai sót trong câu trả lời.

Dữ liệu snapshot được lưu ngày 09–10/11/2026, nên không phản ánh status tại thời điểm chạy. Cơ chế retry khi chạy live chưa được kiểm chứng thực tế.
