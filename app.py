import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import io, re

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

st.set_page_config(page_title="BrainByte Solutions | LinkedIn Toolkit", page_icon="🧠", layout="wide")

# --- Brand styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Montserrat:wght@600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'DM Sans', sans-serif;}
.stApp {background:linear-gradient(145deg,#090909 0%,#121212 55%,#1c1608 100%);color:#f8f5ed;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#050505,#17120a);border-right:1px solid #d4a52a;}
[data-testid="stSidebar"] * {color:#f5f1e8!important;}
.block-container {padding-top:1.5rem;}
.bb-card {background:linear-gradient(145deg,rgba(30,30,30,.95),rgba(10,10,10,.96));border:1px solid rgba(227,177,50,.55);border-radius:18px;padding:20px 22px;box-shadow:0 8px 30px rgba(0,0,0,.25);}
.bb-title {font-family:Montserrat,sans-serif;font-weight:800;color:#f4c542;letter-spacing:.5px;}
.bb-muted {color:#c9c2b5;}
.bb-pill {display:inline-block;padding:6px 12px;border:1px solid #d4a52a;border-radius:999px;color:#f4c542;font-size:13px;margin:4px 4px 4px 0;}
section[data-testid="stFileUploader"] {border:1px dashed #d4a52a;border-radius:14px;}
.stButton>button {background:linear-gradient(90deg,#c79213,#f4cf57);color:#090909;border:0;border-radius:10px;font-weight:700;}
.stButton>button:hover {color:#000;border:1px solid #fff;}
hr {border-color:rgba(212,165,42,.3);}
</style>
""", unsafe_allow_html=True)

# sidebar
with st.sidebar:
    if (ASSETS / "logo.jpeg").exists(): st.image(str(ASSETS / "logo.jpeg"), width=170)
    st.markdown("## BrainByte Solutions")
    st.markdown("<span class='bb-muted'>Transforming Ideas Into Digital Success</span>", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigate", ["🏠 Home", "🧰 LinkedIn Toolkit", "📊 Dataset Lab", "✍️ Content Studio", "🎯 Profile Optimizer", "📁 Resources"])
    st.markdown("---")
    st.markdown("<span class='bb-pill'>Learn</span><span class='bb-pill'>Build</span><span class='bb-pill'>Grow</span>", unsafe_allow_html=True)
    st.caption("A student & professional growth toolkit")

# top banner
if page == "🏠 Home" and (ASSETS / "brand_banner.jpeg").exists():
    st.image(str(ASSETS / "brand_banner.jpeg"), use_container_width=True)

if page == "🏠 Home":
    st.markdown("# 🧠 BrainByte Solutions | LinkedIn Growth Hub")
    st.markdown("### Your workspace to improve your professional presence, analyze data, and create career-ready content.")
    c1,c2,c3,c4 = st.columns(4)
    for col, metric, label in zip([c1,c2,c3,c4],["6+","4","CSV","∞"],["Mini tools","Toolkit areas","Dataset-ready","Ideas"]):
        col.markdown(f"<div class='bb-card'><h2 class='bb-title'>{metric}</h2><div>{label}</div></div>",unsafe_allow_html=True)
    st.markdown("## Explore the workspace")
    tiles = [("🧰 LinkedIn Toolkit","Checklists, quick guides and practical tools."),("📊 Dataset Lab","Upload CSV/Excel files, preview, clean and analyze data."),("✍️ Content Studio","Create draft posts using guided prompts."),("🎯 Profile Optimizer","Evaluate profile completeness with a simple checklist."),("📁 Resources","Download sample data and templates.")]
    cols=st.columns(3)
    for i,(title,desc) in enumerate(tiles):
        cols[i%3].markdown(f"<div class='bb-card'><h3 class='bb-title'>{title}</h3><p>{desc}</p></div>",unsafe_allow_html=True)
    st.info("Use the left menu to open a tool. This app works with uploaded files and does not send them to an external service.")

elif page == "🧰 LinkedIn Toolkit":
    st.title("🧰 LinkedIn Optimization Toolkit")
    st.caption("Practical resources for building a credible and discoverable profile.")
    sections={
        "Profile essentials":["Use a clear, professional profile photo","Add a banner that reflects your field","Write a searchable headline","Add an About section in your own voice","List relevant skills and projects","Add education and certificates","Customize your profile URL where possible"],
        "Networking habits":["Connect with people you genuinely know or share interests with","Personalize connection notes","Follow organizations in your field","Comment thoughtfully on relevant posts","Keep conversations respectful and professional"],
        "Career visibility":["Share projects and learning milestones","Show outcomes, not only tools","Use relevant keywords naturally","Add links to portfolio, GitHub or project demos","Review your profile periodically"]}
    for section,items in sections.items():
        with st.expander(section,expanded=True):
            for item in items: st.checkbox(item,key=f"{section}-{item}")
    st.markdown("### Quick links (add your own URLs)")
    st.text_input("Portfolio / GitHub / project link",placeholder="Paste a URL here")

elif page == "📊 Dataset Lab":
    st.title("📊 Dataset Lab")
    st.write("Upload a CSV or Excel dataset. Preview it, inspect missing values and run quick summaries.")
    upload=st.file_uploader("Upload dataset",type=["csv","xlsx","xls"])
    if upload:
        try:
            df=pd.read_csv(upload) if upload.name.lower().endswith('.csv') else pd.read_excel(upload)
            st.success(f"Loaded {df.shape[0]:,} rows × {df.shape[1]} columns")
            a,b,c=st.columns(3); a.metric("Rows",f"{len(df):,}"); b.metric("Columns",len(df.columns)); c.metric("Missing cells",int(df.isna().sum().sum()))
            tabs=st.tabs(["Preview","Quality","Summary","Charts","Download"])
            with tabs[0]:
                st.dataframe(df.head(100),use_container_width=True)
                st.caption("Showing up to the first 100 rows.")
            with tabs[1]:
                quality=pd.DataFrame({"Column":df.columns,"Data type":[str(x) for x in df.dtypes],"Missing values":df.isna().sum().values,"Missing %":(df.isna().mean()*100).round(2).values,"Unique values":df.nunique(dropna=True).values})
                st.dataframe(quality,use_container_width=True)
                if st.button("Drop rows containing missing values"):
                    cleaned=df.dropna(); st.session_state.cleaned=cleaned; st.success(f"Cleaned preview: {cleaned.shape[0]} rows")
            with tabs[2]:
                st.write("Numeric columns")
                st.dataframe(df.describe(include=[np.number]).T,use_container_width=True)
                st.write("Categorical column counts")
                cats=df.select_dtypes(include=['object','category']).columns.tolist()
                if cats:
                    col=st.selectbox("Choose categorical column",cats)
                    st.dataframe(df[col].value_counts(dropna=False).head(30),use_container_width=True)
                else: st.caption("No categorical columns detected.")
            with tabs[3]:
                nums=df.select_dtypes(include=[np.number]).columns.tolist()
                if nums:
                    col=st.selectbox("Column for histogram",nums,key="histcol")
                    st.bar_chart(df[col].dropna().value_counts().sort_index().head(80))
                    if len(nums)>1:
                        x=st.selectbox("X axis",nums,key="xcol"); y=st.selectbox("Y axis",nums,key="ycol",index=min(1,len(nums)-1))
                        st.scatter_chart(df[[x,y]].dropna())
                else: st.info("No numeric columns to chart.")
            with tabs[4]:
                st.download_button("Download uploaded data as CSV",df.to_csv(index=False).encode('utf-8'),"dataset_export.csv","text/csv")
                if 'cleaned' in st.session_state:
                    st.download_button("Download cleaned dataset",st.session_state.cleaned.to_csv(index=False).encode('utf-8'),"cleaned_dataset.csv","text/csv")
        except Exception as e: st.error(f"Could not read this file: {e}")
    else:
        st.markdown("#### Sample dataset")
        sample=pd.DataFrame({"Name":["Aarav","Meera","Kabir","Sana","Dev"],"Profile_Views":[120,230,85,410,190],"Connections_Added":[12,20,8,35,18],"Posts_Per_Month":[2,4,1,6,3]})
        st.dataframe(sample,use_container_width=True)
        st.download_button("Download sample CSV",sample.to_csv(index=False).encode(),"brainbyte_sample.csv","text/csv")

elif page == "✍️ Content Studio":
    st.title("✍️ LinkedIn Content Studio")
    st.caption("Build a draft from a prompt. Review and personalize before publishing.")
    topic=st.text_input("Topic / milestone",placeholder="e.g. I completed my first ML project")
    audience=st.selectbox("Who is this for?",["Students","Recruiters","Professionals","My learning community"])
    tone=st.selectbox("Tone",["Professional","Warm & personal","Confident","Simple and student-friendly"])
    keypoints=st.text_area("Key points you want included",placeholder="What did you learn? What did you build? What is next?")
    if st.button("Create post draft"):
        if not topic.strip(): st.warning("Enter a topic first.")
        else:
            draft=f"{topic.strip()}\n\nToday, I wanted to share a small milestone with my {audience.lower()}.\n\n{keypoints.strip() if keypoints.strip() else 'This experience helped me reflect, learn, and keep improving.'}\n\nI am continuing to learn, practice, and build one step at a time. Looking forward to what comes next!\n\n#Learning #CareerGrowth #LinkedIn #Skills"
            st.text_area("Draft — edit before posting",draft,height=260)
            st.caption(f"Draft tone selected: {tone}")

elif page == "🎯 Profile Optimizer":
    st.title("🎯 Profile Completeness Checker")
    st.write("Tick items you already have. This is a checklist score—not a LinkedIn ranking or guarantee.")
    items=["Professional profile photo","Relevant banner image","Headline clearly states role/skills","About section","Education","Experience or volunteering","Projects","Skills section","Certificates","Custom profile URL","Featured section with work","Contact / portfolio link"]
    done=[]
    for item in items:
        if st.checkbox(item,key="opt-"+item): done.append(item)
    score=round(len(done)/len(items)*100)
    st.progress(score/100)
    st.metric("Checklist completion",f"{score}%",f"{len(done)} of {len(items)} items")
    if score<40: st.warning("Start with your headline, About section, projects and skills.")
    elif score<75: st.info("Good start. Add proof of work, certificates and a Featured section.")
    else: st.success("Strong checklist completion. Keep your details current and showcase meaningful work.")

elif page == "📁 Resources":
    st.title("📁 Resources & Downloads")
    st.markdown("### Brand assets")
    if (ASSETS / "linkedin_icon.png").exists(): st.image(str(ASSETS / "linkedin_icon.png"),width=180)
    st.markdown("### LinkedIn profile checklist")
    checklist="LinkedIn Profile Checklist\n- Profile photo\n- Banner\n- Headline\n- About\n- Education\n- Experience\n- Projects\n- Skills\n- Certificates\n- Featured links\n- Custom profile URL\n- Contact information\n"
    st.download_button("Download checklist TXT",checklist,"linkedin_checklist.txt","text/plain")
    st.markdown("### BrainByte Solutions")
    st.write("Learn • Practice • Build • Grow")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#b9aa82'>🟡 BrainByte Solutions · Transforming Ideas Into Digital Success</div>",unsafe_allow_html=True)
