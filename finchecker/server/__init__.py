"""Init file with all functionality for server."""

import asyncio

import yfinance as yf
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


full_name = {
        'correlation table': 'corr',
        'stock returns': 'stock',
        'dividends': 'dividends',
        'financials': 'fin',
        'balance sheet': 'balance',
        'cash flow': 'cash',
        'recommendations': 'recom',
        'major holders': 'm_hold',
        'institutional holders': 'i_hold',
        'graphics': 'graphics',
        'sayall': 'sayall',
        'predict': 'predict'
    }

path_xml = str(Path(__file__).parent.resolve()) + '/stat.xml'
tree = ''
root = ''

path_login = str(Path(__file__).parent.resolve()) + '/login.xml'
tree_login = ''
root_login = ''

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def create_xml():
    global tree, root, path_xml, path_login, tree_login, root_login

    if not Path(path_xml).is_file():
        root = ET.Element("statistics")
        tree = ET.ElementTree(root)
        indent(root)

        tree.write(path_xml, encoding="utf-8", xml_declaration=True)

    tree = ET.parse(path_xml)
    root = tree.getroot()

    if not Path(path_login).is_file():
        root_login = ET.Element("login")
        tree_login = ET.ElementTree(root_login)
        indent(root_login)

        tree_login.write(path_login, encoding="utf-8", xml_declaration=True)

    tree_login = ET.parse(path_login)
    root_login = tree_login.getroot()

    return True


def add_user(username, pswd, full_name):
    global tree, root, path_xml, tree_login, root_login, path_login

    for child in root_login:
        if child.get('id') == username:
            return False

    field = ET.SubElement(root_login, "user")
    field.set("id", username)
    field.text = pswd

    tree_login = ET.ElementTree(root_login)
    indent(root_login)
    tree_login.write(path_login, encoding="utf-8", xml_declaration=True)

    field = ET.SubElement(root, "user")
    field.set("id", username)

    for i in full_name:
        f = ET.SubElement(field, "_".join(i.split()))
        f.text = "0"
        f.set('updated', 'no')

    tree = ET.ElementTree(root)
    indent(root)
    tree.write(path_xml, encoding="utf-8", xml_declaration=True)

    return True


def login(username, pswd):
    global tree_login, root_login, path_login

    for child in root_login:
        if child.get('id') == username:
            if child.text == pswd:
                return True
            else:
                return False

    return True

def update_stat(name, cmd):
    global tree, root, path_xml
    for i in full_name:
        if full_name[i] == cmd:
            cmd = i
            break

    for user in root:
        if user.get('id') == name:
            for command in user:
                if command.tag == cmd:
                    command.text = str(int(command.text) + 1)
                    command.set("updated", "yes")
                    break

    tree = ET.ElementTree(root)
    indent(root)
    tree.write(path_xml)


async def send_file(writer, uid, filename, ext):
    """
    Send chosen file.
    
    :param writer: output stream to socket
    :param uid: uid of file on client
    :param file: file being sent 
    """
    writer.write(f"beg file {uid} {ext}\n".encode())
    await writer.drain()

    f = open(filename + ext, "rb")
    await asyncio.sleep(0.01)

    while data := f.read():
        writer.write(f"{uid} {len(data) // 1024 + (len(data) % 1024 > 0)} ".encode() + data)
        await writer.drain()

    await asyncio.sleep(0.1)

    writer.write(f"end file {uid}\n".encode())
    await writer.drain()

    f.close()

def get_correlation_table(tickers, start_date, end_date, filename):
    """
    Получить таблицу корреляции для заданных тикеров в указанный период и сохранить в CSV.

    :param tickers: список тикеров акций
    :param start_date: начальная дата в формате 'YYYY-MM-DD'
    :param end_date: конечная дата в формате 'YYYY-MM-DD'
    :param filename: имя файла для сохранения
    :return: таблица корреляции в формате DataFrame
    """
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    correlation_table = data.corr()
    correlation_table.to_csv(filename)
    return correlation_table

def plot_correlation_table(correlation_table, filename):
    """
    Визуализация таблицы корреляции и сохранение в файл JPG.

    :param correlation_table: таблица корреляции в формате DataFrame
    :param filename: имя файла для сохранения
    """
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_table, annot=True, cmap='coolwarm', linewidths=0.5)
    plt.title('Correlation Table')
    plt.savefig(filename, format='jpg')
    plt.close()

