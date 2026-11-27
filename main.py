
import os
import requests
import fitz

TOKEN = os.getenv("KITOB_BOT_TOKEN")
CHAT_ID = os.getenv("KITOB_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PDF_FILE = "ар-Радд ‘аля-ль-джахмия.pdf"


def translate_to_uzbek(russian_text):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-3.8-flash:generateContent"
    )

    prompt = f"""
Рус тилидаги диний китоб матнини ўзбек тилига кирилл ёзувида таржима қил.

Талаблар:
- Матн маъносини тўлиқ ва аниқ сақла.
- Диний атамаларни эҳтиёткорлик билан таржима қил.
- Ҳеч нарсани қисқартирма ёки қўшиб ёзма.
- Фақат ўзбекча таржимани қайтар.

Русча матн:
{russian_text}
"""

    response = requests.post(
        url,
        headers={
            "x-goog-api-key": GEMINI_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        },
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()

    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
        },
        timeout=60,
    )

    response.raise_for_status()


def main():
    if not TOKEN or not CHAT_ID or not GEMINI_API_KEY:
        raise ValueError("Telegram yoki Gemini kaliti topilmadi")

    if not os.path.exists(PDF_FILE):
        raise FileNotFoundError(f"PDF topilmadi: {PDF_FILE}")

    with fitz.open(PDF_FILE) as pdf:
        russian_text = pdf[0].get_text().strip()

    if not russian_text:
        raise ValueError(
            "PDF'нинг биринчи саҳифасидан матн олинмади"
        )

    uzbek_text = translate_to_uzbek(russian_text)

    message = (
        "📖 Китоб: ар-Радд ‘аля-ль-джахмия\n"
        "📄 1-саҳифа\n\n"
        "🇷🇺 Русча асл матн:\n"
        f"{russian_text}\n\n"
        "🇺🇿 Ўзбекча таржима:\n"
        f"{uzbek_text}"
    )

    send_message(message)
    print("Биринчи саҳифа таржимаси каналга юборилди.")


if __name__ == "__main__":
    main()
