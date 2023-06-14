import os
import mysql.connector.pooling
from dotenv import load_dotenv, find_dotenv
from flask import Flask, redirect, render_template, request

load_dotenv(find_dotenv())

# If you want to use your own environment variables from your local .env file, then change all instances of:
# "os.environ.get()" to "os.getenv()".
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name=os.environ.get('POOL_NAME'),
    pool_reset_session=True,
    pool_size=4,
    host=os.environ.get('HOST'),
    user=os.environ.get('USER'),
    password=os.environ.get('PASSWORD'),
    db=os.environ.get('DB')
)

# Configure application & ensure templates are auto-reloaded
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key=os.environ.get('SECRET_KEY')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        connection = pool.get_connection()
        cursor = connection.cursor()

        name = request.form.get("name")
        month = int(request.form.get("months"))
        day = int(request.form.get("days"))

        cursor.execute(f"INSERT INTO birthdays (name, month, day) VALUES ('{name}', {month}, {day})")
        connection.commit()
        connection.close()
        return redirect("/")
    else:
        connection = pool.get_connection()
        cursor = connection.cursor()

        birthdays = cursor.execute("SELECT * FROM birthdays")
        birthdays = cursor.fetchall()
        connection.close()
        return render_template("index.html", birthdays=birthdays)
        