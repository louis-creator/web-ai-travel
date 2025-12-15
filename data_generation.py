import google.generativeai as genai
import json
import time
import urllib.parse
import sys
import io

# Fix lỗi hiển thị tiếng Việt trên Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- 1. CẤU HÌNH API ---
API_KEY = "Your_api_key" # <--- NHỚ THAY KEY CỦA BẠN VÀO ĐÂY
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

# --- 2. CHIẾN THUẬT QUÉT 100 ĐỊA ĐIỂM ---
BATCHES = [
    "20 Địa điểm biểu tượng nổi tiếng nhất Sài Gòn (Dinh Độc Lập, Nhà thờ Đức Bà, Bưu điện, Chợ Bến Thành, UBND Thành phố, Nhà hát lớn, Bitexco...).",
    "20 Quán ăn và Nhà hàng nổi tiếng: Phở, Cơm Tấm, Bánh Mì, Dimsum, và các quán ăn lâu đời được Michelin hoặc TripAdvisor đề xuất.",
    "20 Bảo tàng (Chứng tích chiến tranh, Mỹ thuật, Y học...), Di tích lịch sử, Chùa chiền (Ngọc Hoàng, Vĩnh Nghiêm) và Hội quán người Hoa.",
    "20 Địa điểm giới trẻ yêu thích: Phố đi bộ Nguyễn Huệ/Bùi Viện, Đường sách, Quán Cafe concept đẹp, Khu tổ hợp nghệ thuật (The Bloq, Thảo Điền).",
    "20 Công viên cây xanh (Tao Đàn, 30/4), Thảo Cầm Viên, Khu du lịch sinh thái (Bình Quới, Văn Thánh, Suối Tiên, Đầm Sen)."
]

BASE_PROMPT = """
Bạn là thổ địa TP.HCM. Hãy tạo danh sách JSON các địa điểm theo yêu cầu.

YÊU CẦU QUAN TRỌNG:
1. **Tên:** Chính xác tên tiếng Việt.
2. **Giờ mở cửa:** Ghi rõ khung giờ (VD: "07:30 - 17:00").
3. **Giá tiền:** Ước lượng thực tế VNĐ (Số nguyên).
4. **Địa chỉ:** Ghi rõ số nhà, tên đường, Quận.

CẤU TRÚC JSON TRẢ VỀ:
[
  {
    "id": 0,
    "name": "Tên địa điểm",
    "tags": ["tag1", "tag2"], 
    "price": (số nguyên),
    "opening_hours": "Giờ mở cửa",
    "address": "Địa chỉ đầy đủ",
    "map_link": ""
  }
]

TAGS (Tiếng Anh): ['history', 'cuisine', 'politics', 'art', 'nature', 'religion']
"""

# --- 3. HÀM CHẠY ---
def generate_data():
    all_places = []
    seen_names = set()
    
    print(f"🚀 Bắt đầu tạo 100 địa điểm (Link Map Chuẩn)...")

    for i, batch_topic in enumerate(BATCHES):
        print(f"\n[Đợt {i+1}/5]: Đang xử lý...")
        
        prompt = f"{BASE_PROMPT}\n\nNHIỆM VỤ CỤ THỂ: Liệt kê {batch_topic}"
        
        try:
            response = model.generate_content(prompt)
            batch_data = json.loads(response.text)
            
            count = 0
            for place in batch_data:
                clean_name = place['name'].strip().lower()
                if clean_name not in seen_names:
                    seen_names.add(clean_name)
                    all_places.append(place)
                    count += 1
            
            print(f"   ✅ Thêm được {count} địa điểm.")
            time.sleep(2) 
            
        except Exception as e:
            print(f"   ❌ Lỗi đợt này: {e}")

    # --- 4. XỬ LÝ HẬU KỲ (FIX LINK TẠI ĐÂY) ---
    print("\n🔄 Đang tạo Link Google Maps chuẩn...")
    
    final_data = []
    for idx, place in enumerate(all_places):
        place['id'] = idx + 1
        
        # --- CÔNG THỨC LINK CHUẨN CỦA GOOGLE ---
        # Tìm kiếm theo: "Tên + Địa chỉ + Hồ Chí Minh"
        query = f"{place['name']} {place['address']} Hồ Chí Minh"
        encoded_query = urllib.parse.quote(query)
        
        # Link chuẩn bắt đầu bằng https://www.google.com/maps/search/...
        place['map_link'] = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
        
        final_data.append(place)

    # --- 5. LƯU FILE ---
    output_file = 'data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 THÀNH CÔNG! Đã lưu {len(final_data)} địa điểm vào '{output_file}'.")

if __name__ == "__main__":

    generate_data()
