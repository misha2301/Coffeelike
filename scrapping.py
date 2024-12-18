from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from bs4 import BeautifulSoup
import requests

# Инициализация приложения Flask и SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drinks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Модель напитка
class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    kcal = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)


def scrape_and_save():
    # URL сайта
    url = "https://coffee-like.com/menu/drinks"

    # Заголовки для имитации запроса из браузера
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    # Отправка GET-запроса
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Создание объекта BeautifulSoup для парсинга
    soup = BeautifulSoup(response.text, "html.parser")

    # Список всех карточек напитков
    drinks = soup.find_all("div", class_="drinks-item__name")
    drink_urls = soup.find_all('a', class_='drinks-item drinks-item_home')

    q = 0
    for drink in drinks:
        drink_name = drink.get_text(strip=True)
        detail_url = drink_urls[q].get('href')
        q += 1

        detail_response = requests.get(detail_url, headers=headers)
        detail_response.raise_for_status()
        detail_soup = BeautifulSoup(detail_response.text, "html.parser")

        # Состав и калорийность
        composition = detail_soup.find_all('span', class_='list__item')
        drink_info = detail_soup.find_all('span')[5:-1]
        drink_info = [info.get_text(strip=True).strip() for info in drink_info]

        var_sizes = ["60 мл", "200 мл", "S", "M", "L", "XL"]

        sizes = list(drink_info)
        for j in range(len(drink_info) - 1, -1, -1):
            if drink_info[j] in var_sizes:
                drink_info.pop(j)

        energy_values = drink_info
        sizes = list(set(sizes) - set(energy_values))

        order_dict = {size: index for index, size in enumerate(var_sizes)}
        sizes = sorted(sizes, key=lambda x: order_dict.get(x, float('inf')))

        for i, size in enumerate(sizes):
            if drink_name == "Латте лимонный пирог" and size == "XL":
                kcal = '461'
                protein = '12'
                fats = '22'
                carbs = '52'
            elif drink_name == "Американо":
                kcal = '5'
                protein = '0'
                fats = '0'
                carbs = '0'
            else:
                kcal = energy_values[1 + i * 8]
                protein = energy_values[3 + i * 8]
                fats = energy_values[5 + i * 8]
                carbs = energy_values[7 + i * 8]

            div = detail_soup.find("div", class_='drink-card__image')
            image_url = None
            if div:
                img = div.find('img')
                if img and 'src' in img.attrs:
                    image_url = img['src']

            # Проверка существования записи в базе данных
            existing_drink = Drink.query.filter_by(name=drink_name.lower(), size=size).first()
            if not existing_drink:
                new_drink = Drink(
                    name=drink_name.lower(),
                    size=size,
                    kcal=float(kcal),
                    protein=float(protein),
                    fats=float(fats),
                    carbs=float(carbs),
                    image_url=image_url
                )
                db.session.add(new_drink)

    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Создание таблиц
        scrape_and_save()
