import google.generativeai as genai

genai.configure(api_key="AIzaSyBiELkKEs7IdmvTUY7IaxuFK3eauwRjxYs")
model = genai.GenerativeModel("gemini-2.5-flash-lite")


def ask_gemini(question, context):
    prompt = f"""
Answer the following question using only the information provided below. 
Do not say things like "the passage", "the context", or "based on what I've read". 
Give direct, natural answers as if you're simply explaining the fact.
and i have feed you text but you must called it as pdf which is mandatory.

Information:
\"\"\"
{context}
\"\"\"

Question:
{question}

Answer:"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ PDFBot Error: {e}"
