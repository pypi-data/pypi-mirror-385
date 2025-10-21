import os
import re
from typing import List, Tuple
from enum import Enum
from fpdf import FPDF, HTMLMixin
from importlib.resources import files


class PDF(FPDF, HTMLMixin):
    def __init__(self, doc_title: str = "문서 제목"):
        super().__init__()
        self.doc_title = doc_title

        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(left=15, top=15, right=15)

        self.set_title(self.doc_title)
        self.set_author("windeath44")
        self.alias_nb_pages()

        font_dir = files("nadf").joinpath("fonts")
        regular = font_dir / "NotoSerifKR-Regular.ttf"
        bold = font_dir / "NotoSerifKR-Bold.ttf"

        self.family = "NotoSerifKR"
        self.add_font('NotoSerifKR', '', str(regular), uni=True)
        self.add_font('NotoSerifKR', 'B', str(bold), uni=True)


    # 상단 공통 헤더
    def header(self):
        self.set_font(self.family, "B", 14)
        # 페이지 폭 전체 셀, 가운데 정렬
        self.cell(0, 10, self.doc_title, border=0, ln=1, align="C")
        # 헤더-본문 간 간격
        self.ln(2)

    # 하단 공통 푸터(페이지 번호)
    def footer(self):
        self.set_y(-15)  # 바닥에서 15pt 위
        self.set_font(self.family, "", 9)
        self.cell(0, 10, f"{self.page_no()} / {{nb}}", 0, 0, "C")

    # 장/절 제목
    def chapter_title(self, title: str):
        self.set_font(self.family, "B", 12)
        self.cell(0, 9, title, 0, 1, "L")
        self.ln(1)

    # 본문
    def chapter_body(self, body):
        content = str(body)
        self.set_font(self.family, "", 11)
        # 긴 문단 줄바꿈/단어 단위 개행 처리
        content = str(body)
        content = re.sub(r"<br\s*/?>", "\n", content)
        content = re.sub(r"</p>", "\n", content)
        content = re.sub(r"<.*?>", "", content)

        self.multi_cell(0, 6, content)
        self.ln(1)

    def h2_title(self, title: str):
        self.set_font(self.family, "B", 14)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(2)

    def h3_title(self, title: str):
        self.set_font(self.family, "B", 12)
        self.cell(0, 8, f"  {title}", 0, 1, "L")  # 들여쓰기
        self.ln(1)

    def h4_title(self, title: str):
        self.set_font(self.family, "B", 10)
        self.cell(0, 7, f"    {title}", 0, 1, "L")  # 더 깊은 들여쓰기
        self.ln(1)

    class ReturnType(Enum):
        SAVE = "save"
        RETURN_OBJECT = "return_object"
        RETURN_BYTES = "return_bytes"

    async def create_pdf_from_namuwiki_list(self, namuwiki_list : List[Tuple[str, str, str]], output_path : str = None, return_type : ReturnType = ReturnType.SAVE):
        # 상대경로 안전 처리
        if return_type == self.ReturnType.SAVE:
            os.makedirs(output_path, exist_ok=True)
            output_path = os.path.abspath(output_path)
            safe_title = self.doc_title.replace("/", "_")  # 경로 안전 처리
            output_path = os.path.join(output_path, f"{safe_title}.pdf")

        self.add_page()
        for title, content, level in namuwiki_list:
            if level == 'h2':
                self.h2_title(title)
            elif level == 'h3':
                self.h3_title(title)
            elif level == 'h4':
                self.h4_title(title)
            else:
                self.chapter_title(title)  # 기본값
            self.chapter_body(content)

        if return_type == self.ReturnType.SAVE:
            self.output(output_path)
            return output_path
        elif return_type == self.ReturnType.RETURN_OBJECT:
            return self
        elif return_type == self.ReturnType.RETURN_BYTES:
            return self.output(dest="S")

