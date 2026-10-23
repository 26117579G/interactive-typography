# /// script
# requires-python = ">=3.10"
# dependencies = ["streamlit"]
# ///

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Particle Typography", page_icon="✨", layout="wide")

st.title("✨ 3D Kinetic Typography")
st.markdown("Type a word and interact with the 3D particles. **Drag to rotate, scroll to zoom.**")

col1, col2, col3, col4 = st.columns(4)

with col1:
    user_word = st.text_input("Text", value="HELLO")
with col2:
    color = st.color_picker("Particle Color", "#00ffcc")
with col3:
    size = st.slider("Particle Size", min_value=0.5, max_value=3.0, value=1.2, step=0.1)
with col4:
    cohesion = st.slider("Cohesion (聚拢程度)", min_value=0, max_value=100, value=100, step=5)

if not user_word.strip():
    st.warning("⚠️ Please enter a valid word.")
    st.stop()

# 使用 Three.js 构建 3D 粒子
html_code = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ margin: 0; overflow: hidden; background-color: #050510; }}
    canvas {{ display: block; }}
</style>
<!-- 引入 Three.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

<script>
    const userWord = "{user_word}";
    const particleColor = "{color}";
    const particleSize = {size};
    const targetCohesion = {cohesion} / 100; // 0.0 到 1.0

    // 1. 设置场景、相机、渲染器
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050510, 0.002);
    
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 60;

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(window.innerWidth, 500); // 匹配 Streamlit iframe 高度
    document.body.appendChild(renderer.domElement);

    // 2. 生成文字粒子数据
    // 用一个隐藏的 2D canvas 把文字画出来，读取像素点转化为 3D 坐标
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 600;
    canvas.height = 200;
    ctx.fillStyle = 'white';
    ctx.font = 'bold 120px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(userWord, 300, 100);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    const particlesGeometry = new THREE.BufferGeometry();
    const positions = [];
    const targetPositions = []; // 用于聚拢
    const velocities = []; // 用于爆炸

    // 扫描像素
    for (let y = 0; y < canvas.height; y += 2) {{
        for (let x = 0; x < canvas.width; x += 2) {{
            const index = (y * canvas.width + x) * 4;
            if (data[index + 3] > 128) {{ // 如果像素不透明
                // 转换到居中坐标系
                const tx = (x - 300) * 0.5;
                const ty = -(y - 100) * 0.5;
                const tz = (Math.random() - 0.5) * 10; // 给一点厚度
                
                targetPositions.push({{ x: tx, y: ty, z: tz }});
                
                // 初始位置随机发散在空间中
                positions.push(
                    (Math.random() - 0.5) * 200,
                    (Math.random() - 0.5) * 200,
                    (Math.random() - 0.5) * 200
                );
                
                // 爆炸速度
                velocities.push({{
                    x: (Math.random() - 0.5) * 0.5,
                    y: (Math.random() - 0.5) * 0.5,
                    z: (Math.random() - 0.5) * 0.5
                }});
            }}
        }}
    }}

    particlesGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));

    // 3. 粒子材质
    const particlesMaterial = new THREE.PointsMaterial({{
        color: particleColor,
        size: particleSize,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending,
        depthWrite: false
    }});

    const particleSystem = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particleSystem);

    // 4. 鼠标交互数据
    let mouseX = 0;
    let mouseY = 0;
    document.addEventListener('mousemove', (e) => {{
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    }});

    // 5. 动画循环
    const clock = new THREE.Clock();
    const positionsArray = particlesGeometry.attributes.position.array;

    function animate() {{
        requestAnimationFrame(animate);
        const time = clock.getElapsedTime();

        // 旋转整个场景
        particleSystem.rotation.y = mouseX * 0.5;
        particleSystem.rotation.x = mouseY * 0.5;

        // 更新粒子位置 (向目标位置移动或飘散)
        for (let i = 0; i < positionsArray.length; i += 3) {{
            const idx = i / 3;
            const tx = targetPositions[idx].x;
            const ty = targetPositions[idx].y;
            const tz = targetPositions[idx].z;

            let px = positionsArray[i];
            let py = positionsArray[i+1];
            let pz = positionsArray[i+2];

            if (targetCohesion > 0.1) {{
                // 聚拢逻辑 (弹簧阻尼)
                px += (tx - px) * 0.05 * targetCohesion;
                py += (ty - py) * 0.05 * targetCohesion;
                pz += (tz - pz) * 0.05 * targetCohesion;
            }} else {{
                // 爆炸/漂移逻辑
                px += velocities[idx].x * (1 - targetCohesion);
                py += velocities[idx].y * (1 - targetCohesion);
                pz += velocities[idx].z * (1 - targetCohesion);
            }}
            
            // 鼠标排斥气场 (在 3D 空间产生轻微扭曲)
            const distToCenter = Math.sqrt(px*px + py*py);
            if (distToCenter < 50) {{
                 px += mouseX * 0.5;
                 py += mouseY * 0.5;
            }}

            positionsArray[i] = px;
            positionsArray[i+1] = py;
            positionsArray[i+2] = pz;
        }}

        particlesGeometry.attributes.position.needsUpdate = true;
        
        // 动态颜色微调（随时间和鼠标变化）
        particlesMaterial.size = particleSize + Math.sin(time * 2) * 0.2;

        renderer.render(scene, camera);
    }}

    animate();

    // 响应窗口缩放
    window.addEventListener('resize', () => {{
        camera.aspect = window.innerWidth / 500;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, 500);
    }});
</script>

</body>
</html>
"""

components.html(html_code, height=520)