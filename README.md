# FinChecker
## Постановка задачи

Создание клиент-серверного приложения для удобного мониторинга акций разных компаний.

В список основных функций входит:

- Построение таблицы корреляций и ее визуализация;
- Получение данных о дохнодности акций и их визуализация;
- Получение финансовых отчетов компаний;
- Получение данных о дивидендах акций;
- Получение балансового отчета компании;
- Получение информации о движении денежных средств компаний;
- Получение рекомендаций аналитиков по акциям;
- Получение данных о крупнейший держателях акций;
- Получение данных об институциональных держателях акций;
- Предсказание цен на акции.


## Взаимодействие с приложением
Установить пакет в консоли:
```py
pip install FinChecker
```
Запуск сервера:
```py
start_server
```
Запуск клиента:
```py
start_client --language [-l] <chosen_locale> [en\ru]
```
### Работа приложения
Сервер работает автономно, не требуя никаких вмешательств извне. В конце своей работы выводит на экран общую статистику запросов.

После запуска клиента для подключения к серверу нужно залогиниться. После чего откроется следующее окно:
<img src="gui-example/gui-example1.png">

Верхнее поле служит для чата, нижнее поле - для ввода команд. Список поддерживаемых командЖ
```
    correlation table 	  - таблица корелляции на основе выбранных компаний;
    stock returns     	  - доходность акций компании;
    dividends         	  - данные о дивидендах акций;
    financials        	  - финансовый отчет компании;
    balance sheet     	  - балансовый отчет компании;
    cash flow         	  - информация движения денежных средств компании;
    recommendations   	  - рекомендация аналитиков по акции компании;
    major holders     	  - данные о крупнейший держателях акций;
    institutional holders - данные об институциональных держателях акций;
    graphics              - график цен акций;
    predict               - Предсказание цен на акции компании.
```
Для выбора команды нужно нажать кнопку `Submit` и в открывшемся окне ввести необходимые поля для работы команды:
<img src="gui-example/gui-example2.png">


## Необходимые инструменты
- yfinance - утилита для получения необработанных исторических финансовых данных;
- PyQt5 - GUI;
- Pandas, Mathplotlib/Seaborn - статистическая работа с данными, визуализация данных;
- scikit-learn - предсказание цен на акции;
- xml.etree - хранение данных.
