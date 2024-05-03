import asyncio
from playwright.async_api import async_playwright
import csv
import re


def read_search_queries(filename):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0] for row in reader]


class OzonParser:
    def __init__(self, keyword):
        self.keyword = keyword


    async def __page_down(self, page):
        """
            Функция для прокручивания страницы для загрузки всех карточек товаров 
        на странице
        
            Args:
                page: объект страницы, на которой нужно прокрутить страницу
        """
        await page.evaluate('''
            const scrollStep = 200;
            const scrollInterval = 100;
            const scrollHeight = document.documentElement.scrollHeight;
            let currentPosition = 0;
            const interval = setInterval(() => {
                window.scrollBy(0, scrollStep);
                currentPosition += scrollStep;
                if (currentPosition >= scrollHeight) {
                    clearInterval(interval);
                }
            }, scrollInterval);
        ''')
        await page.wait_for_timeout(5000)


    async def __get_product_price(self, page):
        """
            Получает цену продукта со страницы.

            Args:
                page: Объект страницы.

            Returns:
                str: Цена продукта, если найдена, иначе "Цена не найдена".
        """
        price_element = await page.query_selector('span.wl5.w3l')
        if not price_element:
            price_element = await page.query_selector('span.xl.lx0.x3l')
            if not price_element:
                price_element = await page.query_selector('span.xl.lx0.l4x')
                if not price_element:
                    price_element = await page.query_selector('span.tsHeadline500Medium')
        if price_element:
            price_text = await price_element.text_content()
            price = ''.join(filter(str.isdigit, price_text))
            return price
        return "Цена не найдена"
    

    async def __get_seller_name(self, page):
        """
                Получает имена продавцов (или одно имя), продающих товар
            и название товара на странице карточки товара

            Args:
                page: Объект страницы.

            Returns:
                str: Название товара
                tuple: Кортеж, содержащий имена продавцов 
        """
        await self.__page_down(page)
        try:
            product_name = await page.text_content('h1.l6x.tsHeadline550Medium')
            product_name = product_name.strip()
        except Exception as e:
            print(f"Ошибка: {e}")
            product_name = None
        seller_names = set()
        try:
            seller_name_elements = await page.query_selector_all('a.zj2')
            for element in seller_name_elements:
                seller_name = await element.text_content()
                seller_names.add(seller_name.strip())
        except Exception as e:
            print(f"Ошибка: {e}")
        return product_name, seller_names
    

    async def __check_black_friday_status(self, page):
        """
            Проверяет статус распордажи (black_friday в коде страницы) на странице товара.

            Args:
                page: Объект страницы.

            Returns:
                int: 1, если статус найден, иначе 0.
        """
        try:
            element = await page.query_selector('div.b9h.bi[data-widget="blackFridayStatus"]')
            if element:
                return 1
            else:
                return 0
        except Exception as e:
            print(f"Ошибка при проверке статуса распродажи: {e}")
            return 0


    def __get_product_code_from_url(self, url):
        """
            Упрощенное регулярное выражение для извлечения кода товара из URL.

            Args:
                url (str): URL, из которого нужно извлечь код товара.

            Returns:
                str: Код товара, если найден, иначе "Код не найден".
        """
        # Упрощенное регулярное выражение для извлечения кода товара из URL
        match = re.search(r'/product/[^/]+-(\d+)', url)
        if match:
            return match.group(1)  # Возвращаем найденный код товара
        return "Код не найден"


    async def __get_product_rating(self, page):
        """
            Получает рейтинг продукта и количество оценок со страницы.

            Args:
                page: Объект страницы.

            Returns:
                tuple: Кортеж, содержащий рейтинг продукта и количество оценок. Если элемент с рейтингом не найден, возвращает None.

        """ 
        rating_element = await page.query_selector('.ga10-a2.tsBodyControl500Medium')
        
        if rating_element:
            rating_text = await rating_element.inner_text()
            rating_parts = rating_text.split(' ')

            if len(rating_parts) >= 3:
                rating = rating_parts[0]
                num_ratings = rating_parts[2]
                return rating, num_ratings
            else:
                return None
        else:
            return None


    async def run(self, output_filename):
        """
            Запускает парсер OzonParser для сбора информации о товарах с сайта Ozon и сохраняет её в файл CSV.

            Args:
                output_filename (str): Имя файла для вывода данных в формате CSV.

            Returns:
                None

            Exception:
                Exception: В случае возникновения ошибки при записи данных в файл CSV.

            Desc:
                Метод `run` инициирует сессию браузера, переходит на главную страницу Ozon, выполняет поиск по заданному ключевому слову и перебирает страницы с результатами.
                Для каждого товара собирается информация о названии, продавцах, цене, рейтинге и статусе участия в распродаже.
                Собранная информация записывается в CSV файл, который включает колонки: название товара, продавцы, цена, URL с SKU, рейтинг, количество оценок, статус распродажи.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto('https://www.ozon.ru/')
            await page.fill('.yz3.tsBody500Medium', self.keyword)
            await page.keyboard.press('Enter')
            await page.wait_for_selector('div[data-widget="searchResultsV2"]', timeout=10000)

            products = []
            processed_urls = set()

            for page_number in range(1, 61):
                current_url = f"{page.url.split('&page=')[0]}&page={page_number}"
                if current_url in processed_urls:
                    continue
                processed_urls.add(current_url)

                await page.goto(current_url, wait_until='networkidle')
                await self.__page_down(page)

                links = await page.query_selector_all('a[href*="/product/"]')
                for link in links:
                    href = await link.get_attribute('href')
                    product_url = f'https://www.ozon.ru{href}'
                    if product_url not in processed_urls:
                        processed_urls.add(product_url)
                        product_page = await context.new_page()
                        try:
                            await product_page.goto(product_url, wait_until='load')
                        except Exception as e:
                            print(f"Page error! Could not navigate to {product_url}. Error: {e}")
                            await product_page.close()
                            continue

                        product_code = self.__get_product_code_from_url(product_page.url)
                        product_name, seller_names = await self.__get_seller_name(product_page)
                        product_price = await self.__get_product_price(product_page)
                        product_url_with_sku = f"https://www.ozon.ru/product/{product_code}"
                        product_rating_info = await self.__get_product_rating(product_page)
                        if product_rating_info:
                            product_rating, product_rating_number = product_rating_info
                        else:
                            product_rating, product_rating_number = None, None
                        black_friday = await self.__check_black_friday_status(product_page)

                        print(f"Название товара: {product_name}")
                        print(f"Имена продавцов: {seller_names}")
                        print(f"Цена товара: {product_price}")
                        print(f"Рейтинг товара: {product_rating}")
                        print(f"URL, SKU: {product_url_with_sku}")
                        print(f"Количество отзывов: {product_rating_number}")
                        print(f"Статус распродажи: {black_friday}")
                        products.append((product_name, ', '.join(seller_names), product_price, product_url_with_sku, product_rating, product_rating_number, black_friday))
                        await product_page.close()
            #print(products)
            try:
                with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['product_name', 'sellers', 'price', 'url', 'rating', 'num_ratings',"black_friday"])
                    writer.writerows(products)
            except Exception as e:
                print(f"An error occurred while writing to CSV: {e}")

            await browser.close()


async def main():
    search_queries = read_search_queries("search_queries.csv")
    for query in search_queries:
        parser = OzonParser(query)
        output_filename = f"results_{query}.csv"
        await parser.run(output_filename)


if __name__ == '__main__':
    asyncio.run(main())

