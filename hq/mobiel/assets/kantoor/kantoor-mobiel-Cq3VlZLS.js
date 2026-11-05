function Sp(o) {
  return o && o.__esModule && Object.prototype.hasOwnProperty.call(o, "default") ? o.default : o;
}
var ga = { exports: {} }, Wr = {}, ha = { exports: {} }, Y = {};
/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Mc;
function _p() {
  if (Mc) return Y;
  Mc = 1;
  var o = Symbol.for("react.element"), s = Symbol.for("react.portal"), a = Symbol.for("react.fragment"), d = Symbol.for("react.strict_mode"), f = Symbol.for("react.profiler"), u = Symbol.for("react.provider"), p = Symbol.for("react.context"), m = Symbol.for("react.forward_ref"), h = Symbol.for("react.suspense"), E = Symbol.for("react.memo"), C = Symbol.for("react.lazy"), M = Symbol.iterator;
  function A(k) {
    return k === null || typeof k != "object" ? null : (k = M && k[M] || k["@@iterator"], typeof k == "function" ? k : null);
  }
  var $ = { isMounted: function() {
    return !1;
  }, enqueueForceUpdate: function() {
  }, enqueueReplaceState: function() {
  }, enqueueSetState: function() {
  } }, Q = Object.assign, b = {};
  function z(k, P, G) {
    this.props = k, this.context = P, this.refs = b, this.updater = G || $;
  }
  z.prototype.isReactComponent = {}, z.prototype.setState = function(k, P) {
    if (typeof k != "object" && typeof k != "function" && k != null) throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");
    this.updater.enqueueSetState(this, k, P, "setState");
  }, z.prototype.forceUpdate = function(k) {
    this.updater.enqueueForceUpdate(this, k, "forceUpdate");
  };
  function ie() {
  }
  ie.prototype = z.prototype;
  function ge(k, P, G) {
    this.props = k, this.context = P, this.refs = b, this.updater = G || $;
  }
  var fe = ge.prototype = new ie();
  fe.constructor = ge, Q(fe, z.prototype), fe.isPureReactComponent = !0;
  var q = Array.isArray, ae = Object.prototype.hasOwnProperty, _e = { current: null }, Re = { key: !0, ref: !0, __self: !0, __source: !0 };
  function nt(k, P, G) {
    var X, Z = {}, ee = null, oe = null;
    if (P != null) for (X in P.ref !== void 0 && (oe = P.ref), P.key !== void 0 && (ee = "" + P.key), P) ae.call(P, X) && !Re.hasOwnProperty(X) && (Z[X] = P[X]);
    var ne = arguments.length - 2;
    if (ne === 1) Z.children = G;
    else if (1 < ne) {
      for (var ce = Array(ne), Ye = 0; Ye < ne; Ye++) ce[Ye] = arguments[Ye + 2];
      Z.children = ce;
    }
    if (k && k.defaultProps) for (X in ne = k.defaultProps, ne) Z[X] === void 0 && (Z[X] = ne[X]);
    return { $$typeof: o, type: k, key: ee, ref: oe, props: Z, _owner: _e.current };
  }
  function Ut(k, P) {
    return { $$typeof: o, type: k.type, key: P, ref: k.ref, props: k.props, _owner: k._owner };
  }
  function xt(k) {
    return typeof k == "object" && k !== null && k.$$typeof === o;
  }
  function cn(k) {
    var P = { "=": "=0", ":": "=2" };
    return "$" + k.replace(/[=:]/g, function(G) {
      return P[G];
    });
  }
  var St = /\/+/g;
  function be(k, P) {
    return typeof k == "object" && k !== null && k.key != null ? cn("" + k.key) : P.toString(36);
  }
  function dt(k, P, G, X, Z) {
    var ee = typeof k;
    (ee === "undefined" || ee === "boolean") && (k = null);
    var oe = !1;
    if (k === null) oe = !0;
    else switch (ee) {
      case "string":
      case "number":
        oe = !0;
        break;
      case "object":
        switch (k.$$typeof) {
          case o:
          case s:
            oe = !0;
        }
    }
    if (oe) return oe = k, Z = Z(oe), k = X === "" ? "." + be(oe, 0) : X, q(Z) ? (G = "", k != null && (G = k.replace(St, "$&/") + "/"), dt(Z, P, G, "", function(Ye) {
      return Ye;
    })) : Z != null && (xt(Z) && (Z = Ut(Z, G + (!Z.key || oe && oe.key === Z.key ? "" : ("" + Z.key).replace(St, "$&/") + "/") + k)), P.push(Z)), 1;
    if (oe = 0, X = X === "" ? "." : X + ":", q(k)) for (var ne = 0; ne < k.length; ne++) {
      ee = k[ne];
      var ce = X + be(ee, ne);
      oe += dt(ee, P, G, ce, Z);
    }
    else if (ce = A(k), typeof ce == "function") for (k = ce.call(k), ne = 0; !(ee = k.next()).done; ) ee = ee.value, ce = X + be(ee, ne++), oe += dt(ee, P, G, ce, Z);
    else if (ee === "object") throw P = String(k), Error("Objects are not valid as a React child (found: " + (P === "[object Object]" ? "object with keys {" + Object.keys(k).join(", ") + "}" : P) + "). If you meant to render a collection of children, use an array instead.");
    return oe;
  }
  function _t(k, P, G) {
    if (k == null) return k;
    var X = [], Z = 0;
    return dt(k, X, "", "", function(ee) {
      return P.call(G, ee, Z++);
    }), X;
  }
  function Fe(k) {
    if (k._status === -1) {
      var P = k._result;
      P = P(), P.then(function(G) {
        (k._status === 0 || k._status === -1) && (k._status = 1, k._result = G);
      }, function(G) {
        (k._status === 0 || k._status === -1) && (k._status = 2, k._result = G);
      }), k._status === -1 && (k._status = 0, k._result = P);
    }
    if (k._status === 1) return k._result.default;
    throw k._result;
  }
  var he = { current: null }, R = { transition: null }, B = { ReactCurrentDispatcher: he, ReactCurrentBatchConfig: R, ReactCurrentOwner: _e };
  function O() {
    throw Error("act(...) is not supported in production builds of React.");
  }
  return Y.Children = { map: _t, forEach: function(k, P, G) {
    _t(k, function() {
      P.apply(this, arguments);
    }, G);
  }, count: function(k) {
    var P = 0;
    return _t(k, function() {
      P++;
    }), P;
  }, toArray: function(k) {
    return _t(k, function(P) {
      return P;
    }) || [];
  }, only: function(k) {
    if (!xt(k)) throw Error("React.Children.only expected to receive a single React element child.");
    return k;
  } }, Y.Component = z, Y.Fragment = a, Y.Profiler = f, Y.PureComponent = ge, Y.StrictMode = d, Y.Suspense = h, Y.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = B, Y.act = O, Y.cloneElement = function(k, P, G) {
    if (k == null) throw Error("React.cloneElement(...): The argument must be a React element, but you passed " + k + ".");
    var X = Q({}, k.props), Z = k.key, ee = k.ref, oe = k._owner;
    if (P != null) {
      if (P.ref !== void 0 && (ee = P.ref, oe = _e.current), P.key !== void 0 && (Z = "" + P.key), k.type && k.type.defaultProps) var ne = k.type.defaultProps;
      for (ce in P) ae.call(P, ce) && !Re.hasOwnProperty(ce) && (X[ce] = P[ce] === void 0 && ne !== void 0 ? ne[ce] : P[ce]);
    }
    var ce = arguments.length - 2;
    if (ce === 1) X.children = G;
    else if (1 < ce) {
      ne = Array(ce);
      for (var Ye = 0; Ye < ce; Ye++) ne[Ye] = arguments[Ye + 2];
      X.children = ne;
    }
    return { $$typeof: o, type: k.type, key: Z, ref: ee, props: X, _owner: oe };
  }, Y.createContext = function(k) {
    return k = { $$typeof: p, _currentValue: k, _currentValue2: k, _threadCount: 0, Provider: null, Consumer: null, _defaultValue: null, _globalName: null }, k.Provider = { $$typeof: u, _context: k }, k.Consumer = k;
  }, Y.createElement = nt, Y.createFactory = function(k) {
    var P = nt.bind(null, k);
    return P.type = k, P;
  }, Y.createRef = function() {
    return { current: null };
  }, Y.forwardRef = function(k) {
    return { $$typeof: m, render: k };
  }, Y.isValidElement = xt, Y.lazy = function(k) {
    return { $$typeof: C, _payload: { _status: -1, _result: k }, _init: Fe };
  }, Y.memo = function(k, P) {
    return { $$typeof: E, type: k, compare: P === void 0 ? null : P };
  }, Y.startTransition = function(k) {
    var P = R.transition;
    R.transition = {};
    try {
      k();
    } finally {
      R.transition = P;
    }
  }, Y.unstable_act = O, Y.useCallback = function(k, P) {
    return he.current.useCallback(k, P);
  }, Y.useContext = function(k) {
    return he.current.useContext(k);
  }, Y.useDebugValue = function() {
  }, Y.useDeferredValue = function(k) {
    return he.current.useDeferredValue(k);
  }, Y.useEffect = function(k, P) {
    return he.current.useEffect(k, P);
  }, Y.useId = function() {
    return he.current.useId();
  }, Y.useImperativeHandle = function(k, P, G) {
    return he.current.useImperativeHandle(k, P, G);
  }, Y.useInsertionEffect = function(k, P) {
    return he.current.useInsertionEffect(k, P);
  }, Y.useLayoutEffect = function(k, P) {
    return he.current.useLayoutEffect(k, P);
  }, Y.useMemo = function(k, P) {
    return he.current.useMemo(k, P);
  }, Y.useReducer = function(k, P, G) {
    return he.current.useReducer(k, P, G);
  }, Y.useRef = function(k) {
    return he.current.useRef(k);
  }, Y.useState = function(k) {
    return he.current.useState(k);
  }, Y.useSyncExternalStore = function(k, P, G) {
    return he.current.useSyncExternalStore(k, P, G);
  }, Y.useTransition = function() {
    return he.current.useTransition();
  }, Y.version = "18.3.1", Y;
}
var Lc;
function Ma() {
  return Lc || (Lc = 1, ha.exports = _p()), ha.exports;
}
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var $c;
function Ep() {
  if ($c) return Wr;
  $c = 1;
  var o = Ma(), s = Symbol.for("react.element"), a = Symbol.for("react.fragment"), d = Object.prototype.hasOwnProperty, f = o.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, u = { key: !0, ref: !0, __self: !0, __source: !0 };
  function p(m, h, E) {
    var C, M = {}, A = null, $ = null;
    E !== void 0 && (A = "" + E), h.key !== void 0 && (A = "" + h.key), h.ref !== void 0 && ($ = h.ref);
    for (C in h) d.call(h, C) && !u.hasOwnProperty(C) && (M[C] = h[C]);
    if (m && m.defaultProps) for (C in h = m.defaultProps, h) M[C] === void 0 && (M[C] = h[C]);
    return { $$typeof: s, type: m, key: A, ref: $, props: M, _owner: f.current };
  }
  return Wr.Fragment = a, Wr.jsx = p, Wr.jsxs = p, Wr;
}
var Fc;
function Cp() {
  return Fc || (Fc = 1, ga.exports = Ep()), ga.exports;
}
var so = Cp(), mo = Ma();
const va = /* @__PURE__ */ Sp(mo);
var uo = {}, ya = { exports: {} }, Ke = {}, ka = { exports: {} }, wa = {};
/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Uc;
function Tp() {
  return Uc || (Uc = 1, (function(o) {
    function s(R, B) {
      var O = R.length;
      R.push(B);
      e: for (; 0 < O; ) {
        var k = O - 1 >>> 1, P = R[k];
        if (0 < f(P, B)) R[k] = B, R[O] = P, O = k;
        else break e;
      }
    }
    function a(R) {
      return R.length === 0 ? null : R[0];
    }
    function d(R) {
      if (R.length === 0) return null;
      var B = R[0], O = R.pop();
      if (O !== B) {
        R[0] = O;
        e: for (var k = 0, P = R.length, G = P >>> 1; k < G; ) {
          var X = 2 * (k + 1) - 1, Z = R[X], ee = X + 1, oe = R[ee];
          if (0 > f(Z, O)) ee < P && 0 > f(oe, Z) ? (R[k] = oe, R[ee] = O, k = ee) : (R[k] = Z, R[X] = O, k = X);
          else if (ee < P && 0 > f(oe, O)) R[k] = oe, R[ee] = O, k = ee;
          else break e;
        }
      }
      return B;
    }
    function f(R, B) {
      var O = R.sortIndex - B.sortIndex;
      return O !== 0 ? O : R.id - B.id;
    }
    if (typeof performance == "object" && typeof performance.now == "function") {
      var u = performance;
      o.unstable_now = function() {
        return u.now();
      };
    } else {
      var p = Date, m = p.now();
      o.unstable_now = function() {
        return p.now() - m;
      };
    }
    var h = [], E = [], C = 1, M = null, A = 3, $ = !1, Q = !1, b = !1, z = typeof setTimeout == "function" ? setTimeout : null, ie = typeof clearTimeout == "function" ? clearTimeout : null, ge = typeof setImmediate < "u" ? setImmediate : null;
    typeof navigator < "u" && navigator.scheduling !== void 0 && navigator.scheduling.isInputPending !== void 0 && navigator.scheduling.isInputPending.bind(navigator.scheduling);
    function fe(R) {
      for (var B = a(E); B !== null; ) {
        if (B.callback === null) d(E);
        else if (B.startTime <= R) d(E), B.sortIndex = B.expirationTime, s(h, B);
        else break;
        B = a(E);
      }
    }
    function q(R) {
      if (b = !1, fe(R), !Q) if (a(h) !== null) Q = !0, Fe(ae);
      else {
        var B = a(E);
        B !== null && he(q, B.startTime - R);
      }
    }
    function ae(R, B) {
      Q = !1, b && (b = !1, ie(nt), nt = -1), $ = !0;
      var O = A;
      try {
        for (fe(B), M = a(h); M !== null && (!(M.expirationTime > B) || R && !cn()); ) {
          var k = M.callback;
          if (typeof k == "function") {
            M.callback = null, A = M.priorityLevel;
            var P = k(M.expirationTime <= B);
            B = o.unstable_now(), typeof P == "function" ? M.callback = P : M === a(h) && d(h), fe(B);
          } else d(h);
          M = a(h);
        }
        if (M !== null) var G = !0;
        else {
          var X = a(E);
          X !== null && he(q, X.startTime - B), G = !1;
        }
        return G;
      } finally {
        M = null, A = O, $ = !1;
      }
    }
    var _e = !1, Re = null, nt = -1, Ut = 5, xt = -1;
    function cn() {
      return !(o.unstable_now() - xt < Ut);
    }
    function St() {
      if (Re !== null) {
        var R = o.unstable_now();
        xt = R;
        var B = !0;
        try {
          B = Re(!0, R);
        } finally {
          B ? be() : (_e = !1, Re = null);
        }
      } else _e = !1;
    }
    var be;
    if (typeof ge == "function") be = function() {
      ge(St);
    };
    else if (typeof MessageChannel < "u") {
      var dt = new MessageChannel(), _t = dt.port2;
      dt.port1.onmessage = St, be = function() {
        _t.postMessage(null);
      };
    } else be = function() {
      z(St, 0);
    };
    function Fe(R) {
      Re = R, _e || (_e = !0, be());
    }
    function he(R, B) {
      nt = z(function() {
        R(o.unstable_now());
      }, B);
    }
    o.unstable_IdlePriority = 5, o.unstable_ImmediatePriority = 1, o.unstable_LowPriority = 4, o.unstable_NormalPriority = 3, o.unstable_Profiling = null, o.unstable_UserBlockingPriority = 2, o.unstable_cancelCallback = function(R) {
      R.callback = null;
    }, o.unstable_continueExecution = function() {
      Q || $ || (Q = !0, Fe(ae));
    }, o.unstable_forceFrameRate = function(R) {
      0 > R || 125 < R ? console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported") : Ut = 0 < R ? Math.floor(1e3 / R) : 5;
    }, o.unstable_getCurrentPriorityLevel = function() {
      return A;
    }, o.unstable_getFirstCallbackNode = function() {
      return a(h);
    }, o.unstable_next = function(R) {
      switch (A) {
        case 1:
        case 2:
        case 3:
          var B = 3;
          break;
        default:
          B = A;
      }
      var O = A;
      A = B;
      try {
        return R();
      } finally {
        A = O;
      }
    }, o.unstable_pauseExecution = function() {
    }, o.unstable_requestPaint = function() {
    }, o.unstable_runWithPriority = function(R, B) {
      switch (R) {
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
          break;
        default:
          R = 3;
      }
      var O = A;
      A = R;
      try {
        return B();
      } finally {
        A = O;
      }
    }, o.unstable_scheduleCallback = function(R, B, O) {
      var k = o.unstable_now();
      switch (typeof O == "object" && O !== null ? (O = O.delay, O = typeof O == "number" && 0 < O ? k + O : k) : O = k, R) {
        case 1:
          var P = -1;
          break;
        case 2:
          P = 250;
          break;
        case 5:
          P = 1073741823;
          break;
        case 4:
          P = 1e4;
          break;
        default:
          P = 5e3;
      }
      return P = O + P, R = { id: C++, callback: B, priorityLevel: R, startTime: O, expirationTime: P, sortIndex: -1 }, O > k ? (R.sortIndex = O, s(E, R), a(h) === null && R === a(E) && (b ? (ie(nt), nt = -1) : b = !0, he(q, O - k))) : (R.sortIndex = P, s(h, R), Q || $ || (Q = !0, Fe(ae))), R;
    }, o.unstable_shouldYield = cn, o.unstable_wrapCallback = function(R) {
      var B = A;
      return function() {
        var O = A;
        A = B;
        try {
          return R.apply(this, arguments);
        } finally {
          A = O;
        }
      };
    };
  })(wa)), wa;
}
var Vc;
function Pp() {
  return Vc || (Vc = 1, ka.exports = Tp()), ka.exports;
}
/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Wc;
function jp() {
  if (Wc) return Ke;
  Wc = 1;
  var o = Ma(), s = Pp();
  function a(e) {
    for (var t = "https://reactjs.org/docs/error-decoder.html?invariant=" + e, n = 1; n < arguments.length; n++) t += "&args[]=" + encodeURIComponent(arguments[n]);
    return "Minified React error #" + e + "; visit " + t + " for the full message or use the non-minified dev environment for full errors and additional helpful warnings.";
  }
  var d = /* @__PURE__ */ new Set(), f = {};
  function u(e, t) {
    p(e, t), p(e + "Capture", t);
  }
  function p(e, t) {
    for (f[e] = t, e = 0; e < t.length; e++) d.add(t[e]);
  }
  var m = !(typeof window > "u" || typeof window.document > "u" || typeof window.document.createElement > "u"), h = Object.prototype.hasOwnProperty, E = /^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/, C = {}, M = {};
  function A(e) {
    return h.call(M, e) ? !0 : h.call(C, e) ? !1 : E.test(e) ? M[e] = !0 : (C[e] = !0, !1);
  }
  function $(e, t, n, r) {
    if (n !== null && n.type === 0) return !1;
    switch (typeof t) {
      case "function":
      case "symbol":
        return !0;
      case "boolean":
        return r ? !1 : n !== null ? !n.acceptsBooleans : (e = e.toLowerCase().slice(0, 5), e !== "data-" && e !== "aria-");
      default:
        return !1;
    }
  }
  function Q(e, t, n, r) {
    if (t === null || typeof t > "u" || $(e, t, n, r)) return !0;
    if (r) return !1;
    if (n !== null) switch (n.type) {
      case 3:
        return !t;
      case 4:
        return t === !1;
      case 5:
        return isNaN(t);
      case 6:
        return isNaN(t) || 1 > t;
    }
    return !1;
  }
  function b(e, t, n, r, i, l, c) {
    this.acceptsBooleans = t === 2 || t === 3 || t === 4, this.attributeName = r, this.attributeNamespace = i, this.mustUseProperty = n, this.propertyName = e, this.type = t, this.sanitizeURL = l, this.removeEmptyString = c;
  }
  var z = {};
  "children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(e) {
    z[e] = new b(e, 0, !1, e, null, !1, !1);
  }), [["acceptCharset", "accept-charset"], ["className", "class"], ["htmlFor", "for"], ["httpEquiv", "http-equiv"]].forEach(function(e) {
    var t = e[0];
    z[t] = new b(t, 1, !1, e[1], null, !1, !1);
  }), ["contentEditable", "draggable", "spellCheck", "value"].forEach(function(e) {
    z[e] = new b(e, 2, !1, e.toLowerCase(), null, !1, !1);
  }), ["autoReverse", "externalResourcesRequired", "focusable", "preserveAlpha"].forEach(function(e) {
    z[e] = new b(e, 2, !1, e, null, !1, !1);
  }), "allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(e) {
    z[e] = new b(e, 3, !1, e.toLowerCase(), null, !1, !1);
  }), ["checked", "multiple", "muted", "selected"].forEach(function(e) {
    z[e] = new b(e, 3, !0, e, null, !1, !1);
  }), ["capture", "download"].forEach(function(e) {
    z[e] = new b(e, 4, !1, e, null, !1, !1);
  }), ["cols", "rows", "size", "span"].forEach(function(e) {
    z[e] = new b(e, 6, !1, e, null, !1, !1);
  }), ["rowSpan", "start"].forEach(function(e) {
    z[e] = new b(e, 5, !1, e.toLowerCase(), null, !1, !1);
  });
  var ie = /[\-:]([a-z])/g;
  function ge(e) {
    return e[1].toUpperCase();
  }
  "accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(e) {
    var t = e.replace(
      ie,
      ge
    );
    z[t] = new b(t, 1, !1, e, null, !1, !1);
  }), "xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(e) {
    var t = e.replace(ie, ge);
    z[t] = new b(t, 1, !1, e, "http://www.w3.org/1999/xlink", !1, !1);
  }), ["xml:base", "xml:lang", "xml:space"].forEach(function(e) {
    var t = e.replace(ie, ge);
    z[t] = new b(t, 1, !1, e, "http://www.w3.org/XML/1998/namespace", !1, !1);
  }), ["tabIndex", "crossOrigin"].forEach(function(e) {
    z[e] = new b(e, 1, !1, e.toLowerCase(), null, !1, !1);
  }), z.xlinkHref = new b("xlinkHref", 1, !1, "xlink:href", "http://www.w3.org/1999/xlink", !0, !1), ["src", "href", "action", "formAction"].forEach(function(e) {
    z[e] = new b(e, 1, !1, e.toLowerCase(), null, !0, !0);
  });
  function fe(e, t, n, r) {
    var i = z.hasOwnProperty(t) ? z[t] : null;
    (i !== null ? i.type !== 0 : r || !(2 < t.length) || t[0] !== "o" && t[0] !== "O" || t[1] !== "n" && t[1] !== "N") && (Q(t, n, i, r) && (n = null), r || i === null ? A(t) && (n === null ? e.removeAttribute(t) : e.setAttribute(t, "" + n)) : i.mustUseProperty ? e[i.propertyName] = n === null ? i.type === 3 ? !1 : "" : n : (t = i.attributeName, r = i.attributeNamespace, n === null ? e.removeAttribute(t) : (i = i.type, n = i === 3 || i === 4 && n === !0 ? "" : "" + n, r ? e.setAttributeNS(r, t, n) : e.setAttribute(t, n))));
  }
  var q = o.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED, ae = Symbol.for("react.element"), _e = Symbol.for("react.portal"), Re = Symbol.for("react.fragment"), nt = Symbol.for("react.strict_mode"), Ut = Symbol.for("react.profiler"), xt = Symbol.for("react.provider"), cn = Symbol.for("react.context"), St = Symbol.for("react.forward_ref"), be = Symbol.for("react.suspense"), dt = Symbol.for("react.suspense_list"), _t = Symbol.for("react.memo"), Fe = Symbol.for("react.lazy"), he = Symbol.for("react.offscreen"), R = Symbol.iterator;
  function B(e) {
    return e === null || typeof e != "object" ? null : (e = R && e[R] || e["@@iterator"], typeof e == "function" ? e : null);
  }
  var O = Object.assign, k;
  function P(e) {
    if (k === void 0) try {
      throw Error();
    } catch (n) {
      var t = n.stack.trim().match(/\n( *(at )?)/);
      k = t && t[1] || "";
    }
    return `
` + k + e;
  }
  var G = !1;
  function X(e, t) {
    if (!e || G) return "";
    G = !0;
    var n = Error.prepareStackTrace;
    Error.prepareStackTrace = void 0;
    try {
      if (t) if (t = function() {
        throw Error();
      }, Object.defineProperty(t.prototype, "props", { set: function() {
        throw Error();
      } }), typeof Reflect == "object" && Reflect.construct) {
        try {
          Reflect.construct(t, []);
        } catch (_) {
          var r = _;
        }
        Reflect.construct(e, [], t);
      } else {
        try {
          t.call();
        } catch (_) {
          r = _;
        }
        e.call(t.prototype);
      }
      else {
        try {
          throw Error();
        } catch (_) {
          r = _;
        }
        e();
      }
    } catch (_) {
      if (_ && r && typeof _.stack == "string") {
        for (var i = _.stack.split(`
`), l = r.stack.split(`
`), c = i.length - 1, g = l.length - 1; 1 <= c && 0 <= g && i[c] !== l[g]; ) g--;
        for (; 1 <= c && 0 <= g; c--, g--) if (i[c] !== l[g]) {
          if (c !== 1 || g !== 1)
            do
              if (c--, g--, 0 > g || i[c] !== l[g]) {
                var v = `
` + i[c].replace(" at new ", " at ");
                return e.displayName && v.includes("<anonymous>") && (v = v.replace("<anonymous>", e.displayName)), v;
              }
            while (1 <= c && 0 <= g);
          break;
        }
      }
    } finally {
      G = !1, Error.prepareStackTrace = n;
    }
    return (e = e ? e.displayName || e.name : "") ? P(e) : "";
  }
  function Z(e) {
    switch (e.tag) {
      case 5:
        return P(e.type);
      case 16:
        return P("Lazy");
      case 13:
        return P("Suspense");
      case 19:
        return P("SuspenseList");
      case 0:
      case 2:
      case 15:
        return e = X(e.type, !1), e;
      case 11:
        return e = X(e.type.render, !1), e;
      case 1:
        return e = X(e.type, !0), e;
      default:
        return "";
    }
  }
  function ee(e) {
    if (e == null) return null;
    if (typeof e == "function") return e.displayName || e.name || null;
    if (typeof e == "string") return e;
    switch (e) {
      case Re:
        return "Fragment";
      case _e:
        return "Portal";
      case Ut:
        return "Profiler";
      case nt:
        return "StrictMode";
      case be:
        return "Suspense";
      case dt:
        return "SuspenseList";
    }
    if (typeof e == "object") switch (e.$$typeof) {
      case cn:
        return (e.displayName || "Context") + ".Consumer";
      case xt:
        return (e._context.displayName || "Context") + ".Provider";
      case St:
        var t = e.render;
        return e = e.displayName, e || (e = t.displayName || t.name || "", e = e !== "" ? "ForwardRef(" + e + ")" : "ForwardRef"), e;
      case _t:
        return t = e.displayName || null, t !== null ? t : ee(e.type) || "Memo";
      case Fe:
        t = e._payload, e = e._init;
        try {
          return ee(e(t));
        } catch {
        }
    }
    return null;
  }
  function oe(e) {
    var t = e.type;
    switch (e.tag) {
      case 24:
        return "Cache";
      case 9:
        return (t.displayName || "Context") + ".Consumer";
      case 10:
        return (t._context.displayName || "Context") + ".Provider";
      case 18:
        return "DehydratedFragment";
      case 11:
        return e = t.render, e = e.displayName || e.name || "", t.displayName || (e !== "" ? "ForwardRef(" + e + ")" : "ForwardRef");
      case 7:
        return "Fragment";
      case 5:
        return t;
      case 4:
        return "Portal";
      case 3:
        return "Root";
      case 6:
        return "Text";
      case 16:
        return ee(t);
      case 8:
        return t === nt ? "StrictMode" : "Mode";
      case 22:
        return "Offscreen";
      case 12:
        return "Profiler";
      case 21:
        return "Scope";
      case 13:
        return "Suspense";
      case 19:
        return "SuspenseList";
      case 25:
        return "TracingMarker";
      case 1:
      case 0:
      case 17:
      case 2:
      case 14:
      case 15:
        if (typeof t == "function") return t.displayName || t.name || null;
        if (typeof t == "string") return t;
    }
    return null;
  }
  function ne(e) {
    switch (typeof e) {
      case "boolean":
      case "number":
      case "string":
      case "undefined":
        return e;
      case "object":
        return e;
      default:
        return "";
    }
  }
  function ce(e) {
    var t = e.type;
    return (e = e.nodeName) && e.toLowerCase() === "input" && (t === "checkbox" || t === "radio");
  }
  function Ye(e) {
    var t = ce(e) ? "checked" : "value", n = Object.getOwnPropertyDescriptor(e.constructor.prototype, t), r = "" + e[t];
    if (!e.hasOwnProperty(t) && typeof n < "u" && typeof n.get == "function" && typeof n.set == "function") {
      var i = n.get, l = n.set;
      return Object.defineProperty(e, t, { configurable: !0, get: function() {
        return i.call(this);
      }, set: function(c) {
        r = "" + c, l.call(this, c);
      } }), Object.defineProperty(e, t, { enumerable: n.enumerable }), { getValue: function() {
        return r;
      }, setValue: function(c) {
        r = "" + c;
      }, stopTracking: function() {
        e._valueTracker = null, delete e[t];
      } };
    }
  }
  function Jr(e) {
    e._valueTracker || (e._valueTracker = Ye(e));
  }
  function Wa(e) {
    if (!e) return !1;
    var t = e._valueTracker;
    if (!t) return !0;
    var n = t.getValue(), r = "";
    return e && (r = ce(e) ? e.checked ? "true" : "false" : e.value), e = r, e !== n ? (t.setValue(e), !0) : !1;
  }
  function Zr(e) {
    if (e = e || (typeof document < "u" ? document : void 0), typeof e > "u") return null;
    try {
      return e.activeElement || e.body;
    } catch {
      return e.body;
    }
  }
  function _o(e, t) {
    var n = t.checked;
    return O({}, t, { defaultChecked: void 0, defaultValue: void 0, value: void 0, checked: n ?? e._wrapperState.initialChecked });
  }
  function Ha(e, t) {
    var n = t.defaultValue == null ? "" : t.defaultValue, r = t.checked != null ? t.checked : t.defaultChecked;
    n = ne(t.value != null ? t.value : n), e._wrapperState = { initialChecked: r, initialValue: n, controlled: t.type === "checkbox" || t.type === "radio" ? t.checked != null : t.value != null };
  }
  function Ba(e, t) {
    t = t.checked, t != null && fe(e, "checked", t, !1);
  }
  function Eo(e, t) {
    Ba(e, t);
    var n = ne(t.value), r = t.type;
    if (n != null) r === "number" ? (n === 0 && e.value === "" || e.value != n) && (e.value = "" + n) : e.value !== "" + n && (e.value = "" + n);
    else if (r === "submit" || r === "reset") {
      e.removeAttribute("value");
      return;
    }
    t.hasOwnProperty("value") ? Co(e, t.type, n) : t.hasOwnProperty("defaultValue") && Co(e, t.type, ne(t.defaultValue)), t.checked == null && t.defaultChecked != null && (e.defaultChecked = !!t.defaultChecked);
  }
  function Ka(e, t, n) {
    if (t.hasOwnProperty("value") || t.hasOwnProperty("defaultValue")) {
      var r = t.type;
      if (!(r !== "submit" && r !== "reset" || t.value !== void 0 && t.value !== null)) return;
      t = "" + e._wrapperState.initialValue, n || t === e.value || (e.value = t), e.defaultValue = t;
    }
    n = e.name, n !== "" && (e.name = ""), e.defaultChecked = !!e._wrapperState.initialChecked, n !== "" && (e.name = n);
  }
  function Co(e, t, n) {
    (t !== "number" || Zr(e.ownerDocument) !== e) && (n == null ? e.defaultValue = "" + e._wrapperState.initialValue : e.defaultValue !== "" + n && (e.defaultValue = "" + n));
  }
  var rr = Array.isArray;
  function xn(e, t, n, r) {
    if (e = e.options, t) {
      t = {};
      for (var i = 0; i < n.length; i++) t["$" + n[i]] = !0;
      for (n = 0; n < e.length; n++) i = t.hasOwnProperty("$" + e[n].value), e[n].selected !== i && (e[n].selected = i), i && r && (e[n].defaultSelected = !0);
    } else {
      for (n = "" + ne(n), t = null, i = 0; i < e.length; i++) {
        if (e[i].value === n) {
          e[i].selected = !0, r && (e[i].defaultSelected = !0);
          return;
        }
        t !== null || e[i].disabled || (t = e[i]);
      }
      t !== null && (t.selected = !0);
    }
  }
  function To(e, t) {
    if (t.dangerouslySetInnerHTML != null) throw Error(a(91));
    return O({}, t, { value: void 0, defaultValue: void 0, children: "" + e._wrapperState.initialValue });
  }
  function Ga(e, t) {
    var n = t.value;
    if (n == null) {
      if (n = t.children, t = t.defaultValue, n != null) {
        if (t != null) throw Error(a(92));
        if (rr(n)) {
          if (1 < n.length) throw Error(a(93));
          n = n[0];
        }
        t = n;
      }
      t == null && (t = ""), n = t;
    }
    e._wrapperState = { initialValue: ne(n) };
  }
  function Qa(e, t) {
    var n = ne(t.value), r = ne(t.defaultValue);
    n != null && (n = "" + n, n !== e.value && (e.value = n), t.defaultValue == null && e.defaultValue !== n && (e.defaultValue = n)), r != null && (e.defaultValue = "" + r);
  }
  function ba(e) {
    var t = e.textContent;
    t === e._wrapperState.initialValue && t !== "" && t !== null && (e.value = t);
  }
  function Ya(e) {
    switch (e) {
      case "svg":
        return "http://www.w3.org/2000/svg";
      case "math":
        return "http://www.w3.org/1998/Math/MathML";
      default:
        return "http://www.w3.org/1999/xhtml";
    }
  }
  function Po(e, t) {
    return e == null || e === "http://www.w3.org/1999/xhtml" ? Ya(t) : e === "http://www.w3.org/2000/svg" && t === "foreignObject" ? "http://www.w3.org/1999/xhtml" : e;
  }
  var ei, Xa = (function(e) {
    return typeof MSApp < "u" && MSApp.execUnsafeLocalFunction ? function(t, n, r, i) {
      MSApp.execUnsafeLocalFunction(function() {
        return e(t, n, r, i);
      });
    } : e;
  })(function(e, t) {
    if (e.namespaceURI !== "http://www.w3.org/2000/svg" || "innerHTML" in e) e.innerHTML = t;
    else {
      for (ei = ei || document.createElement("div"), ei.innerHTML = "<svg>" + t.valueOf().toString() + "</svg>", t = ei.firstChild; e.firstChild; ) e.removeChild(e.firstChild);
      for (; t.firstChild; ) e.appendChild(t.firstChild);
    }
  });
  function ir(e, t) {
    if (t) {
      var n = e.firstChild;
      if (n && n === e.lastChild && n.nodeType === 3) {
        n.nodeValue = t;
        return;
      }
    }
    e.textContent = t;
  }
  var or = {
    animationIterationCount: !0,
    aspectRatio: !0,
    borderImageOutset: !0,
    borderImageSlice: !0,
    borderImageWidth: !0,
    boxFlex: !0,
    boxFlexGroup: !0,
    boxOrdinalGroup: !0,
    columnCount: !0,
    columns: !0,
    flex: !0,
    flexGrow: !0,
    flexPositive: !0,
    flexShrink: !0,
    flexNegative: !0,
    flexOrder: !0,
    gridArea: !0,
    gridRow: !0,
    gridRowEnd: !0,
    gridRowSpan: !0,
    gridRowStart: !0,
    gridColumn: !0,
    gridColumnEnd: !0,
    gridColumnSpan: !0,
    gridColumnStart: !0,
    fontWeight: !0,
    lineClamp: !0,
    lineHeight: !0,
    opacity: !0,
    order: !0,
    orphans: !0,
    tabSize: !0,
    widows: !0,
    zIndex: !0,
    zoom: !0,
    fillOpacity: !0,
    floodOpacity: !0,
    stopOpacity: !0,
    strokeDasharray: !0,
    strokeDashoffset: !0,
    strokeMiterlimit: !0,
    strokeOpacity: !0,
    strokeWidth: !0
  }, Cd = ["Webkit", "ms", "Moz", "O"];
  Object.keys(or).forEach(function(e) {
    Cd.forEach(function(t) {
      t = t + e.charAt(0).toUpperCase() + e.substring(1), or[t] = or[e];
    });
  });
  function qa(e, t, n) {
    return t == null || typeof t == "boolean" || t === "" ? "" : n || typeof t != "number" || t === 0 || or.hasOwnProperty(e) && or[e] ? ("" + t).trim() : t + "px";
  }
  function Ja(e, t) {
    e = e.style;
    for (var n in t) if (t.hasOwnProperty(n)) {
      var r = n.indexOf("--") === 0, i = qa(n, t[n], r);
      n === "float" && (n = "cssFloat"), r ? e.setProperty(n, i) : e[n] = i;
    }
  }
  var Td = O({ menuitem: !0 }, { area: !0, base: !0, br: !0, col: !0, embed: !0, hr: !0, img: !0, input: !0, keygen: !0, link: !0, meta: !0, param: !0, source: !0, track: !0, wbr: !0 });
  function jo(e, t) {
    if (t) {
      if (Td[e] && (t.children != null || t.dangerouslySetInnerHTML != null)) throw Error(a(137, e));
      if (t.dangerouslySetInnerHTML != null) {
        if (t.children != null) throw Error(a(60));
        if (typeof t.dangerouslySetInnerHTML != "object" || !("__html" in t.dangerouslySetInnerHTML)) throw Error(a(61));
      }
      if (t.style != null && typeof t.style != "object") throw Error(a(62));
    }
  }
  function Io(e, t) {
    if (e.indexOf("-") === -1) return typeof t.is == "string";
    switch (e) {
      case "annotation-xml":
      case "color-profile":
      case "font-face":
      case "font-face-src":
      case "font-face-uri":
      case "font-face-format":
      case "font-face-name":
      case "missing-glyph":
        return !1;
      default:
        return !0;
    }
  }
  var xo = null;
  function Ao(e) {
    return e = e.target || e.srcElement || window, e.correspondingUseElement && (e = e.correspondingUseElement), e.nodeType === 3 ? e.parentNode : e;
  }
  var Ro = null, An = null, Rn = null;
  function Za(e) {
    if (e = jr(e)) {
      if (typeof Ro != "function") throw Error(a(280));
      var t = e.stateNode;
      t && (t = Ei(t), Ro(e.stateNode, e.type, t));
    }
  }
  function es(e) {
    An ? Rn ? Rn.push(e) : Rn = [e] : An = e;
  }
  function ts() {
    if (An) {
      var e = An, t = Rn;
      if (Rn = An = null, Za(e), t) for (e = 0; e < t.length; e++) Za(t[e]);
    }
  }
  function ns(e, t) {
    return e(t);
  }
  function rs() {
  }
  var Do = !1;
  function is(e, t, n) {
    if (Do) return e(t, n);
    Do = !0;
    try {
      return ns(e, t, n);
    } finally {
      Do = !1, (An !== null || Rn !== null) && (rs(), ts());
    }
  }
  function lr(e, t) {
    var n = e.stateNode;
    if (n === null) return null;
    var r = Ei(n);
    if (r === null) return null;
    n = r[t];
    e: switch (t) {
      case "onClick":
      case "onClickCapture":
      case "onDoubleClick":
      case "onDoubleClickCapture":
      case "onMouseDown":
      case "onMouseDownCapture":
      case "onMouseMove":
      case "onMouseMoveCapture":
      case "onMouseUp":
      case "onMouseUpCapture":
      case "onMouseEnter":
        (r = !r.disabled) || (e = e.type, r = !(e === "button" || e === "input" || e === "select" || e === "textarea")), e = !r;
        break e;
      default:
        e = !1;
    }
    if (e) return null;
    if (n && typeof n != "function") throw Error(a(231, t, typeof n));
    return n;
  }
  var No = !1;
  if (m) try {
    var ar = {};
    Object.defineProperty(ar, "passive", { get: function() {
      No = !0;
    } }), window.addEventListener("test", ar, ar), window.removeEventListener("test", ar, ar);
  } catch {
    No = !1;
  }
  function Pd(e, t, n, r, i, l, c, g, v) {
    var _ = Array.prototype.slice.call(arguments, 3);
    try {
      t.apply(n, _);
    } catch (j) {
      this.onError(j);
    }
  }
  var sr = !1, ti = null, ni = !1, zo = null, jd = { onError: function(e) {
    sr = !0, ti = e;
  } };
  function Id(e, t, n, r, i, l, c, g, v) {
    sr = !1, ti = null, Pd.apply(jd, arguments);
  }
  function xd(e, t, n, r, i, l, c, g, v) {
    if (Id.apply(this, arguments), sr) {
      if (sr) {
        var _ = ti;
        sr = !1, ti = null;
      } else throw Error(a(198));
      ni || (ni = !0, zo = _);
    }
  }
  function dn(e) {
    var t = e, n = e;
    if (e.alternate) for (; t.return; ) t = t.return;
    else {
      e = t;
      do
        t = e, (t.flags & 4098) !== 0 && (n = t.return), e = t.return;
      while (e);
    }
    return t.tag === 3 ? n : null;
  }
  function os(e) {
    if (e.tag === 13) {
      var t = e.memoizedState;
      if (t === null && (e = e.alternate, e !== null && (t = e.memoizedState)), t !== null) return t.dehydrated;
    }
    return null;
  }
  function ls(e) {
    if (dn(e) !== e) throw Error(a(188));
  }
  function Ad(e) {
    var t = e.alternate;
    if (!t) {
      if (t = dn(e), t === null) throw Error(a(188));
      return t !== e ? null : e;
    }
    for (var n = e, r = t; ; ) {
      var i = n.return;
      if (i === null) break;
      var l = i.alternate;
      if (l === null) {
        if (r = i.return, r !== null) {
          n = r;
          continue;
        }
        break;
      }
      if (i.child === l.child) {
        for (l = i.child; l; ) {
          if (l === n) return ls(i), e;
          if (l === r) return ls(i), t;
          l = l.sibling;
        }
        throw Error(a(188));
      }
      if (n.return !== r.return) n = i, r = l;
      else {
        for (var c = !1, g = i.child; g; ) {
          if (g === n) {
            c = !0, n = i, r = l;
            break;
          }
          if (g === r) {
            c = !0, r = i, n = l;
            break;
          }
          g = g.sibling;
        }
        if (!c) {
          for (g = l.child; g; ) {
            if (g === n) {
              c = !0, n = l, r = i;
              break;
            }
            if (g === r) {
              c = !0, r = l, n = i;
              break;
            }
            g = g.sibling;
          }
          if (!c) throw Error(a(189));
        }
      }
      if (n.alternate !== r) throw Error(a(190));
    }
    if (n.tag !== 3) throw Error(a(188));
    return n.stateNode.current === n ? e : t;
  }
  function as(e) {
    return e = Ad(e), e !== null ? ss(e) : null;
  }
  function ss(e) {
    if (e.tag === 5 || e.tag === 6) return e;
    for (e = e.child; e !== null; ) {
      var t = ss(e);
      if (t !== null) return t;
      e = e.sibling;
    }
    return null;
  }
  var us = s.unstable_scheduleCallback, cs = s.unstable_cancelCallback, Rd = s.unstable_shouldYield, Dd = s.unstable_requestPaint, ye = s.unstable_now, Nd = s.unstable_getCurrentPriorityLevel, Oo = s.unstable_ImmediatePriority, ds = s.unstable_UserBlockingPriority, ri = s.unstable_NormalPriority, zd = s.unstable_LowPriority, fs = s.unstable_IdlePriority, ii = null, Et = null;
  function Od(e) {
    if (Et && typeof Et.onCommitFiberRoot == "function") try {
      Et.onCommitFiberRoot(ii, e, void 0, (e.current.flags & 128) === 128);
    } catch {
    }
  }
  var ft = Math.clz32 ? Math.clz32 : $d, Md = Math.log, Ld = Math.LN2;
  function $d(e) {
    return e >>>= 0, e === 0 ? 32 : 31 - (Md(e) / Ld | 0) | 0;
  }
  var oi = 64, li = 4194304;
  function ur(e) {
    switch (e & -e) {
      case 1:
        return 1;
      case 2:
        return 2;
      case 4:
        return 4;
      case 8:
        return 8;
      case 16:
        return 16;
      case 32:
        return 32;
      case 64:
      case 128:
      case 256:
      case 512:
      case 1024:
      case 2048:
      case 4096:
      case 8192:
      case 16384:
      case 32768:
      case 65536:
      case 131072:
      case 262144:
      case 524288:
      case 1048576:
      case 2097152:
        return e & 4194240;
      case 4194304:
      case 8388608:
      case 16777216:
      case 33554432:
      case 67108864:
        return e & 130023424;
      case 134217728:
        return 134217728;
      case 268435456:
        return 268435456;
      case 536870912:
        return 536870912;
      case 1073741824:
        return 1073741824;
      default:
        return e;
    }
  }
  function ai(e, t) {
    var n = e.pendingLanes;
    if (n === 0) return 0;
    var r = 0, i = e.suspendedLanes, l = e.pingedLanes, c = n & 268435455;
    if (c !== 0) {
      var g = c & ~i;
      g !== 0 ? r = ur(g) : (l &= c, l !== 0 && (r = ur(l)));
    } else c = n & ~i, c !== 0 ? r = ur(c) : l !== 0 && (r = ur(l));
    if (r === 0) return 0;
    if (t !== 0 && t !== r && (t & i) === 0 && (i = r & -r, l = t & -t, i >= l || i === 16 && (l & 4194240) !== 0)) return t;
    if ((r & 4) !== 0 && (r |= n & 16), t = e.entangledLanes, t !== 0) for (e = e.entanglements, t &= r; 0 < t; ) n = 31 - ft(t), i = 1 << n, r |= e[n], t &= ~i;
    return r;
  }
  function Fd(e, t) {
    switch (e) {
      case 1:
      case 2:
      case 4:
        return t + 250;
      case 8:
      case 16:
      case 32:
      case 64:
      case 128:
      case 256:
      case 512:
      case 1024:
      case 2048:
      case 4096:
      case 8192:
      case 16384:
      case 32768:
      case 65536:
      case 131072:
      case 262144:
      case 524288:
      case 1048576:
      case 2097152:
        return t + 5e3;
      case 4194304:
      case 8388608:
      case 16777216:
      case 33554432:
      case 67108864:
        return -1;
      case 134217728:
      case 268435456:
      case 536870912:
      case 1073741824:
        return -1;
      default:
        return -1;
    }
  }
  function Ud(e, t) {
    for (var n = e.suspendedLanes, r = e.pingedLanes, i = e.expirationTimes, l = e.pendingLanes; 0 < l; ) {
      var c = 31 - ft(l), g = 1 << c, v = i[c];
      v === -1 ? ((g & n) === 0 || (g & r) !== 0) && (i[c] = Fd(g, t)) : v <= t && (e.expiredLanes |= g), l &= ~g;
    }
  }
  function Mo(e) {
    return e = e.pendingLanes & -1073741825, e !== 0 ? e : e & 1073741824 ? 1073741824 : 0;
  }
  function ps() {
    var e = oi;
    return oi <<= 1, (oi & 4194240) === 0 && (oi = 64), e;
  }
  function Lo(e) {
    for (var t = [], n = 0; 31 > n; n++) t.push(e);
    return t;
  }
  function cr(e, t, n) {
    e.pendingLanes |= t, t !== 536870912 && (e.suspendedLanes = 0, e.pingedLanes = 0), e = e.eventTimes, t = 31 - ft(t), e[t] = n;
  }
  function Vd(e, t) {
    var n = e.pendingLanes & ~t;
    e.pendingLanes = t, e.suspendedLanes = 0, e.pingedLanes = 0, e.expiredLanes &= t, e.mutableReadLanes &= t, e.entangledLanes &= t, t = e.entanglements;
    var r = e.eventTimes;
    for (e = e.expirationTimes; 0 < n; ) {
      var i = 31 - ft(n), l = 1 << i;
      t[i] = 0, r[i] = -1, e[i] = -1, n &= ~l;
    }
  }
  function $o(e, t) {
    var n = e.entangledLanes |= t;
    for (e = e.entanglements; n; ) {
      var r = 31 - ft(n), i = 1 << r;
      i & t | e[r] & t && (e[r] |= t), n &= ~i;
    }
  }
  var re = 0;
  function ms(e) {
    return e &= -e, 1 < e ? 4 < e ? (e & 268435455) !== 0 ? 16 : 536870912 : 4 : 1;
  }
  var gs, Fo, hs, vs, ys, Uo = !1, si = [], Vt = null, Wt = null, Ht = null, dr = /* @__PURE__ */ new Map(), fr = /* @__PURE__ */ new Map(), Bt = [], Wd = "mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");
  function ks(e, t) {
    switch (e) {
      case "focusin":
      case "focusout":
        Vt = null;
        break;
      case "dragenter":
      case "dragleave":
        Wt = null;
        break;
      case "mouseover":
      case "mouseout":
        Ht = null;
        break;
      case "pointerover":
      case "pointerout":
        dr.delete(t.pointerId);
        break;
      case "gotpointercapture":
      case "lostpointercapture":
        fr.delete(t.pointerId);
    }
  }
  function pr(e, t, n, r, i, l) {
    return e === null || e.nativeEvent !== l ? (e = { blockedOn: t, domEventName: n, eventSystemFlags: r, nativeEvent: l, targetContainers: [i] }, t !== null && (t = jr(t), t !== null && Fo(t)), e) : (e.eventSystemFlags |= r, t = e.targetContainers, i !== null && t.indexOf(i) === -1 && t.push(i), e);
  }
  function Hd(e, t, n, r, i) {
    switch (t) {
      case "focusin":
        return Vt = pr(Vt, e, t, n, r, i), !0;
      case "dragenter":
        return Wt = pr(Wt, e, t, n, r, i), !0;
      case "mouseover":
        return Ht = pr(Ht, e, t, n, r, i), !0;
      case "pointerover":
        var l = i.pointerId;
        return dr.set(l, pr(dr.get(l) || null, e, t, n, r, i)), !0;
      case "gotpointercapture":
        return l = i.pointerId, fr.set(l, pr(fr.get(l) || null, e, t, n, r, i)), !0;
    }
    return !1;
  }
  function ws(e) {
    var t = fn(e.target);
    if (t !== null) {
      var n = dn(t);
      if (n !== null) {
        if (t = n.tag, t === 13) {
          if (t = os(n), t !== null) {
            e.blockedOn = t, ys(e.priority, function() {
              hs(n);
            });
            return;
          }
        } else if (t === 3 && n.stateNode.current.memoizedState.isDehydrated) {
          e.blockedOn = n.tag === 3 ? n.stateNode.containerInfo : null;
          return;
        }
      }
    }
    e.blockedOn = null;
  }
  function ui(e) {
    if (e.blockedOn !== null) return !1;
    for (var t = e.targetContainers; 0 < t.length; ) {
      var n = Wo(e.domEventName, e.eventSystemFlags, t[0], e.nativeEvent);
      if (n === null) {
        n = e.nativeEvent;
        var r = new n.constructor(n.type, n);
        xo = r, n.target.dispatchEvent(r), xo = null;
      } else return t = jr(n), t !== null && Fo(t), e.blockedOn = n, !1;
      t.shift();
    }
    return !0;
  }
  function Ss(e, t, n) {
    ui(e) && n.delete(t);
  }
  function Bd() {
    Uo = !1, Vt !== null && ui(Vt) && (Vt = null), Wt !== null && ui(Wt) && (Wt = null), Ht !== null && ui(Ht) && (Ht = null), dr.forEach(Ss), fr.forEach(Ss);
  }
  function mr(e, t) {
    e.blockedOn === t && (e.blockedOn = null, Uo || (Uo = !0, s.unstable_scheduleCallback(s.unstable_NormalPriority, Bd)));
  }
  function gr(e) {
    function t(i) {
      return mr(i, e);
    }
    if (0 < si.length) {
      mr(si[0], e);
      for (var n = 1; n < si.length; n++) {
        var r = si[n];
        r.blockedOn === e && (r.blockedOn = null);
      }
    }
    for (Vt !== null && mr(Vt, e), Wt !== null && mr(Wt, e), Ht !== null && mr(Ht, e), dr.forEach(t), fr.forEach(t), n = 0; n < Bt.length; n++) r = Bt[n], r.blockedOn === e && (r.blockedOn = null);
    for (; 0 < Bt.length && (n = Bt[0], n.blockedOn === null); ) ws(n), n.blockedOn === null && Bt.shift();
  }
  var Dn = q.ReactCurrentBatchConfig, ci = !0;
  function Kd(e, t, n, r) {
    var i = re, l = Dn.transition;
    Dn.transition = null;
    try {
      re = 1, Vo(e, t, n, r);
    } finally {
      re = i, Dn.transition = l;
    }
  }
  function Gd(e, t, n, r) {
    var i = re, l = Dn.transition;
    Dn.transition = null;
    try {
      re = 4, Vo(e, t, n, r);
    } finally {
      re = i, Dn.transition = l;
    }
  }
  function Vo(e, t, n, r) {
    if (ci) {
      var i = Wo(e, t, n, r);
      if (i === null) ol(e, t, r, di, n), ks(e, r);
      else if (Hd(i, e, t, n, r)) r.stopPropagation();
      else if (ks(e, r), t & 4 && -1 < Wd.indexOf(e)) {
        for (; i !== null; ) {
          var l = jr(i);
          if (l !== null && gs(l), l = Wo(e, t, n, r), l === null && ol(e, t, r, di, n), l === i) break;
          i = l;
        }
        i !== null && r.stopPropagation();
      } else ol(e, t, r, null, n);
    }
  }
  var di = null;
  function Wo(e, t, n, r) {
    if (di = null, e = Ao(r), e = fn(e), e !== null) if (t = dn(e), t === null) e = null;
    else if (n = t.tag, n === 13) {
      if (e = os(t), e !== null) return e;
      e = null;
    } else if (n === 3) {
      if (t.stateNode.current.memoizedState.isDehydrated) return t.tag === 3 ? t.stateNode.containerInfo : null;
      e = null;
    } else t !== e && (e = null);
    return di = e, null;
  }
  function _s(e) {
    switch (e) {
      case "cancel":
      case "click":
      case "close":
      case "contextmenu":
      case "copy":
      case "cut":
      case "auxclick":
      case "dblclick":
      case "dragend":
      case "dragstart":
      case "drop":
      case "focusin":
      case "focusout":
      case "input":
      case "invalid":
      case "keydown":
      case "keypress":
      case "keyup":
      case "mousedown":
      case "mouseup":
      case "paste":
      case "pause":
      case "play":
      case "pointercancel":
      case "pointerdown":
      case "pointerup":
      case "ratechange":
      case "reset":
      case "resize":
      case "seeked":
      case "submit":
      case "touchcancel":
      case "touchend":
      case "touchstart":
      case "volumechange":
      case "change":
      case "selectionchange":
      case "textInput":
      case "compositionstart":
      case "compositionend":
      case "compositionupdate":
      case "beforeblur":
      case "afterblur":
      case "beforeinput":
      case "blur":
      case "fullscreenchange":
      case "focus":
      case "hashchange":
      case "popstate":
      case "select":
      case "selectstart":
        return 1;
      case "drag":
      case "dragenter":
      case "dragexit":
      case "dragleave":
      case "dragover":
      case "mousemove":
      case "mouseout":
      case "mouseover":
      case "pointermove":
      case "pointerout":
      case "pointerover":
      case "scroll":
      case "toggle":
      case "touchmove":
      case "wheel":
      case "mouseenter":
      case "mouseleave":
      case "pointerenter":
      case "pointerleave":
        return 4;
      case "message":
        switch (Nd()) {
          case Oo:
            return 1;
          case ds:
            return 4;
          case ri:
          case zd:
            return 16;
          case fs:
            return 536870912;
          default:
            return 16;
        }
      default:
        return 16;
    }
  }
  var Kt = null, Ho = null, fi = null;
  function Es() {
    if (fi) return fi;
    var e, t = Ho, n = t.length, r, i = "value" in Kt ? Kt.value : Kt.textContent, l = i.length;
    for (e = 0; e < n && t[e] === i[e]; e++) ;
    var c = n - e;
    for (r = 1; r <= c && t[n - r] === i[l - r]; r++) ;
    return fi = i.slice(e, 1 < r ? 1 - r : void 0);
  }
  function pi(e) {
    var t = e.keyCode;
    return "charCode" in e ? (e = e.charCode, e === 0 && t === 13 && (e = 13)) : e = t, e === 10 && (e = 13), 32 <= e || e === 13 ? e : 0;
  }
  function mi() {
    return !0;
  }
  function Cs() {
    return !1;
  }
  function Xe(e) {
    function t(n, r, i, l, c) {
      this._reactName = n, this._targetInst = i, this.type = r, this.nativeEvent = l, this.target = c, this.currentTarget = null;
      for (var g in e) e.hasOwnProperty(g) && (n = e[g], this[g] = n ? n(l) : l[g]);
      return this.isDefaultPrevented = (l.defaultPrevented != null ? l.defaultPrevented : l.returnValue === !1) ? mi : Cs, this.isPropagationStopped = Cs, this;
    }
    return O(t.prototype, { preventDefault: function() {
      this.defaultPrevented = !0;
      var n = this.nativeEvent;
      n && (n.preventDefault ? n.preventDefault() : typeof n.returnValue != "unknown" && (n.returnValue = !1), this.isDefaultPrevented = mi);
    }, stopPropagation: function() {
      var n = this.nativeEvent;
      n && (n.stopPropagation ? n.stopPropagation() : typeof n.cancelBubble != "unknown" && (n.cancelBubble = !0), this.isPropagationStopped = mi);
    }, persist: function() {
    }, isPersistent: mi }), t;
  }
  var Nn = { eventPhase: 0, bubbles: 0, cancelable: 0, timeStamp: function(e) {
    return e.timeStamp || Date.now();
  }, defaultPrevented: 0, isTrusted: 0 }, Bo = Xe(Nn), hr = O({}, Nn, { view: 0, detail: 0 }), Qd = Xe(hr), Ko, Go, vr, gi = O({}, hr, { screenX: 0, screenY: 0, clientX: 0, clientY: 0, pageX: 0, pageY: 0, ctrlKey: 0, shiftKey: 0, altKey: 0, metaKey: 0, getModifierState: bo, button: 0, buttons: 0, relatedTarget: function(e) {
    return e.relatedTarget === void 0 ? e.fromElement === e.srcElement ? e.toElement : e.fromElement : e.relatedTarget;
  }, movementX: function(e) {
    return "movementX" in e ? e.movementX : (e !== vr && (vr && e.type === "mousemove" ? (Ko = e.screenX - vr.screenX, Go = e.screenY - vr.screenY) : Go = Ko = 0, vr = e), Ko);
  }, movementY: function(e) {
    return "movementY" in e ? e.movementY : Go;
  } }), Ts = Xe(gi), bd = O({}, gi, { dataTransfer: 0 }), Yd = Xe(bd), Xd = O({}, hr, { relatedTarget: 0 }), Qo = Xe(Xd), qd = O({}, Nn, { animationName: 0, elapsedTime: 0, pseudoElement: 0 }), Jd = Xe(qd), Zd = O({}, Nn, { clipboardData: function(e) {
    return "clipboardData" in e ? e.clipboardData : window.clipboardData;
  } }), ef = Xe(Zd), tf = O({}, Nn, { data: 0 }), Ps = Xe(tf), nf = {
    Esc: "Escape",
    Spacebar: " ",
    Left: "ArrowLeft",
    Up: "ArrowUp",
    Right: "ArrowRight",
    Down: "ArrowDown",
    Del: "Delete",
    Win: "OS",
    Menu: "ContextMenu",
    Apps: "ContextMenu",
    Scroll: "ScrollLock",
    MozPrintableKey: "Unidentified"
  }, rf = {
    8: "Backspace",
    9: "Tab",
    12: "Clear",
    13: "Enter",
    16: "Shift",
    17: "Control",
    18: "Alt",
    19: "Pause",
    20: "CapsLock",
    27: "Escape",
    32: " ",
    33: "PageUp",
    34: "PageDown",
    35: "End",
    36: "Home",
    37: "ArrowLeft",
    38: "ArrowUp",
    39: "ArrowRight",
    40: "ArrowDown",
    45: "Insert",
    46: "Delete",
    112: "F1",
    113: "F2",
    114: "F3",
    115: "F4",
    116: "F5",
    117: "F6",
    118: "F7",
    119: "F8",
    120: "F9",
    121: "F10",
    122: "F11",
    123: "F12",
    144: "NumLock",
    145: "ScrollLock",
    224: "Meta"
  }, of = { Alt: "altKey", Control: "ctrlKey", Meta: "metaKey", Shift: "shiftKey" };
  function lf(e) {
    var t = this.nativeEvent;
    return t.getModifierState ? t.getModifierState(e) : (e = of[e]) ? !!t[e] : !1;
  }
  function bo() {
    return lf;
  }
  var af = O({}, hr, { key: function(e) {
    if (e.key) {
      var t = nf[e.key] || e.key;
      if (t !== "Unidentified") return t;
    }
    return e.type === "keypress" ? (e = pi(e), e === 13 ? "Enter" : String.fromCharCode(e)) : e.type === "keydown" || e.type === "keyup" ? rf[e.keyCode] || "Unidentified" : "";
  }, code: 0, location: 0, ctrlKey: 0, shiftKey: 0, altKey: 0, metaKey: 0, repeat: 0, locale: 0, getModifierState: bo, charCode: function(e) {
    return e.type === "keypress" ? pi(e) : 0;
  }, keyCode: function(e) {
    return e.type === "keydown" || e.type === "keyup" ? e.keyCode : 0;
  }, which: function(e) {
    return e.type === "keypress" ? pi(e) : e.type === "keydown" || e.type === "keyup" ? e.keyCode : 0;
  } }), sf = Xe(af), uf = O({}, gi, { pointerId: 0, width: 0, height: 0, pressure: 0, tangentialPressure: 0, tiltX: 0, tiltY: 0, twist: 0, pointerType: 0, isPrimary: 0 }), js = Xe(uf), cf = O({}, hr, { touches: 0, targetTouches: 0, changedTouches: 0, altKey: 0, metaKey: 0, ctrlKey: 0, shiftKey: 0, getModifierState: bo }), df = Xe(cf), ff = O({}, Nn, { propertyName: 0, elapsedTime: 0, pseudoElement: 0 }), pf = Xe(ff), mf = O({}, gi, {
    deltaX: function(e) {
      return "deltaX" in e ? e.deltaX : "wheelDeltaX" in e ? -e.wheelDeltaX : 0;
    },
    deltaY: function(e) {
      return "deltaY" in e ? e.deltaY : "wheelDeltaY" in e ? -e.wheelDeltaY : "wheelDelta" in e ? -e.wheelDelta : 0;
    },
    deltaZ: 0,
    deltaMode: 0
  }), gf = Xe(mf), hf = [9, 13, 27, 32], Yo = m && "CompositionEvent" in window, yr = null;
  m && "documentMode" in document && (yr = document.documentMode);
  var vf = m && "TextEvent" in window && !yr, Is = m && (!Yo || yr && 8 < yr && 11 >= yr), xs = " ", As = !1;
  function Rs(e, t) {
    switch (e) {
      case "keyup":
        return hf.indexOf(t.keyCode) !== -1;
      case "keydown":
        return t.keyCode !== 229;
      case "keypress":
      case "mousedown":
      case "focusout":
        return !0;
      default:
        return !1;
    }
  }
  function Ds(e) {
    return e = e.detail, typeof e == "object" && "data" in e ? e.data : null;
  }
  var zn = !1;
  function yf(e, t) {
    switch (e) {
      case "compositionend":
        return Ds(t);
      case "keypress":
        return t.which !== 32 ? null : (As = !0, xs);
      case "textInput":
        return e = t.data, e === xs && As ? null : e;
      default:
        return null;
    }
  }
  function kf(e, t) {
    if (zn) return e === "compositionend" || !Yo && Rs(e, t) ? (e = Es(), fi = Ho = Kt = null, zn = !1, e) : null;
    switch (e) {
      case "paste":
        return null;
      case "keypress":
        if (!(t.ctrlKey || t.altKey || t.metaKey) || t.ctrlKey && t.altKey) {
          if (t.char && 1 < t.char.length) return t.char;
          if (t.which) return String.fromCharCode(t.which);
        }
        return null;
      case "compositionend":
        return Is && t.locale !== "ko" ? null : t.data;
      default:
        return null;
    }
  }
  var wf = { color: !0, date: !0, datetime: !0, "datetime-local": !0, email: !0, month: !0, number: !0, password: !0, range: !0, search: !0, tel: !0, text: !0, time: !0, url: !0, week: !0 };
  function Ns(e) {
    var t = e && e.nodeName && e.nodeName.toLowerCase();
    return t === "input" ? !!wf[e.type] : t === "textarea";
  }
  function zs(e, t, n, r) {
    es(r), t = wi(t, "onChange"), 0 < t.length && (n = new Bo("onChange", "change", null, n, r), e.push({ event: n, listeners: t }));
  }
  var kr = null, wr = null;
  function Sf(e) {
    Js(e, 0);
  }
  function hi(e) {
    var t = Fn(e);
    if (Wa(t)) return e;
  }
  function _f(e, t) {
    if (e === "change") return t;
  }
  var Os = !1;
  if (m) {
    var Xo;
    if (m) {
      var qo = "oninput" in document;
      if (!qo) {
        var Ms = document.createElement("div");
        Ms.setAttribute("oninput", "return;"), qo = typeof Ms.oninput == "function";
      }
      Xo = qo;
    } else Xo = !1;
    Os = Xo && (!document.documentMode || 9 < document.documentMode);
  }
  function Ls() {
    kr && (kr.detachEvent("onpropertychange", $s), wr = kr = null);
  }
  function $s(e) {
    if (e.propertyName === "value" && hi(wr)) {
      var t = [];
      zs(t, wr, e, Ao(e)), is(Sf, t);
    }
  }
  function Ef(e, t, n) {
    e === "focusin" ? (Ls(), kr = t, wr = n, kr.attachEvent("onpropertychange", $s)) : e === "focusout" && Ls();
  }
  function Cf(e) {
    if (e === "selectionchange" || e === "keyup" || e === "keydown") return hi(wr);
  }
  function Tf(e, t) {
    if (e === "click") return hi(t);
  }
  function Pf(e, t) {
    if (e === "input" || e === "change") return hi(t);
  }
  function jf(e, t) {
    return e === t && (e !== 0 || 1 / e === 1 / t) || e !== e && t !== t;
  }
  var pt = typeof Object.is == "function" ? Object.is : jf;
  function Sr(e, t) {
    if (pt(e, t)) return !0;
    if (typeof e != "object" || e === null || typeof t != "object" || t === null) return !1;
    var n = Object.keys(e), r = Object.keys(t);
    if (n.length !== r.length) return !1;
    for (r = 0; r < n.length; r++) {
      var i = n[r];
      if (!h.call(t, i) || !pt(e[i], t[i])) return !1;
    }
    return !0;
  }
  function Fs(e) {
    for (; e && e.firstChild; ) e = e.firstChild;
    return e;
  }
  function Us(e, t) {
    var n = Fs(e);
    e = 0;
    for (var r; n; ) {
      if (n.nodeType === 3) {
        if (r = e + n.textContent.length, e <= t && r >= t) return { node: n, offset: t - e };
        e = r;
      }
      e: {
        for (; n; ) {
          if (n.nextSibling) {
            n = n.nextSibling;
            break e;
          }
          n = n.parentNode;
        }
        n = void 0;
      }
      n = Fs(n);
    }
  }
  function Vs(e, t) {
    return e && t ? e === t ? !0 : e && e.nodeType === 3 ? !1 : t && t.nodeType === 3 ? Vs(e, t.parentNode) : "contains" in e ? e.contains(t) : e.compareDocumentPosition ? !!(e.compareDocumentPosition(t) & 16) : !1 : !1;
  }
  function Ws() {
    for (var e = window, t = Zr(); t instanceof e.HTMLIFrameElement; ) {
      try {
        var n = typeof t.contentWindow.location.href == "string";
      } catch {
        n = !1;
      }
      if (n) e = t.contentWindow;
      else break;
      t = Zr(e.document);
    }
    return t;
  }
  function Jo(e) {
    var t = e && e.nodeName && e.nodeName.toLowerCase();
    return t && (t === "input" && (e.type === "text" || e.type === "search" || e.type === "tel" || e.type === "url" || e.type === "password") || t === "textarea" || e.contentEditable === "true");
  }
  function If(e) {
    var t = Ws(), n = e.focusedElem, r = e.selectionRange;
    if (t !== n && n && n.ownerDocument && Vs(n.ownerDocument.documentElement, n)) {
      if (r !== null && Jo(n)) {
        if (t = r.start, e = r.end, e === void 0 && (e = t), "selectionStart" in n) n.selectionStart = t, n.selectionEnd = Math.min(e, n.value.length);
        else if (e = (t = n.ownerDocument || document) && t.defaultView || window, e.getSelection) {
          e = e.getSelection();
          var i = n.textContent.length, l = Math.min(r.start, i);
          r = r.end === void 0 ? l : Math.min(r.end, i), !e.extend && l > r && (i = r, r = l, l = i), i = Us(n, l);
          var c = Us(
            n,
            r
          );
          i && c && (e.rangeCount !== 1 || e.anchorNode !== i.node || e.anchorOffset !== i.offset || e.focusNode !== c.node || e.focusOffset !== c.offset) && (t = t.createRange(), t.setStart(i.node, i.offset), e.removeAllRanges(), l > r ? (e.addRange(t), e.extend(c.node, c.offset)) : (t.setEnd(c.node, c.offset), e.addRange(t)));
        }
      }
      for (t = [], e = n; e = e.parentNode; ) e.nodeType === 1 && t.push({ element: e, left: e.scrollLeft, top: e.scrollTop });
      for (typeof n.focus == "function" && n.focus(), n = 0; n < t.length; n++) e = t[n], e.element.scrollLeft = e.left, e.element.scrollTop = e.top;
    }
  }
  var xf = m && "documentMode" in document && 11 >= document.documentMode, On = null, Zo = null, _r = null, el = !1;
  function Hs(e, t, n) {
    var r = n.window === n ? n.document : n.nodeType === 9 ? n : n.ownerDocument;
    el || On == null || On !== Zr(r) || (r = On, "selectionStart" in r && Jo(r) ? r = { start: r.selectionStart, end: r.selectionEnd } : (r = (r.ownerDocument && r.ownerDocument.defaultView || window).getSelection(), r = { anchorNode: r.anchorNode, anchorOffset: r.anchorOffset, focusNode: r.focusNode, focusOffset: r.focusOffset }), _r && Sr(_r, r) || (_r = r, r = wi(Zo, "onSelect"), 0 < r.length && (t = new Bo("onSelect", "select", null, t, n), e.push({ event: t, listeners: r }), t.target = On)));
  }
  function vi(e, t) {
    var n = {};
    return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit" + e] = "webkit" + t, n["Moz" + e] = "moz" + t, n;
  }
  var Mn = { animationend: vi("Animation", "AnimationEnd"), animationiteration: vi("Animation", "AnimationIteration"), animationstart: vi("Animation", "AnimationStart"), transitionend: vi("Transition", "TransitionEnd") }, tl = {}, Bs = {};
  m && (Bs = document.createElement("div").style, "AnimationEvent" in window || (delete Mn.animationend.animation, delete Mn.animationiteration.animation, delete Mn.animationstart.animation), "TransitionEvent" in window || delete Mn.transitionend.transition);
  function yi(e) {
    if (tl[e]) return tl[e];
    if (!Mn[e]) return e;
    var t = Mn[e], n;
    for (n in t) if (t.hasOwnProperty(n) && n in Bs) return tl[e] = t[n];
    return e;
  }
  var Ks = yi("animationend"), Gs = yi("animationiteration"), Qs = yi("animationstart"), bs = yi("transitionend"), Ys = /* @__PURE__ */ new Map(), Xs = "abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");
  function Gt(e, t) {
    Ys.set(e, t), u(t, [e]);
  }
  for (var nl = 0; nl < Xs.length; nl++) {
    var rl = Xs[nl], Af = rl.toLowerCase(), Rf = rl[0].toUpperCase() + rl.slice(1);
    Gt(Af, "on" + Rf);
  }
  Gt(Ks, "onAnimationEnd"), Gt(Gs, "onAnimationIteration"), Gt(Qs, "onAnimationStart"), Gt("dblclick", "onDoubleClick"), Gt("focusin", "onFocus"), Gt("focusout", "onBlur"), Gt(bs, "onTransitionEnd"), p("onMouseEnter", ["mouseout", "mouseover"]), p("onMouseLeave", ["mouseout", "mouseover"]), p("onPointerEnter", ["pointerout", "pointerover"]), p("onPointerLeave", ["pointerout", "pointerover"]), u("onChange", "change click focusin focusout input keydown keyup selectionchange".split(" ")), u("onSelect", "focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" ")), u("onBeforeInput", ["compositionend", "keypress", "textInput", "paste"]), u("onCompositionEnd", "compositionend focusout keydown keypress keyup mousedown".split(" ")), u("onCompositionStart", "compositionstart focusout keydown keypress keyup mousedown".split(" ")), u("onCompositionUpdate", "compositionupdate focusout keydown keypress keyup mousedown".split(" "));
  var Er = "abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "), Df = new Set("cancel close invalid load scroll toggle".split(" ").concat(Er));
  function qs(e, t, n) {
    var r = e.type || "unknown-event";
    e.currentTarget = n, xd(r, t, void 0, e), e.currentTarget = null;
  }
  function Js(e, t) {
    t = (t & 4) !== 0;
    for (var n = 0; n < e.length; n++) {
      var r = e[n], i = r.event;
      r = r.listeners;
      e: {
        var l = void 0;
        if (t) for (var c = r.length - 1; 0 <= c; c--) {
          var g = r[c], v = g.instance, _ = g.currentTarget;
          if (g = g.listener, v !== l && i.isPropagationStopped()) break e;
          qs(i, g, _), l = v;
        }
        else for (c = 0; c < r.length; c++) {
          if (g = r[c], v = g.instance, _ = g.currentTarget, g = g.listener, v !== l && i.isPropagationStopped()) break e;
          qs(i, g, _), l = v;
        }
      }
    }
    if (ni) throw e = zo, ni = !1, zo = null, e;
  }
  function se(e, t) {
    var n = t[dl];
    n === void 0 && (n = t[dl] = /* @__PURE__ */ new Set());
    var r = e + "__bubble";
    n.has(r) || (Zs(t, e, 2, !1), n.add(r));
  }
  function il(e, t, n) {
    var r = 0;
    t && (r |= 4), Zs(n, e, r, t);
  }
  var ki = "_reactListening" + Math.random().toString(36).slice(2);
  function Cr(e) {
    if (!e[ki]) {
      e[ki] = !0, d.forEach(function(n) {
        n !== "selectionchange" && (Df.has(n) || il(n, !1, e), il(n, !0, e));
      });
      var t = e.nodeType === 9 ? e : e.ownerDocument;
      t === null || t[ki] || (t[ki] = !0, il("selectionchange", !1, t));
    }
  }
  function Zs(e, t, n, r) {
    switch (_s(t)) {
      case 1:
        var i = Kd;
        break;
      case 4:
        i = Gd;
        break;
      default:
        i = Vo;
    }
    n = i.bind(null, t, n, e), i = void 0, !No || t !== "touchstart" && t !== "touchmove" && t !== "wheel" || (i = !0), r ? i !== void 0 ? e.addEventListener(t, n, { capture: !0, passive: i }) : e.addEventListener(t, n, !0) : i !== void 0 ? e.addEventListener(t, n, { passive: i }) : e.addEventListener(t, n, !1);
  }
  function ol(e, t, n, r, i) {
    var l = r;
    if ((t & 1) === 0 && (t & 2) === 0 && r !== null) e: for (; ; ) {
      if (r === null) return;
      var c = r.tag;
      if (c === 3 || c === 4) {
        var g = r.stateNode.containerInfo;
        if (g === i || g.nodeType === 8 && g.parentNode === i) break;
        if (c === 4) for (c = r.return; c !== null; ) {
          var v = c.tag;
          if ((v === 3 || v === 4) && (v = c.stateNode.containerInfo, v === i || v.nodeType === 8 && v.parentNode === i)) return;
          c = c.return;
        }
        for (; g !== null; ) {
          if (c = fn(g), c === null) return;
          if (v = c.tag, v === 5 || v === 6) {
            r = l = c;
            continue e;
          }
          g = g.parentNode;
        }
      }
      r = r.return;
    }
    is(function() {
      var _ = l, j = Ao(n), I = [];
      e: {
        var T = Ys.get(e);
        if (T !== void 0) {
          var D = Bo, L = e;
          switch (e) {
            case "keypress":
              if (pi(n) === 0) break e;
            case "keydown":
            case "keyup":
              D = sf;
              break;
            case "focusin":
              L = "focus", D = Qo;
              break;
            case "focusout":
              L = "blur", D = Qo;
              break;
            case "beforeblur":
            case "afterblur":
              D = Qo;
              break;
            case "click":
              if (n.button === 2) break e;
            case "auxclick":
            case "dblclick":
            case "mousedown":
            case "mousemove":
            case "mouseup":
            case "mouseout":
            case "mouseover":
            case "contextmenu":
              D = Ts;
              break;
            case "drag":
            case "dragend":
            case "dragenter":
            case "dragexit":
            case "dragleave":
            case "dragover":
            case "dragstart":
            case "drop":
              D = Yd;
              break;
            case "touchcancel":
            case "touchend":
            case "touchmove":
            case "touchstart":
              D = df;
              break;
            case Ks:
            case Gs:
            case Qs:
              D = Jd;
              break;
            case bs:
              D = pf;
              break;
            case "scroll":
              D = Qd;
              break;
            case "wheel":
              D = gf;
              break;
            case "copy":
            case "cut":
            case "paste":
              D = ef;
              break;
            case "gotpointercapture":
            case "lostpointercapture":
            case "pointercancel":
            case "pointerdown":
            case "pointermove":
            case "pointerout":
            case "pointerover":
            case "pointerup":
              D = js;
          }
          var F = (t & 4) !== 0, ke = !F && e === "scroll", w = F ? T !== null ? T + "Capture" : null : T;
          F = [];
          for (var y = _, S; y !== null; ) {
            S = y;
            var x = S.stateNode;
            if (S.tag === 5 && x !== null && (S = x, w !== null && (x = lr(y, w), x != null && F.push(Tr(y, x, S)))), ke) break;
            y = y.return;
          }
          0 < F.length && (T = new D(T, L, null, n, j), I.push({ event: T, listeners: F }));
        }
      }
      if ((t & 7) === 0) {
        e: {
          if (T = e === "mouseover" || e === "pointerover", D = e === "mouseout" || e === "pointerout", T && n !== xo && (L = n.relatedTarget || n.fromElement) && (fn(L) || L[At])) break e;
          if ((D || T) && (T = j.window === j ? j : (T = j.ownerDocument) ? T.defaultView || T.parentWindow : window, D ? (L = n.relatedTarget || n.toElement, D = _, L = L ? fn(L) : null, L !== null && (ke = dn(L), L !== ke || L.tag !== 5 && L.tag !== 6) && (L = null)) : (D = null, L = _), D !== L)) {
            if (F = Ts, x = "onMouseLeave", w = "onMouseEnter", y = "mouse", (e === "pointerout" || e === "pointerover") && (F = js, x = "onPointerLeave", w = "onPointerEnter", y = "pointer"), ke = D == null ? T : Fn(D), S = L == null ? T : Fn(L), T = new F(x, y + "leave", D, n, j), T.target = ke, T.relatedTarget = S, x = null, fn(j) === _ && (F = new F(w, y + "enter", L, n, j), F.target = S, F.relatedTarget = ke, x = F), ke = x, D && L) t: {
              for (F = D, w = L, y = 0, S = F; S; S = Ln(S)) y++;
              for (S = 0, x = w; x; x = Ln(x)) S++;
              for (; 0 < y - S; ) F = Ln(F), y--;
              for (; 0 < S - y; ) w = Ln(w), S--;
              for (; y--; ) {
                if (F === w || w !== null && F === w.alternate) break t;
                F = Ln(F), w = Ln(w);
              }
              F = null;
            }
            else F = null;
            D !== null && eu(I, T, D, F, !1), L !== null && ke !== null && eu(I, ke, L, F, !0);
          }
        }
        e: {
          if (T = _ ? Fn(_) : window, D = T.nodeName && T.nodeName.toLowerCase(), D === "select" || D === "input" && T.type === "file") var U = _f;
          else if (Ns(T)) if (Os) U = Pf;
          else {
            U = Cf;
            var V = Ef;
          }
          else (D = T.nodeName) && D.toLowerCase() === "input" && (T.type === "checkbox" || T.type === "radio") && (U = Tf);
          if (U && (U = U(e, _))) {
            zs(I, U, n, j);
            break e;
          }
          V && V(e, T, _), e === "focusout" && (V = T._wrapperState) && V.controlled && T.type === "number" && Co(T, "number", T.value);
        }
        switch (V = _ ? Fn(_) : window, e) {
          case "focusin":
            (Ns(V) || V.contentEditable === "true") && (On = V, Zo = _, _r = null);
            break;
          case "focusout":
            _r = Zo = On = null;
            break;
          case "mousedown":
            el = !0;
            break;
          case "contextmenu":
          case "mouseup":
          case "dragend":
            el = !1, Hs(I, n, j);
            break;
          case "selectionchange":
            if (xf) break;
          case "keydown":
          case "keyup":
            Hs(I, n, j);
        }
        var W;
        if (Yo) e: {
          switch (e) {
            case "compositionstart":
              var K = "onCompositionStart";
              break e;
            case "compositionend":
              K = "onCompositionEnd";
              break e;
            case "compositionupdate":
              K = "onCompositionUpdate";
              break e;
          }
          K = void 0;
        }
        else zn ? Rs(e, n) && (K = "onCompositionEnd") : e === "keydown" && n.keyCode === 229 && (K = "onCompositionStart");
        K && (Is && n.locale !== "ko" && (zn || K !== "onCompositionStart" ? K === "onCompositionEnd" && zn && (W = Es()) : (Kt = j, Ho = "value" in Kt ? Kt.value : Kt.textContent, zn = !0)), V = wi(_, K), 0 < V.length && (K = new Ps(K, e, null, n, j), I.push({ event: K, listeners: V }), W ? K.data = W : (W = Ds(n), W !== null && (K.data = W)))), (W = vf ? yf(e, n) : kf(e, n)) && (_ = wi(_, "onBeforeInput"), 0 < _.length && (j = new Ps("onBeforeInput", "beforeinput", null, n, j), I.push({ event: j, listeners: _ }), j.data = W));
      }
      Js(I, t);
    });
  }
  function Tr(e, t, n) {
    return { instance: e, listener: t, currentTarget: n };
  }
  function wi(e, t) {
    for (var n = t + "Capture", r = []; e !== null; ) {
      var i = e, l = i.stateNode;
      i.tag === 5 && l !== null && (i = l, l = lr(e, n), l != null && r.unshift(Tr(e, l, i)), l = lr(e, t), l != null && r.push(Tr(e, l, i))), e = e.return;
    }
    return r;
  }
  function Ln(e) {
    if (e === null) return null;
    do
      e = e.return;
    while (e && e.tag !== 5);
    return e || null;
  }
  function eu(e, t, n, r, i) {
    for (var l = t._reactName, c = []; n !== null && n !== r; ) {
      var g = n, v = g.alternate, _ = g.stateNode;
      if (v !== null && v === r) break;
      g.tag === 5 && _ !== null && (g = _, i ? (v = lr(n, l), v != null && c.unshift(Tr(n, v, g))) : i || (v = lr(n, l), v != null && c.push(Tr(n, v, g)))), n = n.return;
    }
    c.length !== 0 && e.push({ event: t, listeners: c });
  }
  var Nf = /\r\n?/g, zf = /\u0000|\uFFFD/g;
  function tu(e) {
    return (typeof e == "string" ? e : "" + e).replace(Nf, `
`).replace(zf, "");
  }
  function Si(e, t, n) {
    if (t = tu(t), tu(e) !== t && n) throw Error(a(425));
  }
  function _i() {
  }
  var ll = null, al = null;
  function sl(e, t) {
    return e === "textarea" || e === "noscript" || typeof t.children == "string" || typeof t.children == "number" || typeof t.dangerouslySetInnerHTML == "object" && t.dangerouslySetInnerHTML !== null && t.dangerouslySetInnerHTML.__html != null;
  }
  var ul = typeof setTimeout == "function" ? setTimeout : void 0, Of = typeof clearTimeout == "function" ? clearTimeout : void 0, nu = typeof Promise == "function" ? Promise : void 0, Mf = typeof queueMicrotask == "function" ? queueMicrotask : typeof nu < "u" ? function(e) {
    return nu.resolve(null).then(e).catch(Lf);
  } : ul;
  function Lf(e) {
    setTimeout(function() {
      throw e;
    });
  }
  function cl(e, t) {
    var n = t, r = 0;
    do {
      var i = n.nextSibling;
      if (e.removeChild(n), i && i.nodeType === 8) if (n = i.data, n === "/$") {
        if (r === 0) {
          e.removeChild(i), gr(t);
          return;
        }
        r--;
      } else n !== "$" && n !== "$?" && n !== "$!" || r++;
      n = i;
    } while (n);
    gr(t);
  }
  function Qt(e) {
    for (; e != null; e = e.nextSibling) {
      var t = e.nodeType;
      if (t === 1 || t === 3) break;
      if (t === 8) {
        if (t = e.data, t === "$" || t === "$!" || t === "$?") break;
        if (t === "/$") return null;
      }
    }
    return e;
  }
  function ru(e) {
    e = e.previousSibling;
    for (var t = 0; e; ) {
      if (e.nodeType === 8) {
        var n = e.data;
        if (n === "$" || n === "$!" || n === "$?") {
          if (t === 0) return e;
          t--;
        } else n === "/$" && t++;
      }
      e = e.previousSibling;
    }
    return null;
  }
  var $n = Math.random().toString(36).slice(2), Ct = "__reactFiber$" + $n, Pr = "__reactProps$" + $n, At = "__reactContainer$" + $n, dl = "__reactEvents$" + $n, $f = "__reactListeners$" + $n, Ff = "__reactHandles$" + $n;
  function fn(e) {
    var t = e[Ct];
    if (t) return t;
    for (var n = e.parentNode; n; ) {
      if (t = n[At] || n[Ct]) {
        if (n = t.alternate, t.child !== null || n !== null && n.child !== null) for (e = ru(e); e !== null; ) {
          if (n = e[Ct]) return n;
          e = ru(e);
        }
        return t;
      }
      e = n, n = e.parentNode;
    }
    return null;
  }
  function jr(e) {
    return e = e[Ct] || e[At], !e || e.tag !== 5 && e.tag !== 6 && e.tag !== 13 && e.tag !== 3 ? null : e;
  }
  function Fn(e) {
    if (e.tag === 5 || e.tag === 6) return e.stateNode;
    throw Error(a(33));
  }
  function Ei(e) {
    return e[Pr] || null;
  }
  var fl = [], Un = -1;
  function bt(e) {
    return { current: e };
  }
  function ue(e) {
    0 > Un || (e.current = fl[Un], fl[Un] = null, Un--);
  }
  function le(e, t) {
    Un++, fl[Un] = e.current, e.current = t;
  }
  var Yt = {}, De = bt(Yt), Ue = bt(!1), pn = Yt;
  function Vn(e, t) {
    var n = e.type.contextTypes;
    if (!n) return Yt;
    var r = e.stateNode;
    if (r && r.__reactInternalMemoizedUnmaskedChildContext === t) return r.__reactInternalMemoizedMaskedChildContext;
    var i = {}, l;
    for (l in n) i[l] = t[l];
    return r && (e = e.stateNode, e.__reactInternalMemoizedUnmaskedChildContext = t, e.__reactInternalMemoizedMaskedChildContext = i), i;
  }
  function Ve(e) {
    return e = e.childContextTypes, e != null;
  }
  function Ci() {
    ue(Ue), ue(De);
  }
  function iu(e, t, n) {
    if (De.current !== Yt) throw Error(a(168));
    le(De, t), le(Ue, n);
  }
  function ou(e, t, n) {
    var r = e.stateNode;
    if (t = t.childContextTypes, typeof r.getChildContext != "function") return n;
    r = r.getChildContext();
    for (var i in r) if (!(i in t)) throw Error(a(108, oe(e) || "Unknown", i));
    return O({}, n, r);
  }
  function Ti(e) {
    return e = (e = e.stateNode) && e.__reactInternalMemoizedMergedChildContext || Yt, pn = De.current, le(De, e), le(Ue, Ue.current), !0;
  }
  function lu(e, t, n) {
    var r = e.stateNode;
    if (!r) throw Error(a(169));
    n ? (e = ou(e, t, pn), r.__reactInternalMemoizedMergedChildContext = e, ue(Ue), ue(De), le(De, e)) : ue(Ue), le(Ue, n);
  }
  var Rt = null, Pi = !1, pl = !1;
  function au(e) {
    Rt === null ? Rt = [e] : Rt.push(e);
  }
  function Uf(e) {
    Pi = !0, au(e);
  }
  function Xt() {
    if (!pl && Rt !== null) {
      pl = !0;
      var e = 0, t = re;
      try {
        var n = Rt;
        for (re = 1; e < n.length; e++) {
          var r = n[e];
          do
            r = r(!0);
          while (r !== null);
        }
        Rt = null, Pi = !1;
      } catch (i) {
        throw Rt !== null && (Rt = Rt.slice(e + 1)), us(Oo, Xt), i;
      } finally {
        re = t, pl = !1;
      }
    }
    return null;
  }
  var Wn = [], Hn = 0, ji = null, Ii = 0, rt = [], it = 0, mn = null, Dt = 1, Nt = "";
  function gn(e, t) {
    Wn[Hn++] = Ii, Wn[Hn++] = ji, ji = e, Ii = t;
  }
  function su(e, t, n) {
    rt[it++] = Dt, rt[it++] = Nt, rt[it++] = mn, mn = e;
    var r = Dt;
    e = Nt;
    var i = 32 - ft(r) - 1;
    r &= ~(1 << i), n += 1;
    var l = 32 - ft(t) + i;
    if (30 < l) {
      var c = i - i % 5;
      l = (r & (1 << c) - 1).toString(32), r >>= c, i -= c, Dt = 1 << 32 - ft(t) + i | n << i | r, Nt = l + e;
    } else Dt = 1 << l | n << i | r, Nt = e;
  }
  function ml(e) {
    e.return !== null && (gn(e, 1), su(e, 1, 0));
  }
  function gl(e) {
    for (; e === ji; ) ji = Wn[--Hn], Wn[Hn] = null, Ii = Wn[--Hn], Wn[Hn] = null;
    for (; e === mn; ) mn = rt[--it], rt[it] = null, Nt = rt[--it], rt[it] = null, Dt = rt[--it], rt[it] = null;
  }
  var qe = null, Je = null, de = !1, mt = null;
  function uu(e, t) {
    var n = st(5, null, null, 0);
    n.elementType = "DELETED", n.stateNode = t, n.return = e, t = e.deletions, t === null ? (e.deletions = [n], e.flags |= 16) : t.push(n);
  }
  function cu(e, t) {
    switch (e.tag) {
      case 5:
        var n = e.type;
        return t = t.nodeType !== 1 || n.toLowerCase() !== t.nodeName.toLowerCase() ? null : t, t !== null ? (e.stateNode = t, qe = e, Je = Qt(t.firstChild), !0) : !1;
      case 6:
        return t = e.pendingProps === "" || t.nodeType !== 3 ? null : t, t !== null ? (e.stateNode = t, qe = e, Je = null, !0) : !1;
      case 13:
        return t = t.nodeType !== 8 ? null : t, t !== null ? (n = mn !== null ? { id: Dt, overflow: Nt } : null, e.memoizedState = { dehydrated: t, treeContext: n, retryLane: 1073741824 }, n = st(18, null, null, 0), n.stateNode = t, n.return = e, e.child = n, qe = e, Je = null, !0) : !1;
      default:
        return !1;
    }
  }
  function hl(e) {
    return (e.mode & 1) !== 0 && (e.flags & 128) === 0;
  }
  function vl(e) {
    if (de) {
      var t = Je;
      if (t) {
        var n = t;
        if (!cu(e, t)) {
          if (hl(e)) throw Error(a(418));
          t = Qt(n.nextSibling);
          var r = qe;
          t && cu(e, t) ? uu(r, n) : (e.flags = e.flags & -4097 | 2, de = !1, qe = e);
        }
      } else {
        if (hl(e)) throw Error(a(418));
        e.flags = e.flags & -4097 | 2, de = !1, qe = e;
      }
    }
  }
  function du(e) {
    for (e = e.return; e !== null && e.tag !== 5 && e.tag !== 3 && e.tag !== 13; ) e = e.return;
    qe = e;
  }
  function xi(e) {
    if (e !== qe) return !1;
    if (!de) return du(e), de = !0, !1;
    var t;
    if ((t = e.tag !== 3) && !(t = e.tag !== 5) && (t = e.type, t = t !== "head" && t !== "body" && !sl(e.type, e.memoizedProps)), t && (t = Je)) {
      if (hl(e)) throw fu(), Error(a(418));
      for (; t; ) uu(e, t), t = Qt(t.nextSibling);
    }
    if (du(e), e.tag === 13) {
      if (e = e.memoizedState, e = e !== null ? e.dehydrated : null, !e) throw Error(a(317));
      e: {
        for (e = e.nextSibling, t = 0; e; ) {
          if (e.nodeType === 8) {
            var n = e.data;
            if (n === "/$") {
              if (t === 0) {
                Je = Qt(e.nextSibling);
                break e;
              }
              t--;
            } else n !== "$" && n !== "$!" && n !== "$?" || t++;
          }
          e = e.nextSibling;
        }
        Je = null;
      }
    } else Je = qe ? Qt(e.stateNode.nextSibling) : null;
    return !0;
  }
  function fu() {
    for (var e = Je; e; ) e = Qt(e.nextSibling);
  }
  function Bn() {
    Je = qe = null, de = !1;
  }
  function yl(e) {
    mt === null ? mt = [e] : mt.push(e);
  }
  var Vf = q.ReactCurrentBatchConfig;
  function Ir(e, t, n) {
    if (e = n.ref, e !== null && typeof e != "function" && typeof e != "object") {
      if (n._owner) {
        if (n = n._owner, n) {
          if (n.tag !== 1) throw Error(a(309));
          var r = n.stateNode;
        }
        if (!r) throw Error(a(147, e));
        var i = r, l = "" + e;
        return t !== null && t.ref !== null && typeof t.ref == "function" && t.ref._stringRef === l ? t.ref : (t = function(c) {
          var g = i.refs;
          c === null ? delete g[l] : g[l] = c;
        }, t._stringRef = l, t);
      }
      if (typeof e != "string") throw Error(a(284));
      if (!n._owner) throw Error(a(290, e));
    }
    return e;
  }
  function Ai(e, t) {
    throw e = Object.prototype.toString.call(t), Error(a(31, e === "[object Object]" ? "object with keys {" + Object.keys(t).join(", ") + "}" : e));
  }
  function pu(e) {
    var t = e._init;
    return t(e._payload);
  }
  function mu(e) {
    function t(w, y) {
      if (e) {
        var S = w.deletions;
        S === null ? (w.deletions = [y], w.flags |= 16) : S.push(y);
      }
    }
    function n(w, y) {
      if (!e) return null;
      for (; y !== null; ) t(w, y), y = y.sibling;
      return null;
    }
    function r(w, y) {
      for (w = /* @__PURE__ */ new Map(); y !== null; ) y.key !== null ? w.set(y.key, y) : w.set(y.index, y), y = y.sibling;
      return w;
    }
    function i(w, y) {
      return w = on(w, y), w.index = 0, w.sibling = null, w;
    }
    function l(w, y, S) {
      return w.index = S, e ? (S = w.alternate, S !== null ? (S = S.index, S < y ? (w.flags |= 2, y) : S) : (w.flags |= 2, y)) : (w.flags |= 1048576, y);
    }
    function c(w) {
      return e && w.alternate === null && (w.flags |= 2), w;
    }
    function g(w, y, S, x) {
      return y === null || y.tag !== 6 ? (y = ua(S, w.mode, x), y.return = w, y) : (y = i(y, S), y.return = w, y);
    }
    function v(w, y, S, x) {
      var U = S.type;
      return U === Re ? j(w, y, S.props.children, x, S.key) : y !== null && (y.elementType === U || typeof U == "object" && U !== null && U.$$typeof === Fe && pu(U) === y.type) ? (x = i(y, S.props), x.ref = Ir(w, y, S), x.return = w, x) : (x = eo(S.type, S.key, S.props, null, w.mode, x), x.ref = Ir(w, y, S), x.return = w, x);
    }
    function _(w, y, S, x) {
      return y === null || y.tag !== 4 || y.stateNode.containerInfo !== S.containerInfo || y.stateNode.implementation !== S.implementation ? (y = ca(S, w.mode, x), y.return = w, y) : (y = i(y, S.children || []), y.return = w, y);
    }
    function j(w, y, S, x, U) {
      return y === null || y.tag !== 7 ? (y = En(S, w.mode, x, U), y.return = w, y) : (y = i(y, S), y.return = w, y);
    }
    function I(w, y, S) {
      if (typeof y == "string" && y !== "" || typeof y == "number") return y = ua("" + y, w.mode, S), y.return = w, y;
      if (typeof y == "object" && y !== null) {
        switch (y.$$typeof) {
          case ae:
            return S = eo(y.type, y.key, y.props, null, w.mode, S), S.ref = Ir(w, null, y), S.return = w, S;
          case _e:
            return y = ca(y, w.mode, S), y.return = w, y;
          case Fe:
            var x = y._init;
            return I(w, x(y._payload), S);
        }
        if (rr(y) || B(y)) return y = En(y, w.mode, S, null), y.return = w, y;
        Ai(w, y);
      }
      return null;
    }
    function T(w, y, S, x) {
      var U = y !== null ? y.key : null;
      if (typeof S == "string" && S !== "" || typeof S == "number") return U !== null ? null : g(w, y, "" + S, x);
      if (typeof S == "object" && S !== null) {
        switch (S.$$typeof) {
          case ae:
            return S.key === U ? v(w, y, S, x) : null;
          case _e:
            return S.key === U ? _(w, y, S, x) : null;
          case Fe:
            return U = S._init, T(
              w,
              y,
              U(S._payload),
              x
            );
        }
        if (rr(S) || B(S)) return U !== null ? null : j(w, y, S, x, null);
        Ai(w, S);
      }
      return null;
    }
    function D(w, y, S, x, U) {
      if (typeof x == "string" && x !== "" || typeof x == "number") return w = w.get(S) || null, g(y, w, "" + x, U);
      if (typeof x == "object" && x !== null) {
        switch (x.$$typeof) {
          case ae:
            return w = w.get(x.key === null ? S : x.key) || null, v(y, w, x, U);
          case _e:
            return w = w.get(x.key === null ? S : x.key) || null, _(y, w, x, U);
          case Fe:
            var V = x._init;
            return D(w, y, S, V(x._payload), U);
        }
        if (rr(x) || B(x)) return w = w.get(S) || null, j(y, w, x, U, null);
        Ai(y, x);
      }
      return null;
    }
    function L(w, y, S, x) {
      for (var U = null, V = null, W = y, K = y = 0, je = null; W !== null && K < S.length; K++) {
        W.index > K ? (je = W, W = null) : je = W.sibling;
        var te = T(w, W, S[K], x);
        if (te === null) {
          W === null && (W = je);
          break;
        }
        e && W && te.alternate === null && t(w, W), y = l(te, y, K), V === null ? U = te : V.sibling = te, V = te, W = je;
      }
      if (K === S.length) return n(w, W), de && gn(w, K), U;
      if (W === null) {
        for (; K < S.length; K++) W = I(w, S[K], x), W !== null && (y = l(W, y, K), V === null ? U = W : V.sibling = W, V = W);
        return de && gn(w, K), U;
      }
      for (W = r(w, W); K < S.length; K++) je = D(W, w, K, S[K], x), je !== null && (e && je.alternate !== null && W.delete(je.key === null ? K : je.key), y = l(je, y, K), V === null ? U = je : V.sibling = je, V = je);
      return e && W.forEach(function(ln) {
        return t(w, ln);
      }), de && gn(w, K), U;
    }
    function F(w, y, S, x) {
      var U = B(S);
      if (typeof U != "function") throw Error(a(150));
      if (S = U.call(S), S == null) throw Error(a(151));
      for (var V = U = null, W = y, K = y = 0, je = null, te = S.next(); W !== null && !te.done; K++, te = S.next()) {
        W.index > K ? (je = W, W = null) : je = W.sibling;
        var ln = T(w, W, te.value, x);
        if (ln === null) {
          W === null && (W = je);
          break;
        }
        e && W && ln.alternate === null && t(w, W), y = l(ln, y, K), V === null ? U = ln : V.sibling = ln, V = ln, W = je;
      }
      if (te.done) return n(
        w,
        W
      ), de && gn(w, K), U;
      if (W === null) {
        for (; !te.done; K++, te = S.next()) te = I(w, te.value, x), te !== null && (y = l(te, y, K), V === null ? U = te : V.sibling = te, V = te);
        return de && gn(w, K), U;
      }
      for (W = r(w, W); !te.done; K++, te = S.next()) te = D(W, w, K, te.value, x), te !== null && (e && te.alternate !== null && W.delete(te.key === null ? K : te.key), y = l(te, y, K), V === null ? U = te : V.sibling = te, V = te);
      return e && W.forEach(function(wp) {
        return t(w, wp);
      }), de && gn(w, K), U;
    }
    function ke(w, y, S, x) {
      if (typeof S == "object" && S !== null && S.type === Re && S.key === null && (S = S.props.children), typeof S == "object" && S !== null) {
        switch (S.$$typeof) {
          case ae:
            e: {
              for (var U = S.key, V = y; V !== null; ) {
                if (V.key === U) {
                  if (U = S.type, U === Re) {
                    if (V.tag === 7) {
                      n(w, V.sibling), y = i(V, S.props.children), y.return = w, w = y;
                      break e;
                    }
                  } else if (V.elementType === U || typeof U == "object" && U !== null && U.$$typeof === Fe && pu(U) === V.type) {
                    n(w, V.sibling), y = i(V, S.props), y.ref = Ir(w, V, S), y.return = w, w = y;
                    break e;
                  }
                  n(w, V);
                  break;
                } else t(w, V);
                V = V.sibling;
              }
              S.type === Re ? (y = En(S.props.children, w.mode, x, S.key), y.return = w, w = y) : (x = eo(S.type, S.key, S.props, null, w.mode, x), x.ref = Ir(w, y, S), x.return = w, w = x);
            }
            return c(w);
          case _e:
            e: {
              for (V = S.key; y !== null; ) {
                if (y.key === V) if (y.tag === 4 && y.stateNode.containerInfo === S.containerInfo && y.stateNode.implementation === S.implementation) {
                  n(w, y.sibling), y = i(y, S.children || []), y.return = w, w = y;
                  break e;
                } else {
                  n(w, y);
                  break;
                }
                else t(w, y);
                y = y.sibling;
              }
              y = ca(S, w.mode, x), y.return = w, w = y;
            }
            return c(w);
          case Fe:
            return V = S._init, ke(w, y, V(S._payload), x);
        }
        if (rr(S)) return L(w, y, S, x);
        if (B(S)) return F(w, y, S, x);
        Ai(w, S);
      }
      return typeof S == "string" && S !== "" || typeof S == "number" ? (S = "" + S, y !== null && y.tag === 6 ? (n(w, y.sibling), y = i(y, S), y.return = w, w = y) : (n(w, y), y = ua(S, w.mode, x), y.return = w, w = y), c(w)) : n(w, y);
    }
    return ke;
  }
  var Kn = mu(!0), gu = mu(!1), Ri = bt(null), Di = null, Gn = null, kl = null;
  function wl() {
    kl = Gn = Di = null;
  }
  function Sl(e) {
    var t = Ri.current;
    ue(Ri), e._currentValue = t;
  }
  function _l(e, t, n) {
    for (; e !== null; ) {
      var r = e.alternate;
      if ((e.childLanes & t) !== t ? (e.childLanes |= t, r !== null && (r.childLanes |= t)) : r !== null && (r.childLanes & t) !== t && (r.childLanes |= t), e === n) break;
      e = e.return;
    }
  }
  function Qn(e, t) {
    Di = e, kl = Gn = null, e = e.dependencies, e !== null && e.firstContext !== null && ((e.lanes & t) !== 0 && (We = !0), e.firstContext = null);
  }
  function ot(e) {
    var t = e._currentValue;
    if (kl !== e) if (e = { context: e, memoizedValue: t, next: null }, Gn === null) {
      if (Di === null) throw Error(a(308));
      Gn = e, Di.dependencies = { lanes: 0, firstContext: e };
    } else Gn = Gn.next = e;
    return t;
  }
  var hn = null;
  function El(e) {
    hn === null ? hn = [e] : hn.push(e);
  }
  function hu(e, t, n, r) {
    var i = t.interleaved;
    return i === null ? (n.next = n, El(t)) : (n.next = i.next, i.next = n), t.interleaved = n, zt(e, r);
  }
  function zt(e, t) {
    e.lanes |= t;
    var n = e.alternate;
    for (n !== null && (n.lanes |= t), n = e, e = e.return; e !== null; ) e.childLanes |= t, n = e.alternate, n !== null && (n.childLanes |= t), n = e, e = e.return;
    return n.tag === 3 ? n.stateNode : null;
  }
  var qt = !1;
  function Cl(e) {
    e.updateQueue = { baseState: e.memoizedState, firstBaseUpdate: null, lastBaseUpdate: null, shared: { pending: null, interleaved: null, lanes: 0 }, effects: null };
  }
  function vu(e, t) {
    e = e.updateQueue, t.updateQueue === e && (t.updateQueue = { baseState: e.baseState, firstBaseUpdate: e.firstBaseUpdate, lastBaseUpdate: e.lastBaseUpdate, shared: e.shared, effects: e.effects });
  }
  function Ot(e, t) {
    return { eventTime: e, lane: t, tag: 0, payload: null, callback: null, next: null };
  }
  function Jt(e, t, n) {
    var r = e.updateQueue;
    if (r === null) return null;
    if (r = r.shared, (J & 2) !== 0) {
      var i = r.pending;
      return i === null ? t.next = t : (t.next = i.next, i.next = t), r.pending = t, zt(e, n);
    }
    return i = r.interleaved, i === null ? (t.next = t, El(r)) : (t.next = i.next, i.next = t), r.interleaved = t, zt(e, n);
  }
  function Ni(e, t, n) {
    if (t = t.updateQueue, t !== null && (t = t.shared, (n & 4194240) !== 0)) {
      var r = t.lanes;
      r &= e.pendingLanes, n |= r, t.lanes = n, $o(e, n);
    }
  }
  function yu(e, t) {
    var n = e.updateQueue, r = e.alternate;
    if (r !== null && (r = r.updateQueue, n === r)) {
      var i = null, l = null;
      if (n = n.firstBaseUpdate, n !== null) {
        do {
          var c = { eventTime: n.eventTime, lane: n.lane, tag: n.tag, payload: n.payload, callback: n.callback, next: null };
          l === null ? i = l = c : l = l.next = c, n = n.next;
        } while (n !== null);
        l === null ? i = l = t : l = l.next = t;
      } else i = l = t;
      n = { baseState: r.baseState, firstBaseUpdate: i, lastBaseUpdate: l, shared: r.shared, effects: r.effects }, e.updateQueue = n;
      return;
    }
    e = n.lastBaseUpdate, e === null ? n.firstBaseUpdate = t : e.next = t, n.lastBaseUpdate = t;
  }
  function zi(e, t, n, r) {
    var i = e.updateQueue;
    qt = !1;
    var l = i.firstBaseUpdate, c = i.lastBaseUpdate, g = i.shared.pending;
    if (g !== null) {
      i.shared.pending = null;
      var v = g, _ = v.next;
      v.next = null, c === null ? l = _ : c.next = _, c = v;
      var j = e.alternate;
      j !== null && (j = j.updateQueue, g = j.lastBaseUpdate, g !== c && (g === null ? j.firstBaseUpdate = _ : g.next = _, j.lastBaseUpdate = v));
    }
    if (l !== null) {
      var I = i.baseState;
      c = 0, j = _ = v = null, g = l;
      do {
        var T = g.lane, D = g.eventTime;
        if ((r & T) === T) {
          j !== null && (j = j.next = {
            eventTime: D,
            lane: 0,
            tag: g.tag,
            payload: g.payload,
            callback: g.callback,
            next: null
          });
          e: {
            var L = e, F = g;
            switch (T = t, D = n, F.tag) {
              case 1:
                if (L = F.payload, typeof L == "function") {
                  I = L.call(D, I, T);
                  break e;
                }
                I = L;
                break e;
              case 3:
                L.flags = L.flags & -65537 | 128;
              case 0:
                if (L = F.payload, T = typeof L == "function" ? L.call(D, I, T) : L, T == null) break e;
                I = O({}, I, T);
                break e;
              case 2:
                qt = !0;
            }
          }
          g.callback !== null && g.lane !== 0 && (e.flags |= 64, T = i.effects, T === null ? i.effects = [g] : T.push(g));
        } else D = { eventTime: D, lane: T, tag: g.tag, payload: g.payload, callback: g.callback, next: null }, j === null ? (_ = j = D, v = I) : j = j.next = D, c |= T;
        if (g = g.next, g === null) {
          if (g = i.shared.pending, g === null) break;
          T = g, g = T.next, T.next = null, i.lastBaseUpdate = T, i.shared.pending = null;
        }
      } while (!0);
      if (j === null && (v = I), i.baseState = v, i.firstBaseUpdate = _, i.lastBaseUpdate = j, t = i.shared.interleaved, t !== null) {
        i = t;
        do
          c |= i.lane, i = i.next;
        while (i !== t);
      } else l === null && (i.shared.lanes = 0);
      kn |= c, e.lanes = c, e.memoizedState = I;
    }
  }
  function ku(e, t, n) {
    if (e = t.effects, t.effects = null, e !== null) for (t = 0; t < e.length; t++) {
      var r = e[t], i = r.callback;
      if (i !== null) {
        if (r.callback = null, r = n, typeof i != "function") throw Error(a(191, i));
        i.call(r);
      }
    }
  }
  var xr = {}, Tt = bt(xr), Ar = bt(xr), Rr = bt(xr);
  function vn(e) {
    if (e === xr) throw Error(a(174));
    return e;
  }
  function Tl(e, t) {
    switch (le(Rr, t), le(Ar, e), le(Tt, xr), e = t.nodeType, e) {
      case 9:
      case 11:
        t = (t = t.documentElement) ? t.namespaceURI : Po(null, "");
        break;
      default:
        e = e === 8 ? t.parentNode : t, t = e.namespaceURI || null, e = e.tagName, t = Po(t, e);
    }
    ue(Tt), le(Tt, t);
  }
  function bn() {
    ue(Tt), ue(Ar), ue(Rr);
  }
  function wu(e) {
    vn(Rr.current);
    var t = vn(Tt.current), n = Po(t, e.type);
    t !== n && (le(Ar, e), le(Tt, n));
  }
  function Pl(e) {
    Ar.current === e && (ue(Tt), ue(Ar));
  }
  var pe = bt(0);
  function Oi(e) {
    for (var t = e; t !== null; ) {
      if (t.tag === 13) {
        var n = t.memoizedState;
        if (n !== null && (n = n.dehydrated, n === null || n.data === "$?" || n.data === "$!")) return t;
      } else if (t.tag === 19 && t.memoizedProps.revealOrder !== void 0) {
        if ((t.flags & 128) !== 0) return t;
      } else if (t.child !== null) {
        t.child.return = t, t = t.child;
        continue;
      }
      if (t === e) break;
      for (; t.sibling === null; ) {
        if (t.return === null || t.return === e) return null;
        t = t.return;
      }
      t.sibling.return = t.return, t = t.sibling;
    }
    return null;
  }
  var jl = [];
  function Il() {
    for (var e = 0; e < jl.length; e++) jl[e]._workInProgressVersionPrimary = null;
    jl.length = 0;
  }
  var Mi = q.ReactCurrentDispatcher, xl = q.ReactCurrentBatchConfig, yn = 0, me = null, Ee = null, Te = null, Li = !1, Dr = !1, Nr = 0, Wf = 0;
  function Ne() {
    throw Error(a(321));
  }
  function Al(e, t) {
    if (t === null) return !1;
    for (var n = 0; n < t.length && n < e.length; n++) if (!pt(e[n], t[n])) return !1;
    return !0;
  }
  function Rl(e, t, n, r, i, l) {
    if (yn = l, me = t, t.memoizedState = null, t.updateQueue = null, t.lanes = 0, Mi.current = e === null || e.memoizedState === null ? Gf : Qf, e = n(r, i), Dr) {
      l = 0;
      do {
        if (Dr = !1, Nr = 0, 25 <= l) throw Error(a(301));
        l += 1, Te = Ee = null, t.updateQueue = null, Mi.current = bf, e = n(r, i);
      } while (Dr);
    }
    if (Mi.current = Ui, t = Ee !== null && Ee.next !== null, yn = 0, Te = Ee = me = null, Li = !1, t) throw Error(a(300));
    return e;
  }
  function Dl() {
    var e = Nr !== 0;
    return Nr = 0, e;
  }
  function Pt() {
    var e = { memoizedState: null, baseState: null, baseQueue: null, queue: null, next: null };
    return Te === null ? me.memoizedState = Te = e : Te = Te.next = e, Te;
  }
  function lt() {
    if (Ee === null) {
      var e = me.alternate;
      e = e !== null ? e.memoizedState : null;
    } else e = Ee.next;
    var t = Te === null ? me.memoizedState : Te.next;
    if (t !== null) Te = t, Ee = e;
    else {
      if (e === null) throw Error(a(310));
      Ee = e, e = { memoizedState: Ee.memoizedState, baseState: Ee.baseState, baseQueue: Ee.baseQueue, queue: Ee.queue, next: null }, Te === null ? me.memoizedState = Te = e : Te = Te.next = e;
    }
    return Te;
  }
  function zr(e, t) {
    return typeof t == "function" ? t(e) : t;
  }
  function Nl(e) {
    var t = lt(), n = t.queue;
    if (n === null) throw Error(a(311));
    n.lastRenderedReducer = e;
    var r = Ee, i = r.baseQueue, l = n.pending;
    if (l !== null) {
      if (i !== null) {
        var c = i.next;
        i.next = l.next, l.next = c;
      }
      r.baseQueue = i = l, n.pending = null;
    }
    if (i !== null) {
      l = i.next, r = r.baseState;
      var g = c = null, v = null, _ = l;
      do {
        var j = _.lane;
        if ((yn & j) === j) v !== null && (v = v.next = { lane: 0, action: _.action, hasEagerState: _.hasEagerState, eagerState: _.eagerState, next: null }), r = _.hasEagerState ? _.eagerState : e(r, _.action);
        else {
          var I = {
            lane: j,
            action: _.action,
            hasEagerState: _.hasEagerState,
            eagerState: _.eagerState,
            next: null
          };
          v === null ? (g = v = I, c = r) : v = v.next = I, me.lanes |= j, kn |= j;
        }
        _ = _.next;
      } while (_ !== null && _ !== l);
      v === null ? c = r : v.next = g, pt(r, t.memoizedState) || (We = !0), t.memoizedState = r, t.baseState = c, t.baseQueue = v, n.lastRenderedState = r;
    }
    if (e = n.interleaved, e !== null) {
      i = e;
      do
        l = i.lane, me.lanes |= l, kn |= l, i = i.next;
      while (i !== e);
    } else i === null && (n.lanes = 0);
    return [t.memoizedState, n.dispatch];
  }
  function zl(e) {
    var t = lt(), n = t.queue;
    if (n === null) throw Error(a(311));
    n.lastRenderedReducer = e;
    var r = n.dispatch, i = n.pending, l = t.memoizedState;
    if (i !== null) {
      n.pending = null;
      var c = i = i.next;
      do
        l = e(l, c.action), c = c.next;
      while (c !== i);
      pt(l, t.memoizedState) || (We = !0), t.memoizedState = l, t.baseQueue === null && (t.baseState = l), n.lastRenderedState = l;
    }
    return [l, r];
  }
  function Su() {
  }
  function _u(e, t) {
    var n = me, r = lt(), i = t(), l = !pt(r.memoizedState, i);
    if (l && (r.memoizedState = i, We = !0), r = r.queue, Ol(Tu.bind(null, n, r, e), [e]), r.getSnapshot !== t || l || Te !== null && Te.memoizedState.tag & 1) {
      if (n.flags |= 2048, Or(9, Cu.bind(null, n, r, i, t), void 0, null), Pe === null) throw Error(a(349));
      (yn & 30) !== 0 || Eu(n, t, i);
    }
    return i;
  }
  function Eu(e, t, n) {
    e.flags |= 16384, e = { getSnapshot: t, value: n }, t = me.updateQueue, t === null ? (t = { lastEffect: null, stores: null }, me.updateQueue = t, t.stores = [e]) : (n = t.stores, n === null ? t.stores = [e] : n.push(e));
  }
  function Cu(e, t, n, r) {
    t.value = n, t.getSnapshot = r, Pu(t) && ju(e);
  }
  function Tu(e, t, n) {
    return n(function() {
      Pu(t) && ju(e);
    });
  }
  function Pu(e) {
    var t = e.getSnapshot;
    e = e.value;
    try {
      var n = t();
      return !pt(e, n);
    } catch {
      return !0;
    }
  }
  function ju(e) {
    var t = zt(e, 1);
    t !== null && yt(t, e, 1, -1);
  }
  function Iu(e) {
    var t = Pt();
    return typeof e == "function" && (e = e()), t.memoizedState = t.baseState = e, e = { pending: null, interleaved: null, lanes: 0, dispatch: null, lastRenderedReducer: zr, lastRenderedState: e }, t.queue = e, e = e.dispatch = Kf.bind(null, me, e), [t.memoizedState, e];
  }
  function Or(e, t, n, r) {
    return e = { tag: e, create: t, destroy: n, deps: r, next: null }, t = me.updateQueue, t === null ? (t = { lastEffect: null, stores: null }, me.updateQueue = t, t.lastEffect = e.next = e) : (n = t.lastEffect, n === null ? t.lastEffect = e.next = e : (r = n.next, n.next = e, e.next = r, t.lastEffect = e)), e;
  }
  function xu() {
    return lt().memoizedState;
  }
  function $i(e, t, n, r) {
    var i = Pt();
    me.flags |= e, i.memoizedState = Or(1 | t, n, void 0, r === void 0 ? null : r);
  }
  function Fi(e, t, n, r) {
    var i = lt();
    r = r === void 0 ? null : r;
    var l = void 0;
    if (Ee !== null) {
      var c = Ee.memoizedState;
      if (l = c.destroy, r !== null && Al(r, c.deps)) {
        i.memoizedState = Or(t, n, l, r);
        return;
      }
    }
    me.flags |= e, i.memoizedState = Or(1 | t, n, l, r);
  }
  function Au(e, t) {
    return $i(8390656, 8, e, t);
  }
  function Ol(e, t) {
    return Fi(2048, 8, e, t);
  }
  function Ru(e, t) {
    return Fi(4, 2, e, t);
  }
  function Du(e, t) {
    return Fi(4, 4, e, t);
  }
  function Nu(e, t) {
    if (typeof t == "function") return e = e(), t(e), function() {
      t(null);
    };
    if (t != null) return e = e(), t.current = e, function() {
      t.current = null;
    };
  }
  function zu(e, t, n) {
    return n = n != null ? n.concat([e]) : null, Fi(4, 4, Nu.bind(null, t, e), n);
  }
  function Ml() {
  }
  function Ou(e, t) {
    var n = lt();
    t = t === void 0 ? null : t;
    var r = n.memoizedState;
    return r !== null && t !== null && Al(t, r[1]) ? r[0] : (n.memoizedState = [e, t], e);
  }
  function Mu(e, t) {
    var n = lt();
    t = t === void 0 ? null : t;
    var r = n.memoizedState;
    return r !== null && t !== null && Al(t, r[1]) ? r[0] : (e = e(), n.memoizedState = [e, t], e);
  }
  function Lu(e, t, n) {
    return (yn & 21) === 0 ? (e.baseState && (e.baseState = !1, We = !0), e.memoizedState = n) : (pt(n, t) || (n = ps(), me.lanes |= n, kn |= n, e.baseState = !0), t);
  }
  function Hf(e, t) {
    var n = re;
    re = n !== 0 && 4 > n ? n : 4, e(!0);
    var r = xl.transition;
    xl.transition = {};
    try {
      e(!1), t();
    } finally {
      re = n, xl.transition = r;
    }
  }
  function $u() {
    return lt().memoizedState;
  }
  function Bf(e, t, n) {
    var r = nn(e);
    if (n = { lane: r, action: n, hasEagerState: !1, eagerState: null, next: null }, Fu(e)) Uu(t, n);
    else if (n = hu(e, t, n, r), n !== null) {
      var i = $e();
      yt(n, e, r, i), Vu(n, t, r);
    }
  }
  function Kf(e, t, n) {
    var r = nn(e), i = { lane: r, action: n, hasEagerState: !1, eagerState: null, next: null };
    if (Fu(e)) Uu(t, i);
    else {
      var l = e.alternate;
      if (e.lanes === 0 && (l === null || l.lanes === 0) && (l = t.lastRenderedReducer, l !== null)) try {
        var c = t.lastRenderedState, g = l(c, n);
        if (i.hasEagerState = !0, i.eagerState = g, pt(g, c)) {
          var v = t.interleaved;
          v === null ? (i.next = i, El(t)) : (i.next = v.next, v.next = i), t.interleaved = i;
          return;
        }
      } catch {
      } finally {
      }
      n = hu(e, t, i, r), n !== null && (i = $e(), yt(n, e, r, i), Vu(n, t, r));
    }
  }
  function Fu(e) {
    var t = e.alternate;
    return e === me || t !== null && t === me;
  }
  function Uu(e, t) {
    Dr = Li = !0;
    var n = e.pending;
    n === null ? t.next = t : (t.next = n.next, n.next = t), e.pending = t;
  }
  function Vu(e, t, n) {
    if ((n & 4194240) !== 0) {
      var r = t.lanes;
      r &= e.pendingLanes, n |= r, t.lanes = n, $o(e, n);
    }
  }
  var Ui = { readContext: ot, useCallback: Ne, useContext: Ne, useEffect: Ne, useImperativeHandle: Ne, useInsertionEffect: Ne, useLayoutEffect: Ne, useMemo: Ne, useReducer: Ne, useRef: Ne, useState: Ne, useDebugValue: Ne, useDeferredValue: Ne, useTransition: Ne, useMutableSource: Ne, useSyncExternalStore: Ne, useId: Ne, unstable_isNewReconciler: !1 }, Gf = { readContext: ot, useCallback: function(e, t) {
    return Pt().memoizedState = [e, t === void 0 ? null : t], e;
  }, useContext: ot, useEffect: Au, useImperativeHandle: function(e, t, n) {
    return n = n != null ? n.concat([e]) : null, $i(
      4194308,
      4,
      Nu.bind(null, t, e),
      n
    );
  }, useLayoutEffect: function(e, t) {
    return $i(4194308, 4, e, t);
  }, useInsertionEffect: function(e, t) {
    return $i(4, 2, e, t);
  }, useMemo: function(e, t) {
    var n = Pt();
    return t = t === void 0 ? null : t, e = e(), n.memoizedState = [e, t], e;
  }, useReducer: function(e, t, n) {
    var r = Pt();
    return t = n !== void 0 ? n(t) : t, r.memoizedState = r.baseState = t, e = { pending: null, interleaved: null, lanes: 0, dispatch: null, lastRenderedReducer: e, lastRenderedState: t }, r.queue = e, e = e.dispatch = Bf.bind(null, me, e), [r.memoizedState, e];
  }, useRef: function(e) {
    var t = Pt();
    return e = { current: e }, t.memoizedState = e;
  }, useState: Iu, useDebugValue: Ml, useDeferredValue: function(e) {
    return Pt().memoizedState = e;
  }, useTransition: function() {
    var e = Iu(!1), t = e[0];
    return e = Hf.bind(null, e[1]), Pt().memoizedState = e, [t, e];
  }, useMutableSource: function() {
  }, useSyncExternalStore: function(e, t, n) {
    var r = me, i = Pt();
    if (de) {
      if (n === void 0) throw Error(a(407));
      n = n();
    } else {
      if (n = t(), Pe === null) throw Error(a(349));
      (yn & 30) !== 0 || Eu(r, t, n);
    }
    i.memoizedState = n;
    var l = { value: n, getSnapshot: t };
    return i.queue = l, Au(Tu.bind(
      null,
      r,
      l,
      e
    ), [e]), r.flags |= 2048, Or(9, Cu.bind(null, r, l, n, t), void 0, null), n;
  }, useId: function() {
    var e = Pt(), t = Pe.identifierPrefix;
    if (de) {
      var n = Nt, r = Dt;
      n = (r & ~(1 << 32 - ft(r) - 1)).toString(32) + n, t = ":" + t + "R" + n, n = Nr++, 0 < n && (t += "H" + n.toString(32)), t += ":";
    } else n = Wf++, t = ":" + t + "r" + n.toString(32) + ":";
    return e.memoizedState = t;
  }, unstable_isNewReconciler: !1 }, Qf = {
    readContext: ot,
    useCallback: Ou,
    useContext: ot,
    useEffect: Ol,
    useImperativeHandle: zu,
    useInsertionEffect: Ru,
    useLayoutEffect: Du,
    useMemo: Mu,
    useReducer: Nl,
    useRef: xu,
    useState: function() {
      return Nl(zr);
    },
    useDebugValue: Ml,
    useDeferredValue: function(e) {
      var t = lt();
      return Lu(t, Ee.memoizedState, e);
    },
    useTransition: function() {
      var e = Nl(zr)[0], t = lt().memoizedState;
      return [e, t];
    },
    useMutableSource: Su,
    useSyncExternalStore: _u,
    useId: $u,
    unstable_isNewReconciler: !1
  }, bf = { readContext: ot, useCallback: Ou, useContext: ot, useEffect: Ol, useImperativeHandle: zu, useInsertionEffect: Ru, useLayoutEffect: Du, useMemo: Mu, useReducer: zl, useRef: xu, useState: function() {
    return zl(zr);
  }, useDebugValue: Ml, useDeferredValue: function(e) {
    var t = lt();
    return Ee === null ? t.memoizedState = e : Lu(t, Ee.memoizedState, e);
  }, useTransition: function() {
    var e = zl(zr)[0], t = lt().memoizedState;
    return [e, t];
  }, useMutableSource: Su, useSyncExternalStore: _u, useId: $u, unstable_isNewReconciler: !1 };
  function gt(e, t) {
    if (e && e.defaultProps) {
      t = O({}, t), e = e.defaultProps;
      for (var n in e) t[n] === void 0 && (t[n] = e[n]);
      return t;
    }
    return t;
  }
  function Ll(e, t, n, r) {
    t = e.memoizedState, n = n(r, t), n = n == null ? t : O({}, t, n), e.memoizedState = n, e.lanes === 0 && (e.updateQueue.baseState = n);
  }
  var Vi = { isMounted: function(e) {
    return (e = e._reactInternals) ? dn(e) === e : !1;
  }, enqueueSetState: function(e, t, n) {
    e = e._reactInternals;
    var r = $e(), i = nn(e), l = Ot(r, i);
    l.payload = t, n != null && (l.callback = n), t = Jt(e, l, i), t !== null && (yt(t, e, i, r), Ni(t, e, i));
  }, enqueueReplaceState: function(e, t, n) {
    e = e._reactInternals;
    var r = $e(), i = nn(e), l = Ot(r, i);
    l.tag = 1, l.payload = t, n != null && (l.callback = n), t = Jt(e, l, i), t !== null && (yt(t, e, i, r), Ni(t, e, i));
  }, enqueueForceUpdate: function(e, t) {
    e = e._reactInternals;
    var n = $e(), r = nn(e), i = Ot(n, r);
    i.tag = 2, t != null && (i.callback = t), t = Jt(e, i, r), t !== null && (yt(t, e, r, n), Ni(t, e, r));
  } };
  function Wu(e, t, n, r, i, l, c) {
    return e = e.stateNode, typeof e.shouldComponentUpdate == "function" ? e.shouldComponentUpdate(r, l, c) : t.prototype && t.prototype.isPureReactComponent ? !Sr(n, r) || !Sr(i, l) : !0;
  }
  function Hu(e, t, n) {
    var r = !1, i = Yt, l = t.contextType;
    return typeof l == "object" && l !== null ? l = ot(l) : (i = Ve(t) ? pn : De.current, r = t.contextTypes, l = (r = r != null) ? Vn(e, i) : Yt), t = new t(n, l), e.memoizedState = t.state !== null && t.state !== void 0 ? t.state : null, t.updater = Vi, e.stateNode = t, t._reactInternals = e, r && (e = e.stateNode, e.__reactInternalMemoizedUnmaskedChildContext = i, e.__reactInternalMemoizedMaskedChildContext = l), t;
  }
  function Bu(e, t, n, r) {
    e = t.state, typeof t.componentWillReceiveProps == "function" && t.componentWillReceiveProps(n, r), typeof t.UNSAFE_componentWillReceiveProps == "function" && t.UNSAFE_componentWillReceiveProps(n, r), t.state !== e && Vi.enqueueReplaceState(t, t.state, null);
  }
  function $l(e, t, n, r) {
    var i = e.stateNode;
    i.props = n, i.state = e.memoizedState, i.refs = {}, Cl(e);
    var l = t.contextType;
    typeof l == "object" && l !== null ? i.context = ot(l) : (l = Ve(t) ? pn : De.current, i.context = Vn(e, l)), i.state = e.memoizedState, l = t.getDerivedStateFromProps, typeof l == "function" && (Ll(e, t, l, n), i.state = e.memoizedState), typeof t.getDerivedStateFromProps == "function" || typeof i.getSnapshotBeforeUpdate == "function" || typeof i.UNSAFE_componentWillMount != "function" && typeof i.componentWillMount != "function" || (t = i.state, typeof i.componentWillMount == "function" && i.componentWillMount(), typeof i.UNSAFE_componentWillMount == "function" && i.UNSAFE_componentWillMount(), t !== i.state && Vi.enqueueReplaceState(i, i.state, null), zi(e, n, i, r), i.state = e.memoizedState), typeof i.componentDidMount == "function" && (e.flags |= 4194308);
  }
  function Yn(e, t) {
    try {
      var n = "", r = t;
      do
        n += Z(r), r = r.return;
      while (r);
      var i = n;
    } catch (l) {
      i = `
Error generating stack: ` + l.message + `
` + l.stack;
    }
    return { value: e, source: t, stack: i, digest: null };
  }
  function Fl(e, t, n) {
    return { value: e, source: null, stack: n ?? null, digest: t ?? null };
  }
  function Ul(e, t) {
    try {
      console.error(t.value);
    } catch (n) {
      setTimeout(function() {
        throw n;
      });
    }
  }
  var Yf = typeof WeakMap == "function" ? WeakMap : Map;
  function Ku(e, t, n) {
    n = Ot(-1, n), n.tag = 3, n.payload = { element: null };
    var r = t.value;
    return n.callback = function() {
      bi || (bi = !0, ta = r), Ul(e, t);
    }, n;
  }
  function Gu(e, t, n) {
    n = Ot(-1, n), n.tag = 3;
    var r = e.type.getDerivedStateFromError;
    if (typeof r == "function") {
      var i = t.value;
      n.payload = function() {
        return r(i);
      }, n.callback = function() {
        Ul(e, t);
      };
    }
    var l = e.stateNode;
    return l !== null && typeof l.componentDidCatch == "function" && (n.callback = function() {
      Ul(e, t), typeof r != "function" && (en === null ? en = /* @__PURE__ */ new Set([this]) : en.add(this));
      var c = t.stack;
      this.componentDidCatch(t.value, { componentStack: c !== null ? c : "" });
    }), n;
  }
  function Qu(e, t, n) {
    var r = e.pingCache;
    if (r === null) {
      r = e.pingCache = new Yf();
      var i = /* @__PURE__ */ new Set();
      r.set(t, i);
    } else i = r.get(t), i === void 0 && (i = /* @__PURE__ */ new Set(), r.set(t, i));
    i.has(n) || (i.add(n), e = up.bind(null, e, t, n), t.then(e, e));
  }
  function bu(e) {
    do {
      var t;
      if ((t = e.tag === 13) && (t = e.memoizedState, t = t !== null ? t.dehydrated !== null : !0), t) return e;
      e = e.return;
    } while (e !== null);
    return null;
  }
  function Yu(e, t, n, r, i) {
    return (e.mode & 1) === 0 ? (e === t ? e.flags |= 65536 : (e.flags |= 128, n.flags |= 131072, n.flags &= -52805, n.tag === 1 && (n.alternate === null ? n.tag = 17 : (t = Ot(-1, 1), t.tag = 2, Jt(n, t, 1))), n.lanes |= 1), e) : (e.flags |= 65536, e.lanes = i, e);
  }
  var Xf = q.ReactCurrentOwner, We = !1;
  function Le(e, t, n, r) {
    t.child = e === null ? gu(t, null, n, r) : Kn(t, e.child, n, r);
  }
  function Xu(e, t, n, r, i) {
    n = n.render;
    var l = t.ref;
    return Qn(t, i), r = Rl(e, t, n, r, l, i), n = Dl(), e !== null && !We ? (t.updateQueue = e.updateQueue, t.flags &= -2053, e.lanes &= ~i, Mt(e, t, i)) : (de && n && ml(t), t.flags |= 1, Le(e, t, r, i), t.child);
  }
  function qu(e, t, n, r, i) {
    if (e === null) {
      var l = n.type;
      return typeof l == "function" && !sa(l) && l.defaultProps === void 0 && n.compare === null && n.defaultProps === void 0 ? (t.tag = 15, t.type = l, Ju(e, t, l, r, i)) : (e = eo(n.type, null, r, t, t.mode, i), e.ref = t.ref, e.return = t, t.child = e);
    }
    if (l = e.child, (e.lanes & i) === 0) {
      var c = l.memoizedProps;
      if (n = n.compare, n = n !== null ? n : Sr, n(c, r) && e.ref === t.ref) return Mt(e, t, i);
    }
    return t.flags |= 1, e = on(l, r), e.ref = t.ref, e.return = t, t.child = e;
  }
  function Ju(e, t, n, r, i) {
    if (e !== null) {
      var l = e.memoizedProps;
      if (Sr(l, r) && e.ref === t.ref) if (We = !1, t.pendingProps = r = l, (e.lanes & i) !== 0) (e.flags & 131072) !== 0 && (We = !0);
      else return t.lanes = e.lanes, Mt(e, t, i);
    }
    return Vl(e, t, n, r, i);
  }
  function Zu(e, t, n) {
    var r = t.pendingProps, i = r.children, l = e !== null ? e.memoizedState : null;
    if (r.mode === "hidden") if ((t.mode & 1) === 0) t.memoizedState = { baseLanes: 0, cachePool: null, transitions: null }, le(qn, Ze), Ze |= n;
    else {
      if ((n & 1073741824) === 0) return e = l !== null ? l.baseLanes | n : n, t.lanes = t.childLanes = 1073741824, t.memoizedState = { baseLanes: e, cachePool: null, transitions: null }, t.updateQueue = null, le(qn, Ze), Ze |= e, null;
      t.memoizedState = { baseLanes: 0, cachePool: null, transitions: null }, r = l !== null ? l.baseLanes : n, le(qn, Ze), Ze |= r;
    }
    else l !== null ? (r = l.baseLanes | n, t.memoizedState = null) : r = n, le(qn, Ze), Ze |= r;
    return Le(e, t, i, n), t.child;
  }
  function ec(e, t) {
    var n = t.ref;
    (e === null && n !== null || e !== null && e.ref !== n) && (t.flags |= 512, t.flags |= 2097152);
  }
  function Vl(e, t, n, r, i) {
    var l = Ve(n) ? pn : De.current;
    return l = Vn(t, l), Qn(t, i), n = Rl(e, t, n, r, l, i), r = Dl(), e !== null && !We ? (t.updateQueue = e.updateQueue, t.flags &= -2053, e.lanes &= ~i, Mt(e, t, i)) : (de && r && ml(t), t.flags |= 1, Le(e, t, n, i), t.child);
  }
  function tc(e, t, n, r, i) {
    if (Ve(n)) {
      var l = !0;
      Ti(t);
    } else l = !1;
    if (Qn(t, i), t.stateNode === null) Hi(e, t), Hu(t, n, r), $l(t, n, r, i), r = !0;
    else if (e === null) {
      var c = t.stateNode, g = t.memoizedProps;
      c.props = g;
      var v = c.context, _ = n.contextType;
      typeof _ == "object" && _ !== null ? _ = ot(_) : (_ = Ve(n) ? pn : De.current, _ = Vn(t, _));
      var j = n.getDerivedStateFromProps, I = typeof j == "function" || typeof c.getSnapshotBeforeUpdate == "function";
      I || typeof c.UNSAFE_componentWillReceiveProps != "function" && typeof c.componentWillReceiveProps != "function" || (g !== r || v !== _) && Bu(t, c, r, _), qt = !1;
      var T = t.memoizedState;
      c.state = T, zi(t, r, c, i), v = t.memoizedState, g !== r || T !== v || Ue.current || qt ? (typeof j == "function" && (Ll(t, n, j, r), v = t.memoizedState), (g = qt || Wu(t, n, g, r, T, v, _)) ? (I || typeof c.UNSAFE_componentWillMount != "function" && typeof c.componentWillMount != "function" || (typeof c.componentWillMount == "function" && c.componentWillMount(), typeof c.UNSAFE_componentWillMount == "function" && c.UNSAFE_componentWillMount()), typeof c.componentDidMount == "function" && (t.flags |= 4194308)) : (typeof c.componentDidMount == "function" && (t.flags |= 4194308), t.memoizedProps = r, t.memoizedState = v), c.props = r, c.state = v, c.context = _, r = g) : (typeof c.componentDidMount == "function" && (t.flags |= 4194308), r = !1);
    } else {
      c = t.stateNode, vu(e, t), g = t.memoizedProps, _ = t.type === t.elementType ? g : gt(t.type, g), c.props = _, I = t.pendingProps, T = c.context, v = n.contextType, typeof v == "object" && v !== null ? v = ot(v) : (v = Ve(n) ? pn : De.current, v = Vn(t, v));
      var D = n.getDerivedStateFromProps;
      (j = typeof D == "function" || typeof c.getSnapshotBeforeUpdate == "function") || typeof c.UNSAFE_componentWillReceiveProps != "function" && typeof c.componentWillReceiveProps != "function" || (g !== I || T !== v) && Bu(t, c, r, v), qt = !1, T = t.memoizedState, c.state = T, zi(t, r, c, i);
      var L = t.memoizedState;
      g !== I || T !== L || Ue.current || qt ? (typeof D == "function" && (Ll(t, n, D, r), L = t.memoizedState), (_ = qt || Wu(t, n, _, r, T, L, v) || !1) ? (j || typeof c.UNSAFE_componentWillUpdate != "function" && typeof c.componentWillUpdate != "function" || (typeof c.componentWillUpdate == "function" && c.componentWillUpdate(r, L, v), typeof c.UNSAFE_componentWillUpdate == "function" && c.UNSAFE_componentWillUpdate(r, L, v)), typeof c.componentDidUpdate == "function" && (t.flags |= 4), typeof c.getSnapshotBeforeUpdate == "function" && (t.flags |= 1024)) : (typeof c.componentDidUpdate != "function" || g === e.memoizedProps && T === e.memoizedState || (t.flags |= 4), typeof c.getSnapshotBeforeUpdate != "function" || g === e.memoizedProps && T === e.memoizedState || (t.flags |= 1024), t.memoizedProps = r, t.memoizedState = L), c.props = r, c.state = L, c.context = v, r = _) : (typeof c.componentDidUpdate != "function" || g === e.memoizedProps && T === e.memoizedState || (t.flags |= 4), typeof c.getSnapshotBeforeUpdate != "function" || g === e.memoizedProps && T === e.memoizedState || (t.flags |= 1024), r = !1);
    }
    return Wl(e, t, n, r, l, i);
  }
  function Wl(e, t, n, r, i, l) {
    ec(e, t);
    var c = (t.flags & 128) !== 0;
    if (!r && !c) return i && lu(t, n, !1), Mt(e, t, l);
    r = t.stateNode, Xf.current = t;
    var g = c && typeof n.getDerivedStateFromError != "function" ? null : r.render();
    return t.flags |= 1, e !== null && c ? (t.child = Kn(t, e.child, null, l), t.child = Kn(t, null, g, l)) : Le(e, t, g, l), t.memoizedState = r.state, i && lu(t, n, !0), t.child;
  }
  function nc(e) {
    var t = e.stateNode;
    t.pendingContext ? iu(e, t.pendingContext, t.pendingContext !== t.context) : t.context && iu(e, t.context, !1), Tl(e, t.containerInfo);
  }
  function rc(e, t, n, r, i) {
    return Bn(), yl(i), t.flags |= 256, Le(e, t, n, r), t.child;
  }
  var Hl = { dehydrated: null, treeContext: null, retryLane: 0 };
  function Bl(e) {
    return { baseLanes: e, cachePool: null, transitions: null };
  }
  function ic(e, t, n) {
    var r = t.pendingProps, i = pe.current, l = !1, c = (t.flags & 128) !== 0, g;
    if ((g = c) || (g = e !== null && e.memoizedState === null ? !1 : (i & 2) !== 0), g ? (l = !0, t.flags &= -129) : (e === null || e.memoizedState !== null) && (i |= 1), le(pe, i & 1), e === null)
      return vl(t), e = t.memoizedState, e !== null && (e = e.dehydrated, e !== null) ? ((t.mode & 1) === 0 ? t.lanes = 1 : e.data === "$!" ? t.lanes = 8 : t.lanes = 1073741824, null) : (c = r.children, e = r.fallback, l ? (r = t.mode, l = t.child, c = { mode: "hidden", children: c }, (r & 1) === 0 && l !== null ? (l.childLanes = 0, l.pendingProps = c) : l = to(c, r, 0, null), e = En(e, r, n, null), l.return = t, e.return = t, l.sibling = e, t.child = l, t.child.memoizedState = Bl(n), t.memoizedState = Hl, e) : Kl(t, c));
    if (i = e.memoizedState, i !== null && (g = i.dehydrated, g !== null)) return qf(e, t, c, r, g, i, n);
    if (l) {
      l = r.fallback, c = t.mode, i = e.child, g = i.sibling;
      var v = { mode: "hidden", children: r.children };
      return (c & 1) === 0 && t.child !== i ? (r = t.child, r.childLanes = 0, r.pendingProps = v, t.deletions = null) : (r = on(i, v), r.subtreeFlags = i.subtreeFlags & 14680064), g !== null ? l = on(g, l) : (l = En(l, c, n, null), l.flags |= 2), l.return = t, r.return = t, r.sibling = l, t.child = r, r = l, l = t.child, c = e.child.memoizedState, c = c === null ? Bl(n) : { baseLanes: c.baseLanes | n, cachePool: null, transitions: c.transitions }, l.memoizedState = c, l.childLanes = e.childLanes & ~n, t.memoizedState = Hl, r;
    }
    return l = e.child, e = l.sibling, r = on(l, { mode: "visible", children: r.children }), (t.mode & 1) === 0 && (r.lanes = n), r.return = t, r.sibling = null, e !== null && (n = t.deletions, n === null ? (t.deletions = [e], t.flags |= 16) : n.push(e)), t.child = r, t.memoizedState = null, r;
  }
  function Kl(e, t) {
    return t = to({ mode: "visible", children: t }, e.mode, 0, null), t.return = e, e.child = t;
  }
  function Wi(e, t, n, r) {
    return r !== null && yl(r), Kn(t, e.child, null, n), e = Kl(t, t.pendingProps.children), e.flags |= 2, t.memoizedState = null, e;
  }
  function qf(e, t, n, r, i, l, c) {
    if (n)
      return t.flags & 256 ? (t.flags &= -257, r = Fl(Error(a(422))), Wi(e, t, c, r)) : t.memoizedState !== null ? (t.child = e.child, t.flags |= 128, null) : (l = r.fallback, i = t.mode, r = to({ mode: "visible", children: r.children }, i, 0, null), l = En(l, i, c, null), l.flags |= 2, r.return = t, l.return = t, r.sibling = l, t.child = r, (t.mode & 1) !== 0 && Kn(t, e.child, null, c), t.child.memoizedState = Bl(c), t.memoizedState = Hl, l);
    if ((t.mode & 1) === 0) return Wi(e, t, c, null);
    if (i.data === "$!") {
      if (r = i.nextSibling && i.nextSibling.dataset, r) var g = r.dgst;
      return r = g, l = Error(a(419)), r = Fl(l, r, void 0), Wi(e, t, c, r);
    }
    if (g = (c & e.childLanes) !== 0, We || g) {
      if (r = Pe, r !== null) {
        switch (c & -c) {
          case 4:
            i = 2;
            break;
          case 16:
            i = 8;
            break;
          case 64:
          case 128:
          case 256:
          case 512:
          case 1024:
          case 2048:
          case 4096:
          case 8192:
          case 16384:
          case 32768:
          case 65536:
          case 131072:
          case 262144:
          case 524288:
          case 1048576:
          case 2097152:
          case 4194304:
          case 8388608:
          case 16777216:
          case 33554432:
          case 67108864:
            i = 32;
            break;
          case 536870912:
            i = 268435456;
            break;
          default:
            i = 0;
        }
        i = (i & (r.suspendedLanes | c)) !== 0 ? 0 : i, i !== 0 && i !== l.retryLane && (l.retryLane = i, zt(e, i), yt(r, e, i, -1));
      }
      return aa(), r = Fl(Error(a(421))), Wi(e, t, c, r);
    }
    return i.data === "$?" ? (t.flags |= 128, t.child = e.child, t = cp.bind(null, e), i._reactRetry = t, null) : (e = l.treeContext, Je = Qt(i.nextSibling), qe = t, de = !0, mt = null, e !== null && (rt[it++] = Dt, rt[it++] = Nt, rt[it++] = mn, Dt = e.id, Nt = e.overflow, mn = t), t = Kl(t, r.children), t.flags |= 4096, t);
  }
  function oc(e, t, n) {
    e.lanes |= t;
    var r = e.alternate;
    r !== null && (r.lanes |= t), _l(e.return, t, n);
  }
  function Gl(e, t, n, r, i) {
    var l = e.memoizedState;
    l === null ? e.memoizedState = { isBackwards: t, rendering: null, renderingStartTime: 0, last: r, tail: n, tailMode: i } : (l.isBackwards = t, l.rendering = null, l.renderingStartTime = 0, l.last = r, l.tail = n, l.tailMode = i);
  }
  function lc(e, t, n) {
    var r = t.pendingProps, i = r.revealOrder, l = r.tail;
    if (Le(e, t, r.children, n), r = pe.current, (r & 2) !== 0) r = r & 1 | 2, t.flags |= 128;
    else {
      if (e !== null && (e.flags & 128) !== 0) e: for (e = t.child; e !== null; ) {
        if (e.tag === 13) e.memoizedState !== null && oc(e, n, t);
        else if (e.tag === 19) oc(e, n, t);
        else if (e.child !== null) {
          e.child.return = e, e = e.child;
          continue;
        }
        if (e === t) break e;
        for (; e.sibling === null; ) {
          if (e.return === null || e.return === t) break e;
          e = e.return;
        }
        e.sibling.return = e.return, e = e.sibling;
      }
      r &= 1;
    }
    if (le(pe, r), (t.mode & 1) === 0) t.memoizedState = null;
    else switch (i) {
      case "forwards":
        for (n = t.child, i = null; n !== null; ) e = n.alternate, e !== null && Oi(e) === null && (i = n), n = n.sibling;
        n = i, n === null ? (i = t.child, t.child = null) : (i = n.sibling, n.sibling = null), Gl(t, !1, i, n, l);
        break;
      case "backwards":
        for (n = null, i = t.child, t.child = null; i !== null; ) {
          if (e = i.alternate, e !== null && Oi(e) === null) {
            t.child = i;
            break;
          }
          e = i.sibling, i.sibling = n, n = i, i = e;
        }
        Gl(t, !0, n, null, l);
        break;
      case "together":
        Gl(t, !1, null, null, void 0);
        break;
      default:
        t.memoizedState = null;
    }
    return t.child;
  }
  function Hi(e, t) {
    (t.mode & 1) === 0 && e !== null && (e.alternate = null, t.alternate = null, t.flags |= 2);
  }
  function Mt(e, t, n) {
    if (e !== null && (t.dependencies = e.dependencies), kn |= t.lanes, (n & t.childLanes) === 0) return null;
    if (e !== null && t.child !== e.child) throw Error(a(153));
    if (t.child !== null) {
      for (e = t.child, n = on(e, e.pendingProps), t.child = n, n.return = t; e.sibling !== null; ) e = e.sibling, n = n.sibling = on(e, e.pendingProps), n.return = t;
      n.sibling = null;
    }
    return t.child;
  }
  function Jf(e, t, n) {
    switch (t.tag) {
      case 3:
        nc(t), Bn();
        break;
      case 5:
        wu(t);
        break;
      case 1:
        Ve(t.type) && Ti(t);
        break;
      case 4:
        Tl(t, t.stateNode.containerInfo);
        break;
      case 10:
        var r = t.type._context, i = t.memoizedProps.value;
        le(Ri, r._currentValue), r._currentValue = i;
        break;
      case 13:
        if (r = t.memoizedState, r !== null)
          return r.dehydrated !== null ? (le(pe, pe.current & 1), t.flags |= 128, null) : (n & t.child.childLanes) !== 0 ? ic(e, t, n) : (le(pe, pe.current & 1), e = Mt(e, t, n), e !== null ? e.sibling : null);
        le(pe, pe.current & 1);
        break;
      case 19:
        if (r = (n & t.childLanes) !== 0, (e.flags & 128) !== 0) {
          if (r) return lc(e, t, n);
          t.flags |= 128;
        }
        if (i = t.memoizedState, i !== null && (i.rendering = null, i.tail = null, i.lastEffect = null), le(pe, pe.current), r) break;
        return null;
      case 22:
      case 23:
        return t.lanes = 0, Zu(e, t, n);
    }
    return Mt(e, t, n);
  }
  var ac, Ql, sc, uc;
  ac = function(e, t) {
    for (var n = t.child; n !== null; ) {
      if (n.tag === 5 || n.tag === 6) e.appendChild(n.stateNode);
      else if (n.tag !== 4 && n.child !== null) {
        n.child.return = n, n = n.child;
        continue;
      }
      if (n === t) break;
      for (; n.sibling === null; ) {
        if (n.return === null || n.return === t) return;
        n = n.return;
      }
      n.sibling.return = n.return, n = n.sibling;
    }
  }, Ql = function() {
  }, sc = function(e, t, n, r) {
    var i = e.memoizedProps;
    if (i !== r) {
      e = t.stateNode, vn(Tt.current);
      var l = null;
      switch (n) {
        case "input":
          i = _o(e, i), r = _o(e, r), l = [];
          break;
        case "select":
          i = O({}, i, { value: void 0 }), r = O({}, r, { value: void 0 }), l = [];
          break;
        case "textarea":
          i = To(e, i), r = To(e, r), l = [];
          break;
        default:
          typeof i.onClick != "function" && typeof r.onClick == "function" && (e.onclick = _i);
      }
      jo(n, r);
      var c;
      n = null;
      for (_ in i) if (!r.hasOwnProperty(_) && i.hasOwnProperty(_) && i[_] != null) if (_ === "style") {
        var g = i[_];
        for (c in g) g.hasOwnProperty(c) && (n || (n = {}), n[c] = "");
      } else _ !== "dangerouslySetInnerHTML" && _ !== "children" && _ !== "suppressContentEditableWarning" && _ !== "suppressHydrationWarning" && _ !== "autoFocus" && (f.hasOwnProperty(_) ? l || (l = []) : (l = l || []).push(_, null));
      for (_ in r) {
        var v = r[_];
        if (g = i != null ? i[_] : void 0, r.hasOwnProperty(_) && v !== g && (v != null || g != null)) if (_ === "style") if (g) {
          for (c in g) !g.hasOwnProperty(c) || v && v.hasOwnProperty(c) || (n || (n = {}), n[c] = "");
          for (c in v) v.hasOwnProperty(c) && g[c] !== v[c] && (n || (n = {}), n[c] = v[c]);
        } else n || (l || (l = []), l.push(
          _,
          n
        )), n = v;
        else _ === "dangerouslySetInnerHTML" ? (v = v ? v.__html : void 0, g = g ? g.__html : void 0, v != null && g !== v && (l = l || []).push(_, v)) : _ === "children" ? typeof v != "string" && typeof v != "number" || (l = l || []).push(_, "" + v) : _ !== "suppressContentEditableWarning" && _ !== "suppressHydrationWarning" && (f.hasOwnProperty(_) ? (v != null && _ === "onScroll" && se("scroll", e), l || g === v || (l = [])) : (l = l || []).push(_, v));
      }
      n && (l = l || []).push("style", n);
      var _ = l;
      (t.updateQueue = _) && (t.flags |= 4);
    }
  }, uc = function(e, t, n, r) {
    n !== r && (t.flags |= 4);
  };
  function Mr(e, t) {
    if (!de) switch (e.tailMode) {
      case "hidden":
        t = e.tail;
        for (var n = null; t !== null; ) t.alternate !== null && (n = t), t = t.sibling;
        n === null ? e.tail = null : n.sibling = null;
        break;
      case "collapsed":
        n = e.tail;
        for (var r = null; n !== null; ) n.alternate !== null && (r = n), n = n.sibling;
        r === null ? t || e.tail === null ? e.tail = null : e.tail.sibling = null : r.sibling = null;
    }
  }
  function ze(e) {
    var t = e.alternate !== null && e.alternate.child === e.child, n = 0, r = 0;
    if (t) for (var i = e.child; i !== null; ) n |= i.lanes | i.childLanes, r |= i.subtreeFlags & 14680064, r |= i.flags & 14680064, i.return = e, i = i.sibling;
    else for (i = e.child; i !== null; ) n |= i.lanes | i.childLanes, r |= i.subtreeFlags, r |= i.flags, i.return = e, i = i.sibling;
    return e.subtreeFlags |= r, e.childLanes = n, t;
  }
  function Zf(e, t, n) {
    var r = t.pendingProps;
    switch (gl(t), t.tag) {
      case 2:
      case 16:
      case 15:
      case 0:
      case 11:
      case 7:
      case 8:
      case 12:
      case 9:
      case 14:
        return ze(t), null;
      case 1:
        return Ve(t.type) && Ci(), ze(t), null;
      case 3:
        return r = t.stateNode, bn(), ue(Ue), ue(De), Il(), r.pendingContext && (r.context = r.pendingContext, r.pendingContext = null), (e === null || e.child === null) && (xi(t) ? t.flags |= 4 : e === null || e.memoizedState.isDehydrated && (t.flags & 256) === 0 || (t.flags |= 1024, mt !== null && (ia(mt), mt = null))), Ql(e, t), ze(t), null;
      case 5:
        Pl(t);
        var i = vn(Rr.current);
        if (n = t.type, e !== null && t.stateNode != null) sc(e, t, n, r, i), e.ref !== t.ref && (t.flags |= 512, t.flags |= 2097152);
        else {
          if (!r) {
            if (t.stateNode === null) throw Error(a(166));
            return ze(t), null;
          }
          if (e = vn(Tt.current), xi(t)) {
            r = t.stateNode, n = t.type;
            var l = t.memoizedProps;
            switch (r[Ct] = t, r[Pr] = l, e = (t.mode & 1) !== 0, n) {
              case "dialog":
                se("cancel", r), se("close", r);
                break;
              case "iframe":
              case "object":
              case "embed":
                se("load", r);
                break;
              case "video":
              case "audio":
                for (i = 0; i < Er.length; i++) se(Er[i], r);
                break;
              case "source":
                se("error", r);
                break;
              case "img":
              case "image":
              case "link":
                se(
                  "error",
                  r
                ), se("load", r);
                break;
              case "details":
                se("toggle", r);
                break;
              case "input":
                Ha(r, l), se("invalid", r);
                break;
              case "select":
                r._wrapperState = { wasMultiple: !!l.multiple }, se("invalid", r);
                break;
              case "textarea":
                Ga(r, l), se("invalid", r);
            }
            jo(n, l), i = null;
            for (var c in l) if (l.hasOwnProperty(c)) {
              var g = l[c];
              c === "children" ? typeof g == "string" ? r.textContent !== g && (l.suppressHydrationWarning !== !0 && Si(r.textContent, g, e), i = ["children", g]) : typeof g == "number" && r.textContent !== "" + g && (l.suppressHydrationWarning !== !0 && Si(
                r.textContent,
                g,
                e
              ), i = ["children", "" + g]) : f.hasOwnProperty(c) && g != null && c === "onScroll" && se("scroll", r);
            }
            switch (n) {
              case "input":
                Jr(r), Ka(r, l, !0);
                break;
              case "textarea":
                Jr(r), ba(r);
                break;
              case "select":
              case "option":
                break;
              default:
                typeof l.onClick == "function" && (r.onclick = _i);
            }
            r = i, t.updateQueue = r, r !== null && (t.flags |= 4);
          } else {
            c = i.nodeType === 9 ? i : i.ownerDocument, e === "http://www.w3.org/1999/xhtml" && (e = Ya(n)), e === "http://www.w3.org/1999/xhtml" ? n === "script" ? (e = c.createElement("div"), e.innerHTML = "<script><\/script>", e = e.removeChild(e.firstChild)) : typeof r.is == "string" ? e = c.createElement(n, { is: r.is }) : (e = c.createElement(n), n === "select" && (c = e, r.multiple ? c.multiple = !0 : r.size && (c.size = r.size))) : e = c.createElementNS(e, n), e[Ct] = t, e[Pr] = r, ac(e, t, !1, !1), t.stateNode = e;
            e: {
              switch (c = Io(n, r), n) {
                case "dialog":
                  se("cancel", e), se("close", e), i = r;
                  break;
                case "iframe":
                case "object":
                case "embed":
                  se("load", e), i = r;
                  break;
                case "video":
                case "audio":
                  for (i = 0; i < Er.length; i++) se(Er[i], e);
                  i = r;
                  break;
                case "source":
                  se("error", e), i = r;
                  break;
                case "img":
                case "image":
                case "link":
                  se(
                    "error",
                    e
                  ), se("load", e), i = r;
                  break;
                case "details":
                  se("toggle", e), i = r;
                  break;
                case "input":
                  Ha(e, r), i = _o(e, r), se("invalid", e);
                  break;
                case "option":
                  i = r;
                  break;
                case "select":
                  e._wrapperState = { wasMultiple: !!r.multiple }, i = O({}, r, { value: void 0 }), se("invalid", e);
                  break;
                case "textarea":
                  Ga(e, r), i = To(e, r), se("invalid", e);
                  break;
                default:
                  i = r;
              }
              jo(n, i), g = i;
              for (l in g) if (g.hasOwnProperty(l)) {
                var v = g[l];
                l === "style" ? Ja(e, v) : l === "dangerouslySetInnerHTML" ? (v = v ? v.__html : void 0, v != null && Xa(e, v)) : l === "children" ? typeof v == "string" ? (n !== "textarea" || v !== "") && ir(e, v) : typeof v == "number" && ir(e, "" + v) : l !== "suppressContentEditableWarning" && l !== "suppressHydrationWarning" && l !== "autoFocus" && (f.hasOwnProperty(l) ? v != null && l === "onScroll" && se("scroll", e) : v != null && fe(e, l, v, c));
              }
              switch (n) {
                case "input":
                  Jr(e), Ka(e, r, !1);
                  break;
                case "textarea":
                  Jr(e), ba(e);
                  break;
                case "option":
                  r.value != null && e.setAttribute("value", "" + ne(r.value));
                  break;
                case "select":
                  e.multiple = !!r.multiple, l = r.value, l != null ? xn(e, !!r.multiple, l, !1) : r.defaultValue != null && xn(
                    e,
                    !!r.multiple,
                    r.defaultValue,
                    !0
                  );
                  break;
                default:
                  typeof i.onClick == "function" && (e.onclick = _i);
              }
              switch (n) {
                case "button":
                case "input":
                case "select":
                case "textarea":
                  r = !!r.autoFocus;
                  break e;
                case "img":
                  r = !0;
                  break e;
                default:
                  r = !1;
              }
            }
            r && (t.flags |= 4);
          }
          t.ref !== null && (t.flags |= 512, t.flags |= 2097152);
        }
        return ze(t), null;
      case 6:
        if (e && t.stateNode != null) uc(e, t, e.memoizedProps, r);
        else {
          if (typeof r != "string" && t.stateNode === null) throw Error(a(166));
          if (n = vn(Rr.current), vn(Tt.current), xi(t)) {
            if (r = t.stateNode, n = t.memoizedProps, r[Ct] = t, (l = r.nodeValue !== n) && (e = qe, e !== null)) switch (e.tag) {
              case 3:
                Si(r.nodeValue, n, (e.mode & 1) !== 0);
                break;
              case 5:
                e.memoizedProps.suppressHydrationWarning !== !0 && Si(r.nodeValue, n, (e.mode & 1) !== 0);
            }
            l && (t.flags |= 4);
          } else r = (n.nodeType === 9 ? n : n.ownerDocument).createTextNode(r), r[Ct] = t, t.stateNode = r;
        }
        return ze(t), null;
      case 13:
        if (ue(pe), r = t.memoizedState, e === null || e.memoizedState !== null && e.memoizedState.dehydrated !== null) {
          if (de && Je !== null && (t.mode & 1) !== 0 && (t.flags & 128) === 0) fu(), Bn(), t.flags |= 98560, l = !1;
          else if (l = xi(t), r !== null && r.dehydrated !== null) {
            if (e === null) {
              if (!l) throw Error(a(318));
              if (l = t.memoizedState, l = l !== null ? l.dehydrated : null, !l) throw Error(a(317));
              l[Ct] = t;
            } else Bn(), (t.flags & 128) === 0 && (t.memoizedState = null), t.flags |= 4;
            ze(t), l = !1;
          } else mt !== null && (ia(mt), mt = null), l = !0;
          if (!l) return t.flags & 65536 ? t : null;
        }
        return (t.flags & 128) !== 0 ? (t.lanes = n, t) : (r = r !== null, r !== (e !== null && e.memoizedState !== null) && r && (t.child.flags |= 8192, (t.mode & 1) !== 0 && (e === null || (pe.current & 1) !== 0 ? Ce === 0 && (Ce = 3) : aa())), t.updateQueue !== null && (t.flags |= 4), ze(t), null);
      case 4:
        return bn(), Ql(e, t), e === null && Cr(t.stateNode.containerInfo), ze(t), null;
      case 10:
        return Sl(t.type._context), ze(t), null;
      case 17:
        return Ve(t.type) && Ci(), ze(t), null;
      case 19:
        if (ue(pe), l = t.memoizedState, l === null) return ze(t), null;
        if (r = (t.flags & 128) !== 0, c = l.rendering, c === null) if (r) Mr(l, !1);
        else {
          if (Ce !== 0 || e !== null && (e.flags & 128) !== 0) for (e = t.child; e !== null; ) {
            if (c = Oi(e), c !== null) {
              for (t.flags |= 128, Mr(l, !1), r = c.updateQueue, r !== null && (t.updateQueue = r, t.flags |= 4), t.subtreeFlags = 0, r = n, n = t.child; n !== null; ) l = n, e = r, l.flags &= 14680066, c = l.alternate, c === null ? (l.childLanes = 0, l.lanes = e, l.child = null, l.subtreeFlags = 0, l.memoizedProps = null, l.memoizedState = null, l.updateQueue = null, l.dependencies = null, l.stateNode = null) : (l.childLanes = c.childLanes, l.lanes = c.lanes, l.child = c.child, l.subtreeFlags = 0, l.deletions = null, l.memoizedProps = c.memoizedProps, l.memoizedState = c.memoizedState, l.updateQueue = c.updateQueue, l.type = c.type, e = c.dependencies, l.dependencies = e === null ? null : { lanes: e.lanes, firstContext: e.firstContext }), n = n.sibling;
              return le(pe, pe.current & 1 | 2), t.child;
            }
            e = e.sibling;
          }
          l.tail !== null && ye() > Jn && (t.flags |= 128, r = !0, Mr(l, !1), t.lanes = 4194304);
        }
        else {
          if (!r) if (e = Oi(c), e !== null) {
            if (t.flags |= 128, r = !0, n = e.updateQueue, n !== null && (t.updateQueue = n, t.flags |= 4), Mr(l, !0), l.tail === null && l.tailMode === "hidden" && !c.alternate && !de) return ze(t), null;
          } else 2 * ye() - l.renderingStartTime > Jn && n !== 1073741824 && (t.flags |= 128, r = !0, Mr(l, !1), t.lanes = 4194304);
          l.isBackwards ? (c.sibling = t.child, t.child = c) : (n = l.last, n !== null ? n.sibling = c : t.child = c, l.last = c);
        }
        return l.tail !== null ? (t = l.tail, l.rendering = t, l.tail = t.sibling, l.renderingStartTime = ye(), t.sibling = null, n = pe.current, le(pe, r ? n & 1 | 2 : n & 1), t) : (ze(t), null);
      case 22:
      case 23:
        return la(), r = t.memoizedState !== null, e !== null && e.memoizedState !== null !== r && (t.flags |= 8192), r && (t.mode & 1) !== 0 ? (Ze & 1073741824) !== 0 && (ze(t), t.subtreeFlags & 6 && (t.flags |= 8192)) : ze(t), null;
      case 24:
        return null;
      case 25:
        return null;
    }
    throw Error(a(156, t.tag));
  }
  function ep(e, t) {
    switch (gl(t), t.tag) {
      case 1:
        return Ve(t.type) && Ci(), e = t.flags, e & 65536 ? (t.flags = e & -65537 | 128, t) : null;
      case 3:
        return bn(), ue(Ue), ue(De), Il(), e = t.flags, (e & 65536) !== 0 && (e & 128) === 0 ? (t.flags = e & -65537 | 128, t) : null;
      case 5:
        return Pl(t), null;
      case 13:
        if (ue(pe), e = t.memoizedState, e !== null && e.dehydrated !== null) {
          if (t.alternate === null) throw Error(a(340));
          Bn();
        }
        return e = t.flags, e & 65536 ? (t.flags = e & -65537 | 128, t) : null;
      case 19:
        return ue(pe), null;
      case 4:
        return bn(), null;
      case 10:
        return Sl(t.type._context), null;
      case 22:
      case 23:
        return la(), null;
      case 24:
        return null;
      default:
        return null;
    }
  }
  var Bi = !1, Oe = !1, tp = typeof WeakSet == "function" ? WeakSet : Set, N = null;
  function Xn(e, t) {
    var n = e.ref;
    if (n !== null) if (typeof n == "function") try {
      n(null);
    } catch (r) {
      ve(e, t, r);
    }
    else n.current = null;
  }
  function bl(e, t, n) {
    try {
      n();
    } catch (r) {
      ve(e, t, r);
    }
  }
  var cc = !1;
  function np(e, t) {
    if (ll = ci, e = Ws(), Jo(e)) {
      if ("selectionStart" in e) var n = { start: e.selectionStart, end: e.selectionEnd };
      else e: {
        n = (n = e.ownerDocument) && n.defaultView || window;
        var r = n.getSelection && n.getSelection();
        if (r && r.rangeCount !== 0) {
          n = r.anchorNode;
          var i = r.anchorOffset, l = r.focusNode;
          r = r.focusOffset;
          try {
            n.nodeType, l.nodeType;
          } catch {
            n = null;
            break e;
          }
          var c = 0, g = -1, v = -1, _ = 0, j = 0, I = e, T = null;
          t: for (; ; ) {
            for (var D; I !== n || i !== 0 && I.nodeType !== 3 || (g = c + i), I !== l || r !== 0 && I.nodeType !== 3 || (v = c + r), I.nodeType === 3 && (c += I.nodeValue.length), (D = I.firstChild) !== null; )
              T = I, I = D;
            for (; ; ) {
              if (I === e) break t;
              if (T === n && ++_ === i && (g = c), T === l && ++j === r && (v = c), (D = I.nextSibling) !== null) break;
              I = T, T = I.parentNode;
            }
            I = D;
          }
          n = g === -1 || v === -1 ? null : { start: g, end: v };
        } else n = null;
      }
      n = n || { start: 0, end: 0 };
    } else n = null;
    for (al = { focusedElem: e, selectionRange: n }, ci = !1, N = t; N !== null; ) if (t = N, e = t.child, (t.subtreeFlags & 1028) !== 0 && e !== null) e.return = t, N = e;
    else for (; N !== null; ) {
      t = N;
      try {
        var L = t.alternate;
        if ((t.flags & 1024) !== 0) switch (t.tag) {
          case 0:
          case 11:
          case 15:
            break;
          case 1:
            if (L !== null) {
              var F = L.memoizedProps, ke = L.memoizedState, w = t.stateNode, y = w.getSnapshotBeforeUpdate(t.elementType === t.type ? F : gt(t.type, F), ke);
              w.__reactInternalSnapshotBeforeUpdate = y;
            }
            break;
          case 3:
            var S = t.stateNode.containerInfo;
            S.nodeType === 1 ? S.textContent = "" : S.nodeType === 9 && S.documentElement && S.removeChild(S.documentElement);
            break;
          case 5:
          case 6:
          case 4:
          case 17:
            break;
          default:
            throw Error(a(163));
        }
      } catch (x) {
        ve(t, t.return, x);
      }
      if (e = t.sibling, e !== null) {
        e.return = t.return, N = e;
        break;
      }
      N = t.return;
    }
    return L = cc, cc = !1, L;
  }
  function Lr(e, t, n) {
    var r = t.updateQueue;
    if (r = r !== null ? r.lastEffect : null, r !== null) {
      var i = r = r.next;
      do {
        if ((i.tag & e) === e) {
          var l = i.destroy;
          i.destroy = void 0, l !== void 0 && bl(t, n, l);
        }
        i = i.next;
      } while (i !== r);
    }
  }
  function Ki(e, t) {
    if (t = t.updateQueue, t = t !== null ? t.lastEffect : null, t !== null) {
      var n = t = t.next;
      do {
        if ((n.tag & e) === e) {
          var r = n.create;
          n.destroy = r();
        }
        n = n.next;
      } while (n !== t);
    }
  }
  function Yl(e) {
    var t = e.ref;
    if (t !== null) {
      var n = e.stateNode;
      switch (e.tag) {
        case 5:
          e = n;
          break;
        default:
          e = n;
      }
      typeof t == "function" ? t(e) : t.current = e;
    }
  }
  function dc(e) {
    var t = e.alternate;
    t !== null && (e.alternate = null, dc(t)), e.child = null, e.deletions = null, e.sibling = null, e.tag === 5 && (t = e.stateNode, t !== null && (delete t[Ct], delete t[Pr], delete t[dl], delete t[$f], delete t[Ff])), e.stateNode = null, e.return = null, e.dependencies = null, e.memoizedProps = null, e.memoizedState = null, e.pendingProps = null, e.stateNode = null, e.updateQueue = null;
  }
  function fc(e) {
    return e.tag === 5 || e.tag === 3 || e.tag === 4;
  }
  function pc(e) {
    e: for (; ; ) {
      for (; e.sibling === null; ) {
        if (e.return === null || fc(e.return)) return null;
        e = e.return;
      }
      for (e.sibling.return = e.return, e = e.sibling; e.tag !== 5 && e.tag !== 6 && e.tag !== 18; ) {
        if (e.flags & 2 || e.child === null || e.tag === 4) continue e;
        e.child.return = e, e = e.child;
      }
      if (!(e.flags & 2)) return e.stateNode;
    }
  }
  function Xl(e, t, n) {
    var r = e.tag;
    if (r === 5 || r === 6) e = e.stateNode, t ? n.nodeType === 8 ? n.parentNode.insertBefore(e, t) : n.insertBefore(e, t) : (n.nodeType === 8 ? (t = n.parentNode, t.insertBefore(e, n)) : (t = n, t.appendChild(e)), n = n._reactRootContainer, n != null || t.onclick !== null || (t.onclick = _i));
    else if (r !== 4 && (e = e.child, e !== null)) for (Xl(e, t, n), e = e.sibling; e !== null; ) Xl(e, t, n), e = e.sibling;
  }
  function ql(e, t, n) {
    var r = e.tag;
    if (r === 5 || r === 6) e = e.stateNode, t ? n.insertBefore(e, t) : n.appendChild(e);
    else if (r !== 4 && (e = e.child, e !== null)) for (ql(e, t, n), e = e.sibling; e !== null; ) ql(e, t, n), e = e.sibling;
  }
  var xe = null, ht = !1;
  function Zt(e, t, n) {
    for (n = n.child; n !== null; ) mc(e, t, n), n = n.sibling;
  }
  function mc(e, t, n) {
    if (Et && typeof Et.onCommitFiberUnmount == "function") try {
      Et.onCommitFiberUnmount(ii, n);
    } catch {
    }
    switch (n.tag) {
      case 5:
        Oe || Xn(n, t);
      case 6:
        var r = xe, i = ht;
        xe = null, Zt(e, t, n), xe = r, ht = i, xe !== null && (ht ? (e = xe, n = n.stateNode, e.nodeType === 8 ? e.parentNode.removeChild(n) : e.removeChild(n)) : xe.removeChild(n.stateNode));
        break;
      case 18:
        xe !== null && (ht ? (e = xe, n = n.stateNode, e.nodeType === 8 ? cl(e.parentNode, n) : e.nodeType === 1 && cl(e, n), gr(e)) : cl(xe, n.stateNode));
        break;
      case 4:
        r = xe, i = ht, xe = n.stateNode.containerInfo, ht = !0, Zt(e, t, n), xe = r, ht = i;
        break;
      case 0:
      case 11:
      case 14:
      case 15:
        if (!Oe && (r = n.updateQueue, r !== null && (r = r.lastEffect, r !== null))) {
          i = r = r.next;
          do {
            var l = i, c = l.destroy;
            l = l.tag, c !== void 0 && ((l & 2) !== 0 || (l & 4) !== 0) && bl(n, t, c), i = i.next;
          } while (i !== r);
        }
        Zt(e, t, n);
        break;
      case 1:
        if (!Oe && (Xn(n, t), r = n.stateNode, typeof r.componentWillUnmount == "function")) try {
          r.props = n.memoizedProps, r.state = n.memoizedState, r.componentWillUnmount();
        } catch (g) {
          ve(n, t, g);
        }
        Zt(e, t, n);
        break;
      case 21:
        Zt(e, t, n);
        break;
      case 22:
        n.mode & 1 ? (Oe = (r = Oe) || n.memoizedState !== null, Zt(e, t, n), Oe = r) : Zt(e, t, n);
        break;
      default:
        Zt(e, t, n);
    }
  }
  function gc(e) {
    var t = e.updateQueue;
    if (t !== null) {
      e.updateQueue = null;
      var n = e.stateNode;
      n === null && (n = e.stateNode = new tp()), t.forEach(function(r) {
        var i = dp.bind(null, e, r);
        n.has(r) || (n.add(r), r.then(i, i));
      });
    }
  }
  function vt(e, t) {
    var n = t.deletions;
    if (n !== null) for (var r = 0; r < n.length; r++) {
      var i = n[r];
      try {
        var l = e, c = t, g = c;
        e: for (; g !== null; ) {
          switch (g.tag) {
            case 5:
              xe = g.stateNode, ht = !1;
              break e;
            case 3:
              xe = g.stateNode.containerInfo, ht = !0;
              break e;
            case 4:
              xe = g.stateNode.containerInfo, ht = !0;
              break e;
          }
          g = g.return;
        }
        if (xe === null) throw Error(a(160));
        mc(l, c, i), xe = null, ht = !1;
        var v = i.alternate;
        v !== null && (v.return = null), i.return = null;
      } catch (_) {
        ve(i, t, _);
      }
    }
    if (t.subtreeFlags & 12854) for (t = t.child; t !== null; ) hc(t, e), t = t.sibling;
  }
  function hc(e, t) {
    var n = e.alternate, r = e.flags;
    switch (e.tag) {
      case 0:
      case 11:
      case 14:
      case 15:
        if (vt(t, e), jt(e), r & 4) {
          try {
            Lr(3, e, e.return), Ki(3, e);
          } catch (F) {
            ve(e, e.return, F);
          }
          try {
            Lr(5, e, e.return);
          } catch (F) {
            ve(e, e.return, F);
          }
        }
        break;
      case 1:
        vt(t, e), jt(e), r & 512 && n !== null && Xn(n, n.return);
        break;
      case 5:
        if (vt(t, e), jt(e), r & 512 && n !== null && Xn(n, n.return), e.flags & 32) {
          var i = e.stateNode;
          try {
            ir(i, "");
          } catch (F) {
            ve(e, e.return, F);
          }
        }
        if (r & 4 && (i = e.stateNode, i != null)) {
          var l = e.memoizedProps, c = n !== null ? n.memoizedProps : l, g = e.type, v = e.updateQueue;
          if (e.updateQueue = null, v !== null) try {
            g === "input" && l.type === "radio" && l.name != null && Ba(i, l), Io(g, c);
            var _ = Io(g, l);
            for (c = 0; c < v.length; c += 2) {
              var j = v[c], I = v[c + 1];
              j === "style" ? Ja(i, I) : j === "dangerouslySetInnerHTML" ? Xa(i, I) : j === "children" ? ir(i, I) : fe(i, j, I, _);
            }
            switch (g) {
              case "input":
                Eo(i, l);
                break;
              case "textarea":
                Qa(i, l);
                break;
              case "select":
                var T = i._wrapperState.wasMultiple;
                i._wrapperState.wasMultiple = !!l.multiple;
                var D = l.value;
                D != null ? xn(i, !!l.multiple, D, !1) : T !== !!l.multiple && (l.defaultValue != null ? xn(
                  i,
                  !!l.multiple,
                  l.defaultValue,
                  !0
                ) : xn(i, !!l.multiple, l.multiple ? [] : "", !1));
            }
            i[Pr] = l;
          } catch (F) {
            ve(e, e.return, F);
          }
        }
        break;
      case 6:
        if (vt(t, e), jt(e), r & 4) {
          if (e.stateNode === null) throw Error(a(162));
          i = e.stateNode, l = e.memoizedProps;
          try {
            i.nodeValue = l;
          } catch (F) {
            ve(e, e.return, F);
          }
        }
        break;
      case 3:
        if (vt(t, e), jt(e), r & 4 && n !== null && n.memoizedState.isDehydrated) try {
          gr(t.containerInfo);
        } catch (F) {
          ve(e, e.return, F);
        }
        break;
      case 4:
        vt(t, e), jt(e);
        break;
      case 13:
        vt(t, e), jt(e), i = e.child, i.flags & 8192 && (l = i.memoizedState !== null, i.stateNode.isHidden = l, !l || i.alternate !== null && i.alternate.memoizedState !== null || (ea = ye())), r & 4 && gc(e);
        break;
      case 22:
        if (j = n !== null && n.memoizedState !== null, e.mode & 1 ? (Oe = (_ = Oe) || j, vt(t, e), Oe = _) : vt(t, e), jt(e), r & 8192) {
          if (_ = e.memoizedState !== null, (e.stateNode.isHidden = _) && !j && (e.mode & 1) !== 0) for (N = e, j = e.child; j !== null; ) {
            for (I = N = j; N !== null; ) {
              switch (T = N, D = T.child, T.tag) {
                case 0:
                case 11:
                case 14:
                case 15:
                  Lr(4, T, T.return);
                  break;
                case 1:
                  Xn(T, T.return);
                  var L = T.stateNode;
                  if (typeof L.componentWillUnmount == "function") {
                    r = T, n = T.return;
                    try {
                      t = r, L.props = t.memoizedProps, L.state = t.memoizedState, L.componentWillUnmount();
                    } catch (F) {
                      ve(r, n, F);
                    }
                  }
                  break;
                case 5:
                  Xn(T, T.return);
                  break;
                case 22:
                  if (T.memoizedState !== null) {
                    kc(I);
                    continue;
                  }
              }
              D !== null ? (D.return = T, N = D) : kc(I);
            }
            j = j.sibling;
          }
          e: for (j = null, I = e; ; ) {
            if (I.tag === 5) {
              if (j === null) {
                j = I;
                try {
                  i = I.stateNode, _ ? (l = i.style, typeof l.setProperty == "function" ? l.setProperty("display", "none", "important") : l.display = "none") : (g = I.stateNode, v = I.memoizedProps.style, c = v != null && v.hasOwnProperty("display") ? v.display : null, g.style.display = qa("display", c));
                } catch (F) {
                  ve(e, e.return, F);
                }
              }
            } else if (I.tag === 6) {
              if (j === null) try {
                I.stateNode.nodeValue = _ ? "" : I.memoizedProps;
              } catch (F) {
                ve(e, e.return, F);
              }
            } else if ((I.tag !== 22 && I.tag !== 23 || I.memoizedState === null || I === e) && I.child !== null) {
              I.child.return = I, I = I.child;
              continue;
            }
            if (I === e) break e;
            for (; I.sibling === null; ) {
              if (I.return === null || I.return === e) break e;
              j === I && (j = null), I = I.return;
            }
            j === I && (j = null), I.sibling.return = I.return, I = I.sibling;
          }
        }
        break;
      case 19:
        vt(t, e), jt(e), r & 4 && gc(e);
        break;
      case 21:
        break;
      default:
        vt(
          t,
          e
        ), jt(e);
    }
  }
  function jt(e) {
    var t = e.flags;
    if (t & 2) {
      try {
        e: {
          for (var n = e.return; n !== null; ) {
            if (fc(n)) {
              var r = n;
              break e;
            }
            n = n.return;
          }
          throw Error(a(160));
        }
        switch (r.tag) {
          case 5:
            var i = r.stateNode;
            r.flags & 32 && (ir(i, ""), r.flags &= -33);
            var l = pc(e);
            ql(e, l, i);
            break;
          case 3:
          case 4:
            var c = r.stateNode.containerInfo, g = pc(e);
            Xl(e, g, c);
            break;
          default:
            throw Error(a(161));
        }
      } catch (v) {
        ve(e, e.return, v);
      }
      e.flags &= -3;
    }
    t & 4096 && (e.flags &= -4097);
  }
  function rp(e, t, n) {
    N = e, vc(e);
  }
  function vc(e, t, n) {
    for (var r = (e.mode & 1) !== 0; N !== null; ) {
      var i = N, l = i.child;
      if (i.tag === 22 && r) {
        var c = i.memoizedState !== null || Bi;
        if (!c) {
          var g = i.alternate, v = g !== null && g.memoizedState !== null || Oe;
          g = Bi;
          var _ = Oe;
          if (Bi = c, (Oe = v) && !_) for (N = i; N !== null; ) c = N, v = c.child, c.tag === 22 && c.memoizedState !== null ? wc(i) : v !== null ? (v.return = c, N = v) : wc(i);
          for (; l !== null; ) N = l, vc(l), l = l.sibling;
          N = i, Bi = g, Oe = _;
        }
        yc(e);
      } else (i.subtreeFlags & 8772) !== 0 && l !== null ? (l.return = i, N = l) : yc(e);
    }
  }
  function yc(e) {
    for (; N !== null; ) {
      var t = N;
      if ((t.flags & 8772) !== 0) {
        var n = t.alternate;
        try {
          if ((t.flags & 8772) !== 0) switch (t.tag) {
            case 0:
            case 11:
            case 15:
              Oe || Ki(5, t);
              break;
            case 1:
              var r = t.stateNode;
              if (t.flags & 4 && !Oe) if (n === null) r.componentDidMount();
              else {
                var i = t.elementType === t.type ? n.memoizedProps : gt(t.type, n.memoizedProps);
                r.componentDidUpdate(i, n.memoizedState, r.__reactInternalSnapshotBeforeUpdate);
              }
              var l = t.updateQueue;
              l !== null && ku(t, l, r);
              break;
            case 3:
              var c = t.updateQueue;
              if (c !== null) {
                if (n = null, t.child !== null) switch (t.child.tag) {
                  case 5:
                    n = t.child.stateNode;
                    break;
                  case 1:
                    n = t.child.stateNode;
                }
                ku(t, c, n);
              }
              break;
            case 5:
              var g = t.stateNode;
              if (n === null && t.flags & 4) {
                n = g;
                var v = t.memoizedProps;
                switch (t.type) {
                  case "button":
                  case "input":
                  case "select":
                  case "textarea":
                    v.autoFocus && n.focus();
                    break;
                  case "img":
                    v.src && (n.src = v.src);
                }
              }
              break;
            case 6:
              break;
            case 4:
              break;
            case 12:
              break;
            case 13:
              if (t.memoizedState === null) {
                var _ = t.alternate;
                if (_ !== null) {
                  var j = _.memoizedState;
                  if (j !== null) {
                    var I = j.dehydrated;
                    I !== null && gr(I);
                  }
                }
              }
              break;
            case 19:
            case 17:
            case 21:
            case 22:
            case 23:
            case 25:
              break;
            default:
              throw Error(a(163));
          }
          Oe || t.flags & 512 && Yl(t);
        } catch (T) {
          ve(t, t.return, T);
        }
      }
      if (t === e) {
        N = null;
        break;
      }
      if (n = t.sibling, n !== null) {
        n.return = t.return, N = n;
        break;
      }
      N = t.return;
    }
  }
  function kc(e) {
    for (; N !== null; ) {
      var t = N;
      if (t === e) {
        N = null;
        break;
      }
      var n = t.sibling;
      if (n !== null) {
        n.return = t.return, N = n;
        break;
      }
      N = t.return;
    }
  }
  function wc(e) {
    for (; N !== null; ) {
      var t = N;
      try {
        switch (t.tag) {
          case 0:
          case 11:
          case 15:
            var n = t.return;
            try {
              Ki(4, t);
            } catch (v) {
              ve(t, n, v);
            }
            break;
          case 1:
            var r = t.stateNode;
            if (typeof r.componentDidMount == "function") {
              var i = t.return;
              try {
                r.componentDidMount();
              } catch (v) {
                ve(t, i, v);
              }
            }
            var l = t.return;
            try {
              Yl(t);
            } catch (v) {
              ve(t, l, v);
            }
            break;
          case 5:
            var c = t.return;
            try {
              Yl(t);
            } catch (v) {
              ve(t, c, v);
            }
        }
      } catch (v) {
        ve(t, t.return, v);
      }
      if (t === e) {
        N = null;
        break;
      }
      var g = t.sibling;
      if (g !== null) {
        g.return = t.return, N = g;
        break;
      }
      N = t.return;
    }
  }
  var ip = Math.ceil, Gi = q.ReactCurrentDispatcher, Jl = q.ReactCurrentOwner, at = q.ReactCurrentBatchConfig, J = 0, Pe = null, Se = null, Ae = 0, Ze = 0, qn = bt(0), Ce = 0, $r = null, kn = 0, Qi = 0, Zl = 0, Fr = null, He = null, ea = 0, Jn = 1 / 0, Lt = null, bi = !1, ta = null, en = null, Yi = !1, tn = null, Xi = 0, Ur = 0, na = null, qi = -1, Ji = 0;
  function $e() {
    return (J & 6) !== 0 ? ye() : qi !== -1 ? qi : qi = ye();
  }
  function nn(e) {
    return (e.mode & 1) === 0 ? 1 : (J & 2) !== 0 && Ae !== 0 ? Ae & -Ae : Vf.transition !== null ? (Ji === 0 && (Ji = ps()), Ji) : (e = re, e !== 0 || (e = window.event, e = e === void 0 ? 16 : _s(e.type)), e);
  }
  function yt(e, t, n, r) {
    if (50 < Ur) throw Ur = 0, na = null, Error(a(185));
    cr(e, n, r), ((J & 2) === 0 || e !== Pe) && (e === Pe && ((J & 2) === 0 && (Qi |= n), Ce === 4 && rn(e, Ae)), Be(e, r), n === 1 && J === 0 && (t.mode & 1) === 0 && (Jn = ye() + 500, Pi && Xt()));
  }
  function Be(e, t) {
    var n = e.callbackNode;
    Ud(e, t);
    var r = ai(e, e === Pe ? Ae : 0);
    if (r === 0) n !== null && cs(n), e.callbackNode = null, e.callbackPriority = 0;
    else if (t = r & -r, e.callbackPriority !== t) {
      if (n != null && cs(n), t === 1) e.tag === 0 ? Uf(_c.bind(null, e)) : au(_c.bind(null, e)), Mf(function() {
        (J & 6) === 0 && Xt();
      }), n = null;
      else {
        switch (ms(r)) {
          case 1:
            n = Oo;
            break;
          case 4:
            n = ds;
            break;
          case 16:
            n = ri;
            break;
          case 536870912:
            n = fs;
            break;
          default:
            n = ri;
        }
        n = Ac(n, Sc.bind(null, e));
      }
      e.callbackPriority = t, e.callbackNode = n;
    }
  }
  function Sc(e, t) {
    if (qi = -1, Ji = 0, (J & 6) !== 0) throw Error(a(327));
    var n = e.callbackNode;
    if (Zn() && e.callbackNode !== n) return null;
    var r = ai(e, e === Pe ? Ae : 0);
    if (r === 0) return null;
    if ((r & 30) !== 0 || (r & e.expiredLanes) !== 0 || t) t = Zi(e, r);
    else {
      t = r;
      var i = J;
      J |= 2;
      var l = Cc();
      (Pe !== e || Ae !== t) && (Lt = null, Jn = ye() + 500, Sn(e, t));
      do
        try {
          ap();
          break;
        } catch (g) {
          Ec(e, g);
        }
      while (!0);
      wl(), Gi.current = l, J = i, Se !== null ? t = 0 : (Pe = null, Ae = 0, t = Ce);
    }
    if (t !== 0) {
      if (t === 2 && (i = Mo(e), i !== 0 && (r = i, t = ra(e, i))), t === 1) throw n = $r, Sn(e, 0), rn(e, r), Be(e, ye()), n;
      if (t === 6) rn(e, r);
      else {
        if (i = e.current.alternate, (r & 30) === 0 && !op(i) && (t = Zi(e, r), t === 2 && (l = Mo(e), l !== 0 && (r = l, t = ra(e, l))), t === 1)) throw n = $r, Sn(e, 0), rn(e, r), Be(e, ye()), n;
        switch (e.finishedWork = i, e.finishedLanes = r, t) {
          case 0:
          case 1:
            throw Error(a(345));
          case 2:
            _n(e, He, Lt);
            break;
          case 3:
            if (rn(e, r), (r & 130023424) === r && (t = ea + 500 - ye(), 10 < t)) {
              if (ai(e, 0) !== 0) break;
              if (i = e.suspendedLanes, (i & r) !== r) {
                $e(), e.pingedLanes |= e.suspendedLanes & i;
                break;
              }
              e.timeoutHandle = ul(_n.bind(null, e, He, Lt), t);
              break;
            }
            _n(e, He, Lt);
            break;
          case 4:
            if (rn(e, r), (r & 4194240) === r) break;
            for (t = e.eventTimes, i = -1; 0 < r; ) {
              var c = 31 - ft(r);
              l = 1 << c, c = t[c], c > i && (i = c), r &= ~l;
            }
            if (r = i, r = ye() - r, r = (120 > r ? 120 : 480 > r ? 480 : 1080 > r ? 1080 : 1920 > r ? 1920 : 3e3 > r ? 3e3 : 4320 > r ? 4320 : 1960 * ip(r / 1960)) - r, 10 < r) {
              e.timeoutHandle = ul(_n.bind(null, e, He, Lt), r);
              break;
            }
            _n(e, He, Lt);
            break;
          case 5:
            _n(e, He, Lt);
            break;
          default:
            throw Error(a(329));
        }
      }
    }
    return Be(e, ye()), e.callbackNode === n ? Sc.bind(null, e) : null;
  }
  function ra(e, t) {
    var n = Fr;
    return e.current.memoizedState.isDehydrated && (Sn(e, t).flags |= 256), e = Zi(e, t), e !== 2 && (t = He, He = n, t !== null && ia(t)), e;
  }
  function ia(e) {
    He === null ? He = e : He.push.apply(He, e);
  }
  function op(e) {
    for (var t = e; ; ) {
      if (t.flags & 16384) {
        var n = t.updateQueue;
        if (n !== null && (n = n.stores, n !== null)) for (var r = 0; r < n.length; r++) {
          var i = n[r], l = i.getSnapshot;
          i = i.value;
          try {
            if (!pt(l(), i)) return !1;
          } catch {
            return !1;
          }
        }
      }
      if (n = t.child, t.subtreeFlags & 16384 && n !== null) n.return = t, t = n;
      else {
        if (t === e) break;
        for (; t.sibling === null; ) {
          if (t.return === null || t.return === e) return !0;
          t = t.return;
        }
        t.sibling.return = t.return, t = t.sibling;
      }
    }
    return !0;
  }
  function rn(e, t) {
    for (t &= ~Zl, t &= ~Qi, e.suspendedLanes |= t, e.pingedLanes &= ~t, e = e.expirationTimes; 0 < t; ) {
      var n = 31 - ft(t), r = 1 << n;
      e[n] = -1, t &= ~r;
    }
  }
  function _c(e) {
    if ((J & 6) !== 0) throw Error(a(327));
    Zn();
    var t = ai(e, 0);
    if ((t & 1) === 0) return Be(e, ye()), null;
    var n = Zi(e, t);
    if (e.tag !== 0 && n === 2) {
      var r = Mo(e);
      r !== 0 && (t = r, n = ra(e, r));
    }
    if (n === 1) throw n = $r, Sn(e, 0), rn(e, t), Be(e, ye()), n;
    if (n === 6) throw Error(a(345));
    return e.finishedWork = e.current.alternate, e.finishedLanes = t, _n(e, He, Lt), Be(e, ye()), null;
  }
  function oa(e, t) {
    var n = J;
    J |= 1;
    try {
      return e(t);
    } finally {
      J = n, J === 0 && (Jn = ye() + 500, Pi && Xt());
    }
  }
  function wn(e) {
    tn !== null && tn.tag === 0 && (J & 6) === 0 && Zn();
    var t = J;
    J |= 1;
    var n = at.transition, r = re;
    try {
      if (at.transition = null, re = 1, e) return e();
    } finally {
      re = r, at.transition = n, J = t, (J & 6) === 0 && Xt();
    }
  }
  function la() {
    Ze = qn.current, ue(qn);
  }
  function Sn(e, t) {
    e.finishedWork = null, e.finishedLanes = 0;
    var n = e.timeoutHandle;
    if (n !== -1 && (e.timeoutHandle = -1, Of(n)), Se !== null) for (n = Se.return; n !== null; ) {
      var r = n;
      switch (gl(r), r.tag) {
        case 1:
          r = r.type.childContextTypes, r != null && Ci();
          break;
        case 3:
          bn(), ue(Ue), ue(De), Il();
          break;
        case 5:
          Pl(r);
          break;
        case 4:
          bn();
          break;
        case 13:
          ue(pe);
          break;
        case 19:
          ue(pe);
          break;
        case 10:
          Sl(r.type._context);
          break;
        case 22:
        case 23:
          la();
      }
      n = n.return;
    }
    if (Pe = e, Se = e = on(e.current, null), Ae = Ze = t, Ce = 0, $r = null, Zl = Qi = kn = 0, He = Fr = null, hn !== null) {
      for (t = 0; t < hn.length; t++) if (n = hn[t], r = n.interleaved, r !== null) {
        n.interleaved = null;
        var i = r.next, l = n.pending;
        if (l !== null) {
          var c = l.next;
          l.next = i, r.next = c;
        }
        n.pending = r;
      }
      hn = null;
    }
    return e;
  }
  function Ec(e, t) {
    do {
      var n = Se;
      try {
        if (wl(), Mi.current = Ui, Li) {
          for (var r = me.memoizedState; r !== null; ) {
            var i = r.queue;
            i !== null && (i.pending = null), r = r.next;
          }
          Li = !1;
        }
        if (yn = 0, Te = Ee = me = null, Dr = !1, Nr = 0, Jl.current = null, n === null || n.return === null) {
          Ce = 1, $r = t, Se = null;
          break;
        }
        e: {
          var l = e, c = n.return, g = n, v = t;
          if (t = Ae, g.flags |= 32768, v !== null && typeof v == "object" && typeof v.then == "function") {
            var _ = v, j = g, I = j.tag;
            if ((j.mode & 1) === 0 && (I === 0 || I === 11 || I === 15)) {
              var T = j.alternate;
              T ? (j.updateQueue = T.updateQueue, j.memoizedState = T.memoizedState, j.lanes = T.lanes) : (j.updateQueue = null, j.memoizedState = null);
            }
            var D = bu(c);
            if (D !== null) {
              D.flags &= -257, Yu(D, c, g, l, t), D.mode & 1 && Qu(l, _, t), t = D, v = _;
              var L = t.updateQueue;
              if (L === null) {
                var F = /* @__PURE__ */ new Set();
                F.add(v), t.updateQueue = F;
              } else L.add(v);
              break e;
            } else {
              if ((t & 1) === 0) {
                Qu(l, _, t), aa();
                break e;
              }
              v = Error(a(426));
            }
          } else if (de && g.mode & 1) {
            var ke = bu(c);
            if (ke !== null) {
              (ke.flags & 65536) === 0 && (ke.flags |= 256), Yu(ke, c, g, l, t), yl(Yn(v, g));
              break e;
            }
          }
          l = v = Yn(v, g), Ce !== 4 && (Ce = 2), Fr === null ? Fr = [l] : Fr.push(l), l = c;
          do {
            switch (l.tag) {
              case 3:
                l.flags |= 65536, t &= -t, l.lanes |= t;
                var w = Ku(l, v, t);
                yu(l, w);
                break e;
              case 1:
                g = v;
                var y = l.type, S = l.stateNode;
                if ((l.flags & 128) === 0 && (typeof y.getDerivedStateFromError == "function" || S !== null && typeof S.componentDidCatch == "function" && (en === null || !en.has(S)))) {
                  l.flags |= 65536, t &= -t, l.lanes |= t;
                  var x = Gu(l, g, t);
                  yu(l, x);
                  break e;
                }
            }
            l = l.return;
          } while (l !== null);
        }
        Pc(n);
      } catch (U) {
        t = U, Se === n && n !== null && (Se = n = n.return);
        continue;
      }
      break;
    } while (!0);
  }
  function Cc() {
    var e = Gi.current;
    return Gi.current = Ui, e === null ? Ui : e;
  }
  function aa() {
    (Ce === 0 || Ce === 3 || Ce === 2) && (Ce = 4), Pe === null || (kn & 268435455) === 0 && (Qi & 268435455) === 0 || rn(Pe, Ae);
  }
  function Zi(e, t) {
    var n = J;
    J |= 2;
    var r = Cc();
    (Pe !== e || Ae !== t) && (Lt = null, Sn(e, t));
    do
      try {
        lp();
        break;
      } catch (i) {
        Ec(e, i);
      }
    while (!0);
    if (wl(), J = n, Gi.current = r, Se !== null) throw Error(a(261));
    return Pe = null, Ae = 0, Ce;
  }
  function lp() {
    for (; Se !== null; ) Tc(Se);
  }
  function ap() {
    for (; Se !== null && !Rd(); ) Tc(Se);
  }
  function Tc(e) {
    var t = xc(e.alternate, e, Ze);
    e.memoizedProps = e.pendingProps, t === null ? Pc(e) : Se = t, Jl.current = null;
  }
  function Pc(e) {
    var t = e;
    do {
      var n = t.alternate;
      if (e = t.return, (t.flags & 32768) === 0) {
        if (n = Zf(n, t, Ze), n !== null) {
          Se = n;
          return;
        }
      } else {
        if (n = ep(n, t), n !== null) {
          n.flags &= 32767, Se = n;
          return;
        }
        if (e !== null) e.flags |= 32768, e.subtreeFlags = 0, e.deletions = null;
        else {
          Ce = 6, Se = null;
          return;
        }
      }
      if (t = t.sibling, t !== null) {
        Se = t;
        return;
      }
      Se = t = e;
    } while (t !== null);
    Ce === 0 && (Ce = 5);
  }
  function _n(e, t, n) {
    var r = re, i = at.transition;
    try {
      at.transition = null, re = 1, sp(e, t, n, r);
    } finally {
      at.transition = i, re = r;
    }
    return null;
  }
  function sp(e, t, n, r) {
    do
      Zn();
    while (tn !== null);
    if ((J & 6) !== 0) throw Error(a(327));
    n = e.finishedWork;
    var i = e.finishedLanes;
    if (n === null) return null;
    if (e.finishedWork = null, e.finishedLanes = 0, n === e.current) throw Error(a(177));
    e.callbackNode = null, e.callbackPriority = 0;
    var l = n.lanes | n.childLanes;
    if (Vd(e, l), e === Pe && (Se = Pe = null, Ae = 0), (n.subtreeFlags & 2064) === 0 && (n.flags & 2064) === 0 || Yi || (Yi = !0, Ac(ri, function() {
      return Zn(), null;
    })), l = (n.flags & 15990) !== 0, (n.subtreeFlags & 15990) !== 0 || l) {
      l = at.transition, at.transition = null;
      var c = re;
      re = 1;
      var g = J;
      J |= 4, Jl.current = null, np(e, n), hc(n, e), If(al), ci = !!ll, al = ll = null, e.current = n, rp(n), Dd(), J = g, re = c, at.transition = l;
    } else e.current = n;
    if (Yi && (Yi = !1, tn = e, Xi = i), l = e.pendingLanes, l === 0 && (en = null), Od(n.stateNode), Be(e, ye()), t !== null) for (r = e.onRecoverableError, n = 0; n < t.length; n++) i = t[n], r(i.value, { componentStack: i.stack, digest: i.digest });
    if (bi) throw bi = !1, e = ta, ta = null, e;
    return (Xi & 1) !== 0 && e.tag !== 0 && Zn(), l = e.pendingLanes, (l & 1) !== 0 ? e === na ? Ur++ : (Ur = 0, na = e) : Ur = 0, Xt(), null;
  }
  function Zn() {
    if (tn !== null) {
      var e = ms(Xi), t = at.transition, n = re;
      try {
        if (at.transition = null, re = 16 > e ? 16 : e, tn === null) var r = !1;
        else {
          if (e = tn, tn = null, Xi = 0, (J & 6) !== 0) throw Error(a(331));
          var i = J;
          for (J |= 4, N = e.current; N !== null; ) {
            var l = N, c = l.child;
            if ((N.flags & 16) !== 0) {
              var g = l.deletions;
              if (g !== null) {
                for (var v = 0; v < g.length; v++) {
                  var _ = g[v];
                  for (N = _; N !== null; ) {
                    var j = N;
                    switch (j.tag) {
                      case 0:
                      case 11:
                      case 15:
                        Lr(8, j, l);
                    }
                    var I = j.child;
                    if (I !== null) I.return = j, N = I;
                    else for (; N !== null; ) {
                      j = N;
                      var T = j.sibling, D = j.return;
                      if (dc(j), j === _) {
                        N = null;
                        break;
                      }
                      if (T !== null) {
                        T.return = D, N = T;
                        break;
                      }
                      N = D;
                    }
                  }
                }
                var L = l.alternate;
                if (L !== null) {
                  var F = L.child;
                  if (F !== null) {
                    L.child = null;
                    do {
                      var ke = F.sibling;
                      F.sibling = null, F = ke;
                    } while (F !== null);
                  }
                }
                N = l;
              }
            }
            if ((l.subtreeFlags & 2064) !== 0 && c !== null) c.return = l, N = c;
            else e: for (; N !== null; ) {
              if (l = N, (l.flags & 2048) !== 0) switch (l.tag) {
                case 0:
                case 11:
                case 15:
                  Lr(9, l, l.return);
              }
              var w = l.sibling;
              if (w !== null) {
                w.return = l.return, N = w;
                break e;
              }
              N = l.return;
            }
          }
          var y = e.current;
          for (N = y; N !== null; ) {
            c = N;
            var S = c.child;
            if ((c.subtreeFlags & 2064) !== 0 && S !== null) S.return = c, N = S;
            else e: for (c = y; N !== null; ) {
              if (g = N, (g.flags & 2048) !== 0) try {
                switch (g.tag) {
                  case 0:
                  case 11:
                  case 15:
                    Ki(9, g);
                }
              } catch (U) {
                ve(g, g.return, U);
              }
              if (g === c) {
                N = null;
                break e;
              }
              var x = g.sibling;
              if (x !== null) {
                x.return = g.return, N = x;
                break e;
              }
              N = g.return;
            }
          }
          if (J = i, Xt(), Et && typeof Et.onPostCommitFiberRoot == "function") try {
            Et.onPostCommitFiberRoot(ii, e);
          } catch {
          }
          r = !0;
        }
        return r;
      } finally {
        re = n, at.transition = t;
      }
    }
    return !1;
  }
  function jc(e, t, n) {
    t = Yn(n, t), t = Ku(e, t, 1), e = Jt(e, t, 1), t = $e(), e !== null && (cr(e, 1, t), Be(e, t));
  }
  function ve(e, t, n) {
    if (e.tag === 3) jc(e, e, n);
    else for (; t !== null; ) {
      if (t.tag === 3) {
        jc(t, e, n);
        break;
      } else if (t.tag === 1) {
        var r = t.stateNode;
        if (typeof t.type.getDerivedStateFromError == "function" || typeof r.componentDidCatch == "function" && (en === null || !en.has(r))) {
          e = Yn(n, e), e = Gu(t, e, 1), t = Jt(t, e, 1), e = $e(), t !== null && (cr(t, 1, e), Be(t, e));
          break;
        }
      }
      t = t.return;
    }
  }
  function up(e, t, n) {
    var r = e.pingCache;
    r !== null && r.delete(t), t = $e(), e.pingedLanes |= e.suspendedLanes & n, Pe === e && (Ae & n) === n && (Ce === 4 || Ce === 3 && (Ae & 130023424) === Ae && 500 > ye() - ea ? Sn(e, 0) : Zl |= n), Be(e, t);
  }
  function Ic(e, t) {
    t === 0 && ((e.mode & 1) === 0 ? t = 1 : (t = li, li <<= 1, (li & 130023424) === 0 && (li = 4194304)));
    var n = $e();
    e = zt(e, t), e !== null && (cr(e, t, n), Be(e, n));
  }
  function cp(e) {
    var t = e.memoizedState, n = 0;
    t !== null && (n = t.retryLane), Ic(e, n);
  }
  function dp(e, t) {
    var n = 0;
    switch (e.tag) {
      case 13:
        var r = e.stateNode, i = e.memoizedState;
        i !== null && (n = i.retryLane);
        break;
      case 19:
        r = e.stateNode;
        break;
      default:
        throw Error(a(314));
    }
    r !== null && r.delete(t), Ic(e, n);
  }
  var xc;
  xc = function(e, t, n) {
    if (e !== null) if (e.memoizedProps !== t.pendingProps || Ue.current) We = !0;
    else {
      if ((e.lanes & n) === 0 && (t.flags & 128) === 0) return We = !1, Jf(e, t, n);
      We = (e.flags & 131072) !== 0;
    }
    else We = !1, de && (t.flags & 1048576) !== 0 && su(t, Ii, t.index);
    switch (t.lanes = 0, t.tag) {
      case 2:
        var r = t.type;
        Hi(e, t), e = t.pendingProps;
        var i = Vn(t, De.current);
        Qn(t, n), i = Rl(null, t, r, e, i, n);
        var l = Dl();
        return t.flags |= 1, typeof i == "object" && i !== null && typeof i.render == "function" && i.$$typeof === void 0 ? (t.tag = 1, t.memoizedState = null, t.updateQueue = null, Ve(r) ? (l = !0, Ti(t)) : l = !1, t.memoizedState = i.state !== null && i.state !== void 0 ? i.state : null, Cl(t), i.updater = Vi, t.stateNode = i, i._reactInternals = t, $l(t, r, e, n), t = Wl(null, t, r, !0, l, n)) : (t.tag = 0, de && l && ml(t), Le(null, t, i, n), t = t.child), t;
      case 16:
        r = t.elementType;
        e: {
          switch (Hi(e, t), e = t.pendingProps, i = r._init, r = i(r._payload), t.type = r, i = t.tag = pp(r), e = gt(r, e), i) {
            case 0:
              t = Vl(null, t, r, e, n);
              break e;
            case 1:
              t = tc(null, t, r, e, n);
              break e;
            case 11:
              t = Xu(null, t, r, e, n);
              break e;
            case 14:
              t = qu(null, t, r, gt(r.type, e), n);
              break e;
          }
          throw Error(a(
            306,
            r,
            ""
          ));
        }
        return t;
      case 0:
        return r = t.type, i = t.pendingProps, i = t.elementType === r ? i : gt(r, i), Vl(e, t, r, i, n);
      case 1:
        return r = t.type, i = t.pendingProps, i = t.elementType === r ? i : gt(r, i), tc(e, t, r, i, n);
      case 3:
        e: {
          if (nc(t), e === null) throw Error(a(387));
          r = t.pendingProps, l = t.memoizedState, i = l.element, vu(e, t), zi(t, r, null, n);
          var c = t.memoizedState;
          if (r = c.element, l.isDehydrated) if (l = { element: r, isDehydrated: !1, cache: c.cache, pendingSuspenseBoundaries: c.pendingSuspenseBoundaries, transitions: c.transitions }, t.updateQueue.baseState = l, t.memoizedState = l, t.flags & 256) {
            i = Yn(Error(a(423)), t), t = rc(e, t, r, n, i);
            break e;
          } else if (r !== i) {
            i = Yn(Error(a(424)), t), t = rc(e, t, r, n, i);
            break e;
          } else for (Je = Qt(t.stateNode.containerInfo.firstChild), qe = t, de = !0, mt = null, n = gu(t, null, r, n), t.child = n; n; ) n.flags = n.flags & -3 | 4096, n = n.sibling;
          else {
            if (Bn(), r === i) {
              t = Mt(e, t, n);
              break e;
            }
            Le(e, t, r, n);
          }
          t = t.child;
        }
        return t;
      case 5:
        return wu(t), e === null && vl(t), r = t.type, i = t.pendingProps, l = e !== null ? e.memoizedProps : null, c = i.children, sl(r, i) ? c = null : l !== null && sl(r, l) && (t.flags |= 32), ec(e, t), Le(e, t, c, n), t.child;
      case 6:
        return e === null && vl(t), null;
      case 13:
        return ic(e, t, n);
      case 4:
        return Tl(t, t.stateNode.containerInfo), r = t.pendingProps, e === null ? t.child = Kn(t, null, r, n) : Le(e, t, r, n), t.child;
      case 11:
        return r = t.type, i = t.pendingProps, i = t.elementType === r ? i : gt(r, i), Xu(e, t, r, i, n);
      case 7:
        return Le(e, t, t.pendingProps, n), t.child;
      case 8:
        return Le(e, t, t.pendingProps.children, n), t.child;
      case 12:
        return Le(e, t, t.pendingProps.children, n), t.child;
      case 10:
        e: {
          if (r = t.type._context, i = t.pendingProps, l = t.memoizedProps, c = i.value, le(Ri, r._currentValue), r._currentValue = c, l !== null) if (pt(l.value, c)) {
            if (l.children === i.children && !Ue.current) {
              t = Mt(e, t, n);
              break e;
            }
          } else for (l = t.child, l !== null && (l.return = t); l !== null; ) {
            var g = l.dependencies;
            if (g !== null) {
              c = l.child;
              for (var v = g.firstContext; v !== null; ) {
                if (v.context === r) {
                  if (l.tag === 1) {
                    v = Ot(-1, n & -n), v.tag = 2;
                    var _ = l.updateQueue;
                    if (_ !== null) {
                      _ = _.shared;
                      var j = _.pending;
                      j === null ? v.next = v : (v.next = j.next, j.next = v), _.pending = v;
                    }
                  }
                  l.lanes |= n, v = l.alternate, v !== null && (v.lanes |= n), _l(
                    l.return,
                    n,
                    t
                  ), g.lanes |= n;
                  break;
                }
                v = v.next;
              }
            } else if (l.tag === 10) c = l.type === t.type ? null : l.child;
            else if (l.tag === 18) {
              if (c = l.return, c === null) throw Error(a(341));
              c.lanes |= n, g = c.alternate, g !== null && (g.lanes |= n), _l(c, n, t), c = l.sibling;
            } else c = l.child;
            if (c !== null) c.return = l;
            else for (c = l; c !== null; ) {
              if (c === t) {
                c = null;
                break;
              }
              if (l = c.sibling, l !== null) {
                l.return = c.return, c = l;
                break;
              }
              c = c.return;
            }
            l = c;
          }
          Le(e, t, i.children, n), t = t.child;
        }
        return t;
      case 9:
        return i = t.type, r = t.pendingProps.children, Qn(t, n), i = ot(i), r = r(i), t.flags |= 1, Le(e, t, r, n), t.child;
      case 14:
        return r = t.type, i = gt(r, t.pendingProps), i = gt(r.type, i), qu(e, t, r, i, n);
      case 15:
        return Ju(e, t, t.type, t.pendingProps, n);
      case 17:
        return r = t.type, i = t.pendingProps, i = t.elementType === r ? i : gt(r, i), Hi(e, t), t.tag = 1, Ve(r) ? (e = !0, Ti(t)) : e = !1, Qn(t, n), Hu(t, r, i), $l(t, r, i, n), Wl(null, t, r, !0, e, n);
      case 19:
        return lc(e, t, n);
      case 22:
        return Zu(e, t, n);
    }
    throw Error(a(156, t.tag));
  };
  function Ac(e, t) {
    return us(e, t);
  }
  function fp(e, t, n, r) {
    this.tag = e, this.key = n, this.sibling = this.child = this.return = this.stateNode = this.type = this.elementType = null, this.index = 0, this.ref = null, this.pendingProps = t, this.dependencies = this.memoizedState = this.updateQueue = this.memoizedProps = null, this.mode = r, this.subtreeFlags = this.flags = 0, this.deletions = null, this.childLanes = this.lanes = 0, this.alternate = null;
  }
  function st(e, t, n, r) {
    return new fp(e, t, n, r);
  }
  function sa(e) {
    return e = e.prototype, !(!e || !e.isReactComponent);
  }
  function pp(e) {
    if (typeof e == "function") return sa(e) ? 1 : 0;
    if (e != null) {
      if (e = e.$$typeof, e === St) return 11;
      if (e === _t) return 14;
    }
    return 2;
  }
  function on(e, t) {
    var n = e.alternate;
    return n === null ? (n = st(e.tag, t, e.key, e.mode), n.elementType = e.elementType, n.type = e.type, n.stateNode = e.stateNode, n.alternate = e, e.alternate = n) : (n.pendingProps = t, n.type = e.type, n.flags = 0, n.subtreeFlags = 0, n.deletions = null), n.flags = e.flags & 14680064, n.childLanes = e.childLanes, n.lanes = e.lanes, n.child = e.child, n.memoizedProps = e.memoizedProps, n.memoizedState = e.memoizedState, n.updateQueue = e.updateQueue, t = e.dependencies, n.dependencies = t === null ? null : { lanes: t.lanes, firstContext: t.firstContext }, n.sibling = e.sibling, n.index = e.index, n.ref = e.ref, n;
  }
  function eo(e, t, n, r, i, l) {
    var c = 2;
    if (r = e, typeof e == "function") sa(e) && (c = 1);
    else if (typeof e == "string") c = 5;
    else e: switch (e) {
      case Re:
        return En(n.children, i, l, t);
      case nt:
        c = 8, i |= 8;
        break;
      case Ut:
        return e = st(12, n, t, i | 2), e.elementType = Ut, e.lanes = l, e;
      case be:
        return e = st(13, n, t, i), e.elementType = be, e.lanes = l, e;
      case dt:
        return e = st(19, n, t, i), e.elementType = dt, e.lanes = l, e;
      case he:
        return to(n, i, l, t);
      default:
        if (typeof e == "object" && e !== null) switch (e.$$typeof) {
          case xt:
            c = 10;
            break e;
          case cn:
            c = 9;
            break e;
          case St:
            c = 11;
            break e;
          case _t:
            c = 14;
            break e;
          case Fe:
            c = 16, r = null;
            break e;
        }
        throw Error(a(130, e == null ? e : typeof e, ""));
    }
    return t = st(c, n, t, i), t.elementType = e, t.type = r, t.lanes = l, t;
  }
  function En(e, t, n, r) {
    return e = st(7, e, r, t), e.lanes = n, e;
  }
  function to(e, t, n, r) {
    return e = st(22, e, r, t), e.elementType = he, e.lanes = n, e.stateNode = { isHidden: !1 }, e;
  }
  function ua(e, t, n) {
    return e = st(6, e, null, t), e.lanes = n, e;
  }
  function ca(e, t, n) {
    return t = st(4, e.children !== null ? e.children : [], e.key, t), t.lanes = n, t.stateNode = { containerInfo: e.containerInfo, pendingChildren: null, implementation: e.implementation }, t;
  }
  function mp(e, t, n, r, i) {
    this.tag = t, this.containerInfo = e, this.finishedWork = this.pingCache = this.current = this.pendingChildren = null, this.timeoutHandle = -1, this.callbackNode = this.pendingContext = this.context = null, this.callbackPriority = 0, this.eventTimes = Lo(0), this.expirationTimes = Lo(-1), this.entangledLanes = this.finishedLanes = this.mutableReadLanes = this.expiredLanes = this.pingedLanes = this.suspendedLanes = this.pendingLanes = 0, this.entanglements = Lo(0), this.identifierPrefix = r, this.onRecoverableError = i, this.mutableSourceEagerHydrationData = null;
  }
  function da(e, t, n, r, i, l, c, g, v) {
    return e = new mp(e, t, n, g, v), t === 1 ? (t = 1, l === !0 && (t |= 8)) : t = 0, l = st(3, null, null, t), e.current = l, l.stateNode = e, l.memoizedState = { element: r, isDehydrated: n, cache: null, transitions: null, pendingSuspenseBoundaries: null }, Cl(l), e;
  }
  function gp(e, t, n) {
    var r = 3 < arguments.length && arguments[3] !== void 0 ? arguments[3] : null;
    return { $$typeof: _e, key: r == null ? null : "" + r, children: e, containerInfo: t, implementation: n };
  }
  function Rc(e) {
    if (!e) return Yt;
    e = e._reactInternals;
    e: {
      if (dn(e) !== e || e.tag !== 1) throw Error(a(170));
      var t = e;
      do {
        switch (t.tag) {
          case 3:
            t = t.stateNode.context;
            break e;
          case 1:
            if (Ve(t.type)) {
              t = t.stateNode.__reactInternalMemoizedMergedChildContext;
              break e;
            }
        }
        t = t.return;
      } while (t !== null);
      throw Error(a(171));
    }
    if (e.tag === 1) {
      var n = e.type;
      if (Ve(n)) return ou(e, n, t);
    }
    return t;
  }
  function Dc(e, t, n, r, i, l, c, g, v) {
    return e = da(n, r, !0, e, i, l, c, g, v), e.context = Rc(null), n = e.current, r = $e(), i = nn(n), l = Ot(r, i), l.callback = t ?? null, Jt(n, l, i), e.current.lanes = i, cr(e, i, r), Be(e, r), e;
  }
  function no(e, t, n, r) {
    var i = t.current, l = $e(), c = nn(i);
    return n = Rc(n), t.context === null ? t.context = n : t.pendingContext = n, t = Ot(l, c), t.payload = { element: e }, r = r === void 0 ? null : r, r !== null && (t.callback = r), e = Jt(i, t, c), e !== null && (yt(e, i, c, l), Ni(e, i, c)), c;
  }
  function ro(e) {
    if (e = e.current, !e.child) return null;
    switch (e.child.tag) {
      case 5:
        return e.child.stateNode;
      default:
        return e.child.stateNode;
    }
  }
  function Nc(e, t) {
    if (e = e.memoizedState, e !== null && e.dehydrated !== null) {
      var n = e.retryLane;
      e.retryLane = n !== 0 && n < t ? n : t;
    }
  }
  function fa(e, t) {
    Nc(e, t), (e = e.alternate) && Nc(e, t);
  }
  function hp() {
    return null;
  }
  var zc = typeof reportError == "function" ? reportError : function(e) {
    console.error(e);
  };
  function pa(e) {
    this._internalRoot = e;
  }
  io.prototype.render = pa.prototype.render = function(e) {
    var t = this._internalRoot;
    if (t === null) throw Error(a(409));
    no(e, t, null, null);
  }, io.prototype.unmount = pa.prototype.unmount = function() {
    var e = this._internalRoot;
    if (e !== null) {
      this._internalRoot = null;
      var t = e.containerInfo;
      wn(function() {
        no(null, e, null, null);
      }), t[At] = null;
    }
  };
  function io(e) {
    this._internalRoot = e;
  }
  io.prototype.unstable_scheduleHydration = function(e) {
    if (e) {
      var t = vs();
      e = { blockedOn: null, target: e, priority: t };
      for (var n = 0; n < Bt.length && t !== 0 && t < Bt[n].priority; n++) ;
      Bt.splice(n, 0, e), n === 0 && ws(e);
    }
  };
  function ma(e) {
    return !(!e || e.nodeType !== 1 && e.nodeType !== 9 && e.nodeType !== 11);
  }
  function oo(e) {
    return !(!e || e.nodeType !== 1 && e.nodeType !== 9 && e.nodeType !== 11 && (e.nodeType !== 8 || e.nodeValue !== " react-mount-point-unstable "));
  }
  function Oc() {
  }
  function vp(e, t, n, r, i) {
    if (i) {
      if (typeof r == "function") {
        var l = r;
        r = function() {
          var _ = ro(c);
          l.call(_);
        };
      }
      var c = Dc(t, r, e, 0, null, !1, !1, "", Oc);
      return e._reactRootContainer = c, e[At] = c.current, Cr(e.nodeType === 8 ? e.parentNode : e), wn(), c;
    }
    for (; i = e.lastChild; ) e.removeChild(i);
    if (typeof r == "function") {
      var g = r;
      r = function() {
        var _ = ro(v);
        g.call(_);
      };
    }
    var v = da(e, 0, !1, null, null, !1, !1, "", Oc);
    return e._reactRootContainer = v, e[At] = v.current, Cr(e.nodeType === 8 ? e.parentNode : e), wn(function() {
      no(t, v, n, r);
    }), v;
  }
  function lo(e, t, n, r, i) {
    var l = n._reactRootContainer;
    if (l) {
      var c = l;
      if (typeof i == "function") {
        var g = i;
        i = function() {
          var v = ro(c);
          g.call(v);
        };
      }
      no(t, c, e, i);
    } else c = vp(n, t, e, i, r);
    return ro(c);
  }
  gs = function(e) {
    switch (e.tag) {
      case 3:
        var t = e.stateNode;
        if (t.current.memoizedState.isDehydrated) {
          var n = ur(t.pendingLanes);
          n !== 0 && ($o(t, n | 1), Be(t, ye()), (J & 6) === 0 && (Jn = ye() + 500, Xt()));
        }
        break;
      case 13:
        wn(function() {
          var r = zt(e, 1);
          if (r !== null) {
            var i = $e();
            yt(r, e, 1, i);
          }
        }), fa(e, 1);
    }
  }, Fo = function(e) {
    if (e.tag === 13) {
      var t = zt(e, 134217728);
      if (t !== null) {
        var n = $e();
        yt(t, e, 134217728, n);
      }
      fa(e, 134217728);
    }
  }, hs = function(e) {
    if (e.tag === 13) {
      var t = nn(e), n = zt(e, t);
      if (n !== null) {
        var r = $e();
        yt(n, e, t, r);
      }
      fa(e, t);
    }
  }, vs = function() {
    return re;
  }, ys = function(e, t) {
    var n = re;
    try {
      return re = e, t();
    } finally {
      re = n;
    }
  }, Ro = function(e, t, n) {
    switch (t) {
      case "input":
        if (Eo(e, n), t = n.name, n.type === "radio" && t != null) {
          for (n = e; n.parentNode; ) n = n.parentNode;
          for (n = n.querySelectorAll("input[name=" + JSON.stringify("" + t) + '][type="radio"]'), t = 0; t < n.length; t++) {
            var r = n[t];
            if (r !== e && r.form === e.form) {
              var i = Ei(r);
              if (!i) throw Error(a(90));
              Wa(r), Eo(r, i);
            }
          }
        }
        break;
      case "textarea":
        Qa(e, n);
        break;
      case "select":
        t = n.value, t != null && xn(e, !!n.multiple, t, !1);
    }
  }, ns = oa, rs = wn;
  var yp = { usingClientEntryPoint: !1, Events: [jr, Fn, Ei, es, ts, oa] }, Vr = { findFiberByHostInstance: fn, bundleType: 0, version: "18.3.1", rendererPackageName: "react-dom" }, kp = { bundleType: Vr.bundleType, version: Vr.version, rendererPackageName: Vr.rendererPackageName, rendererConfig: Vr.rendererConfig, overrideHookState: null, overrideHookStateDeletePath: null, overrideHookStateRenamePath: null, overrideProps: null, overridePropsDeletePath: null, overridePropsRenamePath: null, setErrorHandler: null, setSuspenseHandler: null, scheduleUpdate: null, currentDispatcherRef: q.ReactCurrentDispatcher, findHostInstanceByFiber: function(e) {
    return e = as(e), e === null ? null : e.stateNode;
  }, findFiberByHostInstance: Vr.findFiberByHostInstance || hp, findHostInstancesForRefresh: null, scheduleRefresh: null, scheduleRoot: null, setRefreshHandler: null, getCurrentFiber: null, reconcilerVersion: "18.3.1-next-f1338f8080-20240426" };
  if (typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ < "u") {
    var ao = __REACT_DEVTOOLS_GLOBAL_HOOK__;
    if (!ao.isDisabled && ao.supportsFiber) try {
      ii = ao.inject(kp), Et = ao;
    } catch {
    }
  }
  return Ke.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED = yp, Ke.createPortal = function(e, t) {
    var n = 2 < arguments.length && arguments[2] !== void 0 ? arguments[2] : null;
    if (!ma(t)) throw Error(a(200));
    return gp(e, t, null, n);
  }, Ke.createRoot = function(e, t) {
    if (!ma(e)) throw Error(a(299));
    var n = !1, r = "", i = zc;
    return t != null && (t.unstable_strictMode === !0 && (n = !0), t.identifierPrefix !== void 0 && (r = t.identifierPrefix), t.onRecoverableError !== void 0 && (i = t.onRecoverableError)), t = da(e, 1, !1, null, null, n, !1, r, i), e[At] = t.current, Cr(e.nodeType === 8 ? e.parentNode : e), new pa(t);
  }, Ke.findDOMNode = function(e) {
    if (e == null) return null;
    if (e.nodeType === 1) return e;
    var t = e._reactInternals;
    if (t === void 0)
      throw typeof e.render == "function" ? Error(a(188)) : (e = Object.keys(e).join(","), Error(a(268, e)));
    return e = as(t), e = e === null ? null : e.stateNode, e;
  }, Ke.flushSync = function(e) {
    return wn(e);
  }, Ke.hydrate = function(e, t, n) {
    if (!oo(t)) throw Error(a(200));
    return lo(null, e, t, !0, n);
  }, Ke.hydrateRoot = function(e, t, n) {
    if (!ma(e)) throw Error(a(405));
    var r = n != null && n.hydratedSources || null, i = !1, l = "", c = zc;
    if (n != null && (n.unstable_strictMode === !0 && (i = !0), n.identifierPrefix !== void 0 && (l = n.identifierPrefix), n.onRecoverableError !== void 0 && (c = n.onRecoverableError)), t = Dc(t, null, e, 1, n ?? null, i, !1, l, c), e[At] = t.current, Cr(e), r) for (e = 0; e < r.length; e++) n = r[e], i = n._getVersion, i = i(n._source), t.mutableSourceEagerHydrationData == null ? t.mutableSourceEagerHydrationData = [n, i] : t.mutableSourceEagerHydrationData.push(
      n,
      i
    );
    return new io(t);
  }, Ke.render = function(e, t, n) {
    if (!oo(t)) throw Error(a(200));
    return lo(null, e, t, !1, n);
  }, Ke.unmountComponentAtNode = function(e) {
    if (!oo(e)) throw Error(a(40));
    return e._reactRootContainer ? (wn(function() {
      lo(null, null, e, !1, function() {
        e._reactRootContainer = null, e[At] = null;
      });
    }), !0) : !1;
  }, Ke.unstable_batchedUpdates = oa, Ke.unstable_renderSubtreeIntoContainer = function(e, t, n, r) {
    if (!oo(n)) throw Error(a(200));
    if (e == null || e._reactInternals === void 0) throw Error(a(38));
    return lo(e, t, n, !1, r);
  }, Ke.version = "18.3.1-next-f1338f8080-20240426", Ke;
}
var Hc;
function Ip() {
  if (Hc) return ya.exports;
  Hc = 1;
  function o() {
    if (!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ > "u" || typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE != "function"))
      try {
        __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(o);
      } catch (s) {
        console.error(s);
      }
  }
  return o(), ya.exports = jp(), ya.exports;
}
var Bc;
function xp() {
  if (Bc) return uo;
  Bc = 1;
  var o = Ip();
  return uo.createRoot = o.createRoot, uo.hydrateRoot = o.hydrateRoot, uo;
}
var Ap = xp();
const Kc = (o) => {
  let s;
  const a = /* @__PURE__ */ new Set(), d = (E, C) => {
    const M = typeof E == "function" ? E(s) : E;
    if (!Object.is(M, s)) {
      const A = s;
      s = C ?? (typeof M != "object" || M === null) ? M : Object.assign({}, s, M), a.forEach(($) => $(s, A));
    }
  }, f = () => s, m = { setState: d, getState: f, getInitialState: () => h, subscribe: (E) => (a.add(E), () => a.delete(E)) }, h = s = o(d, f, m);
  return m;
}, Rp = ((o) => o ? Kc(o) : Kc), Dp = (o) => o;
function Np(o, s = Dp) {
  const a = va.useSyncExternalStore(
    o.subscribe,
    va.useCallback(() => s(o.getState()), [o, s]),
    () => s(o.getInitialState())
  );
  return va.useDebugValue(a), a;
}
const Gc = (o) => {
  const s = Rp(o), a = (d) => Np(s, d);
  return Object.assign(a, s), a;
}, La = ((o) => o ? Gc(o) : Gc);
function dd(o, s) {
  let a;
  try {
    a = o();
  } catch {
    return;
  }
  return {
    getItem: (f) => {
      var u;
      const p = (h) => h === null ? null : JSON.parse(h, void 0), m = (u = a.getItem(f)) != null ? u : null;
      return m instanceof Promise ? m.then(p) : p(m);
    },
    setItem: (f, u) => a.setItem(f, JSON.stringify(u, void 0)),
    removeItem: (f) => a.removeItem(f)
  };
}
const ja = (o) => (s) => {
  try {
    const a = o(s);
    return a instanceof Promise ? a : {
      then(d) {
        return ja(d)(a);
      },
      catch(d) {
        return this;
      }
    };
  } catch (a) {
    return {
      then(d) {
        return this;
      },
      catch(d) {
        return ja(d)(a);
      }
    };
  }
}, zp = (o, s) => (a, d, f) => {
  let u = {
    storage: dd(() => window.localStorage),
    partialize: (z) => z,
    version: 0,
    merge: (z, ie) => ({
      ...ie,
      ...z
    }),
    ...s
  }, p = !1, m = 0;
  const h = /* @__PURE__ */ new Set(), E = /* @__PURE__ */ new Set();
  let C = u.storage;
  if (!C)
    return o(
      (...z) => {
        console.warn(
          `[zustand persist middleware] Unable to update item '${u.name}', the given storage is currently unavailable.`
        ), a(...z);
      },
      d,
      f
    );
  const M = () => {
    const z = u.partialize({ ...d() });
    return C.setItem(u.name, {
      state: z,
      version: u.version
    });
  }, A = f.setState;
  f.setState = (...z) => (A(...z), M());
  const $ = o(
    (...z) => (a(...z), M()),
    d,
    f
  );
  f.getInitialState = () => $;
  let Q;
  const b = () => {
    var z, ie;
    if (!C) return;
    const ge = ++m;
    p = !1, h.forEach((q) => {
      var ae;
      return q((ae = d()) != null ? ae : $);
    });
    const fe = ((ie = u.onRehydrateStorage) == null ? void 0 : ie.call(u, (z = d()) != null ? z : $)) || void 0;
    return ja(C.getItem.bind(C))(u.name).then((q) => {
      if (q)
        if (typeof q.version == "number" && q.version !== u.version) {
          if (u.migrate) {
            const ae = u.migrate(
              q.state,
              q.version
            );
            return ae instanceof Promise ? ae.then((_e) => [!0, _e]) : [!0, ae];
          }
          console.error(
            "State loaded from storage couldn't be migrated since no migrate function was provided"
          );
        } else
          return [!1, q.state];
      return [!1, void 0];
    }).then((q) => {
      var ae;
      if (ge !== m)
        return;
      const [_e, Re] = q;
      if (Q = u.merge(
        Re,
        (ae = d()) != null ? ae : $
      ), a(Q, !0), _e)
        return M();
    }).then(() => {
      ge === m && (fe == null || fe(d(), void 0), Q = d(), p = !0, E.forEach((q) => q(Q)));
    }).catch((q) => {
      ge === m && (fe == null || fe(void 0, q));
    });
  };
  return f.persist = {
    setOptions: (z) => {
      u = {
        ...u,
        ...z
      }, z.storage && (C = z.storage);
    },
    clearStorage: () => {
      ++m, C == null || C.removeItem(u.name);
    },
    getOptions: () => u,
    rehydrate: () => b(),
    hasHydrated: () => p,
    onHydrate: (z) => (h.add(z), () => {
      h.delete(z);
    }),
    onFinishHydration: (z) => (E.add(z), () => {
      E.delete(z);
    })
  }, u.skipHydration || b(), Q || $;
}, Op = zp;
var fd = Symbol.for("immer-nothing"), Qc = Symbol.for("immer-draftable"), tt = Symbol.for("immer-state");
function kt(o, ...s) {
  throw new Error(
    `[Immer] minified error nr: ${o}. Full error at: https://bit.ly/3cXEKWf`
  );
}
var Gr = Object.getPrototypeOf;
function tr(o) {
  return !!o && !!o[tt];
}
function jn(o) {
  var s;
  return o ? pd(o) || Array.isArray(o) || !!o[Qc] || !!((s = o.constructor) != null && s[Qc]) || qr(o) || wo(o) : !1;
}
var Mp = Object.prototype.constructor.toString(), bc = /* @__PURE__ */ new WeakMap();
function pd(o) {
  if (!o || typeof o != "object")
    return !1;
  const s = Object.getPrototypeOf(o);
  if (s === null || s === Object.prototype)
    return !0;
  const a = Object.hasOwnProperty.call(s, "constructor") && s.constructor;
  if (a === Object)
    return !0;
  if (typeof a != "function")
    return !1;
  let d = bc.get(a);
  return d === void 0 && (d = Function.toString.call(a), bc.set(a, d)), d === Mp;
}
function go(o, s, a = !0) {
  ko(o) === 0 ? (a ? Reflect.ownKeys(o) : Object.keys(o)).forEach((f) => {
    s(f, o[f], o);
  }) : o.forEach((d, f) => s(f, d, o));
}
function ko(o) {
  const s = o[tt];
  return s ? s.type_ : Array.isArray(o) ? 1 : qr(o) ? 2 : wo(o) ? 3 : 0;
}
function Ia(o, s) {
  return ko(o) === 2 ? o.has(s) : Object.prototype.hasOwnProperty.call(o, s);
}
function md(o, s, a) {
  const d = ko(o);
  d === 2 ? o.set(s, a) : d === 3 ? o.add(a) : o[s] = a;
}
function Lp(o, s) {
  return o === s ? o !== 0 || 1 / o === 1 / s : o !== o && s !== s;
}
function qr(o) {
  return o instanceof Map;
}
function wo(o) {
  return o instanceof Set;
}
function Cn(o) {
  return o.copy_ || o.base_;
}
function xa(o, s) {
  if (qr(o))
    return new Map(o);
  if (wo(o))
    return new Set(o);
  if (Array.isArray(o))
    return Array.prototype.slice.call(o);
  const a = pd(o);
  if (s === !0 || s === "class_only" && !a) {
    const d = Object.getOwnPropertyDescriptors(o);
    delete d[tt];
    let f = Reflect.ownKeys(d);
    for (let u = 0; u < f.length; u++) {
      const p = f[u], m = d[p];
      m.writable === !1 && (m.writable = !0, m.configurable = !0), (m.get || m.set) && (d[p] = {
        configurable: !0,
        writable: !0,
        // could live with !!desc.set as well here...
        enumerable: m.enumerable,
        value: o[p]
      });
    }
    return Object.create(Gr(o), d);
  } else {
    const d = Gr(o);
    if (d !== null && a)
      return { ...o };
    const f = Object.create(d);
    return Object.assign(f, o);
  }
}
function $a(o, s = !1) {
  return So(o) || tr(o) || !jn(o) || (ko(o) > 1 && Object.defineProperties(o, {
    set: co,
    add: co,
    clear: co,
    delete: co
  }), Object.freeze(o), s && Object.values(o).forEach((a) => $a(a, !0))), o;
}
function $p() {
  kt(2);
}
var co = {
  value: $p
};
function So(o) {
  return o === null || typeof o != "object" ? !0 : Object.isFrozen(o);
}
var Fp = {};
function In(o) {
  const s = Fp[o];
  return s || kt(0, o), s;
}
var Qr;
function gd() {
  return Qr;
}
function Up(o, s) {
  return {
    drafts_: [],
    parent_: o,
    immer_: s,
    // Whenever the modified draft contains a draft from another scope, we
    // need to prevent auto-freezing so the unowned draft can be finalized.
    canAutoFreeze_: !0,
    unfinalizedDrafts_: 0
  };
}
function Yc(o, s) {
  s && (In("Patches"), o.patches_ = [], o.inversePatches_ = [], o.patchListener_ = s);
}
function Aa(o) {
  Ra(o), o.drafts_.forEach(Vp), o.drafts_ = null;
}
function Ra(o) {
  o === Qr && (Qr = o.parent_);
}
function Xc(o) {
  return Qr = Up(Qr, o);
}
function Vp(o) {
  const s = o[tt];
  s.type_ === 0 || s.type_ === 1 ? s.revoke_() : s.revoked_ = !0;
}
function qc(o, s) {
  s.unfinalizedDrafts_ = s.drafts_.length;
  const a = s.drafts_[0];
  return o !== void 0 && o !== a ? (a[tt].modified_ && (Aa(s), kt(4)), jn(o) && (o = ho(s, o), s.parent_ || vo(s, o)), s.patches_ && In("Patches").generateReplacementPatches_(
    a[tt].base_,
    o,
    s.patches_,
    s.inversePatches_
  )) : o = ho(s, a, []), Aa(s), s.patches_ && s.patchListener_(s.patches_, s.inversePatches_), o !== fd ? o : void 0;
}
function ho(o, s, a) {
  if (So(s))
    return s;
  const d = o.immer_.shouldUseStrictIteration(), f = s[tt];
  if (!f)
    return go(
      s,
      (u, p) => Jc(o, f, s, u, p, a),
      d
    ), s;
  if (f.scope_ !== o)
    return s;
  if (!f.modified_)
    return vo(o, f.base_, !0), f.base_;
  if (!f.finalized_) {
    f.finalized_ = !0, f.scope_.unfinalizedDrafts_--;
    const u = f.copy_;
    let p = u, m = !1;
    f.type_ === 3 && (p = new Set(u), u.clear(), m = !0), go(
      p,
      (h, E) => Jc(
        o,
        f,
        u,
        h,
        E,
        a,
        m
      ),
      d
    ), vo(o, u, !1), a && o.patches_ && In("Patches").generatePatches_(
      f,
      a,
      o.patches_,
      o.inversePatches_
    );
  }
  return f.copy_;
}
function Jc(o, s, a, d, f, u, p) {
  if (f == null || typeof f != "object" && !p)
    return;
  const m = So(f);
  if (!(m && !p)) {
    if (tr(f)) {
      const h = u && s && s.type_ !== 3 && // Set objects are atomic since they have no keys.
      !Ia(s.assigned_, d) ? u.concat(d) : void 0, E = ho(o, f, h);
      if (md(a, d, E), tr(E))
        o.canAutoFreeze_ = !1;
      else
        return;
    } else p && a.add(f);
    if (jn(f) && !m) {
      if (!o.immer_.autoFreeze_ && o.unfinalizedDrafts_ < 1 || s && s.base_ && s.base_[d] === f && m)
        return;
      ho(o, f), (!s || !s.scope_.parent_) && typeof d != "symbol" && (qr(a) ? a.has(d) : Object.prototype.propertyIsEnumerable.call(a, d)) && vo(o, f);
    }
  }
}
function vo(o, s, a = !1) {
  !o.parent_ && o.immer_.autoFreeze_ && o.canAutoFreeze_ && $a(s, a);
}
function Wp(o, s) {
  const a = Array.isArray(o), d = {
    type_: a ? 1 : 0,
    // Track which produce call this is associated with.
    scope_: s ? s.scope_ : gd(),
    // True for both shallow and deep changes.
    modified_: !1,
    // Used during finalization.
    finalized_: !1,
    // Track which properties have been assigned (true) or deleted (false).
    assigned_: {},
    // The parent draft state.
    parent_: s,
    // The base state.
    base_: o,
    // The base proxy.
    draft_: null,
    // set below
    // The base copy with any updated values.
    copy_: null,
    // Called by the `produce` function.
    revoke_: null,
    isManual_: !1
  };
  let f = d, u = Fa;
  a && (f = [d], u = br);
  const { revoke: p, proxy: m } = Proxy.revocable(f, u);
  return d.draft_ = m, d.revoke_ = p, m;
}
var Fa = {
  get(o, s) {
    if (s === tt)
      return o;
    const a = Cn(o);
    if (!Ia(a, s))
      return Hp(o, a, s);
    const d = a[s];
    return o.finalized_ || !jn(d) ? d : d === Sa(o.base_, s) ? (_a(o), o.copy_[s] = Na(d, o)) : d;
  },
  has(o, s) {
    return s in Cn(o);
  },
  ownKeys(o) {
    return Reflect.ownKeys(Cn(o));
  },
  set(o, s, a) {
    const d = hd(Cn(o), s);
    if (d != null && d.set)
      return d.set.call(o.draft_, a), !0;
    if (!o.modified_) {
      const f = Sa(Cn(o), s), u = f == null ? void 0 : f[tt];
      if (u && u.base_ === a)
        return o.copy_[s] = a, o.assigned_[s] = !1, !0;
      if (Lp(a, f) && (a !== void 0 || Ia(o.base_, s)))
        return !0;
      _a(o), Da(o);
    }
    return o.copy_[s] === a && // special case: handle new props with value 'undefined'
    (a !== void 0 || s in o.copy_) || // special case: NaN
    Number.isNaN(a) && Number.isNaN(o.copy_[s]) || (o.copy_[s] = a, o.assigned_[s] = !0), !0;
  },
  deleteProperty(o, s) {
    return Sa(o.base_, s) !== void 0 || s in o.base_ ? (o.assigned_[s] = !1, _a(o), Da(o)) : delete o.assigned_[s], o.copy_ && delete o.copy_[s], !0;
  },
  // Note: We never coerce `desc.value` into an Immer draft, because we can't make
  // the same guarantee in ES5 mode.
  getOwnPropertyDescriptor(o, s) {
    const a = Cn(o), d = Reflect.getOwnPropertyDescriptor(a, s);
    return d && {
      writable: !0,
      configurable: o.type_ !== 1 || s !== "length",
      enumerable: d.enumerable,
      value: a[s]
    };
  },
  defineProperty() {
    kt(11);
  },
  getPrototypeOf(o) {
    return Gr(o.base_);
  },
  setPrototypeOf() {
    kt(12);
  }
}, br = {};
go(Fa, (o, s) => {
  br[o] = function() {
    return arguments[0] = arguments[0][0], s.apply(this, arguments);
  };
});
br.deleteProperty = function(o, s) {
  return br.set.call(this, o, s, void 0);
};
br.set = function(o, s, a) {
  return Fa.set.call(this, o[0], s, a, o[0]);
};
function Sa(o, s) {
  const a = o[tt];
  return (a ? Cn(a) : o)[s];
}
function Hp(o, s, a) {
  var f;
  const d = hd(s, a);
  return d ? "value" in d ? d.value : (
    // This is a very special case, if the prop is a getter defined by the
    // prototype, we should invoke it with the draft as context!
    (f = d.get) == null ? void 0 : f.call(o.draft_)
  ) : void 0;
}
function hd(o, s) {
  if (!(s in o))
    return;
  let a = Gr(o);
  for (; a; ) {
    const d = Object.getOwnPropertyDescriptor(a, s);
    if (d)
      return d;
    a = Gr(a);
  }
}
function Da(o) {
  o.modified_ || (o.modified_ = !0, o.parent_ && Da(o.parent_));
}
function _a(o) {
  o.copy_ || (o.copy_ = xa(
    o.base_,
    o.scope_.immer_.useStrictShallowCopy_
  ));
}
var Bp = class {
  constructor(o) {
    this.autoFreeze_ = !0, this.useStrictShallowCopy_ = !1, this.useStrictIteration_ = !0, this.produce = (s, a, d) => {
      if (typeof s == "function" && typeof a != "function") {
        const u = a;
        a = s;
        const p = this;
        return function(h = u, ...E) {
          return p.produce(h, (C) => a.call(this, C, ...E));
        };
      }
      typeof a != "function" && kt(6), d !== void 0 && typeof d != "function" && kt(7);
      let f;
      if (jn(s)) {
        const u = Xc(this), p = Na(s, void 0);
        let m = !0;
        try {
          f = a(p), m = !1;
        } finally {
          m ? Aa(u) : Ra(u);
        }
        return Yc(u, d), qc(f, u);
      } else if (!s || typeof s != "object") {
        if (f = a(s), f === void 0 && (f = s), f === fd && (f = void 0), this.autoFreeze_ && $a(f, !0), d) {
          const u = [], p = [];
          In("Patches").generateReplacementPatches_(s, f, u, p), d(u, p);
        }
        return f;
      } else
        kt(1, s);
    }, this.produceWithPatches = (s, a) => {
      if (typeof s == "function")
        return (p, ...m) => this.produceWithPatches(p, (h) => s(h, ...m));
      let d, f;
      return [this.produce(s, a, (p, m) => {
        d = p, f = m;
      }), d, f];
    }, typeof (o == null ? void 0 : o.autoFreeze) == "boolean" && this.setAutoFreeze(o.autoFreeze), typeof (o == null ? void 0 : o.useStrictShallowCopy) == "boolean" && this.setUseStrictShallowCopy(o.useStrictShallowCopy), typeof (o == null ? void 0 : o.useStrictIteration) == "boolean" && this.setUseStrictIteration(o.useStrictIteration);
  }
  createDraft(o) {
    jn(o) || kt(8), tr(o) && (o = Kp(o));
    const s = Xc(this), a = Na(o, void 0);
    return a[tt].isManual_ = !0, Ra(s), a;
  }
  finishDraft(o, s) {
    const a = o && o[tt];
    (!a || !a.isManual_) && kt(9);
    const { scope_: d } = a;
    return Yc(d, s), qc(void 0, d);
  }
  /**
   * Pass true to automatically freeze all copies created by Immer.
   *
   * By default, auto-freezing is enabled.
   */
  setAutoFreeze(o) {
    this.autoFreeze_ = o;
  }
  /**
   * Pass true to enable strict shallow copy.
   *
   * By default, immer does not copy the object descriptors such as getter, setter and non-enumrable properties.
   */
  setUseStrictShallowCopy(o) {
    this.useStrictShallowCopy_ = o;
  }
  /**
   * Pass false to use faster iteration that skips non-enumerable properties
   * but still handles symbols for compatibility.
   *
   * By default, strict iteration is enabled (includes all own properties).
   */
  setUseStrictIteration(o) {
    this.useStrictIteration_ = o;
  }
  shouldUseStrictIteration() {
    return this.useStrictIteration_;
  }
  applyPatches(o, s) {
    let a;
    for (a = s.length - 1; a >= 0; a--) {
      const f = s[a];
      if (f.path.length === 0 && f.op === "replace") {
        o = f.value;
        break;
      }
    }
    a > -1 && (s = s.slice(a + 1));
    const d = In("Patches").applyPatches_;
    return tr(o) ? d(o, s) : this.produce(
      o,
      (f) => d(f, s)
    );
  }
};
function Na(o, s) {
  const a = qr(o) ? In("MapSet").proxyMap_(o, s) : wo(o) ? In("MapSet").proxySet_(o, s) : Wp(o, s);
  return (s ? s.scope_ : gd()).drafts_.push(a), a;
}
function Kp(o) {
  return tr(o) || kt(10, o), vd(o);
}
function vd(o) {
  if (!jn(o) || So(o))
    return o;
  const s = o[tt];
  let a, d = !0;
  if (s) {
    if (!s.modified_)
      return s.base_;
    s.finalized_ = !0, a = xa(o, s.scope_.immer_.useStrictShallowCopy_), d = s.scope_.immer_.shouldUseStrictIteration();
  } else
    a = xa(o, !0);
  return go(
    a,
    (f, u) => {
      md(a, f, vd(u));
    },
    d
  ), s && (s.finalized_ = !1), a;
}
var Gp = new Bp(), Qp = Gp.produce;
const bp = (o) => (s, a, d) => (d.setState = (f, u, ...p) => {
  const m = typeof f == "function" ? Qp(f) : f;
  return s(m, u, ...p);
}, o(d.setState, a, d)), Yp = bp;
let Xp = 0;
const H = (o = "id") => `${o}_${Date.now().toString(36)}${(Xp++).toString(36)}${Math.random().toString(36).slice(2, 6)}`, Ge = (o, s) => o + Math.random() * (s - o), we = (o, s) => Math.floor(Ge(o, s + 1)), Me = (o) => o[Math.floor(Math.random() * o.length)], Qe = (o, s, a) => Math.max(s, Math.min(a, o)), Ft = 24, qp = /* @__PURE__ */ new Date("2026-10-13T22:00:00Z"), Br = () => Math.max(0, Math.floor((Date.now() - qp.getTime()) / 36e5)), un = (o) => Math.floor(o / Ft), Jp = [
  { id: "researcher", title: "Researcher", department: "research", description: "Verzamelt trends, zoekvolume en vragen van kijkers.", skills: ["Data Mining", "Trend Spotting", "Accuracy"], baseSalary: 38, hireCost: 400 },
  { id: "niche_analyst", title: "Niche Analyst", department: "research", description: "Beoordeelt onderwerpen op RPM, concurrentie en blijvende waarde.", skills: ["Market Sizing", "RPM Analysis", "Strategy"], baseSalary: 42, hireCost: 450 },
  { id: "competitor_analyst", title: "Competitor Analyst", department: "research", description: "Ontleedt uitschieters van kanalen zoals IFOLOGY.", skills: ["Outlier Detection", "Pattern Analysis", "Speed"], baseSalary: 40, hireCost: 430 },
  { id: "topic_finder", title: "Topic Finder", department: "research", description: "Maakt van onderzoek een shortlist van What If-onderwerpen.", skills: ["Curiosity", "Search Intent", "Speed"], baseSalary: 36, hireCost: 380 },
  { id: "idea_generator", title: "Idea Generator", department: "creative", description: "Bedenkt invalshoeken en twists die opvallen.", skills: ["Creativity", "Formats", "Speed"], baseSalary: 36, hireCost: 380 },
  { id: "title_specialist", title: "Title Specialist", department: "creative", description: "Schrijft titels met een getal en nieuwsgierigheid.", skills: ["Copywriting", "CTR Psychology", "SEO"], baseSalary: 44, hireCost: 480 },
  { id: "hook_specialist", title: "Hook Specialist", department: "creative", description: "Maakt de eerste 5 seconden zo spannend mogelijk.", skills: ["Hooks", "Retention", "Pacing"], baseSalary: 44, hireCost: 480 },
  { id: "scriptwriter", title: "Scriptwriter", department: "script", description: "Schrijft het hele script (Engels, regie in het Nederlands).", skills: ["Writing", "Structure", "Speed"], baseSalary: 48, hireCost: 520 },
  { id: "storytelling_expert", title: "Storytelling Expert", department: "script", description: "Zorgt voor escalatie, open vragen en emotie.", skills: ["Narrative", "Emotion", "Retention"], baseSalary: 50, hireCost: 560 },
  { id: "fact_checker", title: "Fact Checker", department: "script", description: "Checkt de “this part is real”-momenten.", skills: ["Accuracy", "Research", "Rigor"], baseSalary: 38, hireCost: 400 },
  { id: "quality_controller", title: "Quality Controller", department: "production", description: "Laatste check op geluid, beeld, tempo en clipping.", skills: ["Attention to Detail", "Policy", "Rigor"], baseSalary: 46, hireCost: 500 },
  { id: "voice_director", title: "Voice Director", department: "voice", description: "Kiest stem en toon per personage in ElevenLabs.", skills: ["Direction", "Tone", "Audio"], baseSalary: 44, hireCost: 480 },
  { id: "voice_generator", title: "Voice Generator", department: "voice", description: "Maakt de voice-overs in ElevenLabs v4.", skills: ["Audio", "Speed", "Clarity"], baseSalary: 34, hireCost: 360 },
  { id: "video_editor", title: "Video Editor", department: "production", description: "Animeert in Blender en monteert de video.", skills: ["Editing", "Pacing", "Motion"], baseSalary: 52, hireCost: 600 },
  { id: "visual_researcher", title: "Visual Researcher", department: "production", description: "Verzorgt sets, props en beeldmateriaal.", skills: ["Sourcing", "Licensing", "Speed"], baseSalary: 36, hireCost: 380 },
  { id: "editing_supervisor", title: "Editing Supervisor", department: "production", description: "Bewaakt de montage en de renderwachtrij.", skills: ["Leadership", "Editing", "Rigor"], baseSalary: 56, hireCost: 650 },
  { id: "thumbnail_designer", title: "Thumbnail Designer", department: "thumbnail", description: "Ontwerpt opvallende, leesbare thumbnails.", skills: ["Design", "Composition", "Speed"], baseSalary: 44, hireCost: 480 },
  { id: "ctr_specialist", title: "CTR Specialist", department: "thumbnail", description: "Test thumbnails en titels op klikken.", skills: ["CTR Psychology", "Testing", "Data"], baseSalary: 48, hireCost: 520 },
  { id: "upload_manager", title: "Upload Manager", department: "publishing", description: "Maakt uploads, planning en eindschermen klaar.", skills: ["Operations", "Scheduling", "Accuracy"], baseSalary: 34, hireCost: 360 },
  { id: "seo_specialist", title: "SEO Specialist", department: "publishing", description: "Schrijft beschrijving, tags en hoofdstukken.", skills: ["SEO", "Keywords", "Copywriting"], baseSalary: 40, hireCost: 430 },
  { id: "social_media_manager", title: "Social Media Manager", department: "publishing", description: "Promoot uploads en shorts.", skills: ["Community", "Copywriting", "Timing"], baseSalary: 38, hireCost: 400 },
  { id: "ceo_agent", title: "CEO Agent", department: "ceo", description: "Bepaalt de koers, bereidt goedkeuringen voor en leidt de crisiskamer.", skills: ["Strategy", "Leadership", "Decisions"], baseSalary: 80, hireCost: 1200 },
  { id: "financial_manager", title: "Financial Manager", department: "ceo", description: "Houdt kosten en opbrengst bij.", skills: ["Finance", "Forecasting", "Rigor"], baseSalary: 60, hireCost: 800 },
  { id: "performance_analyst", title: "Performance Analyst", department: "ceo", description: "Analyseert CTR, kijkduur en kanaaltrends.", skills: ["Analytics", "Data", "Insight"], baseSalary: 56, hireCost: 700 }
], Pn = (o) => Jp.find((s) => s.id === o), Zp = ["Ava", "Leo", "Mia", "Noah", "Zara", "Kai", "Luna", "Omar", "Iris", "Finn", "Nova", "Ezra", "Yuki", "Ravi", "Lena", "Milo", "Sara", "Theo", "Ines", "Jonas", "Aria", "Sami", "Elio", "Freya", "Hugo", "Nia", "Otto", "Pia", "Rex", "Vera"], em = ["Byte", "Vector", "Pixel", "Quill", "Nimbus", "Cortex", "Echo", "Prism", "Atlas", "Vale", "Sterling", "Lumen", "Hart", "Novak", "Reyes", "Kim", "Okafor", "Silva", "Berg", "Moreau"], tm = [
  "Analytisch en rustig, houdt van spreadsheets.",
  "Energieke optimist die elk succesje viert.",
  "Perfectionist, zegt nee tegen haastwerk.",
  "Snel en praktisch, eerst af, dan mooi.",
  "Nieuwsgierige verteller die drie keer “waarom?” vraagt.",
  "Stille expert, post weinig maar altijd raak.",
  "Competitief, vergelijkt alles met de concurrentie.",
  "Teamspeler die graag om feedback vraagt."
], nm = ["#f1c7a5", "#d9a07a", "#a86b48", "#7a4a2e", "#f5d6bf", "#c58c64"], rm = ["#1f1a17", "#4a2f1d", "#b5651d", "#e8c26a", "#2b2b2b", "#7c3aed", "#ef4444", "#94a3b8"];
function yd(o, s, a = {}) {
  const d = Pn(o), f = a.name ?? `${Me(Zp)} ${Me(em)}`, u = {
    research: "#3b82f6",
    creative: "#a855f7",
    script: "#fb923c",
    voice: "#ec4899",
    production: "#f43f5e",
    thumbnail: "#f59e0b",
    publishing: "#22d3ee",
    ceo: "#facc15"
  }, p = {};
  return d.skills.forEach((m) => p[m] = Math.round(Ge(42, 72))), {
    id: H("ag"),
    name: f,
    role: o,
    department: d.department,
    avatar: {
      skin: Me(nm),
      hair: Me(rm),
      shirt: u[d.department],
      initials: f.split(" ").map((m) => m[0]).join("")
    },
    personality: Me(tm),
    instructions: `Jij bent de ${d.title} bij Driftmark Studio (3D What If-kanaal). ${d.description} Lever kort en duidelijk werk op en geef het door aan de volgende afdeling.`,
    skills: p,
    level: 1,
    xp: 0,
    performance: Math.round(Ge(60, 80)),
    morale: 80,
    salary: d.baseSalary,
    state: "idle",
    currentTaskId: null,
    taskHistory: [],
    channelIds: [],
    hiredDay: s,
    completed: 0,
    ...a
  };
}
const yo = (o) => {
  const s = Object.values(o.skills);
  return s.reduce((d, f) => d + f, 0) / Math.max(1, s.length) * (0.85 + o.level * 0.05) * (0.7 + o.morale / 333);
}, za = (o) => 100 + (o - 1) * 80, Zc = (o) => 250 + (o - 1) * 200, im = [
  { id: "first_video", title: "First Upload", description: "Publish your first video.", icon: "🎬", xp: 100 },
  { id: "five_videos", title: "Content Machine", description: "Publish 5 videos.", icon: "🏭", xp: 200 },
  { id: "views_100k", title: "100K Views", description: "Reach 100,000 total views across all channels.", icon: "👀", xp: 300 },
  { id: "views_1m", title: "Millionaire Views", description: "Reach 1,000,000 total views.", icon: "💎", xp: 800 },
  { id: "monetized", title: "Monetized!", description: "Get your first channel monetized (1,000 subscribers).", icon: "💸", xp: 300 },
  { id: "rev_1000", title: "First €1,000", description: "Earn €1,000 in total ad revenue.", icon: "💶", xp: 400 },
  { id: "team_10", title: "Growing Team", description: "Hire your first new AI agent.", icon: "👥", xp: 150 },
  { id: "team_20", title: "Full House", description: "Employ 20 AI agents.", icon: "🏢", xp: 300 },
  { id: "first_upgrade", title: "Interior Designer", description: "Buy your first office upgrade.", icon: "🛋️", xp: 100 },
  { id: "war_room", title: "Crisis Manager", description: "Resolve your first War Room case.", icon: "🛡️", xp: 200 },
  { id: "level_5", title: "Rising Company", description: "Reach company level 5.", icon: "⭐", xp: 300 },
  { id: "two_channels", title: "Network Builder", description: "Launch a new channel of your own.", icon: "📺", xp: 150 },
  { id: "agent_lvl5", title: "Elite Employee", description: "Train an agent to level 5.", icon: "🎓", xp: 200 }
], om = [
  { id: "render_farm", name: "Render Farm", description: "GPU racks for the edit bay.", icon: "🖥️", cost: 1500, level: 0, maxLevel: 3, effect: "+15% production speed per level" },
  { id: "coffee_bar", name: "Coffee Bar", description: "Espresso for everyone. Morale stays high.", icon: "☕", cost: 600, level: 0, maxLevel: 2, effect: "+8 morale recovery per level" },
  { id: "expansion", name: "Office Expansion", description: "More desks, more agents.", icon: "🏗️", cost: 2e3, level: 0, maxLevel: 3, effect: "+6 agent slots per level" },
  { id: "neon", name: "Neon Lighting Pack", description: "Instagrammable office. Boosts reputation.", icon: "🌈", cost: 800, level: 0, maxLevel: 1, effect: "+10 reputation" },
  { id: "meeting_pods", name: "Glass Meeting Pods", description: "Faster reviews, fewer rejections.", icon: "🫧", cost: 1200, level: 0, maxLevel: 2, effect: "+6 review quality per level" },
  { id: "training_lab", name: "Training Lab", description: "VR training stations.", icon: "🧪", cost: 1e3, level: 0, maxLevel: 2, effect: "−25% training cost and time per level" },
  { id: "studio", name: "Sound Studio", description: "Acoustic booth for the voice team.", icon: "🎧", cost: 900, level: 0, maxLevel: 2, effect: "+8 voice quality per level" }
], lm = [
  { metric: "start_video", title: (o) => `Start ${o} nieuwe video${o > 1 ? "'s" : ""}`, range: [1, 2], xp: 40, cash: 100 },
  { metric: "publish", title: () => "Publish 1 video", range: [1, 1], xp: 80, cash: 250 },
  { metric: "approve", title: (o) => `Approve ${o} deliverable${o > 1 ? "s" : ""} as CEO`, range: [1, 2], xp: 50, cash: 120 },
  { metric: "like", title: (o) => `Like ${o} Threads-berichten`, range: [2, 4], xp: 25, cash: 50 },
  { metric: "post", title: () => "Post an update on Threads", range: [1, 1], xp: 25, cash: 50 },
  { metric: "train", title: () => "Train an agent", range: [1, 1], xp: 50, cash: 80 },
  { metric: "complete_tasks", title: (o) => `Rond ${o} taken af`, range: [4, 8], xp: 60, cash: 150 }
];
function kd() {
  return [...lm].sort(() => Math.random() - 0.5).slice(0, 3).map((s) => {
    const a = s.range[0] + Math.floor(Math.random() * (s.range[1] - s.range[0] + 1));
    return { id: H("ms"), title: s.title(a), metric: s.metric, target: a, progress: 0, rewardXp: s.xp, rewardCash: s.cash, claimed: !1 };
  });
}
const wd = () => Me(["🔥", "🚀", "🎉", "💪", "✨", "📈"]), Yr = [
  { id: "research", label: "Research", department: "research", roles: ["researcher", "niche_analyst", "competitor_analyst"], effort: 60, deliverable: "report", deliverableName: "Research Brief", cost: 6 },
  { id: "topic", label: "Topic Selection", department: "research", roles: ["topic_finder", "niche_analyst", "researcher"], effort: 40, deliverable: "brief", deliverableName: "Topic Shortlist", cost: 4 },
  { id: "titles", label: "Titles & Hooks", department: "creative", roles: ["title_specialist", "hook_specialist", "idea_generator"], effort: 50, deliverable: "brief", deliverableName: "Title & Hook Pack", cost: 5 },
  { id: "script", label: "Scriptwriting", department: "script", roles: ["scriptwriter", "storytelling_expert"], effort: 110, deliverable: "script", deliverableName: "Full Script", cost: 18 },
  { id: "factcheck", label: "Fact Checking", department: "script", roles: ["fact_checker"], effort: 45, deliverable: "report", deliverableName: "Fact-Check Report", reviewer: "fact_checker", rejectTo: "script", cost: 5 },
  { id: "voice", label: "Voice-over", department: "voice", roles: ["voice_generator", "voice_director"], effort: 60, deliverable: "audio", deliverableName: "Voice-over Track (simulated)", cost: 22 },
  { id: "editing", label: "Video Editing", department: "production", roles: ["video_editor", "visual_researcher", "editing_supervisor"], effort: 140, deliverable: "video", deliverableName: "Edited Cut (simulated)", cost: 45 },
  { id: "thumbnail", label: "Thumbnail", department: "thumbnail", roles: ["thumbnail_designer", "ctr_specialist"], effort: 55, deliverable: "image", deliverableName: "Thumbnail Variants (simulated)", cost: 12 },
  { id: "qc", label: "Quality Control", department: "production", roles: ["quality_controller", "editing_supervisor"], effort: 40, deliverable: "report", deliverableName: "QC Checklist", reviewer: "quality_controller", rejectTo: "editing", cost: 4 },
  { id: "approval", label: "CEO Approval", department: "ceo", roles: ["ceo_agent"], effort: 20, deliverable: "analysis", deliverableName: "Approval Memo", manual: !0, cost: 0 },
  { id: "publishing", label: "Publishing", department: "publishing", roles: ["upload_manager", "seo_specialist", "social_media_manager"], effort: 35, deliverable: "metadata", deliverableName: "Upload Package", manual: !0, cost: 3 }
], ct = (o) => Yr.find((s) => s.id === o), am = (o) => Yr.findIndex((s) => s.id === o), sm = (o) => {
  var s;
  return ((s = Yr[am(o) + 1]) == null ? void 0 : s.id) ?? null;
};
function Ua(o, s, a, d) {
  const f = s.topic, u = (a == null ? void 0 : a.niche) ?? "general", p = Math.round(d);
  switch (o) {
    case "research":
      return [
        `RESEARCH BRIEF — ${f}`,
        `• Niche: ${u} · Est. search demand: ${we(12, 90)}k/mo`,
        `• Top competitor outliers: ${we(3, 9)} videos > 5× channel average`,
        `• Audience questions: "Why ${f.toLowerCase()}?", "Is it true that…", "What happens next?"`,
        "• Gap: few videos cover this with a narrative structure under 15 min",
        `• Confidence score: ${p}/100`
      ].join(`
`);
    case "topic":
      return [
        "TOPIC SHORTLIST",
        `1. ${f} ✅ selected`,
        `2. The hidden history behind ${f.split(" ").slice(-2).join(" ")}`,
        `3. ${Me(["5 myths", "7 facts", "The truth"])} about ${u}`,
        "Selection rationale: highest demand/competition ratio, evergreen potential."
      ].join(`
`);
    case "titles":
      return [
        "TITLE OPTIONS",
        `A) ${s.title}`,
        `B) Nobody Talks About ${f}`,
        `C) ${f} — The Full Story`,
        `HOOK (0:00–0:20): "In ${we(1990, 2024)}, something happened that changed ${u} forever — and almost nobody noticed."`,
        `Predicted CTR uplift vs. baseline: +${(p / 40).toFixed(1)}%`
      ].join(`
`);
    case "script":
      return [
        `SCRIPT v${s.rejections + 1} — ${s.title}`,
        "[HOOK] Open loop + stakes (0:00–0:30)",
        "[ACT 1] Context and the central question (0:30–3:00)",
        "[ACT 2] Three escalating revelations with b-roll cues (3:00–8:30)",
        "[ACT 3] Payoff, twist and takeaway (8:30–11:00)",
        "[CTA] Soft subscribe + next video tease",
        `Word count: ${we(1500, 2100)} · Est. runtime ${we(10, 14)} min`
      ].join(`
`);
    case "factcheck":
      return [
        "FACT-CHECK REPORT",
        `Claims checked: ${we(14, 30)} · Sources cited: ${we(6, 15)}`,
        p >= 55 ? "Result: PASS — no critical inaccuracies." : `Result: ISSUES — ${we(2, 5)} claims need stronger sources.`
      ].join(`
`);
    case "voice":
      return `VOICE-OVER (simulated)
Voice profile: ${Me(["Deep documentary", "Warm storyteller", "Calm narrator"])}
Duration: ${we(10, 14)}:${String(we(0, 59)).padStart(2, "0")} · Loudness −14 LUFS
No audio file generated — voice adapter not connected.`;
    case "editing":
      return `EDITED CUT (simulated)
Clips: ${we(120, 260)} · Cuts/min: ${we(8, 18)} · Music beds: ${we(2, 4)}
Render: 4K/30 · Retention-pacing score ${p}/100
No video file generated — video adapter not connected.`;
    case "thumbnail":
      return `THUMBNAIL VARIANTS (simulated)
A: Big face-less object + 3-word text
B: Contrast split before/after
C: Map + red arrow
Predicted CTR: ${(3 + p / 20).toFixed(1)}%`;
    case "qc":
      return [
        "QC CHECKLIST",
        "☑ Audio levels  ☑ Captions  ☑ Copyright check  ☑ Policy check",
        p >= 55 ? "Verdict: READY for CEO approval" : `Verdict: SEND BACK — pacing dips at ${we(3, 8)}:${String(we(0, 59)).padStart(2, "0")}`
      ].join(`
`);
    case "approval":
      return `APPROVAL MEMO
Overall quality: ${p}/100
Recommendation: ${p >= 65 ? "Approve and publish" : "Approve with caution"}`;
    case "publishing":
      return `UPLOAD PACKAGE
Title: ${s.title}
Tags: ${u.toLowerCase()}, ${f.toLowerCase().split(" ").slice(0, 3).join(", ")}
Chapters: 5 · End screen: yes
Destination: LOCAL SIMULATION (YouTube adapter not connected)`;
  }
}
const um = {
  anthropicKey: "",
  anthropicModel: "claude-sonnet-5-5",
  openaiKey: "",
  openaiModel: "gpt-4o-mini",
  llmProvider: "simulation",
  youtubeApiKey: "",
  threadsToken: "",
  elevenLabsKey: "",
  imageProvider: "",
  supabaseUrl: "",
  supabaseAnonKey: ""
}, ed = un(Br()), td = {
  hook_specialist: "Spannendste beeld binnen 5 s, eerste woord op frame 1. Geen uitleg in de eerste minuut. Thumbnail + titel = wat de eerste seconden tonen.",
  scriptwriter: 'Scripts in het Engels, regie in het Nederlands. Spreek de kijker aan met "you". Escalatie: leuk, indrukwekkend, gevaarlijk, schokkend. Elke 60-90 s een nieuw probleem, twist aan het eind, NIET verwijzen naar de volgende video.',
  fact_checker: 'Elke video heeft "this part is real"-momenten met echte wetenschap. Controleer die.',
  voice_generator: "ElevenLabs v4. Verteller zfc8CJQpe8Kqyl0vvCzo. Genereer op ÉÉN plek, nooit dubbel. Voice-over altijd centraal in de mix.",
  video_editor: "Blender, glans-look, 30 fps. Shots 3-4 s, max 6 s. -14 LUFS. Eindrender op niels' pc.",
  quality_controller: "Kwaliteitscheck: HUD strak, props niet in elkaar, niets zweeft, sets dicht, geen clipping, bestek goed vast, rennen met gebogen knieën.",
  thumbnail_designer: "Thumbnail toont het beeld uit de eerste seconden. Getal in de titel werkt (2x, 10x).",
  seo_specialist: "Korte tags met echt zoekvolume; lange titelzinnen scoren 0.",
  upload_manager: 'Shorts koppelen aan de lange video via "Gerelateerde video". Categorie Film & Animation.'
}, cm = [
  ["researcher", "Ava Quill"],
  ["topic_finder", "Kai Vector"],
  ["niche_analyst", "Iris Novak"],
  ["title_specialist", "Luna Prism"],
  ["hook_specialist", "Milo Hart"],
  ["scriptwriter", "Theo Lumen"],
  ["fact_checker", "Ines Berg"],
  ["voice_generator", "Ezra Echo"],
  ["video_editor", "Zara Pixel"],
  ["quality_controller", "Omar Rigor"],
  ["thumbnail_designer", "Nova Silva"],
  ["upload_manager", "Finn Atlas"],
  ["seo_specialist", "Yuki Kim"],
  ["ceo_agent", "Sterling Cortex"],
  ["performance_analyst", "Ravi Okafor"]
];
function nd() {
  const o = Br(), s = cm.map(
    ([A, $], Q) => yd(A, 0, { name: $, level: 1 + Q % 3, xp: we(0, 60), ...td[A] ? { instructions: `Driftmark-studio. ${td[A]}` } : {} })
  ), a = [
    { id: "ch_history", name: "Driftmark", logo: { emoji: "🌀", color: "#f97316" }, niche: "3D What If animations", audience: "13–34 global, curious about superpowers & science", subscribers: 13, views: 0, revenue: 0, rpm: 4.5, uploadSchedule: "1x / week", uploadsPerWeek: 1, monetized: !1, ctrBoost: 0, retentionBoost: 0, createdTick: 0, isDemo: !0 },
    { id: "ch_science", name: "Driftmark Shorts", logo: { emoji: "⚡", color: "#8b5cf6" }, niche: "3D What If shorts", audience: "Shorts feed, 13–24", subscribers: 0, views: 0, revenue: 0, rpm: 0.1, uploadSchedule: "7x / week", uploadsPerWeek: 7, monetized: !1, ctrBoost: 0, retentionBoost: 0, createdTick: 0, isDemo: !0 }
  ], d = [], f = [], u = [];
  [
    // dag 0 = 14 okt 2026
    ["ch_science", "Teaser-short SH1: 10x sneller per dag", 13],
    ["ch_science", "Teaser-short SH2: tijd stopt", 13],
    ["ch_history", "What IF You Got 2x STRONGER Every Day for 40 Days?", 14],
    ["ch_science", "Short uit video 1: Titan", 15],
    ["ch_science", "Short uit video 1: Sneeze", 16],
    ["ch_science", "Teaser-short SH4: word wat je aanraakt", 17]
  ].forEach(([A, $, Q]) => {
    d.push({ id: H("vid"), projectId: "demo", channelId: A, title: $, publishedTick: Q * Ft + 15, quality: we(55, 78), ctr: +Ge(3.6, 6.2).toFixed(1), avd: +Ge(34, 48).toFixed(1), views: 0, revenue: 0, likes: 0 });
  });
  for (let A = 0; A < ed; A++)
    a.forEach(($) => {
      let Q = 0;
      d.filter((z) => z.channelId === $.id && z.publishedTick / Ft <= A).forEach((z) => {
        const ie = A - Math.floor(z.publishedTick / Ft), ge = Math.round(z.quality * 28 * Math.exp(-ie / 9) * Ge(0.8, 1.2) + 40);
        z.views += ge, z.likes += Math.round(ge * 0.035), Q += ge;
      }), Q += we(20, 60);
      const b = Math.round(Q * Ge(6e-3, 0.011));
      $.subscribers += b, $.views += Q, f.push({ day: A, channelId: $.id, views: Q, subs: b, revenue: 0, ctr: +Ge(3.8, 5.8).toFixed(2), avd: +Ge(35, 47).toFixed(1) });
    }), u.push({ id: H("le"), day: A, channelId: null, category: "Salaries", amount: -Math.round(s.reduce(($, Q) => $ + Q.salary, 0) * 0.08), note: "Daily agent compute & salaries (demo)" }), A % 30 === 0 && (u.push({ id: H("le"), day: A, channelId: null, category: "AI Subscriptions", amount: -120, note: "LLM & voice plans (demo)" }), u.push({ id: H("le"), day: A, channelId: null, category: "Software", amount: -65, note: "Editing suite & stock library (demo)" }));
  d.forEach((A) => u.push({ id: H("le"), day: Math.floor(A.publishedTick / Ft), channelId: A.channelId, category: "Production", amount: -124, note: `Production: ${A.title} (demo)` })), u.push({ id: H("le"), day: 10, channelId: "ch_history", category: "Freelancers", amount: -180, note: "Freelance motion designer (demo)" });
  const m = [], h = [], E = (A, $, Q) => {
    const b = {
      id: H("pr"),
      title: $,
      topic: $,
      channelId: A,
      stage: Yr[Q].id,
      status: "Active",
      createdTick: o - 40,
      deadlineTick: o + Ft * 5,
      priority: "Medium",
      taskIds: [],
      stageQuality: {},
      rejections: 0,
      cost: 0,
      history: [{ tick: o - 40, text: "Project created (demo)" }]
    };
    for (let z = 0; z < Q; z++) {
      const ie = Yr[z], ge = we(58, 82);
      b.stageQuality[ie.id] = ge, b.cost += ie.cost;
      const fe = s.find((ae) => ie.roles.includes(ae.role)), q = {
        id: H("tk"),
        title: `${ie.label}: ${$}`,
        description: `Produce the ${ie.deliverableName}.`,
        agentId: (fe == null ? void 0 : fe.id) ?? null,
        projectId: b.id,
        stage: ie.id,
        kind: "pipeline",
        priority: "Medium",
        status: "Completed",
        progress: 100,
        createdTick: o - 40 + z * 4,
        deadlineTick: o,
        dependencies: [],
        comments: [],
        quality: ge,
        revision: 0,
        documents: [{ id: H("doc"), name: ie.deliverableName, kind: ie.deliverable, content: Ua(ie.id, b, a.find((ae) => ae.id === A), ge) }],
        result: `${ie.deliverableName} delivered.`
      };
      m.push(q), b.taskIds.push(q.id), fe == null || fe.taskHistory.push(q.id);
    }
    return h.push(b), b;
  };
  E("ch_history", "What IF There Were NO RULES?", 6), E("ch_science", "Shorts uit video 3 (No Rules)", 3), E("ch_history", "Video 4: kies uit de ideeënlijst", 1);
  const C = (A) => s.find(($) => $.role === A).id, M = [
    { id: H("po"), authorId: C("ceo_agent"), department: "ceo", kind: "update", content: "Goedemorgen team ☀️ Focus: video 3 (No Rules) afmaken. Spannendste beeld binnen 5 seconden, geen uitleg in de eerste minuut.", tick: o - 30, likes: [C("hook_specialist"), C("scriptwriter")], comments: [{ id: H("c"), authorId: C("hook_specialist"), text: "On it — new hook framework drops today.", tick: o - 28 }], isDemo: !0 },
    { id: H("po"), authorId: C("performance_analyst"), department: "ceo", kind: "report", content: "Rapport: 10,4K weergaven in 28 dagen, +16 abonnees. Shorts doen elk 1,1-1,5K, maar sturen weinig door naar de lange video.", tick: o - 20, likes: [C("ceo_agent")], comments: [], attachment: { title: "Retentie video 1", body: "Gem. kijkduur 6:40 (26,3%) · ~2/3 haakt af in de eerste 30-60 s · daarna vlak 25-35%" }, isDemo: !0 },
    { id: H("po"), authorId: C("video_editor"), department: "production", kind: "update", content: "Renderwachtrij op de pc: scène 1 en 3-9 van No Rules staan erin. Nu bezig met scène 10, de stroom valt uit 🔦", tick: o - 12, likes: [], comments: [], isDemo: !0 },
    { id: H("po"), authorId: C("researcher"), department: "research", kind: "question", content: 'Wie checkt de "this part is real"-momenten van No Rules? Er zijn er 8.', tick: o - 8, likes: [C("fact_checker")], comments: [{ id: H("c"), authorId: C("fact_checker"), text: "Doe ik, ze staan in bijlage D van het script.", tick: o - 7 }], isDemo: !0 },
    { id: H("po"), authorId: C("thumbnail_designer"), department: "thumbnail", kind: "celebration", content: "Video 2 is af en niels vindt hem echt top 🎉 7 shorts staan klaar voor upload.", tick: o - 4, likes: [C("ceo_agent"), C("upload_manager"), C("title_specialist")], comments: [], isDemo: !0 }
  ];
  return {
    version: 1,
    tick: o,
    company: { name: "Driftmark Studio", level: 2, xp: 120, balance: 6e3, reputation: 32, baseSlots: 18 },
    agents: s,
    tasks: m,
    projects: h,
    videos: d,
    channels: a,
    stats: f,
    ledger: u,
    posts: M,
    notifications: [{ id: H("n"), tick: o, text: "Welkom in Driftmark HQ! Het hoofdscherm toont de echte stand; het kantoor is een simulatie die met jouw kanaal speelt.", kind: "info", read: !1 }],
    achievements: im.map((A) => ({ ...A })),
    missions: kd(),
    missionDay: ed,
    upgrades: om.map((A) => ({ ...A })),
    warCases: [],
    modifiers: { speedBoost: 0, speedBoostUntil: 0 },
    settings: { ...um },
    demoMode: !0
  };
}
const dm = 0.08, nr = (o, s) => {
  var a;
  return ((a = o.upgrades.find((d) => d.id === s)) == null ? void 0 : a.level) ?? 0;
}, fm = (o) => o.company.baseSlots + nr(o, "expansion") * 6;
function Ie(o, s, a = "info", d) {
  o.notifications.unshift({ id: H("n"), tick: o.tick, text: s, kind: a, read: !1, link: d }), o.notifications.length > 80 && (o.notifications.length = 80);
}
function wt(o, s, a, d, f) {
  const u = o.agents.find((p) => p.id === s);
  o.posts.unshift({ id: H("po"), authorId: s, department: (u == null ? void 0 : u.department) ?? "hq", kind: a, content: d, tick: o.tick, likes: [], comments: [], attachment: f }), o.posts.length > 150 && (o.posts.length = 150);
}
function $t(o, s) {
  for (o.company.xp += s; o.company.xp >= Zc(o.company.level); )
    o.company.xp -= Zc(o.company.level), o.company.level += 1, Ie(o, `🏆 Bedrijf bereikt niveau ${o.company.level}!`, "achievement"), o.company.reputation = Qe(o.company.reputation + 3, 0, 100);
}
function po(o, s, a) {
  for (s.xp += a; s.xp >= za(s.level); )
    s.xp -= za(s.level), s.level += 1, s.salary += 4, Object.keys(s.skills).forEach((d) => s.skills[d] = Qe(s.skills[d] + 3, 0, 100)), Ie(o, `⬆️ ${s.name} bereikt niveau ${s.level}.`, "success", "agents");
}
function It(o, s, a = 1) {
  o.missions.forEach((d) => {
    d.metric === s && !d.claimed && (d.progress = Math.min(d.target, d.progress + a));
  });
}
function ut(o, s, a, d, f = null, u = un(o.tick)) {
  o.ledger.push({ id: H("le"), day: u, channelId: f, category: s, amount: Math.round(a * 100) / 100, note: d }), o.company.balance += a;
}
const pm = (o) => 1 + nr(o, "render_farm") * 0.15 + (o.modifiers.speedBoostUntil > o.tick ? o.modifiers.speedBoost : 0);
function mm(o, s, a) {
  const d = o.agents.filter(
    (f) => s.includes(f.role) && !f.currentTaskId && f.state !== "training" && (f.channelIds.length === 0 || !a || f.channelIds.includes(a)) && !o.warCases.some((u) => u.status === "Investigating" && u.agentIds.includes(f.id))
  );
  return d.length ? d.sort((f, u) => s.indexOf(f.role) - s.indexOf(u.role) || yo(u) - yo(f))[0] : null;
}
function rd(o, s, a) {
  s.agentId = a.id, s.status = "Assigned", a.currentTaskId = s.id, a.taskHistory.includes(s.id) || a.taskHistory.push(s.id);
}
function Xr(o, s, a, d) {
  const f = ct(a), u = o.tasks.filter((h) => h.projectId === s.id && h.stage === a), p = o.tasks.filter((h) => h.projectId === s.id && h.status === "Completed").slice(-1)[0], m = {
    id: H("tk"),
    title: `${f.label}: ${s.title}`,
    description: `Maak de ${f.deliverableName} voor "${s.title}".${d ? ` Feedback to address: ${d}` : ""}`,
    agentId: null,
    projectId: s.id,
    stage: a,
    kind: "pipeline",
    priority: s.priority,
    status: "Pending",
    progress: 0,
    createdTick: o.tick,
    deadlineTick: o.tick + Math.max(6, Math.round(f.effort / 6)),
    dependencies: p ? [p.id] : [],
    comments: d ? [{ id: H("c"), authorId: "system", text: `Teruggestuurd met feedback: ${d}`, tick: o.tick }] : [],
    documents: [],
    result: null,
    quality: null,
    revision: u.length
  };
  return o.tasks.push(m), s.taskIds.push(m.id), m;
}
function gm(o, s, a) {
  const d = sm(s.stage), f = ct(s.stage);
  if (s.cost += f.cost, ut(o, "Production", -f.cost, `${f.label} · ${s.title}`, s.channelId), s.history.push({ tick: o.tick, text: `${f.label} completed (quality ${a.quality})` }), $t(o, 6), !d) return;
  s.stage = d;
  const u = Xr(o, s, d), p = o.agents.find((h) => h.id === a.agentId), m = ct(d);
  if (a.comments.push({ id: H("c"), authorId: a.agentId ?? "system", text: `${f.deliverableName} ingeleverd. Door naar ${m.label}.`, tick: o.tick }), d === "approval") {
    s.status = "Awaiting Approval", u.status = "Review";
    const h = o.agents.find((E) => E.role === "ceo_agent");
    h && (u.agentId = h.id), u.documents.push({ id: H("doc"), name: "Approval Memo", kind: "analysis", content: Ua("approval", s, o.channels.find((E) => E.id === s.channelId), Kr(s)) }), Ie(o, `🧾 "${s.title}" wacht op jouw goedkeuring.`, "approval", "projects"), h && wt(o, h.id, "update", `"${s.title}" is door de kwaliteitscheck en ligt bij niels voor goedkeuring. Kwaliteit ${Kr(s)}/100.`);
  } else p && Math.random() < 0.35 && wt(o, p.id, "handoff", `${f.deliverableName} voor "${s.title}" net doorgegeven aan ${m.label} ${wd()}`);
}
const Kr = (o) => {
  const s = Object.values(o.stageQuality);
  return s.length ? Math.round(s.reduce((a, d) => a + d, 0) / s.length) : 0;
};
function Sd(o, s, a, d, f) {
  o.tasks.filter((p) => p.projectId === s.id && !["Completed", "Rejected"].includes(p.status)).forEach((p) => {
    p.status = "Rejected";
    const m = o.agents.find((h) => h.id === p.agentId);
    m && m.currentTaskId === p.id && (m.currentTaskId = null, m.state = "idle");
  });
  const u = [...o.tasks].reverse().find((p) => p.projectId === s.id && p.stage === a && p.status === "Completed");
  u && (u.status = "Rejected", u.comments.push({ id: H("c"), authorId: f ?? "player", text: `Rejected: ${d}`, tick: o.tick })), s.rejections += 1, s.stage = a, s.status = "Active", delete s.stageQuality[a], s.history.push({ tick: o.tick, text: `Terug naar ${ct(a).label}: ${d}` }), Xr(o, s, a, d), Ie(o, `↩️ "${s.title}" is teruggestuurd naar ${ct(a).label}.`, "warning", "projects");
}
function hm(o, s, a) {
  const d = ct(a.stage);
  if (!d.rejectTo) return !0;
  const f = s.stageQuality[d.rejectTo] ?? 60, u = nr(o, "meeting_pods") * 6, p = Qe((f + u - 30) / 50, 0.25, 0.97);
  if (Math.random() < p || s.rejections >= 3) return !0;
  const m = d.id === "factcheck" ? `${we(2, 5)} beweringen hebben betere bronnen nodig` : Me(["tempo zakt in deel 2", "geluidsniveau wisselt", "beeld past niet bij de voice-over"]);
  a.result = `Rejected — ${m}`, a.status = "Completed";
  const h = o.agents.find((E) => E.id === a.agentId);
  return h && wt(o, h.id, "alert", `"${s.title}" terug naar ${ct(d.rejectTo).label}: ${m}. Even strakker maken 🔁`), Sd(o, s, d.rejectTo, m, a.agentId), !1;
}
function id(o) {
  var f;
  const s = un(o.tick);
  o.tick += 1;
  const a = un(o.tick);
  o.projects.filter((u) => u.status === "Active").forEach((u) => {
    o.tasks.find((m) => m.projectId === u.id && m.stage === u.stage && !["Completed", "Rejected"].includes(m.status)) || Xr(o, u, u.stage);
  }), o.tasks.filter((u) => u.status === "Pending").forEach((u) => {
    if (!u.dependencies.some((p) => {
      const m = o.tasks.find((h) => h.id === p);
      return m && m.status !== "Completed" && m.status !== "Approved";
    })) {
      if (u.agentId) {
        const p = o.agents.find((m) => m.id === u.agentId);
        p && !p.currentTaskId && p.state !== "training" && rd(o, u, p);
        return;
      }
      if (u.stage) {
        const p = o.projects.find((h) => h.id === u.projectId), m = mm(o, ct(u.stage).roles, (p == null ? void 0 : p.channelId) ?? null);
        m && (rd(o, u, m), Math.random() < 0.2 && wt(o, m.id, "update", `"${u.title}" opgepakt. ${Me(["Daar gaan we!", "Eerst koffie ☕", "Leuke klus.", "Deadline genoteerd."])}`));
      }
    }
  });
  const d = pm(o);
  if (o.tasks.forEach((u) => {
    var m;
    if (u.status === "Assigned") {
      u.status = "In Progress";
      return;
    }
    const p = o.agents.find((h) => h.id === u.agentId);
    if (u.status === "In Progress" && p) {
      const h = u.stage ? ct(u.stage).effort : 50, E = { Low: 0.9, Medium: 1, High: 1.12, Critical: 1.25 }[u.priority];
      if (u.progress = Math.min(100, u.progress + yo(p) / h * 6 * d * E), p.state = "working", u.progress >= 100) {
        let C = yo(p) * Ge(0.85, 1.2) + u.revision * 6;
        u.stage === "voice" && (C += nr(o, "studio") * 8), u.quality = Math.round(Qe(C, 20, 99));
        const M = o.projects.find((A) => A.id === u.projectId);
        if (u.stage && M) {
          const A = ct(u.stage);
          u.documents.push({ id: H("doc"), name: `${A.deliverableName}${u.revision ? ` (rev ${u.revision + 1})` : ""}`, kind: A.deliverable, content: Ua(u.stage, M, o.channels.find(($) => $.id === M.channelId), u.quality) });
        } else
          u.documents.push({ id: H("doc"), name: "Deliverable", kind: "report", content: `${u.title}
Afgerond door ${p.name} (${Pn(p.role).title}).
Kwaliteit ${u.quality}/100.
(Simulatie)` });
        u.status = "Review", u.comments.push({ id: H("c"), authorId: p.id, text: "Deliverable submitted — requesting feedback.", tick: o.tick }), p.state = "meeting";
      }
    } else if (u.status === "Review" && u.stage !== "approval" && u.stage !== "publishing")
      p && (p.state = "meeting"), o.tick - u.createdTick > 0 && Math.random() < 0.55 && (u.status = "Approved", u.comments.push({ id: H("c"), authorId: "system", text: "Peer review approved.", tick: o.tick }));
    else if (u.status === "Approved" && u.kind !== "warroom") {
      u.status = "Completed", u.result = u.result ?? `${((m = u.documents.at(-1)) == null ? void 0 : m.name) ?? "Deliverable"} delivered (quality ${u.quality}).`, p && (p.currentTaskId = null, p.state = "idle", p.completed += 1, p.performance = Math.round(Qe(p.performance * 0.85 + (u.quality ?? 60) * 0.15, 0, 100)), p.morale = Qe(p.morale - 2, 0, 100), po(o, p, Math.round((u.stage ? ct(u.stage).effort : 50) / 3))), It(o, "complete_tasks");
      const h = o.projects.find((E) => E.id === u.projectId);
      h && u.stage && h.stage === u.stage && h.status === "Active" && (h.stageQuality[u.stage] = u.quality ?? 60, hm(o, h, u) && gm(o, h, u));
    }
  }), o.agents.forEach((u) => {
    if (u.state === "training" && u.trainingUntil && o.tick >= u.trainingUntil && (u.state = "idle", u.trainingUntil = void 0, Ie(o, `🎓 ${u.name} is klaar met de training.`, "success", "agents")), u.state !== "training" && !u.currentTaskId) {
      const p = o.warCases.some((m) => m.status === "Investigating" && m.agentIds.includes(u.id));
      u.state = p || u.state === "meeting" && Math.random() < 0.5 ? "meeting" : "idle", u.morale = Qe(u.morale + 0.4 + nr(o, "coffee_bar") * 0.3, 0, 100);
    }
  }), o.warCases.forEach((u) => {
    if (u.status === "Investigating" && o.tick >= u.readyTick) {
      u.status = "Ready", Ie(o, `🛡️ Analyse crisiskamer klaar: ${u.title}`, "approval", "warroom");
      const p = o.agents.find((m) => m.role === "ceo_agent");
      p && wt(o, p.id, "report", `De crisiskamer is klaar met "${u.title}". De aanbevelingen liggen bij niels.`, { title: u.title, body: u.analysis.join(`
`) });
    }
  }), Math.random() < 0.12) {
    const u = Me(o.agents);
    if (u) {
      const p = [
        "Herinnering: spannendste beeld binnen 5 seconden. De retentie van video 1 liegt niet 📊",
        `Sterk voorbeeldkanaal gevonden voor onze ${((f = Me(o.channels)) == null ? void 0 : f.niche) ?? "niche"}. Staat in de onderzoeksmap.`,
        `Productieve ochtend op de afdeling ${Pn(u.role).department} ${wd()}`,
        "Heeft iemand tijd voor feedback op mijn laatste oplevering?",
        `Persoonlijk record: ${we(3, 6)} taken af deze week.`
      ];
      wt(o, u.id, Me(["update", "update", "question"]), Me(p));
    }
  }
  if (Math.random() < 0.25 && o.posts.length) {
    const u = Me(o.posts.slice(0, 10)), p = Me(o.agents);
    p && !u.likes.includes(p.id) && u.authorId !== p.id && u.likes.push(p.id);
  }
  a !== s && vm(o, s), an(o);
}
function vm(o, s) {
  o.channels.reduce((d, f) => d + f.subscribers, 0), o.channels.forEach((d) => {
    let f = 0, u = 0, p = 0, m = 0;
    o.videos.filter((C) => C.channelId === d.id).forEach((C) => {
      const M = s - un(C.publishedTick);
      if (M < 0) return;
      const A = (C.quality * 40 + d.subscribers * 0.15 + o.company.reputation * 6) * (C.ctr / 5) * (C.avd / 42), $ = Math.round(A * Math.exp(-M / 10) * Ge(0.75, 1.25) + 15);
      C.views += $, C.likes += Math.round($ * 0.035);
      const Q = d.monetized ? $ / 1e3 * d.rpm : 0;
      C.revenue += Q, f += $, u += C.ctr, p += C.avd, m++;
    }), f += Math.round(d.subscribers * 0.02);
    const h = Math.round(f * Ge(6e-3, 0.012)), E = d.monetized ? f / 1e3 * d.rpm : 0;
    if (d.views += f, d.subscribers += h, d.revenue += E, o.stats.push({ day: s, channelId: d.id, views: f, subs: h, revenue: Math.round(E * 100) / 100, ctr: m ? +(u / m).toFixed(2) : 0, avd: m ? +(p / m).toFixed(1) : 0 }), E > 0 && ut(o, "Ad Revenue", E, `Advertentie-inkomsten · ${d.name}`, d.id, s), !d.monetized && d.subscribers >= 1e3) {
      d.monetized = !0, Ie(o, `💸 ${d.name} verdient nu geld! De advertentie-inkomsten komen binnen.`, "achievement", "channels");
      const C = o.agents.find((M) => M.role === "financial_manager" || M.role === "ceo_agent");
      C && wt(o, C.id, "celebration", `${d.name} heeft 1.000 abonnees en verdient nu geld 💸 Topwerk, team!`);
    }
  });
  const a = o.agents.reduce((d, f) => d + f.salary, 0) * dm;
  ut(o, "Salaries", -a, `Dagelijkse kosten agents (${o.agents.length} agents)`, null, s), s % 30 === 0 && (ut(o, "AI Subscriptions", -(80 + o.agents.length * 4), "Maandelijkse AI- en stemabonnementen"), ut(o, "Software", -65, "Software en bibliotheek")), o.missions = kd(), o.missionDay = s + 1, o.company.reputation = Qe(o.company.reputation + (o.videos.length ? 0.2 : -0.1), 0, 100), o.channels.forEach((d) => {
    d.ctrBoost *= 0.97, d.retentionBoost *= 0.97;
  }), s % 3 === 0 && ym(o);
}
function ym(o) {
  const s = un(o.tick), a = o.projects.filter((d) => d.status === "Active" && d.deadlineTick < o.tick).length;
  a >= 2 && !o.warCases.some((d) => d.type === "production_delays" && ["Investigating", "Ready"].includes(d.status)) && Ie(o, `⚠️ ${a} projecten zijn te laat. Roep misschien de crisiskamer bijeen.`, "warning", "warroom"), o.channels.forEach((d) => {
    const f = o.stats.filter((m) => m.channelId === d.id && m.day > s - 15);
    if (f.length < 14) return;
    const u = f.slice(-7).reduce((m, h) => m + h.views, 0), p = f.slice(-14, -7).reduce((m, h) => m + h.views, 0);
    p > 0 && u < p * 0.85 && Ie(o, `📉 ${d.name}: weergaven ${Math.round((1 - u / p) * 100)}% lager dan vorige week.`, "warning", "warroom");
  });
}
function an(o) {
  const s = o.channels.reduce((u, p) => u + p.views, 0), a = o.ledger.filter((u) => u.category === "Ad Revenue").reduce((u, p) => u + p.amount, 0), d = o.projects.filter((u) => u.status === "Published").length, f = {
    first_video: d >= 1,
    five_videos: d >= 5,
    views_100k: s >= 1e5,
    views_1m: s >= 1e6,
    monetized: o.channels.some((u) => u.monetized),
    rev_1000: a >= 1e3,
    team_10: o.agents.some((u) => u.hiredDay > 0),
    team_20: o.agents.length >= 20,
    first_upgrade: o.upgrades.some((u) => u.level > 0),
    war_room: o.warCases.some((u) => u.status === "Resolved"),
    level_5: o.company.level >= 5,
    two_channels: o.channels.some((u) => !u.isDemo),
    agent_lvl5: o.agents.some((u) => u.level >= 5)
  };
  o.achievements.forEach((u) => {
    !u.unlockedTick && f[u.id] && (u.unlockedTick = o.tick, $t(o, u.xp), Ie(o, `🏅 Prestatie behaald: ${u.title}`, "achievement", "achievements"));
  });
}
const od = {
  declining_views: { label: "Declining Views", icon: "📉", color: "#f43f5e" },
  low_ctr: { label: "Low CTR", icon: "🖱️", color: "#f59e0b" },
  poor_retention: { label: "Poor Retention", icon: "⏱️", color: "#a855f7" },
  production_delays: { label: "Production Delays", icon: "🐢", color: "#3b82f6" },
  falling_revenue: { label: "Falling Revenue", icon: "💶", color: "#ef4444" }
};
function km(o, s) {
  const a = (d, f, u, p, m) => ({ id: H("rec"), title: d, detail: f, cost: u, effect: p, magnitude: m });
  switch (o) {
    case "low_ctr":
      return {
        analysis: [
          `Prestatie-analist: de CTR van ${s} ligt de laatste 7 dagen onder de 4,5% van de niche.`,
          "CTR-specialist: thumbnails hebben te veel tekst; uitschieters gebruiken 1 blikvanger en max. 3 woorden.",
          "CEO-agent: vertoningen zijn goed, de verpakking is het probleem, niet het onderwerp."
        ],
        recs: [
          a("Thumbnails opnieuw ontwerpen", "CTR-specialist en thumbnailontwerper maken een nieuwe stijlgids.", 400, "ctr", 1.2),
          a("Titels A/B testen", "Elke upload krijgt 3 titelvarianten, na 48 uur wisselen.", 150, "ctr", 0.6)
        ]
      };
    case "poor_retention":
      return {
        analysis: [
          `Prestatie-analist: de kijkduur van ${s} zakt hard na de eerste 45 seconden.`,
          "Hook-specialist: intro’s geven te lang uitleg voor de spanning begint.",
          "Montagechef: het tempo zakt in deel 2, minder verrassingen dan de concurrentie."
        ],
        recs: [
          a("Hooks herschrijven", "Spanning binnen 5 seconden. Creatief team trainen.", 300, "retention", 6),
          a("Montage met meer verrassingen", "Shots max 6 s, elke 60-90 s een nieuw probleem.", 500, "retention", 9)
        ]
      };
    case "declining_views":
      return {
        analysis: [
          `Prestatie-analist: de weergaven van ${s} dalen ten opzichte van vorige week.`,
          "Niche-analist: de laatste uploads leken te veel op elkaar.",
          "Uploadmanager: we halen het uploadschema niet."
        ],
        recs: [
          a("Vaker uploaden", "+1 video per week; productie voorrang geven.", 250, "schedule", 1),
          a("Nieuwe onderwerpen zoeken", "Concurrentie-analist zoekt 10 nieuwe uitschieters.", 350, "ctr", 0.8)
        ]
      };
    case "production_delays":
      return {
        analysis: [
          "CEO-agent: meerdere projecten zijn over hun deadline.",
          "Montagechef: de montage is de flessenhals, taken wachten op een animator.",
          "Financieel manager: vertraging kost naar schatting 12% van de maandinkomsten."
        ],
        recs: [
          a("Tijdelijke freelance animator", "Freelancer versnelt de productie 14 dagen.", 600, "speed", 0.25),
          a("Week overwerk", "Iets minder moraal, sneller klaar.", 200, "speed", 0.12)
        ]
      };
    case "falling_revenue":
      return {
        analysis: [
          "Financieel manager: minder inkomsten dan vorige periode, terwijl de kosten stegen.",
          "Prestatie-analist: meer onderwerpen met een lage RPM.",
          "CEO-agent: kies onderwerpen met hogere RPM en video’s langer dan 8 minuten."
        ],
        recs: [
          a("Onderwerpen met hogere RPM", "Kies wetenschap- en techhoeken.", 300, "rpm", 0.8),
          a("Advertenties halverwege", "Video’s langer dan 8 min met natuurlijke pauzes.", 150, "rpm", 0.4)
        ]
      };
  }
}
const wm = {
  getItem: (o) => {
    try {
      return localStorage.getItem(o);
    } catch {
      return null;
    }
  },
  setItem: (o, s) => {
    try {
      localStorage.setItem(o, s);
    } catch {
    }
  },
  removeItem: (o) => {
    try {
      localStorage.removeItem(o);
    } catch {
    }
  }
}, _d = "driftmark-orders", Sm = () => {
  try {
    return JSON.parse(localStorage.getItem(_d) || "[]");
  } catch {
    return [];
  }
}, Ea = (o) => {
  try {
    localStorage.setItem(_d, JSON.stringify(o.slice(0, 100)));
  } catch {
  }
};
let sn = null;
const _m = (async () => {
  try {
    const o = window.claude;
    sn = o != null && o.use ? await o.use("comments") : null;
  } catch {
    sn = null;
  }
})();
async function ld(o) {
  if (!sn) return { ok: !1, reason: "Versturen kan alleen op de gepubliceerde pagina in claude.ai." };
  try {
    const s = await sn.canSendToClaude();
    if (s !== "available") return { ok: !1, reason: s === "no_session" ? "Claude luistert nu niet mee; de opdracht wacht." : s === "writers_only" ? "Alleen de eigenaar kan opdrachten sturen." : "Versturen staat hier uit." };
    const a = document.getElementById("orders-anchor") ?? document.getElementById("root"), d = await sn.anchorFor(a);
    return await sn.sendToClaude({ anchor: d, text: o.slice(0, 3800) }), { ok: !0 };
  } catch (s) {
    const a = (s == null ? void 0 : s.code) ?? "fout";
    return { ok: !1, reason: a === "rate_limited" ? "Te snel achter elkaar; probeer zo opnieuw." : `Niet verstuurd (${a}).` };
  }
}
const Va = La((o, s) => ({
  orders: Sm(),
  avail: "laden",
  refresh: async () => {
    if (await _m, !sn) {
      o({ avail: "geen" });
      return;
    }
    try {
      o({ avail: await sn.canSendToClaude() });
    } catch {
      o({ avail: "off" });
    }
  },
  send: async (a) => {
    const d = { id: Math.random().toString(36).slice(2), at: Date.now(), text: a, status: "wachtrij" }, f = [d, ...s().orders];
    o({ orders: f }), Ea(f);
    const u = await ld(`[DRIFTMARK HQ · ECHTE OPDRACHT]
${a}`), p = s().orders.map((m) => m.id === d.id ? { ...m, status: u.ok ? "verstuurd" : "wachtrij", reason: u.reason } : m);
    return o({ orders: p }), Ea(p), { ...d, status: u.ok ? "verstuurd" : "wachtrij", reason: u.reason };
  },
  resend: async (a) => {
    const d = s().orders.find((p) => p.id === a);
    if (!d) return;
    const f = await ld(`[DRIFTMARK HQ · ECHTE OPDRACHT]
${d.text}`), u = s().orders.map((p) => p.id === a ? { ...p, status: f.ok ? "verstuurd" : "wachtrij", reason: f.reason } : p);
    o({ orders: u }), Ea(u);
  }
}));
Va.getState().refresh();
setInterval(() => void Va.getState().refresh(), 3e4);
function Em(o, s) {
  Va.getState().send(o).then((a) => {
    s == null || s(a.status === "verstuurd" ? "✅ Echte opdracht naar Claude gestuurd" : `⏳ Opdracht in de wachtrij: ${a.reason ?? ""}`, a.status === "verstuurd" ? "success" : "warning");
  });
}
const Ca = {
  page: "driftmark",
  selectedDept: null,
  selectedAgentId: null,
  selectedProjectId: null,
  modal: null,
  modalPayload: null,
  confirm: null,
  paused: !1,
  speed: 1,
  toasts: [],
  notifOpen: !1
}, et = La()(
  Op(
    Yp((o, s) => ({
      ...nd(),
      ...Ca,
      // ── UI ───────────────────────────────────────────
      setPage: (a) => o((d) => {
        d.page = a, d.selectedDept = null;
      }),
      selectDept: (a) => o((d) => {
        d.selectedDept = a;
      }),
      selectAgent: (a) => o((d) => {
        d.selectedAgentId = a;
      }),
      selectProject: (a) => o((d) => {
        d.selectedProjectId = a;
      }),
      openModal: (a, d) => o((f) => {
        f.modal = a, f.modalPayload = d ?? null;
      }),
      closeModal: () => o((a) => {
        a.modal = null, a.modalPayload = null;
      }),
      askConfirm: (a) => o((d) => {
        d.confirm = a;
      }),
      closeConfirm: () => o((a) => {
        a.confirm = null;
      }),
      toast: (a, d = "info") => {
        const f = H("t");
        o((u) => {
          u.toasts.push({ id: f, text: a, kind: d });
        }), setTimeout(() => s().dismissToast(f), 3800);
      },
      dismissToast: (a) => o((d) => {
        d.toasts = d.toasts.filter((f) => f.id !== a);
      }),
      setNotifOpen: (a) => o((d) => {
        d.notifOpen = a;
      }),
      togglePause: () => o((a) => {
        a.paused = !a.paused;
      }),
      setSpeed: (a) => o((d) => {
        d.speed = a, d.paused = !1;
      }),
      // ── simulation ───────────────────────────────────
      advance: () => o((a) => {
        id(a);
      }),
      fastForward: (a) => o((d) => {
        for (let f = 0; f < a; f++) id(d);
      }),
      // ── projects & tasks ─────────────────────────────
      startVideo: ({ channelId: a, title: d, topic: f, priority: u, deadlineDays: p }) => {
        const m = H("pr");
        return o((h) => {
          const E = h;
          E.projects.unshift({
            id: m,
            title: d,
            topic: f,
            channelId: a,
            stage: "research",
            status: "Active",
            createdTick: E.tick,
            deadlineTick: E.tick + p * Ft,
            priority: u,
            taskIds: [],
            stageQuality: {},
            rejections: 0,
            cost: 0,
            history: [{ tick: E.tick, text: "Project gestart door niels" }]
          }), Xr(E, E.projects[0], "research"), It(E, "start_video"), $t(E, 10);
          const C = E.agents.find((M) => M.role === "ceo_agent");
          C && wt(E, C.id, "update", `Nieuwe video gestart: "${d}" 🎬 Onderzoek, aan jullie.`);
        }), s().toast(`"${d}" gestart. Onderzoek heeft de opdracht.`, "success"), m;
      },
      assignManualTask: (a) => {
        o((d) => {
          var m, h;
          const f = d;
          let u = a.agentId;
          !u && a.role && (u = ((m = f.agents.find((E) => E.role === a.role)) == null ? void 0 : m.id) ?? null);
          const p = {
            id: H("tk"),
            title: a.title,
            description: a.description,
            agentId: u,
            projectId: a.projectId,
            stage: null,
            kind: "manual",
            priority: a.priority,
            status: "Pending",
            progress: 0,
            createdTick: f.tick,
            deadlineTick: f.tick + a.deadlineDays * Ft,
            dependencies: a.dependencies,
            comments: [{ id: H("c"), authorId: "player", text: "Assigned by CEO.", tick: f.tick }],
            documents: [{ id: H("doc"), name: "Task Brief", kind: "brief", content: a.description || a.title }],
            result: null,
            quality: null,
            revision: 0
          };
          f.tasks.push(p), a.projectId && ((h = f.projects.find((E) => E.id === a.projectId)) == null || h.taskIds.push(p.id));
        }), s().toast("Taak gemaakt en klaargezet voor de agent.", "success");
      },
      setTaskPriority: (a, d) => o((f) => {
        const u = f.tasks.find((p) => p.id === a);
        u && (u.priority = d);
      }),
      commentTask: (a, d) => o((f) => {
        const u = f.tasks.find((m) => m.id === a);
        if (!u) return;
        u.comments.push({ id: H("c"), authorId: "player", text: d, tick: f.tick });
        const p = f.agents.find((m) => m.id === u.agentId);
        p && u.comments.push({ id: H("c"), authorId: p.id, text: `Thanks — noted. I'll factor that in. (${p.personality.split(" ")[0]} response)`, tick: f.tick });
      }),
      reviewTask: (a, d, f) => o((u) => {
        const p = u, m = p.tasks.find((h) => h.id === a);
        m && (d ? (m.status = "Approved", m.comments.push({ id: H("c"), authorId: "player", text: f || "Approved by CEO.", tick: p.tick }), It(p, "approve")) : (m.status = "In Progress", m.progress = 55, m.revision += 1, m.comments.push({ id: H("c"), authorId: "player", text: `Aanpassingen gevraagd: ${f || "Please improve quality."}`, tick: p.tick })));
      }),
      reassignTask: (a, d) => o((f) => {
        const u = f.tasks.find((m) => m.id === a);
        if (!u) return;
        const p = f.agents.find((m) => m.id === u.agentId);
        p && p.currentTaskId === u.id && (p.currentTaskId = null, p.state = "idle"), u.agentId = d, u.status = "Pending", u.comments.push({ id: H("c"), authorId: "player", text: "Reassigned by CEO.", tick: f.tick });
      }),
      // ── agents ───────────────────────────────────────
      hireAgent: (a, d) => {
        const f = s(), u = Pn(a);
        if (f.agents.length >= fm(f))
          return s().toast("Geen vrij bureau. Koop de upgrade Kantooruitbreiding.", "warning"), !1;
        if (f.company.balance < u.hireCost)
          return s().toast("Niet genoeg saldo om aan te nemen.", "warning"), !1;
        let p = "";
        return o((m) => {
          const h = m, E = yd(a, un(h.tick), { channelIds: d });
          p = E.name, h.agents.push(E), ut(h, "Hiring", -u.hireCost, `Hired ${E.name} (${u.title})`), It(h, "hire"), wt(h, E.id, "celebration", `Hoi allemaal 👋 Ik ben ${E.name}, de nieuwe ${u.title}. Zin in het team ${u.department}!`), Ie(h, `👋 ${E.name} is begonnen als ${u.title}.`, "success", "agents"), an(h);
        }), s().toast(`Hired ${p} as ${u.title}.`, "success"), !0;
      },
      fireAgent: (a) => o((d) => {
        const f = d.agents.find((u) => u.id === a);
        f && (d.tasks.filter((u) => u.agentId === a && !["Completed", "Rejected"].includes(u.status)).forEach((u) => {
          u.agentId = null, u.status = "Pending";
        }), d.agents = d.agents.filter((u) => u.id !== a), Ie(d, `${f.name} heeft het bedrijf verlaten.`, "info", "agents"), d.selectedAgentId === a && (d.selectedAgentId = null));
      }),
      trainAgent: (a, d) => {
        const f = s(), u = f.agents.find((h) => h.id === a);
        if (!u) return !1;
        const p = nr(f, "training_lab"), m = Math.round(120 * u.level * (1 - p * 0.25));
        return u.currentTaskId ? (s().toast(`${u.name} is bezig met een taak. Probeer het als hij vrij is.`, "warning"), !1) : u.state === "training" ? (s().toast(`${u.name} zit al in een training.`, "warning"), !1) : f.company.balance < m ? (s().toast("Niet genoeg saldo voor de training.", "warning"), !1) : (o((h) => {
          const E = h, C = E.agents.find((M) => M.id === a);
          C.state = "training", C.trainingUntil = E.tick + Math.round(10 * (1 - p * 0.25)), C.skills[d] = Qe((C.skills[d] ?? 40) + 8, 0, 100), po(E, C, 40), C.morale = Qe(C.morale + 6, 0, 100), ut(E, "Training", -m, `Training ${C.name}: ${d}`), It(E, "train");
        }), s().toast(`${u.name} started ${d} training (−€${m}).`, "success"), !0);
      },
      promoteAgent: (a) => {
        const d = s(), f = d.agents.find((p) => p.id === a);
        if (!f) return !1;
        const u = 250 * f.level;
        return d.company.balance < u ? (s().toast("Niet genoeg saldo voor deze upgrade.", "warning"), !1) : (o((p) => {
          const m = p, h = m.agents.find((E) => E.id === a);
          ut(m, "Training", -u, `${h.name} naar niveau ${h.level + 1}`), po(m, h, za(h.level) - h.xp), an(m);
        }), !0);
      },
      // Max upgraden in één keer (niels 2026-11-05): niveau 10, alle vaardigheden 100
      maxUpgradeAgent: (a) => {
        const d = s(), f = d.agents.find((p) => p.id === a);
        if (!f) return !1;
        if (f.level >= er && Object.values(f.skills).every((p) => p >= 100))
          return s().toast(`${f.name} is al maximaal.`, "info"), !1;
        const u = Tm(f);
        return d.company.balance < u ? (s().toast("Niet genoeg saldo om maximaal te upgraden.", "warning"), !1) : (o((p) => {
          const m = p, h = m.agents.find((E) => E.id === a);
          ut(m, "Training", -u, `${h.name} maximaal geüpgraded (niveau ${er})`), h.salary += 4 * Math.max(0, er - h.level), h.level = Math.max(h.level, er), h.xp = 0, Object.keys(h.skills).forEach((E) => h.skills[E] = 100), h.morale = 100, h.performance = 100, Ie(m, `🚀 ${h.name} is maximaal geüpgraded.`, "success", "agents"), an(m);
        }), !0);
      },
      maxUpgradeAll: () => {
        let a = 0;
        for (const d of s().agents)
          d.level >= er && Object.values(d.skills).every((f) => f >= 100) || s().maxUpgradeAgent(d.id) && a++;
        return s().toast(a ? `${a} agents maximaal geüpgraded.` : "Iedereen is al maximaal.", a ? "success" : "info"), a;
      },
      updateAgent: (a, d) => o((f) => {
        const u = f.agents.find((p) => p.id === a);
        u && Object.assign(u, d);
      }),
      // ── approvals & publishing ───────────────────────
      approveProject: (a) => o((d) => {
        var h;
        const f = d, u = f.projects.find((E) => E.id === a);
        if (!u || u.status !== "Awaiting Approval") return;
        const p = f.tasks.find((E) => E.projectId === a && E.stage === "approval" && E.status === "Review");
        p && (p.status = "Completed", p.quality = Kr(u), p.result = "Goedgekeurd door niels."), u.stageQuality.approval = Kr(u), u.stage = "publishing", u.status = "Awaiting Publish", u.history.push({ tick: f.tick, text: "Goedgekeurd door niels" });
        const m = Xr(f, u, "publishing");
        m.status = "Review", m.agentId = ((h = f.agents.find((E) => E.role === "upload_manager")) == null ? void 0 : h.id) ?? null, m.documents.push({ id: H("doc"), name: "Upload Package", kind: "metadata", content: `UPLOADPAKKET
Titel: ${u.title}
Wacht op bevestiging van niels.` }), It(f, "approve"), $t(f, 15), Ie(f, `✅ "${u.title}" goedgekeurd, klaar om te publiceren (jij bevestigt).`, "approval", "projects");
      }),
      rejectProject: (a, d, f) => o((u) => {
        const p = u, m = p.projects.find((h) => h.id === a);
        m && Sd(p, m, d, f, null);
      }),
      publishProject: (a) => {
        o((d) => {
          const f = d, u = f.projects.find(($) => $.id === a);
          if (!u || u.status !== "Awaiting Publish") return;
          const p = f.channels.find(($) => $.id === u.channelId), m = Kr(u), h = u.stageQuality.thumbnail ?? 60, E = u.stageQuality.titles ?? 60, C = {
            id: H("vid"),
            projectId: u.id,
            channelId: u.channelId,
            title: u.title,
            publishedTick: f.tick,
            quality: m,
            ctr: +Qe(2.2 + h / 25 + E / 60 + p.ctrBoost + Ge(-0.5, 0.5), 1, 14).toFixed(1),
            avd: +Qe(26 + m / 4.5 + p.retentionBoost + Ge(-3, 3), 15, 75).toFixed(1),
            views: 0,
            revenue: 0,
            likes: 0
          };
          f.videos.push(C), f.tasks.filter(($) => $.projectId === a && $.stage === "publishing").forEach(($) => {
            $.status = "Completed", $.result = "Gepubliceerd.", $.quality = m;
          }), u.status = "Published", u.publishedTick = f.tick, u.videoId = C.id, u.history.push({ tick: f.tick, text: "Gepubliceerd (uploaden doet niels in Studio)" });
          const M = Math.round((m * 8 + p.subscribers * 0.05) * (C.ctr / 5));
          C.views += M, p.views += M, It(f, "publish"), $t(f, 60), f.company.reputation = Qe(f.company.reputation + 1.5, 0, 100);
          const A = f.agents.find(($) => $.role === "social_media_manager" || $.role === "upload_manager");
          A && wt(f, A.id, "celebration", `🚀 "${u.title}" is LIVE on ${p.name} (simulated). Predicted CTR ${C.ctr}% · AVD ${C.avd}%`), f.agents.filter(($) => f.tasks.some((Q) => Q.projectId === a && Q.agentId === $.id)).forEach(($) => po(f, $, 15)), Ie(f, `🚀 "${u.title}" gepubliceerd.`, "success", "analytics"), an(f);
        }), s().toast("Video gepubliceerd. Claude maakt het uploadpakket klaar.", "success");
      },
      cancelProject: (a) => o((d) => {
        const f = d.projects.find((u) => u.id === a);
        f && (f.status = "Cancelled", d.tasks.filter((u) => u.projectId === a && !["Completed", "Rejected"].includes(u.status)).forEach((u) => {
          u.status = "Rejected";
          const p = d.agents.find((m) => m.id === u.agentId);
          p && p.currentTaskId === u.id && (p.currentTaskId = null, p.state = "idle");
        }));
      }),
      // ── threads ──────────────────────────────────────
      likePost: (a) => o((d) => {
        const f = d.posts.find((u) => u.id === a);
        f && (f.likes.includes("player") ? f.likes = f.likes.filter((u) => u !== "player") : (f.likes.push("player"), It(d, "like")));
      }),
      commentPost: (a, d) => o((f) => {
        const u = f.posts.find((m) => m.id === a);
        if (!u) return;
        u.comments.push({ id: H("c"), authorId: "player", text: d, tick: f.tick });
        const p = f.agents.find((m) => m.id === u.authorId);
        p && u.comments.push({ id: H("c"), authorId: p.id, text: "Thanks boss! 🙌", tick: f.tick });
      }),
      createPost: (a, d) => o((f) => {
        const u = f;
        u.posts.unshift({ id: H("po"), authorId: "player", department: "hq", kind: d ? "report" : "update", content: a, tick: u.tick, likes: [], comments: [], attachment: d }), It(u, "post"), u.agents.slice().sort(() => Math.random() - 0.5).slice(0, 3).forEach((p) => u.posts[0].likes.push(p.id));
      }),
      sharePost: (a) => o((d) => {
        var m;
        const f = d, u = f.posts.find((h) => h.id === a);
        if (!u) return;
        const p = ((m = f.agents.find((h) => h.id === u.authorId)) == null ? void 0 : m.name) ?? "CEO";
        f.posts.unshift({ id: H("po"), authorId: "player", department: "hq", kind: "report", content: `Sharing ${p}'s post with the whole company 👇`, tick: f.tick, likes: [], comments: [], attachment: { title: `${p} wrote`, body: u.content } }), It(f, "post");
      }),
      markAllRead: () => o((a) => {
        a.notifications.forEach((d) => d.read = !0);
      }),
      // ── game mechanics ───────────────────────────────
      buyUpgrade: (a) => {
        const d = s(), f = d.upgrades.find((p) => p.id === a);
        if (!f || f.level >= f.maxLevel) return !1;
        const u = Math.round(f.cost * (1 + f.level * 0.6));
        return d.company.balance < u ? (s().toast("Niet genoeg saldo voor deze upgrade.", "warning"), !1) : (o((p) => {
          const m = p, h = m.upgrades.find((E) => E.id === a);
          h.level += 1, ut(m, "Upgrades", -u, `Kantoor-upgrade: ${h.name} N${h.level}`), a === "neon" && (m.company.reputation = Qe(m.company.reputation + 10, 0, 100)), $t(m, 40), Ie(m, `🛠️ ${h.name} naar niveau ${h.level}.`, "success", "upgrades"), an(m);
        }), s().toast(`${f.name} installed!`, "success"), !0);
      },
      claimMission: (a) => o((d) => {
        const f = d, u = f.missions.find((p) => p.id === a);
        !u || u.claimed || u.progress < u.target || (u.claimed = !0, $t(f, u.rewardXp), ut(f, "Rewards", u.rewardCash, `Missiebeloning: ${u.title}`));
      }),
      // ── channels ─────────────────────────────────────
      addChannel: (a) => o((d) => {
        const f = d;
        f.channels.push({ ...a, id: H("ch"), subscribers: 0, views: 0, revenue: 0, monetized: !1, ctrBoost: 0, retentionBoost: 0, createdTick: f.tick, isDemo: !1 }), $t(f, 30), Ie(f, `📺 Nieuw kanaal gestart: ${a.name}`, "success", "channels"), an(f);
      }),
      updateChannel: (a, d) => o((f) => {
        const u = f.channels.find((p) => p.id === a);
        u && Object.assign(u, d);
      }),
      assignDeptToChannel: (a, d) => o((f) => {
        f.agents.filter((u) => u.department === a).forEach((u) => {
          u.channelIds = d ? [d] : [];
        });
      }),
      // ── war room ─────────────────────────────────────
      openWarCase: (a, d) => o((f) => {
        const u = f, p = u.channels.find((C) => C.id === d), { analysis: m, recs: h } = km(a, (p == null ? void 0 : p.name) ?? "alle kanalen"), E = u.agents.filter((C) => ["ceo_agent", "performance_analyst", "financial_manager", "ctr_specialist", "editing_supervisor"].includes(C.role)).slice(0, 4);
        u.warCases.unshift({
          id: H("war"),
          type: a,
          channelId: d,
          title: `${od[a].label}${p ? ` · ${p.name}` : ""}`,
          evidence: Cm(u, a, d),
          status: "Investigating",
          openedTick: u.tick,
          readyTick: u.tick + 6,
          agentIds: E.map((C) => C.id),
          analysis: m,
          recommendations: h
        }), E.forEach((C) => {
          C.currentTaskId || (C.state = "meeting");
        }), Ie(u, `🛡️ Crisiskamer bijeengeroepen: ${od[a].label}`, "info", "warroom");
      }),
      approveRecommendation: (a, d) => {
        const f = s(), u = f.warCases.find((m) => m.id === a), p = u == null ? void 0 : u.recommendations.find((m) => m.id === d);
        if (!(!u || !p)) {
          if (f.company.balance < p.cost) {
            s().toast("Niet genoeg saldo voor dit plan.", "warning");
            return;
          }
          o((m) => {
            const h = m, E = h.warCases.find((A) => A.id === a);
            E.status = "Resolved", E.chosen = d;
            const C = E.channelId ? h.channels.filter((A) => A.id === E.channelId) : h.channels;
            p.effect === "ctr" && C.forEach((A) => A.ctrBoost += p.magnitude), p.effect === "retention" && C.forEach((A) => A.retentionBoost += p.magnitude), p.effect === "rpm" && C.forEach((A) => A.rpm = +(A.rpm + p.magnitude).toFixed(2)), p.effect === "schedule" && C.forEach((A) => {
              A.uploadsPerWeek += 1, A.uploadSchedule = `${A.uploadsPerWeek}x / week`;
            }), p.effect === "speed" && (h.modifiers.speedBoost = p.magnitude, h.modifiers.speedBoostUntil = h.tick + 14 * Ft), ut(h, p.effect === "speed" ? "Freelancers" : "Production", -p.cost, `Plan crisiskamer: ${p.title}`, E.channelId), $t(h, 50);
            const M = h.agents.find((A) => A.role === "ceo_agent");
            M && wt(h, M.id, "update", `niels keurde het plan "${p.title}" goed. We voeren het nu uit.`), an(h);
          }), s().toast(`Plan goedgekeurd: ${p.title}`, "success");
        }
      },
      dismissCase: (a) => o((d) => {
        const f = d.warCases.find((u) => u.id === a);
        f && (f.status = "Dismissed");
      }),
      // ── settings ─────────────────────────────────────
      updateSettings: (a) => o((d) => {
        Object.assign(d.settings, a);
      }),
      resetGame: () => o(() => ({ ...nd(), ...Ca })),
      importSave: (a) => o(() => ({ ...a, ...Ca }))
    })),
    {
      name: "driftmark-hq",
      version: 1,
      storage: dd(() => wm),
      partialize: (o) => {
        const { page: s, selectedDept: a, selectedAgentId: d, selectedProjectId: f, modal: u, modalPayload: p, confirm: m, toasts: h, notifOpen: E, paused: C, ...M } = o;
        return Object.fromEntries(Object.entries(M).filter(([, A]) => typeof A != "function"));
      }
    }
  )
);
function Cm(o, s, a) {
  const d = un(o.tick), f = o.stats.filter((h) => (!a || h.channelId === a) && h.day > d - 8), u = f.reduce((h, E) => h + E.views, 0), p = f.length ? f.reduce((h, E) => h + E.ctr, 0) / f.length : 0, m = f.length ? f.reduce((h, E) => h + E.avd, 0) / f.length : 0;
  switch (s) {
    case "declining_views":
      return `Laatste 7 dagen: ${u.toLocaleString("nl-NL")} weergaven.`;
    case "low_ctr":
      return `Gem. CTR laatste 7 dagen: ${p.toFixed(2)}%.`;
    case "poor_retention":
      return `Gem. kijkduur laatste 7 dagen: ${m.toFixed(1)}%.`;
    case "production_delays":
      return `${o.projects.filter((h) => h.status === "Active" && h.deadlineTick < o.tick).length} projecten te laat · ${o.tasks.filter((h) => h.status === "Pending").length} taken wachten op een agent.`;
    case "falling_revenue":
      return `Inkomsten laatste 7 dagen: €${f.reduce((h, E) => h + E.revenue, 0).toFixed(2)}.`;
  }
}
const er = 10, Tm = (o) => {
  let s = 0;
  for (let a = o.level; a < er; a++) s += 250 * a;
  return Math.max(s, 500);
};
{
  const o = et.getState(), s = (m, h) => et.getState().toast(m, h), a = (m) => et.getState().projects.find((h) => h.id === m), d = (m) => et.getState().tasks.find((h) => h.id === m), f = (m) => et.getState().agents.find((h) => h.id === m), u = (m) => {
    var h;
    return ((h = et.getState().channels.find((E) => E.id === m)) == null ? void 0 : h.name) ?? m;
  }, p = (m, h) => {
    const E = o[m];
    et.setState({ [m]: (...C) => {
      const M = h(...C), A = E(...C);
      return M && Em(M, s), A;
    } });
  };
  p("startVideo", (m) => `Start een nieuwe video voor ${u(m.channelId)}.
Titel: ${m.title}
Onderwerp: ${m.topic}
Prioriteit: ${m.priority} · deadline over ${m.deadlineDays} dagen.
Begin met het verloop (zoals bij video 3) volgens het productiehandboek.`), p("assignManualTask", (m) => `Nieuwe taak: ${m.title}
${m.description}
Rol: ${m.role ? Pn(m.role).title : f(m.agentId) ? Pn(f(m.agentId).role).title : "vrij"} · prioriteit ${m.priority} · deadline ${m.deadlineDays} dagen${a(m.projectId) ? ` · project: ${a(m.projectId).title}` : ""}.`), p("commentTask", (m, h) => {
    var E;
    return `Opmerking bij taak "${((E = d(m)) == null ? void 0 : E.title) ?? m}": ${h}`;
  }), p("reviewTask", (m, h, E) => {
    var C;
    return `${h ? "Goedgekeurd" : "Afgekeurd"}: taak "${((C = d(m)) == null ? void 0 : C.title) ?? m}"${E ? `. Opmerking: ${E}` : ""}.`;
  }), p("setTaskPriority", (m, h) => {
    var E;
    return `Prioriteit van taak "${((E = d(m)) == null ? void 0 : E.title) ?? m}" naar ${h}.`;
  }), p("approveProject", (m) => {
    var h;
    return `Goedkeuring niels: "${(h = a(m)) == null ? void 0 : h.title}" is goed, ga door naar de volgende stap (klaarmaken voor upload).`;
  }), p("rejectProject", (m, h, E) => {
    var C;
    return `Afgekeurd: "${(C = a(m)) == null ? void 0 : C.title}" moet terug naar ${ct(h).label}. Reden: ${E}`;
  }), p("publishProject", (m) => {
    var h;
    return `Publiceren: "${(h = a(m)) == null ? void 0 : h.title}". Maak titel, beschrijving, tags en thumbnail klaar. (Uploaden naar YouTube doet niels zelf in Studio.)`;
  }), p("cancelProject", (m) => {
    var h;
    return `Stop project: "${(h = a(m)) == null ? void 0 : h.title}". Niet verder aan werken.`;
  }), p("updateAgent", (m, h) => h.instructions ? `Nieuwe werkregel voor ${Pn(f(m).role).title}: ${h.instructions}
Voeg dit toe aan de werkwijze en het projectgeheugen.` : null), p("createPost", (m) => `Bericht van niels aan het team: ${m}`), p("commentPost", (m, h) => `Reactie van niels: ${h}`), p("updateChannel", (m, h) => `Kanaal ${u(m)} aanpassen: ${Object.entries(h).map(([E, C]) => `${E} = ${C}`).join(", ")}.`), p("approveRecommendation", (m, h) => {
    const E = et.getState().warCases.find((M) => M.id === m), C = E == null ? void 0 : E.recommendations.find((M) => M.id === h);
    return C ? `War Room: voer deze aanbeveling echt uit voor Driftmark: ${C.title}. ${C.detail}` : null;
  });
}
const Pm = "donderdag 5 november 2026, 00:15", jm = {
  name: "Driftmark",
  handle: "@driftmark3d",
  url: "https://youtube.com/@driftmark3d",
  slogan: "A NEW 3D WHAT IF EVERY WEEK",
  format: "Eén lange 3D What If-video per week (15-18 min) + teaser-shorts (30-45 s)",
  stats: [
    { label: "Abonnees", value: "25", note: "via vidIQ, 5 nov 01:00" },
    { label: "Weergaven totaal", value: "13.566", note: "16 openbare video’s" },
    { label: "Views per short", value: "1,2-1,8K", note: "beste: teleport-short 1.811" },
    { label: "Lange video’s", value: "52 / 19", note: "video 1 / video 2" }
  ],
  insight: "Shorts trekken kijkers, maar sturen nog weinig door naar de lange video. In de eerste 30-60 s van video 1 haakt ~2/3 af; daarna blijft 25-35% tot het eind."
}, Ta = (o, s, a = -1) => o.map((d, f) => ({ label: d, done: f < s, active: f === a })), Pa = ["Idee", "Verloop", "Script", "Stemmen", "Cast", "Sets", "Animatie", "Render", "Montage", "Upload-tekst", "Shorts", "Online"], Im = [
  {
    nr: 1,
    title: "What IF You Got 2x STRONGER Every Day for 40 Days?",
    werktitel: "Elke dag 2x sterker",
    status: "Online",
    lengte: "25:24",
    youtube: "https://youtu.be/9xSou5t37nk",
    kern: "Dag 1-5 grappig, dag 10 1000x (geen hand meer schudden), dag 20 een miljoen keer (kraters, nies als schokgolf).",
    twist: "Rond dag 40 sterker dan de zwaartekracht: je springt en komt nooit meer terug.",
    folder: "videos/2x-sterker/",
    script: "videos/2x-sterker/script_2x_stronger.md",
    repoBranch: "claude/project-thread-fd4epr",
    threads: [
      { title: "Script: elke dag 2x sterker", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WG9VGTvMrkr1r8Ub1qVc4sF3" },
      { title: "Animeer video 1", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGHoJN16bfuxJYzWRDbGoAtV" },
      { title: "Analyseer video 1", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGC9FZ2NQY5sy1pnC2J5cgdC" },
      { title: "Maak 7 shorts uit video 1", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGWQCGZvuCwwBd3cBDe1CZev" }
    ],
    steps: Ta(Pa, 12),
    notes: ["Bestand: WHAT IF\\WHAT_IF_2x_STRONGER.mp4", "Cold open ingekort naar ~23 s", 'Titel mist nog het slot-haakje "(Day 1 to Day 40"', "22 sets, 13 cast-figuren"]
  },
  {
    nr: 2,
    title: "What IF You Got 10x FASTER Every Day?",
    werktitel: "Elke dag 10x sneller",
    status: "Online",
    lengte: "12:56",
    youtube: "https://youtu.be/XZip23B4Q2M",
    kern: "Elke keer dat hij wakker wordt is hij 10x sneller. Al zijn dagen passen vóór dinsdag 09:00:00, als zijn broertje de kaarsjes uitblaast.",
    twist: 'Wakker blijven is de enige weg ernaartoe. "So… can you stay awake?"',
    folder: "videos/10x-sneller/",
    script: "videos/10x-sneller/script_10x_faster.md",
    repoBranch: "claude/project-thread-fdaxoy",
    threads: [
      { title: "Script: elke dag 10x sneller", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGTcYDSw9V7u6i1kCtSxA2kj" },
      { title: "Animeer video 2", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WG5C7m5zPrEbj5TGD66gKUQY" },
      { title: "Titel, beschrijving en tags video 2", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGFt2jvrzboJ4GbK8fbcasKv" },
      { title: "Maak 7 shorts uit video 2", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGMQM7kDpE2gpgLgMAovYDUq" },
      { title: "Analyseer video 2", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGRmJDkcSLjBnCebSWiTjgHW" }
    ],
    steps: Ta(Pa, 12),
    notes: ["Render klaar (1 nov); niels vindt hem top", "Upload-tekst: videos/10x-sneller/youtube_upload.md", "Blijft ongewijzigd; lessen gelden vanaf video 3", "7 shorts V2S1-V2S7 klaar (uploadvolgorde 1,2,7,3,6,5,4)"]
  },
  {
    nr: 3,
    title: "What IF There Were NO RULES?",
    werktitel: "Geen regels meer",
    status: "In productie",
    lengte: "~16:30",
    kern: 'Vredige dag, om 00:00 nucleair alarm op alle schermen: "er zijn geen regels meer". Dag 1, 2, 3… tot jaar 10. Teller "DAY X · RULES: N".',
    twist: 'Jaar 10, middernacht: "TEST COMPLETE … PHASE 2" (twist A).',
    folder: "videos/geen-regels/",
    script: "videos/geen-regels/script_no_rules.md",
    repoBranch: "claude/project-thread-maefml",
    threads: [
      { title: "Verloop video: wat als er geen regels zijn", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WG8Td6Q42bhkx3TbQHgnSwbh" },
      { title: "Bouw cast en sets voor geen-regels-video", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGCHT43zJaABsdPF4uv4swV5" },
      { title: "Animeer video 3: geen regels meer", id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGTfi8z2mFAQH5Qa5zaASKk1" }
    ],
    steps: Ta(Pa, 6, 6),
    notes: ["Scène 1 en 3-9 gebouwd en in de renderwachtrij op de pc", "Nu bezig: scène 10 (dag 4, de stroom valt uit)", "Nog te doen: scènes 11-22, teaser, flash-forwards, montage", "Stemmen in ElevenLabs v4; wetenschapper is een man (Wyatt)"]
  }
], xm = [
  { title: "Teaser-shorts (eigen ideeën)", status: "7 klaar", where: "WHAT IF\\shorts\\", items: ["SH1 10x sneller per dag", "SH2 Tijd stopt", "SH3 1 jaar vooruit kijken", "SH4 Word wat je aanraakt", "SH5 10x kleiner per uur", "SH7 Teleport-kopieën", "SH8 1.000.000x zwaarder"] },
  { title: "Shorts uit video 1", status: "7 klaar", where: "/mnt/project-files/v1_0*.mp4", items: ["Titan", "Sneeze", "Mug", "No off switch", "Catch", "Lab", "Space"] },
  { title: "Shorts uit video 2", status: "7 klaar", where: "WHAT IF\\shorts\\video2\\", items: ["V2S1 De vuilniswagen", "V2S2 De sonische knal", "V2S3 De zwevende regen", "V2S4", "V2S5", "V2S6", "V2S7"] },
  { title: "Shorts uit video 3", status: "Nog niet gestart", where: "-", items: ["Na de montage van video 3"] }
], Am = [
  { title: "Productiehandboek (idee → upload)", url: "https://claude.ai/artifact/L8mdYWg5dxBJMPSyqgj8j3" },
  { title: "Afvinklijst volgende video", url: "https://claude.ai/artifact/C3d9ZTfm2oUG3Cn3g3ebgM" },
  { title: "Analyse video 2", url: "https://claude.ai/artifact/EaRkosZvmiP1S64J1n34QQ" },
  { title: "Verloop video 3", url: "https://claude.ai/artifact/JGxd7EcrYfWDmDdbZVpWdo" },
  { title: "Kijkers van shorts naar lange video", url: "https://claude.ai/artifact/FjDq5ekayWynRHW6NLvJ8R" },
  { title: "YouTube-kanaal Driftmark", url: "https://youtube.com/@driftmark3d" },
  { title: "Repo nielz023/WhatIF", url: "https://github.com/nielz023/WhatIF" },
  { title: "Stijlvoorbeeld IFOLOGY", url: "https://youtube.com/@IFOLOGYFILMS" }
], Rm = [
  { title: "Teleporteren (ben jij het nog?)", groep: "Superkracht" },
  { title: "Vliegen tot 30 km hoog", groep: "Superkracht" },
  { title: "Onzichtbaar (en dus blind)", groep: "Superkracht" },
  { title: "Tijd 10 seconden terugspoelen", groep: "Superkracht" },
  { title: "Elke dag 2x kleiner", groep: "Jij verandert" },
  { title: "Elke dag 2x groter", groep: "Jij verandert" },
  { title: "Nooit meer slapen", groep: "Jij verandert" },
  { title: "Alle gedachten om je heen horen", groep: "Jij verandert" },
  { title: "Aarde draait 10x sneller", groep: "Wereld verandert" },
  { title: "Zwaartekracht valt 1 seconde uit", groep: "Wereld verandert" },
  { title: "Maan 2x zo dichtbij", groep: "Wereld verandert" },
  { title: "Zon verdwijnt 1 minuut", groep: "Wereld verandert" },
  { title: "Onsterfelijk voor altijd", groep: "Duister" },
  { title: "Elke dag 1 jaar jonger", groep: "Duister" },
  { title: "Wakker worden en iedereen is weg", groep: "Duister" },
  { title: "Tijd stilzetten", groep: "Kandidaat (sterke short)" }
], Dm = [
  "Video 3: scènes 10-22 animeren en renderen op de pc",
  "Video 3: teaser, flash-forwards en eindmontage (-14 LUFS)",
  "Video 3: titel, thumbnail, beschrijving en 7 shorts",
  "Video 1: slot-haakje in de titel fixen",
  "Onderwerp video 4 kiezen uit de ideeënlijst"
], Nm = [
  {
    title: "Animeer video 3: geen regels meer",
    id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGTfi8z2mFAQH5Qa5zaASKk1",
    state: "working",
    last: "5 nov 00:42",
    doing: "Animeert scène 13 (de brug), stills checken"
  },
  {
    title: "Maak thumbnail voor video 3",
    id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGTs2SxpLDEpFBKs9hyAGKot",
    state: "working",
    last: "5 nov 00:38",
    doing: "Eerste echte opdracht uit Driftmark HQ. Eigen thread start: jongen in rood licht, kruispunt bij nacht, tekst NO MORE RULES."
  },
  {
    title: "Driftmark HQ (dit hoofdscherm)",
    id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGD3kJS5r6nXrqiC2f5NfjRQ",
    state: "working",
    last: "5 nov 00:17",
    doing: "Live data, echte tijd en alles in het Nederlands."
  },
  {
    title: "Bouw cast en sets voor geen-regels-video",
    id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGCHT43zJaABsdPF4uv4swV5",
    state: "done",
    last: "5 nov 00:25",
    doing: "Cast (37 figuren), dieren en 36 set-varianten klaar in videos/geen-regels/ (cast, dieren, sets + overzicht_sets_no_rules.jpg). Wacht op jouw akkoord."
  },
  {
    title: "Schrijf titel, beschrijving en tags video 2",
    id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGFt2jvrzboJ4GbK8fbcasKv",
    state: "done",
    last: "31 okt 15:23",
    doing: "Wacht op jouw reactie."
  },
  {
    title: "Bedenk ideeën voor teaser-shorts",
    id: "cmsg_01LkmukDuDNkj8pXsDu4v8WGS9PSyyns39jsYw5hE9SySp",
    state: "done",
    last: "28 okt 12:30",
    doing: "Wacht op jouw reactie."
  },
  {
    title: "Schrijf werkwijze-document",
    id: "cmsg_01LkmukDuDNkj8pXsDu4v8WG3mkzfMZCLNKhwkm4CN7Tss",
    state: "done",
    last: "4 nov 21:49"
  },
  {
    title: "Verloop video 3",
    id: "cmsg_01LkmukDuDNkj8pXsDu4v8WG8Td6Q42bhkx3TbQHgnSwbh",
    state: "done",
    last: "4 nov 15:33"
  }
], zm = { subscribers: 25, views: 13566, bron: "vidIQ", datum: "5 nov 01:00" }, Oa = { updated: Pm, channel: jm, videos: Im, shorts: xm, next: Dm, ideas: Rm, links: Am, activity: Nm, youtube: zm }, Om = ["driftmark-hq/status.json", "/driftmark-hq/status.json"];
let fo;
const ad = La((o) => ({
  data: Oa,
  source: "ingebouwd",
  checkedAt: null,
  refresh: async () => {
    try {
      if (fo === void 0) {
        const d = window.claude;
        fo = d != null && d.use ? await d.use("files") : null;
      }
      if (!fo) {
        o({ source: "geen-toegang", checkedAt: Date.now() });
        return;
      }
      let s = null;
      for (const d of Om)
        try {
          const f = await fo.read(d), u = JSON.parse(new TextDecoder().decode(f.bytes)), p = { ...Oa, ...u };
          o({ data: p, source: "live", checkedAt: Date.now() });
          try {
            (await import("./sync-4RTPzONh.js")).applyReal(p);
          } catch (m) {
            console.warn("sync", m);
          }
          return;
        } catch (f) {
          s = f;
        }
      const a = s == null ? void 0 : s.code;
      o({ source: a === "not_granted" ? "geen-toegang" : "fout", checkedAt: Date.now() });
    } catch {
      o({ source: "fout", checkedAt: Date.now() });
    }
  }
}));
let sd = !1;
function Mm() {
  sd || (sd = !0, import("./sync-4RTPzONh.js").then((o) => o.applyReal(Oa)), setTimeout(() => void ad.getState().refresh(), 1500), setInterval(() => void ad.getState().refresh(), 6e4));
}
const Lm = {
  // navigatie & algemeen
  Projects: "Projecten",
  Agents: "Agents",
  Channels: "Kanalen",
  Analytics: "Statistieken",
  Threads: "Threads",
  Finances: "Financiën",
  "War Room": "Crisiskamer",
  Upgrades: "Upgrades",
  Achievements: "Prestaties",
  Settings: "Instellingen",
  "Company rank": "Bedrijfsrang",
  XP: "XP",
  Notifications: "Meldingen",
  "Mark all read": "Alles gelezen",
  "All caught up.": "Je bent helemaal bij.",
  "Total views": "Totaal weergaven",
  Balance: "Saldo",
  Reputation: "Reputatie",
  "Skip 1 day": "1 dag overslaan",
  "Resume simulation": "Simulatie hervatten",
  "Pause simulation": "Simulatie pauzeren",
  "Skipped ahead one day.": "Een dag vooruitgespoeld.",
  Cancel: "Annuleren",
  Close: "Sluiten",
  "DEMO DATA": "DEMODATA",
  DEMO: "DEMO",
  "INCLUDES DEMO DATA": "BEVAT DEMODATA",
  "LOCAL SIMULATION": "LOKALE SIMULATIE",
  "INTERNAL · SIMULATED": "INTERN · GESIMULEERD",
  "Start New Video": "Nieuwe video starten",
  "Assign Task": "Taak geven",
  "Hire Agent": "Agent aannemen",
  "Upgrade Office": "Kantoor upgraden",
  "🎬 Start New Video": "🎬 Nieuwe video starten",
  "👋 Hire AI Agent": "👋 AI-agent aannemen",
  "📋 Assign Task": "📋 Taak geven",
  "📺 Launch New Channel": "📺 Nieuw kanaal starten",
  "📊 Reports": "📊 Rapporten",
  "CEO Dashboard": "CEO-dashboard",
  "Office Upgrades": "Kantoor-upgrades",
  "Achievements & Missions": "Prestaties & missies",
  "YouTube Channels": "YouTube-kanalen",
  "AI Agents": "AI-agents",
  // statussen & prioriteit
  Pending: "Wachtend",
  Assigned: "Toegewezen",
  "In Progress": "Bezig",
  Review: "Controle",
  Approved: "Goedgekeurd",
  Rejected: "Afgekeurd",
  Completed: "Afgerond",
  Low: "Laag",
  Medium: "Normaal",
  High: "Hoog",
  Critical: "Kritiek",
  Active: "Actief",
  "Awaiting Approval": "Wacht op goedkeuring",
  "Awaiting Publish": "Klaar om te publiceren",
  Published: "Gepubliceerd",
  Cancelled: "Gestopt",
  idle: "vrij",
  working: "aan het werk",
  meeting: "in overleg",
  training: "in training",
  Idle: "Vrij",
  Working: "Aan het werk",
  Meeting: "In overleg",
  Training: "In training",
  Investigating: "Onderzoek loopt",
  Ready: "Klaar",
  Resolved: "Opgelost",
  Dismissed: "Afgewezen",
  // afdelingen & stappen
  Research: "Onderzoek",
  Creative: "Creatief",
  Script: "Script",
  Voice: "Stem",
  Production: "Productie",
  Thumbnail: "Thumbnail",
  Publishing: "Publicatie",
  "CEO & Analytics": "CEO & statistieken",
  "Research Department": "Onderzoeksafdeling",
  "Creative Department": "Creatieve afdeling",
  "Script Department": "Scriptafdeling",
  "Voice Department": "Stemafdeling",
  "Production Department": "Productieafdeling",
  "Thumbnail Department": "Thumbnailafdeling",
  "Publishing Department": "Publicatieafdeling",
  "CEO & Analytics Department": "CEO & statistiekafdeling",
  "Topic Selection": "Onderwerp kiezen",
  "Titles & Hooks": "Titels & hooks",
  Scriptwriting: "Script schrijven",
  "Fact Checking": "Feiten checken",
  "Voice-over": "Voice-over",
  "Video Editing": "Animatie & montage",
  "Quality Control": "Kwaliteitscheck",
  "CEO Approval": "Goedkeuring niels",
  // rollen
  Researcher: "Onderzoeker",
  "Niche Analyst": "Niche-analist",
  "Competitor Analyst": "Concurrentie-analist",
  "Topic Finder": "Onderwerpzoeker",
  "Idea Generator": "Ideeënbedenker",
  "Title Specialist": "Titelspecialist",
  "Hook Specialist": "Hook-specialist",
  Scriptwriter: "Scriptschrijver",
  "Storytelling Expert": "Verhaalexpert",
  "Fact Checker": "Feitenchecker",
  "Quality Controller": "Kwaliteitscontroleur",
  "Voice Director": "Stemregisseur",
  "Voice Generator": "Stemmenmaker",
  "Video Editor": "Animator/editor",
  "Visual Researcher": "Beeldresearcher",
  "Editing Supervisor": "Montagechef",
  "Thumbnail Designer": "Thumbnailontwerper",
  "CTR Specialist": "CTR-specialist",
  "Upload Manager": "Uploadmanager",
  "SEO Specialist": "SEO-specialist",
  "Social Media Manager": "Socialemediamanager",
  "CEO Agent": "CEO-agent",
  "Financial Manager": "Financieel manager",
  "Performance Analyst": "Prestatie-analist",
  "Attention to Detail": "Oog voor detail",
  "in meetings": "in overleg",
  "⏳ Waiting for you (": "⏳ Wacht op jou (",
  Publish: "Publiceren",
  "Garage Startup": "Garagebedrijf",
  "Growing Studio": "Groeiende studio",
  "DEMO DATA ": "DEMODATA",
  // crisiskamer
  "Declining Views": "Dalende weergaven",
  "Low CTR": "Lage CTR",
  "Poor Retention": "Slechte kijkduur",
  "Production Delays": "Productievertraging",
  "Falling Revenue": "Dalende inkomsten",
  Problem: "Probleem",
  Scope: "Bereik",
  "Convene War Room": "Crisiskamer bijeenroepen",
  "Approve plan": "Plan goedkeuren",
  "✓ Approved by CEO": "✓ Goedgekeurd door niels",
  "Dismiss case": "Zaak sluiten",
  "Hire a CEO Agent, Performance Analyst or Financial Manager first.": "Neem eerst een CEO-agent, prestatie-analist of financieel manager aan.",
  "No cases yet. Pick a problem above and convene the War Room.": "Nog geen zaken. Kies hierboven een probleem en roep de crisiskamer bijeen.",
  "Agents are gathering data in the War Room…": "Agents verzamelen data in de crisiskamer…",
  "Approve recommendation?": "Aanbeveling goedkeuren?",
  "Management agents investigate problems and prepare recommendations. Nothing is executed without your approval.": "Management-agents onderzoeken problemen en maken aanbevelingen. Niets gebeurt zonder jouw goedkeuring.",
  "War Room convened — analysis in ~6 hours (game time).": "Crisiskamer bijeengeroepen. Analyse over ~6 uur (speltijd).",
  "The executive crisis room. Management agents investigate declining metrics and bring recommendations for your approval.": "De crisiskamer. Management-agents onderzoeken dalende cijfers en leggen aanbevelingen aan jou voor.",
  "No active cases. Convene the War Room to investigate a problem.": "Geen open zaken. Roep de crisiskamer bijeen om een probleem te onderzoeken.",
  "Open War Room dashboard": "Crisiskamer openen",
  // modals
  "Greenlight project": "Project starten",
  Channel: "Kanaal",
  Topic: "Onderwerp",
  "Working title": "Werktitel",
  Priority: "Prioriteit",
  "Deadline (game days)": "Deadline (dagen, echte tijd)",
  "The project enters the pipeline at": "Het project begint bij",
  "and flows through all 11 stages. You'll be asked to approve it at": "en gaat door alle 11 stappen. Je keurt het goed bij",
  "and to confirm before": "en bevestigt vóór",
  Assign: "Toewijzen",
  Title: "Titel",
  "Description / instructions": "Beschrijving / instructies",
  "Assigned agent": "Agent",
  "Deadline (days)": "Deadline (dagen)",
  "Link to project": "Koppel aan project",
  "— none —": "— geen —",
  "Depends on": "Hangt af van",
  "— no dependency —": "— niets —",
  "Assign to channel": "Toewijzen aan kanaal",
  "All channels": "Alle kanalen",
  "All desks are taken. Buy an Office Expansion upgrade to hire more agents.": "Alle bureaus zijn bezet. Koop de upgrade Kantooruitbreiding om meer agents aan te nemen.",
  "Create channel": "Kanaal maken",
  "Channel name": "Kanaalnaam",
  Logo: "Logo",
  Color: "Kleur",
  Niche: "Niche",
  "Target audience": "Doelgroep",
  "Expected RPM (€)": "Verwachte RPM (€)",
  "Uploads per week": "Uploads per week",
  "This creates a simulated channel. Linking a real YouTube channel requires the YouTube Data API (see Settings).": "Dit maakt een gesimuleerd kanaal. Een echt YouTube-kanaal koppelen kan via de YouTube Data API (zie Instellingen).",
  "What's the video about?": "Waar gaat de video over?",
  "Ask Research for a suggestion": "Vraag Onderzoek om een idee",
  "e.g. Analyse top 10 competitor videos": "bv. Analyseer de top 10 IFOLOGY-video's",
  "General audience": "Algemeen publiek",
  "e.g. Personal finance explainers": "bv. 3D What If-shorts",
  "e.g. 22–40, US/EU, beginner investors": "bv. 13-24, wereldwijd",
  "e.g. Money Mechanics": "bv. Driftmark Extra",
  // agent
  Level: "Niveau",
  Performance: "Prestatie",
  Morale: "Moraal",
  "Assign task": "Taak geven",
  Remove: "Ontslaan",
  "Save instructions": "Instructies opslaan",
  "Share to Threads": "Delen op Threads",
  "No AI model connected — output is simulated. Add a Claude or OpenAI key in Settings for real results.": "Geen AI-model gekoppeld, de uitvoer is gesimuleerd. Echte opdrachten lopen via Driftmark HQ.",
  "No tasks yet.": "Nog geen taken.",
  "Agent profile": "Agentprofiel",
  "This agent will leave the company permanently. Their open tasks return to the queue. This cannot be undone.": "Deze agent verlaat het bedrijf. Open taken gaan terug in de wachtrij. Dit kan niet ongedaan worden.",
  "Remove agent": "Agent ontslaan",
  "Busy with a task": "Bezig met een taak",
  "Instructions (system prompt)": "Instructies (werkregels)",
  "Instructions saved.": "Instructies opgeslagen.",
  "Channel assignment": "Kanaal",
  "Current task": "Huidige taak",
  "In training.": "In training.",
  "Idle — waiting for work.": "Vrij, wacht op werk.",
  // afdeling & project
  "Assign department to channel…": "Afdeling aan kanaal koppelen…",
  "Pending CEO approvals": "Wacht op jouw goedkeuring",
  "Nothing waiting for you.": "Er wacht niets op je.",
  "No active work in this stage.": "Geen werk in deze stap.",
  "Recently delivered": "Net opgeleverd",
  "Assigned tasks": "Toegewezen taken",
  Team: "Team",
  "Open tasks": "Open taken",
  "Avg quality": "Gem. kwaliteit",
  Quality: "Kwaliteit",
  Cost: "Kosten",
  Rejections: "Afkeuringen",
  Tasks: "Taken",
  "CEO approval required": "Jouw goedkeuring nodig",
  "Review the deliverables below. Approve to move to Publishing, or send it back to a department with feedback.": "Bekijk het werk hieronder. Keur goed voor publicatie, of stuur het terug met feedback.",
  Approve: "Goedkeuren",
  "Send back": "Terugsturen",
  "Ready to publish": "Klaar om te publiceren",
  "Publishing requires your explicit confirmation. YouTube is not connected, so the upload is simulated locally.": "Publiceren vraagt jouw bevestiging. Claude maakt titel, beschrijving, tags en thumbnail klaar; uploaden doe je zelf in YouTube Studio.",
  "Publish…": "Publiceren…",
  Views: "Weergaven",
  Revenue: "Inkomsten",
  "Tasks & deliverables": "Taken & opleveringen",
  Timeline: "Tijdlijn",
  "Publish this video?": "Deze video publiceren?",
  "Feedback for the department…": "Feedback voor de afdeling…",
  "CEO requested revisions": "niels wil aanpassingen",
  "Cancel project?": "Project stoppen?",
  "Cancel project": "Project stoppen",
  "· overdue": "· te laat",
  "Created:": "Gemaakt:",
  "Deadline:": "Deadline:",
  "Quality:": "Kwaliteit:",
  "Kind:": "Soort:",
  Documents: "Documenten",
  Send: "Versturen",
  "Approve deliverable": "Oplevering goedkeuren",
  "Request changes": "Aanpassingen vragen",
  "Reassign to…": "Overdragen aan…",
  "Open agent": "Agent openen",
  "Former agent": "Oud-agent",
  "Leave feedback for the agent…": "Feedback voor de agent…",
  Deliverable: "Oplevering",
  Project: "Project",
  // pagina's
  "Company level": "Bedrijfsniveau",
  "Company reputation": "Reputatie",
  "Daily missions": "Dagelijkse missies",
  "refresh every game day": "nieuw elke speldag",
  "Hire agent": "Agent aannemen",
  All: "Alle",
  "Open roles you haven't hired yet": "Open rollen die je nog niet hebt",
  "Search agents…": "Agents zoeken…",
  Subs: "Abonnees",
  Videos: "Video's",
  "Top videos": "Topvideo's",
  "Active agents": "Actieve agents",
  "Active projects": "Actieve projecten",
  "Pending approvals": "Wacht op goedkeuring",
  "Revenue vs expenses (€ / day)": "Inkomsten vs. uitgaven (€ per dag)",
  "Views per day": "Weergaven per dag",
  "Channel performance (views/day)": "Kanaalprestaties (weergaven per dag)",
  "Production performance by stage": "Productie per stap",
  "Average quality by stage": "Gem. kwaliteit per stap",
  "CTR & AVD trend (%)": "CTR & kijkduur (%)",
  "CTR (7d)": "CTR (7 d)",
  "AVD (7d)": "Kijkduur (7 d)",
  AVD: "Kijkduur",
  Subscribers: "Abonnees",
  Expenses: "Uitgaven",
  Income: "Inkomsten",
  Profit: "Winst",
  "Break-even": "Break-even",
  "Monthly P&L": "Maandresultaat",
  "New channel": "Nieuw kanaal",
  "💸 Monetized": "💸 Inkomsten aan",
  "New video": "Nieuwe video",
  "No projects yet for this channel.": "Nog geen projecten voor dit kanaal.",
  "(demo)": "(demo)",
  "Channel profile": "Kanaalprofiel",
  Edit: "Bewerken",
  Save: "Opslaan",
  "Uploads / week": "Uploads per week",
  "Agents not assigned to a specific channel work for all channels.": "Agents zonder vast kanaal werken voor alle kanalen.",
  "Assign a whole department": "Hele afdeling koppelen",
  "Simulated channels. Each has its own niche, audience, schedule, projects and dedicated agents.": "Gesimuleerde kanalen, elk met eigen niche, publiek, schema, projecten en agents.",
  "New subs": "Nieuwe abonnees",
  "Channel updated.": "Kanaal bijgewerkt.",
  "Upload schedule": "Uploadschema",
  "Assign department": "Afdeling koppelen",
  "All channels (incl. company overhead)": "Alle kanalen (incl. vaste kosten)",
  "All months": "Alle maanden",
  "Channel view shows only costs and revenue attributed to this channel; salaries, subscriptions and software are company overhead.": "Per kanaal zie je alleen de kosten en inkomsten van dat kanaal; salarissen, abonnementen en software zijn vaste kosten.",
  "No expenses in this period.": "Geen uitgaven in deze periode.",
  Categories: "Categorieën",
  "Video ROI": "Rendement per video",
  "Publish a video to track its ROI.": "Publiceer een video om het rendement te zien.",
  Date: "Datum",
  Category: "Categorie",
  Note: "Notitie",
  Amount: "Bedrag",
  "Profit margin": "Winstmarge",
  "Expense breakdown": "Uitgaven per soort",
  "Ad Revenue": "Advertentie-inkomsten",
  Salaries: "Salarissen",
  Freelancers: "Freelancers",
  "AI Subscriptions": "AI-abonnementen",
  Software: "Software",
  Hiring: "Aannemen",
  Rewards: "Beloningen",
  "Building the office…": "Kantoor wordt gebouwd…",
  "Click a room to open its dashboard · click an employee for their profile · drag to rotate, scroll to zoom": "Klik op een kamer voor het dashboard · klik op een medewerker voor het profiel · sleep om te draaien, scroll om te zoomen",
  "Production pipeline": "Productielijn",
  "All projects →": "Alle projecten →",
  "No active projects. Start a new video!": "Geen actieve projecten. Start een nieuwe video!",
  "Live on Threads": "Live op Threads",
  "Open →": "Openen →",
  "Waiting for you": "Wacht op jou",
  Empty: "Leeg",
  "No projects yet.": "Nog geen projecten.",
  "Every video moves through the 11-stage production pipeline. Rejected work loops back to the responsible department.": "Elke video gaat door de productielijn van 11 stappen. Afgekeurd werk gaat terug naar de afdeling die het maakte.",
  "Pipeline board": "Productiebord",
  "All projects": "Alle projecten",
  "Task engine": "Takenlijst",
  "Integration status": "Koppelingen",
  "API credentials": "API-sleutels",
  "Agent AI provider": "AI voor agents",
  "Local simulation (no API)": "Lokale simulatie (geen API)",
  "Anthropic API key": "Anthropic API-sleutel",
  "Claude model": "Claude-model",
  "OpenAI API key": "OpenAI API-sleutel",
  "OpenAI model": "OpenAI-model",
  "YouTube Data API key (read-only stats)": "YouTube Data API-sleutel (alleen stats lezen)",
  "Threads access token": "Threads-token",
  "Voice API key": "Stem-API-sleutel",
  "Supabase anon key": "Supabase anon-sleutel",
  "Save settings": "Instellingen opslaan",
  "YouTube Data API test (read-only)": "YouTube Data API-test (alleen lezen)",
  Fetch: "Ophalen",
  "Save data": "Opslag",
  "Export save (keys stripped)": "Opslag exporteren (zonder sleutels)",
  "Import save": "Opslag importeren",
  "Save to Supabase": "Opslaan in Supabase",
  "Load from Supabase": "Laden uit Supabase",
  "Progress autosaves to this browser. Supabase requires the table in": "Voortgang wordt in deze browser bewaard. Supabase heeft de tabel nodig uit",
  "Danger zone": "Gevarenzone",
  "Reset game": "Game resetten",
  "Integrations, data and simulation.": "Koppelingen, data en simulatie.",
  "Settings saved locally.": "Instellingen lokaal opgeslagen.",
  "Not a valid save file": "Geen geldig opslagbestand",
  "Import save?": "Opslag importeren?",
  "Replace progress": "Voortgang vervangen",
  "Saved to Supabase.": "Opgeslagen in Supabase.",
  "Loaded from Supabase.": "Geladen uit Supabase.",
  "No cloud save found.": "Geen cloudopslag gevonden.",
  "Reset the whole company?": "Hele bedrijf resetten?",
  "All progress, agents, channels and history will be permanently replaced with a fresh demo company. This cannot be undone.": "Alle voortgang, agents, kanalen en geschiedenis worden vervangen door een nieuwe start. Dit kan niet ongedaan worden.",
  "Reset everything": "Alles resetten",
  "Company reset to demo state.": "Bedrijf opnieuw gestart.",
  "External publishing (YouTube, Threads) is never performed automatically. Publishing in this game always stays in the local simulation and requires your explicit confirmation.": "Er wordt nooit automatisch iets op YouTube of Threads gezet. Uploaden doe je altijd zelf; Claude maakt alles klaar.",
  "Keys are stored only in this browser's local storage and sent directly to the provider you choose. Use restricted keys and never share your save file if it contains keys.": "Sleutels worden alleen in deze browser bewaard en direct naar de gekozen dienst gestuurd. Deel je opslagbestand nooit als er sleutels in staan.",
  "Internal company social network": "Intern sociaal netwerk",
  "Visible to all agents · never posted externally": "Zichtbaar voor alle agents · je berichten gaan als opdracht naar Claude",
  Post: "Plaatsen",
  Share: "Delen",
  Reply: "Reageren",
  "Reply…": "Reageer…",
  "Most active": "Meest actief",
  "About this feed": "Over deze feed",
  "not connected": "niet gekoppeld",
  "but is": "maar is",
  "for the real Meta Threads API is prepared in": "voor de echte Meta Threads-API staat klaar in",
  "Feedback loop": "Feedbacklus",
  "Post an update to the whole company…": "Plaats een bericht voor het hele team…",
  "For you": "Voor jou",
  "Shared with the whole company.": "Gedeeld met het hele team.",
  "Maxed out": "Maximaal",
  Update: "Update",
  Report: "Rapport",
  Question: "Vraag",
  Win: "Succes",
  "Hand-off": "Overdracht",
  Alert: "Waarschuwing",
  Upgrade: "Upgraden",
  About: "Over",
  "Approval Memo": "Goedkeuringsnotitie",
  "Upload Package": "Uploadpakket",
  "Task Brief": "Opdracht",
  "Publish (simulation)": "Publiceren",
  // upgrades & prestaties
  "Render Farm": "Renderfarm",
  "Coffee Bar": "Koffiebar",
  "Office Expansion": "Kantooruitbreiding",
  "Neon Lighting Pack": "Neonverlichting",
  "Glass Meeting Pods": "Glazen vergaderhokjes",
  "Training Lab": "Trainingslab",
  "Sound Studio": "Geluidsstudio",
  "GPU racks for the edit bay.": "GPU-rekken voor de montage.",
  "Espresso for everyone. Morale stays high.": "Espresso voor iedereen. Moraal blijft hoog.",
  "More desks, more agents.": "Meer bureaus, meer agents.",
  "Instagrammable office. Boosts reputation.": "Fotogeniek kantoor. Meer reputatie.",
  "Faster reviews, fewer rejections.": "Snellere controles, minder afkeuringen.",
  "VR training stations.": "VR-trainingsplekken.",
  "Acoustic booth for the voice team.": "Geluidscabine voor het stemteam.",
  "+15% production speed per level": "+15% productiesnelheid per niveau",
  "+8 morale recovery per level": "+8 moraalherstel per niveau",
  "+6 agent slots per level": "+6 bureaus per niveau",
  "+10 reputation": "+10 reputatie",
  "+6 review quality per level": "+6 controlekwaliteit per niveau",
  "−25% training cost and time per level": "−25% trainingskosten en -tijd per niveau",
  "+8 voice quality per level": "+8 stemkwaliteit per niveau",
  "First Upload": "Eerste upload",
  "100K Views": "100K weergaven",
  "Millionaire Views": "Miljoen weergaven",
  "Monetized!": "Inkomsten aan!",
  "First €1,000": "Eerste €1.000",
  "Growing Team": "Groeiend team",
  "Interior Designer": "Interieurontwerper",
  "Crisis Manager": "Crisismanager",
  "Rising Company": "Groeiend bedrijf",
  "Network Builder": "Netwerkbouwer",
  "Elite Employee": "Topmedewerker",
  "Content Machine": "Contentmachine",
  "Full House": "Vol huis",
  "Publish your first video.": "Publiceer je eerste video.",
  "Reach 100,000 total views across all channels.": "Haal 100.000 weergaven over alle kanalen.",
  "Reach 1,000,000 total views.": "Haal 1.000.000 weergaven.",
  "Get your first channel monetized (1,000 subscribers).": "Zet de inkomsten van je eerste kanaal aan (1.000 abonnees).",
  "Earn €1,000 in total ad revenue.": "Verdien in totaal €1.000 aan advertenties.",
  "Hire your first new AI agent.": "Neem je eerste nieuwe AI-agent aan.",
  "Buy your first office upgrade.": "Koop je eerste kantoor-upgrade.",
  "Resolve your first War Room case.": "Los je eerste crisiskamer-zaak op.",
  "Reach company level 5.": "Haal bedrijfsniveau 5.",
  "Launch a new channel of your own.": "Start een eigen nieuw kanaal.",
  "Train an agent to level 5.": "Train een agent tot niveau 5.",
  "Post an update on Threads": "Plaats een bericht op Threads",
  "Train an agent": "Train een agent",
  // adapters
  "Agent reasoning & text deliverables": "Denkwerk en tekst van agents",
  "Agents use the local simulation for text output.": "Agents gebruiken de lokale simulatie voor tekst.",
  "Read channel statistics": "Kanaalstatistieken lezen",
  "Read-only. Uploading is not implemented; publishing is simulated locally.": "Alleen lezen. Uploaden doe je zelf in YouTube Studio.",
  "Cross-post internal updates": "Interne berichten doorplaatsen",
  "Adapter interface only. The internal Threads feed is simulated and never posts externally.": "Alleen de koppeling. De interne Threads-feed plaatst nooit iets extern.",
  "Voice generation": "Stemmen maken",
  "Interface prepared. Voice-over stage outputs simulated metadata.": "Koppeling klaar. Echte stemmen maakt Claude in ElevenLabs v4.",
  "Image generation": "Beelden maken",
  "Interface prepared. Thumbnail stage outputs simulated variants.": "Koppeling klaar. Echte thumbnails maakt Claude op opdracht.",
  "Video production": "Videoproductie",
  "Interface prepared. Editing stage outputs simulated renders.": "Koppeling klaar. Echte animatie gebeurt in Blender op je pc.",
  "Cloud saves": "Cloudopslag",
  "Save data is in local browser storage until you configure Supabase.": "Opslag staat in deze browser tot je Supabase instelt.",
  "Claude / OpenAI models": "Claude- / OpenAI-modellen"
}, $m = [
  [/^(\d+) working$/, (o, s) => `${s} aan het werk`],
  [/^(\d+) in meetings$/, (o, s) => `${s} in overleg`],
  [/^(\d+) idle$/, (o, s) => `${s} vrij`],
  [/^just now$/, () => "zojuist"],
  [/^(\d+)h ago$/, (o, s) => `${s} u geleden`],
  [/^(\d+)d ago$/, (o, s) => `${s} d geleden`],
  [/^(\d+) completed$/, (o, s) => `${s} afgerond`],
  [/^Task history · (\d+) completed$/, (o, s) => `Takengeschiedenis · ${s} afgerond`],
  [/^Day (\d+)/, (o, s) => `Dag ${s}`],
  [/^(\d+)d$/, (o, s) => `${s} d`],
  [/^⏳ Waiting for you \((\d+)\)$/, (o, s) => `⏳ Wacht op jou (${s})`],
  [/^Start (\d+) new videos?$/, (o, s) => `Start ${s} nieuwe video${s === "1" ? "" : "'s"}`],
  [/^Like (\d+) Threads posts$/, (o, s) => `Like ${s} Threads-berichten`],
  [/^Complete (\d+) tasks company-wide$/, (o, s) => `Rond ${s} taken af`],
  [/^(\d+)\/(\d+) achievements unlocked$/, (o, s, a) => `${s}/${a} prestaties behaald`],
  [/^Needs (.*)× current income$/, (o, s) => `Vraagt ${s}× de huidige inkomsten`],
  [/^No revenue yet$/, () => "Nog geen inkomsten"],
  [/^(\d+)\/(\d+) desks filled · payroll ≈ (.*)\/day$/, (o, s, a, d) => `${s}/${a} bureaus bezet · loonkosten ≈ ${d}/dag`],
  [/^Level (\d+)$/, (o, s) => `Niveau ${s}`],
  [/^L(\d+)$/, (o, s) => `N${s}`]
], Ed = ["placeholder", "title", "aria-label"];
function ud(o) {
  const s = o.trim();
  if (!s) return null;
  const a = Lm[s];
  if (a !== void 0) return a === s ? null : o.replace(s, a);
  for (const [d, f] of $m)
    if (s.match(d)) {
      const p = s.replace(d, f);
      return p === s ? null : o.replace(s, p);
    }
  return null;
}
function Hr(o) {
  if (o.nodeType === 3) {
    const a = ud(o.nodeValue || "");
    a !== null && a !== o.nodeValue && (o.nodeValue = a);
    return;
  }
  if (o.nodeType !== 1) return;
  const s = o;
  if (!(s.tagName === "SCRIPT" || s.tagName === "STYLE" || s.tagName === "TEXTAREA")) {
    for (const a of Ed) {
      const d = s.getAttribute(a);
      if (d) {
        const f = ud(d);
        f !== null && f !== d && s.setAttribute(a, f);
      }
    }
    o.childNodes.forEach(Hr);
  }
}
function Fm(o) {
  document.documentElement.lang = "nl", Hr(o), new MutationObserver((s) => {
    for (const a of s)
      a.type === "characterData" || a.type === "attributes" ? Hr(a.target) : a.addedNodes.forEach(Hr);
  }).observe(o, { subtree: !0, childList: !0, characterData: !0, attributes: !0, attributeFilter: Ed });
}
const Um = mo.lazy(() => import("./OfficeScene-CyGBRfg1.js"));
let Tn = null, cd = !1;
function Vm(o, s) {
  Tn || (cd || (cd = !0, et.setState({ tick: Br() }), Mm(), setInterval(() => {
    Br() !== et.getState().tick && et.setState({ tick: Br() });
  }, 1e4), et.subscribe((a, d) => {
    if (a.selectedAgentId === d.selectedAgentId && a.agents === d.agents) return;
    const f = a.agents.find((u) => u.id === a.selectedAgentId);
    s == null || s(f ? { id: f.id, name: f.name, doing: f.personality, state: f.state, department: f.department } : null);
  }), Fm(o)), Tn = Ap.createRoot(o), Tn.render(
    /* @__PURE__ */ so.jsx(mo.StrictMode, { children: /* @__PURE__ */ so.jsx(mo.Suspense, { fallback: /* @__PURE__ */ so.jsx("div", { style: { display: "grid", placeItems: "center", height: "100%", color: "#8f9bcb", font: "14px system-ui" }, children: "Kantoor laden…" }), children: /* @__PURE__ */ so.jsx(Um, {}) }) })
  ));
}
function Wm() {
  Tn == null || Tn.unmount(), Tn = null;
}
function Hm() {
  et.getState().selectAgent(null);
}
export {
  va as R,
  Ma as a,
  Br as b,
  Ap as c,
  yd as d,
  H as e,
  Hm as f,
  Sp as g,
  Wm as h,
  so as j,
  Vm as m,
  mo as r,
  ct as s,
  et as u
};
