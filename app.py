import base64
from datetime import datetime

import pymysql

connection = pymysql.connect(host="localhost", user="root", password="", database="FoodOrderDB")
print("connected successfully")

from flask import *

# start
app = Flask(__name__)
app.secret_key = "programming"


@app.route('/')
def home():
    cursor = connection.cursor()
    sql = "SELECT * FROM Meal_order"
    cursor.execute(sql)
    row = cursor.fetchall()
    return render_template("order.html", meals=row)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pswd']

        cursor = connection.cursor()
        sql = 'SELECT * FROM users WHERE email=%s AND password=%s'
        cursor.execute(sql, (email, password))

        if cursor.rowcount == 0:
            return render_template('sign_up.html', error="Invalid Credential Try Again")
        elif cursor.rowcount == 1:
            row = cursor.fetchone()
            session['key'] = row[0]  # user_name
            session['email'] = row[1]  # Email
            print(session['email'])
            print(session['key'])

            return redirect('/')
        else:
            return render_template('sign_up.html', error="Something  wrong with your Credential")

    return render_template('sign_up.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':

        name = request.form['txt']
        email = request.form['email']
        password = request.form['pswd']
        cursor = connection.cursor()
        sql = 'INSERT INTO users (name, email, password) VALUES (%s, %s,%s)'
        cursor.execute(sql, (name, email, password))
        connection.commit()

        return render_template('sign_up.html', message="REGISTERED SUCCESSFULLY")

    else:
        return render_template('sign_up.html')

@app.route('/logout')
def logout():
    if 'key' in session:
        session.clear()
        return redirect('/login')

@app.route('/single/<product_id>')
def single(products_id):
    cursor = connection.cursor()
    sql = 'SELECT * FROM meals WHERE product_id=%s'
    cursor.execute(sql, products_id)

    row = cursor.fetchone()

    return render_template('single.html', item_data=row)


class HTTPBasicAuth:
    pass


@app.route('/mpesa_payment', methods=['POST', 'GET'])
def mpesa(requests=None):
    if request.method == 'POST':
        phone = request.form['phone']
        amount = request.form['amount']

        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()

        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')

        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"

        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())

        password = encoded.decode('utf-8')

        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": print(int(session['all_total_price'])),  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "Modcom",
            "TransactionDesc": "Modcom"
        }

        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)

        return render_template('mpesa_payment.html', message="Please check your phone for Payment")

    else:
        return render_template('mpesa_payment.html')

    @app.route('/cart')
    def cart():
        if 'key' in session:
            return render_template('cart.html')
        else:
            return redirect('/login')






app.run(debug=True)
