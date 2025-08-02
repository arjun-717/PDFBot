import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from gemini_chat import ask_gemini
from deepseek_chat import ask_deepseek 
import pyttsx3
import warnings
from elevenlabs import ElevenLabs
from elevenlabs import play
import speech_recognition as sr



warnings.filterwarnings("ignore", category=FutureWarning)

#for elevenlabs voice
client = ElevenLabs(api_key="sk_55fbb7297c0a3c09eba75e1267e133ddad2cf0b99fcd4ac8")

# Choose a voice (you can list voices via client.voices.get_all())
voice_id = "EXAVITQu4vr4xnSDxMaL"  # Example: Rachel


# load pdf
def load_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# split into chunks
def split_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

#  model for converting text to numerical
model = SentenceTransformer('all-MiniLM-L6-v2')
def get_embeddings(chunks):
    return model.encode(chunks, convert_to_tensor=True) #['abc'] -> ['321']

# Find best matching chunk for the question (finding based on qn)
# def answer_question(question, chunks, embeddings, model):
#     question_embedding = model.encode([question])
#     similarities = cosine_similarity(question_embedding, embeddings)[0]
#     most_similar_idx = similarities.argmax()
#     best_chunk = chunks[most_similar_idx]
#     return best_chunk

def answer_question(question, chunks, embeddings, model, top_k=2):
    question_embedding = model.encode([question])
    similarities = cosine_similarity(question_embedding, embeddings)[0]
    
    # Get indices of top_k most similar chunks
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    # Combine the top chunks into one context string
    top_chunks = [chunks[i] for i in top_indices]
    return "\n\n".join(top_chunks)

    # initialize text-to-speech engine
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    engine.stop()



def ElevenSpeak(text):
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id="eleven_monolingual_v1",
        text=text
    )
    return audio

#speech input
def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print("📝 You said:", text)
        return text
    except sr.UnknownValueError:
        print("❗ Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"❗ Could not request results: {e}")
        return ""

if __name__ == "__main__":
    pdf_path = "HisFirstFlight.pdf"
    text = load_pdf_text(pdf_path)
    chunks = split_text(text)
    # print(f"Total chunks: {len(chunks)}\n")
    # for i, chunk in enumerate(chunks[:3]):  # print first 3 chunks
    #     print(f"\n--- Chunk {i+1} ---\n{chunk}\n")
    embeddings = get_embeddings(chunks)
    # print(f"\n✅ Total embeddings created: {len(embeddings)}")
    # print(f"🔢 Shape of 1st embedding: {embeddings[0].shape}")s
    

   
    while True:
        mode = input("\n👉 Press 1 to type a question or 2 to speak it (type 'exit' to quit): ").strip()
        if mode.lower() == "exit":
            break
        
        #basic model
        # response = answer_question(query, chunks, embeddings, model)
        # print(f"\n📄 Answer:\n{response}")

        #gemini integration
        if mode == "1":
            query = input("\n⌨️ Enter your question: ").strip()
        elif mode == "2":
            query = voice_to_text()
        else:
            print("❗ Invalid choice. Try again.")
            continue

        if not query:
            print("⚠️ Empty question. Try again.")
            continue

        context = answer_question(query, chunks, embeddings, model, top_k=2)
        print("🤖 PDFBot is thinking...\n")
        answer = ask_gemini(query, context)
        # answer = ask_deepseek(query, context)

        print(f"\n📄 Answer:\n{answer}")
        
        # audio = ElevenSpeak(answer)
        play_voice = input("\n🔊 Do you want to hear the answer? (y/n): ").strip().lower()
        if play_voice == 'y':
            #  play(audio)
            speak(answer)