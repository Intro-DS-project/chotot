import os
from dotenv import load_dotenv
from pathlib import Path

import google.generativeai as genai

load_dotenv(dotenv_path=Path('./.env'))
GOOGLE_API_KEY = os.getenv('API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}


model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config)

def extract_location(location):
    prompt = f"Ta có thông tin địa chỉ bằng tiếng Việt như sau: \
        {location} \n \
        Hãy trích xuất thông tin trên và trả về 3 trường thông tin dưới đây. \
        Danh sách các trường: \
        street (tên đường hoặc phố. Không bao gồm ngõ/ngách. Không bao gồm số nhà ở trước tên đường. Chỉ có tên, không có chữ 'đường' ở trước), \
        ward (là phường, nhưng có thể thay bằng xã. Chỉ gồm tên, không có chữ 'phường'/'xã' ở trước), \
        district (là quận, nhưng có thể thay bằng huyện Chỉ gồm tên, không có chữ 'quận'/'huyện' ở trước). Không bao gồm tên thành phố Hà Nội. \
        Trường nào không xuất hiện thì để là rỗng. \
        Các trường thông tin ngăn cách bởi dấu phẩy.\
        Ví dụ: \"Tân Triều,Thanh Xuân Nam,Thanh Xuân\", hoặc \"Tân Triều,,Thanh Xuân\" nếu có trường trống."

    response = model.generate_content(prompt)
    return response.text