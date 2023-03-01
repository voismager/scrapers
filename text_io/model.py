import dataclasses


@dataclasses.dataclass
class SectionContent:
    name: str
    text: str


@dataclasses.dataclass
class ArticleContent:
    url: str
    title: str
    location: str
    start_date: str
    end_date: str
    content: [SectionContent]