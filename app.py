import streamlit as st
import pandas as pd
import numpy as np
import io, os
import matplotlib.pyplot as plt

st.set_page_config(page_title="BrainByte Solutions | Digital Workspace", page_icon="🧠", layout="wide")

GOLD="#D4AF37"; BG="#07090D"; PANEL="#11151D"; MUTED="#A8AFBC"
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"] {{font-family: Inter, sans-serif;}}
.stApp {{background:radial-gradient(circle at 15% 0%, #1c1b14 0, {BG} 40%); color:#F7F7F7;}}
[data-testid="stSidebar"] {{background:#0B0D12; border-right:1px solid #29231A;}}
[data-testid="stSidebar"] * {{color:#f4f4f4;}}
.block-container {{padding-top:1.2rem;}}
.bb-card {{background:linear-gradient(145deg,#151922,#0d1016);border:1px solid #393021;border-radius:18px;padding:20px 22px;margin:7px 0;box-shadow:0 8px 25px rgba(0,0,0,.25);}}
.bb-kicker {{color:{GOLD};letter-spacing:2px;font-size:12px;font-weight:800;text-transform:uppercase;}}
.bb-title {{font-size:38px;font-weight:800;line-height:1.1;margin:5px 0 10px;}}
.bb-sub {{color:#BEC4CF;font-size:15px;}}
.gold {{color:{GOLD};}}
div.stButton>button {{background:linear-gradient(100deg,#b88b18,#f3d46a);color:#101010;border:0;border-radius:12px;font-weight:700;}}
div.stButton>button:hover {{border:1px solid white;color:black;}}
.stTabs [data-baseweb="tab"] {{font-weight:700;}}
hr {{border-color:#30281b;}}
[data-testid="stMetric"] {{background:#11151d;border:1px solid #342a1c;padding:14px;border-radius:14px;}}
</style>
""",unsafe_allow_html=True)

logo="brainbyte_logo.jpeg"
with st.sidebar:
    if os.path.exists(logo): st.image(logo,width=220)
    st.markdown("### <span class='gold'>BrainByte Solutions</span>",unsafe_allow_html=True)
    st.caption("Transforming Ideas into Digital Success")
    st.markdown("---")
    page=st.radio("Workspace",["Overview","LinkedIn Toolkit","Dataset Lab","Resources & Files"],index=0)
    st.markdown("---")
    st.markdown("**Learn • Practice • Build • Grow**")
    st.caption("A learning and productivity workspace")

def header(title, subtitle):
    st.markdown(f"<div class='bb-card'><div class='bb-kicker'>BrainByte Solutions</div><div class='bb-title'>{title}</div><div class='bb-sub'>{subtitle}</div></div>",unsafe_allow_html=True)

if page=="Overview":
    header("Digital Success Workspace","Your compact toolkit for professional branding, data exploration and learning.")
    a,b,c=st.columns(3)
    a.markdown("<div class='bb-card'><div class='bb-kicker'>01 • Profile</div><h3>LinkedIn Toolkit</h3><p>Headline, About, posts, hashtags and profile checklist.</p></div>",unsafe_allow_html=True)
    b.markdown("<div class='bb-card'><div class='bb-kicker'>02 • Data</div><h3>Dataset Lab</h3><p>Upload CSV, explore columns, summary statistics and charts.</p></div>",unsafe_allow_html=True)
    c.markdown("<div class='bb-card'><div class='bb-kicker'>03 • Learning</div><h3>Resource Hub</h3><p>Quick links, file uploads and reusable workspace notes.</p></div>",unsafe_allow_html=True)
    st.markdown("### Start here")
    st.info("Choose a tool from the sidebar. Upload your own CSV in Dataset Lab to explore it, or use the LinkedIn Toolkit to draft professional profile content.")
    st.markdown("<div class='bb-card'><h3 class='gold'>Learn • Grow • Succeed</h3><p>Designed with a premium black-and-gold theme inspired by BrainByte Solutions branding.</p></div>",unsafe_allow_html=True)

elif page=="LinkedIn Toolkit":
    header("LinkedIn Optimization Toolkit","Create profile-ready content and improve your professional presence.")
    tabs=st.tabs(["Headline Builder","About Builder","Post Studio","Hashtag Finder","Profile Checklist"])
    with tabs[0]:
        st.subheader("Headline Builder")
        role=st.text_input("Target role / career goal",placeholder="e.g. Aspiring Data Analyst")
        skills=st.text_input("Skills (comma-separated)",placeholder="Python, SQL, Excel, Machine Learning")
        keywords=st.text_input("Keywords / niche",placeholder="Data, AI, business insights")
        style=st.selectbox("Style",["Professional","Student / Aspiring","Creative"])
        if st.button("Build Headline",key="headline"):
            if role:
                sk=[x.strip() for x in skills.split(",") if x.strip()]
                key=[x.strip() for x in keywords.split(",") if x.strip()]
                if style=="Student / Aspiring": result=f"Aspiring {role} | { ' • '.join(sk[:3]) } | Learning, Building & Growing" if sk else f"Aspiring {role} | Learning, Building & Growing"
                elif style=="Creative": result=f"{role} | Turning Ideas into Impact | { ' • '.join(sk[:3]) }" if sk else f"{role} | Turning Ideas into Impact"
                else: result=f"{role} | { ' • '.join(sk[:4]) } | { ' • '.join(key[:2]) }" if sk or key else role
                st.success(result); st.code(result)
    with tabs[1]:
        st.subheader("About Section Builder")
        name=st.text_input("Name (optional)",key="aboutname")
        role2=st.text_input("Role / field",key="aboutrole")
        learning=st.text_area("What are you learning or working on?",placeholder="Projects, learning goals, experience...")
        strengths=st.text_area("Strengths / skills",placeholder="Technical and soft skills")
        goal=st.text_area("Career goal",placeholder="What opportunities or work do you want?")
        if st.button("Draft About Section"):
            if role2:
                about=f"Hi{(', I am '+name) if name else ''}! I am focused on {role2}.\n\n{learning}\n\nMy strengths and skills include: {strengths}.\n\nMy goal is to {goal}.\n\nI enjoy learning, building projects, collaborating and continuously improving. Let's connect and grow together!"
                st.text_area("Generated draft (edit before publishing)",about,height=260)
    with tabs[2]:
        st.subheader("Post Studio")
        topic=st.text_input("Post topic",placeholder="e.g. My first machine learning project")
        audience=st.selectbox("Audience",["Students","Professionals","Recruiters","General"])
        tone=st.selectbox("Tone",["Confident and professional","Friendly and reflective","Excited and celebratory"])
        keypoints=st.text_area("Key points to include")
        if st.button("Draft Post"):
            if topic:
                post=f"{topic}\n\n{keypoints}\n\nThis journey is a reminder that learning happens by doing, reflecting and improving. I look forward to taking the next step and connecting with others interested in {topic}.\n\n#Learning #Growth #CareerDevelopment"
                st.text_area("Draft",post,height=250)
    with tabs[3]:
        st.subheader("Hashtag Finder")
        niche=st.text_input("Topic / field",placeholder="e.g. AI, web development, student")
        if st.button("Suggest Hashtags"):
            if niche:
                words=[w.strip().replace(" ","") for w in niche.split(",") if w.strip()]
                tags=["#"+w.title() for w in words]+["#Learning","#CareerGrowth","#ProfessionalDevelopment","#BuildInPublic","#BrainByteSolutions"]
                st.code(" ".join(dict.fromkeys(tags)))
    with tabs[4]:
        st.subheader("Profile Readiness Checklist")
        items=["Professional profile photo","Custom banner","Clear headline with role and keywords","About section with story and goals","Skills section updated","Projects / portfolio featured","Education and certifications added","Contact and profile URL reviewed","Recent meaningful post","Network with relevant people"]
        done=[st.checkbox(x,key="check"+str(i)) for i,x in enumerate(items)]
        st.metric("Checklist progress",f"{sum(done)}/{len(items)}")
        st.progress(sum(done)/len(items))

elif page=="Dataset Lab":
    header("Dataset Lab","Upload a CSV file, inspect data, view summaries and create quick visualizations.")
    uploaded=st.file_uploader("Upload CSV dataset",type=["csv"])
    if uploaded:
        try:
            df=pd.read_csv(uploaded)
            st.success(f"Loaded dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")
            m1,m2,m3,m4=st.columns(4)
            m1.metric("Rows",f"{df.shape[0]:,}");m2.metric("Columns",df.shape[1]);m3.metric("Missing cells",int(df.isna().sum().sum()));m4.metric("Duplicate rows",int(df.duplicated().sum()))
            t1,t2,t3,t4=st.tabs(["Preview","Statistics","Charts","Clean & Download"])
            with t1:
                st.dataframe(df.head(100),use_container_width=True)
                st.write("Column types")
                st.dataframe(pd.DataFrame({"Column":df.columns,"Data type":df.dtypes.astype(str),"Missing":df.isna().sum().values}),use_container_width=True)
            with t2:
                st.dataframe(df.describe(include="all").transpose(),use_container_width=True)
            with t3:
                numeric=df.select_dtypes(include=np.number).columns.tolist()
                if numeric:
                    col=st.selectbox("Numeric column",numeric)
                    chart=st.selectbox("Chart type",["Histogram","Box plot","Line chart"])
                    fig,ax=plt.subplots()
                    if chart=="Histogram": df[col].dropna().plot(kind="hist",ax=ax,bins=25)
                    elif chart=="Box plot": df[col].dropna().plot(kind="box",ax=ax)
                    else: df[col].dropna().reset_index(drop=True).plot(kind="line",ax=ax)
                    ax.set_title(col); st.pyplot(fig); plt.close(fig)
                    if len(numeric)>1:
                        st.markdown("#### Correlation matrix")
                        fig,ax=plt.subplots()
                        df[numeric].corr().plot(kind="imshow",ax=ax) if False else ax.imshow(df[numeric].corr(),aspect="auto")
                        ax.set_xticks(range(len(numeric)));ax.set_xticklabels(numeric,rotation=45,ha="right")
                        ax.set_yticks(range(len(numeric)));ax.set_yticklabels(numeric)
                        st.pyplot(fig);plt.close(fig)
                else: st.warning("No numeric columns found for charting.")
            with t4:
                st.write("Choose basic cleaning actions.")
                drop_missing=st.checkbox("Drop rows containing missing values")
                drop_duplicates=st.checkbox("Drop duplicate rows")
                cleaned=df.copy()
                if drop_missing: cleaned=cleaned.dropna()
                if drop_duplicates: cleaned=cleaned.drop_duplicates()
                st.metric("Rows after selected cleaning",len(cleaned))
                st.dataframe(cleaned.head(50),use_container_width=True)
                out=cleaned.to_csv(index=False).encode("utf-8")
                st.download_button("Download cleaned CSV",out,"cleaned_dataset.csv","text/csv")
        except Exception as e: st.error(f"Could not read this CSV: {e}")
    else:
        st.markdown("<div class='bb-card'><h3>Upload your data to begin</h3><p>CSV files are supported. The data is processed in this app session.</p></div>",unsafe_allow_html=True)
        sample=pd.DataFrame({"Student":["A","B","C","D"],"Score":[78,88,67,92],"Hours":[2.5,4.0,1.5,5.0]})
        st.caption("Example dataset preview")
        st.dataframe(sample,use_container_width=True)

else:
    header("Resources & Files","Keep your reference files in this session and access helpful learning resources.")
    st.subheader("File Drop")
    files=st.file_uploader("Upload documents or images",type=["pdf","docx","pptx","xlsx","csv","txt","png","jpg","jpeg"],accept_multiple_files=True)
    if files:
        for f in files:
            st.write(f"📎 **{f.name}** • {f.size:,} bytes")
            st.download_button("Download "+f.name,f.getvalue(),f.name,key=f.name)
    st.markdown("### Workspace notes")
    note=st.text_area("Write your ideas, tasks or reminders here")
    if note: st.download_button("Download notes as TXT",note.encode(),"brainbyte_notes.txt")
    st.markdown("### Recommended learning areas")
    st.markdown("- Artificial Intelligence & Machine Learning\n- Python and data analysis\n- Web development\n- Professional branding and career preparation\n- Project building and presentation skills")

st.markdown("---")
st.markdown("<center><small>© BrainByte Solutions • Learn • Practice • Build • Grow</small></center>",unsafe_allow_html=True)
