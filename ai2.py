import os
import google.generativeai as genai
import json
import sys
import io

# --- CẤU HÌNH HỆ THỐNG ---
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ✅ LẤY API KEY TỪ ENV (Node.js sẽ truyền vào: GEMINI_API_KEY)
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print(json.dumps({"error": "Missing GEMINI_API_KEY (must be provided via environment)"}, ensure_ascii=False))
    sys.exit(0)

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

def plan_trip(start_time, end_time, priority_list_str):
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            all_places = json.load(f)
    except FileNotFoundError:
        return {"error": "Lỗi: Không tìm thấy file data.json"}
    except Exception as e:
        return {"error": f"Lỗi đọc dữ liệu: {str(e)}"}

    priorities = []
    if priority_list_str and priority_list_str.strip():
        priorities = priority_list_str.split('|')

    # AI2 chỉ chạy khi có AI1
    if not priorities:
        return {"error": "AI2 only runs after AI1. Please generate Suggested Places (AI1) first."}

    # AI2 chỉ được xuất hiện các địa điểm có ở AI1
    allowed_set = set(priorities)
    simple_data = []
    for p in all_places:
        if p.get("name") not in allowed_set:
            continue
        simple_data.append({
            "name": p.get("name"),
            "address": p.get("address", ""),
            "hours": p.get("opening_hours", "Unknown"),
            "price": p.get("price", 0),
            "tags": p.get("tags", []),
            "priority": "YES"
        })

    if not simple_data:
        return {"error": "No matching places found for AI2. Please run AI1 again."}

    prompt = f"""
Bạn là một chuyên gia du lịch thông minh, thực tế tại TP.HCM.

THÔNG TIN CHUYẾN ĐI:
- Thời gian: Bắt đầu lúc {start_time} và Kết thúc lúc {end_time}.
- Nguồn dữ liệu: Dùng danh sách địa điểm JSON bên dưới.

NHIỆM VỤ:
Tạo một lịch trình chi tiết (timeline) tuân thủ các quy tắc sau:

1) Danh sách hợp lệ:
- CHỈ được dùng các địa điểm có trong dữ liệu đầu vào.
- KHÔNG được bịa thêm địa điểm mới dưới bất kỳ hình thức nào.

2) AI2 chỉ dùng các điểm từ AI1:
- Tất cả địa điểm đầu vào đều là ưu tiên (priority="YES").
- Sắp xếp theo logic hợp lý (gần nhau đi trước) và phù hợp giờ mở cửa.

3) Logic thời gian:
- Giữa 2 địa điểm PHẢI có hoạt động "Di chuyển" (15–30 phút).
- Mỗi điểm tham quan (icon "visit") thường 45–90 phút tùy loại.

4) Ăn uống hợp lý (tránh lịch trình ngớ ngẩn):
- TUYỆT ĐỐI KHÔNG tạo "Tham quan quán ăn". Nếu có ăn uống phải dùng icon "food".
- Nếu timeline đi qua 11:30–13:30 => chèn tối đa 1 bữa chính: "Ăn trưa/Nghỉ ngơi".
- Chỉ thêm bữa tối nếu endTime > 18:00.
- Không được đề xuất nhiều bữa chính quá gần nhau (mỗi bữa chính cách nhau tối thiểu 3 giờ).
- Có thể gợi ý "Ăn vặt" (icon "food") nếu còn trống thời gian, nhưng phải ghi rõ là "Ăn vặt".

5) Không đủ thời gian:
- Nếu không thể xếp hết các địa điểm trong khoảng thời gian cho phép, hãy chọn một phần hợp lý (điểm nổi bật/đi gần nhau).
- Ghi rõ trong "note" rằng không đủ thời gian để đi hết.

DỮ LIỆU ĐẦU VÀO:
{json.dumps(simple_data, ensure_ascii=False)}

YÊU CẦU OUTPUT JSON CHUẨN:
{{
  "total_locations": (số lượng địa điểm tham quan thực tế),
  "note": "Một lời khuyên ngắn gọn, thân thiện",
  "timeline": [
    {{
      "time": "HH:MM - HH:MM",
      "activity": "Tên hoạt động (Tham quan X / Di chuyển / Ăn trưa / Ăn vặt)",
      "icon": "visit",
      "detail": "Mô tả chi tiết"
    }}
  ]
}}

QUAN TRỌNG:
- icon chỉ được là: "visit" hoặc "move" hoặc "food".
- Nếu activity là ăn uống (Ăn trưa/Ăn tối/Ăn vặt) thì icon bắt buộc là "food".
"""

    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        # Để server.js nhận diện quota/429 dễ hơn, giữ nguyên text lỗi
        return {"error": f"{str(e)}"}

if __name__ == "__main__":
    try:
        s_time = sys.argv[1] if len(sys.argv) > 1 else "08:00"
        e_time = sys.argv[2] if len(sys.argv) > 2 else "17:00"
        p_list = sys.argv[3] if len(sys.argv) > 3 else ""

        result = plan_trip(s_time, e_time, p_list)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": f"Lỗi hệ thống Python: {str(e)}"}, ensure_ascii=False))
