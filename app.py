"""
Gratitude Fest — Streamlit Cloud Demo
--------------------------------------
A fully self-contained demo of the Gratitude Fest app.
All Snowflake dependencies replaced with synthetic in-memory data.
No external links, no PII, no database required.
"""

import json
import random
import re
import uuid
from datetime import datetime

import streamlit as st

# ─────────────────────────────────────────────
# Synthetic data
# ─────────────────────────────────────────────

SYNTHETIC_DONORS = [
    {
        "FEST_QUEUE_ID": "Q001",
        "ACCOUNT_NAME": "Alice Pemberton",
        "PHONE_NUMBER": "5125550101",
        "ADDRESS_ENVELOPE_TO": "ALICE PEMBERTON",
        "ADDRESS_CARD_TO": "THE PEMBERTON FAMILY",
        "MAILING_STREET": "123 Maple Ave",
        "MAILING_STREET_2": "",
        "MAILING_CITY": "Nashville",
        "MAILING_STATE": "TN",
        "MAILING_POSTAL_CODE": "37201",
        "PLEDGE_COMMENT": "Alice called in during the morning show and said listening while commuting changed her life.",
    },
    {
        "FEST_QUEUE_ID": "Q002",
        "ACCOUNT_NAME": "Robert & Diane Okoye",
        "PHONE_NUMBER": "6155550234",
        "ADDRESS_ENVELOPE_TO": "ROBERT AND DIANE OKOYE",
        "ADDRESS_CARD_TO": "THE OKOYE FAMILY",
        "MAILING_STREET": "456 Oak Street",
        "MAILING_STREET_2": "Apt 12",
        "MAILING_CITY": "Franklin",
        "MAILING_STATE": "TN",
        "MAILING_POSTAL_CODE": "37064",
        "PLEDGE_COMMENT": "",
    },
    {
        "FEST_QUEUE_ID": "Q003",
        "ACCOUNT_NAME": "Margaret VanDyke",
        "PHONE_NUMBER": "9015550345",
        "ADDRESS_ENVELOPE_TO": "MARGARET VANDYKE",
        "ADDRESS_CARD_TO": "MRS. MARGARET VANDYKE",
        "MAILING_STREET": "789 Birch Lane",
        "MAILING_STREET_2": "",
        "MAILING_CITY": "Memphis",
        "MAILING_STATE": "TN",
        "MAILING_POSTAL_CODE": "38103",
        "PLEDGE_COMMENT": "Margaret is a long-time supporter and mentioned her late husband used to listen every Sunday.",
    },
    {
        "FEST_QUEUE_ID": "Q004",
        "ACCOUNT_NAME": "Carlos & Maria de la Rosa",
        "PHONE_NUMBER": "6155550456",
        "ADDRESS_ENVELOPE_TO": "CARLOS AND MARIA DE LA ROSA",
        "ADDRESS_CARD_TO": "THE DE LA ROSA FAMILY",
        "MAILING_STREET": "22 Sunset Blvd",
        "MAILING_STREET_2": "",
        "MAILING_CITY": "Murfreesboro",
        "MAILING_STATE": "TN",
        "MAILING_POSTAL_CODE": "37130",
        "PLEDGE_COMMENT": "",
    },
    {
        "FEST_QUEUE_ID": "Q005",
        "ACCOUNT_NAME": "Thomas O'Brien",
        "PHONE_NUMBER": "6155550567",
        "ADDRESS_ENVELOPE_TO": "THOMAS O'BRIEN",
        "ADDRESS_CARD_TO": "MR. THOMAS O'BRIEN",
        "MAILING_STREET": "55 Elm Court",
        "MAILING_STREET_2": "Suite 3B",
        "MAILING_CITY": "Brentwood",
        "MAILING_STATE": "TN",
        "MAILING_POSTAL_CODE": "37027",
        "PLEDGE_COMMENT": "Thomas donated in memory of his mother and asked us to keep her in prayer.",
    },
    {
        "FEST_QUEUE_ID": "Q006",
        "ACCOUNT_NAME": "Sandra McAllister",
        "PHONE_NUMBER": "4235550678",
        "ADDRESS_ENVELOPE_TO": "SANDRA MCALLISTER",
        "ADDRESS_CARD_TO": "THE MCALLISTER FAMILY",
        "MAILING_STREET": "900 Ridgeway Dr",
        "MAILING_STREET_2": "",
        "MAILING_CITY": "Chattanooga",
        "MAILING_STATE": "TN",
        "MAILING_POSTAL_CODE": "37402",
        "PLEDGE_COMMENT": "",
    },
    {
        "FEST_QUEUE_ID": "Q007",
        "ACCOUNT_NAME": "James & Evelyn Washington",
        "PHONE_NUMBER": "8655550789",
        "ADDRESS_ENVELOPE_TO": "JAMES AND EVELYN WASHINGTON",
        "ADDRESS_CARD_TO": "THE WASHINGTON FAMILY",
        "MAILING_STREET": "14 Lakeview Terrace",
        "MAILING_STREET_2": "",
        "MAILING_CITY": "Knoxville",
        "MAILING_STATE": "TN",
        "MAILING_POSTAL_CODE": "37902",
        "PLEDGE_COMMENT": "Evelyn left a voicemail saying she's been a supporter for over 20 years.",
    },
    {
        "FEST_QUEUE_ID": "Q008",
        "ACCOUNT_NAME": "Patricia Nguyen",
        "PHONE_NUMBER": "6155550890",
        "ADDRESS_ENVELOPE_TO": "PATRICIA NGUYEN",
        "ADDRESS_CARD_TO": "MS. PATRICIA NGUYEN",
        "MAILING_STREET": "3301 Cedar Hill Rd",
        "MAILING_STREET_2": "",
        "MAILING_CITY": "Nashville",
        "MAILING_STATE": "TN",
        "MAILING_POSTAL_CODE": "37215",
        "PLEDGE_COMMENT": "",
    },
]


