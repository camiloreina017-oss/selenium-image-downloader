import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 1. Entrada de datos
producto = input("Ingrese el producto: ")
cantidad = int(input("Cantidad de imágenes: "))

carpeta_base = r"COLOCAS LA URL DE LA  CARPETA DONDE SE VA ALMACENAR  LAS IMAGENES "
carpeta_destino = os.path.join(carpeta_base, producto)
os.makedirs(carpeta_destino, exist_ok=True)

# 2. Configurar Chrome
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    url_busqueda = f"https://www.bing.com/images/search?q={producto}"
    driver.get(url_busqueda)
    time.sleep(3)

    # 3. Obtener los contenedores
    tarjetas = driver.find_elements(By.CSS_SELECTOR, "a.iusc")
    guardadas = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for tarjeta in tarjetas:
        if guardadas >= cantidad:
            break

        try:
            # ABRIR: Hacer clic para abrir el visor de la imagen
            driver.execute_script("arguments[0].click();", tarjeta)
            time.sleep(1.5)

            # EXTRAER URL REAL: Obtener el atributo 'm' de la tarjeta que contiene el enlace original
            m_attr = tarjeta.get_attribute("m")
            if m_attr:
                data = json.loads(m_attr)
                img_url = data.get("murl")  # Enlace directo a la imagen original

                # GUARDAR COMO: Descargar el archivo de la URL
                if img_url and img_url.startswith("http"):
                    res = requests.get(img_url, headers=headers, timeout=5)
                    if res.status_code == 200 and "image" in res.headers.get("Content-Type", ""):
                        ruta = os.path.join(carpeta_destino, f"{producto}_{guardadas + 1}.jpg")
                        with open(ruta, "wb") as f:
                            f.write(res.content)
                        
                        guardadas += 1
                        print(f"Imagen {guardadas} guardada correctamente.")

            # CERRAR: Enviar la tecla ESC para cerrar el visor abierto y volver al feed
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)

        except Exception:
            # En caso de error, intentar cerrar el visor para no quedarse atascado
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(1)
            continue

    print(f"\n¡Proceso finalizado! Se guardaron {guardadas} imágenes en: '{carpeta_destino}'")

finally:
    driver.quit()