from .html_io import read_html
from .abstract_extractor import AbstractExtractor


class SerHtmlContentExtractor(AbstractExtractor):
    def __init__(self):
        self.base_url = 'https://www.ser-rrc.org/project-database/'

    def traverse_and_extract(self, start_page, last_page):
        page = start_page

        while last_page < 0 or page <= last_page:
            projects = read_html(f'{self.base_url}/page/{page}').find_all('div', class_='project')
            if len(projects) == 0:
                break
            else:
                print(f'Extracting {len(projects)} docs from page #{page}...')
                for i, project in enumerate(projects):
                    if (project_url_doc := project.find('a', href=True)) is not None:
                        doc = read_html(project_url_doc['href'])
                        yield doc.find(id="main")
                        print(f'Extracted {i + 1} of {len(projects)}')
                page += 1