# ─────────────────────────────────────────────
# In-memory "database" helpers
# ─────────────────────────────────────────────

def _init_db():
    """Initialize the in-memory donor queue once per session."""
    if "db_queue" not in st.session_state:
        # Shuffle for a realistic feel; copy so we don't mutate the original
        pool = [d.copy() for d in SYNTHETIC_DONORS]
        random.shuffle(pool)
        st.session_state["db_queue"] = pool
        st.session_state["db_thanked"] = []   # list of completed records
        st.session_state["db_feedback"] = []  # list of feedback strings


def claim_next(mode: str):
    """Pop the next available donor from the queue."""
    _init_db()
    queue = st.session_state["db_queue"]
    if not queue:
        return None
    donor = queue.pop(0)
    return donor


def mark_thanked(fest_queue_id, note, activity):
    """Record the donor as thanked and store the outcome."""
    _init_db()
    record = {
        "fest_queue_id": fest_queue_id,
        "note": note,
        "activity": activity,
        "thanked_at": datetime.now().isoformat(),
    }
    st.session_state["db_thanked"].append(record)
    return True


def submit_feedback(text):
    _init_db()
    st.session_state["db_feedback"].append(
        {"text": text, "submitted_at": datetime.now().isoformat()}
    )
    return True


# ─────────────────────────────────────────────
# Page setup
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Gratitude Fest Demo",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS (identical to production, minus branding)
# ─────────────────────────────────────────────

