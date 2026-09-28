"""
TikZ → SVG 변환 훅 (MkDocs hooks 기능)

마크다운 안의 ```tikz 코드 블록을 빌드할 때 LaTeX로 컴파일해
SVG 그림으로 바꿔 넣는다.

동작 순서:
  1) 각 페이지의 마크다운에서 ```tikz 블록을 찾는다
  2) 블록 내용을 standalone 문서로 감싸 latex(DVI)로 컴파일한다
  3) dvisvgm으로 DVI → SVG 변환 (글자는 도형 경로로 변환되어 폰트 의존 없음)
  4) SVG를 이미지(data URI)로 페이지에 삽입한다
  5) 같은 코드는 .cache/tikz/에 저장해 다음 빌드에서 재사용한다

필요 프로그램: latex, dvisvgm (TeX Live / MacTeX에 포함)

블록 작성 규칙:
  - 여는 줄은 ```tikz 로 시작한다
  - '%preamble:'로 시작하는 줄은 해당 그림의 전처리부(preamble)로 옮겨진다
      예) %preamble: \\usetikzlibrary{decorations.pathmorphing}
  - '%alt:'로 시작하는 줄은 그림의 대체 텍스트(alt)가 된다
      예) %alt: 단위원과 각 theta
  - '%scale:'로 시작하는 줄은 화면 표시 배율이다 (기본값 DEFAULT_SCALE)
      예) %scale: 1.8   (작은 가환도표를 크게)
      ※ 그림 자체(비율·선 굵기 관계)는 바뀌지 않고 표시 크기만 바뀐다
  - 나머지는 문서 본문(tikzpicture, tikzcd 환경 등)으로 들어간다
"""

import base64
import hashlib
import html
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from mkdocs.exceptions import PluginError

# 모든 그림에 공통으로 들어가는 전처리부.
# 여기를 고치면 전체 그림의 기본 환경이 바뀐다 (캐시도 자동으로 갱신됨).
BASE_PREAMBLE = r"""
\usepackage{kotex}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{tikz}
\usepackage{tikz-cd}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{arrows.meta,calc,positioning,shapes,decorations.markings,angles,quotes,matrix,intersections,patterns}
"""

DOC_TEMPLATE = r"""\documentclass[tikz,border=2pt]{standalone}
%(base)s
%(extra)s
\begin{document}
%(body)s
\end{document}
"""

CACHE_DIR = Path(".cache/tikz")

# 화면 표시 배율 기본값. LaTeX는 인쇄용 크기(pt)로 그림을 만들기 때문에
# 웹 본문 글자 크기와 맞추려면 조금 키우는 편이 읽기 좋다.
DEFAULT_SCALE = 1.3
PT_TO_PX = 96 / 72

# ``` 또는 ~~~ 로 시작하는 코드 울타리(fence)를 인식
FENCE_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})(?P<info>.*)$")


def _check_tools():
    missing = [t for t in ("latex", "dvisvgm") if shutil.which(t) is None]
    if missing:
        raise PluginError(
            "TikZ 변환에 필요한 프로그램이 없습니다: " + ", ".join(missing)
            + "\n(로컬: MacTeX 설치 / GitHub Actions: deploy.yml의 TeX 설치 단계 확인)"
        )


def _compile(source: str, page_path: str) -> str:
    """TikZ 소스를 SVG 문자열로 변환한다 (캐시 사용)."""
    extra, body = [], []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("%preamble:"):
            extra.append(stripped[len("%preamble:"):].strip())
        elif stripped.startswith(("%alt:", "%scale:")):
            continue
        else:
            body.append(line)

    doc = DOC_TEMPLATE % {
        "base": BASE_PREAMBLE,
        "extra": "\n".join(extra),
        "body": "\n".join(body),
    }

    key = hashlib.sha256(doc.encode("utf-8")).hexdigest()[:20]
    cached = CACHE_DIR / f"{key}.svg"
    if cached.exists():
        return cached.read_text(encoding="utf-8")

    _check_tools()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "fig.tex").write_text(doc, encoding="utf-8")

        run = subprocess.run(
            ["latex", "-interaction=nonstopmode", "-halt-on-error", "fig.tex"],
            cwd=tmp, capture_output=True, text=True, errors="replace",
        )
        if run.returncode != 0:
            log = run.stdout
            # 로그에서 오류 부분('!'로 시작하는 줄 주변)만 뽑아 보여준다
            idx = log.find("\n!")
            snippet = log[idx: idx + 800] if idx != -1 else log[-800:]
            raise PluginError(
                f"[TikZ] {page_path} 의 그림 컴파일 실패:\n{snippet}"
            )

        conv = subprocess.run(
            ["dvisvgm", "--no-fonts", "--exact-bbox", "--precision=5",
             "-o", "fig.svg", "fig.dvi"],
            cwd=tmp, capture_output=True, text=True, errors="replace",
        )
        svg_path = tmp / "fig.svg"
        if conv.returncode != 0 or not svg_path.exists():
            raise PluginError(
                f"[TikZ] {page_path} 의 SVG 변환 실패:\n{conv.stderr[-800:]}"
            )
        svg = svg_path.read_text(encoding="utf-8")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached.write_text(svg, encoding="utf-8")
    return svg


def _to_html(svg: str, alt: str, scale: float, indent: str) -> str:
    data = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    alt_attr = html.escape(alt or "TikZ 그림", quote=True)
    size = ""
    m = re.search(r"width='([\d.]+)pt'", svg)
    if m:
        size = f' width="{round(float(m.group(1)) * PT_TO_PX * scale)}"'
    return (
        f'{indent}<figure class="tikz">'
        f'<img alt="{alt_attr}"{size} src="data:image/svg+xml;base64,{data}">'
        f"</figure>"
    )


def on_page_markdown(markdown, page, config, files):
    lines = markdown.split("\n")
    out = []
    i = 0
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue

        indent, fence, info = m.group("indent"), m.group("fence"), m.group("info").strip()
        # 같은 종류·길이 이상의 울타리로 닫히는 지점을 찾는다
        j = i + 1
        while j < len(lines):
            c = FENCE_RE.match(lines[j])
            if (c and c.group("fence")[0] == fence[0]
                    and len(c.group("fence")) >= len(fence)
                    and c.group("info").strip() == ""):
                break
            j += 1

        block = lines[i + 1: j]
        if info == "tikz" and j < len(lines):
            # 블록 들여쓰기 제거 (admonition 안에서도 쓸 수 있게)
            dedented = [l[len(indent):] if l.startswith(indent) else l for l in block]
            source = "\n".join(dedented)
            alt, scale = "", DEFAULT_SCALE
            for l in dedented:
                t = l.strip()
                if t.startswith("%alt:"):
                    alt = t[len("%alt:"):].strip()
                elif t.startswith("%scale:"):
                    try:
                        scale = float(t[len("%scale:"):].strip())
                    except ValueError:
                        raise PluginError(
                            f"[TikZ] {page.file.src_path}: %scale 값이 숫자가 아닙니다 → {t}"
                        )
            svg = _compile(source, page.file.src_path)
            out.append(_to_html(svg, alt, scale, indent))
        else:
            # tikz가 아닌 코드 블록(예: 사용법 예시)은 건드리지 않고 그대로 둔다
            out.extend(lines[i: j + 1])
        i = j + 1

    return "\n".join(out)
