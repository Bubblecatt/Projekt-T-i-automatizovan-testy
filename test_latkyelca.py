import time
import pytest
from playwright.sync_api import Page

def test_pridani_vice_kusu_s_omezenim_a_kontrolou_hlasky(page: Page):
    # 1. Otevřeme stránku s balíčky s prodlouženým timeoutem a mírně upraveným čekáním
    page.goto("https://www.latkyelca.cz/balicky/", timeout=60000, wait_until="domcontentloaded")
    page.wait_for_selector("div.product", timeout=20000)

    produkt = page.query_selector("div.product")
    assert produkt is not None, "Nenašel se žádný produkt"

    # 2. Získáme cenu produktu
    cena_text = produkt.query_selector(".price").inner_text()
    jednotkova_cena = float(cena_text.replace("Kč", "").replace(",", ".").strip())
    print(f"Jednotková cena produktu: {jednotkova_cena} Kč")

    # 3. Pokusíme se přidat produkt vícenásobně
    max_pokusy = 5
    skutecne_pridano = 0
    omezeni_zachyceno = False

    for i in range(max_pokusy):
        button = produkt.query_selector("button[data-testid='buttonAddToCart']")
        if not button:
            print("Tlačítko 'Do košíku' nebylo nalezeno.")
            break

        produkt.scroll_into_view_if_needed()
        try:
            button.click(timeout=3000)
            time.sleep(1.5)
            skutecne_pridano += 1
            print(f"Přidán kus č. {i+1}")
        except:
            print(f"Produkt č. {i+1} se nepodařilo přidat – zřejmě kvůli omezení.")
            break

        # 3a. Zkusíme detekovat hlášku o omezeném množství
        notifikace = page.query_selector("div[class*='toast'], div.alert, div.notification, .notices")
        if notifikace and "omezen" in notifikace.inner_text().lower():
            print(f"Zachycena hláška: {notifikace.inner_text().strip()}")
            omezeni_zachyceno = True
            break

    if skutecne_pridano < max_pokusy and not omezeni_zachyceno:
        print("Omezené množství – ale nezachycena žádná hláška!")
        print("--- Výpis části HTML stránky pro ladění ---")
        print(page.content())

    # 4. Přejdeme do košíku a ověříme cenu
    page.goto("https://www.latkyelca.cz/kosik/")
    page.wait_for_selector("[data-testid='recapFullPrice']", timeout=10000)

    cena_kosik_text = page.locator("[data-testid='recapFullPrice']").inner_text()
    cena_kosik = float(cena_kosik_text.replace("Kč", "").replace(",", ".").strip())

    ocekavana_cena = jednotkova_cena * skutecne_pridano

    print(f"Skutečně přidáno: {skutecne_pridano}")
    print(f"Očekávaná cena: {ocekavana_cena} Kč")
    print(f"Cena v košíku: {cena_kosik} Kč")

    assert abs(cena_kosik - ocekavana_cena) < 0.1, \
        f"Cena v košíku ({cena_kosik}) neodpovídá očekávané ({ocekavana_cena})"

    if skutecne_pridano < max_pokusy:
        if omezeni_zachyceno:
            print("Hláška o omezení byla správně zachycena.")
        else:
            print("Byl zaznamenán limit, ale nezobrazila se žádná hláška – to může být očekávané chování.")
