from urllib.request import urlopen
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
from threading import Thread
import schedule
from time import sleep
import pandas.io.sql as sql


class database:

    def __init__(self, host_name, user_name, user_password, db_name):

        self.host_name = host_name
        self.user_name = user_name
        self.user_password = user_password
        self.db_name = db_name

    def create_db_connection(self):

        try:
            connection = mysql.connector.connect(
                host=self.host_name,
                user=self.user_name,
                passwd=self.user_password,
                database=self.db_name
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return connection

    def execute_query(self, connection, query):
        try:
            with connection:
                with connection.cursor() as cursor:
                    for result in cursor.execute(query, multi=True):
                        if result.with_rows:
                            print(result.fetchall())
                    connection.commit()
        except Error as err:
            print(err)

    def export_to_excel(self, columns, connection):

        df = sql.read_sql(f'select * from product', connection)
        df.to_excel('spreadsheet.xlsx')

class currency:

    def __init__(self, url):

        self.url = url

    def _extract_data(self):
        html_content = urlopen(self.url)
        data = BeautifulSoup(html_content, "lxml")
        return data.text

    def get_value(self):
        data = self._extract_data()
        num = data.find('mid')
        num += 5
        currency = data[num:num+6]
        return float(currency)

mydb = database('localhost', 'root', '1234', 'mydb')
connection = mydb.create_db_connection()

url_usd = 'https://api.nbp.pl/api/exchangerates/rates/a/usd/'
url_eur = 'https://api.nbp.pl/api/exchangerates/rates/a/eur/'

def wait_for_input(mydb, columns, connection):
    prompt = None
    prompt = input('Press Enter to create excel spreadsheet')
    if prompt != None:
        mydb.export_to_excel(columns, connection)

new_thread = Thread(target=wait_for_input, args=(mydb, desired_columns, connection))

def main():

    currency_usd = currency(url_usd)
    val_usd = currency_usd.get_value()

    currency_eur = currency(url_eur)
    val_eur = currency_eur.get_value()

    query = '''UPDATE `mydb`.`product` SET `%s` = `UnitPrice`*%f;
               UPDATE `mydb`.`product` SET `%s` = `UnitPrice`*%f;'''%('UnitPriceUSD', val_usd, 'UnitPriceEuro', val_eur)

    mydb.execute_query(connection, query)

if __name__ == '__main__': 
    
    schedule.every().day.at('16:00').do(main)
    while True:

        new_thread.start()
        schedule.run_pending()
        sleep(1)
        new_thread.join(10)
        new_thread = Thread(target=wait_for_input, args=(mydb, desired_columns, connection))
    





    






    




