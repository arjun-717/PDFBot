import streamlit as st
from gemini_chat import ask_gemini
from deepseek_chat import ask_deepseek 
from elevenlabs import play
import tempfile
import os
from main import load_pdf_text, split_text, get_embeddings, answer_question, ElevenSpeak, model,speak,voice_to_text
import base64
from gtts import gTTS
from playsound import playsound
import os
# gtts

def Gtts(text):
    # Generate audio file
    tts = gTTS(text=text)
    filename = "output.mp3"
    tts.save(filename)

    # Encode to base64
    with open(filename, "rb") as f:
        audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()

    # Delete file after use
    os.remove(filename)

    # HTML + JS to auto play and reset audio silently
    audio_html = f"""
    <audio id="gtts_audio" autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    <script>
        const audio = document.getElementById("gtts_audio");
        if (audio) {{
            audio.pause();
            audio.currentTime = 0;
            audio.play().catch(e => console.log("Autoplay error:", e));
        }}
    </script>
    """
    st.markdown(audio_html, unsafe_allow_html=True)




    
st.title("📘 PDFBot - Ask Your PDF")
uploaded_file = st.file_uploader("📄 Upload a PDF file", type="pdf")

# Define session state
if "query" not in st.session_state:
    st.session_state.query = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "embeddings" not in st.session_state:
    st.session_state.embeddings = []

if "input_mode" not in st.session_state:
    st.session_state.input_mode = "text"  # default input mode

if "audio_count" not in st.session_state:
    st.session_state.audio_count = 0
if "prev_answer" not in st.session_state:
    st.session_state.prev_answer = ""

if st.session_state.answer != st.session_state.prev_answer:
    st.session_state.audio_count = 0
    st.session_state.prev_answer = st.session_state.answer


# Load PDF if uploaded
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        temp_pdf_path = tmp.name
    text = load_pdf_text(temp_pdf_path)
    st.session_state.chunks = split_text(text)
    st.session_state.embeddings = get_embeddings(st.session_state.chunks)
    os.remove(temp_pdf_path)

# Ask UI
if st.session_state.chunks:
    st.subheader("Ask Your Question")
     # Toggle Input Mode
    mode1, mode2 = st.columns([1, 1])
    with mode1:
        if st.button("📝 Text"):
            st.session_state.input_mode = "text"
    with mode2:
        if st.button("🎤 Speech"):
            st.session_state.input_mode = "speech"


    if st.session_state.input_mode == "text":
        st.session_state.query = st.text_input("❓ Ask a question about the PDF:", value=st.session_state.query)
    elif st.session_state.input_mode == "speech":
        st.info("🎤 Say your question")
        if st.button("🎙️ Simulate Speech"):
            st.session_state.query = voice_to_text()
            st.write(st.session_state.query)


    col1, col2, col3 = st.columns([2, 1, 1])

    # ✅ Ask
    with col1:
        if st.session_state.chunks:
            if st.button("✅ Ask"):
                st.info("🤖 PDFBot is thinking...")
                context = answer_question(
                    st.session_state.query,
                    st.session_state.chunks,
                    st.session_state.embeddings,
                    model,
                    top_k=3
                )
                # st.session_state.answer = ask_gemini(st.session_state.query, context)
                # st.session_state.answer = ask_deepseek(st.session_state.query, context)

                try:
                    answer = ask_deepseek(st.session_state.query, context)
                    if not answer.strip() or "⚠️" in answer:
                            raise Exception("DeepSeek response empty or failed.")
                except Exception as e:
                        st.warning(f"⚠️ DeepSeek failed, switching to Gemini LLM... ({str(e)})")
                        answer = ask_gemini(st.session_state.query, context)

                st.session_state.answer = answer
    with col2:
        if st.session_state.answer:
            if st.button("❌ Clear All"):
                st.session_state.query = ""
                st.session_state.answer = ""
                st.session_state.is_speaking = False
                # st.session_state.audio_count=0
                st.rerun()

    # 🔊 Hear Answer
    with col3:
        if st.session_state.answer:
            if st.button("🔊 Hear Answer"):
                if st.session_state.audio_count == 0:
                    Gtts(st.session_state.answer)
                    st.session_state.audio_count += 1
                elif st.session_state.audio_count >= 1:
                    st.info("🔁 Audio repetition is not available")

    # Show answer
    if st.session_state.answer:
        st.success("📄 Answer:")
        st.write(st.session_state.answer)
else:
    st.warning("Please upload a PDF file to get started.")
