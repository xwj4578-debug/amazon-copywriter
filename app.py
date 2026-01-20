import streamlit as st
import requests
import json

# 1. 设置页面配置 (必须是第一行)
st.set_page_config(page_title="AI 跨境电商文案专家", page_icon="🌍", layout="wide")

# 2. 侧边栏：核心设置区
st.sidebar.header("🛠️ 生成设置")

# 🟢 功能一：模型选择 (让用户自己选)
model_label = st.sidebar.selectbox(
    "选择 AI 模型",
    ("DeepSeek-V3 (极速生成)", "DeepSeek-R1 (深度思考)"),
    index=0,
    help="V3速度快适合批量生成；R1逻辑强适合写复杂卖点"
)

# 映射模型名字（给API看的）
model_map = {
    "DeepSeek-V3 (极速生成)": "deepseek-ai/DeepSeek-V3",
    "DeepSeek-R1 (深度思考)": "deepseek-ai/DeepSeek-R1"
}
selected_model = model_map[model_label]

# 🟢 功能二：语言选择
language = st.sidebar.selectbox(
    "目标语言",
    ("English (英语 - 美国)", "Chinese (简体中文)", "Japanese (日语)", "German (德语)", "French (法语)"),
    index=0
)

st.sidebar.markdown("---")
st.sidebar.header("📝 产品信息")

# 🟢 功能三：更详细的输入
product_brand = st.sidebar.text_input("品牌名称", placeholder="例如：Anker / Sony")
product_keywords = st.sidebar.text_input("产品关键词 *", placeholder="例如：无线蓝牙耳机, 降噪")
target_audience = st.sidebar.text_input("目标受众 *", placeholder="例如：通勤者, 健身爱好者")
product_price = st.sidebar.number_input("产品价格 (币种自定)", min_value=0.0, value=0.0, step=1.0)


# 3. 核心逻辑函数
def generate_copywriting(model, lang, brand, keywords, audience, price):
    # 获取 API Key
    api_key = st.secrets.get("deepseek_api_key")
    if not api_key:
        return "❌ 错误：未检测到 API Key，请检查 secrets.toml 文件。"
    
    # 硅基流动地址
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 构建更高级的 Prompt (提示词)
    price_info = f"价格约为 {price}" if price > 0 else "不提及具体价格"
    brand_info = f"品牌名为【{brand}】" if brand else "不强调特定品牌"

    prompt = f"""
    你是一位亚马逊(Amazon)的金牌文案专家。请使用【{lang}】为以下产品撰写Listing。
    
    【产品信息】：
    - {brand_info}
    - 核心关键词：{keywords}
    - 目标受众：{audience}
    - {price_info}

    【撰写要求】：
    1. 标题 (Title)：包含核心关键词，吸引点击，不超过200字符。
    2. 五点描述 (Bullet Points)：写5个卖点，每个卖点前加一个合适的Emoji表情，强调痛点解决和产品优势。
    3. 语气风格：地道、专业、具有煽动性，符合当地消费者的阅读习惯。
    4. 结尾：包含一句强有力的购买号召 (Call to Action)。
    """

    data = {
        "model": model, 
        "messages": [
            {"role": "system", "content": "你是一位精通SEO和消费心理学的跨境电商文案专家。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8, #稍微调高一点，让文案更有创意
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API 调用出错: {str(e)}"

# 4. 主界面布局
st.title("🌍 AI 跨境电商文案生成器")
st.markdown("### 一键生成亚马逊/独立站 Listing，支持多语言与 SEO 优化")

# 检查必填项
if st.button("🚀 开始生成文案", type="primary", use_container_width=True):
    if not product_keywords or not target_audience:
        st.warning("⚠️ 请至少在侧边栏输入【产品关键词】和【目标受众】")
    else:
        with st.spinner(f"正在呼叫 {model_label} 为您撰写 {language} 文案..."):
            # 调用函数
            result_text = generate_copywriting(
                selected_model, 
                language, 
                product_brand, 
                product_keywords, 
                target_audience, 
                product_price
            )
            
            # 展示结果
            st.success("✅ 生成成功！")
            st.markdown("---")
            st.markdown(result_text)
            
            # 贴心功能：一键复制的提示
            st.caption("提示：鼠标悬停在文案右上角可以一键复制内容")

# 5. 底部版权/说明
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: grey;'>
        Powered by DeepSeek V3/R1 & SiliconFlow | Designed for Global Sellers
    </div>
    """, 
    unsafe_allow_html=True
)