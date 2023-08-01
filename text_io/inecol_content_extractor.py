from .abstract_extractor import AbstractExtractor
from .html_io import read_html


def is_doc_not_blank(doc):
    return doc is not None and len(doc.get_text().strip()) > 0


class InecolContentExtractor(AbstractExtractor):
    def __init__(self):
        self.base_url = 'https://myb.ojs.inecol.mx/index.php/myb/issue/'
        self.available_item_ids = [
            82, 83, 84, 85, 86,
            212, 225, 226, 228, 227, 229, 230,
            232, 231, 233, 234, 235, 236, 240,
            241, 242, 244, 243, 245, 246, 247,
            248, 249
        ]

    def __extract(self, url) -> dict:
        doc = read_html(url)

        # Issue credentials
        article_issue_credentials_container = doc.find(class_='article_issue_credentials')
        if is_doc_not_blank(article_issue_credentials_container):
            article_issue_credentials = article_issue_credentials_container.get_text().strip()
        else:
            print(f'{url}: issue is missing')
            article_issue_credentials = None

        # Title
        title_container = doc.find(class_='article-full-title')
        if is_doc_not_blank(title_container):
            title = title_container.text.strip()
        else:
            print(f'{url}: title is missing')
            title = None

        # DOI
        if (doi_container := doc.find(class_='doi_value')) is not None:
            doi = doi_container.find('a', href=True)['href']
        else:
            print(f'{url}: DOI is missing')
            doi = None

        # Abstract
        if (abstract_container := doc.find(class_='abstract')) is not None:
            abstract_text = '\n'.join([doc.get_text() for doc in abstract_container]).strip()
            abstract_html = str(abstract_container)
        else:
            print(f'{url}: Abstract is missing')
            abstract_text = None
            abstract_html = None

        # Pdf
        if (pdf_container := doc.find('a', class_='pdf', href=True)) is not None:
            pdf = pdf_container['href']
        else:
            print(f'{url}: PDF is missing')
            pdf = None

        # Keywords
        keyword_containers = doc.find_all('li', class_='keyword_item')
        keywords = [keyword_container.find_next('span').get_text().strip() for keyword_container in keyword_containers]
        if len(keywords) == 0:
            print(f'{url}: keywords are missing')

        return {
            'url': url,
            'article_issue_credentials': article_issue_credentials,
            'title': title,
            'doi': doi,
            'abstract_text': abstract_text,
            'abstract_html': abstract_html,
            'pdf': pdf,
            'keywords': keywords
        }

    def traverse_and_extract(self, start_page, last_page):
        index = start_page

        while (last_page < 0 or index <= last_page) and len(self.available_item_ids) > index:
            item_id = self.available_item_ids[index]

            articles = read_html(f'{self.base_url}/view/{item_id}').find_all('article', class_='article_summary')

            print(f'Extracting {len(articles)} articles from item #{item_id}...')

            for i, article in enumerate(articles):
                if (article_url_doc := article.find('a', href=True)) is not None:
                    yield self.__extract(article_url_doc['href'])
                    print(f'Extracted {i + 1} of {len(articles)}')

            index += 1
