"""
BrainByte Solutions - AI/ML Course Website (Streamlit)

Run locally :  streamlit run app.py
Deploy      :  push this folder to GitHub -> share.streamlit.io -> select app.py

Features
  - Home, Courses, Enroll Now, Student Portal, About Us, Contact, Admin
  - Student register / login (passwords stored hashed)
  - Course enrollment with coupon, seat tracking, enrollment ID and receipt download
  - Admin panel: enrollments, students, inquiries, course editing, revenue charts
  - SQLite database (brainbyte.db) is created automatically on first run
"""

import hashlib
import hmac
import html
import os
import re
import secrets
from datetime import date, datetime, timedelta

import pandas as pd
import sqlite3
import streamlit as st

# ----------------------------------------------------------------------------
# CONFIG  (edit these to match the company)
# ----------------------------------------------------------------------------
COMPANY = "BrainByte Solutions"
TAGLINE = "Transforming Ideas Into Digital Success"
CONTACT_EMAIL = "info@brainbytesolutions.com"
CONTACT_PHONE = "+91 98765 43210"
CONTACT_ADDRESS = "BrainByte Solutions, Your City, India"
UPI_ID = "brainbyte@upi"  # shown to students who choose UPI

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brainbyte.db")
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg")

COUPONS = {"BRAIN10": ("percent", 10), "WELCOME500": ("flat", 500)}
BATCHES = ["Weekday Morning (7-9 AM)", "Weekday Evening (7-9 PM)", "Weekend (Sat-Sun)"]
PAYMENT_MODES = ["UPI", "Debit / Credit Card", "Net Banking", "Pay at Center"]
STATUSES = ["Pending Payment", "Confirmed", "Completed", "Cancelled"]
PAGES = ["Home", "Courses", "Enroll Now", "Student Portal", "About Us", "Contact", "Admin"]