def get_stock_returns(ticker, start_date, end_date, filename):
    """
    Получить исторические данные о доходности акций и сохранить в CSV.

    :param ticker: тикер акции
    :param start_date: начальная дата в формате 'YYYY-MM-DD'
    :param end_date: конечная дата в формате 'YYYY-MM-DD'
    :param filename: имя файла для сохранения
    :return: данные о доходности акций в формате DataFrame
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    data['Returns'] = data['Adj Close'].pct_change()
    data[['Returns']].to_csv(filename)
    return data[['Returns']]

def plot_stock_returns(returns, ticker, filename):
    """
    Визуализация доходности акций и сохранение в файл JPG.

    :param returns: данные о доходности акций в формате DataFrame
    :param ticker: тикер акции
    :param filename: имя файла для сохранения
    """
    plt.figure(figsize=(10, 6))
    returns['Returns'].plot()
    plt.title(f'{ticker} Stock Returns')
    plt.xlabel('Date')
    plt.ylabel('Returns')
    plt.savefig(filename, format='jpg')
    plt.close()

def get_dividends(ticker, start_date, end_date, filename):
    """
    Получить данные о дивидендах акций и сохранить в CSV.

    :param ticker: тикер акции
    :param start_date: начальная дата в формате 'YYYY-MM-DD'
    :param end_date: конечная дата в формате 'YYYY-MM-DD'
    :param filename: имя файла для сохранения
    :return: данные о дивидендах в формате DataFrame
    """
    stock = yf.Ticker(ticker)
    dividends = stock.dividends[start_date:end_date]
    dividends.to_csv(filename)
    return dividends

def plot_dividends(dividends, ticker, filename):
    """
    Визуализация данных о дивидендах и сохранение в файл JPG.

    :param dividends: данные о дивидендах в формате DataFrame
    :param ticker: тикер акции
    :param filename: имя файла для сохранения
    """
    plt.figure(figsize=(10, 6))
    dividends.plot(kind='bar')
    plt.title(f'{ticker} Dividends')
    plt.xlabel('Date')
    plt.ylabel('Dividend')
    plt.savefig(filename, format='jpg')
    plt.close()

def get_financials(ticker, filename):
    """
    Получить финансовые отчеты компании и сохранить в CSV.

    :param ticker: тикер акции
    :param filename: имя файла для сохранения
    :return: финансовые отчеты в формате DataFrame
    """
    stock = yf.Ticker(ticker)
    financials = stock.financials
    financials.to_csv(filename)
    return financials

def get_balance_sheet(ticker, filename):
    """
    Получить балансовый отчет компании и сохранить в CSV.

    :param ticker: тикер акции
    :param filename: имя файла для сохранения
    :return: балансовый отчет в формате DataFrame
    """
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet
    balance_sheet.to_csv(filename)
    return balance_sheet

def get_cash_flow(ticker, filename):
    """
    Получить данные о движении денежных средств компании и сохранить в CSV.

    :param ticker: тикер акции
    :param filename: имя файла для сохранения
    :return: отчет о движении денежных средств в формате DataFrame
    """
    stock = yf.Ticker(ticker)
    cash_flow = stock.cashflow
    cash_flow.to_csv(filename)
    return cash_flow

def get_recommendations(ticker, filename):
    """
    Получить рекомендации аналитиков по акциям и сохранить в CSV.

    :param ticker: тикер акции
    :param filename: имя файла для сохранения
    :return: данные о рекомендациях в формате DataFrame
    """
    stock = yf.Ticker(ticker)
    recommendations = stock.recommendations
    recommendations.to_csv(filename)
    return recommendations

def get_major_holders(ticker, filename):
    """
    Получить данные о крупнейших держателях акций и сохранить в CSV.

    :param ticker: тикер акции
    :param filename: имя файла для сохранения
    :return: данные о крупнейших держателях в формате DataFrame
    """
    stock = yf.Ticker(ticker)
    major_holders = stock.major_holders
    major_holders.to_csv(filename)
    return major_holders

def get_institutional_holders(ticker, filename):
    """
    Получить данные о институциональных держателях акций и сохранить в CSV.

    :param ticker: тикер акции
    :param filename: имя файла для сохранения
    :return: данные о институциональных держателях в формате DataFrame
    """
    stock = yf.Ticker(ticker)
    institutional_holders = stock.institutional_holders
    institutional_holders.to_csv(filename)
    return institutional_holders

def plot_stock_prices(ticker, start_date, end_date, filename):
    """
    Визуализация цен акций и сохранение в файл JPG.

    :param ticker: тикер акции
    :param start_date: начальная дата в формате 'YYYY-MM-DD'
    :param end_date: конечная дата в формате 'YYYY-MM-DD'
    :param filename: имя файла для сохранения
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    plt.figure(figsize=(10, 6))
    plt.plot(data['Adj Close'])
    plt.title(f'{ticker} Stock Prices')
    plt.xlabel('Date')
    plt.ylabel('Adjusted Close Price')
    plt.savefig(filename, format='jpg')
    plt.close()

