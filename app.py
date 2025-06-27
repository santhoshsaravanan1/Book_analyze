import os
import streamlit as st
import freesound  # from freesound-api
import google.generativeai as genai

# Configure Gemini API key
genai.configure(api_key="AIzaSyASpYofjJXEWLMnGM-Lxucb_DZGV0Vp4EQ")

# Initialize Freesound client
FS_CLIENT = freesound.FreesoundClient()
API_KEY = "bnvLHj0a3oBdWCUyfY61Rds7SINt4cntex3UBI5n"
if not API_KEY:
    st.error("Please set FREESOUND_API_KEY env var")
    st.stop()
FS_CLIENT.set_token(API_KEY, "token")

# Load Gemini model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Function to analyze sentiment
def analyze_sentiment(user_text: str) -> list:
    prompt = f'''
Split this text into segments where the sentiment changes.
Output single-word sentiment tags for each segment (e.g., happy, tense, calm, anxious).
Join them with dots. No extra words.

Text: """{user_text}"""
'''
    response = model.generate_content(prompt)
    sentiments = response.text.strip().split('.')
    return [s.strip() for s in sentiments if s.strip()]

# Function to play audio
def play_looping_audio(url: str):
    html = f"""
    <audio autoplay loop>
      <source src="{url}" type="audio/mp3">
      Your browser does not support the audio element.
    </audio>
    """
    st.markdown(html, unsafe_allow_html=True)

# Function to search and play Freesound audio for a sentiment
def play_emotion_sound(emotion: str):
    try:
        results = FS_CLIENT.text_search(
            query=emotion,
            fields="id,previews,username,name",
            filter="duration:[1.0 TO 10.0]",
            sort="rating_desc",
            page_size=1
        )
    except Exception as e:
        st.error(f"API error while searching sound for '{emotion}': {e}")
        return

    if results.count == 0:
        st.warning(f"😞 No sounds found for '{emotion}'.")
    else:
        sound = results[0]
        preview_url = getattr(sound.previews, 'preview_hq_mp3', None) or getattr(sound.previews, 'preview_lq_mp3', None)
        if preview_url:
            st.subheader(f"🎵 {sound.name}  — by {sound.username} [Emotion: {emotion}]")
            play_looping_audio(preview_url)
        else:
            st.error("No preview available for this sound.")

# Streamlit UI
def main():
    st.title("🎧 Emotion-Aware Soundscape Generator")
    st.write("Enter a story or paragraph. The AI will detect emotions and play a corresponding sound.")

    user_input = st.text_area("Enter your text here...", height=200)

    if st.button("Generate & Play Sound"):
        if not user_input.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Analyzing sentiment and fetching sound..."):
                try:
                    sentiments = analyze_sentiment(user_input)
                    if sentiments:
                        chosen_emotion = sentiments[0]  # Pick the first detected emotion for playback
                        st.success(f"Detected sentiments: {' > '.join(sentiments)}")
                        play_emotion_sound(chosen_emotion)
                    else:
                        st.warning("No sentiments detected.")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

if __name__ == "__main__":
    main()
