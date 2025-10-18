import sys
import requests
import threading
from queue import Queue
from time import sleep
import random
import uuid
import secrets

class JackSocialChecker:
    def __init__(self, emails, proxies, choice, threads):
        self.q = Queue()
        self.req = requests.Session()
        self.lock = threading.Lock()
        self.error, self.counter, self.banned, self.attempts = 0, 0, 0, 0

        self.emails = emails
        self.proxies_list = proxies
        self.choice = choice
        self.threads = threads

        self.instagram_email_url = "https://www.instagram.com/accounts/account_recovery_send_ajax/"
        self.snapchat_login_url = "https://accounts.snapchat.com/accounts/merlin/login"

        for email in self.emails:
            self.q.put(email)

    def _get_proxy(self, proxy_type):
        if not self.proxies_list:
            return None
        pro = random.choice(self.proxies_list)
        if proxy_type == 1:  # Http/Https
            return {"http": f"http://{pro}", "https": f"https://{pro}"}
        elif proxy_type == 2:  # socks4
            return {"http": f"socks4://{pro}", "https": f"socks4://{pro}"}
        elif proxy_type == 3:  # socks5
            return {"http": f"socks5://{pro}", "https": f"socks5://{pro}"}
        return None

    def _instagram_check(self, email, proxy_func):
        data = {
            "email_or_username": email,
            "recaptcha_challenge_field": "",
            "flow": "",
            "app_id": ""
        }
        head = {"method": "POST", "X-CSRFToken": "missing",
                "Referer": self.instagram_email_url,
                "X-Requested-With": "XMLHttpRequest",
                "path": "/accounts/account_recovery_send_ajax/",
                "accept": "*/*", "ContentType": "application/x-www-form-urlencoded",
                "mid": secrets.token_hex(8) * 2, "csrftoken": "missing", "rur": "FTW",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0"}
        try:
            c = self.req.post(self.instagram_email_url, headers=head, data=data, proxies=proxy_func(), timeout=5)
            if 200 == c.status_code:
                with self.lock:
                    with open("Instagram.txt", "a") as wr:
                        wr.write(email + "\n")
                    with open("social_media.txt", "a") as wr:
                        wr.write("instagram:" + email + "\n")
                    self.counter += 1
                    print(f"[+] LINKED : {email} | PLATFORM:INSTAGRAM")
            elif c.status_code == 429:
                with self.lock:
                    self.q.put(email)
                    self.banned += 1
        except requests.exceptions.Timeout:
            self._instagram_check(email=email, proxy_func=proxy_func) # Retry on timeout
        except Exception as e:
            with self.lock:
                print(f"Error Instagram {e}")
                self.error += 1
                self.q.put(email)

    def _twitter_check(self, email, proxy_func):
        headers = {
            "Host": "api.twitter.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "content-type": "application/json",
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUq265zDSWxHu storage.googleapis.com/gweb-uniblog-publish-prod/images/Google_Blog_Favicon_64x64.max-1000x1000.png",
            "x-twitter-auth-type": "OAuthSession",
            "x-twitter-client-language": "en",
            "x-twitter-active-user": "yes",
            "Origin": "https://twitter.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Te": "trailers"
        }
        data = {"email": email}
        url = "https://api.twitter.com/1.1/users/email_available.json"
        try:
            r = self.req.get(url, params=data, headers=headers, proxies=proxy_func(), timeout=5)
            if "false" in r.text:
                with self.lock:
                    with open("twitter.txt", "a") as wr:
                        wr.write(email + "\n")
                    with open("social_media.txt", "a") as wr:
                        wr.write("twitter:" + email + "\n")
                    self.counter += 1
                    print(f"[+] LINKED : {email} | PLATFORM:TWITTER")
            elif "true" in r.text:
                pass
            elif "Too Many Requests" in r.text:
                with self.lock:
                    self.q.put(email)
                    self.banned += 1
            else:
                pass
        except requests.exceptions.Timeout:
            self._twitter_check(email=email, proxy_func=proxy_func) # Retry on timeout
        except Exception as e:
            with self.lock:
                print("Error Twitter:", e)
                self.error += 1
                self.q.put(email)

    def _snapchat_check(self, email, proxy_func):
        headers = {
            'Host': 'accounts.snapchat.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://accounts.snapchat.com/accounts/merlin/login#/enter-user-email',
            'Content-Type': 'application/json',
            'X-XSRF-TOKEN': str(uuid.uuid4()),
            'Content-Length': '73',
            'Origin': 'https://accounts.snapchat.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Te': 'trailers'
        }
        data = {
            "email": email,
            "app_id": "", "app_version": "", "app_build": "",
            "client_id": "", "client_secret": "", "redirect_uri": "",
            "scope": "", "response_type": "", "state": "",
            "code_challenge": "", "code_challenge_method": "",
            "username": "", "password": "", "remember_me": False
        }
        try:
            response = self.req.post(self.snapchat_login_url, headers=headers, json=data, proxies=proxy_func(), timeout=5)
            if response.status_code == 200:
                with self.lock:
                    with open("snapchat.txt", "a") as wr:
                        wr.write(email + "\n")
                    with open("social_media.txt", "a") as wr:
                        wr.write("snapchat:" + email + "\n")
                    self.counter += 1
                    print(f"[+] LINKED : {email} | PLATFORM:SNAPCHAT")
            elif response.status_code == 400:
                pass
            elif response.status_code == 429:
                with self.lock:
                    self.q.put(email)
                    self.banned += 1
            else:
                pass
        except requests.exceptions.Timeout:
            self._snapchat_check(email=email, proxy_func=proxy_func) # Retry on timeout
        except Exception as e:
            with self.lock:
                print("Error Snapchat:", e)
                self.error += 1
                self.q.put(email)

    def _worker(self, proxy_type):
        proxy_func = lambda: self._get_proxy(proxy_type)
        while not self.q.empty():
            try:
                email = self.q.get(timeout=1)
                print(f"Targeting:{email}")

                if "1" in self.choice or "3" in self.choice:
                    self._instagram_check(email, proxy_func)
                if "1" in self.choice or "2" in self.choice:
                    self._twitter_check(email, proxy_func)
                if "1" in self.choice or "4" in self.choice:
                    self._snapchat_check(email, proxy_func)

                with self.lock:
                    self.attempts += 1
                    sys.stdout.write(f"\rAttempts:{self.attempts} | success:{self.counter} | error:{self.error} | Banned:{self.banned}")
                    sys.stdout.flush()

            except queue.Empty:
                break
            except Exception as e:
                with self.lock:
                    print(f"Worker error: {e}")
                    self.error += 1
                    self.q.put(email) # Re-add email to queue if an unexpected error occurs

    def start(self, proxy_type=1): # Default to HTTP/HTTPS proxies
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self._worker, args=(proxy_type,))
            t.daemon = True
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        print("\nFinished checking emails.")

