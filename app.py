import streamlit as st
import requests
import json

# 1. 设置页面配置
st.set_page_config(page_title="AI 跨境电商文案专家", page_icon="🌍", layout="wide")

# 2. 优化后的 CSS (修复了笔误，增强了兼容性)
st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* 按钮美化 */
    div.stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.2);
    }
    
    /* 输入框边框增强 */
    .stTextInput > div > div > input {
        border: 1px solid #dfe6e9;
    }
    
    /* 底部版权 */
    .footer {
        color: #7f8c8d;
        text-align: center;
        margin-top: 50px;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# --- 核心逻辑函数 (保持不变) ---
def generate_copywriting(model, lang, brand, keywords, audience, price, style, category, features, advantages, usage, seo_density, platform):
    api_key = st.secrets.get("deepseek_api_key")
    if not api_key:
        return "❌ 错误：未检测到 API Key，请检查 secrets.toml 文件。"
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    price_info = f"价格约为 {price}" if price > 0 else "不提及具体价格"
    brand_info = f"品牌名为【{brand}】" if brand else "不强调特定品牌"
    features_info = f"核心特点：{features}" if features else ""
    advantages_info = f"竞争优势：{advantages}" if advantages else ""
    usage_info = f"使用场景：{usage}" if usage else ""

    prompt = f"""
    你是一位精通{platform}平台的金牌文案专家。请使用【{lang}】为以下产品撰写适合{platform}平台的Listing。
    
    【产品信息】：
    - {brand_info}
    - 产品类型：{category}
    - 核心关键词：{keywords}
    - 目标受众：{audience}
    - {features_info}
    - {advantages_info}
    - {usage_info}
    - {price_info}

    【撰写要求】：
    1. 标题：包含核心关键词，吸引点击，符合{platform}平台的长度要求。
    2. 产品描述：根据{platform}平台的特点，撰写详细的产品描述，突出产品优势。
    3. 五点描述：写5个卖点，每个卖点前加一个合适的Emoji表情，强调痛点解决和产品优势。
    4. 语气风格：{style}，地道、专业、具有煽动性，符合当地消费者的阅读习惯。
    5. SEO优化：控制关键词密度在{seo_density}%左右，自然融入文案中，符合{platform}平台的SEO要求。
    6. 结尾：包含一句强有力的购买号召 (Call to Action)。
    7. 格式：使用Markdown格式，清晰易读。
    """

    data = {
        "model": model, 
        "messages": [
            {"role": "system", "content": "你是一位精通SEO和消费心理学的跨境电商文案专家。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 1500 # 增加长度，防止文案写一半断掉
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API 调用出错: {str(e)}"

# --- 侧边栏 ---
st.sidebar.header("🛠️ 生成设置")

# 模型与语言
model_label = st.sidebar.selectbox("选择 AI 模型", ("DeepSeek-V3 (极速生成)", "DeepSeek-R1 (深度思考)"))
model_map = {"DeepSeek-V3 (极速生成)": "deepseek-ai/DeepSeek-V3", "DeepSeek-R1 (深度思考)": "deepseek-ai/DeepSeek-R1"}
selected_model = model_map[model_label]

language = st.sidebar.selectbox("目标语言", ("English (英语 - 美国)", "Chinese (简体中文)", "Japanese (日语)", "German (德语)", "French (法语)"))
copywriting_style = st.sidebar.selectbox("文案风格", ("专业销售型", "亲切友好型", "科技感强", "幽默风趣", "简洁明了"))
product_category = st.sidebar.selectbox("产品类型", ("电子产品", "家居用品", "服装配饰", "美容护肤", "运动户外", "玩具游戏", "宠物用品", "其他"))
sales_platform = st.sidebar.selectbox("销售平台", ("亚马逊 (Amazon)", "独立站", "eBay", "Shopee", "Lazada", "Wish"))
st.sidebar.markdown("---")
st.sidebar.header("🔍 SEO 优化")
seo_density = st.sidebar.slider("关键词密度 (%)", 1, 5, 3)

# --- 模板数据 ---
product_templates = {
    "无线蓝牙耳机": {"brand": "Anker", "keywords": "无线蓝牙耳机, 主动降噪", "audience": "通勤者, 商务人士", "features": "40小时续航, IPX7防水", "advantages": "性价比高, 音质纯净", "price": 99.9, "usage": "通勤, 健身"},
    "面部精华液": {"brand": "SK-II", "keywords": "精华液, 抗衰老", "audience": "25+女性", "features": "含PITERA™, 易吸收", "advantages": "淡化细纹, 提亮肤色", "price": 159.0, "usage": "早晚护肤"},
    "智能手表": {"brand": "Apple", "keywords": "智能手表, 健康监测", "audience": "科技爱好者", "features": "心率监测, GPS", "advantages": "生态完善, 操作流畅", "price": 399.0, "usage": "运动, 日常"}
}

st.sidebar.markdown("---")
st.sidebar.header("📋 快速模板")

# 关键修改：使用回调函数来更新 Session State
def on_template_change():
    selected = st.session_state.template_selector
    if selected != "无 (手动输入)":
        data = product_templates[selected]
        st.session_state.brand_input = data["brand"]
        st.session_state.kw_input = data["keywords"]
        st.session_state.aud_input = data["audience"]
        st.session_state.feat_input = data["features"]
        st.session_state.adv_input = data["advantages"]
        st.session_state.price_input = data["price"]
        st.session_state.usage_input = data["usage"]

template_option = st.sidebar.selectbox(
    "选择预设模板",
    ["无 (手动输入)"] + list(product_templates.keys()),
    key="template_selector",
    on_change=on_template_change # 选中时触发填充
)

# --- 主界面 ---
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🌍 AI 跨境电商文案生成器")
        st.markdown("### 一键生成亚马逊/独立站 Listing，支持多语言与 SEO 优化")
    with col2:
        # 使用 Emoji 代替图片，加载更快且不会挂
        st.markdown("# 🚀")

st.markdown("---")

# 初始化 session_state 如果不存在 (防止报错)
if 'brand_input' not in st.session_state: st.session_state.brand_input = ""
if 'kw_input' not in st.session_state: st.session_state.kw_input = ""
if 'aud_input' not in st.session_state: st.session_state.aud_input = ""
if 'feat_input' not in st.session_state: st.session_state.feat_input = ""
if 'adv_input' not in st.session_state: st.session_state.adv_input = ""
if 'price_input' not in st.session_state: st.session_state.price_input = 0.0
if 'usage_input' not in st.session_state: st.session_state.usage_input = ""

# 📝 产品信息输入区 (关键：使用 key 绑定 session_state)
st.header("📝 产品信息")
col_a, col_b = st.columns(2)
with col_a:
    product_brand = st.text_input("品牌名称", key="brand_input", placeholder="例如：Anker")
    product_keywords = st.text_input("产品关键词 *", key="kw_input", placeholder="核心词，逗号分隔")
    product_price = st.number_input("产品价格", key="price_input", min_value=0.0, step=1.0)
with col_b:
    target_audience = st.text_input("目标受众 *", key="aud_input", placeholder="例如：通勤者")
    product_usage = st.text_input("使用场景", key="usage_input", placeholder="例如：户外露营")

product_features = st.text_area("产品核心特点", key="feat_input", placeholder="例如：续航40小时...")
product_advantages = st.text_area("竞争优势", key="adv_input", placeholder="例如：比竞品轻50%...")

st.markdown("---")

# 生成按钮
if st.button("🚀 开始生成文案", type="primary", use_container_width=True):
    if not product_keywords or not target_audience:
        st.warning("⚠️ 请至少输入【产品关键词】和【目标受众】")
    else:
        with st.spinner(f"正在呼叫 {model_label} 为您撰写 {language} 文案..."):
            result_text = generate_copywriting(
                selected_model, language, product_brand, product_keywords, target_audience, 
                product_price, copywriting_style, product_category, product_features, 
                product_advantages, product_usage, seo_density, sales_platform
            )
            
            st.success("✅ 生成成功！")
            with st.expander("📄 查看生成的文案", expanded=True):
                st.markdown(result_text)
                st.markdown("---")
                st.code(result_text, language='markdown')
                st.caption("提示：点击代码块右上角的复制按钮即可复制全文案")

# 底部
st.markdown("---")
st.markdown(
    """
    <div class='footer'>
        <p>Powered by DeepSeek V3/R1 & SiliconFlow | Designed for Global Sellers</p>
        <p>© 2026 AI 跨境电商文案专家</p>
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown("""
<style>
    /* 隐藏右上角的 Deploy 按钮 */
    .stDeployButton {
        display: none;
    }
    /* 隐藏右上角的三点菜单 (汉堡菜单) */
    #MainMenu {
        visibility: hidden;
    }
    /* 隐藏底部的 "Made with Streamlit" */
    footer {
        visibility: hidden;
    }
    /* 隐藏顶部的彩色条 */
    header {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)