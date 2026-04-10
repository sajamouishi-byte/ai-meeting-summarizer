import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY saknas. Lägg till den i din .env-fil.")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(page_title="AI Meeting Summarizer", page_icon="📝")

st.title("📝 AI Meeting Summarizer")
st.write("Klistra in mötesanteckningar och få en sammanfattning, beslut och action points.")

notes = st.text_area("Mötesanteckningar", height=250, placeholder="Klistra in mötesanteckningar här...")

if st.button("Sammanfatta möte"):
    if not notes.strip():
        st.warning("Du måste skriva eller klistra in mötesanteckningar först.")
    else:
        with st.spinner("Analyserar mötet..."):
            prompt = f"""
Du är en senior projektledare inom tech.

Analysera följande mötesanteckningar.

Ge svaret i exakt detta format:

Sammanfattning:
- max 5 tydliga punkter

Beslut:
- lista alla beslut som togs

Action points:
- Uppgift | Ansvarig | Deadline

Om ansvarig eller deadline saknas, skriv "Ej angivet".

Mötesanteckningar:
{notes}
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                result = response.choices[0].message.content

                st.subheader("Resultat")
                st.write(result)

            except Exception as e:
                st.error(f"Något gick fel: {e}")