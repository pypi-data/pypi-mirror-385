import { defineComponent as b, ref as N, computed as n, normalizeClass as l, watch as T, createElementBlock as w, openBlock as L, normalizeStyle as x, createElementVNode as i, unref as u, toDisplayString as z } from "vue";
import { useBindingGetter as D, useLanguage as H } from "instaui";
import { highlighterTask as S, getTransformers as $, readyCopyButton as E } from "@/shiki_code_logic";
const M = { class: "lang" }, V = ["innerHTML"], q = /* @__PURE__ */ b({
  __name: "Shiki_Code",
  props: {
    code: {},
    language: {},
    theme: {},
    themes: {},
    transformers: {},
    lineNumbers: { type: Boolean },
    useDark: { type: Boolean }
  },
  setup(g) {
    const e = g, {
      transformers: h = [],
      themes: d = {
        light: "vitesse-light",
        dark: "vitesse-dark"
      },
      useDark: f
    } = e, { getValue: p } = D(), c = N(""), s = n(() => e.language || "python"), a = n(
      () => e.theme || (p(f) ? "dark" : "light")
    ), v = n(() => e.lineNumbers ?? !0), y = n(() => l([
      `language-${s.value}`,
      `theme-${a.value}`,
      "shiki-code",
      { "line-numbers": v.value }
    ]));
    T(
      [() => e.code, a],
      async ([t, o]) => {
        if (!t)
          return;
        t = t.trim();
        const r = await S, B = await $(h);
        c.value = await r.codeToHtml(t, {
          themes: d,
          lang: s.value,
          transformers: B,
          defaultColor: a.value,
          colorReplacements: {
            "#ffffff": "#f8f8f2"
          }
        });
      },
      { immediate: !0 }
    );
    const { copyButtonClick: m, btnClasses: k } = E(e), C = H(), _ = n(() => `--shiki-code-copy-copied-text-content: '${C.value === "zh_CN" ? "已复制" : "Copied"}'`);
    return (t, o) => (L(), w("div", {
      class: l(y.value),
      style: x(_.value)
    }, [
      i("button", {
        class: l(u(k)),
        title: "Copy Code",
        onClick: o[0] || (o[0] = //@ts-ignore
        (...r) => u(m) && u(m)(...r))
      }, null, 2),
      i("span", M, z(s.value), 1),
      i("div", {
        innerHTML: c.value,
        style: { overflow: "hidden" }
      }, null, 8, V)
    ], 6));
  }
});
export {
  q as default
};
