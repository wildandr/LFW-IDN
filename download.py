import os
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Path ke file CSV dan direktori penyimpanan
csv_path = "C:/Users/Administrator/Downloads/scrapping/sorted.csv"  # Ganti dengan path file CSV Anda
output_dir = "C:/Users/Administrator/Downloads/scrapping/downloaded_images"  # Ganti dengan path tujuan penyimpanan gambar

# Baca CSV sebagai plain text dan konversi ke daftar
with open(csv_path, 'r') as file:
    names = [line.strip() for line in file if line.strip()]

# Fungsi untuk format nama folder
def format_name_for_folder(name):
    return name.replace(" ", "_").lower()

# Fungsi untuk format nama pencarian
def format_name_for_search(name):
    return name.replace("_", " ")

# Inisialisasi Selenium WebDriver dengan WebDriver Manager (tanpa headless mode)
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

def download_images(query, folder_name, limit=30, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        # Ubah nama query untuk pencarian dengan spasi
        search_query = format_name_for_search(query)
        
        # Buka Google Images
        print(f"Mencari gambar untuk '{search_query}' (percobaan {retry_count + 1})")
        driver.get("https://www.google.com/imghp?hl=en")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)  # Tunggu hingga hasil pencarian muncul

        # Scroll untuk memuat lebih banyak gambar
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Ambil elemen gambar
        image_elements = driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
        os.makedirs(folder_name, exist_ok=True)

        count = 0
        for img in image_elements:
            if count >= limit:
                break
            try:
                # Klik thumbnail untuk membuka versi gambar yang lebih besar
                img.click()
                time.sleep(1)  # Tunggu hingga gambar besar dimuat

                # Ambil URL gambar besar
                large_image = driver.find_element(By.CSS_SELECTOR, "img.n3VNCb")
                img_url = large_image.get_attribute("src")
                
                # Simpan gambar jika URL valid
                if img_url and "http" in img_url:
                    urllib.request.urlretrieve(img_url, os.path.join(folder_name, f"{count + 1}.jpg"))
                    count += 1
                    print(f"Downloaded {count}/{limit} images for {search_query}")
            except Exception as e:
                print(f"Could not download image {count + 1} for {search_query}: {e}")

        # Log hasil unduhan
        print(f"{search_query} - Downloaded {count}/{limit} images")

        # Jika berhasil mengunduh setidaknya 1 gambar, hentikan retry
        if count > 0:
            break
        else:
            retry_count += 1
            print(f"Attempt {retry_count} for {search_query} failed to download images. Retrying...")

# Loop setiap nama untuk mencari dan mengunduh gambar
for name in names:
    folder_name = os.path.join(output_dir, format_name_for_folder(name))
    print(f"Starting download for {name}...")
    download_images(name, folder_name)

# Tutup browser
driver.quit()