st.markdown(
    """
    <style>
      .block-container {
        padding-top: 1.0rem;
        padding-bottom: 2.5rem;
        max-width: 980px;
        margin-top: 2.5rem;
      }

      @media (max-width: 640px) {
        div.stButton > button { width: 100%; padding: 0.8rem 1rem; font-size: 1rem; }
        div[data-testid="stHorizontalBlock"] { gap: 0.5rem; }
        .block-container { padding-left: 1rem; padding-right: 1rem; }
      }

      .gf-card {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 16px;
        padding: 16px;
        margin: 10px 0 16px 0;
        background: rgba(255,255,255,0.02);
      }
      .gf-muted { opacity: 0.8; }

      .demo-banner {
        background: #D1ECF1;
        color: #0C5460;
        border: 1px solid #BEE5EB;
        border-radius: 10px;
        padding: 10px 16px;
        margin-bottom: 12px;
        font-size: 0.92rem;
        font-weight: 600;
        text-align: center;
      }
      @media (prefers-color-scheme: dark) {
        .demo-banner { background: #062C33; color: #BEE5EB; border-color: #0C5460; }
      }

      .mode-banner {
        background: #D1ECF1;
        color: #0C5460;
        border: 1px solid #BEE5EB;
        border-radius: 10px;
        padding: 10px 16px;
        margin: 8px 0 16px 0;
        font-size: 0.92rem;
        font-weight: 500;
        text-align: center;
      }
      @media (prefers-color-scheme: dark) {
        .mode-banner { background: #062C33; color: #BEE5EB; border-color: #0C5460; }
      }

      .gf-actions {
        position: sticky;
        bottom: 0;
        z-index: 10;
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(49, 51, 63, 0.15);
        border-radius: 16px;
        padding: 12px;
        margin-top: 12px;
      }
      @media (prefers-color-scheme: dark) {
        .gf-actions { background: rgba(19, 23, 32, 0.88); }
      }

      [data-testid="collapsedControl"]::after {
        content: " 💬 Feedback";
        font-size: 0.8rem;
        font-weight: 600;
        color: #0C5460;
        margin-left: 6px;
        white-space: nowrap;
      }
      @media (prefers-color-scheme: dark) {
        [data-testid="collapsedControl"]::after { color: #BEE5EB; }
      }

      .exit-banner {
        background: #D4EDDA;
        color: #155724;
        border: 1px solid #C3E6CB;
        border-radius: 16px;
        padding: 24px 20px;
        margin: 16px 0;
        font-size: 1.1rem;
        font-weight: 500;
        text-align: center;
        line-height: 1.6;
      }
      @media (prefers-color-scheme: dark) {
        .exit-banner { background: #0A2E14; color: #C3E6CB; border-color: #155724; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Demo notice banner
# ─────────────────────────────────────────────

st.markdown(
    """
    <div class="demo-banner">
      🧪 DEMO MODE — Synthetic data only. No real donors, no database connections.
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Session state defaults
# ─────────────────────────────────────────────

st.session_state.setdefault("just_thanked", False)
st.session_state.setdefault("thanked_count", 0)
st.session_state.setdefault("donor", None)
st.session_state.setdefault("confirming", False)
st.session_state.setdefault("pending_action", None)
st.session_state.setdefault("call_outcome", "")
st.session_state.setdefault("exited", False)
st.session_state.setdefault("feedback_submitted", False)

st.session_state.setdefault("mode_locked", False)
st.session_state.setdefault("mode_confirming", False)
st.session_state.setdefault("pending_mode", None)
st.session_state.setdefault("mode_choice_ui", "Calls")
st.session_state.setdefault("mode_value", None)

# init demo DB
_init_db()

# ─────────────────────────────────────────────
# Demo actor (replaces Snowflake current_user())
# ─────────────────────────────────────────────

actor = "demo_user"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

PHONE_TARGET_RE = re.compile(r"^\(\d{3}\)-\d{3}-\d{4}$")


def format_phone_us(s: str) -> str:
    if s is None:
        return "—"
    raw = str(s).strip()
    if raw == "":
        return "—"
    if PHONE_TARGET_RE.match(raw):
        return raw
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[0:3]})-{digits[3:6]}-{digits[6:10]}"
    return raw


def normalize_name(s: str) -> str:
    if not s or not isinstance(s, str):
        return s
    stripped = s.strip()
    if not stripped:
        return s
    if stripped != stripped.upper() and stripped != stripped.lower():
        return stripped

    PARTICLES = {
        "van", "de", "di", "da", "del", "della", "des", "du",
        "la", "le", "les", "von", "zu", "of", "the", "and"
    }

    def fix_word(word, is_first=False):
        if not word:
            return word
        if "-" in word:
            parts = word.split("-")
            return "-".join(
                fix_word(p, is_first=(i == 0 and is_first))
                for i, p in enumerate(parts)
            )
        lower = word.lower()
        if lower in PARTICLES and not is_first:
            return lower
        if lower.startswith("o'") and len(word) > 2:
            return "O'" + lower[2:].capitalize()
        if lower.startswith("mc") and len(word) > 2:
            return "Mc" + lower[2:].capitalize()
        if lower.startswith("mac") and len(word) > 4:
            rest = lower[3:]
            if rest[0].isalpha() and not rest.startswith(("e", "a", "i")):
                return "Mac" + rest.capitalize()
        return word.capitalize()

    words = stripped.split()
    result = [fix_word(w, is_first=(i == 0)) for i, w in enumerate(words)]
    return " ".join(result)


