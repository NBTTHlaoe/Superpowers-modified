"""
Vertex AI Model Client for Antigravity Workspace.
Tự động kết nối tới Google Cloud Project qua Application Default Credentials (ADC).
"""

import os
import sys
from google import genai
from google.genai import types

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "project-b637a764-1cbb-4743-a3a")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

def get_vertex_client():
    """Khởi tạo GenAI Client kết nối Vertex AI."""
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )

def generate_text(prompt: str, model_name: str = "gemini-2.5-flash", temperature: float = 0.7) -> str:
    """
    Gửi prompt tới model trên Vertex AI và trả về kết quả text.
    
    Args:
        prompt: Nội dung câu hỏi/yêu cầu
        model_name: Tên model (gemini-2.5-flash, gemini-2.5-pro, gemini-3.5-flash, gemini-3.8-flash, v.v.)
        temperature: Độ sáng tạo (0.0 đến 1.0)
    """
    client = get_vertex_client()
    config = types.GenerateContentConfig(
        temperature=temperature,
    )
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config
    )
    return response.text

def list_available_models():
    """Liệt kê danh sách các model có trên Vertex AI của Project."""
    client = get_vertex_client()
    print(f"--- Danh sách model Vertex AI trên project: {PROJECT_ID} ({LOCATION}) ---")
    for model in client.models.list():
        if "gemini" in model.name.lower():
            print(f" - {model.name}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
        print(f"Đang gọi Vertex AI ({PROJECT_ID}) với prompt: {user_prompt}\n")
        try:
            result = generate_text(user_prompt)
            print("Kết quả:")
            print(result)
        except Exception as e:
            print(f"Lỗi: {e}")
    else:
        print("Đang kiểm tra kết nối và liệt kê model...")
        try:
            list_available_models()
        except Exception as e:
            print(f"Lỗi: {e}")
