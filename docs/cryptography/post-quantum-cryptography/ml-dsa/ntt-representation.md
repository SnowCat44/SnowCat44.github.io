# NTT 표현 (NTT Representation)

***상태: 작성 중 · 최종 수정일: 2026. 9. 30.***

수론 변환(Number Theoretic Transform, NTT)은 환(ring)의 $R_q$와 $T_q$ 사이의 특정한 동형사상(isomorphism)이다. $\zeta=1753 \in \mathbb{Z}_q$라 하자. 이는 512번째 단위근(root of unity)이다. $w \in R_q$일 때,

$$\text{NTT}(w)=(w(\zeta_0),w(\zeta_1),\dots,w(\zeta_{255})) \in T_q,$$

여기서 $\zeta_i=w(\zeta^{2\text{BitRev}_8(i)+1}) \bmod q$ 이다.

NTT를 사용하는 동기는 환 $T_q$에서 곱셈이 상당히 더 빠르기 때문이다. NTT가 동형사상이므로, 임의의 $a,b \in R_q$에 대해,

$$\text{NTT}(ab)=text{NTT}(a) \circ text{NTT}(b).$$



<!--
[개념 페이지 템플릿] 수학·암호학·컴퓨터 과학 등 이론 항목용
- 위치: docs/<대분류>/<소분류>/<항목>.md  (파일 이름: 영문 소문자 + 하이픈)
- 필요 없는 상자는 지운다. 같은 종류의 상자를 여러 개 둘 수 있다.
- ID: NNNNNN 자리를 빌드 로그의 "다음 번호"로 바꾼다 (제목과 attrs 두 곳 모두).
  바꾸지 않으면 ID 검사에서 빌드가 멈춘다.
- 다른 용어가 이 페이지에서 처음 나올 때 그 용어의 정의 상자 ID로 링크한다.
- 상태: '작성 중' 또는 '검증 완료'
  (검증 완료 = 모든 사실 주장에 출처 각주가 있고 원문과 대조를 마침)
- 이 주석은 화면에 보이지 않지만 페이지 소스(HTML)에는 남는다. 다 쓴 뒤에는 지운다.
-->

/// note | 표기
    attrs: {id: notation}

(헷갈릴 수 있는 표기가 있을 때만 둔다. 없으면 이 상자를 지운다.)
///

/// definition | 정의 · def-NNNNNN · 용어 (English Term)
    attrs: {id: def-NNNNNN}

정의문. 다른 용어는 처음 나올 때 링크한다: [용어](../소분류/항목.md#def-NNNNNN)[^src-def]
///

/// theorem | 정리 · thm-NNNNNN · 정리 이름 (English Name)
    attrs: {id: thm-NNNNNN}

<!-- 종류가 보조정리·명제·따름정리이면 제목 앞의 '정리'만 바꾼다. 접두어는 항상 thm- -->

**가정.** …

**결론.** …[^src-thm]

//// proof | 증명
증명 내용. $\blacksquare$
////
///

/// example | 예 · ex-NNNNNN · 제목
    attrs: {id: ex-NNNNNN}

<!-- 반례이면 제목 앞의 '예'를 '반례'로 바꾼다. 접두어는 항상 ex- -->

내용
///

/// algorithm | 알고리즘 · alg-NNNNNN · 알고리즘 이름 (English Name)
    attrs: {id: alg-NNNNNN}

**입력.** …

**출력.** …

```text
1. …
2. …
```

**정확성.** [정리 thm-NNNNNN](#thm-NNNNNN)에 의해 …

**복잡도.** 시간 $O(\cdot)$, 공간 $O(\cdot)$

**구현.** [Python](../../programming/python/항목.md) · [C](../../programming/c/항목.md)
///

## 출처 (References)

- (이 페이지의 참고문헌을 모아 적는다)

[^src-def]: 저자, *책 제목*, 판, 출판사, 연도, p. 쪽.
[^src-thm]: 저자, *책 제목*, 판, 출판사, 연도, Theorem 번호, p. 쪽.
