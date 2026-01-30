import requests, random, threading, os, time
from concurrent.futures import ThreadPoolExecutor
from user_agent import generate_user_agent

# --- بياناتك الشخصية ---
ID = '8565274048'
token = '8246792427:AAFYBupze6boH3PzGFVAb3KD1eIJZ8T8po'

hits, bads = 0, 0
PROXIES_LIST = []
lock = threading.Lock()

def get_proxies():
    sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
    ]
    all_proxies = []
    for s in sources:
        try:
            res = requests.get(s, timeout=5)
            all_proxies.extend(res.text.splitlines())
        except: continue
    return list(set(all_proxies))

def check_tiktok_user(user):
    global hits, bads
    proxy = random.choice(PROXIES_LIST) if PROXIES_LIST else None
    proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'} if proxy else None
    
    url = f"https://www.tiktok.com/@{user}"
    headers = {"User-Agent": generate_user_agent()}

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=3)
        # إذا كانت حالة الصفحة 404 تعني اليوزر متاح
        if response.status_code == 404:
            with lock:
                hits += 1
                email = f"{user}@gmail.com"
                msg = f"🎯 صيد تيك توك جديد!\n👤 User: {user}\n📧 Email: {email}"
                # إرسال الرسالة لتليجرام
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": ID, "text": msg})
                # حفظ في ملف السيرفر
                with open("tiktok_hits.txt", "a") as f: f.write(f"User: {user} | Email: {email}\n")
        else:
            with lock: bads += 1
    except:
        with lock: bads += 1

    print(f"\r🔥 TikTok Hunt | Check: {user} | ❌ Bad: {bads} | ✅ Hits: {hits}", end="")

def start_hunt():
    global PROXIES_LIST
    PROXIES_LIST = get_proxies()
    print(f"📡 Loaded {len(PROXIES_LIST)} Proxies. Hunting TikTok & Gmails...")
    
    chars = 'abcdefghijklmnopqrstuvwxyz1234567890._'
    with ThreadPoolExecutor(max_workers=40) as executor:
        while True:
            if (hits + bads) % 500 == 0 and (hits + bads) != 0:
                PROXIES_LIST = get_proxies()
            length = random.choice([4, 5]) 
            user = "".join(random.choice(chars) for _ in range(length))
            executor.submit(check_tiktok_user, user)

if __name__ == "__main__":
    start_hunt()