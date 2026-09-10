/**
 * app.js — Client-side logic for Campus Findr.
 *
 * Handles:
 *  1. Live search & filter via the /api/items JSON endpoint
 *  2. Image preview on file upload
 *  3. Conditional deposit_location field toggle
 *  4. Claim form expand/collapse
 *  5. Description character counter
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
                        itemGrid.innerHTML = items.map(item => buildCard(item)).join("");
                    }
                })
                .catch(err => console.error("Fetch error:", err));
        };

        // Debounced search input
        searchInput.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(fetchAndRender, 300);
        });

        // Instant filter on dropdown change
        filterType.addEventListener("change", fetchAndRender);
        filterStatus.addEventListener("change", fetchAndRender);
        filterCategory.addEventListener("change", fetchAndRender);
    }

    /**
     * Build an item card HTML string from an API item object.
     */
    function buildCard(item) {
        const categoryEmoji = {
            id_card: "🪪", electronics: "🎧", keys: "🔑",
            books: "📚", bottle: "🧴", other: "📦"
        };

        const thumbHtml = item.thumbnail_filename
            ? `<div class="h-44 bg-gray-100 overflow-hidden">
                   <img src="/static/uploads/${item.thumbnail_filename}"
                        alt="${escapeHtml(item.title)}"
                        class="w-full h-full object-cover">
               </div>`
            : `<div class="h-44 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                   <span class="text-5xl opacity-40">${categoryEmoji[item.category] || "📦"}</span>
               </div>`;

        const typeBadge = item.item_type === "lost"
            ? `<span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-red-100 text-red-700">LOST</span>`
            : `<span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-green-100 text-green-700">FOUND</span>`;

        const statusBadge = item.status === "claimed"
            ? `<span class="text-xs font-medium px-2 py-0.5 rounded-full bg-gray-200 text-gray-600">Claimed</span>`
            : `<span class="text-xs font-medium px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 badge-open">Open</span>`;

        const dateStr = new Date(item.date_occurred).toLocaleDateString("en-IN", {
            day: "2-digit", month: "short", year: "numeric"
        });

        return `
        <a href="/item/${item.id}"
           class="item-card bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:border-primary/30">
            ${thumbHtml}
            <div class="p-4 flex-1 flex flex-col">
                <div class="flex items-center gap-2 mb-2">
                    ${typeBadge}${statusBadge}
                </div>
                <h3 class="font-semibold text-gray-900 text-base leading-snug line-clamp-2">
                    ${escapeHtml(item.title)}
                </h3>
                <p class="text-sm text-gray-500 mt-1 flex items-center gap-1">
                    <span>📍</span> ${escapeHtml(item.location)}
                </p>
                <p class="text-xs text-gray-400 mt-auto pt-3">${dateStr}</p>
            </div>
        </a>`;
    }

    /** Simple HTML escape to prevent XSS in dynamic content. */
    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }


    // =====================================================================
    // 2. IMAGE PREVIEW (report page)
    // =====================================================================
    const photoInput     = document.getElementById("photoInput");
    const imagePreview   = document.getElementById("imagePreview");
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
    // 3. CONDITIONAL DEPOSIT_LOCATION FIELD (report page)
    // =====================================================================
    const typeRadios  = document.querySelectorAll('input[name="item_type"]');
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
    // 4. CLAIM FORM TOGGLE (item_detail page)
    // =====================================================================
    const claimToggle  = document.getElementById("claimToggle");
    const claimSection = document.getElementById("claimSection");

    if (claimToggle && claimSection) {
        claimToggle.addEventListener("click", () => {
            claimSection.classList.toggle("open");
            // Scroll into view when opening
            if (claimSection.classList.contains("open")) {
                setTimeout(() => claimSection.scrollIntoView({ behavior: "smooth", block: "nearest" }), 100);
            }
        });
    }


    // =====================================================================
    // 5. DESCRIPTION CHARACTER COUNTER (report page)
    // =====================================================================
    const descTextarea = document.getElementById("description");
    const charCount    = document.getElementById("charCount");

    if (descTextarea && charCount) {
        descTextarea.addEventListener("input", () => {
            charCount.textContent = descTextarea.value.length;
        });
    }

});
