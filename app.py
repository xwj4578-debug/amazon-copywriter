import streamlit as st
import requests
import json
import time

# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="AI 跨境电商文案专家 V2.0",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS 样式增强 ---
st.markdown("""
<style>
    /* 全局字体与背景 */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }

    /* 标题样式 */
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }

    /* 按钮美化 */
    div.stButton > button {
        background: linear-gradient(to right, #2980b9, #3498db);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* 成功提示框美化 */
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border-left: 5px solid #28a745;
    }

    /* 底部版权 */
    .footer {
        margin-top: 60px;
        padding-top: 20px;
        border-top: 1px solid #e9ecef;
        text-align: center;
        color: #6c757d;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# --- 3. 核心逻辑函数 ---
def generate_copywriting(model, lang, brand, keywords, audience, price, style, category, features, advantages, usage,
                         seo_density, platform, modules):
    api_key = st.secrets.get("deepseek_api_key")
    if not api_key:
        return "❌ 错误：未检测到 API Key，请检查 secrets.toml 文件。"

    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 构建信息片段
    price_info = f"价格约为 {price}" if price > 0 else "不提及具体价格"
    brand_info = f"品牌名为【{brand}】" if brand else "不强调特定品牌"
    features_info = f"核心特点：{features}" if features else ""
    advantages_info = f"竞争优势：{advantages}" if advantages else ""
    usage_info = f"使用场景：{usage}" if usage else ""

    # 动态生成模块要求
    modules_prompt = "请包含以下部分：\n" + "\n".join(modules) if modules else "请生成完整的 Listing (标题、五点、长描述)。"

    prompt = f"""
    你是一位精通{platform}平台的金牌文案专家。请使用【{lang}】为以下产品撰写Listing。

    【产品信息】：
    - {brand_info}
    - 产品类型：{category}
    - 核心关键词：{keywords}
    - 目标受众：{audience}
    - {features_info}
    - {advantages_info}
    - {usage_info}
    - {price_info}

    【任务要求】：
    {modules_prompt}

    【通用撰写标准】：
    1. 语气风格：{style}。
    2. SEO优化：控制关键词密度在{seo_density}%左右，自然融入。
    3. 五点描述：每个卖点前加一个合适的Emoji表情。
    4. 格式：使用清晰的 Markdown 格式，标题加粗。
    """

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一位精通SEO和消费心理学的跨境电商文案专家。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 2000
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API 调用出错: {str(e)}"


# --- 4. 侧边栏设置 ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2855/2855523.png", width=60)
st.sidebar.title("🛠️ 生成设置")

with st.sidebar.expander("🤖 模型与语言 (点击展开)", expanded=True):
    model_label = st.selectbox("选择 AI 模型", ("DeepSeek-V3 (极速生成)", "DeepSeek-R1 (深度思考)"))
    model_map = {"DeepSeek-V3 (极速生成)": "deepseek-ai/DeepSeek-V3",
                 "DeepSeek-R1 (深度思考)": "deepseek-ai/DeepSeek-R1"}
    selected_model = model_map[model_label]

    language = st.selectbox("目标语言",
                            ("English (英语 - 美国)", "Chinese (简体中文)", "Japanese (日语)", "German (德语)",
                             "French (法语)", "Spanish (西班牙语)"))

with st.sidebar.expander("🎨 风格与平台", expanded=False):
    copywriting_style = st.selectbox("文案风格", ("专业销售型", "亲切友好型", "科技感强", "幽默风趣", "简洁明了"))
    product_category = st.selectbox("产品类型",
                                    ("电子产品", "家居用品", "服装配饰", "美容护肤", "运动户外", "玩具游戏", "宠物用品",
                                     "其他"))
    sales_platform = st.selectbox("销售平台", ("亚马逊 (Amazon)", "独立站 (Shopify)", "Temu", "TikTok Shop", "eBay"))

with st.sidebar.expander("🔍 SEO 高级设置", expanded=False):
    seo_density = st.slider("关键词密度 (%)", 1, 5, 3)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 快速模板")

# 模板数据
product_templates = {
    "无线蓝牙耳机": {"brand": "SoundPro", "keywords": "无线蓝牙耳机, 主动降噪, 运动", "audience": "通勤者, 健身爱好者",
                     "features": "40小时续航, IPX7防水", "advantages": "比竞品轻30%, 音质纯净", "price": 49.9,
                     "usage": "地铁, 健身房"},
    "维C美白精华": {"brand": "GlowSkin", "keywords": "维C精华, 美白, 抗氧化", "audience": "20-35岁女性",
                    "features": "15%纯维C, 玻尿酸保湿", "advantages": "7天提亮, 温和不刺激", "price": 29.0,
                    "usage": "早晚护肤"},
    "宠物智能喂食器": {"brand": "PetLife", "keywords": "自动喂食器, 宠物, 远程控制", "audience": "上班族养宠人士",
                       "features": "APP控制, 摄像头监控", "advantages": "不卡粮, 双电源供电", "price": 89.9,
                       "usage": "出差, 加班"}
}


# 模板回调
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
    on_change=on_template_change
)

# --- 5. 主界面内容 ---

# 标题区
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.title("🌍 AI 跨境电商文案专家 V2.0")
    st.markdown("##### 🚀 基于 DeepSeek R1 · 一键生成多语言爆款 Listing")
with col_h2:
    st.markdown("## 🛒")

st.markdown("---")

# 初始化 session state
keys = ['brand_input', 'kw_input', 'aud_input', 'feat_input', 'adv_input', 'price_input', 'usage_input']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = "" if "price" not in key else 0.0

# 输入区
with st.container():
    st.subheader("📝 产品档案")
    c1, c2 = st.columns(2)
    with c1:
        product_brand = st.text_input("品牌名称", key="brand_input", placeholder="例如：Anker")
        product_keywords = st.text_input("核心关键词 *", key="kw_input",
                                         placeholder="必填，例如：Running Shoes, Breathable")
        product_price = st.number_input("参考价格 ($)", key="price_input", min_value=0.0, step=1.0)
    with c2:
        target_audience = st.text_input("目标受众 *", key="aud_input", placeholder="必填，例如：Marathon Runners")
        product_usage = st.text_input("使用场景", key="usage_input", placeholder="例如：Outdoor, Gym")

    c3, c4 = st.columns(2)
    with c3:
        product_features = st.text_area("核心卖点/参数", key="feat_input", height=100,
                                        placeholder="例如：Lightweight, Non-slip sole...")
    with c4:
        product_advantages = st.text_area("竞争优势 (差异化)", key="adv_input", height=100,
                                          placeholder="例如：Cheaper than Nike, More durable...")

st.markdown("---")

# 生成控制区
st.subheader("🎯 生成选项")
check_cols = st.columns(4)
with check_cols[0]: gen_title = st.checkbox("标题 (Title)", value=True)
with check_cols[1]: gen_bullets = st.checkbox("五点描述 (Bullets)", value=True)
with check_cols[2]: gen_desc = st.checkbox("长描述 (Description)", value=True)
with check_cols[3]: gen_keywords = st.checkbox("后台搜索词 (ST)", value=True)

# 按钮逻辑
if st.button("🚀 开始生成文案", type="primary", use_container_width=True):
    if not product_keywords or not target_audience:
        st.error("⚠️ 请至少填写【核心关键词】和【目标受众】")
    else:
        # 构建模块列表
        modules_req = []
        if gen_title: modules_req.append("1. 标题 (Product Title)")
        if gen_bullets: modules_req.append("2. 五点描述 (Bullet Points)")
        if gen_desc: modules_req.append("3. 产品长描述 (Product Description)")
        if gen_keywords: modules_req.append("4. 后台搜索词 (Search Terms)")

        with st.spinner(f"正在调用 {model_label} 进行深度创作... (预计耗时 10-20秒)"):
            # 调用函数
            result_text = generate_copywriting(
                selected_model, language, product_brand, product_keywords, target_audience,
                product_price, copywriting_style, product_category, product_features,
                product_advantages, product_usage, seo_density, sales_platform, modules_req
            )

            # 存入 Session State
            st.session_state.generated_result = result_text
            st.toast("✅ 生成成功！", icon="🎉")

# --- 6. 结果展示与下载 ---
if 'generated_result' in st.session_state:
    st.markdown("### ✨ 生成结果")

    # 标签页展示
    tab1, tab2, tab3 = st.tabs(["📄 预览模式", "📝 源码模式", "💾 导出下载"])

    with tab1:
        st.info("💡 提示：您可以直接复制下方内容到亚马逊后台。")
        st.markdown(st.session_state.generated_result)

    with tab2:
        st.text_area("Markdown 源码", value=st.session_state.generated_result, height=400)

    with tab3:
        st.success("准备好下载了吗？")
        col_d1, col_d2 = st.columns(2)

        # 不同的下载格式
        with col_d1:
            st.download_button(
                label="📥 下载为 Markdown (.md)",
                data=st.session_state.generated_result,
                file_name=f"{product_brand}_listing.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                label="📥 下载为 纯文本 (.txt)",
                data=st.session_state.generated_result,
                file_name=f"{product_brand}_listing.txt",
                mime="text/plain",
                use_container_width=True
            )

# --- 7. 页脚 ---
st.markdown(
    """
    <div class='footer'>
        <p>Powered by <b>DeepSeek V3/R1</b> & <b>SiliconFlow</b> | 专为跨境卖家打造 🚀</p>
        <p style='font-size:0.8em; color:#bdc3c7;'>此内容由 AI 生成，建议使用前进行人工校对</p>
    </div>
    """,
    unsafe_allow_html=True
)