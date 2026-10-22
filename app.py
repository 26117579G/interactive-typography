# /// script
# requires-python = ">=3.10"
# dependencies = ["streamlit"]
# ///

import streamlit as st
import streamlit.components.v1 as components

# 设置页面配置
st.set_page_config(page_title="Kinetic Typography Studio", page_icon="🔤", layout="wide")

# 标题和介绍
st.title("🔤 Kinetic Typography Studio")
st.markdown("Create a dynamic, interactive poster. Move your mouse over the letters to disturb them.")

# --- 交互输入区 (Input) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    user_word = st.text_input("Text", value="CHAOS")
    # 进阶5：错误处理 - 长度限制
    if len(user_word) > 15:
        st.info("💡 For the best visual results, use 15 characters or fewer.")

with col2:
    font_size = st.slider("Font Size", min_value=50, max_value=200, value=120, step=10)

with col3:
    gravity = st.slider("Wave Amplitude", min_value=0, max_value=150, value=40)
    crowding = st.slider("Crowding", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

with col4:
    text_color = st.color_picker("Neon Color", "#00FFCC")

# --- 错误处理 (Error Handling) ---
if not user_word.strip():
    st.warning("⚠️ Please enter a valid word. The current word is empty.")
    st.stop() # 如果输入为空，停止执行后续渲染，防崩溃

# --- 前端渲染区 (Response & Feedback) ---
# 进阶1：选择极具张力的 Anton 字体
# 进阶2：加入 CSS 霓虹渐变和混合模式
# 进阶3：加入鼠标跟随斥力物理引擎
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    /* 引入 Google Fonts 的 Anton 字体 */
    @import url('https://fonts.googleapis.com/css2?family=Anton&display=swap');
    
    body {{
        margin: 0;
        padding: 0;
        height: 500px;
        background: #0a0a0c; /* 极深色背景 */
        /* 进阶：动态深色星空渐变背景 */
        background-image: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #0a0a0c 80%);
        color: #fff;
        font-family: 'Anton', sans-serif;
        overflow: hidden; /* 防止滚动条出现 */
        display: flex;
        justify-content: center;
        align-items: center;
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
        color: {text_color};
        /* 混合模式：让重叠的字母产生反色/发光效果 */
        mix-blend-mode: screen;
        /* 霓虹发光阴影 */
        text-shadow: 0 0 10px {text_color}80, 0 0 30px {text_color}40;
        transition: transform 0.1s ease-out;
        pointer-events: none;
        user-select: none;
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
    container.innerHTML = ""; 
    const letters = [];
    
    // 计算总宽度，使其居中
    const totalWidth = word.length * (fontSize * crowding * 0.6);

    for (let i = 0; i < word.length; i++) {{
        const span = document.createElement("span");
        span.className = "letter";
        span.innerText = word[i];
        
        // 基础横向位置：居中计算
        span.dataset.baseX = (i * (fontSize * crowding * 0.6)) - (totalWidth / 2) + (totalWidth / word.length / 2);
        span.dataset.phase = Math.random() * Math.PI * 2; // 随机波浪相位
        container.appendChild(span);
        letters.push(span);
    }}

    // 进阶3：鼠标监听 (用于物理斥力)
    let mouseX = -1000;
    let mouseY = -1000;

    window.addEventListener('mousemove', (e) => {{
        const rect = container.getBoundingClientRect();
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
    }});

    // 鼠标离开时重置位置
    window.addEventListener('mouseleave', () => {{
        mouseX = -1000;
        mouseY = -1000;
    }});

    // 动画循环
    let time = 0;
    function animate() {{
        time += 0.05;
        
        letters.forEach((letter) => {{
            // 基础排版
            let x = parseFloat(letter.dataset.baseX);
            let phase = parseFloat(letter.dataset.phase);
            
            // 波浪起伏
            let y = Math.sin(time + phase) * gravity;
            
            // 拥挤度带来的旋转（越拥挤越歪斜）
            let rotation = (crowding - 1.0) * 45 * Math.sin(time * 0.5 + phase);

            // --- 进阶：鼠标斥力计算 ---
            const containerCenter = container.offsetWidth / 2;
            const containerCenterY = container.offsetHeight / 2;
            
            // 计算字母在屏幕上的近似绝对位置
            const letterX = containerCenter + x;
            const letterY = containerCenterY + y;

            const dx = letterX - mouseX;
            const dy = letterY - mouseY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            // 斥力半径 (200px)
            const forceRadius = 200;
            let pushX = 0;
            let pushY = 0;

            if (distance < forceRadius && distance > 0) {{
                // 距离越近，推力越大
                const force = (forceRadius - distance) / forceRadius;
                // 计算单位方向向量并乘以力
                pushX = (dx / distance) * force * 80; 
                pushY = (dy / distance) * force * 80;
            }}

            // 应用所有变换
            letter.style.transform = `translate(${{x + pushX}}px, ${{y + pushY}}px) rotate(${{rotation}}deg)`;
        }});
        
        requestAnimationFrame(animate);
    }}

    animate();
</script>

</body>
</html>
"""

# 将 HTML 渲染到 Streamlit 中，设置高度
components.html(html_code, height=520)