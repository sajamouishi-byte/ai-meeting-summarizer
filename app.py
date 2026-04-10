import os
import pandas as pd
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

notes = st.text_area(
    "Mötesanteckningar",
    height=250,
    placeholder="Klistra in mötesanteckningar här..."
)

def parse_sections(text: str) -> dict:
    sections = {
        "Sammanfattning": "",
        "Beslut": "",
        "Action points": ""
    }

    current_section = None
    lines = text.splitlines()

    for line in lines:
        stripped = line.strip()

        if stripped.lower().startswith("sammanfattning"):
            current_section = "Sammanfattning"
            continue
        elif stripped.lower().startswith("beslut"):
            current_section = "Beslut"
            continue
        elif stripped.lower().startswith("action points"):
            current_section = "Action points"
            continue

        if current_section and stripped:
            sections[current_section] += line + "\n"

    return {k: v.strip() for k, v in sections.items()}

if st.button("Sammanfatta möte"):
    if not notes.strip():
        st.warning("Du måste skriva eller klistra in mötesanteckningar först.")
    else:
        with st.spinner("Analyserar mötet..."):
            prompt = f"""
Du är en senior projektledare inom tech.

Analysera följande mötesanteckningar.

Ge svaret i exakt detta format och på svenska:

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
                parsed = parse_sections(result)

                st.success("Klart.")

                st.markdown("## 📌 Sammanfattning")
                st.markdown(parsed["Sammanfattning"] or "Ingen sammanfattning hittades.")

                st.markdown("## 🧠 Beslut")
                st.markdown(parsed["Beslut"] or "Inga beslut hittades.")

                st.markdown("## ✅ Action Points")

                actions_text = parsed["Action points"]
                rows = []

                for line in actions_text.split("\n"):
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) == 3:
                            rows.append(parts)

                if rows:
                    df = pd.DataFrame(rows, columns=["Uppgift", "Ansvarig", "Deadline"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.write("Inga action points hittades.")

                st.download_button(
                    label="⬇️ Ladda ner resultat",
                    data=result,
                    file_name="meeting_summary.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Något gick fel: {e}")