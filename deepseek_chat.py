import requests
import json

OPENROUTER_API_KEY = "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"

def ask_deepseek(question, context):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourprojectname.com",  # Optional
        "X-Title": "PDFBot"  # Optional
    }

    payload = {
      "model": "deepseek/deepseek-r1-0528:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant named PDFBot. You answer only using information "
                    "from the provided PDF context. Speak in a natural, direct way. No phrases like "
                    "'the passage' or 'based on the context'."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ]
    }

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)  # ✅ Important: Use `data=` with `json.dumps`
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ PDFBot Error (DeepSeek): {e}"