def getk(d, *keys, default=None):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def _reboot_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def _exit_reboot_row(key_suffix=""):
    _ec, _rc = st.columns([1, 1])
    with _ec:
        if st.button("🚪 Exit Session", key=f"exit_{key_suffix}", use_container_width=True):
            st.session_state["exited"] = True
            st.rerun()
    with _rc:
        if st.button("↻ Reboot Session", key=f"reboot_{key_suffix}", use_container_width=True):
            _reboot_session()
            st.rerun()


# ─────────────────────────────────────────────
# Feedback sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 💬 Leave Some Feedback!")
    st.caption("We'd love to know what you think about the Gratitude Fest App.")
    feedback_text = st.text_area(
        "Your feedback",
        placeholder="Type your feedback here...",
        key="feedback_input",
        label_visibility="collapsed",
    )
    if st.button("Submit Feedback", use_container_width=True, type="primary"):
        if feedback_text and feedback_text.strip():
            submit_feedback(feedback_text.strip())
            st.session_state["feedback_submitted"] = True
            st.rerun()
        else:
            st.warning("Please enter some feedback before submitting.")
    if st.session_state.get("feedback_submitted"):
        st.success("Thank you for your feedback! 🙏")
    
    # Demo: show collected feedback
    fb_list = st.session_state.get("db_feedback", [])
    if fb_list:
        st.markdown("---")
        st.caption(f"**{len(fb_list)} feedback entry(ies) this session:**")
        for fb in fb_list:
            st.caption(f"• {fb['text'][:60]}{'…' if len(fb['text']) > 60 else ''}")

# ─────────────────────────────────────────────
# Header (only when no active donor and not exited)
# ─────────────────────────────────────────────

