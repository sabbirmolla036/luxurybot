import requests
import json
import os
import time
import random
from multiprocessing import Process, Lock, Semaphore, Manager
from colorama import init, Fore

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
        usernames = []
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, "r") as f:
                    usernames = json.load(f)
            except:
                usernames = []
        usernames.append({"username": username, "ref": ref_code})
        with open(JSON_FILE, "w") as f:
            json.dump(usernames, f, indent=4)

def complete_tasks(username, lock):
    for task in TASK_TYPES:
        payload = {"username": username, "taskType": task}
        try:
            proxy = get_proxy()
            response = requests.post(TASK_URL, json=payload, proxies=proxy)
            if response.status_code == 200:
                log_message(f"✅ Completed task {task} for {username}", Fore.GREEN, lock)
            else:
                log_message(f"⚠️ Failed task {task} for {username}", Fore.YELLOW, lock)
            time.sleep(60)
        except Exception as e:
            log_message(f"❌ Task {task} error: {str(e)}", Fore.RED, lock)

def register_user(ref_code, run_tasks, index, total, lock, semaphore):
    with semaphore:
        retries = 0
        while retries < 10:
            username = get_random_username()
            payload = {"username": username, "ref": ref_code}
            try:
                proxy = get_proxy()
                response = requests.post(REGISTER_URL, json=payload, proxies=proxy)
                if response.status_code == 201:
                    log_message(f"✅ [{index}/{total}] Registered username {username}", Fore.GREEN, lock)
                    save_username(username, ref_code, lock)
                    if run_tasks:
                        complete_tasks(username, lock)
                    return
                elif response.status_code == 409:
                    log_message(f"⚠️ Username {username} already taken, retrying...", Fore.YELLOW, lock)
                    retries += 1
                elif response.status_code == 429:
                    log_message("⏳ Too many requests (429). Waiting 15 seconds...", Fore.RED, lock)
                    time.sleep(15)
                    retries += 1
                else:
                    log_message(f"❌ Failed to register {username} (Status {response.status_code}): {response.text}", Fore.RED, lock)
                    return
            except Exception as e:
                log_message(f"🚫 Registration error: {str(e)}", Fore.RED, lock)
                time.sleep(5)
                retries += 1

def main():
    try:
        num_requests = int(input("Enter number of referrals: "))
        ref_code = input("Enter your referral code: ").strip()
        run_tasks = input("Run all tasks for each? (y/n): ").strip().lower() == 'y'

        if num_requests <= 0:
            print("❌ Referral number must be greater than 0")
            return

        manager = Manager()
        lock = Lock()
        semaphore = Semaphore(5)  # Adjust based on your proxy/IP safety

        log_message(f"🚀 Starting multiprocessing for {num_requests} referrals...", Fore.CYAN, lock)

        processes = []
        for i in range(num_requests):
            p = Process(target=register_user, args=(ref_code, run_tasks, i + 1, num_requests, lock, semaphore))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        log_message("🎉 All registrations completed using multiprocessing!", Fore.MAGENTA, lock)

    except ValueError:
        print("❌ Referral number must be a number")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
