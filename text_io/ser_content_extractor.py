import re

from bs4 import BeautifulSoup

from .abstract_extractor import AbstractExtractor
from .html_io import read_html
from .model import SectionContent


def is_blank(string):
    return not (string and string.strip())


class SerContentExtractor(AbstractExtractor):
    def __init__(self):
        self.base_url = 'https://www.ser-rrc.org/project-database/'
        self.ignored_section_names = {'Funding', 'Contacts', 'Timeframe', 'Learn More'}

    def __traverse_and_extract(self, start_page, last_page):
        page = start_page

        while last_page < 0 or page <= last_page:
            projects = read_html(f'{self.base_url}/page/{page}').find_all('div', class_='project')
            if len(projects) == 0:
                break
            else:
                print(f'Extracting {len(projects)} docs from page #{page}...')
                for i, project in enumerate(projects):
                    if (project_url_doc := project.find('a', href=True)) is not None:
                        yield self.__extract(project_url_doc['href'])
                        print(f'Extracted {i + 1} of {len(projects)}')
                page += 1

    def __extract(self, url) -> dict:
        doc = read_html(url)

        title = self.__extract_title(doc)
        location = self.__extract_location(doc)
        start_date, end_date = self.__extract_dates(doc)
        text = self.__extract_text(doc)

        return {
            'url': url,
            'title' : title,
            'location' : location,
            'start_date' : start_date,
            'end_date' : end_date,
            'text' : text
        }

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
