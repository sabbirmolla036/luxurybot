import requests
import json
import os
import time
import random
from colorama import init, Fore
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

print("""
╔══════════════════════════════════════════════╗
║ Developer Contact: @Sabbirmolla036           ║
╚══════════════════════════════════════════════╝
""")

REGISTER_URL = "https://luxury-airdrop.onrender.com/api/create-username"
TASK_URL = "https://luxury-airdrop.onrender.com/api/complete-task"
JSON_FILE = "username.json"
PROXY_FILE = "proxy.txt"

TASK_TYPES = [
    "telegramGroup", "telegramChannel", "twitter", "twitterRepost6", "twitterRepost5",
    "twitterRepost4", "twitterRepost3", "twitterRepost2", "twitterRepost1",
    "twitterRetweet", "twitterLike"
]

CUSTOM_NAMES = [
    "alex", "bella", "charlie", "diana", "ethan", "fiona", "george", "hannah",
    "ian", "julia", "kyle", "luna", "mike", "nina", "oliver", "paula",
    "quentin", "rose", "sam", "tina", "victor", "wade", "xena", "yuri", "zara",
    "abby", "brad", "carmen", "daniel", "ella", "felix", "grace", "harry",
    "iris", "jack", "karen", "leo", "mia", "noah", "olga", "peter", "queen",
    "rachel", "steve", "terry", "ursula", "van", "will", "xander", "yasmin", "zane",
    "amber", "blake", "claire", "derek", "emily", "frank", "gabby", "helen",
    "ivan", "joan", "kevin", "laura", "mark", "nathan", "opal", "phoebe",
    "quincy", "riley", "sophie", "tyler", "una", "veronica", "wayne", "xenia", "yosef", "zoe",
    "arnold", "beth", "caleb", "delia", "edgar", "faith", "gavin", "holly",
    "isaac", "jade", "kirk", "lilly", "marvin", "nora", "oscar", "paige", "quinn", "ryan"
]

def get_random_username():
    base = random.choice(CUSTOM_NAMES)
    timestamp = str(int(time.time()))[-5:]
    rand = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=3))
    return f"{base}{timestamp}{rand}"

def load_proxies():
    if os.path.exists(PROXY_FILE):
        with open(PROXY_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def get_proxy():
    proxies = load_proxies()
    if proxies:
        proxy = random.choice(proxies)
        return {"http": proxy, "https": proxy}
    return None

def log_message(message, color, lock):
    with lock:
        print(f"{color}{message}")

def save_username(username, ref_code, lock):
    with lock:
        try:
            usernames = []
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, "r") as f:
                    usernames = json.load(f)
            usernames.append({"username": username, "ref": ref_code})
            with open(JSON_FILE, "w") as f:
                json.dump(usernames, f, indent=4)
        except:
            pass

def complete_tasks(username, lock):
    for task in TASK_TYPES:
        payload = {"username": username, "taskType": task}
        try:
            proxy = get_proxy()
            response = requests.post(TASK_URL, json=payload, proxies=proxy, timeout=20)
            if response.status_code == 200:
                log_message(f"✅ Completed task {task} for {username}", Fore.GREEN, lock)
            else:
                log_message(f"⚠️ Failed task {task} for {username}", Fore.YELLOW, lock)
            time.sleep(5)  # Reduced sleep to make it faster
        except:
            pass  # Suppressed task error

def register_user(ref_code, run_tasks, index, total, lock):
    retries = 0
    while retries < 10:
        username = get_random_username()
        payload = {"username": username, "ref": ref_code}
        try:
            proxy = get_proxy()
            response = requests.post(REGISTER_URL, json=payload, proxies=proxy, timeout=20)
            if response.status_code == 201:
                log_message(f"✅ [{index}/{total}] Registered username {username}", Fore.GREEN, lock)
                save_username(username, ref_code, lock)
                if run_tasks:
                    complete_tasks(username, lock)
                return
            elif response.status_code == 409:
                retries += 1
            elif response.status_code == 429:
                time.sleep(15)
                retries += 1
            else:
                return
        except:
            time.sleep(3)
            retries += 1

def main():
    try:
        num_requests = int(input("Enter number of referrals: "))
        ref_code = input("Enter your referral code: ").strip()
        run_tasks = input("Run all tasks for each? (y/n): ").strip().lower() == 'y'

        if num_requests <= 0:
            print("❌ Referral number must be greater than 0")
            return

        lock = Lock()
        log_message(f"🚀 Starting registration with 4x speed for {num_requests} referrals...", Fore.CYAN, lock)

        with ThreadPoolExecutor(max_workers=4) as executor:
            for i in range(num_requests):
                executor.submit(register_user, ref_code, run_tasks, i + 1, num_requests, lock)

        log_message("🎉 All registrations completed!", Fore.MAGENTA, lock)

    except:
        pass  # Suppressed all main errors

if __name__ == "__main__":
    main()
