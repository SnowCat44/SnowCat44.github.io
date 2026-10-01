# NTT 표현 (NTT Representation)

***상태: 작성 중 · 최종 수정일: 2026. 9. 30.***

수론 변환(Number Theoretic Transform, NTT)은 환(ring)의 $R_q$와 $T_q$ 사이의 특정한 동형사상(isomorphism)이다. $\zeta=1753 \in \mathbb{Z}_q$라 하자. 이는 512번째 단위근(root of unity)이다. $w \in R_q$일 때,

$$\text{NTT}(w)=(w(\zeta_0),w(\zeta_1),\dots,w(\zeta_{255})) \in T_q,$$

여기서 $\zeta_i=w(\zeta^{2\text{BitRev}_8(i)+1}) \bmod q$ 이다.

NTT를 사용하는 동기는 환 $T_q$에서 곱셈이 상당히 더 빠르기 때문이다. NTT가 동형사상이므로, 임의의 $a,b \in R_q$에 대해,

$$\text{NTT}(ab)=\text{NTT}(a) \circ \text{NTT}(b).$$

