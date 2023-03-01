import csv
import re
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup

from model import ArticleContent, SectionContent


def is_blank(string):
    return not (string and string.strip())


class SerContentExtractor:
    def __init__(self):
        self.base_url = 'https://www.ser-rrc.org/project-database/'
        self.ignored_section_names = {'Funding', 'Contacts', 'Timeframe', 'Learn More'}

    def traverse_and_extract(self, page_limit=-1):
        page = 1

        while page_limit < 0 or page <= page_limit:
            projects = self.__read_html(f'{self.base_url}/page/{page}').find_all('div', class_='project')
            if len(projects) == 0:
                break
            else:
                print(f'Extracting {len(projects)} docs from page #{page}...')
                for i, project in enumerate(projects):
                    if (project_url_doc := project.find('a', href=True)) is not None:
                        yield self.__extract(project_url_doc['href'])
                        print(f'Extracted {i + 1} of {len(projects)}')
                page += 1

    def __extract(self, url) -> ArticleContent:
        doc = self.__read_html(url)

        title = self.__extract_title(doc)
        location = self.__extract_location(doc)
        start_date, end_date = self.__extract_dates(doc)
        text = self.__extract_text(doc)

        return ArticleContent(url, title, location, start_date, end_date, text)

    def __read_html(self, url) -> BeautifulSoup:
        with urlopen(Request(url, headers={'User-Agent': "Magic Browser"})) as resp:
            text = resp.read().decode("utf8")
            return BeautifulSoup(text, 'html.parser')

    def __extract_title(self, doc: BeautifulSoup):
        if (main_container := doc.find(id="main")) is not None:
            return main_container.find('h1').string
        else:
            return None

    def __extract_text(self, doc: BeautifulSoup):
        result = []

        # Check for overview
        if (overview_doc := doc.find(lambda tag: tag.name == 'div' and 'overview' in tag.attrs.get('class', []))) is not None:
            if (h2_doc := overview_doc.find('h2', string='Overview')) is not None:
                overview_text_docs = h2_doc.find_next_siblings()
                if len(overview_text_docs) != 0:
                    result.append(SectionContent('Overview', ''.join([doc.get_text() for doc in overview_text_docs])))

        # Check for other sections
        section_buttons = doc.find_all('button', class_='accordion')

        for section_button in section_buttons:
            section_name = section_button.string

            if section_name not in self.ignored_section_names:
                section: BeautifulSoup = section_button.find_next_sibling('div', class_='panel')
                result = result + self.__parse_section(section_name, section)

        return result

    def __parse_section(self, section_name, section_doc: BeautifulSoup):
        result = []

        def append(name, text):
            if not is_blank(text):
                result.append(SectionContent(name, text))

        current_name = section_name
        current_text = ''

        for element in section_doc:
            if element.name == 'h2':
                append(current_name, current_text)
                current_name = element.string
                current_text = ''
            else:
                current_text = current_text + element.get_text()

        append(current_name, current_text)
        return result

    def __extract_dates(self, doc: BeautifulSoup):
        timeframe_button = doc.find('button', string='Timeframe')

        if timeframe_button is not None:
            start_date = None
            start_date_doc = timeframe_button.find_next(self.__get_attr_predicate('Start Date:'))
            if start_date_doc is not None:
                start_date = start_date_doc.text.removeprefix('Start Date: ')

            end_date = None
            end_date_doc = timeframe_button.find_next(self.__get_attr_predicate('End Date:'))
            if end_date_doc is not None:
                end_date = end_date_doc.text.removeprefix('End Date: ')

            return start_date, end_date

        return None, None

    def __extract_location(self, doc: BeautifulSoup):
        quick_facts = doc.find('div', class_=['quick_facts'])

        if quick_facts is not None:
            if (location_doc := quick_facts.find(self.__get_attr_predicate('((c|C)ountry)|((t|T)erritory)'), recursive=False)) is not None:
                return location_doc.find('span').string

        return None

    def __get_attr_predicate(self, pattern):
        return lambda tag: \
            tag.name == 'p' and \
            tag.attrs.get('class') == ['singleattr'] and \
            tag.find('strong', string=re.compile(pattern)) is not None


class IteratorAsList(list):
    def __init__(self, it):
        super().__init__()
        self.it = it

    def __iter__(self):
        return self.it

    def __len__(self):
        return 1


if __name__ == '__main__':
    extractor = SerContentExtractor()

    articles = extractor.traverse_and_extract()

    with open('ser_projects_data.tsv', 'w', newline='') as out_f:
        writer = csv.writer(out_f, delimiter='\t')

        writer.writerow(['url', 'title', 'location', 'start_date', 'end_date', 'abstract'])

        for article in articles:
            text = ''.join([section.text for section in article.content]).replace('\t', '')
            writer.writerow([article.url, article.title, article.location, article.start_date, article.end_date, text])
