# /// script
# requires-python = ">=3.10"
# dependencies = ["streamlit"]
# ///

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Interactive Typography", page_icon="🔤", layout="centered")

st.title("🔤 Interactive Typography Generator")
st.markdown("Design your own dynamic poster. Type a word and adjust the parameters.")

# --- 交互输入区 (Input) ---
col1, col2 = st.columns(2)

with col1:
    user_word = st.text_input("Enter a word", value="CHAOS")
    font_size = st.slider("Font Size", min_value=20, max_value=150, value=80)

with col2:
    crowding = st.slider("Crowding (间距)", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
    gravity = st.slider("Gravity (重力波动)", min_value=0, max_value=100, value=20)

# --- 错误处理 (Error Handling) ---
if not user_word.strip():
    st.warning("⚠️ Please enter a valid word. The current word is empty.")
    st.stop() # 如果用户输入为空，停止执行后面的代码

# --- 前端渲染区 (Response & Feedback) ---
# 我们用 HTML/CSS/JS 来绘制动态排版，实现丝滑的动画
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');
    
    body {{
        margin: 0;
        padding: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 400px;
        background-color: #111;
        color: #fff;
        font-family: 'Space Mono', monospace;
        overflow: hidden;
    }}

    #canvas-container {{
        position: relative;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }}

    .letter {{
        position: absolute;
        font-size: {font_size}px;
        font-weight: 700;
        transition: all 0.05s ease-out;
        pointer-events: none;
        /* 初始位置全在中心 */
        transform: translate(0, 0);
    }}
</style>
</head>
<body>

<div id="canvas-container"></div>

<script>
    const container = document.getElementById("canvas-container");
    const word = "{user_word}";
    const crowding = {crowding};
    const gravity = {gravity};
    const fontSize = {font_size};

    // 动态创建字母元素
    container.innerHTML = ""; // 清空上一次的字母
    const letters = [];
    for (let i = 0; i < word.length; i++) {{
        const span = document.createElement("span");
        span.className = "letter";
        span.innerText = word[i];
        // 初始随机偏移
        span.dataset.baseX = (i - word.length / 2) * (fontSize * crowding);
        span.dataset.baseY = 0;
        span.dataset.phase = Math.random() * Math.PI * 2;
        container.appendChild(span);
        letters.push(span);
    }}

    // 动画循环
    let time = 0;
    function animate() {{
        time += 0.05;
        
        letters.forEach((letter, index) => {{
            // 基础排版位置（横向排列）
            let x = parseFloat(letter.dataset.baseX);
            
            // 重力学效应：每个字母上下起伏，相位不同
            let phase = parseFloat(letter.dataset.phase);
            let y = Math.sin(time + phase) * gravity;

            // 拥挤度效应：当 crowding 小，字母靠得很近；甚至产生重叠错位感
            // 这里用一个微小的旋转来增加高级感
            let rotation = (crowding - 1.0) * 45 * Math.sin(time * 0.5 + phase);

            letter.style.transform = `translate(${{x}}px, ${{y}}px) rotate(${{rotation}}deg)`;
        }});
        
        requestAnimationFrame(animate);
    }}

    animate();
</script>

</body>
</html>
"""

# 将 HTML 渲染到 Streamlit 中
components.html(html_code, height=420)