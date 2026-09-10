/**
 * app.js — Client-side logic for Campus Findr (Dark Theme).
 */

document.addEventListener("DOMContentLoaded", () => {

    // =====================================================================
    // 1. SEARCH & FILTER (index page only)
    // =====================================================================
    const searchInput    = document.getElementById("searchInput");
    const filterType     = document.getElementById("filterType");
    const filterStatus   = document.getElementById("filterStatus");
    const filterCategory = document.getElementById("filterCategory");
    const itemGrid       = document.getElementById("itemGrid");
    const emptyState     = document.getElementById("emptyState");

    if (searchInput && itemGrid) {
        let debounceTimer = null;

        const fetchAndRender = () => {
            const params = new URLSearchParams();
            if (searchInput.value.trim())    params.set("q", searchInput.value.trim());
            if (filterType.value)            params.set("type", filterType.value);
            if (filterStatus.value)          params.set("status", filterStatus.value);
            if (filterCategory.value)        params.set("category", filterCategory.value);

            fetch(`/api/items?${params.toString()}`)
                .then(res => res.json())
                .then(items => {
                    if (items.length === 0) {
                        itemGrid.innerHTML = "";
                        emptyState.classList.remove("hidden");
                    } else {
                        emptyState.classList.add("hidden");
                        itemGrid.innerHTML = items.map((item, i) => buildCard(item, i)).join("");
                    }
                })
                .catch(err => console.error("Fetch error:", err));
        };

        searchInput.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(fetchAndRender, 300);
        });

        filterType.addEventListener("change", fetchAndRender);
        filterStatus.addEventListener("change", fetchAndRender);
        filterCategory.addEventListener("change", fetchAndRender);
    }

    /**
     * Build a dark-themed glass card from API data.
     */
    function buildCard(item, index) {
        const categoryEmoji = {
            id_card: "\uD83E\uDEAA", electronics: "\uD83C\uDFA7", keys: "\uD83D\uDD11",
            books: "\uD83D\uDCDA", bottle: "\uD83E\uDDF4", other: "\uD83D\uDCE6"
        };

        const glowColor = item.item_type === "lost" ? "red" : "green";

        const thumbHtml = item.thumbnail_filename
            ? `<div class="h-48 bg-slate-800 overflow-hidden">
                   <img src="/static/uploads/${item.thumbnail_filename}"
                        alt="${escapeHtml(item.title)}"
                        class="w-full h-full object-cover opacity-90 hover:opacity-100 transition">
               </div>`
            : `<div class="h-48 bg-gradient-to-br from-slate-800 to-slate-700 flex items-center justify-center relative overflow-hidden">
                   <div class="absolute w-32 h-32 rounded-full opacity-20 bg-${glowColor}-500 blur-2xl"></div>
                   <span class="text-5xl relative z-10">${categoryEmoji[item.category] || "\uD83D\uDCE6"}</span>
               </div>`;

        const typeBadge = item.item_type === "lost"
            ? `<span class="text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wide bg-red-500/20 text-red-400 border border-red-500/30">lost</span>`
            : `<span class="text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wide bg-green-500/20 text-green-400 border border-green-500/30">found</span>`;

        const statusBadge = item.status === "claimed"
            ? `<span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-600/50 text-gray-400">Claimed</span>`
            : `<span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 badge-open">Open</span>`;

        const dateStr = new Date(item.date_occurred).toLocaleDateString("en-IN", {
            day: "2-digit", month: "short", year: "numeric"
        });

        const delay = Math.min(index + 1, 6);

        return `
        <a href="/item/${item.id}"
           class="item-card glass rounded-2xl overflow-hidden flex flex-col animate-in delay-${delay}">
            ${thumbHtml}
            <div class="p-4 flex-1 flex flex-col">
                <div class="flex items-center gap-2 mb-2.5">
                    ${typeBadge}${statusBadge}
                </div>
                <h3 class="font-semibold text-white text-base leading-snug line-clamp-2">
                    ${escapeHtml(item.title)}
                </h3>
                <p class="text-sm text-gray-400 mt-1.5 flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5 text-purple-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
                    </svg>
                    ${escapeHtml(item.location)}
                </p>
                <p class="text-xs text-gray-500 mt-auto pt-3">${dateStr}</p>
            </div>
        </a>`;
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // =====================================================================
    // 2. IMAGE PREVIEW
    // =====================================================================
    const photoInput        = document.getElementById("photoInput");
    const imagePreview      = document.getElementById("imagePreview");
    const uploadPlaceholder = document.getElementById("uploadPlaceholder");

    if (photoInput && imagePreview) {
        photoInput.addEventListener("change", () => {
            const file = photoInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = e => {
                    imagePreview.src = e.target.result;
                    imagePreview.classList.remove("hidden");
                    if (uploadPlaceholder) uploadPlaceholder.classList.add("hidden");
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // =====================================================================
    // 3. CONDITIONAL DEPOSIT_LOCATION FIELD
    // =====================================================================
    const typeRadios   = document.querySelectorAll('input[name="item_type"]');
    const depositField = document.getElementById("depositField");

    if (typeRadios.length && depositField) {
        typeRadios.forEach(radio => {
            radio.addEventListener("change", () => {
                if (radio.value === "found" && radio.checked) {
                    depositField.classList.remove("hidden");
                } else if (radio.value === "lost" && radio.checked) {
                    depositField.classList.add("hidden");
                }
            });
        });
    }

    // =====================================================================
    // 4. CLAIM FORM TOGGLE
    // =====================================================================
    const claimToggle  = document.getElementById("claimToggle");
    const claimSection = document.getElementById("claimSection");

    if (claimToggle && claimSection) {
        claimToggle.addEventListener("click", () => {
            claimSection.classList.toggle("open");
            if (claimSection.classList.contains("open")) {
                setTimeout(() => claimSection.scrollIntoView({ behavior: "smooth", block: "nearest" }), 100);
            }
        });
    }

    // =====================================================================
    // 5. CHARACTER COUNTER
    // =====================================================================
    const descTextarea = document.getElementById("description");
    const charCount    = document.getElementById("charCount");

    if (descTextarea && charCount) {
        descTextarea.addEventListener("input", () => {
            charCount.textContent = descTextarea.value.length;
        });
    }

});