st.set_page_config(
    page_title=f"{COMPANY} | AI & ML Courses",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# STYLE  (black + gold, from the BrainByte logo)
# ----------------------------------------------------------------------------
CSS = """
<style>
:root { --gold:#E0A91B; --gold-soft:#F5CF6B; --ink:#000; --panel:#14110A; --line:#3A2F12; }
.stApp { background: radial-gradient(1200px 500px at 85% -10%, #2a1f06 0%, #000 60%); }
h1, h2, h3 { letter-spacing: -0.01em; }
.hero { padding: 2.2rem 0 1rem 0; }
.hero h1 { font-size: 3.1rem; line-height: 1.08; margin: 0 0 .8rem 0; color:#fff; }
.hero h1 span { color: var(--gold); }
.hero p { font-size: 1.12rem; color:#d9d2bd; max-width: 38rem; }
.badge { display:inline-block; padding:.2rem .7rem; border:1px solid var(--gold); color:var(--gold-soft);
         border-radius:999px; font-size:.8rem; margin-right:.4rem; margin-bottom:.4rem; }
.price { color: var(--gold-soft); font-size:1.5rem; font-weight:700; }
.muted { color:#a59d86; font-size:.9rem; }
.gold-line { height:2px; background:linear-gradient(90deg, var(--gold), transparent); margin:.4rem 0 1.2rem 0; border:0; }
.stat { border-left:3px solid var(--gold); padding:.2rem 0 .2rem .9rem; }
.stat b { font-size:1.7rem; color:#fff; display:block; }
.stat span { color:#a59d86; font-size:.9rem; }
.quote { border-left:3px solid var(--gold); padding:.4rem 1rem; color:#e8e1cc; background:#0d0b06; border-radius:0 8px 8px 0; }
div[data-testid="stSidebar"] { border-right:1px solid var(--line); }
div.stButton > button, div.stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button {
    border:1px solid var(--gold); border-radius:8px; font-weight:600; }
div.stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"] {
    background: var(--gold); color:#000; }
@media (max-width: 700px) { .hero h1 { font-size: 2.1rem; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# DATABASE
# ----------------------------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetchall(sql, params=()):
    conn = get_conn()
    try:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def fetchone(sql, params=()):
    rows = fetchall(sql, params)
    return rows[0] if rows else None


def fetchdf(sql, params=()):
    conn = get_conn()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_conn()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


@st.cache_resource
def init_db():
    conn = get_conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, phone TEXT,
            password_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at TEXT);
        CREATE TABLE IF NOT EXISTS courses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, tagline TEXT, level TEXT, duration TEXT, mode TEXT,
            fee REAL, instructor TEXT, start_date TEXT, seats INTEGER,
            description TEXT, modules TEXT, tools TEXT, outcomes TEXT, active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS enrollments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enroll_code TEXT UNIQUE, user_id INTEGER, course_id INTEGER,
            batch TEXT, education TEXT, payment_mode TEXT, coupon TEXT,
            amount REAL, status TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS inquiries(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT, message TEXT, created_at TEXT);
        """
    )
    count = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    if count == 0:
        today = date.today()
        seed = [
            ("AI & Machine Learning Foundations",
             "Start from zero and build your first ML models",
             "Beginner", "12 weeks", "Live Online", 14999, "BrainByte Faculty",
             today + timedelta(days=14), 40,
             "A beginner-friendly program that takes you from Python basics to training and evaluating real machine learning models.",
             "Python for Data Science|NumPy & Pandas|Data Visualization (Matplotlib, Seaborn)|Statistics & Probability Basics|Supervised Learning: Regression & Classification|Model Evaluation & Cross-Validation|Mini Project: Prediction App",
             "Python, Jupyter, NumPy, Pandas, Scikit-learn, Streamlit",
             "Build and evaluate ML models|Clean and analyse real datasets|Deploy a simple ML web app"),
            ("Machine Learning with Python (Pro)",
             "Regression, classification, clustering and model tuning",
             "Intermediate", "16 weeks", "Live Online + Recorded", 24999, "BrainByte Faculty",
             today + timedelta(days=21), 35,
             "Go deep into classical machine learning with hands-on projects such as price prediction, loan approval and placement prediction.",
             "Linear & Multiple Linear Regression|Logistic Regression & Classification|Decision Trees, Random Forest, XGBoost|Clustering & Dimensionality Reduction|Feature Engineering|Hyperparameter Tuning|Capstone: End-to-end ML Project with Streamlit",
             "Scikit-learn, XGBoost, Pandas, Matplotlib, Streamlit, Git",
             "Choose the right model for a problem|Tune and validate models|Ship an end-to-end ML project"),
            ("Deep Learning & Neural Networks",
             "From perceptrons to CNNs and RNNs",
             "Advanced", "12 weeks", "Live Online", 29999, "BrainByte Faculty",
             today + timedelta(days=30), 30,
             "Understand how neural networks learn and build deep learning models for images and sequences.",
             "Neural Network Fundamentals|Backpropagation & Optimizers|TensorFlow / Keras|Convolutional Neural Networks|Recurrent Networks & LSTMs|Transfer Learning|Capstone: Image Classifier",
             "TensorFlow, Keras, PyTorch basics, Google Colab",
             "Design and train neural networks|Apply transfer learning|Build an image classification system"),
            ("Data Science with Python",
             "Analytics, dashboards and storytelling with data",
             "Beginner", "14 weeks", "Live Online", 19999, "BrainByte Faculty",
             today + timedelta(days=10), 40,
             "Learn the complete data science workflow: collect, clean, analyse, visualise and present insights.",
             "Python & SQL for Analytics|Data Cleaning & EDA|Statistics for Data Science|Dashboards with Streamlit & Power BI|A/B Testing Basics|Intro to Machine Learning|Capstone: Business Analytics Report",
             "Python, SQL, Pandas, Power BI, Streamlit",
             "Analyse business data end-to-end|Create interactive dashboards|Present insights clearly"),
            ("Generative AI & LLM Applications",
             "Build chatbots and AI tools with large language models",
             "Intermediate", "10 weeks", "Live Online", 27999, "BrainByte Faculty",
             today + timedelta(days=28), 30,
             "Learn prompt engineering, APIs and retrieval-augmented generation to build useful AI applications.",
             "How LLMs Work|Prompt Engineering|Using LLM APIs|Embeddings & Vector Search|RAG (Retrieval-Augmented Generation)|Building Chatbots with Streamlit|Evaluation & Safety|Capstone: AI Assistant",
             "Python, LLM APIs, LangChain, Vector DBs, Streamlit",
             "Build chat and RAG applications|Write reliable prompts|Evaluate and deploy AI assistants"),
            ("Computer Vision with OpenCV",
             "Teach machines to see: detection, tracking and recognition",
             "Intermediate", "8 weeks", "Live Online + Lab", 17999, "BrainByte Faculty",
             today + timedelta(days=35), 25,
             "A practical course on image processing and computer vision, useful for IoT, drone and automation projects.",
             "Image Processing Basics|Filters, Edges & Contours|Face & Object Detection|Video Processing|Intro to YOLO|Capstone: Object Detection App",
             "Python, OpenCV, NumPy, YOLO, Google Colab",
             "Process images and video|Detect objects in real time|Build a vision-based mini product"),
        ]
        conn.executemany(
            """INSERT INTO courses(title,tagline,level,duration,mode,fee,instructor,start_date,seats,
                                   description,modules,tools,outcomes,active)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
            [(*s[:7], s[7].isoformat(), *s[8:]) for s in seed],
        )
        conn.commit()
    conn.close()
    return True


init_db()


# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------
def esc(x):
    return html.escape(str(x if x is not None else ""))


def inr(x):
    return f"₹{float(x):,.0f}"


def hash_pw(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 120_000).hex()
    return digest, salt


def seats_left(course):
    row = fetchone(
        "SELECT COUNT(*) AS n FROM enrollments WHERE course_id=? AND status!='Cancelled'",
        (int(course["id"]),),
    )
    return max(int(course["seats"]) - int(row["n"]), 0)


def get_courses(active_only=True):
    sql = "SELECT * FROM courses" + (" WHERE active=1" if active_only else "") + " ORDER BY id"
    return fetchall(sql)


def calc_price(fee, coupon):
    coupon = (coupon or "").strip().upper()
    if coupon in COUPONS:
        kind, val = COUPONS[coupon]
        disc = fee * val / 100 if kind == "percent" else val
        return max(fee - disc, 0), coupon, disc
    return fee, "", 0


def make_receipt(enrollment_row, user, course):
    lines = [
        "=" * 52,
        f"  {COMPANY.upper()}",
        f"  {TAGLINE}",
        "=" * 52,
        "  ENROLLMENT RECEIPT",
        "-" * 52,
        f"  Enrollment ID : {enrollment_row['enroll_code']}",
        f"  Date          : {enrollment_row['created_at']}",
        f"  Student       : {user['name']}",
        f"  Email         : {user['email']}",
        f"  Course        : {course['title']}",
        f"  Duration      : {course['duration']} ({course['mode']})",
        f"  Start date    : {course['start_date']}",
        f"  Batch         : {enrollment_row['batch']}",
        f"  Payment mode  : {enrollment_row['payment_mode']}",
        f"  Coupon        : {enrollment_row['coupon'] or '-'}",
        f"  Amount        : INR {float(enrollment_row['amount']):,.0f}",
        f"  Status        : {enrollment_row['status']}",
        "-" * 52,
        f"  Questions? {CONTACT_EMAIL} | {CONTACT_PHONE}",
        "=" * 52,
    ]
    return "\n".join(lines)


def goto(page, course_id=None):
    st.session_state["nav_page"] = page
    if course_id is not None:
        st.session_state["selected_course"] = int(course_id)


def current_user():
    return st.session_state.get("user")


def show_logo(width=None):
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=width) if width else st.image(LOGO_PATH)


def section_title(text, sub=None):
    st.markdown(f"## {text}")
    st.markdown('<hr class="gold-line">', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<p class="muted">{esc(sub)}</p>', unsafe_allow_html=True)


def course_card(c, key_prefix):
    left = seats_left(c)
    with st.container(border=True):
        st.markdown(
            f'<span class="badge">{esc(c["level"])}</span><span class="badge">{esc(c["duration"])}</span>'
            f'<span class="badge">{esc(c["mode"])}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f"### {c['title']}")
        st.markdown(f'<span class="muted">{esc(c["tagline"])}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="price">{inr(c["fee"])}</div>', unsafe_allow_html=True)
        st.caption(f"Starts {c['start_date']}  |  {left} seats left")
        b1, b2 = st.columns(2)
        b1.button("View details", key=f"{key_prefix}_d_{c['id']}", on_click=goto, args=("Courses", c["id"]))
        b2.button("Enroll", key=f"{key_prefix}_e_{c['id']}", on_click=goto, args=("Enroll Now", c["id"]),
                  type="primary", disabled=left == 0)


# ----------------------------------------------------------------------------
# PAGES
# ----------------------------------------------------------------------------
def page_home():
    courses = get_courses()
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown(
            f"""
            <div class="hero">
              <h1>Learn AI &amp; Machine Learning by <span>building real things</span>.</h1>
              <p>{esc(COMPANY)} runs project-based AI/ML courses with live classes, mentors and
              a portfolio you can show to employers. Pick a course, enroll in two minutes, start learning.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        b1, b2, _ = st.columns([1.2, 1.2, 2])
        b1.button("Browse courses", on_click=goto, args=("Courses",), type="primary")
        b2.button("Enroll now", on_click=goto, args=("Enroll Now",))
    with col2:
        show_logo()

    st.write("")
    total_students = fetchone("SELECT COUNT(*) AS n FROM users")["n"]
    total_enr = fetchone("SELECT COUNT(*) AS n FROM enrollments WHERE status!='Cancelled'")["n"]
    s1, s2, s3, s4 = st.columns(4)
    for col, big, small in [
        (s1, str(len(courses)), "Courses open for enrollment"),
        (s2, "100%", "Project-based learning"),
        (s3, str(total_students), "Registered students"),
        (s4, str(total_enr), "Active enrollments"),
    ]:
        col.markdown(f'<div class="stat"><b>{big}</b><span>{small}</span></div>', unsafe_allow_html=True)

    st.write("")
    section_title("Featured courses", "Choose the path that fits where you are today.")
    cols = st.columns(3)
    for i, c in enumerate(courses[:6]):
        with cols[i % 3]:
            course_card(c, "home")

    st.write("")
    section_title("How it works")
    h1, h2, h3, h4 = st.columns(4)
    steps = [
        ("Create your account", "Register with your email in under a minute."),
        ("Pick a course", "Compare syllabus, fee, start date and seats."),
        ("Enroll and pay", "Choose a batch and payment mode, apply a coupon."),
        ("Start learning", "Get your enrollment ID and track it in the Student Portal."),
    ]
    for col, (t, d) in zip((h1, h2, h3, h4), steps):
        with col.container(border=True):
            st.markdown(f"**{t}**")
            st.caption(d)

    st.write("")
    section_title("What students get")
    w1, w2 = st.columns(2)
    with w1:
        st.markdown(
            "- Live classes with recordings for every session\n"
            "- Real datasets and a capstone project in every course\n"
            "- Doubt-clearing sessions and mentor feedback\n"
            "- Resume and GitHub portfolio guidance"
        )
    with w2:
        st.markdown(
            "- Course completion certificate\n"
            "- Internship and placement support\n"
            "- Small batches so every student is heard\n"
            "- Lifetime access to course material"
        )

    st.write("")
    section_title("Student voices")
    q1, q2, q3 = st.columns(3)
    quotes = [
        ("I built a car price predictor and deployed it on Streamlit in my first month.", "BCA student"),
        ("The mentors explain concepts with real examples, not just slides.", "Working professional"),
        ("The capstone project became the best part of my resume.", "Career switcher"),
    ]
    for col, (q, who) in zip((q1, q2, q3), quotes):
        col.markdown(f'<div class="quote">“{esc(q)}”<br><span class="muted">- {esc(who)}</span></div>',
                     unsafe_allow_html=True)

    st.write("")
    section_title("Frequently asked questions")
    faqs = [
        ("Do I need coding experience?", "Not for the Foundations and Data Science courses. Intermediate and advanced courses expect basic Python."),
        ("What if I miss a live class?", "Every class is recorded and available in your course material."),
        ("How do I pay?", "Choose UPI, card, net banking or pay at center while enrolling. Your enrollment is confirmed once payment is verified."),
        ("Can I cancel my enrollment?", "Yes. You can cancel a pending enrollment from the Student Portal."),
        ("Is there a certificate?", "Yes, every student who completes the course and capstone project receives a certificate."),
    ]
    for q, a in faqs:
        with st.expander(q):
            st.write(a)


def page_courses():
    section_title("Courses", "Search, compare and enroll.")
    courses = get_courses()
    f1, f2, f3 = st.columns([2, 1, 1])
    query = f1.text_input("Search courses", placeholder="e.g. deep learning, Python, LLM")
    levels = f2.multiselect("Level", ["Beginner", "Intermediate", "Advanced"])
    sort = f3.selectbox("Sort by", ["Start date", "Fee: low to high", "Fee: high to low"])

    shown = []
    for c in courses:
        hay = " ".join(str(c.get(k, "")) for k in ("title", "tagline", "description", "tools", "modules")).lower()
        if query and query.lower() not in hay:
            continue
        if levels and c["level"] not in levels:
            continue
        shown.append(c)
    if sort == "Fee: low to high":
        shown.sort(key=lambda c: c["fee"])
    elif sort == "Fee: high to low":
        shown.sort(key=lambda c: -c["fee"])
    else:
        shown.sort(key=lambda c: c["start_date"])

    if not shown:
        st.info("No course matches your filters. Clear the search or level to see all courses.")
        return

    selected = st.session_state.get("selected_course")
    for c in shown:
        left = seats_left(c)
        with st.expander(f"{c['title']}  -  {inr(c['fee'])}  |  {c['duration']}  |  {c['level']}",
                         expanded=(selected == c["id"])):
            st.write(c["description"])
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Fee", inr(c["fee"]))
            d2.metric("Duration", c["duration"])
            d3.metric("Starts", c["start_date"])
            d4.metric("Seats left", left)
            t1, t2 = st.columns(2)
            with t1:
                st.markdown("**Syllabus**")
                for m in (c["modules"] or "").split("|"):
                    if m.strip():
                        st.markdown(f"- {m.strip()}")
            with t2:
                st.markdown("**You will be able to**")
                for o in (c["outcomes"] or "").split("|"):
                    if o.strip():
                        st.markdown(f"- {o.strip()}")
                st.markdown("**Tools**")
                st.write(c["tools"])
                st.markdown(f"**Mode:** {c['mode']}  \n**Instructor:** {c['instructor']}")
            st.button("Enroll in this course", key=f"cl_enroll_{c['id']}", on_click=goto,
                      args=("Enroll Now", c["id"]), type="primary", disabled=left == 0)
            if left == 0:
                st.warning("This batch is full. Contact us to join the waiting list.")


def page_enroll():
    section_title("Enroll in a course", "Fill in the details below to reserve your seat.")
    user = current_user()
    if not user:
        st.info("Please log in or create a free account to enroll.")
        st.button("Go to Student Portal", on_click=goto, args=("Student Portal",), type="primary")
        return

    courses = get_courses()
    if not courses:
        st.warning("No courses are open right now. Please check back soon.")
        return
    ids = [c["id"] for c in courses]
    default = st.session_state.get("selected_course", ids[0])
    idx = ids.index(default) if default in ids else 0
    by_id = {c["id"]: c for c in courses}

    chosen_id = st.selectbox("Course", ids, index=idx,
                             format_func=lambda i: f"{by_id[i]['title']} ({inr(by_id[i]['fee'])})")
    course = by_id[chosen_id]
    left = seats_left(course)

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Fee", inr(course["fee"]))
        c2.metric("Starts", course["start_date"])
        c3.metric("Seats left", left)
        st.caption(course["tagline"])

    if left == 0:
        st.error("This course is full. Choose another course or contact us to join the waiting list.")
        return

    existing = fetchone(
        "SELECT * FROM enrollments WHERE user_id=? AND course_id=? AND status!='Cancelled'",
        (int(user["id"]), int(course["id"])),
    )
    if existing:
        st.success(f"You are already enrolled in this course. Your enrollment ID is {existing['enroll_code']}.")
        st.button("View in Student Portal", on_click=goto, args=("Student Portal",))
        return

    with st.form("enroll_form"):
        st.markdown(f"**Student:** {user['name']}  |  {user['email']}")
        e1, e2 = st.columns(2)
        batch = e1.selectbox("Preferred batch", BATCHES)
        education = e2.selectbox("Current status", ["School", "Diploma", "Undergraduate (BCA / BTech / BSc)",
                                                   "Postgraduate", "Working professional", "Other"])
        p1, p2 = st.columns(2)
        pay = p1.selectbox("Payment mode", PAYMENT_MODES)
        coupon = p2.text_input("Coupon code (optional)", placeholder="e.g. BRAIN10")
        agree = st.checkbox("I agree to the course terms and refund policy.")
        submitted = st.form_submit_button("Confirm enrollment", type="primary")

    final, applied, disc = calc_price(course["fee"], coupon)
    if coupon.strip() and not applied:
        st.warning("That coupon code is not valid.")
    elif applied:
        st.success(f"Coupon {applied} applied. You save {inr(disc)}.")
    st.markdown(f"**Amount payable: {inr(final)}**")

    if submitted:
        if not agree:
            st.error("Please accept the terms to continue.")
            return
        if seats_left(course) == 0:
            st.error("The last seat was just taken. Please choose another course.")
            return
        code = f"BB{datetime.now():%y%m%d}{secrets.randbelow(9000) + 1000}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        status = "Pending Payment"
        execute(
            """INSERT INTO enrollments(enroll_code,user_id,course_id,batch,education,payment_mode,coupon,amount,status,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (code, int(user["id"]), int(course["id"]), batch, education, pay, applied, float(final), status, now),
        )
        st.balloons()
        st.success(f"You are enrolled! Your enrollment ID is {code}.")
        if pay == "UPI":
            st.info(f"Pay {inr(final)} to UPI ID {UPI_ID} and mention {code} in the note. "
                    "We confirm your seat once the payment is verified.")
        elif pay == "Pay at Center":
            st.info(f"Visit our center with enrollment ID {code} to complete the payment.")
        else:
            st.info("Our team will send you a secure payment link on your registered email shortly.")
        row = {"enroll_code": code, "created_at": now, "batch": batch, "payment_mode": pay,
               "coupon": applied, "amount": final, "status": status}
        st.download_button("Download receipt", make_receipt(row, user, course),
                           file_name=f"receipt_{code}.txt", mime="text/plain")


def page_portal():
    section_title("Student Portal")
    user = current_user()

    if not user:
        tab_login, tab_reg = st.tabs(["Log in", "Create account"])
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                pw = st.text_input("Password", type="password")
                ok = st.form_submit_button("Log in", type="primary")
            if ok:
                row = fetchone("SELECT * FROM users WHERE email=?", (email.strip().lower(),))
                if row:
                    digest, _ = hash_pw(pw, row["salt"])
                    if hmac.compare_digest(digest, row["password_hash"]):
                        st.session_state["user"] = {"id": row["id"], "name": row["name"],
                                                    "email": row["email"], "phone": row["phone"]}
                        st.rerun()
                st.error("Email or password is incorrect.")
        with tab_reg:
            with st.form("register_form"):
                name = st.text_input("Full name")
                email = st.text_input("Email address")
                phone = st.text_input("Phone number (10 digits)")
                pw1 = st.text_input("Password (min 6 characters)", type="password")
                pw2 = st.text_input("Confirm password", type="password")
                ok = st.form_submit_button("Create account", type="primary")
            if ok:
                email_n = email.strip().lower()
                if len(name.strip()) < 2:
                    st.error("Enter your full name.")
                elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email_n):
                    st.error("Enter a valid email address.")
                elif not re.match(r"^\d{10}$", phone.strip()):
                    st.error("Enter a 10-digit phone number.")
                elif len(pw1) < 6:
                    st.error("Password must be at least 6 characters.")
                elif pw1 != pw2:
                    st.error("Passwords do not match.")
                elif fetchone("SELECT id FROM users WHERE email=?", (email_n,)):
                    st.error("This email is already registered. Please log in.")
                else:
                    digest, salt = hash_pw(pw1)
                    uid = execute(
                        "INSERT INTO users(name,email,phone,password_hash,salt,created_at) VALUES(?,?,?,?,?,?)",
                        (name.strip(), email_n, phone.strip(), digest, salt, datetime.now().strftime("%Y-%m-%d %H:%M")),
                    )
                    st.session_state["user"] = {"id": uid, "name": name.strip(), "email": email_n, "phone": phone.strip()}
                    st.rerun()
        return

    h1, h2 = st.columns([4, 1])
    h1.markdown(f"### Welcome, {user['name']}")
    h1.caption(f"{user['email']}  |  {user['phone']}")
    if h2.button("Log out"):
        st.session_state.pop("user", None)
        st.rerun()

    rows = fetchall(
        """SELECT e.*, c.title, c.duration, c.mode, c.start_date, c.tagline, c.fee
           FROM enrollments e JOIN courses c ON c.id=e.course_id
           WHERE e.user_id=? ORDER BY e.id DESC""",
        (int(user["id"]),),
    )
    st.markdown("#### My courses")
    if not rows:
        st.info("You have not enrolled in any course yet.")
        st.button("Find a course", on_click=goto, args=("Courses",), type="primary")
        return

    for r in rows:
        with st.container(border=True):
            a, b = st.columns([3, 1])
            a.markdown(f"**{r['title']}**")
            a.caption(f"ID {r['enroll_code']}  |  {r['batch']}  |  Starts {r['start_date']}  |  Paid via {r['payment_mode']}")
            b.markdown(f"**{inr(r['amount'])}**")
            b.caption(r["status"])
            if r["status"] == "Confirmed":
                st.success("Your seat is confirmed. Joining details will be sent to your email before the start date.")
            elif r["status"] == "Pending Payment":
                st.warning("Waiting for payment verification.")
            elif r["status"] == "Completed":
                st.success("Course completed. Your certificate is available on request.")
            course = {"title": r["title"], "duration": r["duration"], "mode": r["mode"], "start_date": r["start_date"]}
            d1, d2, _ = st.columns([1, 1, 3])
            d1.download_button("Receipt", make_receipt(r, user, course), file_name=f"receipt_{r['enroll_code']}.txt",
                               key=f"rc_{r['id']}")
            if r["status"] == "Pending Payment":
                if d2.button("Cancel", key=f"cx_{r['id']}"):
                    execute("UPDATE enrollments SET status='Cancelled' WHERE id=?", (int(r["id"]),))
                    st.rerun()


def page_about():
    section_title("About us", TAGLINE)
    a, b = st.columns([3, 2], gap="large")
    with a:
        st.markdown(
            f"{COMPANY} is a technology company that builds AI and machine learning solutions and trains the "
            "next generation of engineers to do the same. Our courses are designed by people who work on real "
            "projects, so every lesson connects to something you can build and show."
        )
        st.markdown("#### What we believe")
        st.markdown(
            "- You learn machine learning by shipping models, not by watching slides.\n"
            "- Small batches and direct mentor access beat large lecture halls.\n"
            "- Every student should leave with a deployed project and a clear next step."
        )
        st.markdown("#### What we do")
        st.markdown(
            "- AI/ML training programs for students and professionals\n"
            "- Custom AI, data and web solutions for businesses\n"
            "- Internships and live project experience"
        )
    with b:
        show_logo()


def page_contact():
    section_title("Contact us", "Questions about a course or batch? Send us a message.")
    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        with st.form("contact_form", clear_on_submit=True):
            name = st.text_input("Your name")
            email = st.text_input("Email")
            phone = st.text_input("Phone (optional)")
            msg = st.text_area("How can we help?", height=140)
            ok = st.form_submit_button("Send message", type="primary")
        if ok:
            if not name.strip() or not msg.strip() or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()):
                st.error("Please add your name, a valid email and a message.")
            else:
                execute("INSERT INTO inquiries(name,email,phone,message,created_at) VALUES(?,?,?,?,?)",
                        (name.strip(), email.strip(), phone.strip(), msg.strip(),
                         datetime.now().strftime("%Y-%m-%d %H:%M")))
                st.success("Message sent. We will reply within one working day.")
    with c2:
        with st.container(border=True):
            st.markdown("**Email**")
            st.write(CONTACT_EMAIL)
            st.markdown("**Phone / WhatsApp**")
            st.write(CONTACT_PHONE)
            st.markdown("**Address**")
            st.write(CONTACT_ADDRESS)
            st.markdown("**Hours**")
            st.write("Mon-Sat, 10 AM - 7 PM")


def admin_password():
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        return "admin123"  # CHANGE THIS: set ADMIN_PASSWORD in .streamlit/secrets.toml


def page_admin():
    section_title("Admin panel")
    if not st.session_state.get("is_admin"):
        with st.form("admin_login"):
            pw = st.text_input("Admin password", type="password")
            ok = st.form_submit_button("Open admin panel", type="primary")
        if ok:
            if hmac.compare_digest(pw.encode(), admin_password().encode()):
                st.session_state["is_admin"] = True
                st.rerun()
            else:
                st.error("Incorrect admin password.")
        return

    if st.button("Log out of admin"):
        st.session_state["is_admin"] = False
        st.rerun()

    enr = fetchdf(
        """SELECT e.id, e.enroll_code AS enrollment_id, u.name AS student, u.email, u.phone,
                  c.title AS course, e.batch, e.education, e.payment_mode, e.coupon, e.amount, e.status, e.created_at
           FROM enrollments e JOIN users u ON u.id=e.user_id JOIN courses c ON c.id=e.course_id
           ORDER BY e.id DESC"""
    )
    paid = enr[enr["status"].isin(["Confirmed", "Completed"])] if not enr.empty else enr
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Students", fetchone("SELECT COUNT(*) AS n FROM users")["n"])
    m2.metric("Enrollments", 0 if enr.empty else int((enr["status"] != "Cancelled").sum()))
    m3.metric("Pending payments", 0 if enr.empty else int((enr["status"] == "Pending Payment").sum()))
    m4.metric("Revenue (confirmed)", inr(0 if paid.empty else paid["amount"].sum()))

    t1, t2, t3, t4, t5 = st.tabs(["Enrollments", "Students", "Inquiries", "Courses", "Analytics"])

    with t1:
        if enr.empty:
            st.info("No enrollments yet.")
        else:
            st.dataframe(enr.drop(columns=["id"]), hide_index=True)
            st.download_button("Download CSV", enr.to_csv(index=False), file_name="enrollments.csv", mime="text/csv")
            st.markdown("**Update status**")
            with st.form("status_form"):
                code = st.selectbox("Enrollment ID", enr["enrollment_id"].tolist())
                new = st.selectbox("New status", STATUSES)
                if st.form_submit_button("Update", type="primary"):
                    execute("UPDATE enrollments SET status=? WHERE enroll_code=?", (new, code))
                    st.success(f"{code} is now {new}.")
                    st.rerun()

    with t2:
        users = fetchdf("SELECT id, name, email, phone, created_at FROM users ORDER BY id DESC")
        if users.empty:
            st.info("No students registered yet.")
        else:
            st.dataframe(users.drop(columns=["id"]), hide_index=True)
            st.download_button("Download CSV", users.to_csv(index=False), file_name="students.csv", mime="text/csv")

    with t3:
        inq = fetchdf("SELECT name, email, phone, message, created_at FROM inquiries ORDER BY id DESC")
        if inq.empty:
            st.info("No inquiries yet.")
        else:
            st.dataframe(inq, hide_index=True)

    with t4:
        st.markdown("**Edit courses** (change values in the table, then save)")
        cdf = fetchdf("SELECT id, title, level, duration, mode, fee, seats, start_date, instructor, active FROM courses ORDER BY id")
        cdf["active"] = cdf["active"].astype(bool)
        edited = st.data_editor(cdf, hide_index=True, disabled=["id"], key="course_editor")
        if st.button("Save course changes", type="primary"):
            for _, r in edited.iterrows():
                execute(
                    """UPDATE courses SET title=?, level=?, duration=?, mode=?, fee=?, seats=?, start_date=?,
                       instructor=?, active=? WHERE id=?""",
                    (r["title"], r["level"], r["duration"], r["mode"], float(r["fee"]), int(r["seats"]),
                     str(r["start_date"]), r["instructor"], 1 if r["active"] else 0, int(r["id"])),
                )
            st.success("Courses updated.")
            st.rerun()

        st.markdown("**Add a new course**")
        with st.form("add_course", clear_on_submit=True):
            n1, n2 = st.columns(2)
            title = n1.text_input("Title")
            tagline = n2.text_input("Tagline")
            n3, n4, n5, n6 = st.columns(4)
            level = n3.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
            duration = n4.text_input("Duration", "8 weeks")
            fee = n5.number_input("Fee (INR)", min_value=0, value=15000, step=500)
            seats = n6.number_input("Seats", min_value=1, value=30)
            n7, n8 = st.columns(2)
            mode = n7.text_input("Mode", "Live Online")
            start = n8.date_input("Start date", value=date.today() + timedelta(days=14))
            desc = st.text_area("Description")
            modules = st.text_area("Syllabus modules (separate with | )")
            tools = st.text_input("Tools")
            outcomes = st.text_area("Outcomes (separate with | )")
            if st.form_submit_button("Add course", type="primary"):
                if not title.strip():
                    st.error("Course title is required.")
                else:
                    execute(
                        """INSERT INTO courses(title,tagline,level,duration,mode,fee,instructor,start_date,seats,
                                               description,modules,tools,outcomes,active)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
                        (title.strip(), tagline, level, duration, mode, float(fee), "BrainByte Faculty",
                         start.isoformat(), int(seats), desc, modules, tools, outcomes),
                    )
                    st.success("Course added.")
                    st.rerun()

    with t5:
        if enr.empty:
            st.info("Charts appear after the first enrollment.")
        else:
            active = enr[enr["status"] != "Cancelled"]
            st.markdown("**Enrollments per course**")
            st.bar_chart(active.groupby("course").size())
            st.markdown("**Revenue per course (confirmed + completed)**")
            if not paid.empty:
                st.bar_chart(paid.groupby("course")["amount"].sum())
            else:
                st.caption("No confirmed payments yet.")
            st.markdown("**Enrollments by day**")
            daily = active.assign(day=active["created_at"].str[:10]).groupby("day").size()
            st.line_chart(daily)


# ----------------------------------------------------------------------------
# NAVIGATION
# ----------------------------------------------------------------------------
st.session_state.setdefault("nav_page", "Home")

with st.sidebar:
    show_logo(200)
    st.markdown(f"**{COMPANY}**")
    st.caption(TAGLINE)
    st.radio("Navigate", PAGES, key="nav_page", label_visibility="collapsed")
    st.divider()
    u = current_user()
    if u:
        st.caption(f"Signed in as {u['name']}")
    else:
        st.caption("Not signed in")
        st.button("Log in / Register", on_click=goto, args=("Student Portal",))
    st.divider()
    st.caption(f"{CONTACT_EMAIL}\n\n{CONTACT_PHONE}")

ROUTER = {
    "Home": page_home,
    "Courses": page_courses,
    "Enroll Now": page_enroll,
    "Student Portal": page_portal,
    "About Us": page_about,
    "Contact": page_contact,
    "Admin": page_admin,
}
ROUTER[st.session_state["nav_page"]]()

st.write("")
st.markdown('<hr class="gold-line">', unsafe_allow_html=True)
st.caption(f"© {date.today().year} {COMPANY}. {TAGLINE}.")
