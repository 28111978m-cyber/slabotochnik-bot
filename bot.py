import requests
import json
import os

# ===== НАСТРОЙКИ =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = "349238448"
KEYWORDS = ["слаботочник", "слаботочных систем", "СКУД", "видеонаблюдение", "ОПС"]
LIMIT_PER_KEYWORD = 20
SENT_FILE = "sent_vacancies.json"
# =====================

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent), f, ensure_ascii=False)

def fetch_vacancies(keyword):
    url = "http://opendata.trudvsem.ru/api/v1/vacancies"
    params = {"text": keyword, "limit": LIMIT_PER_KEYWORD}
    try:
        r = requests.get(url, params=params, timeout=30)
        return r.json().get("results", {}).get("vacancies", [])
    except Exception as e:
        print(f"Ошибка запроса [{keyword}]: {e}")
        return []

def format_vacancy(v):
    name = v.get("job-name", "Без названия")
    company = v.get("company", {}).get("name", "Компания не указана")
    region = v.get("region", {}).get("name", "Регион не указан")
    salary = v.get("salary", "не указана")
    schedule = v.get("schedule", "")
    link = v.get("vac_url", "")
    text = f"🔧 {name}\n🏢 {company}\n📍 {region}\n💰 {salary}\n"
    if schedule:
        text += f"🕒 {schedule}\n"
    text += f"🔗 {link}"
    return text

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    for i in range(0, len(text), 4000):
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": text[i:i+4000],
            "disable_web_page_preview": True,
        })

def main():
    sent = load_sent()
    found = []
    for kw in KEYWORDS:
        for item in fetch_vacancies(kw):
            v = item.get("vacancy", {})
            vid = v.get("id")
            if vid and vid not in sent:
                found.append(v)
                sent.add(vid)
    if not found:
        print("Новых вакансий не найдено.")
        return
    messages = [format_vacancy(v) for v in found]
    header = f"🆕 Новых вакансий по слаботочке: {len(found)}\n\n"
    full_text = header + "\n\n➖➖➖\n\n".join(messages)
    send_message(full_text)
    save_sent(sent)
    print(f"Отправлено вакансий: {len(found)}")

if __name__ == "__main__":
    main()
