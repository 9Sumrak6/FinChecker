import unittest
import pandas as pd


from finchecker.server import get_correlation_table, plot_correlation_table, get_stock_returns, \
    plot_stock_returns, cut_login

class TestServer(unittest.TestCase):
    """Test server."""

    def compare_jpg_files(self, file1, file2):
        """
        Сравнивает два изображения в формате JPG побайтово.

        :param file1: Путь к первому изображению.
        :param file2: Путь ко второму изображению.
        :return: True, если изображения идентичны, иначе False.
        """
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            content1 = f1.read()
            content2 = f2.read()

            return content1 == content2

    def test_0_test_server(self):
        """Zero test."""
        # Генерация файла corr_table_create.csv    Amazon, Caterpillar Inc., Ameren, Airbnb
        get_correlation_table(["AMZN", "CAT", "AEE", "ABNB"], "2020-01-01", "2022-01-01", "correlation_table.csv")

        # Чтение файлов model.csv и corr_table_create.csv
        model_df = pd.read_csv('tests_files/correlation_table_model.csv')
        created_df = pd.read_csv('correlation_table.csv')

        # Округление значений до 5 знаков после запятой
        model_df = model_df.round(5)
        created_df = created_df.round(5)

        # Сравнение содержимого файлов
        self.assertEqual(model_df.to_csv(index=False), created_df.to_csv(index=False), "CSV файлы не совпадают")
    
    def test_1_test_server(self):
        """First test."""
        # Генерация файла correlation_table.jpg
        correlation_table = get_correlation_table(["AMZN", "CAT", "AEE", "ABNB"], "2020-01-01", "2022-01-01", 'correlation_table.csv')
        plot_correlation_table(correlation_table, 'correlation_table.jpg')

        # Запись имён сравниваемых файлов
        file1 = 'tests_files/correlation_table_model.jpg'
        file2 = 'correlation_table.jpg'

        # Сравнение содержимого файлов
        self.assertTrue(self.compare_jpg_files(file1, file2), "JPG файлы не совпадают")

    def test_2_test_server(self):
        """Second test."""
        # Генерация файла aapl_returns.jpg
        returns = get_stock_returns("AMZN", "2018-12-12", "2022-02-02", 'aapl_returns.csv')
        plot_stock_returns(returns, "AMZN", 'aapl_returns.jpg')

        # Запись имён сравниваемых файлов
        file1 = 'tests_files/aapl_returns_model.jpg'
        file2 = 'aapl_returns.jpg'

        # Сравнение содержимого файлов
        self.assertTrue(self.compare_jpg_files(file1, file2), "JPG файлы не совпадают")

    def test_3_test_server(self):
        """Third test."""
        self.assertTrue(cut_login("usr my_name /pswd/ my_password"), ('my_name', 'my_password'))

    def test_4_test_server(self):
        """Third test."""
        self.assertTrue(cut_login("usr my name /pswd/ my password"), ('my name', 'my password'))