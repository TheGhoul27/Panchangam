const CITY_OPTIONS = [
  "Atlanta, USA",
  "Chicago, USA",
  "Houston, USA",
  "New Jersey, USA",
  "New York, USA",
  "Toronto, Ontario, Canada",
  "London, UK",
  "Edinburgh, UK",
  "Sydney, Australia",
  "Melbourne, Australia",
  "Perth, Australia",
  "Durban, South Africa",
  "Cape Town, South Africa",
  "Munich, Germany",
  "Singapore, Singapore",
  "Kuala Lumpur, Malaysia",
  "Dubai, UAE",
  "Bangkok, Thailand",
  "Hongkong, China",
  "Riyadh, Saudi Arabia",
  "Doha, Qatar",
  "Kuwait City, Kuwait",
  "Hamilton, New Zealand",
  "Auckland, New Zealand"
];

const sections = {
  panchangam: ["samvatsara", "ayana", "ruthu", "masa", "paksham", "tithi", "vasara", "nakshatram", "yogam", "karanam"],
  avoid: ["rahukalam", "yamagandam", "varjyam", "gulika"],
  good: ["amritakalam", "abhijit_muhurtham"]
};

const els = {
  city: document.getElementById("cityInput"),
  date: document.getElementById("dateInput"),
  mode: document.getElementById("modeInput"),
  loadBtn: document.getElementById("loadBtn"),
  status: document.getElementById("status"),
  title: document.getElementById("title"),
  details: document.getElementById("details"),
  panchangamTable: document.getElementById("panchangamTable"),
  avoidTable: document.getElementById("avoidTable"),
  goodTable: document.getElementById("goodTable")
};

let manifest = null;

function normalizeCity(displayCity) {
  const firstPart = displayCity.split(",")[0];
  return firstPart.replace(/\b[Cc]ity\b/g, "").trim().replace(/\s+/g, "+");
}

function humanize(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
}

function setStatus(message, type = "ok") {
  els.status.className = `status ${type}`;
  els.status.textContent = message;
}

async function loadManifest() {
  if (manifest) return manifest;
  const res = await fetch("data/manifest.json", { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Failed to load snapshot manifest.");
  }
  manifest = await res.json();
  return manifest;
}

function tableRows(keys, data) {
  return keys
    .map((key) => {
      const value = data[key] ?? "-";
      return `<tr><th>${humanize(key)}</th><td>${value}</td></tr>`;
    })
    .join("");
}

function renderData(data) {
  els.title.textContent = data.title || "Panchangam";
  els.details.textContent = data.details || "";
  els.panchangamTable.innerHTML = tableRows(sections.panchangam, data);
  els.avoidTable.innerHTML = tableRows(sections.avoid, data);
  els.goodTable.innerHTML = tableRows(sections.good, data);
}

async function loadSnapshotData(date, city) {
  const currentManifest = await loadManifest();
  const filePath = currentManifest?.index?.[city]?.[date];
  if (!filePath) {
    throw new Error(`No prebuilt snapshot for ${city} on ${date}.`);
  }

  const res = await fetch(filePath, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Could not load snapshot file: ${filePath}`);
  }

  return res.json();
}

function htmlToData(html, cityToken) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");
  const allVals = Array.from(doc.querySelectorAll("td")).map((td) => td.textContent.trim());

  if (!allVals.length) {
    throw new Error("Live scrape returned no table cells. Possible CORS block or HTML shape change.");
  }

  const title = (allVals[0] || "").replace("Today's ", "").trim();
  const col1 = ["Samvatsara"];
  const col2 = ["Unknown Samvatsara"];

  let skip = 0;
  for (let i = 1; i < allVals.length; i += 1) {
    const val = allVals[i];
    if (["Panchangam", "Time to Avoid (Bad time to start any important work)", "Good Time (to start any important work)"].includes(val)) {
      continue;
    }
    if (skip % 2 !== 0) {
      col2.push(val);
    } else {
      col1.push(val);
    }
    skip += 1;
  }

  const map = { title };
  for (let i = 0; i < Math.min(col1.length, col2.length); i += 1) {
    const key = col1[i].trim().replace(/\s+/g, "_").toLowerCase();
    map[key] = col2[i];
  }

  const cityName = cityToken.replace(/\+/g, " ");
  const details = [
    `City: ${map.city || cityName}`,
    `Sunrise: ${map.sunrise || "n/a"}`,
    `Sunset: ${map.sunset || "n/a"}`
  ].join(", ");

  map.details = details;
  delete map.city;
  delete map.sunrise;
  delete map.sunset;
  return map;
}

async function loadLiveData(date, city, proxyMode) {
  const target = `https://www.panchangam.org/global/daily.php?city=${city}&date=${date}`;
  let url = target;

  if (proxyMode === "proxy") {
    url = `https://api.allorigins.win/raw?url=${encodeURIComponent(target)}`;
  }

  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Live request failed with status ${res.status}`);
  }

  const html = await res.text();
  return htmlToData(html, city);
}

async function onLoadClick() {
  const date = els.date.value;
  const city = normalizeCity(els.city.value || "New York, USA");
  const mode = els.mode.value;

  if (!date) {
    setStatus("Select a date first.", "warn");
    return;
  }

  try {
    setStatus("Loading...", "ok");
    let data;
    if (mode === "snapshot") {
      data = await loadSnapshotData(date, city);
      setStatus(`Loaded snapshot for ${city} on ${date}.`, "ok");
    } else if (mode === "live-direct") {
      data = await loadLiveData(date, city, "direct");
      setStatus("Loaded via direct live scrape (CORS permitted).", "ok");
    } else {
      data = await loadLiveData(date, city, "proxy");
      setStatus("Loaded via CORS proxy live scrape.", "warn");
    }
    renderData(data);
  } catch (err) {
    setStatus(`${err.message} Falling back to snapshot mode if available.`, "error");
    if (mode !== "snapshot") {
      try {
        const fallbackData = await loadSnapshotData(date, city);
        renderData(fallbackData);
      } catch (fallbackErr) {
        setStatus(`${err.message} Also failed fallback: ${fallbackErr.message}`, "error");
      }
    }
  }
}

async function initForm() {
  CITY_OPTIONS.forEach((city) => {
    const opt = document.createElement("option");
    opt.value = city;
    opt.textContent = city;
    if (city === "New York, USA") {
      opt.selected = true;
    }
    els.city.appendChild(opt);
  });

  const today = new Date().toISOString().slice(0, 10);
  els.date.value = today;

  try {
    const currentManifest = await loadManifest();
    const cityToken = normalizeCity(els.city.value);
    const cityDates = Object.keys(currentManifest?.index?.[cityToken] || {});
    if (cityDates.length && !cityDates.includes(today)) {
      els.date.value = cityDates[0];
      setStatus(`Defaulted date to available snapshot: ${cityDates[0]}.`, "warn");
    }
  } catch (err) {
    setStatus("Manifest unavailable on load; live mode may still work.", "warn");
  }

  els.loadBtn.addEventListener("click", onLoadClick);
}

initForm();
