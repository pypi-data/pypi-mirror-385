"""
책 표지 생성기 (Book Cover Maker)

이 모듈은 사용자가 지정한 텍스트와 폰트를 사용하여 책 표지를 생성하는 도구입니다.
Typer CLI 프레임워크를 사용하여 명령줄 인터페이스를 제공합니다.
"""

import importlib.resources
import random
import site
from pathlib import Path
from typing import Optional, Tuple

import typer
from PIL import Image, ImageDraw, ImageFont

# Typer 앱 인스턴스 생성
app = typer.Typer(
    name="book-cover-maker",
    help="책 표지를 생성하는 도구입니다.",
    add_completion=False,
)


class FontManager:
    """폰트 관리 클래스"""
    
    def __init__(self):
        self.fonts_dir = self._get_fonts_directory()
    
    def _get_fonts_directory(self) -> Path:
        """
        폰트 디렉토리 경로를 반환합니다.
        
        검색 순서:
        1) 패키지 루트 (개발 환경)
        2) site-packages 루트 (설치된 환경)
        3) 현재 작업 디렉토리
        
        Returns:
            Path: 폰트 디렉토리 경로
        """
        # 1) 패키지 루트 (프로젝트 레이아웃 또는 wheel이 site-packages에 추출된 경우)
        pkg_root = Path(__file__).parent.parent.parent
        candidate = pkg_root / "fonts"
        if candidate.exists():
            return candidate

        # 2) site-packages 루트 (일부 설치 프로그램이 데이터를 site 루트에 배치할 수 있음)
        try:
            for sp in site.getsitepackages():
                sp_path = Path(sp) / "fonts"
                if sp_path.exists():
                    return sp_path
        except Exception:
            pass

        # 3) 현재 작업 디렉토리 폴백
        cwd_fonts = Path.cwd() / "fonts"
        if cwd_fonts.exists():
            return cwd_fonts

        # 기본값으로 pkg_root/fonts 반환 (없어도 load_font에서 폴백 처리)
        return candidate
    
    def load_font(self, font_path: Optional[str], size: int, fallback_paths: Optional[list] = None) -> ImageFont.FreeTypeFont:
        """
        폰트를 로드합니다. 폴백 옵션을 제공합니다.
        
        Args:
            font_path: 사용자 지정 폰트 경로
            size: 폰트 크기
            fallback_paths: 폴백 폰트 경로 목록
            
        Returns:
            ImageFont.FreeTypeFont: 로드된 폰트 객체
        """
        if font_path:
            try:
                return ImageFont.truetype(font_path, size)
            except IOError:
                typer.echo(f"경고: 사용자 지정 폰트를 찾을 수 없습니다: {font_path}, 폴백을 시도합니다...")

        if fallback_paths:
            for fallback_path in fallback_paths:
                try:
                    return ImageFont.truetype(fallback_path, size)
                except IOError:
                    continue

        typer.echo("경고: 모든 폰트 옵션이 실패했습니다. 기본 Pillow 폰트를 사용합니다.")
        return ImageFont.load_default()
    
    def get_fonts_by_language(self, language: str) -> Tuple[str, str, str]:
        """
        언어에 따라 적절한 폰트 경로를 반환합니다.
        
        Args:
            language: 언어 코드 ('kr', 'jp', 'en')
            
        Returns:
            Tuple[str, str, str]: (제목 폰트, 저자 폰트, 판본 폰트) 경로
        """
        if language == "kr":
            return (
                str(self.fonts_dir / "NotoSansKR-Bold.ttf"),
                str(self.fonts_dir / "NotoSansKR-Regular.ttf"),
                str(self.fonts_dir / "NotoSansKR-Regular.ttf"),
            )
        elif language == "jp":
            return (
                str(self.fonts_dir / "NotoSansJP-VF.ttf"),
                str(self.fonts_dir / "NotoSansJP-VF.ttf"),
                str(self.fonts_dir / "NotoSansJP-VF.ttf"),
            )
        elif language == "en":
            return (
                str(self.fonts_dir / "NotoSans-Bold.ttf"),
                str(self.fonts_dir / "NotoSans-Regular.ttf"),
                str(self.fonts_dir / "NotoSans-Regular.ttf"),
            )
        else:
            # 기본값으로 한국어 폰트 사용
            return (
                str(self.fonts_dir / "NotoSansKR-Bold.ttf"),
                str(self.fonts_dir / "NotoSansKR-Regular.ttf"),
                str(self.fonts_dir / "NotoSansKR-Regular.ttf"),
            )


