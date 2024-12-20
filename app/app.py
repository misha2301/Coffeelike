import subprocess

from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)


def get_drinks(sort_by=None,order = None, search = None):
    # Подключаемся к базе данных
    conn = sqlite3.connect('../drinks.db')
    cursor = conn.cursor()

    # Формируем SQL-запрос
    query = "SELECT name, size, kcal, protein, fats, carbs, image_url FROM drinks"

    # Добавляем фильтрацию по поисковому запросу
    if search:
        query += f" WHERE LOWER(name) LIKE ('%{search.lower()}%')"

    if sort_by:
        query += f" ORDER BY {sort_by} {order.upper() if order else ''}"
    cursor.execute(query)

    cursor.execute(query)
    drinks = cursor.fetchall()
    conn.close()

    return drinks


@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')  # Получаем поисковый запрос
    sort_by = request.args.get('sort_by')# Получаем параметр сортировки
    order = request.args.get('order')  # Получаем параметр порядка сортировки (по возрастанию или убыванию)
    drinks = get_drinks(sort_by=sort_by, order=order, search=search_query)  # Получаем напитки из базы
    return render_template('index.html', drinks=drinks)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Запускаем скрипт скрапинга
        subprocess.run(["python", "scrapping.py"], check=True)
        return jsonify({"message": "Скрапинг успешно завершён!"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"message": "Ошибка при запуске скрапинга!", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9191, debug=True)
