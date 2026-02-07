import streamlit as st
import json
import os
from datetime import datetime

# --- הגדרות עמוד ועיצוב ---
st.set_page_config(page_title="My FBW Tracker", page_icon="💪", layout="centered")

# CSS מותאם אישית לעיצוב מודרני ותמיכה ב-RTL
st.markdown("""
    <style>
    /* כיווניות לימין */
    .stApp { direction: rtl; }
    
    /* עיצוב כותרות */
    h1, h2, h3 { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #60A5FA; text-align: center; }
    
    /* כרטיסיות לתרגילים */
    div[data-testid="stVerticalBlock"] > div {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* כפתור ראשי */
    .stButton button {
        width: 100%;
        background-color: #4F46E5;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 15px;
        border: none;
        transition: 0.3s;
    }
    .stButton button:hover { background-color: #4338CA; }
    
    /* שדות קלט */
    input { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- נתונים ולוגיקה ---
PROGRAMS = {
    "יום 1: דגש לחיצה אנכית": [
        {"name": "לחיצת כתפיים (OHP)", "rest": "2-3 דק'"},
        {"name": "לחיצת רגליים (Leg Press)", "rest": "90 שנ'"},
        {"name": "לחיצת חזה בשיפוע (משקולות)", "rest": "90 שנ'"},
        {"name": "חתירה בתמיכת חזה", "rest": "90 שנ'"},
        {"name": "פייס-פולס (Face Pulls)", "rest": "60 שנ'"},
        {"name": "כפיפת מרפקים (מוט EZ)", "rest": "60 שנ'"},
        {"name": "פשיטת טריצפס מעל הראש", "rest": "60 שנ'"},
    ],
    "יום 2: דגש לחיצה אופקית": [
        {"name": "לחיצת חזה (סמית' שטוח)", "rest": "2-3 דק'"},
        {"name": "דדליפט רומני (RDL)", "rest": "90 שנ'"},
        {"name": "מתח / פולי עליון", "rest": "90 שנ'"},
        {"name": "הרחקת כתפיים לצדדים", "rest": "90 שנ'"},
        {"name": "כפיפת מרפקים (פטישים)", "rest": "60 שנ'"},
        {"name": "פשיטת מרפקים בכבלים", "rest": "60 שנ'"},
        {"name": "הרמות רגליים בתליה", "rest": "60 שנ'"},
    ],
    "יום 3: דגש גב אחורי ופאמפ": [
        {"name": "פוש פרס (Push Press)", "rest": "2-3 דק'"},
        {"name": "פשיטת רגליים + כפיפה", "rest": "90 שנ'"},
        {"name": "לחיצת חזה (מכונה)", "rest": "90 שנ'"},
        {"name": "פולי עליון (אחיזה רחבה)", "rest": "90 שנ'"},
        {"name": "פרפר אחורי (מכונה/משקולות)", "rest": "60 שנ'"},
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
        except:
            return []
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
    return "חדש"

# --- הממשק ---
st.title("🔥 FBW Tracker")

# טאבים לבחירת יום (יותר נוח בנייד מסלקטבוקס)
tabs = st.tabs(["יום 1", "יום 2", "יום 3"])
days = list(PROGRAMS.keys())

# בחירת היום הנוכחי לפי הטאב הפעיל
selected_day = None
for i, tab in enumerate(tabs):
    with tab:
        selected_day = days[i]
        st.caption(f"**{selected_day}**")
        
        # טופס אימון
        with st.form(key=f"form_{i}"):
            current_drills = PROGRAMS[selected_day]
            results = []
            
            for drill in current_drills:
                last_val = get_last_data(drill['name'])
                st.markdown(f"**{drill['name']}** <span style='color:gray; font-size:0.8em'>({drill['rest']})</span>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    w = st.text_input("משקל", key=f"w_{drill['name']}_{i}", placeholder=last_val)
                with c2:
                    r = st.text_input("חזרות", key=f"r_{drill['name']}_{i}", placeholder="10")
                
                results.append({"name": drill['name'], "weight": w, "reps": r})
                st.divider()
            
            # כפתור שמירה
            submit = st.form_submit_button("✅ סיים אימון ושמור")
            
            if submit:
                date_str = datetime.now().strftime("%d/%m/%Y")
                save_to_history({"name": selected_day, "date": date_str, "drills": results})
                
                # יצירת סיכום להעתקה
                summary_txt = f"💪 אימון {selected_day} ({date_str})\n"
                for res in results:
                    val = res['weight'] if res['weight'] else "0"
                    reps = res['reps'] if res['reps'] else "-"
                    summary_txt += f"• {res['name']}: {val} | {reps}\n"
                
                st.success("נשמר!")
                st.code(summary_txt, language="text")

# --- היסטוריה ---
st.markdown("---")
with st.expander("📜 היסטוריית אימונים מלאה"):
    history = load_history()
    if not history:
        st.info("אין עדיין אימונים שמורים.")
    else:
        for item in history:
            st.markdown(f"**{item['date']} - {item['name']}**")
            txt = ""
            for d in item['drills']:
                w = d['weight'] if d['weight'] else "-"
                txt += f"{d['name']}: {w} | "
            st.caption(txt)
            st.divider()