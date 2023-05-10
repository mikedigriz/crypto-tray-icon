import win32con
import win32console
import win32gui
from pathlib import Path
from typing import Tuple
from PIL import Image
from bs4 import BeautifulSoup
from pystray import Icon, MenuItem, Menu
from requests import get
from win11toast import toast


def get_text(url: str) -> Tuple[str, bool]:
    """
    Получение кода страницы по заданной ссылке.
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/113.0.0.0 Safari/537.36"
    }
    try:
        res = get(url=url, headers=headers)
        return res.text if res.status_code == 200 else False
    except Exception:
        return False


def parse_course(url: str) -> Tuple[str, bool]:
    """
    Парсинг стоимости основной валюты.
    """
    try:
        if res := get_text(url):
            soup = BeautifulSoup(res, "lxml")
            course = (
                soup.find("div", class_="dDoNo ikb4Bb gsrt")
                .find("span", class_="DFlfde SwHCTb")
                .text.strip()
            )
            return course if course else False
        else:
            return False
    except AttributeError:
        return False


def parse_crypto(url: str) -> Tuple[str, bool]:
    """
    Парсинг стоимости криптовалюты по отношению к доллару.
    """
    try:
        if res := get_text(url):
            soup = BeautifulSoup(res, "lxml")
            course = soup.find("span", class_="pclqee").text.strip()
            return course if course else False
        else:
            return False
    except AttributeError:
        return False


def notify_send(text: str, url="", icon=None):
    """
    Вывод уведомления с активными кнопками.
    """
    if icon:
        buttons = [
            {
                "activationType": "protocol",
                "arguments": f"{url}",
                "content": "Открыть в Google",
            },
            {
                "activationType": "protocol",
                "arguments": "http:Dismiss",
                "content": "Закрыть",
            },
        ]
        toast(
            "Курс",
            f"{text}",
            buttons=buttons,
            icon=icon,
            on_dismissed=lambda *args: None,
        )
    else:
        toast(
            "Курс",
            f"{text}",
            button={
                "activationType": "protocol",
                "arguments": "http:Dismiss",
                "content": "Закрыть",
            },
            icon=icon,
            on_dismissed=lambda *args: None,
        )


def notify_choice(course: str, url: str, val: str):
    """
    Выбор сообщения для определенной валюты, в зависимости от значения val.
    """
    if val == "b":
        icon = {
            "src": f'{Path.cwd() / "icons" / "dollar.png"}',
            "placement": "appLogoOverride",
        }
        notify_send(f"USD/RUB: {course}", url, icon)
    elif val == "btc":
        icon = {
            "src": f'{Path.cwd() / "icons" / "bitcoin.png"}',
            "placement": "appLogoOverride",
        }
        notify_send(f"BTC/USD: {course}", url, icon)
    elif val == "eth":
        icon = {
            "src": f'{Path.cwd() / "icons" / "eth.png"}',
            "placement": "appLogoOverride",
        }
        notify_send(f"ETH/USD: {course}", url, icon)


def click(icon: Icon, item: MenuItem):
    """
    Обработка полученных значений меню.  В зависимости от выбранного
    пункта выполняется запрос данных по определенной валюте.
    """
    if str(item) == "USD":
        url = "https://www.google.ru/search?q=курс+USD"
        if course := parse_course(url):
            notify_choice(course, url, "b")
        else:
            notify_send("Данные по курсу не получены")
    elif str(item) == "BTC":
        url = "https://www.google.ru/search?q=курс+BTC+к+доллару"
        if course := parse_crypto(url):
            notify_choice(course, url, "btc")
        else:
            notify_send("Данные по курсу не получены")
    elif str(item) == "ETH":
        url = "https://www.google.ru/search?q=курс+ETH+к+доллару"
        if course := parse_crypto(url):
            notify_choice(course, url, "eth")
        else:
            notify_send("Данные по курсу не получены")
    elif str(item) == "Выход":
        icon.stop()


def main():
    image = Image.open(Path.cwd() / "icons" / "money.png")
    icon = Icon(
        "money",
        image,
        menu=Menu(
            MenuItem(
                "Курс",
                Menu(
                    MenuItem("USD", click),
                    MenuItem("BTC", click),
                    MenuItem("ETH", click),
                ),
            ),
            MenuItem("Выход", click),
        ),
    )
    win32gui.ShowWindow(win32console.GetConsoleWindow(), win32con.SW_HIDE)
    icon.run()


if __name__ == "__main__":
    main()
