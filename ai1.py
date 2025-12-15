import pandas as pd
import json
import sys
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Đảm bảo in ra tiếng Việt không lỗi (nếu có)
sys.stdout.reconfigure(encoding='utf-8')

try:
    # 1. Nhận dữ liệu từ Node.js
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit()
    
    input_tags_str = sys.argv[1] # Chuỗi tag (vd: "cuisine,history")
    input_budget = int(sys.argv[2])

    user_tags = [t.strip() for t in input_tags_str.split(',')]

    # 2. Load Data
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['tags_string'] = df['tags'].apply(lambda x: ' '.join(x))

    # 3. Train AI
    vectorizer = CountVectorizer(binary=True)
    location_matrix = vectorizer.fit_transform(df['tags_string'])
    
    # 4. Tính toán Similarity
    user_query = ' '.join(user_tags)
    user_vector = vectorizer.transform([user_query])
    similarities = cosine_similarity(user_vector, location_matrix)
    df['score'] = similarities[0]
    
    # 5. Lọc và Sắp xếp
    df_filtered = df[df['price'] <= input_budget].copy()
    
    if df_filtered.empty:
        print(json.dumps([]))
        sys.exit()

    results = df_filtered.sort_values(by=['score', 'price'], ascending=[False, False])
    final_results = results[results['score'] > 0.1].head(10)
    
    # 6. Xuất JSON
    output_data = final_results[['name', 'price', 'opening_hours', 'address', 'map_link', 'score']].to_dict(orient='records')
    print(json.dumps(output_data))

except Exception as e:
    print(json.dumps({"error": str(e)}))