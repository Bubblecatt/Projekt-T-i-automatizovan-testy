import pytest
from playwright.sync_api import Page, expect

# Test 1: Přidání produktu do košíku a kontrola správné celkové ceny
def test_add_to_cart_and_verify_price(page: Page):
    page.goto("https://www.latkyelca.cz")
    page.click("text=Novinky")
    page.click("text=Bavlna")  # Změň, pokud tento produkt není dostupný
    page.fill("input[name='quantity']", "2")
    unit_price_text = page.locator(".our_price_display").inner_text()
    unit_price = float(unit_price_text.replace(" Kč", "").replace(",", "."))
    page.click("button:has-text('Přidat do košíku')")
    page.click("a:has-text('Košík')")
    total_price_text = page.locator(".cart_total_price").inner_text()
    total_price = float(total_price_text.replace(" Kč", "").replace(",", "."))
    assert total_price == unit_price * 2

# Test 2: Kontrola validace formuláře – povinná pole
def test_required_fields_validation(page: Page):
    page.goto("https://www.latkyelca.cz/objednavka")
    page.click("button:has-text('Odeslat objednávku')")
    expect(page.locator(".form-error")).to_contain_text("Toto pole je povinné")

# Test 3: Simulace přechodu na platební bránu
def test_payment_redirect(page: Page):
    page.goto("https://www.latkyelca.cz")
    page.click("text=Novinky")
    page.click("text=Bavlna")
    page.click("button:has-text('Přidat do košíku')")
    page.click("a:has-text('Košík')")
    page.click("a:has-text('Pokračovat v objednávce')")
    expect(page).to_have_url(lambda url: "platba" in url or "payment" in url)
