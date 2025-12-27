import geoip2.database
import urllib.parse
import os

MMDB_PATH = "GeoLite2-Country.mmdb"

FILES = [
    "working_all.txt",
    "working_nonru.txt",
    "working_ru.txt"
]

# Счётчики по странам
country_counters = {}

def country_code_to_flag(code: str) -> str:
    # RU -> 🇷🇺
    return ''.join(chr(127397 + ord(c)) for c in code.upper())

def get_country_by_ip(ip: str):
    with geoip2.database.Reader(MMDB_PATH) as reader:
        response = reader.country(ip)
        country = response.country.name or "Unknown"
        code = response.country.iso_code or ""
        return country, code

def sign_vless(vless_url: str) -> str:
    base = vless_url.strip().split("#")[0]

    parsed = urllib.parse.urlparse(base)
    ip = parsed.hostname

    if not ip:
        return vless_url.strip()

    try:
        country, code = get_country_by_ip(ip)
    except Exception:
        country, code = "Unknown", ""

    # счётчик
    country_counters[country] = country_counters.get(country, 0) + 1
    number = country_counters[country]

    flag = country_code_to_flag(code) if code else "🏳️"

    comment = f"{flag} {country} - #{number}"

    return f"{base}#{comment}"

def process_file(filename: str):
    if not os.path.exists(filename):
        print(f"[!] Файл не найден: {filename}")
        return

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    result = []
    for line in lines:
        line = line.strip()
        if line.startswith("vless://"):
            result.append(sign_vless(line))
        else:
            result.append(line)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(result) + "\n")

    print(f"[✓] Обработан файл: {filename}")

def main():
    for file in FILES:
        process_file(file)

if __name__ == "__main__":
    main()
