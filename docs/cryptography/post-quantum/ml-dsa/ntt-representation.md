# NTT 표현 (NTT Representation)

***상태: 작성 중 · 최종 수정일: 2026. 10. 1.***

수론 변환(Number Theoretic Transform, NTT)은 환(ring)의 $R_q$와 $T_q$ 사이의 특정한 동형사상(isomorphism)이다. $\zeta=1753 \in \mathbb{Z}_q$라 하자. 이는 512번째 단위근(root of unity)이다.[^fips204-2.5][^own-zeta] $w \in R_q$일 때,

$$\mathrm{NTT}(w)=(w(\zeta_0),w(\zeta_1),\dots,w(\zeta_{255})) \in T_q,$$

여기서 $\zeta_i=w(\zeta^{2\mathrm{BitRev}_8(i)+1}) \bmod q$ 이다.[^fips204-2.5][^fips204-typo]

NTT를 사용하는 동기는 환 $T_q$에서 곱셈이 상당히 더 빠르기 때문이다. NTT가 동형사상이므로, 임의의 $a,b \in R_q$에 대해,

$$\mathrm{NTT}(ab)=\mathrm{NTT}(a) \circ \mathrm{NTT}(b).$$


## 출처 (References)

- NIST, *FIPS 204: Module-Lattice-Based Digital Signature Standard*, 2024-08-13. DOI: <https://doi.org/10.6028/NIST.FIPS.204>

[^fips204-2.5]: NIST, FIPS 204, §2.5 "NTT Representation", p. 8. (accessed 2026-10-01)
[^own-zeta]: "원시"임은 $\zeta^{256} \equiv -1 \pmod q$를 직접 계산해 확인 (2026-10-01). 원문은 "a 512th root of unity"라고만 적음.
[^fips204-typo]: 원문 §2.5에는 $\zeta_i = w(\zeta^{2\mathrm{BitRev}_8(i)+1}) \bmod q$로 적혀 있으나, $w$가 들어가면 순환 정의가 된다. 각 성분이 $\zeta^{2\mathrm{BitRev}_8(i)+1}$에서 $w$를 평가한 값임을 직접 계산으로 확인 (2026-10-01).