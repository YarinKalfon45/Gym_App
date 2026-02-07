import streamlit as st
import json
import os
from datetime import datetime

# --- הגדרות עמוד ---
st.set_page_config(page_title="Gym Tracker Pro", page_icon="💪", layout="centered")

# --- CSS אגרסיבי לתיקון העיצוב ---
st.markdown("""
    <style>
    /* איפוס כללי ותמיכה בעברית */
    .stApp {
        background-color: #000000; /* שחור מוחלט */
        color: #ffffff;
        direction: rtl;
    }
    
    /* העלמת אלמנטים מיותרים של סטרימליט */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* כותרות */
    h1 {
        color: #4ADE80 !important; /* ירוק ניאון */
        text-align: center;
        font-weight: 900;
        letter-spacing: -1px;
        padding-bottom: 20px;
    }

    /* עיצוב הטאבים (בחירת ימים) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: #1F2937;
        border-radius: 10px;
        color: #ffffff;
        font-weight: bold;
        flex: 1; /* פורס את הטאבים לרוחב מלא */
    }
    .stTabs [aria-selected="true"] {
        background-color: #4ADE80 !important;
        color: #000000 !important;
    }

    /* כרטיסיות של התרגילים */
    div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
        background-color: #111827; /* אפור כהה מאוד */
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }

    /* טקסטים בתוך הכרטיסיות */
    p, label {
        color: #E5E7EB !important;
        font-size: 16px !important;
    }
    
    /* עיצוב שדות הקלט (Input Fields) - שיהיו ברורים! */
    input[type="text"] {
        background-color: #374151 !important;
        color: #ffffff !important;
        border: 2px solid #4B5563 !important;
        border-radius: 8px !important;
        text-align: center !important;
        font-size: 18px !important;
        height: 50px;
    }
    input[type="text"]:focus {
        border-color: #4ADE80 !important; /* גבול ירוק כשלוחצים */
        outline: none;
    }

    /* כפתור שמירה ראשי */
    .stButton button {
        width: 100%;
        background: linear-gradient(90deg, #4ADE80 0%, #22C55E 100%);
        color: black !important;
        font-weight: 900;
        font-size: 20px;
        padding: 15px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 0 15px rgba(74, 222, 128, 0.4);
        margin-top: 20px;
    }
    .stButton button:active {
        transform: scale(0.98);
    }

    /* טקסט של "פעם אחרונה" */
    .last-weight {
        color: #FACC15; /* צהוב */
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 5px;
        display: block;
    }
    
    /* שם התרגיל */
    .drill-title {
        font-size: 18px;
        font-weight: 800;
        color: white;
        margin-bottom: 2px;
    }
    .rest-time {
        font-size: 12px;
        color: #9CA3AF;
    }
    </style>
""", unsafe_allow_html=True)

# --- נתונים ולוגיקה ---
PROGRAMS = {
    "יום 1": [ # Vertical Focus
        {"name": "לחיצת כתפיים (OHP)", "rest": "2-3 דק'"},
        {"name": "לחיצת רגליים (Leg Press)", "rest": "90 שנ'"},
        {"name": "לחיצת חזה בשיפוע (משקולות)", "rest": "90 שנ'"},
        {"name": "חתירה בתמיכת חזה", "rest": "90 שנ'"},
        {"name": "פייס-פולס (Face Pulls)", "rest": "60 שנ'"},
        {"name": "כפיפת מרפקים (מוט EZ)", "rest": "60 שנ'"},
        {"name": "פשיטת טריצפס מעל הראש", "rest": "60 שנ'"},
    ],
    "יום 2": [ # Horizontal Focus
        {"name": "לחיצת חזה (סמית' שטוח)", "rest": "2-3 דק'"},
        {"name": "דדליפט רומני (RDL)", "rest": "90 שנ'"},
        {"name": "מתח / פולי עליון", "rest": "90 שנ'"},
        {"name": "הרחקת כתפיים לצדדים", "rest": "90 שנ'"},
        {"name": "כפיפת מרפקים (פטישים)", "rest": "60 שנ'"},
        {"name": "פשיטת מרפקים בכבלים", "rest": "60 שנ'"},
        {"name": "הרמות רגליים בתליה", "rest": "60 שנ'"},
    ],
    "יום 3": [ # Posterior Focus
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
    return "טרם בוצע"

# --- הממשק ---
st.title("GYM LOG 🔥")

# טאבים גדולים
tabs = st.tabs(["יום 1", "יום 2", "יום 3"])
days = list(PROGRAMS.keys())

for i, tab in enumerate(tabs):
    with tab:
        selected_day = days[i]
        
        # טופס אימון
        with st.form(key=f"form_{i}"):
            current_drills = PROGRAMS[selected_day]
            results = []
            
            for drill in current_drills:
                last_val = get_last_data(drill['name'])
                
                # כרטיסייה לכל תרגיל (Custom HTML בשביל עיצוב מדוייק)
                st.markdown(f"""
                <div style="margin-bottom: 5px;">
                    <div class="drill-title">{drill['name']}</div>
                    <div class="rest-time">⏱️ מנוחה: {drill['rest']}</div>
                    <div class="last-weight">פעם שעברה: {last_val}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    w = st.text_input("משקל", key=f"w_{drill['name']}_{i}", placeholder="ק\"ג", label_visibility="collapsed")
                with c2:
                    r = st.text_input("חזרות", key=f"r_{drill['name']}_{i}", placeholder="חזרות", label_visibility="collapsed")
                
                results.append({"name": drill['name'], "weight": w, "reps": r})
                st.markdown("---") # קו מפריד עדין
            
            # כפתור שמירה
            submit = st.form_submit_button("✅ שמור אימון")
            
            if submit:
                date_str = datetime.now().strftime("%d/%m/%Y")
                save_to_history({"name": selected_day, "date": date_str, "drills": results})
                
                # יצירת סיכום נקי להעתקה
                summary_txt = f"💪 אימון {selected_day} ({date_str})\n"
                for res in results:
                    val = res['weight'] if res['weight'] else "0"
                    reps = res['reps'] if res['reps'] else "-"
                    if val != "0": # רק אם מילאת משקל זה יופיע בסיכום
                        summary_txt += f"• {res['name']}: {val} ק\"ג ({reps})\n"
                
                st.success("נשמר בהצלחה!")
                st.code(summary_txt, language="text")

# --- כפתור היסטוריה מחוץ לטאבים ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("📜 היסטוריה מלאה (לחץ לפתיחה)"):
    history = load_history()
    if not history:
        st.info("אין נתונים עדיין")
    else:
        for item in history:
            st.markdown(f"<div style='color:#4ADE80; font-weight:bold; direction:rtl;'>{item['date']} - {item['name']}</div>", unsafe_allow_html=True)
            txt = ""
            for d in item['drills']:
                if d['weight'] and d['weight'] != "0":
                    txt += f"{d['name']}: {d['weight']} | "
            st.caption(txt)
            st.divider()