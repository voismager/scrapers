import json

from summa import summarizer, keywords

if __name__ == '__main__':
    with open('./text_io/sample_out.json') as in_f:
        articles = [(doc['content'], doc['url']) for doc in json.loads(in_f.read())]
        test_article = articles[0]
        print(test_article[1])
        merged_sections = ' '.join([section['text'] for section in test_article[0]])
        print(summarizer.summarize(merged_sections))

