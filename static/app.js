/* Foodify main page. Loaded as a module, so top-level "await" works. */
const $ = id => document.getElementById(id);

async function getJSON(url, options) {
  const res = await fetch(url, options);
  if (res.status === 401) {
    window.location.href = "/login.html";
    throw new Error("Not logged in");
  }
  return res.json();
}

// Makes text safe to put inside innerHTML (turns < > & " ' into harmless codes).
const esc = text => String(text).replace(/[&<>"']/g, c => "&#" + c.charCodeAt(0) + ";");

/* ---------- Load data from the server ---------- */
const me = await getJSON("/api/me");
$("welcome").textContent = "Welcome, " + me.name + "!";

const foods = await getJSON("/api/foods");
const find = id => foods.find(f => f.id === id);

/* ---------- Tabs ---------- */
const tabs = document.querySelectorAll(".tab");
const sections = document.querySelectorAll("main section");

function showTab(name) {
  sections.forEach(s => s.classList.toggle("active", s.id === name));
  tabs.forEach(t => t.classList.toggle("on", t.dataset.tab === name));
}

tabs.forEach(t => t.addEventListener("click", () => showTab(t.dataset.tab)));
showTab("scan");

/* ---------- Nutrition bars (used by every tab) ---------- */
const nutrients = [
  { key: "kcal",    label: "Calories", unit: "kcal", daily: 2000 },
  { key: "protein", label: "Protein",  unit: "g",    daily: 50 },
  { key: "carbs",   label: "Carbs",    unit: "g",    daily: 275 },
  { key: "fat",     label: "Fat",      unit: "g",    daily: 78 },
  { key: "fiber",   label: "Fibre",    unit: "g",    daily: 28 },
  { key: "sugar",   label: "Sugar",    unit: "g",    daily: 50 },
  { key: "sodium",  label: "Sodium",   unit: "mg",   daily: 2300 }
];

// values looks like { kcal: 95, protein: 0.5, ... }. The bar shows a share of the daily reference.
function bars(values) {
  return nutrients.map(n => {
    const value = Math.round(values[n.key] * 10) / 10;
    const percent = Math.min(100, value / n.daily * 100);
    return `
      <div class="row">
        <span>${n.label}</span>
        <div class="track"><div class="fill" style="width: ${percent}%"></div></div>
        <b>${value} ${n.unit}</b>
      </div>`;
  }).join("");
}

/* ---------- Foods tab: search, portion calculator, history ---------- */
const HINT = "<p>Type a food name above.</p>";
let selected = null;

const card = f => `
  <article class="card" data-id="${esc(f.id)}">
    <h3>${esc(f.emoji)} ${esc(f.name)}</h3>
    <p>${esc(f.serving)}: ${f.kcal} kcal. Tap for details.</p>
  </article>`;

function showBars() {
  const grams = Number($("grams").value);
  if (!grams || grams < 1 || grams > 2000) {
    $("bars").innerHTML = "<p>Enter 1 to 2000 grams.</p>";
    return;
  }
  const factor = grams / selected.grams;   // eating half the serving gives half of everything
  const values = {};
  nutrients.forEach(n => values[n.key] = selected[n.key] * factor);
  $("bars").innerHTML = bars(values);
}

async function loadRecent() {
  const list = await getJSON("/api/history");
  $("recent").innerHTML = list.length === 0 ? "" :
    "<h3>Recently viewed</h3><p>" + list.map(h => esc(h.emoji) + " " + esc(h.name)).join(", ") + "</p>";
}

function selectFood(id) {
  selected = find(id);
  $("detail").innerHTML = `
    <h3>${esc(selected.emoji)} ${esc(selected.name)}</h3>
    <label for="grams">How many grams did you eat?</label>
    <input id="grams" type="number" min="1" max="2000" value="${selected.grams}">
    <p><small>Share of a typical adult's daily reference. Source: ${esc(selected.source)}.</small></p>
    <div id="bars"></div>`;
  $("grams").addEventListener("input", showBars);
  showBars();

  getJSON("/api/history", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ food_id: id })
  }).then(loadRecent);
}

$("search").addEventListener("input", () => {
  $("detail").innerHTML = "";
  const query = $("search").value.trim().toLowerCase();
  if (query === "") {
    $("results").innerHTML = HINT;
    return;
  }
  const matches = foods.filter(f => f.name.toLowerCase().includes(query)).slice(0, 8);
  $("results").innerHTML = matches.length ? matches.map(card).join("") : "<p>No food found. Try another name.</p>";
});

$("results").addEventListener("click", e => {
  const clicked = e.target.closest(".card");
  if (clicked) {
    selectFood(clicked.dataset.id);
  }
});

$("results").innerHTML = HINT;
loadRecent();

/* ---------- Compare tab ---------- */
const options = foods.map(f => `<option value="${esc(f.id)}">${esc(f.emoji)} ${esc(f.name)}</option>`).join("");
$("foodA").innerHTML = options;
$("foodB").innerHTML = options;
$("foodA").value = "chips";
$("foodB").value = "makhana";

function compare() {
  const a = find($("foodA").value);
  const b = find($("foodB").value);
  if (a === b) {
    $("compareResult").innerHTML = "<p>Pick two different foods.</p>";
    return;
  }
  const rows = nutrients.map(n =>
    `<tr><td>${n.label}</td><td>${a[n.key]} ${n.unit}</td><td>${b[n.key]} ${n.unit}</td></tr>`).join("");
  const notes = nutrients.filter(n => a[n.key] !== b[n.key]).map(n => {
    const more = a[n.key] > b[n.key] ? a : b;
    return `<p class="note">${esc(more.name)} has more ${n.label.toLowerCase()}.</p>`;
  }).join("");
  $("compareResult").innerHTML = `
    <table>
      <tr><th></th><th>${esc(a.emoji)} ${esc(a.name)}</th><th>${esc(b.emoji)} ${esc(b.name)}</th></tr>
      ${rows}
    </table>
    ${notes}`;
}

$("foodA").addEventListener("change", compare);
$("foodB").addEventListener("change", compare);
compare();

/* ---------- Build a meal tab ---------- */
const groups = { veg: "Vegetables", fruit: "Fruit", grain: "Grains", protein: "Protein", dairy: "Dairy" };
const plate = new Set();   // a Set holds each food only once

$("mealChips").innerHTML = foods.map(f =>
  `<button type="button" class="chip" data-id="${esc(f.id)}">${esc(f.emoji)} ${esc(f.name)}</button>`).join("");

function showMeal() {
  const items = Array.from(plate).map(find);
  if (items.length === 0) {
    $("mealResult").innerHTML = "<p>Your plate is empty. Tap a food above.</p>";
    return;
  }
  const totals = {};
  nutrients.forEach(n => totals[n.key] = items.reduce((sum, f) => sum + f[n.key], 0));

  const have = new Set(items.map(f => f.group));
  const missing = Object.keys(groups).filter(g => !have.has(g)).map(g => groups[g]);
  const message = missing.length === 0 ? "All 5 food groups are on your plate!"
                                       : "Missing food groups: " + missing.join(", ") + ".";

  $("mealResult").innerHTML = bars(totals) + `<p class="note">${message}</p>`;
}

$("mealChips").addEventListener("click", e => {
  const chip = e.target.closest(".chip");
  if (!chip) {
    return;
  }
  const id = chip.dataset.id;
  if (plate.has(id)) {
    plate.delete(id);
  } else {
    plate.add(id);
  }
  chip.classList.toggle("on", plate.has(id));
  showMeal();
});

showMeal();
