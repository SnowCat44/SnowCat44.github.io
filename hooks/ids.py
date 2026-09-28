"""
ID 자동 검사 훅 (MkDocs hooks 기능)

정의·정리·예시·알고리즘 상자의 고유 ID가 규칙을 지키는지 빌드할 때 검사한다.
하나라도 어기면 빌드를 멈추고 어느 파일의 무엇이 틀렸는지 알려준다.

검사 항목:
  1) 형식      : 접두어-숫자 (숫자는 최소 6자리, 예: thm-000042)
  2) 접두어    : 상자 종류와 맞아야 함
                 definition → def / theorem → thm / algorithm → alg / example → ex
  3) 제목 일치 : 상자 제목에 적힌 ID와 attrs의 ID가 같아야 함 (복사·붙여넣기 실수 방지)
  4) 누락      : 위 네 종류의 상자에는 반드시 ID가 있어야 함
  5) 중복      : 번호는 사이트 전체에서 하나로 이어 매기므로,
                 접두어가 달라도 번호가 같으면 중복 (def-000001 과 thm-000001 은 충돌)

검사를 통과하면 빌드 로그에 사용 중인 ID 개수와 다음에 쓸 번호를 알려준다.

작성 형식 (templates/concept.md 참고):
    /// theorem | 정리 · thm-000002 · 라그랑주 정리
        attrs: {id: thm-000002}

    내용
    ///
"""

import logging
import re

from mkdocs.exceptions import PluginError

log = logging.getLogger("mkdocs.hooks.ids")

# 상자 종류 → 허용 접두어
PREFIX_OF = {
    "definition": "def",
    "theorem": "thm",
    "algorithm": "alg",
    "example": "ex",
}

MIN_DIGITS = 6

BOX_OPEN_RE = re.compile(r"^(?P<indent>[ \t]*)/{3,}\s*(?P<type>[a-z]+)\s*(\|\s*(?P<title>.*))?$")
ATTRS_ID_RE = re.compile(r"attrs:\s*\{[^}]*\bid:\s*(?P<id>[^\s,}]+)")
ID_RE = re.compile(r"^(?P<prefix>[a-z]+)-(?P<num>\d+)$")
TITLE_ID_RE = re.compile(r"\b(?:def|thm|alg|ex)-\d+\b")
FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")

# 빌드마다 새로 채워지는 기록: 번호 → (ID, 파일)
_seen = {}
_errors = []


def on_pre_build(config):
    _seen.clear()
    _errors.clear()


def _lines_outside_code(markdown):
    """코드 블록(``` 또는 ~~~) 바깥의 줄만 (줄 번호, 내용)으로 돌려준다."""
    fence = None
    for no, line in enumerate(markdown.split("\n"), start=1):
        m = FENCE_RE.match(line)
        if m:
            mark = m.group(1)
            if fence is None:
                fence = mark
                continue
            if mark[0] == fence[0] and len(mark) >= len(fence) and line.strip() == mark:
                fence = None
                continue
        if fence is None:
            yield no, line


def on_page_markdown(markdown, page, config, files):
    src = page.file.src_path
    lines = list(_lines_outside_code(markdown))

    for i, (no, line) in enumerate(lines):
        m = BOX_OPEN_RE.match(line)
        if not m or m.group("type") not in PREFIX_OF:
            continue
        box_type = m.group("type")
        title = (m.group("title") or "").strip()
        where = f"{src}:{no}"

        # 상자 바로 아래 들여쓴 옵션 줄들에서 attrs의 id를 찾는다
        box_id = None
        for no2, opt in lines[i + 1:]:
            if not opt.strip():
                break
            a = ATTRS_ID_RE.search(opt)
            if a:
                box_id = a.group("id")
                break
            if not opt.startswith((" ", "\t")):
                break

        if box_id is None:
            _errors.append(f"{where}: '{box_type}' 상자에 ID가 없습니다 (attrs: {{id: ...}} 필요)")
            continue

        idm = ID_RE.match(box_id)
        if not idm:
            _errors.append(
                f"{where}: ID 형식이 틀렸습니다 → '{box_id}' (예: {PREFIX_OF[box_type]}-000042)"
            )
            continue

        prefix, num = idm.group("prefix"), idm.group("num")
        expected = PREFIX_OF[box_type]
        if prefix != expected:
            _errors.append(
                f"{where}: '{box_type}' 상자의 접두어는 '{expected}-' 이어야 합니다 → '{box_id}'"
            )
        if len(num) < MIN_DIGITS:
            _errors.append(
                f"{where}: ID 숫자는 최소 {MIN_DIGITS}자리입니다 → '{box_id}' "
                f"(예: {prefix}-{num.zfill(MIN_DIGITS)})"
            )

        title_ids = TITLE_ID_RE.findall(title)
        if title_ids and box_id not in title_ids:
            _errors.append(
                f"{where}: 제목의 ID({', '.join(title_ids)})와 attrs의 ID({box_id})가 다릅니다"
            )

        n = int(num)
        if n in _seen:
            first_id, first_where = _seen[n]
            _errors.append(
                f"{where}: 번호 {num} 중복 → '{box_id}' (이미 {first_where} 에서 '{first_id}'로 사용)"
            )
        else:
            _seen[n] = (box_id, where)

    return markdown


def on_post_build(config):
    if _errors:
        raise PluginError(
            "[ID 검사] 규칙을 어긴 ID가 있습니다:\n  - " + "\n  - ".join(_errors)
        )
    next_num = (max(_seen) + 1) if _seen else 1
    log.info(
        f"[ID 검사] 통과 · 사용 중 {len(_seen)}개 · 다음 번호: {str(next_num).zfill(MIN_DIGITS)}"
    )
