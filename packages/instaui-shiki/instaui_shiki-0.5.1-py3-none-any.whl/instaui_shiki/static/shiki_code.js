import { defineComponent as N, ref as b, computed as n, normalizeClass as i, watch as w, createElementBlock as T, openBlock as L, normalizeStyle as $, createElementVNode as u, unref as c, toDisplayString as x } from "vue";
import { useBindingGetter as z, useLanguage as D } from "instaui";
import { highlighterTask as H, getTransformers as S, readyCopyButton as E } from "@/shiki_code_logic";
function M(s) {
  return s.replace(/^[\r\n\u2028\u2029]+|[\r\n\u2028\u2029]+$/g, "");
}
const V = { class: "lang" }, G = ["innerHTML"], A = /* @__PURE__ */ N({
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
  setup(s) {
    const e = s, {
      transformers: f = [],
      themes: h = {
        light: "vitesse-light",
        dark: "vitesse-dark"
      },
      useDark: d
    } = e, { getValue: p } = z(), m = b(""), a = n(() => e.language || "python"), o = n(
      () => e.theme || (p(d) ? "dark" : "light")
    ), v = n(() => e.lineNumbers ?? !0), y = n(() => i([
      `language-${a.value}`,
      `theme-${o.value}`,
      "shiki-code",
      { "line-numbers": v.value }
    ]));
    w(
      [() => e.code, o],
      async ([t, r]) => {
        if (!t)
          return;
        t = M(t);
        const l = await H, B = await S(f);
        m.value = await l.codeToHtml(t, {
          themes: h,
          lang: a.value,
          transformers: B,
          defaultColor: o.value,
          colorReplacements: {
            "#ffffff": "#f8f8f2"
          }
        });
      },
      { immediate: !0 }
    );
    const { copyButtonClick: g, btnClasses: k } = E(e), C = D(), _ = n(() => `--shiki-code-copy-copied-text-content: '${C.value === "zh_CN" ? "已复制" : "Copied"}'`);
    return (t, r) => (L(), T("div", {
      class: i(y.value),
      style: $(_.value)
    }, [
      u("button", {
        class: i(c(k)),
        title: "Copy Code",
        onClick: r[0] || (r[0] = //@ts-ignore
        (...l) => c(g) && c(g)(...l))
      }, null, 2),
      u("span", V, x(a.value), 1),
      u("div", {
        innerHTML: m.value,
        style: { overflow: "hidden" }
      }, null, 8, G)
    ], 6));
  }
});
export {
  A as default
};
