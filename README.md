
-----

# 📘 HƯỚNG DẪN CÀI ĐẶT & CHẠY DỰ ÁN AI TRAVEL PLANNER

Dự án Web App gợi ý địa điểm và lập lịch trình du lịch tự động sử dụng **Node.js** (Backend), **Python** (AI Logic) và **Gemini API**.

-----

## 1\. Yêu Cầu Hệ Thống (Prerequisites)

Trước khi bắt đầu, hãy chắc chắn máy tính của bạn đã cài đặt 2 phần mềm sau:

1.  **Node.js** (Phiên bản LTS): [Tải tại đây](https://nodejs.org/)
2.  **Python** (Phiên bản 3.x): [Tải tại đây](https://www.python.org/)
      * *Lưu ý khi cài Python:* Nhớ tích vào ô **"Add Python to PATH"**.

-----

## 2\. Cài Đặt Thư Viện (Dependencies)

Mở **Terminal** (hoặc PowerShell/CMD) tại thư mục dự án `web-ai-travel` và chạy lần lượt các lệnh sau:

### A. Cài đặt thư viện cho Backend (Node.js)

```bash
npm init -y
npm install express body-parser
```

### B. Cài đặt thư viện cho AI (Python)

```bash
pip install pandas scikit-learn google-generativeai
```

*(Nếu bạn dùng Mac/Linux, có thể cần dùng `pip3` thay vì `pip`)*.

-----

## 3\. Cấu Hình API Key (Quan Trọng)

Để chức năng **Lập lịch trình (AI2)** hoạt động, bạn cần có API Key của Google Gemini.

1.  Mở file **`ai2.py`**.
2.  Tìm dòng: `API_KEY = "YOUR_API_KEY"`
3.  Thay thế `"YOUR_API_KEY"` bằng mã key thật của bạn (lấy tại [aistudio.google.com](https://aistudio.google.com/)).
4.  Lưu file lại (`Ctrl + S`).

-----

## 4\. Kiểm Tra Dữ Liệu

Đảm bảo trong thư mục dự án có đầy đủ các file sau:

  * `server.js` (Server chính)
  * `recommender.py` (AI Gợi ý địa điểm)
  * `ai2.py` (AI Lập lịch trình)
  * `data.json` (Dữ liệu địa điểm - Tiếng Anh chuẩn)
  * Thư mục `public/` (Chứa `index.html`, `style.css`, `script.js`)

-----

## 5\. Cách Chạy Dự Án

### Bước 1: Khởi động Server

Tại Terminal của thư mục dự án, gõ lệnh:

```bash
node server.js
```

Nếu thành công, màn hình sẽ hiện:

> `Server đang chạy tại http://localhost:3000`

### Bước 2: Sử dụng Web App

1.  Mở trình duyệt (Chrome, Cốc Cốc, Edge...).
2.  Truy cập địa chỉ: **[http://localhost:3000](https://www.google.com/search?q=http://localhost:3000)**
3.  Chọn sở thích, nhập ngân sách, chọn giờ đi/về và bấm nút **"Generate Plan"**.

-----

## 6\. Khắc Phục Lỗi Thường Gặp (Troubleshooting)

  * **Lỗi `ModuleNotFoundError`**: Do chưa cài đủ thư viện Python. Hãy chạy lại bước 2B.
  * **Lỗi `AI2 Error` / `No plan found`**:
      * Kiểm tra lại API Key trong `ai2.py`.
      * Kiểm tra xem file `data.json` có đúng định dạng không.
  * **Lỗi tiếng Việt (trên Windows)**: Code đã có sẵn đoạn fix lỗi hiển thị (`io.TextIOWrapper`), nhưng nếu vẫn lỗi, hãy đảm bảo file code được lưu với encoding **UTF-8**.
  * **Không mở được Web**: Kiểm tra xem bạn đã chạy lệnh `node server.js` chưa và cửa sổ Terminal đó có đang mở không (đừng tắt nó khi đang dùng web).

-----

**Chúc bạn thành công\! 🚀**
