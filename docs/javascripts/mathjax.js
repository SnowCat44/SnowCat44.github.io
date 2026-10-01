window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  },
  chtml: {
    mtextInheritFont: true
  }
};

// 페이지 이동(navigation.instant) 때마다 수식을 다시 그린다.
// MathJax의 첫 그리기가 끝난 뒤에만 실행해야, 자동으로 불러오는 확장(\color 등)이 깨지지 않는다.
document$.subscribe(() => {
  MathJax.startup.promise.then(() => {
    MathJax.startup.output.clearCache();
    MathJax.typesetClear();
    MathJax.texReset();
    return MathJax.typesetPromise();
  });
});
