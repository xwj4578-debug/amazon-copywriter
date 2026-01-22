import streamlit as st
import requests
import json

# 1. 设置页面配置
st.set_page_config(page_title="万能检讨书/小作文生成器", page_icon="🙏", layout="wide")

# 2. 样式美化 (保持不变)
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    div.stButton > button {
        background-color: #ff4b4b; /* 换成红色，更有警示感 */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        background-color: #d63031;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.2);
    }
    .footer { color: #7f8c8d; text-align: center; margin-top: 50px; font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

# --- 核心逻辑函数 (修改了 Prompt) ---
def generate_apology(model, article_type, recipient, mistake, reason, consequence, promise, style, word_count):
    # 获取 Key (逻辑不变)
    api_key = st.secrets.get("deepseek_api_key")
    if not api_key:
        return "❌ 错误：未检测到 API Key，请检查 secrets.toml 文件。"
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 构建核心 Prompt (这是最关键的修改！)
    prompt = f"""
    请你帮我写一篇【{article_type}】。
    
    【核心信息】：
    - 检讨/写作对象：{recipient}
    - 错误/主题：{mistake}
    - 发生原因/细节：{reason}
    - 造成的影响/后果：{consequence}
    - 改正措施/承诺：{promise}
    - 字数要求：大约 {word_count} 字
    - 语气风格：{style}

    【写作要求】：
    1. 结构清晰：开头(认错/破题) -> 中间(深刻剖析原因+具体经过) -> 结尾(整改措施+恳请原谅/升华)。
    2. 情感真挚：{style}，不要像机器人写的，要像人写的。
    3. 逻辑自洽：一定要针对"{mistake}"这个具体事件展开，不要假大空。
    4. 格式：分段清晰。
    """

    data = {
        "model": model, 
        "messages": [
            {"role": "system", "content": "你是一位精通心理学和公文写作的专家，擅长撰写各种检讨书、道歉信、保证书和情感小作文。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9, # 稍微调高，让生成的文章更有人味，不那么死板
        "max_tokens": 2000  # 字数可能较多，调大 token 限制
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API 调用出错: {str(e)}"

# --- 侧边栏 ---
st.sidebar.header("⚙️ 生成设置")

# 模型选择
model_label = st.sidebar.selectbox("选择 AI 模型", ("DeepSeek-V3 (极速生成)", "DeepSeek-R1 (深度思考)"))
model_map = {"DeepSeek-V3 (极速生成)": "deepseek-ai/DeepSeek-V3", "DeepSeek-R1 (深度思考)": "deepseek-ai/DeepSeek-R1"}
selected_model = model_map[model_label]

# 文章类型与风格
article_type = st.sidebar.selectbox("文章类型", ("检讨书", "道歉信", "保证书", "读后感/观后感", "申诉书", "分手/挽回小作文"))
style = st.sidebar.selectbox("语气风格", ("诚恳悔过型 (适合老师/家长)", "严肃深刻型 (适合领导/单位)", "卑微求饶型 (适合女朋友)", "感人肺腑型 (适合情感)", "公事公办型 (适合申诉)"))
word_count = st.sidebar.slider("预计字数", 500, 3000, 800, step=100)

st.sidebar.markdown("---")
st.sidebar.header("📋 快速模板")

# --- 模板数据 (针对不同倒霉场景) ---
templates = {
    "上课迟到 (学生版)": {
        "recipient": "班主任王老师", 
        "mistake": "早上睡过头，上课迟到了20分钟", 
        "reason": "昨晚熬夜打游戏，闹钟没定好", 
        "consequence": "影响了班级纪律，打断了老师讲课", 
        "promise": "以后设置3个闹钟，晚上11点前必睡，自愿罚站"
    },
    "工作失误 (社畜版)": {
        "recipient": "部门经理", 
        "mistake": "周报数据填错了，导致汇报出现偏差", 
        "reason": "周五临下班太着急，没有进行二次核对", 
        "consequence": "给团队造成了困扰，显得工作不严谨", 
        "promise": "以后建立Checklist，所有数据提交前复核一遍，自愿扣除本月绩效"
    },
    "惹女朋友生气 (求生欲版)": {
        "recipient": "亲爱的宝宝", 
        "mistake": "忘记了恋爱三周年纪念日", 
        "reason": "最近加班太忙，脑子糊涂了", 
        "consequence": "让你伤心了，显得我不够在乎你", 
        "promise": "补送一个大礼物，包揽一个月家务，带你去吃大餐，以后设日历提醒"
    }
}

# 模板回调函数
def on_template_change():
    selected = st.session_state.template_selector
    if selected != "无 (手动输入)":
        data = templates[selected]
        st.session_state.recip_input = data["recipient"]
        st.session_state.mistake_input = data["mistake"]
        st.session_state.reason_input = data["reason"]
        st.session_state.cons_input = data["consequence"]
        st.session_state.prom_input = data["promise"]

template_option = st.sidebar.selectbox(
    "选择场景模板",
    ["无 (手动输入)"] + list(templates.keys()),
    key="template_selector",
    on_change=on_template_change
)

# --- 主界面 ---
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🙏 万能检讨书/小作文生成器")
        st.markdown("### 无论犯了什么错，AI 帮你体面地认错")
    with col2:
        st.markdown("# 🙇‍♂️")

st.markdown("---")

# 初始化 Session State
if 'recip_input' not in st.session_state: st.session_state.recip_input = ""
if 'mistake_input' not in st.session_state: st.session_state.mistake_input = ""
if 'reason_input' not in st.session_state: st.session_state.reason_input = ""
if 'cons_input' not in st.session_state: st.session_state.cons_input = ""
if 'prom_input' not in st.session_state: st.session_state.prom_input = ""

# 📝 输入区
col_a, col_b = st.columns(2)
with col_a:
    recipient = st.text_input("写给谁？(对象)", key="recip_input", placeholder="例如：辅导员、老板、老婆")
    mistake = st.text_input("犯了什么错？(主题)", key="mistake_input", placeholder="例如：上班摸鱼被抓、忘记回消息")
with col_b:
    reason = st.text_input("错误原因 (甩锅/找补)", key="reason_input", placeholder="例如：身体不舒服、闹钟坏了")
    promise = st.text_input("怎么改？(承诺)", key="prom_input", placeholder="例如：写保证书、罚款、跪键盘")

consequence = st.text_area("造成了什么后果/影响？", key="cons_input", placeholder="例如：影响了团队进度，让您失望了...")

st.markdown("---")

# 生成按钮
if st.button("😭 深刻反省，开始生成", type="primary", use_container_width=True):
    if not recipient or not mistake:
        st.warning("⚠️ 请至少填写【写给谁】和【犯了什么错】，不然 AI 没法编...")
    else:
        with st.spinner(f"正在通过 {model_label} 构思措辞，请稍候..."):
            result_text = generate_apology(
                selected_model, article_type, recipient, mistake, 
                reason, consequence, promise, style, word_count
            )
            
            st.success("✅ 生成完成！希望能帮你过关！")
            with st.expander("📄 查看结果 (可一键复制)", expanded=True):
                st.markdown(result_text)
                st.markdown("---")
                st.code(result_text, language='markdown')

# 底部
st.markdown("---")
st.markdown(
    """
    <div class='footer'>
        <p>Powered by DeepSeek V3/R1 | 这是一个 AI 工具，但认错的态度要真诚哦 ❤️</p>
    </div>
    """, 
    unsafe_allow_html=True
)