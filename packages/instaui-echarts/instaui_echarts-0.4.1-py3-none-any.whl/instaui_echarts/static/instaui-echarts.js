import { computed as _e, watch as kt, defineComponent as we, useTemplateRef as Ae, shallowRef as Oe, onMounted as je, useAttrs as Ie, createElementBlock as Se, openBlock as Ce, mergeProps as Ee, unref as Me } from "vue";
import * as qt from "echarts";
import { useBindingGetter as Te } from "instaui";
function* ht(t, e, n) {
  if (!e || n === "value") {
    yield void 0;
    return;
  }
  const r = t.dimensions.indexOf(e);
  if (r === -1) throw new Error(`Invalid color field: ${e}`);
  const o = /* @__PURE__ */ new Set();
  for (const i of t.source) {
    const a = i[r];
    o.has(a) || (o.add(a), yield a);
  }
}
function q(t, e) {
  return {
    labelConfig: t ? e : void 0,
    encodeLabelConfig: t ? {
      label: t
    } : void 0
  };
}
function X(t) {
  return {
    encodeTooltipConfig: t ? {
      tooltip: t
    } : void 0
  };
}
function I(t) {
  const { dataset: e, field: n } = t, r = e.dimensions.indexOf(n);
  if (r === -1)
    throw new Error(`Invalid color field: ${n}`);
  return typeof e.source[0][r] == "string" ? "category" : "value";
}
function $e(t) {
  const { dataset: e, field: n } = t, r = e.dimensions.indexOf(n);
  if (r === -1)
    throw new Error(`Invalid color field: ${n}`);
  const o = e.source.map((s) => s[r]), i = Math.min(...o), a = Math.max(...o);
  return [i, a];
}
function U(t) {
  const { xType: e, xField: n, extendConfig: r } = t;
  return { ...r, type: e, name: n + " →" };
}
function G(t) {
  const { yType: e, yField: n, extendConfig: r } = t;
  return { ...r, type: e, name: "↑ " + n };
}
function Jt(t) {
  const { colorField: e, colorValue: n } = t;
  if (e)
    return n;
}
class yt {
  constructor(e) {
    this.dataset = e;
  }
  filterWithFacet(e) {
    const { facetConfig: n, rowValue: r, columnValue: o } = e, i = this.dataset.dimensions, a = this.dataset.source, { row: s, column: c } = n, u = s ? i.indexOf(s) : -1, l = c ? i.indexOf(c) : -1, f = {
      source: u > -1 || l > -1 ? a.filter((d) => {
        const p = u === -1 || r === void 0 || d[u] === r, y = l === -1 || o === void 0 || d[l] === o;
        return p && y;
      }) : a,
      dimensions: i
    };
    return new yt(f);
  }
  getValues(e) {
    const n = this.dataset.dimensions.indexOf(e);
    if (n === -1)
      throw new Error(`Invalid field: ${e}`);
    return this.dataset.source.map((r) => r[n]);
  }
}
const gt = {
  axisLine: {
    show: !1
  }
}, mt = {
  axisLine: {
    show: !1
  }
}, ze = {
  axisLine: {
    show: !1,
    onZero: !1
  }
}, Ve = {
  axisLine: {
    show: !1,
    onZero: !1
  }
};
function Fe(t, e, n) {
  const r = t.x || "x", o = t.y || "y", i = t.echarts || {}, { facetInfo: a } = e, { row: s, column: c } = t.facet || {}, u = s !== void 0, l = c !== void 0;
  a.rowValues.forEach((f) => {
    a.columnValues.forEach((d) => {
      const p = n.getAxes({
        rowValue: f,
        columnValue: d
      }), y = p.fillXAxisConfig({
        config: U({
          xType: "category",
          xField: r,
          extendConfig: gt
        }),
        xName: r
      }), w = p.fillYAxisConfig({
        config: G({
          yType: "value",
          yField: o,
          extendConfig: mt
        }),
        yName: o
      }), m = [];
      u && m.push({ dim: s, value: f }), l && m.push({ dim: c, value: d });
      const { labelConfig: v, encodeLabelConfig: x } = q(
        t.label,
        {
          label: {
            show: !0,
            position: "insideTop"
          }
        }
      ), { encodeTooltipConfig: g } = X(
        t.tooltip
      ), j = {
        ...i,
        type: "bar",
        ...v,
        encode: { x: r, y: o, ...x, ...g },
        datasetId: n.datasetManager.getDatasetId({
          data: t.data,
          filters: m
        }),
        xAxisId: y,
        yAxisId: w
      };
      n.addSeries(j);
    });
  });
}
function Pe(t, e, n) {
  const r = t.x || "x", o = t.y || "y", i = t.color, { facetInfo: a } = e, { row: s, column: c } = t.facet || {}, u = t.echarts || {}, l = s !== void 0, f = c !== void 0, d = i ? I({
    dataset: t.data,
    field: i
  }) : void 0;
  a.rowValues.forEach((p) => {
    a.columnValues.forEach((y) => {
      const w = n.getAxes({
        rowValue: p,
        columnValue: y
      }), m = w.fillXAxisConfig({
        config: U({
          xType: "category",
          xField: r,
          extendConfig: gt
        }),
        xName: r
      }), v = w.fillYAxisConfig({
        config: G({
          yType: "value",
          yField: o,
          extendConfig: mt
        }),
        yName: o
      });
      for (const x of ht(
        t.data,
        i,
        d
      )) {
        const g = [];
        l && g.push({ dim: s, value: p }), f && g.push({ dim: c, value: y }), i && d === "category" && g.push({ dim: i, value: x });
        const { labelConfig: j, encodeLabelConfig: T } = q(
          t.label,
          {
            label: {
              show: !0,
              position: "top"
            }
          }
        ), { encodeTooltipConfig: b } = X(
          t.tooltip
        ), A = {
          ...u,
          type: "line",
          showSymbol: !1,
          ...j,
          encode: { x: r, y: o, ...T, ...b },
          datasetId: n.datasetManager.getDatasetId({
            data: t.data,
            filters: g
          }),
          xAxisId: m,
          yAxisId: v
        };
        n.addSeries(A);
      }
    });
  });
}
function Ne(t, e, n) {
  const { facetInfo: r } = e, { row: o, column: i } = t.facet || {}, a = t.echarts || {}, s = o !== void 0, c = i !== void 0;
  r.rowValues.forEach((u) => {
    r.columnValues.forEach((l) => {
      const f = [];
      s && f.push({ dim: o, value: u }), c && f.push({ dim: i, value: l });
      const { encodeTooltipConfig: d } = X(
        t.tooltip
      ), p = {
        ...a,
        type: "pie",
        encode: {
          name: t.name || "name",
          value: t.value || "value",
          ...d
        },
        datasetId: n.datasetManager.getDatasetId({
          data: t.data,
          filters: f
        })
      };
      n.addSeries(p);
    });
  });
}
function De(t, e, n) {
  const r = t.x || "x", o = t.y || "y", i = t.color, a = t.size, { facetInfo: s } = e, { row: c, column: u } = t.facet || {}, l = t.echarts || {}, f = c !== void 0, d = u !== void 0, p = i ? I({
    dataset: t.data,
    field: i
  }) : void 0, y = i ? $e({
    dataset: t.data,
    field: i
  }) : void 0, w = I({
    dataset: t.data,
    field: r
  }), m = I({
    dataset: t.data,
    field: o
  });
  s.rowValues.forEach((v) => {
    s.columnValues.forEach((x) => {
      const g = n.getAxes({
        rowValue: v,
        columnValue: x
      }), j = g.fillXAxisConfig({
        config: U({
          xType: w,
          xField: r,
          extendConfig: ze
        }),
        xName: r
      }), T = g.fillYAxisConfig({
        config: G({
          yType: m,
          yField: o,
          extendConfig: Ve
        }),
        yName: o
      });
      for (const b of ht(
        t.data,
        i,
        p
      )) {
        const A = [];
        f && A.push({ dim: c, value: v }), d && A.push({ dim: u, value: x }), i && p === "category" && A.push({ dim: i, value: b });
        const { labelConfig: ot, encodeLabelConfig: it } = q(
          t.label,
          {
            label: {
              show: !0,
              position: "top"
            }
          }
        ), { encodeTooltipConfig: at } = X(
          t.tooltip
        ), st = {
          name: Jt({ colorField: i, colorValue: b }),
          ...l,
          type: "scatter",
          ...ot,
          encode: { x: r, y: o, ...it, ...at },
          datasetId: n.datasetManager.getDatasetId({
            data: t.data,
            filters: A
          }),
          xAxisId: j,
          yAxisId: T
        }, Ct = n.addSeries(st);
        a && n.addVisualMap({
          show: !1,
          type: "continuous",
          seriesId: Ct,
          dimension: a,
          inRange: {
            symbolSize: [10, 100]
          }
        }), i && p === "value" && n.addVisualMap({
          show: !1,
          type: "continuous",
          min: y[0],
          max: y[1],
          seriesId: Ct,
          dimension: i,
          inRange: {
            color: ["#053061", "#f4eeeb", "#67001f"]
          }
        });
      }
    });
  });
}
function Re(t, e, n) {
  const r = t.x || "x", o = t.y || "y", i = t.color, a = t.size, { facetInfo: s } = e, { row: c, column: u } = t.facet || {}, l = t.echarts || {}, f = c !== void 0, d = u !== void 0, p = i ? I({
    dataset: t.data,
    field: i
  }) : void 0, y = I({
    dataset: t.data,
    field: r
  }), w = I({
    dataset: t.data,
    field: o
  });
  s.rowValues.forEach((m) => {
    s.columnValues.forEach((v) => {
      const x = n.getAxes({
        rowValue: m,
        columnValue: v
      }), g = x.fillXAxisConfig({
        config: U({ xType: y, xField: r }),
        xName: r
      }), j = x.fillYAxisConfig({
        config: G({ yType: w, yField: o }),
        yName: o
      });
      for (const T of ht(
        t.data,
        i,
        p
      )) {
        const b = [];
        f && b.push({ dim: c, value: m }), d && b.push({ dim: u, value: v }), i && p === "category" && b.push({ dim: i, value: T });
        const { labelConfig: A, encodeLabelConfig: ot } = q(
          t.label,
          {
            label: {
              show: !0,
              position: "top"
            }
          }
        ), { encodeTooltipConfig: it } = X(
          t.tooltip
        ), at = {
          name: Jt({ colorField: i, colorValue: T }),
          ...l,
          type: "effectScatter",
          ...A,
          encode: { x: r, y: o, ...ot, ...it },
          datasetId: n.datasetManager.getDatasetId({
            data: t.data,
            filters: b
          }),
          xAxisId: g,
          yAxisId: j
        }, st = n.addSeries(at);
        a && n.addVisualMap({
          show: !1,
          type: "continuous",
          seriesId: st,
          dimension: a,
          inRange: {
            symbolSize: [10, 100]
          }
        });
      }
    });
  });
}
var Qt = typeof global == "object" && global && global.Object === Object && global, We = typeof self == "object" && self && self.Object === Object && self, z = Qt || We || Function("return this")(), B = z.Symbol, te = Object.prototype, Le = te.hasOwnProperty, Xe = te.toString, N = B ? B.toStringTag : void 0;
function Ue(t) {
  var e = Le.call(t, N), n = t[N];
  try {
    t[N] = void 0;
    var r = !0;
  } catch {
  }
  var o = Xe.call(t);
  return r && (e ? t[N] = n : delete t[N]), o;
}
var Ge = Object.prototype, He = Ge.toString;
function Be(t) {
  return He.call(t);
}
var Ye = "[object Null]", Ke = "[object Undefined]", Et = B ? B.toStringTag : void 0;
function J(t) {
  return t == null ? t === void 0 ? Ke : Ye : Et && Et in Object(t) ? Ue(t) : Be(t);
}
function H(t) {
  return t != null && typeof t == "object";
}
var Y = Array.isArray;
function E(t) {
  var e = typeof t;
  return t != null && (e == "object" || e == "function");
}
function ee(t) {
  return t;
}
var Ze = "[object AsyncFunction]", ke = "[object Function]", qe = "[object GeneratorFunction]", Je = "[object Proxy]";
function vt(t) {
  if (!E(t))
    return !1;
  var e = J(t);
  return e == ke || e == qe || e == Ze || e == Je;
}
var ct = z["__core-js_shared__"], Mt = function() {
  var t = /[^.]+$/.exec(ct && ct.keys && ct.keys.IE_PROTO || "");
  return t ? "Symbol(src)_1." + t : "";
}();
function Qe(t) {
  return !!Mt && Mt in t;
}
var tn = Function.prototype, en = tn.toString;
function nn(t) {
  if (t != null) {
    try {
      return en.call(t);
    } catch {
    }
    try {
      return t + "";
    } catch {
    }
  }
  return "";
}
var rn = /[\\^$.*+?()[\]{}|]/g, on = /^\[object .+?Constructor\]$/, an = Function.prototype, sn = Object.prototype, cn = an.toString, un = sn.hasOwnProperty, ln = RegExp(
  "^" + cn.call(un).replace(rn, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
);
function fn(t) {
  if (!E(t) || Qe(t))
    return !1;
  var e = vt(t) ? ln : on;
  return e.test(nn(t));
}
function dn(t, e) {
  return t?.[e];
}
function xt(t, e) {
  var n = dn(t, e);
  return fn(n) ? n : void 0;
}
var Tt = Object.create, pn = /* @__PURE__ */ function() {
  function t() {
  }
  return function(e) {
    if (!E(e))
      return {};
    if (Tt)
      return Tt(e);
    t.prototype = e;
    var n = new t();
    return t.prototype = void 0, n;
  };
}();
function hn(t, e, n) {
  switch (n.length) {
    case 0:
      return t.call(e);
    case 1:
      return t.call(e, n[0]);
    case 2:
      return t.call(e, n[0], n[1]);
    case 3:
      return t.call(e, n[0], n[1], n[2]);
  }
  return t.apply(e, n);
}
function yn(t, e) {
  var n = -1, r = t.length;
  for (e || (e = Array(r)); ++n < r; )
    e[n] = t[n];
  return e;
}
var gn = 800, mn = 16, vn = Date.now;
function xn(t) {
  var e = 0, n = 0;
  return function() {
    var r = vn(), o = mn - (r - n);
    if (n = r, o > 0) {
      if (++e >= gn)
        return arguments[0];
    } else
      e = 0;
    return t.apply(void 0, arguments);
  };
}
function bn(t) {
  return function() {
    return t;
  };
}
var K = function() {
  try {
    var t = xt(Object, "defineProperty");
    return t({}, "", {}), t;
  } catch {
  }
}(), _n = K ? function(t, e) {
  return K(t, "toString", {
    configurable: !0,
    enumerable: !1,
    value: bn(e),
    writable: !0
  });
} : ee, wn = xn(_n), An = 9007199254740991, On = /^(?:0|[1-9]\d*)$/;
function ne(t, e) {
  var n = typeof t;
  return e = e ?? An, !!e && (n == "number" || n != "symbol" && On.test(t)) && t > -1 && t % 1 == 0 && t < e;
}
function bt(t, e, n) {
  e == "__proto__" && K ? K(t, e, {
    configurable: !0,
    enumerable: !0,
    value: n,
    writable: !0
  }) : t[e] = n;
}
function Q(t, e) {
  return t === e || t !== t && e !== e;
}
var jn = Object.prototype, In = jn.hasOwnProperty;
function Sn(t, e, n) {
  var r = t[e];
  (!(In.call(t, e) && Q(r, n)) || n === void 0 && !(e in t)) && bt(t, e, n);
}
function Cn(t, e, n, r) {
  var o = !n;
  n || (n = {});
  for (var i = -1, a = e.length; ++i < a; ) {
    var s = e[i], c = void 0;
    c === void 0 && (c = t[s]), o ? bt(n, s, c) : Sn(n, s, c);
  }
  return n;
}
var $t = Math.max;
function En(t, e, n) {
  return e = $t(e === void 0 ? t.length - 1 : e, 0), function() {
    for (var r = arguments, o = -1, i = $t(r.length - e, 0), a = Array(i); ++o < i; )
      a[o] = r[e + o];
    o = -1;
    for (var s = Array(e + 1); ++o < e; )
      s[o] = r[o];
    return s[e] = n(a), hn(t, this, s);
  };
}
function Mn(t, e) {
  return wn(En(t, e, ee), t + "");
}
var Tn = 9007199254740991;
function re(t) {
  return typeof t == "number" && t > -1 && t % 1 == 0 && t <= Tn;
}
function _t(t) {
  return t != null && re(t.length) && !vt(t);
}
function $n(t, e, n) {
  if (!E(n))
    return !1;
  var r = typeof e;
  return (r == "number" ? _t(n) && ne(e, n.length) : r == "string" && e in n) ? Q(n[e], t) : !1;
}
function oe(t) {
  return Mn(function(e, n) {
    var r = -1, o = n.length, i = o > 1 ? n[o - 1] : void 0, a = o > 2 ? n[2] : void 0;
    for (i = t.length > 3 && typeof i == "function" ? (o--, i) : void 0, a && $n(n[0], n[1], a) && (i = o < 3 ? void 0 : i, o = 1), e = Object(e); ++r < o; ) {
      var s = n[r];
      s && t(e, s, r, i);
    }
    return e;
  });
}
var zn = Object.prototype;
function ie(t) {
  var e = t && t.constructor, n = typeof e == "function" && e.prototype || zn;
  return t === n;
}
function Vn(t, e) {
  for (var n = -1, r = Array(t); ++n < t; )
    r[n] = e(n);
  return r;
}
var Fn = "[object Arguments]";
function zt(t) {
  return H(t) && J(t) == Fn;
}
var ae = Object.prototype, Pn = ae.hasOwnProperty, Nn = ae.propertyIsEnumerable, ft = zt(/* @__PURE__ */ function() {
  return arguments;
}()) ? zt : function(t) {
  return H(t) && Pn.call(t, "callee") && !Nn.call(t, "callee");
};
function Dn() {
  return !1;
}
var se = typeof exports == "object" && exports && !exports.nodeType && exports, Vt = se && typeof module == "object" && module && !module.nodeType && module, Rn = Vt && Vt.exports === se, Ft = Rn ? z.Buffer : void 0, Wn = Ft ? Ft.isBuffer : void 0, ce = Wn || Dn, Ln = "[object Arguments]", Xn = "[object Array]", Un = "[object Boolean]", Gn = "[object Date]", Hn = "[object Error]", Bn = "[object Function]", Yn = "[object Map]", Kn = "[object Number]", Zn = "[object Object]", kn = "[object RegExp]", qn = "[object Set]", Jn = "[object String]", Qn = "[object WeakMap]", tr = "[object ArrayBuffer]", er = "[object DataView]", nr = "[object Float32Array]", rr = "[object Float64Array]", or = "[object Int8Array]", ir = "[object Int16Array]", ar = "[object Int32Array]", sr = "[object Uint8Array]", cr = "[object Uint8ClampedArray]", ur = "[object Uint16Array]", lr = "[object Uint32Array]", h = {};
h[nr] = h[rr] = h[or] = h[ir] = h[ar] = h[sr] = h[cr] = h[ur] = h[lr] = !0;
h[Ln] = h[Xn] = h[tr] = h[Un] = h[er] = h[Gn] = h[Hn] = h[Bn] = h[Yn] = h[Kn] = h[Zn] = h[kn] = h[qn] = h[Jn] = h[Qn] = !1;
function fr(t) {
  return H(t) && re(t.length) && !!h[J(t)];
}
function dr(t) {
  return function(e) {
    return t(e);
  };
}
var ue = typeof exports == "object" && exports && !exports.nodeType && exports, R = ue && typeof module == "object" && module && !module.nodeType && module, pr = R && R.exports === ue, ut = pr && Qt.process, Pt = function() {
  try {
    var t = R && R.require && R.require("util").types;
    return t || ut && ut.binding && ut.binding("util");
  } catch {
  }
}(), Nt = Pt && Pt.isTypedArray, le = Nt ? dr(Nt) : fr;
function hr(t, e) {
  var n = Y(t), r = !n && ft(t), o = !n && !r && ce(t), i = !n && !r && !o && le(t), a = n || r || o || i, s = a ? Vn(t.length, String) : [], c = s.length;
  for (var u in t)
    a && // Safari 9 has enumerable `arguments.length` in strict mode.
    (u == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
    o && (u == "offset" || u == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
    i && (u == "buffer" || u == "byteLength" || u == "byteOffset") || // Skip index properties.
    ne(u, c)) || s.push(u);
  return s;
}
function yr(t, e) {
  return function(n) {
    return t(e(n));
  };
}
function gr(t) {
  var e = [];
  if (t != null)
    for (var n in Object(t))
      e.push(n);
  return e;
}
var mr = Object.prototype, vr = mr.hasOwnProperty;
function xr(t) {
  if (!E(t))
    return gr(t);
  var e = ie(t), n = [];
  for (var r in t)
    r == "constructor" && (e || !vr.call(t, r)) || n.push(r);
  return n;
}
function fe(t) {
  return _t(t) ? hr(t) : xr(t);
}
var W = xt(Object, "create");
function br() {
  this.__data__ = W ? W(null) : {}, this.size = 0;
}
function _r(t) {
  var e = this.has(t) && delete this.__data__[t];
  return this.size -= e ? 1 : 0, e;
}
var wr = "__lodash_hash_undefined__", Ar = Object.prototype, Or = Ar.hasOwnProperty;
function jr(t) {
  var e = this.__data__;
  if (W) {
    var n = e[t];
    return n === wr ? void 0 : n;
  }
  return Or.call(e, t) ? e[t] : void 0;
}
var Ir = Object.prototype, Sr = Ir.hasOwnProperty;
function Cr(t) {
  var e = this.__data__;
  return W ? e[t] !== void 0 : Sr.call(e, t);
}
var Er = "__lodash_hash_undefined__";
function Mr(t, e) {
  var n = this.__data__;
  return this.size += this.has(t) ? 0 : 1, n[t] = W && e === void 0 ? Er : e, this;
}
function S(t) {
  var e = -1, n = t == null ? 0 : t.length;
  for (this.clear(); ++e < n; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
S.prototype.clear = br;
S.prototype.delete = _r;
S.prototype.get = jr;
S.prototype.has = Cr;
S.prototype.set = Mr;
function Tr() {
  this.__data__ = [], this.size = 0;
}
function tt(t, e) {
  for (var n = t.length; n--; )
    if (Q(t[n][0], e))
      return n;
  return -1;
}
var $r = Array.prototype, zr = $r.splice;
function Vr(t) {
  var e = this.__data__, n = tt(e, t);
  if (n < 0)
    return !1;
  var r = e.length - 1;
  return n == r ? e.pop() : zr.call(e, n, 1), --this.size, !0;
}
function Fr(t) {
  var e = this.__data__, n = tt(e, t);
  return n < 0 ? void 0 : e[n][1];
}
function Pr(t) {
  return tt(this.__data__, t) > -1;
}
function Nr(t, e) {
  var n = this.__data__, r = tt(n, t);
  return r < 0 ? (++this.size, n.push([t, e])) : n[r][1] = e, this;
}
function _(t) {
  var e = -1, n = t == null ? 0 : t.length;
  for (this.clear(); ++e < n; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
_.prototype.clear = Tr;
_.prototype.delete = Vr;
_.prototype.get = Fr;
_.prototype.has = Pr;
_.prototype.set = Nr;
var de = xt(z, "Map");
function Dr() {
  this.size = 0, this.__data__ = {
    hash: new S(),
    map: new (de || _)(),
    string: new S()
  };
}
function Rr(t) {
  var e = typeof t;
  return e == "string" || e == "number" || e == "symbol" || e == "boolean" ? t !== "__proto__" : t === null;
}
function et(t, e) {
  var n = t.__data__;
  return Rr(e) ? n[typeof e == "string" ? "string" : "hash"] : n.map;
}
function Wr(t) {
  var e = et(this, t).delete(t);
  return this.size -= e ? 1 : 0, e;
}
function Lr(t) {
  return et(this, t).get(t);
}
function Xr(t) {
  return et(this, t).has(t);
}
function Ur(t, e) {
  var n = et(this, t), r = n.size;
  return n.set(t, e), this.size += n.size == r ? 0 : 1, this;
}
function V(t) {
  var e = -1, n = t == null ? 0 : t.length;
  for (this.clear(); ++e < n; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
V.prototype.clear = Dr;
V.prototype.delete = Wr;
V.prototype.get = Lr;
V.prototype.has = Xr;
V.prototype.set = Ur;
var pe = yr(Object.getPrototypeOf, Object), Gr = "[object Object]", Hr = Function.prototype, Br = Object.prototype, he = Hr.toString, Yr = Br.hasOwnProperty, Kr = he.call(Object);
function ye(t) {
  if (!H(t) || J(t) != Gr)
    return !1;
  var e = pe(t);
  if (e === null)
    return !0;
  var n = Yr.call(e, "constructor") && e.constructor;
  return typeof n == "function" && n instanceof n && he.call(n) == Kr;
}
function Zr() {
  this.__data__ = new _(), this.size = 0;
}
function kr(t) {
  var e = this.__data__, n = e.delete(t);
  return this.size = e.size, n;
}
function qr(t) {
  return this.__data__.get(t);
}
function Jr(t) {
  return this.__data__.has(t);
}
var Qr = 200;
function to(t, e) {
  var n = this.__data__;
  if (n instanceof _) {
    var r = n.__data__;
    if (!de || r.length < Qr - 1)
      return r.push([t, e]), this.size = ++n.size, this;
    n = this.__data__ = new V(r);
  }
  return n.set(t, e), this.size = n.size, this;
}
function F(t) {
  var e = this.__data__ = new _(t);
  this.size = e.size;
}
F.prototype.clear = Zr;
F.prototype.delete = kr;
F.prototype.get = qr;
F.prototype.has = Jr;
F.prototype.set = to;
var ge = typeof exports == "object" && exports && !exports.nodeType && exports, Dt = ge && typeof module == "object" && module && !module.nodeType && module, eo = Dt && Dt.exports === ge, Rt = eo ? z.Buffer : void 0;
Rt && Rt.allocUnsafe;
function no(t, e) {
  return t.slice();
}
var Wt = z.Uint8Array;
function ro(t) {
  var e = new t.constructor(t.byteLength);
  return new Wt(e).set(new Wt(t)), e;
}
function oo(t, e) {
  var n = ro(t.buffer);
  return new t.constructor(n, t.byteOffset, t.length);
}
function io(t) {
  return typeof t.constructor == "function" && !ie(t) ? pn(pe(t)) : {};
}
function ao(t) {
  return function(e, n, r) {
    for (var o = -1, i = Object(e), a = r(e), s = a.length; s--; ) {
      var c = a[++o];
      if (n(i[c], c, i) === !1)
        break;
    }
    return e;
  };
}
var so = ao();
function dt(t, e, n) {
  (n !== void 0 && !Q(t[e], n) || n === void 0 && !(e in t)) && bt(t, e, n);
}
function co(t) {
  return H(t) && _t(t);
}
function pt(t, e) {
  if (!(e === "constructor" && typeof t[e] == "function") && e != "__proto__")
    return t[e];
}
function uo(t) {
  return Cn(t, fe(t));
}
function lo(t, e, n, r, o, i, a) {
  var s = pt(t, n), c = pt(e, n), u = a.get(c);
  if (u) {
    dt(t, n, u);
    return;
  }
  var l = i ? i(s, c, n + "", t, e, a) : void 0, f = l === void 0;
  if (f) {
    var d = Y(c), p = !d && ce(c), y = !d && !p && le(c);
    l = c, d || p || y ? Y(s) ? l = s : co(s) ? l = yn(s) : p ? (f = !1, l = no(c)) : y ? (f = !1, l = oo(c)) : l = [] : ye(c) || ft(c) ? (l = s, ft(s) ? l = uo(s) : (!E(s) || vt(s)) && (l = io(c))) : f = !1;
  }
  f && (a.set(c, l), o(l, c, r, i, a), a.delete(c)), dt(t, n, l);
}
function wt(t, e, n, r, o) {
  t !== e && so(e, function(i, a) {
    if (o || (o = new F()), E(i))
      lo(t, e, a, n, wt, r, o);
    else {
      var s = r ? r(pt(t, a), i, a + "", t, e, o) : void 0;
      s === void 0 && (s = i), dt(t, a, s);
    }
  }, fe);
}
var fo = oe(function(t, e, n, r) {
  wt(t, e, n, r);
}), po = oe(function(t, e, n) {
  wt(t, e, n);
});
function Z(t, e) {
  return e ? fo({}, t, e, (n, r) => {
    if (Y(n) && ye(r))
      return n.map((o) => po({}, o, r));
  }) : t;
}
function ho(t, e, n) {
  const { facetInfo: r } = e, o = t.value ? "value" : "map", i = t.rType;
  r.rowValues.forEach((a) => {
    r.columnValues.forEach((s) => {
      const c = n.getAxes({
        rowValue: a,
        columnValue: s
      }), u = new yt(
        t.data
      ).filterWithFacet({
        facetConfig: t.facet || {},
        rowValue: a,
        columnValue: s
      });
      o === "value" ? go(c, i, t, n) : o === "map" && yo(
        i,
        t,
        u,
        c,
        n
      );
    });
  });
}
function yo(t, e, n, r, o) {
  const i = t === "x" ? e.map.x1 : e.map.y1, a = t === "x" ? e.map.y1 : e.map.x1, s = n.getValues(i), c = n.getValues(a), u = r.fillXAxisConfig({
    config: U({
      xType: "value",
      xField: i,
      extendConfig: {
        ...gt,
        min: Math.min(...s),
        max: Math.max(...s)
      }
    }),
    xName: i
  }), l = r.fillYAxisConfig({
    config: G({
      yType: "value",
      yField: a,
      extendConfig: {
        ...mt,
        min: Math.min(...c),
        max: Math.max(...c)
      }
    }),
    yName: a
  }), f = Z(
    {
      color: "black",
      type: "solid",
      width: 1
    },
    e.lineStyle
  ), d = mo(e, n, t), p = {
    type: "lines",
    xAxisId: u,
    yAxisId: l,
    coordinateSystem: "cartesian2d",
    polyline: !0,
    lineStyle: f,
    data: d
  };
  o.addSeries(p);
}
function go(t, e, n, r) {
  const o = t.getXAxisId(), i = t.getYAxisId(), a = e === "x" ? "xAxis" : "yAxis", s = n.value.value.map((l) => ({
    [a]: l
  })), c = Z(
    {
      color: "black",
      type: "solid",
      width: 1
    },
    n.lineStyle
  ), u = {
    type: "line",
    xAxisId: o,
    yAxisId: i,
    data: [],
    markLine: {
      symbol: "none",
      label: { show: !1 },
      lineStyle: c,
      data: s,
      animation: !1
    }
  };
  r.addSeries(u);
}
function mo(t, e, n) {
  const r = e.dataset.source;
  if (n === "x") {
    const o = t.map.x1, i = t.map.y1, a = t.map.y2, s = t.data.dimensions.indexOf(o), c = t.data.dimensions.indexOf(i), u = t.data.dimensions.indexOf(a);
    return r.map((l) => {
      const f = l[s], d = l[c], p = l[u];
      return {
        coords: [
          [f, d],
          [f, p]
        ]
      };
    });
  }
  if (n === "y") {
    const o = t.map.y1, i = t.map.x1, a = t.map.x2, s = t.data.dimensions.indexOf(o), c = t.data.dimensions.indexOf(i), u = t.data.dimensions.indexOf(a);
    return r.map((l) => {
      const f = l[s], d = l[c], p = l[u];
      return {
        coords: [
          [d, f],
          [p, f]
        ]
      };
    });
  }
  throw new Error(`Invalid axisType ${n}`);
}
function vo(t, e, n) {
  switch (t.type) {
    case "bar":
      return Fe(
        t,
        e,
        n
      );
    case "line":
      return Pe(
        t,
        e,
        n
      );
    case "pie":
      return Ne(
        t,
        e,
        n
      );
    case "scatter":
      return De(
        t,
        e,
        n
      );
    case "effect-scatter":
      return Re(
        t,
        e,
        n
      );
    case "rule":
      return ho(
        t,
        e,
        n
      );
    default:
      throw new Error(`Unsupported mark type: ${t.type}`);
  }
}
const O = "-1", xo = {
  backgroundStyle: {
    borderWidth: 0
  },
  body: {
    itemStyle: {
      borderWidth: 0
    }
  }
};
class bo {
  constructor(e) {
    this.config = e, this.matrix = this.initMatrix(), this.axesManager = new _o(this.matrix), this.datasetManager = new Ao();
  }
  series = [];
  visualMap = [];
  datasetManager;
  axesManager;
  matrix;
  initMatrix() {
    const e = {
      ...xo,
      x: {
        data: [O],
        show: !1
      },
      y: {
        data: [O],
        show: !1
      }
    }, { rowValues: n, columnValues: r } = this.config.facetInfo || {};
    return n && (e.x.data = n), r && (e.y.data = r), e;
  }
  /**
   * getAxes
   */
  getAxes(e) {
    return this.axesManager.getAxes(e);
  }
  /**
   * addSeries
   */
  addSeries(e) {
    const n = `series-id-${this.series.length}`;
    return this.series.push({ ...e, id: n }), n;
  }
  /**
   * addVisualMap
   */
  addVisualMap(e) {
    this.visualMap.push(e);
  }
  toEChartsOption() {
    const { xAxis: e, yAxis: n, grid: r } = this.axesManager.toEChartsOption(), o = Oo(this.matrix), i = jo(
      r,
      o
    );
    return {
      xAxis: e,
      yAxis: n,
      grid: i,
      series: this.series,
      visualMap: this.visualMap,
      matrix: o,
      dataset: this.datasetManager.toDatasetOption()
    };
  }
}
class _o {
  itemMap;
  constructor(e) {
    this.itemMap = this.initItemMap(e);
  }
  initItemMap(e) {
    const n = /* @__PURE__ */ new Map();
    return e.x.data.forEach((r) => {
      e.y.data.forEach((o) => {
        const i = `${r}-${o}`, a = new wo({
          gridIdNumber: n.size,
          matrixCoord: [r, o]
        });
        n.set(i, a);
      });
    }), n;
  }
  getAxes(e) {
    const { rowValue: n, columnValue: r } = e, o = this.itemMap.get(`${n}-${r}`);
    if (!o)
      throw new Error("Invalid facet config");
    return o;
  }
  toEChartsOption() {
    const e = Array.from(this.itemMap.values()), n = e.flatMap((i) => i.xAxis), r = e.flatMap((i) => i.yAxis), o = e.flatMap((i) => i.grid);
    return {
      xAxis: n.length > 0 ? n : void 0,
      yAxis: r.length > 0 ? r : void 0,
      grid: o
    };
  }
}
class wo {
  xAxis = [];
  xAxisNamesIndexMap = /* @__PURE__ */ new Map();
  yAxis = [];
  yAxisNamesIndexMap = /* @__PURE__ */ new Map();
  grid = {};
  gridIdNumber;
  constructor(e) {
    const { gridIdNumber: n, matrixCoord: r } = e;
    this.gridIdNumber = n;
    const o = this.genGridId();
    this.grid = {
      id: o,
      coord: r,
      coordinateSystem: "matrix"
    };
  }
  genGridId() {
    return `gid-${this.gridIdNumber}`;
  }
  genXAxisId() {
    return `g-${this.gridIdNumber}-${this.xAxis.length}`;
  }
  genYAxisId() {
    return `g-${this.gridIdNumber}-${this.yAxis.length}`;
  }
  getXAxisId() {
    if (this.xAxis.length === 0) throw new Error("No xAxis");
    return `g-${this.gridIdNumber}-${this.xAxis.length - 1}`;
  }
  getYAxisId() {
    if (this.yAxis.length === 0) throw new Error("No yAxis");
    return `g-${this.gridIdNumber}-${this.yAxis.length - 1}`;
  }
  fillXAxisConfig(e) {
    if (this.xAxis.length > 2)
      throw new Error("Too many xAxis");
    const { config: n, xName: r } = e, o = this.xAxisNamesIndexMap.get(r);
    if (o !== void 0) {
      const a = this.xAxis[o];
      return Object.assign(a, {
        ...a,
        ...n
      }), a.id;
    }
    const i = this.genXAxisId();
    return this.xAxis.push({
      ...n,
      id: i,
      gridId: this.grid.id,
      show: !0
    }), this.xAxisNamesIndexMap.set(r, this.xAxis.length - 1), i;
  }
  fillYAxisConfig(e) {
    if (this.yAxis.length > 2)
      throw new Error("Too many yAxis");
    const { config: n, yName: r } = e, o = this.yAxisNamesIndexMap.get(r);
    if (o !== void 0) {
      const a = this.yAxis[o];
      return Object.assign(a, {
        ...a,
        ...n
      }), a.id;
    }
    const i = this.genYAxisId();
    return this.yAxis.push({
      ...n,
      id: i,
      gridId: this.grid.id,
      show: !0
    }), this.yAxisNamesIndexMap.set(r, this.yAxis.length - 1), i;
  }
}
class Ao {
  dataset = [];
  datasetMap = /* @__PURE__ */ new Map();
  datasetWithFilterSet = /* @__PURE__ */ new Set();
  /**
   * getDatasetId
   */
  getDatasetId(e) {
    const { data: n, filters: r } = e;
    let o = this.datasetMap.get(n);
    if (o || (o = this.genDataset(n)), r.length === 0)
      return o;
    const i = this.genWithFilterKey(o, r);
    return this.datasetWithFilterSet.has(i) || (this.datasetWithFilterSet.add(i), this.dataset.push({
      id: i,
      fromDatasetId: o,
      transform: {
        type: "filter",
        config: {
          and: r.map((a) => ({
            dimension: a.dim,
            [Lt(a.op)]: a.value
          }))
        }
      }
    })), i;
  }
  toDatasetOption() {
    return this.dataset;
  }
  genDataset(e) {
    const n = `ds${this.dataset.length}`;
    return this.datasetMap.set(e, n), this.dataset.push({
      id: n,
      dimensions: e.dimensions,
      source: e.source
    }), n;
  }
  genWithFilterKey(e, n) {
    const r = n.map((o) => `${o.dim}-${Lt(o.op)}-${o.value}`).join("-");
    return `${e}-${r}`;
  }
}
function Lt(t) {
  return t ?? "=";
}
function Oo(t) {
  const e = t.x.data[0] !== O, n = t.y.data[0] !== O;
  if (!(!e && !n))
    return {
      backgroundStyle: {
        borderWidth: 0
      },
      body: {
        itemStyle: {
          borderWidth: 0
        }
      },
      x: {
        ...t.x,
        show: t.x.data[0] !== O,
        levelSize: 30,
        itemStyle: {
          borderWidth: 0
        }
      },
      y: {
        ...t.y,
        show: t.y.data[0] !== O,
        levelSize: 30,
        itemStyle: {
          borderWidth: 0
        }
      }
    };
}
function jo(t, e) {
  if (e === void 0) {
    const { coord: n, coordinateSystem: r, ...o } = t[0];
    return [o];
  }
  return t;
}
const Io = {
  tooltip: {
    trigger: "axis"
  }
};
function So(t) {
  const e = Co(t), { marks: n } = e, r = new bo(e);
  n.forEach(
    (i) => vo(i, e, r)
  );
  const o = Z(
    r.toEChartsOption(),
    Io
  );
  return Z(o, t.echartsOptions);
}
function Co(t) {
  const { data: e, facet: n, marks: r, echartsOptions: o } = t, i = e && Xt(e), a = {
    data: null,
    row: null,
    column: null
  }, s = r.map((u) => {
    const l = u.data ?? i ?? { dimensions: [], source: [] };
    if (!l)
      throw new Error("Mark is missing data and no dataset is available");
    const f = Xt(l), d = u.facet ?? n;
    if (a.row === null)
      a.row = d?.row;
    else if (d && a.row !== d.row)
      throw new Error("Facet row is not consistent");
    if (a.column === null)
      a.column = d?.column;
    else if (d && a.column !== d?.column)
      throw new Error("Facet column is not consistent");
    return a.data === null && (a.data = f), {
      ...u,
      data: f,
      facet: d
    };
  }), c = {
    rowValues: [O],
    columnValues: [O]
  };
  if (a.row || a.column) {
    const u = a.data;
    if (a.row) {
      const l = u.dimensions.indexOf(a.row);
      c.rowValues = Array.from(
        new Set(u.source.map((f) => f[l]))
      );
    }
    if (a.column) {
      const l = u.dimensions.indexOf(a.column);
      c.columnValues = Array.from(
        new Set(u.source.map((f) => f[l]))
      );
    }
  }
  return {
    facetInfo: c,
    marks: s,
    echartsOptions: o
  };
}
function Xt(t) {
  const e = typeof t == "function" ? t() : t;
  if (Array.isArray(e)) {
    if (e.length === 0)
      return { dimensions: [], source: [] };
    const n = Object.keys(e[0]), r = e.map((o) => Object.values(o));
    return { dimensions: n, source: r };
  }
  return e;
}
var Eo = typeof global == "object" && global && global.Object === Object && global, Mo = typeof self == "object" && self && self.Object === Object && self, At = Eo || Mo || Function("return this")(), $ = At.Symbol, me = Object.prototype, To = me.hasOwnProperty, $o = me.toString, D = $ ? $.toStringTag : void 0;
function zo(t) {
  var e = To.call(t, D), n = t[D];
  try {
    t[D] = void 0;
    var r = !0;
  } catch {
  }
  var o = $o.call(t);
  return r && (e ? t[D] = n : delete t[D]), o;
}
var Vo = Object.prototype, Fo = Vo.toString;
function Po(t) {
  return Fo.call(t);
}
var No = "[object Null]", Do = "[object Undefined]", Ut = $ ? $.toStringTag : void 0;
function ve(t) {
  return t == null ? t === void 0 ? Do : No : Ut && Ut in Object(t) ? zo(t) : Po(t);
}
function Ro(t) {
  return t != null && typeof t == "object";
}
var Wo = "[object Symbol]";
function Ot(t) {
  return typeof t == "symbol" || Ro(t) && ve(t) == Wo;
}
function Lo(t, e) {
  for (var n = -1, r = t == null ? 0 : t.length, o = Array(r); ++n < r; )
    o[n] = e(t[n], n, t);
  return o;
}
var jt = Array.isArray, Gt = $ ? $.prototype : void 0, Ht = Gt ? Gt.toString : void 0;
function xe(t) {
  if (typeof t == "string")
    return t;
  if (jt(t))
    return Lo(t, xe) + "";
  if (Ot(t))
    return Ht ? Ht.call(t) : "";
  var e = t + "";
  return e == "0" && 1 / t == -1 / 0 ? "-0" : e;
}
function k(t) {
  var e = typeof t;
  return t != null && (e == "object" || e == "function");
}
var Xo = "[object AsyncFunction]", Uo = "[object Function]", Go = "[object GeneratorFunction]", Ho = "[object Proxy]";
function Bo(t) {
  if (!k(t))
    return !1;
  var e = ve(t);
  return e == Uo || e == Go || e == Xo || e == Ho;
}
var lt = At["__core-js_shared__"], Bt = function() {
  var t = /[^.]+$/.exec(lt && lt.keys && lt.keys.IE_PROTO || "");
  return t ? "Symbol(src)_1." + t : "";
}();
function Yo(t) {
  return !!Bt && Bt in t;
}
var Ko = Function.prototype, Zo = Ko.toString;
function ko(t) {
  if (t != null) {
    try {
      return Zo.call(t);
    } catch {
    }
    try {
      return t + "";
    } catch {
    }
  }
  return "";
}
var qo = /[\\^$.*+?()[\]{}|]/g, Jo = /^\[object .+?Constructor\]$/, Qo = Function.prototype, ti = Object.prototype, ei = Qo.toString, ni = ti.hasOwnProperty, ri = RegExp(
  "^" + ei.call(ni).replace(qo, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
);
function oi(t) {
  if (!k(t) || Yo(t))
    return !1;
  var e = Bo(t) ? ri : Jo;
  return e.test(ko(t));
}
function ii(t, e) {
  return t?.[e];
}
function It(t, e) {
  var n = ii(t, e);
  return oi(n) ? n : void 0;
}
var Yt = function() {
  try {
    var t = It(Object, "defineProperty");
    return t({}, "", {}), t;
  } catch {
  }
}(), ai = 9007199254740991, si = /^(?:0|[1-9]\d*)$/;
function ci(t, e) {
  var n = typeof t;
  return e = e ?? ai, !!e && (n == "number" || n != "symbol" && si.test(t)) && t > -1 && t % 1 == 0 && t < e;
}
function ui(t, e, n) {
  e == "__proto__" && Yt ? Yt(t, e, {
    configurable: !0,
    enumerable: !0,
    value: n,
    writable: !0
  }) : t[e] = n;
}
function be(t, e) {
  return t === e || t !== t && e !== e;
}
var li = Object.prototype, fi = li.hasOwnProperty;
function di(t, e, n) {
  var r = t[e];
  (!(fi.call(t, e) && be(r, n)) || n === void 0 && !(e in t)) && ui(t, e, n);
}
var pi = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, hi = /^\w*$/;
function yi(t, e) {
  if (jt(t))
    return !1;
  var n = typeof t;
  return n == "number" || n == "symbol" || n == "boolean" || t == null || Ot(t) ? !0 : hi.test(t) || !pi.test(t) || e != null && t in Object(e);
}
var L = It(Object, "create");
function gi() {
  this.__data__ = L ? L(null) : {}, this.size = 0;
}
function mi(t) {
  var e = this.has(t) && delete this.__data__[t];
  return this.size -= e ? 1 : 0, e;
}
var vi = "__lodash_hash_undefined__", xi = Object.prototype, bi = xi.hasOwnProperty;
function _i(t) {
  var e = this.__data__;
  if (L) {
    var n = e[t];
    return n === vi ? void 0 : n;
  }
  return bi.call(e, t) ? e[t] : void 0;
}
var wi = Object.prototype, Ai = wi.hasOwnProperty;
function Oi(t) {
  var e = this.__data__;
  return L ? e[t] !== void 0 : Ai.call(e, t);
}
var ji = "__lodash_hash_undefined__";
function Ii(t, e) {
  var n = this.__data__;
  return this.size += this.has(t) ? 0 : 1, n[t] = L && e === void 0 ? ji : e, this;
}
function C(t) {
  var e = -1, n = t == null ? 0 : t.length;
  for (this.clear(); ++e < n; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
C.prototype.clear = gi;
C.prototype.delete = mi;
C.prototype.get = _i;
C.prototype.has = Oi;
C.prototype.set = Ii;
function Si() {
  this.__data__ = [], this.size = 0;
}
function nt(t, e) {
  for (var n = t.length; n--; )
    if (be(t[n][0], e))
      return n;
  return -1;
}
var Ci = Array.prototype, Ei = Ci.splice;
function Mi(t) {
  var e = this.__data__, n = nt(e, t);
  if (n < 0)
    return !1;
  var r = e.length - 1;
  return n == r ? e.pop() : Ei.call(e, n, 1), --this.size, !0;
}
function Ti(t) {
  var e = this.__data__, n = nt(e, t);
  return n < 0 ? void 0 : e[n][1];
}
function $i(t) {
  return nt(this.__data__, t) > -1;
}
function zi(t, e) {
  var n = this.__data__, r = nt(n, t);
  return r < 0 ? (++this.size, n.push([t, e])) : n[r][1] = e, this;
}
function P(t) {
  var e = -1, n = t == null ? 0 : t.length;
  for (this.clear(); ++e < n; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
P.prototype.clear = Si;
P.prototype.delete = Mi;
P.prototype.get = Ti;
P.prototype.has = $i;
P.prototype.set = zi;
var Vi = It(At, "Map");
function Fi() {
  this.size = 0, this.__data__ = {
    hash: new C(),
    map: new (Vi || P)(),
    string: new C()
  };
}
function Pi(t) {
  var e = typeof t;
  return e == "string" || e == "number" || e == "symbol" || e == "boolean" ? t !== "__proto__" : t === null;
}
function rt(t, e) {
  var n = t.__data__;
  return Pi(e) ? n[typeof e == "string" ? "string" : "hash"] : n.map;
}
function Ni(t) {
  var e = rt(this, t).delete(t);
  return this.size -= e ? 1 : 0, e;
}
function Di(t) {
  return rt(this, t).get(t);
}
function Ri(t) {
  return rt(this, t).has(t);
}
function Wi(t, e) {
  var n = rt(this, t), r = n.size;
  return n.set(t, e), this.size += n.size == r ? 0 : 1, this;
}
function M(t) {
  var e = -1, n = t == null ? 0 : t.length;
  for (this.clear(); ++e < n; ) {
    var r = t[e];
    this.set(r[0], r[1]);
  }
}
M.prototype.clear = Fi;
M.prototype.delete = Ni;
M.prototype.get = Di;
M.prototype.has = Ri;
M.prototype.set = Wi;
var Li = "Expected a function";
function St(t, e) {
  if (typeof t != "function" || e != null && typeof e != "function")
    throw new TypeError(Li);
  var n = function() {
    var r = arguments, o = e ? e.apply(this, r) : r[0], i = n.cache;
    if (i.has(o))
      return i.get(o);
    var a = t.apply(this, r);
    return n.cache = i.set(o, a) || i, a;
  };
  return n.cache = new (St.Cache || M)(), n;
}
St.Cache = M;
var Xi = 500;
function Ui(t) {
  var e = St(t, function(r) {
    return n.size === Xi && n.clear(), r;
  }), n = e.cache;
  return e;
}
var Gi = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, Hi = /\\(\\)?/g, Bi = Ui(function(t) {
  var e = [];
  return t.charCodeAt(0) === 46 && e.push(""), t.replace(Gi, function(n, r, o, i) {
    e.push(o ? i.replace(Hi, "$1") : r || n);
  }), e;
});
function Yi(t) {
  return t == null ? "" : xe(t);
}
function Ki(t, e) {
  return jt(t) ? t : yi(t, e) ? [t] : Bi(Yi(t));
}
function Zi(t) {
  if (typeof t == "string" || Ot(t))
    return t;
  var e = t + "";
  return e == "0" && 1 / t == -1 / 0 ? "-0" : e;
}
function ki(t, e, n, r) {
  if (!k(t))
    return t;
  e = Ki(e, t);
  for (var o = -1, i = e.length, a = i - 1, s = t; s != null && ++o < i; ) {
    var c = Zi(e[o]), u = n;
    if (c === "__proto__" || c === "constructor" || c === "prototype")
      return t;
    if (o != a) {
      var l = s[c];
      u = void 0, u === void 0 && (u = k(l) ? l : ci(e[o + 1]) ? [] : {});
    }
    di(s, c, u), s = s[c];
  }
  return t;
}
function qi(t, e, n) {
  return t == null ? t : ki(t, e, n);
}
function Kt(t, e) {
  return qt.init(t, e.theme, e.initOptions);
}
function Ji(t, e, n) {
  kt(
    () => n.resizeOption,
    (r, o, i) => {
      let a = null;
      if (r) {
        const { offsetWidth: s, offsetHeight: c } = t, { throttle: u = 100 } = r;
        let l = !1;
        const f = () => {
          e.resize();
        }, d = u ? qt.throttle(f, u) : f;
        a = new ResizeObserver(() => {
          !l && (l = !0, t.offsetWidth === s && t.offsetHeight === c) || d();
        }), a.observe(t);
      }
      i(() => {
        a && (a.disconnect(), a = null);
      });
    },
    { deep: !0, immediate: !0 }
  );
}
function Zt(t, e, n) {
  t.setOption(n || {}, e.updateOptions || {});
}
function Qi(t, e, n) {
  const { chartEvents: r, zrEvents: o } = n;
  r && r.forEach((i) => {
    t.on(i, (...a) => {
      if (a.length > 0) {
        const s = a[0];
        delete s.event, delete s.$vars;
      }
      e(`chart:${i}`, ...a);
    });
  }), o && o.forEach((i) => {
    t.getZr().on(i, (...a) => e(`zr:${i}`, ...a));
  });
}
function ta(t) {
  const { getValue: e } = Te();
  return _e(() => {
    if (t.optionType === "dict")
      return t.option;
    const n = t.option;
    return n.refSets?.forEach((o) => {
      const { path: i, ref: a } = o;
      qi(n.grammar, i, e(a));
    }), So(n.grammar);
  });
}
const ra = /* @__PURE__ */ we({
  __name: "echarts",
  props: {
    option: {},
    optionType: {},
    theme: {},
    initOptions: {},
    resizeOption: {},
    updateOptions: {},
    chartEvents: {},
    zrEvents: {}
  },
  setup(t, { emit: e }) {
    const n = t, r = Ae("root"), o = Oe(), i = e, a = ta(n);
    je(() => {
      r.value && (o.value = Kt(r.value, n), Ji(r.value, o.value, n), Zt(o.value, n, a.value), Qi(o.value, i, n));
    }), kt(
      a,
      (c) => {
        !o.value && r.value && (o.value = Kt(r.value, n)), Zt(o.value, n, c);
      },
      { deep: !0 }
    );
    const s = Ie();
    return (c, u) => (Ce(), Se("div", Ee({ ref: "root" }, Me(s)), null, 16));
  }
});
export {
  ra as default
};
