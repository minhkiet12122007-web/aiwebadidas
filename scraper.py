import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def maybe_reexec_venv():
    workspace_root = Path(__file__).resolve().parent
    venv_python = workspace_root / '.venv' / \
        ('Scripts' if sys.platform == 'win32' else 'bin') / \
        ('python.exe' if sys.platform == 'win32' else 'python')
    try:
        if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
            print(f"Doi Python interpreter sang .venv: {venv_python}")
            cmd = [str(venv_python), str(
                Path(__file__).resolve())] + sys.argv[1:]
            rc = subprocess.run(cmd).returncode
            sys.exit(rc)
    except Exception as exc:
        print(f"Khong the chuyen sang interpreter .venv: {exc}")


def install_packages(packages):
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + packages
    print("   Đang cài đặt gói cần thiết:")
    print("   ", " ".join(f'\"{p}\"' if ' ' in p else p for p in cmd))
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except Exception as exc:
        print(f"   Lỗi khi chạy pip: {exc}")
        return False

    if proc.returncode != 0:
        print("   Cài đặt thất bại:")
        print(proc.stderr.strip() or proc.stdout.strip())
        return False

    print("   Cài đặt thành công.")
    return True


def find_chrome_executable():
    candidates = []
    if sys.platform == "win32":
        candidates.extend([
            os.path.expandvars(
                r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(
                r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expanduser(
                r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ])
    else:
        candidates.extend([
            shutil.which("google-chrome"),
            shutil.which("chromium"),
            shutil.which("chrome"),
        ])
    candidates = [p for p in candidates if p and os.path.isfile(p)]
    if candidates:
        return candidates[0]
    fallback = shutil.which("chrome")
    return fallback


def get_chrome_major_version():
    if sys.platform == "win32":
        try:
            import winreg
            for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    key = winreg.OpenKey(
                        root, r"Software\Google\Chrome\BLBeacon")
                    version, _ = winreg.QueryValueEx(key, "version")
                    match = re.search(
                        r"(\d+)\.(\d+)\.(\d+)\.(\d+)", str(version))
                    if match:
                        return int(match.group(1))
                except Exception:
                    continue
        except Exception:
            pass

    chrome_path = find_chrome_executable()
    if not chrome_path:
        return None
    try:
        proc = subprocess.run([chrome_path, "--version"],
                              capture_output=True, text=True, timeout=5)
        output = proc.stdout.strip() or proc.stderr.strip()
        match = re.search(r"(\d+)\.(\d+)\.(\d+)\.(\d+)", output)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return None


def run_scraper():
    try:
        import undetected_chromedriver as uc
    except Exception as e:
        print("Loi khi tai thu vien 'undetected_chromedriver':")
        print(f"   {type(e).__name__}: {e}")

        packages = ["undetected-chromedriver", "selenium", "setuptools"]
        if isinstance(e, ModuleNotFoundError) and e.name == 'distutils':
            print("   Python 3.14 đã loại bỏ distutils khỏi thư viện chuẩn.")
            print("   Đang nâng cấp setuptools và thử lại...")
        else:
            print("   Đang cài đặt undetected-chromedriver, selenium và setuptools...")

        if not install_packages(packages):
            print("   Vui lòng chạy thủ công:")
            print(
                f"   {sys.executable} -m pip install undetected-chromedriver selenium setuptools")
            return

        try:
            import undetected_chromedriver as uc
        except Exception as e2:
            print("   Sau khi cài, vẫn không import được:")
            print(f"   {type(e2).__name__}: {e2}")
            return

    print("Dang khoi tao trinh duyet chong bi chan (Undetected Mode)...")

    options = uc.ChromeOptions()

    # Tắt headless để bạn có thể nhìn thấy và giải CAPTCHA nếu trang web yêu cầu
    # options.add_argument('--headless')

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    driver = None
    try:
        # Khởi tạo driver đặc biệt
        chrome_major = get_chrome_major_version()
        if chrome_major:
            print(
                f"   Phat hien Chrome major version: {chrome_major}, su dung version_main={chrome_major}")
            driver = uc.Chrome(options=options, version_main=chrome_major)
        else:
            driver = uc.Chrome(options=options)

        url = "https://www.adidas.com.vn/vi/nam-giay"
        print(f"Dang truy cap: {url}")
        driver.get(url)

        # Chờ đợi một chút để trang tải (Adidas có thể hiện màn hình chờ)
        print("Vui long cho 10 giay de trang tai het noi dung...")
        time.sleep(10)

        # Cuộn trang từ từ để tải thêm sản phẩm (Lazy Load)
        print("Dang cuon trang de lay them du lieu...")
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {(i+1) * 800});")
            time.sleep(3)

        # Sử dụng WebDriverWait để đợi sản phẩm hiện ra
        print("Dang tim kiem cac the san pham...")
        wait = WebDriverWait(driver, 20)

        # Adidas hay thay đổi class, mình sẽ thử tìm theo thuộc tính testid nếu class thất bại
        try:
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".glass-product-card")))
            items = driver.find_elements(
                By.CSS_SELECTOR, ".glass-product-card")
        except Exception:
            # Phương án dự phòng nếu class .glass-product-card bị đổi
            items = driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='product-card']")

        products = []

        for item in items:
            try:
                # Lấy tên sản phẩm
                name = item.find_element(
                    By.CSS_SELECTOR, "[data-testid='product-card-title'], .glass-product-card__title").text

                # Lấy giá sản phẩm
                try:
                    price_text = item.find_element(
                        By.CSS_SELECTOR, ".gl-price-item").text
                except Exception:
                    price_text = item.find_element(
                        By.CSS_SELECTOR, ".gl-price-item--sale").text

                price = int(''.join(filter(str.isdigit, price_text)))

                # Lấy hình ảnh (Adidas dùng lazy load cực mạnh nên cần kiểm tra nhiều thuộc tính)
                img_element = item.find_element(By.TAG_NAME, "img")
                img = img_element.get_attribute("src") or img_element.get_attribute(
                    "data-src") or img_element.get_attribute("srcset")

                # Lấy đường dẫn sản phẩm
                link = item.find_element(
                    By.TAG_NAME, "a").get_attribute("href")

                products.append({
                    "name": name,
                    "price": price,
                    "img": img,
                    "url": link
                })
            except Exception:
                continue

        # Lưu dữ liệu vào file JSON
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump({"products": products}, f, ensure_ascii=False, indent=4)

        print("-" * 30)
        print(f"✅ Xong rồi! Đã lấy được {len(products)} sản phẩm.")
        print("📂 Dữ liệu đã được lưu vào file: database.json")
        print("-" * 30)

    except Exception as e:
        print(f"Loi he thong: {e}")
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    maybe_reexec_venv()
    run_scraper()
