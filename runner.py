import csv
import time

from text_io.inecol_content_extractor import InecolContentExtractor

if __name__ == '__main__':
    extractor = InecolContentExtractor()

    with open('inecol_articles.tsv', 'w', newline='') as out_f:
        writer = csv.writer(out_f, delimiter='\t')

        writer.writerow([
            'url', 'article_issue_credentials',
            'title', 'doi',
            'abstract_text', 'abstract_html',
            'pdf', 'keywords'
        ])

        t1 = time.time()

        for article in extractor.extract():
            writer.writerow([
                article['url'],
                article['article_issue_credentials'],
                article['title'],
                article['doi'],
                article['abstract_text'],
                article['abstract_html'],
                article['pdf'],
                '|'.join(article['keywords'])
            ])

        t2 = time.time()

        print(f'Extraction took {t2 - t1}s to finish')