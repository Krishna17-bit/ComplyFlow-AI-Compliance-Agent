APP_CSS = """
<style>
:root {
    --bg: #070707;
    --panel: #111111;
    --panel2: #171717;
    --text: #f7f7f7;
    --muted: #b7b7b7;
    --line: #333333;
    --soft: #222222;
    --white: #ffffff;
    --black: #050505;
}
.stApp {
    background: radial-gradient(circle at 10% 0%, #1b1b1b 0%, #080808 35%, #050505 100%);
    color: var(--text);
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1320px;
}
section[data-testid="stSidebar"] {
    background: #0d0d0d;
    border-right: 1px solid #2a2a2a;
}
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: var(--text);
}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
    color: #e9e9e9;
}
.small-muted, .stCaptionContainer, .stCaptionContainer p {
    color: var(--muted) !important;
    font-size: 0.88rem;
}
.hero {
    border: 1px solid var(--line);
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    border-radius: 24px;
    padding: 28px 30px;
    box-shadow: 0 22px 60px rgba(0,0,0,0.35);
    margin-bottom: 22px;
}
.hero h1 {
    margin: 0;
    font-size: 2.45rem;
    letter-spacing: -0.04em;
}
.hero p {
    margin-top: 10px;
    max-width: 920px;
    color: #d8d8d8;
    font-size: 1.05rem;
}
.metric-card, .panel, .evidence-card, .risk-card {
    border: 1px solid var(--line);
    background: rgba(17,17,17,0.95);
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 12px 34px rgba(0,0,0,0.26);
}
.metric-card .label {
    color: var(--muted);
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.metric-card .value {
    color: var(--white);
    font-size: 2rem;
    font-weight: 800;
    margin-top: 6px;
}
.status-pill {
    display: inline-flex;
    align-items: center;
    padding: 6px 11px;
    border-radius: 999px;
    border: 1px solid #3b3b3b;
    color: #f4f4f4;
    background: #141414;
    margin: 4px 6px 4px 0;
    font-size: 0.84rem;
}
.good { border-color: #e8e8e8; }
.warn { border-color: #9f9f9f; }
.bad { border-color: #ffffff; background: #1f1f1f; }
.evidence-card {
    margin-bottom: 10px;
    background: #0f0f0f;
}
.risk-card {
    margin-bottom: 10px;
}
hr { border-color: #2b2b2b; }
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    border: 1px solid #333;
    background: #111;
    color: #f5f5f5;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #050505 !important;
}
.stTabs [aria-selected="true"] p {
    color: #050505 !important;
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div {
    background-color: #111111 !important;
    color: #ffffff !important;
    border-color: #444444 !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #aaaaaa !important;
}
div.stButton > button, div.stDownloadButton > button {
    background: #ffffff !important;
    color: #050505 !important;
    border: 1px solid #ffffff !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    min-height: 42px;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background: #eaeaea !important;
    color: #050505 !important;
    border: 1px solid #eaeaea !important;
}
div.stButton > button p, div.stDownloadButton > button p {
    color: #050505 !important;
    font-weight: 800 !important;
}
button[kind="primary"] {
    background: #ffffff !important;
    color: #050505 !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid #333;
    border-radius: 16px;
    overflow: hidden;
}
.stAlert {
    background: #151515 !important;
    color: #ffffff !important;
    border: 1px solid #3a3a3a !important;
}
.stProgress > div > div > div > div {
    background-color: #ffffff !important;
}
</style>
"""
