import re
import streamlit as st
import requests

from assets.theme import inject_global_css, page_hero

# ─────────────────────────────────────────────
# Page config + shared theme
# ─────────────────────────────────────────────
st.set_page_config(page_title="Jio Plans", page_icon="📶", layout="wide")
inject_global_css()

# ── Jio-specific styles ───────────────────────
st.markdown("""
<style>
.plan-card {
    background: linear-gradient(145deg, #111827, #1a2234);
    border: 1px solid #1f2d44;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    position: relative;
    transition: transform 0.2s ease, border-color 0.2s ease;
    overflow: hidden;
}
.plan-card:hover { transform: translateY(-2px); border-color: #4a9eff55; }
.plan-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #4a9eff, #a855f7, #f472b6);
    opacity: 0.7;
}
.price-badge {
    display: inline-block;
    background: linear-gradient(135deg, #4a9eff22, #a855f722);
    border: 1px solid #4a9eff44;
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 22px; font-weight: 800; color: #e2eaff;
    letter-spacing: -0.5px; margin-bottom: 10px;
}
.rupee { font-size: 14px; color: #a0aec0; margin-right: 2px; }
.specs-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
.spec-pill {
    background: #1e2d47; border-radius: 8px; padding: 5px 10px;
    font-size: 12px; font-weight: 600; color: #cbd5e1;
    display: flex; align-items: center; gap: 4px;
}
.spec-pill .label { color: #64748b; font-weight: 500; }
.spec-pill .value { color: #e2eaff; }
.ott-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.ott-chip {
    background: #0f172a; border: 1px solid #334155; border-radius: 6px;
    padding: 3px 8px; font-size: 11px; color: #94a3b8; font-weight: 500;
}
.plan-badge {
    position: absolute; top: 14px; right: 14px;
    background: linear-gradient(135deg, #f59e0b, #ef4444);
    color: white; font-size: 10px; font-weight: 700;
    padding: 3px 8px; border-radius: 100px; letter-spacing: 0.5px;
    text-transform: uppercase;
}
.note-item {
    background: #0f172a; border-left: 3px solid #4a9eff44;
    border-radius: 0 8px 8px 0; padding: 6px 10px;
    font-size: 11px; color: #64748b; margin-top: 6px; line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)



# ─────────────────────────────────────────────
# Data fetching (cached 15 min)
# ─────────────────────────────────────────────
@st.cache_data(ttl=900)
def fetch_jio_plans():
    url = "https://www.jio.com/api/jio-mdmdata-service/mdmdata/recharge/plans"
    params = {"productType": "MOBILITY", "billingType": "1"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _safe_int(val, fallback=0):
    """Convert val to int, returning fallback for non-numeric strings like 'Calendar'."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return fallback


def parse_plans(data):
    """Flatten all plans from categories → subcategories → plans."""
    plans = []
    for cat in data.get("planCategories", []):
        cat_name = cat.get("type", "Other")
        for sub in cat.get("subCategories", []):
            sub_name = sub.get("type", "")
            for plan in sub.get("plans", []):
                fk = plan.get("filterKeys", {})
                misc = plan.get("misc", {})
                prime = plan.get("primeData", {})
                details = {d["header"]: d["value"] for d in misc.get("details", []) if "header" in d and "value" in d}

                # OTT list
                ott_raw = fk.get("ott", "")
                ott_list = [o.strip() for o in ott_raw.split(",") if o.strip()] if ott_raw else []

                # Notes — strip HTML tags
                notes_raw = misc.get("notes", [])
                notes = [re.sub(r"<[^>]+>", "", n).strip() for n in notes_raw if n.strip()]

                plans.append({
                    "id": plan.get("id"),
                    "category": cat_name,
                    "sub_category": sub_name,
                    "price": _safe_int(fk.get("price", plan.get("amount", 0))),
                    "validity_days": _safe_int(fk.get("validity", 0)),
                    "data_per_day": fk.get("data", ""),       # GB/Day numeric string
                    "ott": ott_list,
                    "voice": details.get("Voice", ""),
                    "sms": details.get("SMS", ""),
                    "total_data": details.get("Total data", ""),
                    "description": plan.get("description", ""),
                    "notes": notes,
                    "badge_theme": plan.get("badgeData", {}).get("cardTheme", ""),
                    "subscriptions": [s.get("title", "") for s in misc.get("subscriptions", [])],
                    "is_5g": "true5g" in ott_raw.lower(),
                    "is_popular": cat_name == "Popular Plans",
                })
    return plans


def build_plan_card_html(p):
    badge_html = ""
    badge_labels = []
    if p["is_popular"]:
        badge_labels.append("⭐ Popular")
    if p["is_5g"]:
        badge_labels.append("5G")
    if badge_labels:
        badge_html = f'<div class="plan-badge">{" • ".join(badge_labels)}</div>'

    # Spec pills
    specs = []
    if p["data_per_day"]:
        specs.append(("📡", "Data", f"{p['data_per_day']} GB/Day"))
    if p["validity_days"]:
        specs.append(("📅", "Validity", f"{p['validity_days']} Days"))
    if p["voice"]:
        specs.append(("📞", "Calls", p["voice"]))
    if p["sms"]:
        specs.append(("💬", "SMS", p["sms"]))
    if p["total_data"]:
        specs.append(("🗄️", "Total", p["total_data"]))

    pills_html = "".join(
        f'<div class="spec-pill"><span class="label">{icon} {lbl}</span>&nbsp;<span class="value">{val}</span></div>'
        for icon, lbl, val in specs
    )

    # OTT chips
    ott_html = ""
    if p["subscriptions"]:
        chips = "".join(f'<div class="ott-chip">{s}</div>' for s in p["subscriptions"])
        ott_html = f'<div class="ott-row">{chips}</div>'

    # Notes (first 2 only, to keep cards compact)
    notes_html = ""
    for note in p["notes"][:2]:
        if note:
            notes_html += f'<div class="note-item">{note[:180]}{"…" if len(note) > 180 else ""}</div>'

    return (
        '<div class="plan-card">'
        + badge_html
        + f'<div class="price-badge"><span class="rupee">₹</span>{p["price"]}</div>'
        + f'<div class="specs-row">{pills_html}</div>'
        + ott_html
        + notes_html
        + '</div>'
    )


# ─────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────
# Hero header
st.markdown("""
<div style="padding: 8px 0 24px 0;">
    <h1 style="font-size:2.2rem; font-weight:800; color:#e2eaff; margin:0; letter-spacing:-1px;">
        📶 Jio Recharge Plans
    </h1>
    <p style="color:#64748b; margin:6px 0 0 0; font-size:14px;">
        Live data from Jio API • Prepaid Mobility Plans
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch data
with st.spinner("Fetching latest plans from Jio…"):
    try:
        raw = fetch_jio_plans()
    except Exception as e:
        st.error(f"❌ Failed to fetch plans: {e}")
        st.stop()

all_plans = parse_plans(raw)

if not all_plans:
    st.warning("No plans found in API response.")
    st.stop()

# ── Metrics row ──
prices = [p["price"] for p in all_plans if p["price"]]
validities = [p["validity_days"] for p in all_plans if p["validity_days"]]
categories = sorted(set(p["category"] for p in all_plans))

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-box"><div class="m-val">{len(all_plans)}</div><div class="m-lbl">Total Plans</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-box"><div class="m-val">₹{min(prices)}</div><div class="m-lbl">Lowest Price</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-box"><div class="m-val">₹{max(prices)}</div><div class="m-lbl">Highest Price</div></div>', unsafe_allow_html=True)
with m4:
    five_g_count = sum(1 for p in all_plans if p["is_5g"])
    st.markdown(f'<div class="metric-box"><div class="m-val">{five_g_count}</div><div class="m-lbl">5G Plans</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Filters ──
with st.expander("🔧 Filters", expanded=True):
    fc1, fc2, fc3, fc4, fc5 = st.columns([2, 2, 2, 2, 1])
    with fc1:
        selected_cats = st.multiselect("Category", categories, placeholder="All categories")
    with fc2:
        price_min, price_max = st.slider("Price range (₹)", min(prices), max(prices), (min(prices), max(prices)), step=10)
    with fc3:
        all_vals = sorted(set(p["validity_days"] for p in all_plans if p["validity_days"]))
        if len(all_vals) > 1:
            valid_range = st.select_slider("Validity (days)", options=all_vals, value=(all_vals[0], all_vals[-1]))
        else:
            val = all_vals[0] if all_vals else 0
            st.caption(f"Validity: {val} days")
            valid_range = (val, val)
    with fc4:
        sort_by = st.selectbox("Sort by", ["Price ↑", "Price ↓", "Validity ↑", "Validity ↓", "Data/Day ↓"])
    with fc5:
        only_5g = st.toggle("5G only", False)
        only_popular = st.toggle("Popular", False)

# ── Apply filters ──
filtered = all_plans[:]

if selected_cats:
    filtered = [p for p in filtered if p["category"] in selected_cats]
if only_5g:
    filtered = [p for p in filtered if p["is_5g"]]
if only_popular:
    filtered = [p for p in filtered if p["is_popular"]]

filtered = [p for p in filtered if price_min <= p["price"] <= price_max]
filtered = [p for p in filtered if valid_range[0] <= p["validity_days"] <= valid_range[1]]

# Sort
sort_map = {
    "Price ↑": (lambda p: p["price"], False),
    "Price ↓": (lambda p: p["price"], True),
    "Validity ↑": (lambda p: p["validity_days"], False),
    "Validity ↓": (lambda p: p["validity_days"], True),
    "Data/Day ↓": (lambda p: float(p["data_per_day"]) if p["data_per_day"] else 0, True),
}
key_fn, reverse = sort_map[sort_by]
filtered.sort(key=key_fn, reverse=reverse)

# ── Results summary ──
st.markdown(f"<p style='color:#64748b; font-size:13px; margin-bottom:16px;'>Showing <b style='color:#e2eaff'>{len(filtered)}</b> of {len(all_plans)} plans</p>", unsafe_allow_html=True)

if not filtered:
    st.info("No plans match your filters.")
    st.stop()

# ── Group by category — render all cards in one HTML block per category ──
from collections import defaultdict
by_cat = defaultdict(list)
for p in filtered:
    by_cat[p["category"]].append(p)

for cat_name, cat_plans in by_cat.items():
    st.markdown(f'<div class="section-header">{cat_name} &nbsp;·&nbsp; {len(cat_plans)} plans</div>', unsafe_allow_html=True)

    # Build a 3-column CSS grid in one markdown call (avoids column iframe scoping)
    cards_html = '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 8px;">'
    for plan in cat_plans:
        cards_html += build_plan_card_html(plan)
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

