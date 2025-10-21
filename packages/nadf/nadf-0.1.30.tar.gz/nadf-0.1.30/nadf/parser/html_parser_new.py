# """
# 개선된 HTML 파서 - 동적 클래스명 대신 구조 기반 파싱
# """
# from typing import List, Tuple
# from urllib.parse import unquote, urlparse
#
# from bs4 import BeautifulSoup, Tag
#
#
# class HtmlParser:
#     def __init__(self, html: BeautifulSoup, url: str):
#         self.soup = html
#         self.url = url
#
#     async def extract_small_topics(self) -> List[Tuple[str, str, str]]:
#         """제목 추출 (기존과 동일)"""
#         small_topics = self.soup.find_all(['h2', 'h3', 'h4'])
#         small_topics_list = []
#
#         for topic in small_topics:
#             level = topic.name  # 'h2', 'h3', 'h4'
#             span = topic.find('span')
#             if not span:
#                 continue
#
#             small_topics_title = span.get_text().replace("[편집]", "")
#
#             if (link := span.find('a')):
#                 small_topic = (small_topics_title, link.get("href"), level)
#                 small_topics_list.append(small_topic)
#         return small_topics_list
#
#     async def extract_content(self) -> List[str]:
#         """
#         구조 기반 콘텐츠 추출
#         각 h2/h3/h4 헤딩 다음의 콘텐츠를 추출 (다음 헤딩 전까지)
#         """
#         headings = self.soup.find_all(['h2', 'h3', 'h4'])
#         result = []
#
#         for heading in headings:
#             content_parts = []
#
#             # 현재 헤딩 다음의 모든 형제 요소를 순회
#             for sibling in heading.find_next_siblings():
#                 # 다음 헤딩을 만나면 중단
#                 if sibling.name in ['h2', 'h3', 'h4']:
#                     break
#
#                 # div나 p 태그에서 텍스트 추출
#                 if sibling.name in ['div', 'p', 'section']:
#                     text = sibling.get_text(separator=" ", strip=True)
#                     if text and len(text) > 10:  # 의미있는 텍스트만
#                         content_parts.append(text)
#
#             # 모든 텍스트를 합침
#             if content_parts:
#                 combined_text = " ".join(content_parts)
#                 result.append(combined_text)
#             else:
#                 # 콘텐츠가 없으면 빈 문자열
#                 result.append("")
#
#         return result
#
#     async def extract_content_alternative(self) -> List[str]:
#         """
#         대안: 클래스명 패턴 매칭
#         나무위키의 동적 클래스명이 특정 패턴을 따르는 경우
#         """
#         # 방법 1: 클래스명 길이가 8자인 div 찾기 (해시 패턴)
#         import re
#
#         all_divs = self.soup.find_all('div', class_=True)
#         content_divs = []
#
#         for div in all_divs:
#             classes = div.get('class', [])
#             # 8자 길이의 알파벳+숫자 클래스를 가진 div
#             for cls in classes:
#                 if re.match(r'^[a-zA-Z0-9_\-]{8}$', cls):
#                     text = div.get_text(separator=" ", strip=True)
#                     if len(text) > 50:  # 충분한 길이의 콘텐츠
#                         content_divs.append(div)
#                         break
#
#         result = []
#         for div in content_divs:
#             text = div.get_text(separator=" ", strip=True)
#             result.append(text)
#
#         return result
#
#     async def extract_content_by_wiki_class_prefix(self) -> List[str]:
#         """
#         대안 2: 'wiki'로 시작하는 클래스 찾기
#         """
#         divs = self.soup.find_all('div', class_=lambda x: x and any('wiki' in cls.lower() for cls in x))
#
#         result = []
#         for div in divs:
#             text = div.get_text(separator=" ", strip=True)
#             if len(text) > 50:  # 의미있는 콘텐츠만
#                 result.append(text)
#
#         return result