import requests

from text_io.wri_simple_extractor import WriSimpleExtractor
from text_io.grobid_tei_parser import parse_grobid

from aicacia_document_exporter.Document import Document
from aicacia_document_exporter.SimpleFileDocumentExporter import SimpleFileDocumentExporter


def download_and_return_path(doc_id, pdf_download_link):
    if pdf_download_link is not None:
        response = requests.get(pdf_download_link)

        if response.status_code == 200:
            path = f"./wri_files/{doc_id}.pdf"
            with open(path, "wb") as file:
                file.write(response.content)
            return path
        else:
            print(f"Failed to download PDF. Status code: {response.status_code}")
            return None
    else:
        return None


def run_extractor():
    extractor = WriSimpleExtractor()

    with SimpleFileDocumentExporter('./wri_files/metadata.db') as exporter:
        for doc in extractor.extract(start_page=0, page_limit=3):
            doc_title = doc['title']
            doc_url = doc['url']
            doc_doi = doc['doi']
            doc_authors = doc['authors']
            doc_downloadable_sources = doc['downloadable_sources']

            document = Document(
                title=doc_title,
                sections=[],
                source_link=doc_url,
                doi=doc_doi,
                authors=doc_authors,
                metadata={
                    'downloadable_sources': doc_downloadable_sources
                }
            )

            exporter.insert([document])


# def run_grobid_parser():
#     dir_path = './wri_files'
#
#     grobid_files = [f for f in os.listdir(dir_path) if f.endswith('.full.pdf.tei.xml')]
#
#     for grobid_file in grobid_files:
#         grobid_result = parse_grobid(f'{dir_path}/{grobid_file}')
#
#         doc_id = grobid_file[0:grobid_file.find('.')]
#
#         doc_refs = grobid_result['refs']
#         doc_raw_refs = grobid_result['raw_refs']
#         doc_contents = grobid_result['content']
#
#         for doc_ref in doc_refs:
#             ref_id = str(uuid.uuid4())
#             title = doc_ref['title']
#             doi = doc_ref['doi']
#             publisher = doc_ref['publisher']
#             published_date = doc_ref['published_date']
#             authors = doc_ref['authors']
#
#             cur.execute(
#                 'INSERT INTO refs (id, title, doi, publisher, published_date, authors, doc_id)'
#                 'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                 (ref_id, title, doi, publisher, published_date, ','.join(authors), doc_id)
#             )
#
#         con.commit()
#
#         for doc_ref in doc_raw_refs:
#             ref_id = str(uuid.uuid4())
#
#             cur.execute(
#                 'INSERT INTO raw_refs (id, text, doc_id)'
#                 'VALUES (?, ?, ?)',
#                 (ref_id, doc_ref, doc_id)
#             )
#
#         con.commit()
#
#         for doc_content in doc_contents:
#             content_id = str(uuid.uuid4())
#             doc_type = doc_content['type']
#             content = doc_content['content']
#
#             cur.execute(
#                 'INSERT INTO doc_contents (id, type, content, doc_id)'
#                 'VALUES (?, ?, ?, ?)',
#                 (content_id, doc_type, content, doc_id)
#             )
#
#         con.commit()


if __name__ == '__main__':
    run_extractor()
    # run_grobid_parser()
