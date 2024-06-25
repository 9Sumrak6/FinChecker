import asyncio
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


async def send_file(writer, uid, file):
    writer.write(f"beg file {uid}\n".encode())
    await writer.drain()

    f = open(file, "rb")
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

clients_names = set()
clients_conns = dict()
clients_locales = dict()


async def chat(reader, writer):
    global clients_names, clients_conns, clients_locales

    me = "{}:{}".format(*writer.get_extra_info('peername'))

    name = await reader.readline()
    name = name.decode()[:-1]

    while name in clients_names:
        writer.write("off".encode())
        await writer.drain()

        name = await reader.readline()
        name = name.decode()[:-1]

    clients_names.add(name)

    writer.write("in".encode())
    await writer.drain()

    clients_conns[name] = asyncio.Queue()

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients_conns[name].get())

    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)

        for q in done:
            if q is send:
                query = q.result().decode().strip().split()
                print(query)

                if len(query) == 0:
                    writer.write("Command is incorrect.\n".encode())
                    continue
                elif query[0] == 'corr':
                    uid = query[1]
                    ticker = query[2]
                    start_date = query[3]
                    end_date = query[4]
                    correlation_table = get_correlation_table(ticker, start_date, end_date, 'correlation_table.csv')
                    send_file(writer, uid, 'correlation_table.csv')
                    plot_correlation_table(correlation_table, 'correlation_table.jpg')
                    send_file(writer, uid, 'correlation_table.jpg')
                elif query[0] == 'stock':
                    uid = query[1]
                    ticker = query[2]
                    start_date = query[3]
                    end_date = query[4]
                    returns = get_stock_returns(ticker, start_date, end_date, 'aapl_returns.csv')
                    send_file(writer, uid, 'aapl_returns.csv')
                    plot_stock_returns(returns, ticker, 'aapl_returns.jpg')
                    send_file(writer, uid, 'aapl_returns.jpg')
                elif query[0] == 'dividends':
                    uid = query[1]
                    ticker = query[2]
                    start_date = query[3]
                    end_date = query[4]
                    dividends = get_dividends(ticker, start_date, end_date, 'aapl_dividends.csv')
                    send_file(writer, uid, 'aapl_dividends.csv')
                    plot_dividends(dividends, ticker, 'aapl_dividends.jpg')
                    send_file(writer, uid, 'aapl_dividends.jpg')
                elif query[0] == 'fin':
                    uid = query[1]
                    ticker = query[2]
                    get_financials(ticker, 'aapl_financials.csv')
                    send_file(writer, uid, 'aapl_financials.csv')
                elif query[0] == 'balance':
                    uid = query[1]
                    ticker = query[2]
                    get_balance_sheet(ticker, 'aapl_balance_sheet.csv')
                    send_file(writer, uid, 'aapl_balance_sheet.csv')
                elif query[0] == 'cash':
                    uid = query[1]
                    ticker = query[2]
                    get_cash_flow(ticker, 'aapl_cash_flow.csv')
                    send_file(writer, uid, 'aapl_cash_flow.csv')
                elif query[0] == 'recom':
                    uid = query[1]
                    ticker = query[2]
                    get_recommendations(ticker, 'aapl_recommendations.csv')
                    send_file(writer, uid, 'aapl_recommendations.csv')
                # elif query[0] == 'sust':
                #     uid = query[1]
                #     ticker = query[2]
                #     pass
                elif query[0] == 'm_hold':
                    uid = query[1]
                    ticker = query[2]
                    get_major_holders(ticker, 'aapl_major_holders.csv')
                    send_file(writer, uid, 'aapl_major_holders.csv')
                elif query[0] == 'i_hold':
                    uid = query[1]
                    ticker = query[2]
                    get_institutional_holders(ticker, 'aapl_institutional_holders.csv')
                    send_file(writer, uid, 'aapl_institutional_holders.csv')
                elif query[0] == 'graphics':
                    uid = query[1]
                    await send_file(writer, uid, "1.txt")
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
	asyncio.run(run_server())