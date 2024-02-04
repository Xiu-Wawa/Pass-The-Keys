from src.utils import By


class CategoryPageLocators:
    pass

class LogoPopup:
    POPUP = (By.XPATH, '//span[@aria-label="blue Genius logo"]')
    CLOSE_POPUP = (By.XPATH, '//span[@aria-label="blue Genius logo"]/../../../..//button[@aria-label="Dismiss sign in information."]')

class Pagination:
    NEXT_PAGE = (By.XPATH, '//button[@aria-label="Next page"]')

class PropertyLinks:
    PROPERTY_LIST = (By.XPATH, '//h3/a')
    CHECK_PROPERTY_LIST = (By.XPATH, '//div[@id="basiclayout"]/following-sibling::div')

class Details:
    JSON_DETAILS = (By.XPATH, '//script[@type="application/ld+json"]')
    MANAGER = (By.XPATH, "//h2/div[contains(text(), 'Hosted')] | //h2/div[@class='e1f827110f' or contains(text(), 'Managed by')]")
    STATUS = (By.XPATH, '//div[@data-testid="property-highlights"]//div[contains(text(), "Entire") or contains(text(), "Apartments") or contains(text(), "Houses")]')
    PROPERTY_TYPE = (By.XPATH, '//h1/a[@class="bui_breadcrumb__link_masked"]')