def predict_stock_price(ticker, start_date, end_date, forecast_days, filename):
    """
    Предсказать цены акций на основе линейной регрессии и сохранить график в JPG.

    :param ticker: тикер акции
    :param start_date: начальная дата в формате 'YYYY-MM-DD'
    :param end_date: конечная дата в формате 'YYYY-MM-DD'
    :param forecast_days: количество дней для предсказания
    :param filename: имя файла для сохранения
    :return: None
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    data['Date'] = data.index
    data['Date'] = pd.to_datetime(data['Date'])
    data['Date'] = data['Date'].map(pd.Timestamp.toordinal)

    X = data[['Date']]
    y = data['Adj Close']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    future_dates = pd.date_range(start=data.index[-1], periods=forecast_days+1, inclusive='right')
    future_dates_ordinal = future_dates.map(pd.Timestamp.toordinal).values.reshape(-1, 1)

    future_predictions = model.predict(future_dates_ordinal)

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Adj Close'], label='Historical Prices')
    plt.plot(future_dates, future_predictions, label='Predicted Prices', linestyle='--')
    plt.title(f'{ticker} Stock Price Prediction')
    plt.xlabel('Date')
    plt.ylabel('Adjusted Close Price')
    plt.legend()
    plt.savefig(filename, format='jpg')
    plt.close()

def get_earliest_date(ticker):
    """
    Получить самую раннюю доступную дату для указанного тикера.

    :param ticker: тикер акции
    :return: самая ранняя доступная дата в формате 'YYYY-MM-DD'
    """
    data = yf.download(ticker, start='1900-01-01')
    earliest_date = data.index.min()
    return earliest_date.strftime('%Y-%m-%d')

clients_names = set()
clients_pswd = dict()
clients_conns = dict()
clients_locales = dict()


def cut_login(register):
    name, pswd = '', ''

    for i in range(4, len(register)):
        if register[i:i+6] == '/pswd/':
            pswd = register[i+7:]
            break
        else:
            name += register[i]

    return name.strip(), pswd.strip()


async def chat(reader, writer):
    """
    Async chat with users.
    
    :param reader: inpurt stream from socket
    :param writer: output stream to socket
    """
    global clients_names, clients_conns, clients_locales, tree, root, full_name

    me = "{}:{}".format(*writer.get_extra_info('peername'))

    register = await reader.readline()
    register = register.decode()

    name, pswd = cut_login(register)

    while name in clients_names or not login(name, pswd):
        writer.write("off".encode())
        await writer.drain()

        register = await reader.readline()
        register = register.decode()

        name, pswd = cut_login(register)

    clients_names.add(name)
    clients_pswd[name] = pswd

    add_user(name, pswd, full_name)

    writer.write("in".encode())
    await writer.drain()

    clients_conns[name] = asyncio.Queue()

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients_conns[name].get())

    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)

        for q in done:
            if q is send:
                query = q.result().decode()
                query = query.replace(',', ' ')
                query = query.strip().split()


                if len(query) == 0:
                    writer.write("Command is incorrect.\n".encode())
                    continue

                print(query)
                update_stat(name, query[0])
                if query[0] == 'corr':
                    uid = query[1]
                    ticker = query[2:-2]
                    start_date = query[-2]
                    end_date = query[-1]
                    correlation_table = get_correlation_table(ticker, start_date, end_date, 'correlation_table.csv')
                    await send_file(writer, uid, 'correlation_table', '.csv')
                    plot_correlation_table(correlation_table, 'correlation_table.jpg')
                    await send_file(writer, uid, 'correlation_table', '.jpg')
                elif query[0] == 'stock':
                    uid = query[1]
                    ticker = query[2]
                    start_date = query[3]
                    end_date = query[4]
                    returns = get_stock_returns(ticker, start_date, end_date, 'aapl_returns.csv')
                    await send_file(writer, uid, 'aapl_returns', '.csv')
                    plot_stock_returns(returns, ticker, 'aapl_returns.jpg')
                    await send_file(writer, uid, 'aapl_returns', '.jpg')
                elif query[0] == 'dividends':
                    uid = query[1]
                    ticker = query[2]
                    start_date = query[3]
                    end_date = query[4]
                    dividends = get_dividends(ticker, start_date, end_date, 'aapl_dividends.csv')
                    await send_file(writer, uid, 'aapl_dividends', '.csv')
                    plot_dividends(dividends, ticker, 'aapl_dividends.jpg')
                    await send_file(writer, uid, 'aapl_dividends', '.jpg')
                elif query[0] == 'fin':
                    uid = query[1]
                    ticker = query[2]
                    get_financials(ticker, 'aapl_financials.csv')
                    await send_file(writer, uid, 'aapl_financials', '.csv')
                elif query[0] == 'balance':
                    uid = query[1]
                    ticker = query[2]
                    get_balance_sheet(ticker, 'aapl_balance_sheet.csv')
                    await send_file(writer, uid, 'aapl_balance_sheet', '.csv')
                elif query[0] == 'cash':
                    uid = query[1]
                    ticker = query[2]
                    get_cash_flow(ticker, 'aapl_cash_flow.csv')
                    await send_file(writer, uid, 'aapl_cash_flow', '.csv')
                elif query[0] == 'recom':
                    uid = query[1]
                    ticker = query[2]
                    get_recommendations(ticker, 'aapl_recommendations.csv')
                    await send_file(writer, uid, 'aapl_recommendations', '.csv')
                elif query[0] == 'm_hold':
                    uid = query[1]
                    ticker = query[2]
                    get_major_holders(ticker, 'aapl_major_holders.csv')
                    await send_file(writer, uid, 'aapl_major_holders', '.csv')
                elif query[0] == 'i_hold':
                    uid = query[1]
                    ticker = query[2]
                    get_institutional_holders(ticker, 'aapl_institutional_holders.csv')
                    await send_file(writer, uid, 'aapl_institutional_holders', '.csv')
                elif query[0] == 'graphics':
                    uid = query[1]
                    ticker = query[2]
                    start_date = query[3]
                    end_date = query[4]
                    plot_stock_prices(ticker, start_date, end_date, 'aapl_stock_prices.jpg')
                    await send_file(writer, uid, 'aapl_stock_prices', '.jpg')
                    #await send_file(writer, uid, "1.txt")
                elif query[0] == 'predict':
                    uid = query[1]
                    ticker = query[2]
                    start_date = query[3]
                    end_date = query[4]
                    forecast_days = int(query[5])
                    predict_stock_price(ticker, start_date, end_date, forecast_days, filename='aapl_price_prediction.jpg')
                    await send_file(writer, uid, 'aapl_price_prediction', '.jpg')
                elif query[0] == 'sayall':
                    for i in clients_names:
                        if i == name:
                            continue

                        await clients_conns[i].put('say ' + " ".join(query[1:]))
                elif query[0] == 'EOF':
                    send.cancel()
                    receive.cancel()
                    writer.close()

                    clients_names.remove(name)

                    return
                else:
                    print("skip")

                send = asyncio.create_task(reader.readline())
            elif q is receive:
                receive = asyncio.create_task(clients_conns[name].get())
                writer.write("{}\n".format(q.result()).encode())
                await writer.drain()

    print(f'{me} Done')

    send.cancel()
    receive.cancel()
    writer.close()

    clients_names.remove(name)


async def run_server():
    """Run async server."""
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()


def main():
    """Start server activity."""
    create_xml()
    asyncio.run(run_server())
