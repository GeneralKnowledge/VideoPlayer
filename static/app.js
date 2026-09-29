const form = document.getElementById("search-form");
const resultsEl = document.getElementById("results");
const statusEl = document.getElementById("status");
const dialog = document.getElementById("detail");
const detailBody = document.getElementById("detail-body");

function setStatus(message, show = true) {
  statusEl.hidden = !show;
  statusEl.textContent = message || "";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function posterMarkup(item) {
  if (item.poster) {
    return `<img src="${escapeHtml(item.poster)}" alt="" loading="lazy" />`;
  }
  return `<div class="poster-fallback" aria-hidden="true">No poster</div>`;
}

function renderResults(items) {
  resultsEl.innerHTML = "";

  if (!items.length) {
    setStatus("No titles matched that search.");
    return;
  }

  setStatus(`${items.length} result${items.length === 1 ? "" : "s"}`);

  items.forEach((item, index) => {
    const li = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "result";
    button.style.animationDelay = `${Math.min(index * 0.04, 0.4)}s`;
    button.innerHTML = `
      ${posterMarkup(item)}
      <div class="meta">
        <h2>${escapeHtml(item.title)}</h2>
        <p>${escapeHtml(item.year || "—")} · ${escapeHtml(item.media_type)}</p>
      </div>
      <span class="chip">${escapeHtml(item.media_type)}</span>
    `;
    button.addEventListener("click", () => openDetail(item));
    li.appendChild(button);
    resultsEl.appendChild(li);
  });
}

function openDetail(item) {
  const rating =
    typeof item.rating === "number" && item.rating > 0
      ? `${item.rating.toFixed(1)} / 10`
      : "Unrated";

  detailBody.innerHTML = `
    <div class="detail-layout">
      ${posterMarkup(item)}
      <div>
        <h2>${escapeHtml(item.title)}</h2>
        <p class="sub">${escapeHtml(item.year || "—")} · ${escapeHtml(
          item.media_type
        )} · ${escapeHtml(rating)}</p>
        <p class="overview">${escapeHtml(
          item.overview || "No overview available."
        )}</p>
        ${
          item.embed_url
            ? `<div class="embed-box">
                <label for="embed-url">Fictional embed URL</label>
                <div class="embed-row">
                  <input id="embed-url" readonly value="${escapeHtml(
                    item.embed_url
                  )}" />
                  <button type="button" id="copy-embed">Copy</button>
                </div>
                <p class="note">Demo path only — points at embed.example.invalid.</p>
              </div>`
            : ""
        }
      </div>
    </div>
  `;

  const copyBtn = detailBody.querySelector("#copy-embed");
  const input = detailBody.querySelector("#embed-url");
  if (copyBtn && input) {
    copyBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(input.value);
        copyBtn.textContent = "Copied";
        copyBtn.classList.add("copied");
        setTimeout(() => {
          copyBtn.textContent = "Copy";
          copyBtn.classList.remove("copied");
        }, 1400);
      } catch {
        input.select();
      }
    });
  }

  if (typeof dialog.showModal === "function") {
    dialog.showModal();
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const q = new FormData(form).get("q")?.toString().trim() || "";
  const type =
    form.querySelector('input[name="type"]:checked')?.value || "multi";

  if (!q) {
    setStatus("Enter a title to search.");
    resultsEl.innerHTML = "";
    return;
  }

  setStatus("Searching…");
  resultsEl.innerHTML = "";

  try {
    const response = await fetch(
      `/api/search?q=${encodeURIComponent(q)}&type=${encodeURIComponent(type)}`
    );
    const data = await response.json();

    if (!response.ok) {
      setStatus(data.error || "Search failed.");
      return;
    }

    renderResults(data.results || []);
  } catch {
    setStatus("Network error while searching.");
  }
});
