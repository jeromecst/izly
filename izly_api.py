import requests
import re
from bs4 import BeautifulSoup


def get_csrf() -> tuple[dict, str]:
    """
    get the csrf token and the cookies to use in next requests

    Raises:
            Exception: if the csrf token can't be found

    Returns:
            tuple[dict, str]: list of cookies to use in next requests and the csrf token
    """
    login_form = requests.get("https://mon-espace.izly.fr/Home/Logon", timeout=20)
    if login_form.status_code != 200:
        raise PermissionError("Error: can't get the login form")
    soup = BeautifulSoup(login_form.text, "html.parser")
    return login_form.cookies, soup.find("input", {"name": "__RequestVerificationToken"})["value"]


def get_credentials(cookies: dict, csrf: str, username: str, password: str) -> dict:
    """
    get the credentials of the izly account to perform actions as the user

    Args:
            cookies (dict): list of cookies to use in next requests
            csrf (str): csrf token
            username (str): username of the izly account
            password (str): password of the izly account

    Returns:
            dict: list of cookies to use in next requests
    """

    login = requests.post(
        "https://mon-espace.izly.fr/Home/Logon",
        data={
            "__RequestVerificationToken": csrf,
            "UserName": username,
            "Password": password,
        },
        cookies=cookies,
        allow_redirects=False,
        timeout=20
    )

    if login.status_code != 302:
        raise PermissionError("Error: Invalid credentials")

    if ".ASPXAUTH" not in login.cookies:
        raise PermissionError("Error: invalid credentials")

    cookies[".ASPXAUTH"] = login.cookies[".ASPXAUTH"]
    return cookies


def get_qrcode(credentials: dict, codes: int = 1) -> list:
    """
    get the qr-code of the izly account

    Args:
            credentials (dict): list of cookies to use in next requests
            codes (int): number of qr-code to generate

    Returns:
            list: list of qr-code
    """
    base_codes = requests.post(
        "https://mon-espace.izly.fr/Home/CreateQrCodeImg",
        cookies=credentials,
        data={
            "nbrOfQrCode": str(codes)
        },
        allow_redirects=True,
        timeout=20
    )

    if base_codes.status_code != 200:
        raise requests.exceptions.RequestException(
            f"Error {base_codes.status_code}: can't get the qr-code"
        )

    return base_codes.json()


def get_balance(credentials: dict) -> list:
    """
    get the qr-code of the izly account

    Args:
            credentials (dict): list of cookies to use in next requests
            codes (int): number of qr-code to generate

    Returns:
            list: list of qr-code
    """
    balance = requests.get(
        "https://mon-espace.izly.fr/",
        cookies=credentials,
        allow_redirects=True,
        timeout=20
    )

    if balance.status_code != 200:
        raise requests.exceptions.RequestException(
            f"Error {balance.status_code}: can't get the qr-code"
        )

    m = re.search(r"id=\"balance\".*\n.*\+(\d+,?\d+).*\n", balance.text)
    return m.group(1) + '€'