_has_donor = st.session_state.get("donor") is not None
if not _has_donor and not st.session_state.get("exited"):
    _header_col, _help_col = st.columns([6, 1])
    with _header_col:
        st.markdown(
            '<h1 style="margin: 0; padding: 0; font-size: 2rem;">Gratitude Fest 🎉</h1>',
            unsafe_allow_html=True,
        )
        st.caption("Claim a donor → make the call or write a card → mark as Thanked.")
    with _help_col:
        with st.popover("ℹ️ Help", use_container_width=True):
            st.markdown(
                "**Demo mode.** Use the controls below to explore the app flow. "
                "Select Calls or Cards, claim a donor, fill in the outcome, "
                "then mark them as Thanked."
            )

    st.markdown(
        f"""
        <div class="gf-card">
          <div><b>Signed in as</b> <span class="gf-muted">{actor}</span></div>
          <div class="gf-muted">Thanked this session: <b>{st.session_state["thanked_count"]}</b></div>
          <div class="gf-muted">Donors remaining in queue: <b>{len(st.session_state.get("db_queue", []))}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# Exit screen
# ─────────────────────────────────────────────

if st.session_state.get("exited"):
    count = st.session_state.get("thanked_count", 0)
    st.markdown(
        f"""
        <div class="exit-banner">
          🙏 Thank you for participating in the Gratitude Fest!<br><br>
          You thanked <b>{count}</b> donor{"s" if count != 1 else ""} this session,
          so allow us to thank <b>YOU</b> for all that you do.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("✅ You're all done! Please **close this tab** when you're finished.")

    # Demo only: show summary of what was "thanked"
    thanked = st.session_state.get("db_thanked", [])
    if thanked:
        with st.expander("📋 Session summary (demo only)"):
            for r in thanked:
                st.write(
                    f"**{r['fest_queue_id']}** — {r['activity']}"
                    + (f" | Note: {r['note'][:60]}" if r["note"] else "")
                )

    if st.button("↻ Start New Session", use_container_width=True):
        _reboot_session()
        st.rerun()
    st.stop()

# ─────────────────────────────────────────────
# Mode selection
# ─────────────────────────────────────────────

if not st.session_state["mode_locked"]:
    st.markdown(
        '<h2 style="margin: 0; padding: 0; font-size: 2rem;">Calls or Cards?</h2>',
        unsafe_allow_html=True,
    )

    if not st.session_state["mode_confirming"]:
        st.radio(
            "Choose your mode (reboot to change later)",
            options=["Calls", "Cards"],
            horizontal=True,
            key="mode_choice_ui",
        )
        if st.button("Continue", type="primary", use_container_width=True):
            chosen = st.session_state["mode_choice_ui"]
            st.session_state["pending_mode"] = "CALLS" if chosen == "Calls" else "CARDS"
            st.session_state["mode_confirming"] = True
            st.rerun()
    else:
        pretty = "Calls" if st.session_state["pending_mode"] == "CALLS" else "Cards"
        st.warning(f"Are you sure you want to do **{pretty}** for this session?")
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button(f"✅ Confirm {pretty}", type="primary", use_container_width=True):
                st.session_state["mode_value"] = st.session_state["pending_mode"]
                st.session_state["mode_locked"] = True
                st.session_state["mode_confirming"] = False
                st.session_state["pending_mode"] = None
                st.rerun()
        with c2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state["mode_confirming"] = False
                st.session_state["pending_mode"] = None
                st.rerun()

mode_upper = st.session_state["mode_value"]
donor = st.session_state.get("donor")
has_active_donor = donor is not None

# ─────────────────────────────────────────────
# Claim next donor
# ─────────────────────────────────────────────

if not has_active_donor:
    claim_disabled = (mode_upper is None) or st.session_state.get("confirming", False)

    if st.button(
        "🎯 Claim Next Donor",
        disabled=claim_disabled,
        type="primary",
        use_container_width=True,
    ):
        result = claim_next(mode_upper)
        st.session_state["donor"] = result
        st.session_state["just_thanked"] = False
        st.session_state["confirming"] = False
        st.session_state["pending_action"] = None
        st.session_state["call_outcome"] = ""
        if result is None:
            st.info(
                "🎉 The queue is empty — all synthetic donors have been thanked! "
                "Reboot the session to start over."
            )
        else:
            st.rerun()

    if claim_disabled and mode_upper is None:
        st.caption("Select and confirm a mode to begin.")

    if st.session_state.get("just_thanked"):
        st.caption("🎉 Great job! Click **Claim Next Donor** to claim another donor.")

    if st.session_state["mode_locked"] and not st.session_state.get("confirming"):
        _exit_reboot_row("home")

# ─────────────────────────────────────────────
# Donor view
# ─────────────────────────────────────────────

if has_active_donor:
    fest_queue_id    = getk(donor, "FEST_QUEUE_ID",           default="")
    account_name     = getk(donor, "ACCOUNT_NAME",            default="(no name)")
    phone_raw        = getk(donor, "PHONE_NUMBER",            default="—")
    phone            = format_phone_us(phone_raw)
    envelope_to      = normalize_name(getk(donor, "ADDRESS_ENVELOPE_TO", default="(no name)"))
    card_to          = normalize_name(getk(donor, "ADDRESS_CARD_TO",     default="(no name)"))
    mailing_street   = getk(donor, "MAILING_STREET",          default="")
    mailing_street_2 = getk(donor, "MAILING_STREET_2",        default="")
    city             = getk(donor, "MAILING_CITY",            default="")
    state            = getk(donor, "MAILING_STATE",           default="")
    zipc             = getk(donor, "MAILING_POSTAL_CODE",     default="")

    st.markdown('<h2 style="margin-bottom:0.5rem;">Current Donor</h2>', unsafe_allow_html=True)

    if mode_upper == "CALLS":
        st.markdown(
            f"""
            <div class="gf-card" style="display:flex;flex-direction:column;justify-content:center;padding:12px 16px;">
              <div style="font-size:1.5rem;font-weight:700;">{envelope_to}</div>
              <div style="font-size:1.25rem;font-weight:200;"><b>📞 Phone</b>: {phone}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        street_line = (
            f"{mailing_street} {mailing_street_2}".strip()
            if mailing_street_2
            else mailing_street
        )
        st.markdown(
            f"""
            <div class="gf-card" style="display:flex;flex-direction:column;justify-content:center;padding:12px 16px;">
              <div style="font-size:1.5rem;font-weight:200;margin-bottom:8px;"><b>✉️ Address Envelope To</b>: {envelope_to}</div>
              <div style="font-size:1.5rem;font-weight:200;margin-bottom:8px;"><b>📬 Address Card To</b>: {card_to}</div>
              <div style="font-size:1.25rem;">{street_line}</div>
              <div style="font-size:1.25rem;">{city}, {state} {zipc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    pledge_comment = getk(donor, "PLEDGE_COMMENT")
    if pledge_comment:
        st.info(f"💬 Donor Story: {pledge_comment}")

    # Outcome picker (Calls only)
    if mode_upper == "CALLS":
        OUTCOMES = ["Live Call", "Voicemail", "Attempted Call - No VM"]
        st.selectbox(
            "Call outcome",
            options=["", *OUTCOMES],
            index=0,
            format_func=lambda x: "— Select an outcome —" if x == "" else x,
            key="call_outcome",
            help="Select the outcome of this call.",
        )
        pending_activity = st.session_state["call_outcome"]
        note = st.text_area(
            "Notes (Leave the donor's story or a note for staff to follow up).",
            key="note",
            placeholder="Type any notes here...",
        )
    else:
        pending_activity = "Correspondence"
        note = st.text_area(
            "Notes (Leave a note for staff to follow up if necessary).",
            key="note",
            placeholder="Type any notes here...",
        )

    # ── Thanked action area ──────────────────────────────────────────────────

    outcome_missing = mode_upper == "CALLS" and not st.session_state.get("call_outcome")

    if not st.session_state.get("confirming"):
        if mode_upper == "CALLS" and st.session_state.get("call_outcome") == "Attempted Call - No VM":
            st.caption("ℹ️ Please select Thanked to go to the next donor even if Attempted Call - No VM.")

        if outcome_missing:
            st.caption("⚠️ Please select a call outcome above before marking as Thanked.")

        if st.button(
            "✅ Thanked",
            type="primary",
            use_container_width=True,
            disabled=outcome_missing,
        ):
            pa = {
                "fest_queue_id": fest_queue_id,
                "note": note or "",
                "activity": pending_activity,
            }
            if mode_upper == "CALLS":
                # Calls: no confirm step — submit immediately
                mark_thanked(pa["fest_queue_id"], pa["note"], pa["activity"])
                st.session_state["donor"] = None
                st.session_state["just_thanked"] = True
                st.session_state["thanked_count"] += 1
                st.session_state["confirming"] = False
                st.session_state["pending_action"] = None
                st.rerun()
            else:
                # Cards: confirmation step
                st.session_state["pending_action"] = pa
                st.session_state["confirming"] = True
                st.rerun()

    else:
        # Confirm/Cancel — Cards mode only
        st.warning("Are you sure you want to mark this donor as **Thanked**?")
        cc1, cc2 = st.columns([1, 1])
        with cc1:
            if st.button("✅ Confirm Thanked", type="primary", use_container_width=True):
                pa = st.session_state.get("pending_action") or {}
                mark_thanked(
                    pa.get("fest_queue_id"),
                    pa.get("note", ""),
                    pa.get("activity", ""),
                )
                st.session_state["donor"] = None
                st.session_state["just_thanked"] = True
                st.session_state["thanked_count"] += 1
                st.session_state["confirming"] = False
                st.session_state["pending_action"] = None
                st.rerun()
        with cc2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state["confirming"] = False
                st.session_state["pending_action"] = None
                st.rerun()

    # Always-visible Exit + Reboot
    if st.session_state["mode_locked"] and not st.session_state.get("confirming"):
        _exit_reboot_row("donor")
