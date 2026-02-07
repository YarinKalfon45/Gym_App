import streamlit as st
import json
import os
from datetime import datetime

# --- הגדרות עמוד ---
st.set_page_config(page_title="FBW Log", page_icon="📝", layout="centered")

# --- תיקון עיצוב אגרסיבי (High Contrast) ---
st.markdown("""
    <style>
    /* הגדרת כיווניות וצבע רקע כללי */
    .stApp {
        background-color: #121212;
        color: #ffffff;
        direction: rtl;
    }

    /* תיקון שדות הקלט - רקע לבן וטקסט שחור כדי שיהיה קריא ב-100% */
    input[type="text"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 2px solid #ccc !important;
        border-radius: 5px !important;
        padding: 10px !important;
        font-size: 16px !important;
    }
    
    /* תיקון לתיוג של השדות בסטרימליט */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border-radius: 5px !important;
    }

    /* כותרות */
    h1 {
        color: #60A5FA !important; /* כחול בהיר */
        text-align: center;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
    }

    /* עיצוב הטאבים */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important; /* כחול רויאל */
        color: white !important;
    }

    /* כרטיסיות אימון - מסגרת אפורה וברורה */
    div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
        background-color: #1E1E1E;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }

    /* כפתור שמירה - גדול וכחול */
    .stButton button {
        background-color: #2563EB !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #1D4ED8 !important;
    }

    /* טקסטים קטנים */
    .drill-header {
        font-size: 18px;
        font-weight: bold;
        color: #E5E7EB;
        margin-bottom: 5px;
    }
    .drill-info {
        font-size: 14px;
        color: #9CA3AF;
        margin-bottom: 10px;
    }
    .last-score {
        color: #FACC15; /* צהוב */
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- נתונים ---
PROGRAMS = {
    "יום 1": [
        {"name": "לחיצת כתפיים (OHP)", "rest": "2-3 דק'"},
        {"name": "לחיצת רגליים (Leg Press)", "rest": "90 שנ'"},
        {"name": "לחיצת חזה בשיפוע (משקולות)", "rest": "90 שנ'"},
        {"name": "חתירה בתמיכת חזה", "rest": "90 שנ'"},
        {"name": "פייס-פולס (Face Pulls)", "rest": "60 שנ'"},
        {"name": "כפיפת מרפקים (מוט EZ)", "rest": "60 שנ'"},
        {"name": "פשיטת טריצפס מעל הראש", "rest": "60 שנ'"},
    ],
    "יום 2": [
        {"name": "לחיצת חזה (סמית' שטוח)", "rest": "2-3 דק'"},
        {"name": "דדליפט רומני (RDL)", "rest": "90 שנ'"},
        {"name": "מתח / פולי עליון", "rest": "90 שנ'"},
        {"name": "הרחקת כתפיים לצדדים", "rest": "90 שנ'"},
        {"name": "כפיפת מרפקים (פטישים)", "rest": "60 שנ'"},
        {"name": "פשיטת מרפקים בכבלים", "rest": "60 שנ'"},
        {"name": "הרמות רגליים בתליה", "rest": "60 שנ'"},
    ],
    "יום 3": [
        {"name": "פוש פרס (Push Press)", "rest": "2-3 דק'"},
        {"name": "פשיטת רגליים + כפיפה", "rest": "90 שנ'"},
        {"name": "לחיצת חזה (מכונה)", "rest": "90 שנ'"},
        {"name": "פולי עליון (אחיזה רחבה)", "rest": "90 שנ'"},
        {"name": "פרפר אחורי (מכונה)", "rest": "60 שנ'"},
        {"name": "כפיפת מרפקים (פריצ'ר)", "rest": "60 שנ'"},
        {"name": "פשיטת מרפקים (Skull Crushers)", "rest": "60 שנ'"},
    ]
}

DB_FILE = "workout_history.json"

# --- פונקציות ---
def load_history():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_to_history(workout_data):
    history = load_history()
    history.insert(0, workout_data)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:30], f, ensure_ascii=False, indent=4)

def get_last_data(drill_name):
    history = load_history()
    for workout in history:
        for drill in workout["drills"]:
            if drill["name"] == drill_name and drill["weight"]:
                return f"{drill['weight']} ק\"ג"
    return "ריק"

# --- ממשק משתמש ---
st.title("יומן אימונים 🏋️‍♂️")

# בחירת יום
tabs = st.tabs(["יום 1", "יום 2", "יום 3"])
days_list = list(PROGRAMS.keys())

for i, tab in enumerate(tabs):
    with tab:
        current_day_name = days_list[i]
        
        with st.form(key=f"workout_form_{i}"):
            results = []
            
            for drill in PROGRAMS[current_day_name]:
                last_val = get_last_data(drill['name'])
                
                # כותרת התרגיל
                st.markdown(f"""
                <div style="margin-top: 10px;">
                    <div class="drill-header">{drill['name']}</div>
                    <div class="drill-info">
                        מנוחה: {drill['rest']} | <span class="last-score">פעם שעברה: {last_val}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # שדות הקלט - עכשיו לבנים וברורים
                c1, c2 = st.columns(2)
                with c1:
                    w = st.text_input("משקל (ק\"ג)", key=f"w_{drill['name']}_{i}", placeholder="0")
                with c2:
                    r = st.text_input("חזרות", key=f"r_{drill['name']}_{i}", placeholder="10")
                
                results.append({"name": drill['name'], "weight": w, "reps": r})
                st.markdown("---")

            # כפתור שמירה
            if st.form_submit_button("שמור אימון ✅"):
                date_str = datetime.now().strftime("%d/%m/%Y")
                save_to_history({"name": current_day_name, "date": date_str, "drills": results})
                
                summary = f"💪 אימון {current_day_name} ({date_str})\n"
                for item in results:
                    if item['weight'] and item['weight'] != "0":
                        summary += f"• {item['name']}: {item['weight']} ק\"ג ({item['reps']})\n"
                
                st.success("האימון נשמר!")
                st.code(summary, language="text")

# --- היסטוריה ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("היסטוריה (לחץ לפתיחה)"):
    history_data = load_history()
    if not history_data:
        st.info("אין נתונים.")
    else:
        for entry in history_data:
            st.markdown(f"**{entry['date']} - {entry['name']}**")
            details = " | ".join([f"{d['name']}: {d['weight']}" for d in entry['drills'] if d['weight'] and d['weight'] != '0'])
            st.caption(details)
            st.divider()