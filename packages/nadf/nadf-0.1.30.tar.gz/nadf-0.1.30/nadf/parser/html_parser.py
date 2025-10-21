from typing import List, Tuple
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

class HtmlParser:
    def __init__(self, html: BeautifulSoup, url: str):
        self.soup = html
        self.url = url

    async def extract_small_topics(self) -> List[Tuple[str, str, str]]:  # 레벨 추가
        small_topics = self.soup.find_all(['h2', 'h3', 'h4'])
        small_topics_list = []


        for topic in small_topics:
            level = topic.name  # 'h2', 'h3', 'h4'
            span = topic.find('span')
            small_topics_title = span.get_text().replace("[편집]", "")

            if (link := span.find('a')):
                small_topic = (small_topics_title, link.get("href"), level)
                small_topics_list.append(small_topic)
        return small_topics_list

    async def extract_content(self) -> List[str]:
        """
        콘텐츠 추출 - 구조 기반 접근 (동적 클래스명 대응)
        """
        import re
        
        # 전략 1: h2/h3/h4 헤딩의 부모 다음 형제에서 콘텐츠 추출
        headings = self.soup.find_all(['h2', 'h3', 'h4'])
        result = []
        
        for heading in headings:
            content_text = ""
            
            # h2의 부모 (div)의 다음 형제를 찾음
            if heading.parent:
                next_sibling = heading.parent.find_next_sibling()
                if next_sibling and next_sibling.name == 'div':
                    # 다음 div에서 텍스트 추출
                    content_text = next_sibling.get_text(separator=" ", strip=True)
            
            # 텍스트가 없으면 대안: 8자 해시 클래스명 패턴 매칭
            if not content_text or len(content_text) < 20:
                # 헤딩 다음의 div들에서 해시 클래스를 가진 것 찾기
                for sibling in heading.find_next_siblings(limit=5):
                    if sibling.name == 'div':
                        classes = sibling.get('class', [])
                        # 8-10자 길이의 영숫자 클래스 패턴 (나무위키 해시)
                        has_hash_class = any(
                            re.match(r'^[a-zA-Z0-9_\-+]{7,12}$', cls) 
                            for cls in classes
                        )
                        if has_hash_class:
                            text = sibling.get_text(separator=" ", strip=True)
                            if len(text) > 20:
                                content_text = text
                                break
            
            result.append(content_text)
        
        return result
