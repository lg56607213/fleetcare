/* FleetCare 견적 요청 (/quote)
   차량 → 특장·외주장착 → 계약 조건 → 신청자 순서로 고르고 /api/quote 로 보낸다.
   차량 데이터는 /truck-data.js (TRUCK_DATA, TRUCK_COLORS) — tools/acerent-to-data.js 가 만든다.
   화면 구조는 gen.py 의 QUOTE 에 있다.
*/
(function () {
  "use strict";

  var root = document.getElementById("quote");
  if (!root || typeof TRUCK_DATA === "undefined") return;

  var TEL = "02-6925-0516";
  var STEPS = 4;
  var MANUAL = "목록에 없는 차량";
  var COLORS = typeof TRUCK_COLORS === "undefined" ? {} : TRUCK_COLORS;

  var state = {
    step: 1,
    brand: "", cat: "", model: "", line: "", trim: "",
    opts: [],                 // 제조사 옵션 [{n, p}]
    extColor: null, intColor: null,
    kit: [], kitCustom: [],   // 특장·외주장착
    tuning: "",               // 구조변경
    product: "", usage: "", period: "", prepay: "", deposit: "", km: "",
    insurance: "", maintenance: ""
  };

  function $(id) { return document.getElementById(id); }
  function won(n) { return Number(n || 0).toLocaleString("ko-KR"); }
  function show(id, on) { $(id).hidden = !on; }
  function isManual() { return state.brand === MANUAL; }

  /* ---------- 1단계: 차량 ---------- */

  function chip(label, extra) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "q-chip";
    b.setAttribute("aria-pressed", "false");
    b.appendChild(document.createTextNode(label));
    if (extra) {
      var s = document.createElement("span");
      s.className = "q-chip-p";
      s.textContent = extra;
      b.appendChild(s);
    }
    return b;
  }

  function press(b, on) {
    b.classList.toggle("is-on", on);
    b.setAttribute("aria-pressed", on ? "true" : "false");
  }

  // 하나만 고르는 목록을 채운다
  function fillOne(grpId, wrapId, names, onPick) {
    var grp = $(grpId);
    grp.innerHTML = "";
    names.forEach(function (name) {
      var b = chip(name);
      b.addEventListener("click", function () {
        Array.prototype.forEach.call(grp.children, function (c) { press(c, c === b); });
        onPick(name);
      });
      grp.appendChild(b);
    });
    if (wrapId) show(wrapId, names.length > 0);
  }

  var LEVELS = ["qCatWrap", "qModelWrap", "qLineWrap", "qTrimWrap", "qOptWrap"];

  function hideFrom(level) {
    LEVELS.slice(level).forEach(function (id) { show(id, false); });
    show("qColorWrap", false);
    show("qPrice", false);
    state.extColor = state.intColor = null;
  }

  function pickBrand(brand) {
    state.brand = brand;
    state.cat = state.model = state.line = state.trim = "";
    state.opts = [];
    hideFrom(0);
    show("qManualWrap", isManual());
    if (isManual()) { $("qManualCar").focus(); return; }
    fillOne("qCat", "qCatWrap", Object.keys(TRUCK_DATA[brand]), pickCat);
  }

  function pickCat(cat) {
    state.cat = cat;
    state.model = state.line = state.trim = "";
    state.opts = [];
    hideFrom(1);
    fillOne("qModel", "qModelWrap", Object.keys(TRUCK_DATA[state.brand][cat]), pickModel);
  }

  function pickModel(model) {
    state.model = model;
    state.line = state.trim = "";
    state.opts = [];
    hideFrom(2);
    fillOne("qLine", "qLineWrap", Object.keys(TRUCK_DATA[state.brand][state.cat][model]), pickLine);
  }

  function pickLine(line) {
    state.line = line;
    state.trim = "";
    state.opts = [];
    hideFrom(3);
    fillOne("qTrim", "qTrimWrap",
      Object.keys(TRUCK_DATA[state.brand][state.cat][state.model][line]), pickTrim);
  }

  function curTrim() {
    try { return TRUCK_DATA[state.brand][state.cat][state.model][state.line][state.trim] || null; }
    catch (e) { return null; }
  }

  function pickTrim(trim) {
    state.trim = trim;
    state.opts = [];
    hideFrom(4);

    var node = curTrim();
    var grp = $("qOpt");
    grp.innerHTML = "";
    (node.opts || []).forEach(function (o) {
      var b = chip(o.n, o.p ? "+" + won(o.p) + "원" : "");
      b.addEventListener("click", function () {
        var on = !b.classList.contains("is-on");
        press(b, on);
        if (on) state.opts.push(o);
        else state.opts = state.opts.filter(function (x) { return x !== o; });
        updatePrice();
      });
      grp.appendChild(b);
    });
    show("qOptWrap", (node.opts || []).length > 0);

    renderColors();
    updatePrice();
  }

  // 색상은 정하지 않아도 된다. 한 번 더 누르면 선택이 풀린다.
  function renderColors() {
    var cols = null;
    try { cols = COLORS[state.brand][state.cat][state.model] || null; } catch (e) {}
    var any = false;
    [["ext", "extColor", "qExt"], ["int", "intColor", "qInt"]].forEach(function (d) {
      var list = (cols && cols[d[0]]) || [];
      var grp = $(d[2]);
      grp.innerHTML = "";
      list.forEach(function (c) {
        var b = chip(c.n, c.p ? "+" + won(c.p) + "원" : "");
        b.addEventListener("click", function () {
          var on = !b.classList.contains("is-on");
          Array.prototype.forEach.call(grp.children, function (x) { press(x, false); });
          press(b, on);
          state[d[1]] = on ? c : null;
          updatePrice();
        });
        grp.appendChild(b);
      });
      show(d[2] + "Row", list.length > 0);
      if (list.length) any = true;
    });
    show("qColorWrap", any);
  }

  function sum(list) {
    return list.reduce(function (s, o) { return s + (o.p || 0); }, 0);
  }

  function colorSum() {
    return (state.extColor ? state.extColor.p : 0) + (state.intColor ? state.intColor.p : 0);
  }

  function unitPrice() {
    var node = curTrim();
    return node ? (node.price || 0) + sum(state.opts) + colorSum() : 0;
  }

  function qty() {
    var n = parseInt($("qQty").value, 10);
    return n > 0 ? Math.min(n, 999) : 1;
  }

  function updatePrice() {
    var node = curTrim();
    if (!node) return;
    $("qPriceNum").textContent = won(unitPrice()) + "원";
    var parts = ["기본 " + won(node.price) + "원"];
    if (sum(state.opts)) parts.push("옵션 " + won(sum(state.opts)) + "원");
    if (colorSum()) parts.push("색상 " + won(colorSum()) + "원");
    var text = parts.length > 1 ? parts.join(" + ") : "";
    if (qty() > 1) text += (text ? " · " : "") + qty() + "대 합계 " + won(unitPrice() * qty()) + "원";
    $("qPriceBreak").textContent = text;
    show("qPrice", true);
  }

  function carLabel() {
    if (isManual()) return $("qManualCar").value.trim();
    var parts = [];
    [state.brand, state.model, state.line, state.trim].forEach(function (v) {
      if (v && parts.indexOf(v) < 0) parts.push(v);
    });
    return parts.join(" ");
  }

  function colorLabel() {
    var parts = [];
    if (state.extColor) parts.push("외장 " + state.extColor.n);
    if (state.intColor) parts.push("내장 " + state.intColor.n);
    return parts.length ? parts.join(" / ") : "미정";
  }

  /* ---------- 2~3단계: 눌러서 고르는 목록 ----------
     data-key 가 붙은 묶음 안의 버튼은 여기서 한꺼번에 처리한다.
     data-multi 가 있으면 여러 개, 없으면 하나만 고른다. */

  root.addEventListener("click", function (e) {
    var b = e.target.closest(".q-chip, .q-card");
    if (!b) return;
    var grp = b.closest("[data-key]");
    if (!grp) return;
    var key = grp.getAttribute("data-key");
    var v = b.getAttribute("data-v");

    if (grp.hasAttribute("data-multi")) {
      var on = !b.classList.contains("is-on");
      press(b, on);
      if (on) state[key].push(v);
      else state[key] = state[key].filter(function (x) { return x !== v; });
    } else {
      Array.prototype.forEach.call(grp.querySelectorAll(".q-chip, .q-card"), function (x) {
        press(x, x === b);
      });
      state[key] = v;
    }
    clearError();
  });

  function addCustom() {
    var inp = $("qKitInput");
    var v = inp.value.trim();
    if (!v) return;
    if (state.kitCustom.indexOf(v) < 0) state.kitCustom.push(v);
    inp.value = "";
    inp.focus();
    renderCustom();
  }

  function renderCustom() {
    var list = $("qKitList");
    list.innerHTML = "";
    state.kitCustom.forEach(function (v) {
      var tag = document.createElement("span");
      tag.className = "q-tag";
      tag.appendChild(document.createTextNode(v));
      var x = document.createElement("button");
      x.type = "button";
      x.setAttribute("aria-label", v + " 삭제");
      x.textContent = "×";
      x.addEventListener("click", function () {
        state.kitCustom = state.kitCustom.filter(function (k) { return k !== v; });
        renderCustom();
      });
      tag.appendChild(x);
      list.appendChild(tag);
    });
  }

  $("qKitAdd").addEventListener("click", addCustom);
  $("qKitInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") { e.preventDefault(); addCustom(); }
  });
  $("qQty").addEventListener("input", updatePrice);

  /* ---------- 단계 이동 ---------- */

  var errBox = $("qError");

  function showError(html) {
    errBox.innerHTML = html;
    errBox.hidden = false;
  }

  function clearError() {
    errBox.hidden = true;
    errBox.innerHTML = "";
  }

  function check(n) {
    if (n === 1) {
      if (!state.brand) return "제조사를 선택해 주세요.";
      if (isManual()) {
        if (!$("qManualCar").value.trim()) return "원하시는 차종을 적어 주세요.";
      } else if (!state.trim) {
        return "차량을 트림까지 선택해 주세요.";
      }
    }
    if (n === 3) {
      if (!state.product) return "상품 종류를 선택해 주세요.";
      if (!state.period) return "계약 기간을 선택해 주세요.";
    }
    return "";
  }

  function go(n) {
    clearError();
    for (var i = state.step; i < n; i++) {
      var err = check(i);
      if (err) { render(i); showError(err); return; }
    }
    render(n);
  }

  function render(n) {
    state.step = n;
    Array.prototype.forEach.call(root.querySelectorAll(".q-step"), function (s) {
      s.hidden = Number(s.getAttribute("data-step")) !== n;
    });
    Array.prototype.forEach.call($("qProg").children, function (li, i) {
      li.classList.toggle("is-done", i + 1 < n);
      li.classList.toggle("is-now", i + 1 === n);
      if (i + 1 === n) li.setAttribute("aria-current", "step");
      else li.removeAttribute("aria-current");
    });
    if (n === STEPS) buildSummary();
    root.scrollIntoView({ block: "start" });
  }

  root.addEventListener("click", function (e) {
    var b = e.target.closest("[data-go]");
    if (b) go(Number(b.getAttribute("data-go")));
  });

  /* ---------- 4단계: 요약과 전송 ---------- */

  function kitAll() { return state.kit.concat(state.kitCustom); }

  // 메일 본문과 화면 요약이 같은 줄을 쓴다
  function rows() {
    var out = [["차량", carLabel() || "-"], ["대수", qty() + "대"]];
    if (!isManual()) {
      out.push(["제조사 옵션", state.opts.length
        ? state.opts.map(function (o) { return o.n + "(+" + won(o.p) + "원)"; }).join(", ") : "없음"]);
      out.push(["색상", colorLabel()]);
      out.push(["예상 차량가", won(unitPrice()) + "원" +
        (qty() > 1 ? " × " + qty() + "대 = " + won(unitPrice() * qty()) + "원" : "")]);
    } else {
      out.push(["예상 차량가", "가격표에 없는 차량 — 확인 후 안내"]);
    }
    out.push(["특장·외주장착", kitAll().length ? kitAll().join(", ") : "없음"]);
    out.push(["구조변경", state.tuning || "미정"]);
    out.push(["상품 종류", state.product || "-"]);
    out.push(["운행 구분", state.usage || "미정"]);
    out.push(["계약 기간", state.period || "-"]);
    out.push(["선납금 / 보증금", (state.prepay || "미정") + " / " + (state.deposit || "미정")]);
    out.push(["연간 주행거리", state.km || "미정"]);
    out.push(["보험 / 정비", (state.insurance || "미정") + " / " + (state.maintenance || "미정")]);
    return out;
  }

  function buildSummary() {
    var box = $("qSummary");
    box.innerHTML = "";
    rows().forEach(function (r) {
      var row = document.createElement("div");
      row.className = "q-sum-row";
      var k = document.createElement("span");
      k.className = "q-sum-k";
      k.textContent = r[0];
      var v = document.createElement("span");
      v.className = "q-sum-v";
      v.textContent = r[1];
      row.appendChild(k);
      row.appendChild(v);
      box.appendChild(row);
    });
  }

  function val(id) { return $(id).value.trim(); }

  function failMessage() {
    return '전송에 실패했습니다. <a href="tel:0269250516">' + TEL +
      "</a>으로 전화 주시면 바로 도와드리겠습니다.";
  }

  var btn = $("qSubmit");

  function setSending(on) {
    btn.disabled = on;
    btn.textContent = on ? "보내는 중" : "견적 요청 보내기";
  }

  $("qForm").addEventListener("submit", function (e) {
    e.preventDefault();
    clearError();

    for (var i = 1; i < STEPS; i++) {
      var err = check(i);
      if (err) { render(i); showError(err); return; }
    }
    if (val("qWebsite") !== "") return;          // 허니팟
    if (!val("qName")) { showError("담당자명을 입력해 주세요."); $("qName").focus(); return; }
    if (val("qPhone").replace(/[^0-9]/g, "").length < 9) {
      showError("연락처를 정확히 입력해 주세요."); $("qPhone").focus(); return;
    }
    if (!$("qAgree").checked) { showError("개인정보 수집·이용에 동의해 주세요."); $("qAgree").focus(); return; }

    setSending(true);

    fetch("/api/quote", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        company: val("qCompany"),
        name: val("qName"),
        phone: val("qPhone"),
        email: val("qEmail"),
        message: val("qMessage"),
        car: carLabel(),
        rows: rows(),
        website: val("qWebsite"),
        agree: true
      })
    })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (body) {
        if (body && body.ok) {
          show("qFlow", false);
          var done = $("qDone");
          done.hidden = false;
          done.setAttribute("tabindex", "-1");
          done.focus();
          root.scrollIntoView({ block: "start" });
          return;
        }
        setSending(false);
        showError(body && body.error && !body.detail ? body.error : failMessage());
      })
      .catch(function () {
        setSending(false);
        showError(failMessage());
      });
  });

  $("qForm").addEventListener("input", clearError);

  /* ---------- 시작 ---------- */

  fillOne("qBrand", null, Object.keys(TRUCK_DATA).concat(MANUAL), pickBrand);

  /* 다른 페이지에서 넘어온 선택 이어받기
     /quote?brand=현대&cat=포터II&model=포터II 특장차&line=냉동탑차&kit=파워게이트
     이름이 가격표와 안 맞으면 거기서 멈추고, 나머지는 직접 고르면 된다. */
  (function prefill() {
    var q = new URLSearchParams(location.search);

    function tap(grpId, text) {
      if (!text) return false;
      var hit = Array.prototype.filter.call($(grpId).children, function (c) {
        return c.firstChild && c.firstChild.nodeValue === text;
      })[0];
      if (!hit) return false;
      hit.click();
      return true;
    }

    (q.get("kit") || "").split(",").forEach(function (k) {
      var b = root.querySelector('[data-key="kit"] [data-v="' + k.trim().replace(/"/g, "") + '"]');
      if (b) b.click();
    });

    if (tap("qBrand", q.get("brand")) && tap("qCat", q.get("cat")) &&
        tap("qModel", q.get("model"))) tap("qLine", q.get("line"));
  })();
})();
