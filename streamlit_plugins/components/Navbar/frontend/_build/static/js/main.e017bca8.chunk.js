(this.webpackJsonpnav_bar = this.webpackJsonpnav_bar || []).push([[0], {
    13: function(e, t, a) {
        e.exports = a(24)
    },
    23: function(e, t, a) {},
    24: function(e, t, a) {
        "use strict";
        a.r(t);
        var n = a(2)
          , i = a.n(n)
          , r = a(10)
          , c = a.n(r)
          , l = a(4)
          , o = a(1)
          , u = a(3)
          , m = a(5)
          , s = a(12)
          , d = (a(8),
        function(e) {
            var t = e.menuitem
              , a = e.isactive
              , n = e.menu_id
              , r = e.menu_callback
              , c = function(e) {
                r(""),
                m.Streamlit.setComponentValue(e)
            };
            return function(e, t, a) {
                var n = ""
                  , r = ""
                  , o = "";
                return n = e.id ? e.id : e.label,
                !function(e) {
                    if (e) {
                        var t, a = Object(l.a)(e);
                        try {
                            for (a.s(); !(t = a.n()).done; ) {
                                var n = ("" + t.value).codePointAt(0);
                                if (n) {
                                    var i = n.toString(16)
                                      , r = i.length;
                                    if (r > 3) {
                                        var c = i.substring(0, 2);
                                        if (5 === r && "1f" === c)
                                            return !0;
                                        if (4 === r && ["20", "21", "23", "24", "25", "26", "27", "2B", "29", "30", "32"].indexOf(c) > -1)
                                            return !0
                                    }
                                }
                            }
                        } catch (o) {
                            a.e(o)
                        } finally {
                            a.f()
                        }
                    }
                    return !1
                }(e.icon) ? (o = e.icon,
                r = e.label) : r = e.icon + " " + e.label,
                a ? i.a.createElement("li", {
                    className: "nav-item active py-0",
                    key: t
                }, i.a.createElement("a", {
                    className: "nav-link",
                    href: "#" + t,
                    onClick: function() {
                        return c(n)
                    },
                    "data-toggle": "tooltip",
                    "data-placement": "top",
                    "data-html": "true",
                    title: e.ttip
                }, i.a.createElement("i", {
                    className: o
                }), r)) : i.a.createElement("li", {
                    className: "nav-item py-0",
                    key: t
                }, i.a.createElement("a", {
                    className: "nav-link",
                    href: "#" + t,
                    onClick: function() {
                        return c(n)
                    },
                    "data-toggle": "tooltip",
                    "data-placement": "top",
                    "data-html": "true",
                    title: e.ttip
                }, i.a.createElement("i", {
                    className: o
                }), r))
            }(t, n, a)
        }
        )
          , v = function(e) {
            var t = e.subitem
              , a = e.menuid
              , n = e.parent_id
              , r = e.submenu_callback;
            return function(e, t, a) {
                var n = ""
                  , c = ""
                  , o = "";
                return n = e.id ? e.id : e.label,
                !function(e) {
                    if (e) {
                        var t, a = Object(l.a)(e);
                        try {
                            for (a.s(); !(t = a.n()).done; ) {
                                var n = ("" + t.value).codePointAt(0);
                                if (n) {
                                    var i = n.toString(16)
                                      , r = i.length;
                                    if (r > 3) {
                                        var c = i.substring(0, 2);
                                        if (5 === r && "1f" === c)
                                            return !0;
                                        if (4 === r && ["20", "21", "23", "24", "25", "26", "27", "2B", "29", "30", "32"].indexOf(c) > -1)
                                            return !0
                                    }
                                }
                            }
                        } catch (o) {
                            a.e(o)
                        } finally {
                            a.f()
                        }
                    }
                    return !1
                }(e.icon) ? (o = e.icon,
                c = e.label) : c = e.icon + " " + e.label,
                i.a.createElement("li", {
                    key: a + 97 * t
                }, i.a.createElement("a", {
                    className: "dropdown-item",
                    href: "#" + 97 * t,
                    onClick: function() {
                        return function(e, t) {
                            r(t),
                            m.Streamlit.setComponentValue(e)
                        }(n, a)
                    },
                    "data-toggle": "tooltip",
                    "data-placement": "top",
                    "data-html": "true",
                    title: e.ttip
                }, i.a.createElement("i", {
                    className: o
                }), c))
            }(t, a, n)
        }
          , f = (a(23),
        function() {
            var e = Object(s.useStreamlit)()
              , t = Object(n.useState)(!1)
              , a = Object(u.a)(t, 2)
              , r = a[0]
              , c = a[1]
              , f = Object(n.useState)("")
              , p = Object(u.a)(f, 2)
              , b = p[0]
              , g = p[1]
              , _ = Object(n.useState)(!1)
              , k = Object(u.a)(_, 2)
              , E = k[0]
              , y = k[1]
              , h = Object(n.useState)("none")
              , N = Object(u.a)(h, 2)
              , x = N[0]
              , F = N[1];
            if (null == e)
                return null;
            var O = e.args.menu_definition
              , S = e.args.home
              , w = e.args.use_animation
              , C = e.args.login
              , j = e.args.first_select
              , A = e.args.override_theme
              , B = e.args.key
              , P = (e.args.fvalue,
            e.theme)
              , H = function(e, t) {
                return i.a.createElement(v, {
                    subitem: e,
                    menu_id: t,
                    submenu_callback: J,
                    parent_id: e.label,
                    key: t
                })
            }
              , J = function(e) {
                y("" !== e && !E),
                g(e),
                m.Streamlit.setFrameHeight(),
                setTimeout((function() {
                    m.Streamlit.setFrameHeight()
                }
                ), 250)
            }
              , V = function(e, t, a) {
                var n = ""
                  , r = "";
                return !function(e) {
                    if (e) {
                        var t, a = Object(l.a)(e);
                        try {
                            for (a.s(); !(t = a.n()).done; ) {
                                var n = ("" + t.value).codePointAt(0);
                                if (n) {
                                    var i = n.toString(16)
                                      , r = i.length;
                                    if (r > 3) {
                                        var c = i.substring(0, 2);
                                        if (5 === r && "1f" === c)
                                            return !0;
                                        if (4 === r && ["20", "21", "23", "24", "25", "26", "27", "2B", "29", "30", "32"].indexOf(c) > -1)
                                            return !0
                                    }
                                }
                            }
                        } catch (o) {
                            a.e(o)
                        } finally {
                            a.f()
                        }
                    }
                    return !1
                }(e.icon) ? (r = e.icon,
                n = e.label) : n = e.icon + " " + e.label,
                Array.isArray(e.submenu) ? t === j ? i.a.createElement("li", {
                    className: "nav-item py-0 dropdown active",
                    key: 100 * t
                }, i.a.createElement("a", {
                    className: "nav-link dropdown-toggle",
                    href: "#_sub" + t,
                    key: "sub1_" + t,
                    onClick: function() {
                        return J(e.label)
                    },
                    "data-toggle": "tooltip",
                    "data-placement": "top",
                    "data-html": "true",
                    title: e.ttip
                }, i.a.createElement("i", {
                    className: r
                }), n), i.a.createElement("ul", {
                    className: b === e.label && E ? "dropdown-menu show" : "dropdown-menu",
                    key: 103 * t
                }, e.submenu.map((function(e, t) {
                    return H(e, t)
                }
                )))) : i.a.createElement("li", {
                    className: "nav-item py-0 dropdown",
                    key: 100 * t
                }, i.a.createElement("a", {
                    className: "nav-link dropdown-toggle",
                    href: "#_sub" + t,
                    key: "sub1_" + t,
                    onClick: function() {
                        return J(e.label)
                    },
                    "data-toggle": "tooltip",
                    "data-placement": "top",
                    "data-html": "true",
                    title: e.ttip
                }, i.a.createElement("i", {
                    className: r
                }), n), i.a.createElement("ul", {
                    className: b === e.label && E ? "dropdown-menu show" : "dropdown-menu",
                    key: 103 * t
                }, e.submenu.map((function(e, t) {
                    return H(e, t)
                }
                )))) : i.a.createElement(d, {
                    menuitem: e,
                    menu_id: t,
                    isactive: t === j,
                    menu_callback: J
                })
            };
            return function() {
                var e = "complexnavbarSupportedContent"
                  , t = i.a.createElement("div", {
                    className: "hori-selector"
                }, i.a.createElement("div", {
                    className: "left"
                }), i.a.createElement("div", {
                    className: "right"
                }));
                return w ? (e = "complexnavbarSupportedContent",
                t = i.a.createElement("div", {
                    className: "hori-selector"
                }, i.a.createElement("div", {
                    className: "left"
                }), i.a.createElement("div", {
                    className: "right"
                }))) : (e = "navbarSupportedContent",
                t = i.a.createElement(i.a.Fragment, null)),
                i.a.createElement("div", {
                    key: B
                }, (() => {
                    let styleTag = document.querySelector("style.colorsAttr");
                    let styleFunc = () => {
                      var e, t, a, n, i = {
                          menu_background: "#F0F2F6",
                          txc_inactive: "#FFFFFF",
                          txc_active: "#FFFFFF",
                          option_active: "#F63366",
                          "padding-top": "0rem"
                      };
                      (P && (i.menu_background = P.primaryColor,
                      i.txc_inactive = P.secondaryBackgroundColor,
                      i.txc_active = P.textColor,
                      i.option_active = P.backgroundColor),
                      A) && (i.menu_background = null !== (e = A.menu_background) && void 0 !== e ? e : i.menu_background,
                      i.txc_inactive = null !== (t = A.txc_inactive) && void 0 !== t ? t : i.txc_inactive,
                      i.txc_active = null !== (a = A.txc_active) && void 0 !== a ? a : i.txc_active,
                      i.option_active = null !== (n = A.option_active) && void 0 !== n ? n : i.option_active);
                      return ":root {--menu_background: " + i.menu_background + ";--txc_inactive: " + i.txc_inactive + ";--txc_active:" + i.txc_active + ";--option_active:" + i.option_active + ";}"
                    }
                    if ( !styleTag ) {
                        return i.a.createElement("style", {className: "colorsAttr"}, styleFunc());
                    }
                     else {
                         return i.a.createElement("style", {className: "colorsAttr"}, styleFunc());
                     }

                })(), i.a.createElement("nav", {
                    className: "navbar navbar-expand-custom navbar-mainbg w-100 py-0 py-md-0"
                }, i.a.createElement("button", {
                    className: "navbar-toggler",
                    type: "button",
                    onClick: function() {
                        r ? (c(!1),
                        F("none")) : (c(!0),
                        F("block"))
                    },
                    "aria-expanded": r
                }, i.a.createElement("i", {
                    className: "fas fa-bars text-white"
                })), i.a.createElement("div", {
                    className: "navbar-collapse",
                    id: e,
                    style: {
                        display: x
                    }
                }, i.a.createElement("ul", {
                    className: "navbar-nav py-0"
                }, t, (S && (O = [{
                    id: S,
                    label: null,
                    icon: "fa fa-home",
                    ttip: S
                }].concat(Object(o.a)(O))),
                void (C && (O = [].concat(Object(o.a)(O), [{
                    id: C,
                    label: null,
                    icon: "fa fa-user-circle",
                    ttip: C
                }])))), O.map((function(e, t) {
                    return V(e, t)
                }
                ))))))
            }()
        }
        );
        c.a.render(i.a.createElement(i.a.StrictMode, null, i.a.createElement(f, null)), document.getElementById("root"))
    },
    8: function(e, t, a) {}
}, [[13, 1, 2]]]);
//# sourceMappingURL=main.e017bca8.chunk.js.map
