

import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="AI Meeting Summarizer", page_icon="📝")

# 🔑 API key (Streamlit secrets + fallback local)
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY saknas. Lägg till den i Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

st.title("📝 AI Meeting Summarizer")

st.write("Klistra in mötesanteckningar eller ladda upp en .txt-fil.")

# 📂 FILE UPLOAD
uploaded_file = st.file_uploader("Ladda upp mötesanteckningar (.txt)")

# ✍️ TEXT INPUT
notes_input = st.text_area(
    "Eller klistra in mötesanteckningar",
    height=200
)

# 🧠 Bestäm vilken input som används
notes = ""

if uploaded_file is not None:
    notes = uploaded_file.read().decode("utf-8")
    st.success("Fil uppladdad!")
elif notes_input.strip():
    notes = notes_input


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
            sections[current_section] += stripped + "\n"

    return {k: v.strip() for k, v in sections.items()}


if st.button("Sammanfatta möte"):
    if not notes.strip():
        st.warning("Du måste skriva eller ladda upp mötesanteckningar först.")
    else:
        with st.spinner("Analyserar mötet..."):
            prompt = f"""
You are a senior technical project manager.

Analyze the meeting notes below.

Respond in the same language as the input.

Use exactly this format:

Sammanfattning:
- max 5 tydliga punkter

Beslut:
- lista alla beslut som togs

Action points:
- Uppgift | Ansvarig | Deadline

If responsible person or deadline is missing, write "Ej angivet".

Meeting notes:
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

                # 📌 Sammanfattning
                st.markdown("## 📌 Sammanfattning")
                st.markdown(parsed["Sammanfattning"] or "Ingen sammanfattning hittades.")

                # 🧠 Beslut
                st.markdown("## 🧠 Beslut")
                st.markdown(parsed["Beslut"] or "Inga beslut hittades.")

                # ✅ Action Points (TABELL)
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

                # 📥 Download
                st.download_button(
                    label="⬇️ Ladda ner resultat",
                    data=result,
                    file_name="meeting_summary.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Något gick fel: {e}")