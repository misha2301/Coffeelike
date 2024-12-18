from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


def get_drinks(sort_by=None,order = None, search = None):
    # Подключаемся к базе данных
    conn = sqlite3.connect('drinks.db')
    cursor = conn.cursor()

    # Формируем SQL-запрос
    query = "SELECT name, size, kcal, protein, fats, carbs, image_url FROM drinks"

    # Добавляем фильтрацию по поисковому запросу
    if search:
        query += f" WHERE LOWER(name) LIKE ('%{search.lower()}%')"

    # Добавляем сортировку, если указано
    if sort_by:
        query += f" ORDER BY {sort_by}"
        if order == "desc":
            query += " DESC"
        elif order == "asc":
            query += " ASC"

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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9191, debug=True)
