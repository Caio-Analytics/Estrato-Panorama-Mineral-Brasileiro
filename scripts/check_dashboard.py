"""Browser regression checks against the generated, fully offline dashboard."""
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    assert (ROOT / 'docs/index.html').read_bytes() == (ROOT / 'output/dashboard.html').read_bytes()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, color_scheme="light")
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto((ROOT / 'output/dashboard.html').as_uri())
        expect(page).to_have_title('Estrato Panorama Mineral Brasileiro')
        expect(page.locator('#bruta-results')).to_contain_text('6.313 registros')
        expect(page.locator('#beneficiada')).to_be_hidden()
        # Search accents, empty results, reset and keyboard-operated chips.
        search = page.locator('#bruta-substanciaSearch')
        search.fill('niquel')
        expect(page.locator('#bruta-chartSubstancias')).to_contain_text('Níquel', ignore_case=True)
        search.fill('sem-resultados-xyz')
        expect(page.locator('#bruta-results')).to_contain_text('Nenhum registro')
        page.locator('#bruta-resetFilters').click()
        expect(page.locator('#bruta-results')).to_contain_text('6.313 registros')
        chip = page.locator('#bruta-regiaoChips button').first
        chip.focus()
        chip.press('Space')
        expect(chip).to_have_attribute('aria-pressed', 'false')
        page.locator('#bruta-resetFilters').click()
        expect(chip).to_have_attribute('aria-pressed', 'true')
        # A one-year recorte must remain chartable, without a fictional YoY.
        page.locator('#bruta-anoFrom').select_option('2025')
        expect(page.locator('#bruta-tableSerie tbody tr')).to_have_count(1)
        expect(page.locator('#bruta-tableSerie tbody tr td').nth(3)).to_have_text('—')
        page.locator('#bruta-resetFilters').click()
        toggle = page.locator('[data-target="bruta-tableSerie"]')
        toggle.click()
        expect(page.locator('#bruta-tableSerie')).to_be_hidden()
        toggle.click()
        expect(toggle).to_have_text('Ocultar tabela')
        # A gap between years must not produce a year-over-year comparison.
        page.evaluate("DATA.bruta.rows = DATA.bruta.rows.filter(r => r[0] === 2010 || r[0] === 2012)")
        page.locator('#bruta-resetFilters').click()
        expect(page.locator('#bruta-tableSerie tbody tr')).to_have_count(2)
        expect(page.locator('#bruta-tableSerie tbody tr').nth(1).locator('td').nth(3)).to_have_text('—')
        page.reload()
        # Focus exposes the same value as pointer hover.
        mark = page.locator('#bruta-chartValor svg [tabindex="0"]').first
        mark.focus()
        expect(page.locator('#tooltip')).to_have_css('opacity', '1')
        mark.press('Escape')
        expect(page.locator('#tooltip')).to_have_css('opacity', '0')
        page.locator('a[href="#beneficiada"]').click()
        expect(page.locator('#beneficiada')).to_be_visible()
        expect(page.locator('#bruta')).to_be_hidden()
        page.reload()
        expect(page.locator('#beneficiada')).to_be_visible()
        page.locator('a[href="#beneficiamento"]').click()
        expect(page.locator('#beneficiamento')).to_be_visible()
        page.go_back()
        expect(page.locator('#beneficiada')).to_be_visible()
        page.locator('a[href="#metodologia"]').click()
        expect(page.locator('#metodologia')).to_have_attribute('open', '')
        # Themes persist; system follows OS changes. No page overflow at target sizes.
        page.locator('#themeToggle').click()
        expect(page.locator('html')).to_have_attribute('data-theme', 'light')
        page.locator('#themeToggle').click()
        page.reload()
        expect(page.locator('html')).to_have_attribute('data-theme', 'dark')
        page.locator('#themeToggle').click()
        page.emulate_media(color_scheme='dark', reduced_motion='reduce')
        expect(page.locator('html')).to_have_attribute('data-theme', 'dark')
        for width in (375, 768, 1024, 1440):
            page.set_viewport_size({'width': width, 'height': 900})
            for area in ('bruta', 'beneficiada', 'beneficiamento'):
                page.locator(f'.section-nav a[href="#{area}"]').click()
                expect(page.locator(f'#{area}')).to_be_visible()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, area)
        assert not errors, errors
        browser.close()
    print('Dashboard OK: offline, filters, keyboard, navigation, themes, four viewport sizes; no JS errors.')


if __name__ == '__main__':
    main()
