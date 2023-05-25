from selenium.webdriver.common.by import By

EMAIL_FORM_LOCATOR = (
    By.ID,
    'emailform'
)

EMAIL_INPUT_LOCATOR = (
    By.TAG_NAME,
    'input'
)

EMAIL_BTN_LOCATOR = (
    By.TAG_NAME,
    'button'
)

LOGIN_WITH_PASSWORD_URL_LOCATOR = (
    By.ID,
    'auth-page-google-password-fallback'
)

PASSWORD_FORM_LOCATOR = (
    By.ID,
    'loginform'
)

PASSWORD_INPUT_LOCATOR = (
    By.ID,
    'ifl-InputFormField-131'
)

LOGIN_BTN_LOCATOR = (
    By.TAG_NAME,
    'button'
)