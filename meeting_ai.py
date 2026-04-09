import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

notes = """
Anna sa att vi behöver uppdatera tidsplanen.
Johan ska fixa buggar.
Deadline är fredag.
Maria bokar nästa möte.
"""

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

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": prompt}]
)

print("\nRESULTAT:\n")
print(response.choices[0].message.content)