class BackgroundManager:
    """배경 이미지 관리 클래스"""
    
    @staticmethod
    def get_package_resource_path(resource_name: str) -> Optional[str]:
        """
        패키지에 포함된 리소스 파일의 경로를 가져옵니다.
        
        Args:
            resource_name: 리소스 파일 이름
            
        Returns:
            str: 리소스 파일 경로 또는 None (찾을 수 없는 경우)
        """
        try:
            # importlib.resources를 사용하여 리소스 가져오기 시도
            if hasattr(importlib.resources, "files"):
                # Python 3.9+ 방식
                return str(importlib.resources.files("book_cover_maker") / resource_name)
            else:
                # Python 3.8 방식
                with importlib.resources.path("book_cover_maker", resource_name) as path:
                    return str(path)
        except (ModuleNotFoundError, FileNotFoundError, TypeError):
            # 폴백: 패키지 디렉토리에서 파일 찾기
            package_dir = Path(__file__).parent.parent.parent
            resource_path = package_dir / resource_name
            if resource_path.exists():
                return str(resource_path)
            return None
    
    @staticmethod
    def get_default_background_path() -> str:
        """
        기본 배경 이미지(cover_background.png)의 경로를 해결합니다.
        
        검색 순서:
        1) 프로젝트/패키지 루트 (개발 환경)
        2) site-packages 루트 (wheel이 루트에 강제 포함됨)
        3) 패키지 디렉토리 (패키지 디렉토리 내부에 번들된 경우)
        4) 현재 작업 디렉토리
        5) 더미 배경 생성으로 폴백
        
        Returns:
            str: 배경 이미지 경로
        """
        candidates = []
        pkg_root = Path(__file__).parent.parent.parent
        candidates.append(pkg_root / "cover_background.png")

        try:
            for sp in site.getsitepackages():
                candidates.append(Path(sp) / "cover_background.png")
        except Exception:
            pass

        # 파일이 패키지 디렉토리 내부에 배치된 경우
        candidates.append(Path(__file__).parent / "cover_background.png")

        # 현재 작업 디렉토리 폴백
        candidates.append(Path.cwd() / "cover_background.png")

        for path in candidates:
            if path.exists():
                return str(path)

        # 폴백: 더미 배경 생성
        typer.echo("경고: 패키지에서 cover_background.png를 찾을 수 없습니다. 더미 배경을 생성합니다...")
        return BackgroundManager.create_dummy_background(1000, 1500)
    
    @staticmethod
    def create_dummy_background(width: int, height: int, path: str = "dummy_background.jpg") -> str:
        """
        테스트용 더미 배경 이미지를 생성합니다.
        
        Args:
            width: 이미지 너비
            height: 이미지 높이
            path: 저장할 파일 경로
            
        Returns:
            str: 생성된 이미지 파일 경로
        """
        dummy_img = Image.new("RGB", (width, height), color="darkgrey")
        draw = ImageDraw.Draw(dummy_img)
        
        # 깊이감을 모방하는 간단한 그라데이션 추가
        for y in range(height):
            r = int(30 + (100 - 30) * y / height)
            g = int(40 + (120 - 40) * y / height)
            b = int(70 + (150 - 70) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 원본과 유사한 시각적 효과를 위한 "빛나는 점" 추가
        for _ in range(50):
            x = random.randint(0, width)
            y = random.randint(int(height * 0.5), height)
            radius = random.randint(1, 3)
            draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius), fill=(255, 150, 0)
            )  # 주황색 빛

        dummy_img.save(path)
        return path


