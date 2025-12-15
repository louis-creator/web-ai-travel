# AI Travel Planner (AI1 Recommender + AI2 Itinerary)

Web app gợi ý địa điểm và lập lịch trình du lịch trong ngày.

- **AI1 (Python + ML)**: Gợi ý địa điểm theo *sở thích* (tags) và *ngân sách*.
- **AI2 (Python + Gemini API)**: Tạo *timeline lịch trình* dựa trên danh sách địa điểm từ AI1, có di chuyển + ăn uống hợp lý.
- **Backend**: Node.js (Express) gọi Python scripts.
- **Frontend**: HTML/CSS/JS (UI 2 cột: AI1 & AI2).

---

## 1) Yêu cầu hệ thống

Cài sẵn:

1. **Node.js** (khuyến nghị bản LTS)
2. **Python 3.x**
3. (Khuyến nghị) Mở Terminal/PowerShell tại đúng thư mục dự án

---

## 2) Cấu trúc dự án (tóm tắt)

```
web-ai-travel/
├─ server.js
├─ ai1.py
├─ ai2.py
├─ data.json
├─ package.json
├─ .env                
└─ public/
   ├─ index.html
   ├─ style.css
   └─ script.js
```

> Lưu ý: `data.json` là dữ liệu địa điểm. AI1/AI2 đều đọc từ file này.

---

## 3) Cài đặt thư viện

### 3.1) Cài thư viện Node.js (Backend)

Trong thư mục dự án, chạy:

```bash
npm install
```

Nếu dự án chưa có `node_modules` hoặc bạn muốn cài thủ công:

```bash
npm i express body-parser dotenv
```

### 3.2) Cài thư viện Python (AI)

```bash
pip install pandas scikit-learn google-generativeai
```

> Nếu dùng Mac/Linux và `pip` không chạy, thử `pip3`.

---

## 4) Cấu hình Gemini API Key (Quan trọng)

AI2 cần Gemini API Key. Dự án hỗ trợ **nhiều API key** để tự đảo key khi gặp quota/rate limit.

### 4.1) Tạo file `.env`

Tạo file tên **.env** (cùng cấp với `server.js`) với nội dung:

```env
GEMINI_API_KEYS=KEY1,KEY2,KEY3
```

- Thay `KEY1,KEY2,KEY3` bằng key thật của bạn (có thể 1 hoặc nhiều key)
- Không thêm dấu ngoặc kép
- Không để dấu cách thừa

### 4.2) Lấy Gemini API Key ở đâu?

- Google AI Studio: https://aistudio.google.com/

---

## 5) Chạy dự án

### Bước 1: Start server

```bash
node server.js
```

Nếu thành công sẽ thấy:

```
Server running at http://localhost:3000
```

### Bước 2: Mở web

Mở trình duyệt và truy cập:

- http://localhost:3000

---

## 6) Cách sử dụng (cho người mới)

### 6.1) Chạy AI1 (Suggested Places)

1. Chọn **Interests** (Cuisine/History/Art/Nature/Religion…)
2. Nhập **Budget (VND)**  
   - Nếu để trống / nhập sai / nhập số âm → hệ thống tự dùng **500000**
3. Bấm **Run AI1** để nhận danh sách địa điểm gợi ý.

### 6.2) Chạy AI2 (Smart Itinerary)

1. Chọn **Start / End time**  
   - Nếu để trống → mặc định **08:00 – 17:00**
   - Nếu thời lượng < **2 giờ** → hệ thống sẽ báo lỗi và yêu cầu nhập lại
2. Bấm **Run AI2** để tạo timeline lịch trình.

**Lưu ý quan trọng:**
- AI2 **chỉ chạy khi AI1 đã có kết quả**
- AI2 **chỉ dùng các địa điểm do AI1 gợi ý**, không tự bịa địa điểm mới

---

## 7) Troubleshooting (lỗi thường gặp)

### 7.1) Lỗi “No Gemini API keys configured”
Nguyên nhân: chưa tạo `.env` hoặc `.env` không đúng vị trí.

Cách sửa:
- Đảm bảo `.env` nằm cùng thư mục với `server.js`
- Nội dung đúng dạng:
  ```env
  GEMINI_API_KEYS=KEY1,KEY2
  ```
- Tắt server và chạy lại `node server.js`

### 7.2) Lỗi Python: ModuleNotFoundError
Chưa cài đủ thư viện Python.

Chạy lại:
```bash
pip install pandas scikit-learn google-generativeai
```

### 7.3) AI2 báo lỗi quota / 429 / rate limit
Gemini key bị giới hạn lượt gọi (quota). Dự án sẽ tự:
- đổi sang key khác (nếu bạn cấu hình nhiều key trong `.env`)
- hoặc yêu cầu thử lại sau

### 7.4) Không thấy web hiển thị
- Kiểm tra server đã chạy chưa (terminal có dòng “Server running…”)
- Kiểm tra link: http://localhost:3000
- Nếu cổng 3000 bị chiếm, đổi `PORT` trong `server.js`

---

## 8) Ghi chú cho bài nộp/đánh giá

- AI1 dùng **CountVectorizer + Cosine Similarity** để tính độ phù hợp theo tags và lọc theo ngân sách.
- AI2 dùng **Gemini** để tạo lịch trình theo thời gian, có di chuyển và ăn uống hợp lý, chỉ dựa trên danh sách điểm từ AI1.
- Backend gọi Python bằng `child_process.spawn`, nhận dữ liệu JSON và trả về frontend.

---

Chúc bạn nộp bài thành công! 🚀

