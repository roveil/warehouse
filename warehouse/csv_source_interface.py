from csv import DictReader
from typing import Iterator, Iterable, Tuple


class CSVSyncInterface:

    def __init__(self, csv_content: Iterable[str], pk_header: str, name_header: str, photo_url_header: str,
                 bar_code_header: str, price_header: str, producer_header: str) -> None:
        """
        :param csv_content: Итератор возвращаюший строки
        :param pk_header: Заголовок csv-файла содержащий первичный ключ
        :param name_header: Заголовок csv-файла содержащий имя
        :param photo_url_header: Заголовок csv-файла содержащий url фотографии продукта
        :param bar_code_header: Заголовок csv-файла содержащий bar_code
        :param price_header: Заголовок csv-файла содержащий стоимость
        :param producer_header: Заголовок csv-файла содержащий изготовителя
        """
        self.reader = DictReader(csv_content)
        self.db_field_header = {
            'name': name_header,
            'photo_url': photo_url_header,
            'bar_code': bar_code_header,
            'price': price_header
        }
        self.pk_header = pk_header
        self.producer_header = producer_header

    def get_products(self) -> Iterator[Tuple[str, dict, str]]:
        """
        Возвращает генератор из таплов для более удобной работы с данными 
        :return: генератор из таплов (первичный ключ продукта, словарь с информацией о продукте, имя производителя)
        """
        for row in self.reader:
            yield row[self.pk_header], {db_field: row[header] for db_field, header in self.db_field_header.items()}, \
                  row[self.producer_header]