class TextRenderer:
    """텍스트 렌더링 클래스"""
    
    @staticmethod
    def wrap_text(draw_context: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        """
        텍스트를 지정된 최대 너비에 맞게 줄바꿈합니다.
        
        공백 경계를 우선하지만, 긴/CJK 시퀀스의 경우 문자 단위로 폴백합니다.
        
        Args:
            draw_context: PIL ImageDraw 객체
            text: 줄바꿈할 텍스트
            font: 사용할 폰트
            max_width: 최대 너비
            
        Returns:
            list[str]: 줄바꿈된 텍스트 라인 목록
        """
        if not text:
            return [""]

        lines = []
        # 먼저 명시적 줄바꿈을 존중
        raw_lines = text.split("\n")

        for raw in raw_lines:
            words = raw.split()
            # 공백이 없는 경우 (예: CJK), 문자 기반 줄바꿈으로 폴백
            if len(words) == 0:
                current_line = ""
                for ch in raw:
                    test_line = current_line + ch
                    bbox = draw_context.textbbox((0, 0), test_line, font=font)
                    test_w = bbox[2] - bbox[0]
                    if test_w <= max_width or current_line == "":
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = ch
                if current_line:
                    lines.append(current_line)
                continue

            current_line = ""
            for word in words:
                # 단일 단어가 최대 너비보다 긴 경우, 문자로 분할
                bbox_word = draw_context.textbbox((0, 0), word, font=font)
                word_w = bbox_word[2] - bbox_word[0]
                if word_w > max_width:
                    # 먼저 current_line을 플러시
                    if current_line:
                        lines.append(current_line)
                        current_line = ""
                    piece = ""
                    for ch in word:
                        test_piece = piece + ch
                        bbox_piece = draw_context.textbbox((0, 0), test_piece, font=font)
                        piece_w = bbox_piece[2] - bbox_piece[0]
                        if piece_w <= max_width or piece == "":
                            piece = test_piece
                        else:
                            lines.append(piece)
                            piece = ch
                    if piece:
                        # 이 조각으로 새 줄을 시작하거나 현재 줄에 추가 (맞는 경우)
                        current_line = piece
                    continue

                tentative = word if current_line == "" else current_line + " " + word
                bbox = draw_context.textbbox((0, 0), tentative, font=font)
                tw = bbox[2] - bbox[0]
                if tw <= max_width:
                    current_line = tentative
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

        return lines


class BookCoverGenerator:
    """책 표지 생성기 메인 클래스"""
    
    def __init__(self):
        self.font_manager = FontManager()
        self.background_manager = BackgroundManager()
        self.text_renderer = TextRenderer()
    
    def create_book_cover(
        self,
        background_image_path: str,
        title: str,
        author: str,
        edition_label: str,
        output_path: str = "book_cover.png",
        title_font_path: Optional[str] = None,
        author_font_path: Optional[str] = None,
        edition_font_path: Optional[str] = None,
    ) -> None:
        """
        지정된 텍스트 요소로 책 표지 이미지를 생성합니다.
        
        Args:
            background_image_path: 배경 이미지 경로
            title: 책 제목
            author: 저자 이름
            edition_label: 판본 라벨 (예: "1ST EDITION")
            output_path: 생성된 책 표지를 저장할 경로
            title_font_path: 제목 폰트 파일 경로 (선택사항)
            author_font_path: 저자 폰트 파일 경로 (선택사항)
            edition_font_path: 판본 라벨 폰트 파일 경로 (선택사항)
        """
        try:
            img = Image.open(background_image_path).convert("RGB")
        except FileNotFoundError:
            typer.echo(f"오류: 배경 이미지를 찾을 수 없습니다: {background_image_path}")
            return

        draw = ImageDraw.Draw(img)
        width, height = img.size

        # 색상 정의
        white_color = (255, 255, 255)
        light_gray_color = (200, 200, 200)
        dark_blue_color = (30, 40, 70)  # 판본 라벨 박스용 근사값

        # 폰트 로드
        default_fonts = [
            str(self.font_manager.fonts_dir / "NotoSansJP-VF.ttf"),
            str(self.font_manager.fonts_dir / "NotoSansKR-Bold.ttf"),
            str(self.font_manager.fonts_dir / "NotoSans-Bold.ttf"),
        ]

        default_regular_fonts = [
            str(self.font_manager.fonts_dir / "NotoSansJP-VF.ttf"),
            str(self.font_manager.fonts_dir / "NotoSansKR-Regular.ttf"),
            str(self.font_manager.fonts_dir / "NotoSans-Regular.ttf"),
        ]

        title_font = self.font_manager.load_font(title_font_path, int(height * 0.045), default_fonts)
        author_font = self.font_manager.load_font(author_font_path, int(height * 0.025), default_regular_fonts)
        edition_font = self.font_manager.load_font(edition_font_path, int(height * 0.015), default_regular_fonts)

        # 판본 라벨 (우상단) 렌더링
        self._render_edition_label(draw, edition_label, edition_font, width, height, dark_blue_color, white_color)

        # 제목 (좌하단) 렌더링
        title_lines = self._render_title(draw, title, title_font, width, height, white_color, light_gray_color)

        # 저자 (제목 아래) 렌더링
        self._render_author(draw, author, author_font, width, height, light_gray_color, title_lines, title_font)

        img.save(output_path)
        typer.echo(f"책 표지가 저장되었습니다: {output_path}")

    def _render_edition_label(
        self, 
        draw: ImageDraw.Draw, 
        edition_label: str, 
        edition_font: ImageFont.FreeTypeFont,
        width: int, 
        height: int, 
        dark_blue_color: tuple, 
        white_color: tuple
    ) -> None:
        """판본 라벨을 렌더링합니다."""
        edition_padding_x = int(width * 0.03)
        edition_padding_y = int(height * 0.03)

        # 텍스트 크기 측정하여 배경 박스 생성
        edition_text_bbox = draw.textbbox((0, 0), edition_label, font=edition_font)
        edition_text_width = edition_text_bbox[2] - edition_text_bbox[0]
        edition_text_height = edition_text_bbox[3] - edition_text_bbox[1]

        edition_box_width = edition_text_width + int(width * 0.03)
        edition_box_height = edition_text_height + int(height * 0.01)

        edition_box_x1 = width - edition_box_width
        edition_box_y1 = 0
        edition_box_x2 = width
        edition_box_y2 = edition_box_height

        # 배경 사각형 그리기
        draw.rectangle(
            [(edition_box_x1, edition_box_y1), (edition_box_x2, edition_box_y2)],
            fill=dark_blue_color,
        )
        draw.text(
            (width - edition_padding_x - edition_text_width, edition_padding_y),
            edition_label,
            font=edition_font,
            fill=white_color,
        )

    def _render_title(
        self, 
        draw: ImageDraw.Draw, 
        title: str, 
        title_font: ImageFont.FreeTypeFont,
        width: int, 
        height: int, 
        white_color: tuple, 
        light_gray_color: tuple
    ) -> list[str]:
        """제목을 렌더링합니다."""
        # 제목 영역 너비 내에서 줄바꿈하면서 좌우 여백을 동일하게 유지
        title_start_x = int(width * 0.07)
        title_start_y = int(height * 0.75)

        # 제목 영역의 최대 너비 정의 (동일한 좌우 여백)
        title_area_max_width = width - (title_start_x * 2)

        title_lines = self.text_renderer.wrap_text(draw, title, title_font, title_area_max_width)

        for i, line in enumerate(title_lines):
            draw.text(
                (
                    title_start_x,
                    title_start_y + i * int(title_font.size * 1.2),
                ),  # 줄 간격
                line,
                font=title_font,
                fill=white_color,
            )

        # 제목 아래 수평선 그리기
        line_y = (
            title_start_y
            + (len(title_lines) * int(title_font.size * 1.2))
            + int(height * 0.01)
        )
        # 제목 영역의 왼쪽 여백과 일치하고 영역 내의 합리적인 길이로 선 그리기
        available_line_length = min(int(width * 0.5), width - title_start_x * 2)
        line_length = available_line_length
        draw.line(
            [(title_start_x, line_y), (title_start_x + line_length, line_y)],
            fill=light_gray_color,
            width=3,
        )
        
        return title_lines

    def _render_author(
        self, 
        draw: ImageDraw.Draw, 
        author: str, 
        author_font: ImageFont.FreeTypeFont,
        width: int, 
        height: int, 
        light_gray_color: tuple,
        title_lines: list,
        title_font: ImageFont.FreeTypeFont
    ) -> None:
        """저자를 렌더링합니다."""
        # 제목 선 아래에 저자 배치
        title_start_x = int(width * 0.07)
        title_start_y = int(height * 0.75)
        
        # 제목의 실제 높이 계산
        title_height = len(title_lines) * int(title_font.size * 1.2)
        line_y = title_start_y + title_height + int(height * 0.01)
        author_start_y = line_y + int(height * 0.02)
        
        draw.text(
            (title_start_x, author_start_y), author, font=author_font, fill=light_gray_color
        )


@app.command()
def generate(
    title: str = typer.Argument(..., help="책 제목"),
    author: str = typer.Argument(..., help="저자 이름"),
    edition: str = typer.Argument(..., help='판본 라벨 (예: "1ST EDITION")'),
    bg_image_path: Optional[str] = typer.Argument(None, help="배경 이미지 경로 (선택사항, 제공하지 않으면 포함된 기본값 사용)"),
    language: str = typer.Option("kr", "--lang", "-l", help="폰트 선택을 위한 언어 (기본값: kr)", show_default=True),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="생성된 책 표지의 출력 경로 (선택사항, 기본값: generated_book_cover_{lang}.png)"),
) -> None:
    """
    책 표지를 생성합니다.
    
    지정된 텍스트와 폰트를 사용하여 책 표지 이미지를 생성합니다.
    언어에 따라 적절한 폰트가 자동으로 선택됩니다.
    """
    # 배경 이미지 경로 결정
    if bg_image_path is None:
        bg_image_path = BackgroundManager.get_default_background_path()
        typer.echo(f"기본 배경 사용: {bg_image_path}")

    # 언어에 따라 적절한 폰트 가져오기
    font_manager = FontManager()
    title_font_path, author_font_path, edition_font_path = font_manager.get_fonts_by_language(language)

    # 출력 파일명 결정
    if output:
        output_filename = output
    else:
        output_filename = f"generated_book_cover_{language}.png"

    # 책 표지 생성기 인스턴스 생성 및 실행
    generator = BookCoverGenerator()
    generator.create_book_cover(
        background_image_path=bg_image_path,
        title=title,
        author=author,
        edition_label=edition,
        output_path=output_filename,
        title_font_path=title_font_path,
        author_font_path=author_font_path,
        edition_font_path=edition_font_path,
    )

    typer.echo("책 표지가 성공적으로 생성되었습니다!")
    typer.echo(f"언어: {language}")
    typer.echo(f"출력 파일: {output_filename}")


def main() -> None:
    """메인 진입점"""
    app()


if __name__ == "__main__":
    main()