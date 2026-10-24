# /// script
# requires-python = ">=3.10"
# dependencies = ["streamlit"]
# ///

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Kinetic Audio Typography", layout="wide")

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kinetic Audio Typography</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;800&display=swap" rel="stylesheet">
    <style>
        :root { --bg: #0a0a0f; --primary: #00ffcc; }
        body, html {
            margin: 0; padding: 0; width: 100%; height: 100vh; overflow: hidden;
            background-color: var(--bg);
            background-image: radial-gradient(circle at 50% 50%, rgba(20, 20, 35, 1) 0%, #0a0a0f 100%);
            font-family: 'Outfit', sans-serif; color: white;
        }
        #canvas-container { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        
        .glass-panel {
            position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); z-index: 10;
            background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 24px; padding: 20px 36px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6); display: flex; gap: 24px; align-items: center;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .glass-panel:hover { transform: translateX(-50%) translateY(-4px); border-color: rgba(255, 255, 255, 0.15); }
        
        .control-group { display: flex; flex-direction: column; gap: 8px; }
        .control-group label { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: rgba(255, 255, 255, 0.5); font-weight: 500; }
        
        input[type="text"] {
            background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1); color: white;
            padding: 10px 16px; border-radius: 12px; font-family: 'Outfit', sans-serif;
            font-size: 15px; font-weight: 500; outline: none; transition: all 0.3s ease; width: 130px;
        }
        input[type="text"]:focus { border-color: #00ffcc; box-shadow: 0 0 15px rgba(0, 255, 204, 0.2); }

        input[type="range"] { -webkit-appearance: none; width: 100px; background: transparent; }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none; height: 14px; width: 14px; border-radius: 50%;
            background: #fff; cursor: pointer; box-shadow: 0 0 12px rgba(255, 255, 255, 0.8); margin-top: -5px;
        }
        input[type="range"]::-webkit-slider-runnable-track { width: 100%; height: 4px; background: rgba(255, 255, 255, 0.15); border-radius: 2px; cursor: pointer; }

        .color-picker-wrapper { display: flex; gap: 8px; }
        input[type="color"] {
            -webkit-appearance: none; border: none; width: 28px; height: 28px; border-radius: 50%;
            cursor: pointer; background: none; padding: 0;
        }
        input[type="color"]::-webkit-color-swatch-wrapper { padding: 0; }
        input[type="color"]::-webkit-color-swatch { border: 2px solid rgba(255, 255, 255, 0.3); border-radius: 50%; }

        .audio-btn {
            background: rgba(0, 255, 204, 0.1); border: 1px solid #00ffcc; color: #00ffcc;
            padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 12px;
            text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s;
        }
        .audio-btn.active { background: #00ffcc; color: #000; box-shadow: 0 0 15px #00ffcc; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="glass-panel">
        <div class="control-group">
            <label>Text</label>
            <input type="text" id="textInput" value="SYNTHESIA" maxlength="15">
        </div>
        <div class="control-group">
            <label>Explosion</label>
            <input type="range" id="cohesionInput" min="0" max="200" value="200">
        </div>
        <div class="control-group">
            <label>Scale</label>
            <input type="range" id="scaleInput" min="0.5" max="2" value="1" step="0.01">
        </div>
        <div class="control-group">
            <label>Gradient</label>
            <div class="color-picker-wrapper">
                <input type="color" id="colorStart" value="#00ffcc">
                <input type="color" id="colorEnd" value="#ff007f">
            </div>
        </div>
        <div class="control-group">
            <label>Audio</label>
            <button class="audio-btn" id="audioToggle">Enable Sound</button>
        </div>
    </div>

    <script>
        // ================= 1. 混合合成引擎 (Morphing Synthesizer) =================
        let audioCtx = null;
        let isAudioEnabled = false;
        let masterFilter = null; 
        let delayNode = null; 

        const majorPentatonic = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25, 783.99];
        const minorPentatonic = [220.00, 261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25];

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                
                masterFilter = audioCtx.createBiquadFilter();
                masterFilter.type = "lowpass";
                masterFilter.Q.value = 1.0; 
                
                delayNode = audioCtx.createDelay(1.0);
                delayNode.delayTime.value = 0.5;
                const feedback = audioCtx.createGain();
                feedback.gain.value = 0.3;
                
                delayNode.connect(feedback);
                feedback.connect(delayNode);
                
                masterFilter.connect(delayNode);
                delayNode.connect(audioCtx.destination);
                masterFilter.connect(audioCtx.destination);
            }
            if (audioCtx.state === 'suspended') audioCtx.resume();
        }

        // 将颜色转化为各个乐器的权重（%）
        function getColorWeights(hexColor) {
            let r = parseInt(hexColor.slice(1, 3), 16) / 255;
            let g = parseInt(hexColor.slice(3, 5), 16) / 255;
            let b = parseInt(hexColor.slice(5, 7), 16) / 255;
            let max = Math.max(r, g, b), min = Math.min(r, g, b);
            let h = 0;
            if (max !== min) {
                if (max === r) h = (g - b) / (max - min) + (g < b ? 6 : 0);
                else if (max === g) h = (b - r) / (max - min) + 2;
                else h = (r - g) / (max - min) + 4;
                h /= 6;
            }

            // 计算到三个基准色相的距离
            // 吉他 (红/粉): 中心在 0 (或 1)
            let distGuitar = Math.min(Math.abs(h - 0), Math.abs(h - 1));
            // 笛子 (绿/青): 中心在 0.33
            let distFlute = Math.abs(h - 0.33);
            // 钢琴 (蓝/紫): 中心在 0.66
            let distPiano = Math.abs(h - 0.66);

            // 将距离映射到权重 (0.0 - 1.0)，距离越近权重越高
            // 这里使用简单的线性衰减，0.33 是一半色轮的范围
            let wGuitar = Math.max(0, 1 - distGuitar / 0.33);
            let wFlute = Math.max(0, 1 - distFlute / 0.33);
            let wPiano = Math.max(0, 1 - distPiano / 0.33);

            // 归一化权重，确保总和为 1
            let total = wGuitar + wFlute + wPiano;
            if (total === 0) total = 1; // 防止除以零

            return {
                guitar: wGuitar / total,
                flute: wFlute / total,
                piano: wPiano / total,
                hue: h // 返回色相用于判断冷暖调
            };
        }

        function playTone(baseFreqIndex, cohesionFactor, weights, isMinorTone) {
            if (!isAudioEnabled || !audioCtx) return;
            
            const now = audioCtx.currentTime;
            const scatter = 1 - cohesionFactor; 
            const releaseTime = 0.2 + (scatter * 3.0);
            const attackTime = 0.01;
            const maxVolume = 0.15; // 整体音量，因为三路混合，所以调低一点

            const freqArray = isMinorTone ? minorPentatonic : majorPentatonic;
            let baseFreq = freqArray[baseFreqIndex % freqArray.length];
            if (scatter > 0.5) baseFreq *= 0.8;

            // --- 动态生成三种乐器并混合 ---
            const instruments = ['piano', 'flute', 'guitar'];
            
            instruments.forEach(inst => {
                const weight = weights[inst];
                if (weight < 0.01) return; // 权重太低则不发声，节省资源

                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();

                if (inst === 'piano') {
                    osc.type = 'triangle';
                } else if (inst === 'flute') {
                    osc.type = 'sine';
                } else if (inst === 'guitar') {
                    // 吉他/竖琴：混合三角波和正弦波泛音
                    osc.type = 'triangle';
                    // 简单模拟：我们用高频正弦波代替原本的泛音，直接连接到同一个gain
                    const oscHarm = audioCtx.createOscillator();
                    const harmGain = audioCtx.createGain();
                    oscHarm.type = 'sine';
                    oscHarm.frequency.setValueAtTime(baseFreq * 2.5, now);
                    harmGain.gain.setValueAtTime(weight * maxVolume * 0.3, now);
                    harmGain.gain.exponentialRampToValueAtTime(0.001, now + releaseTime);
                    oscHarm.connect(harmGain);
                    harmGain.connect(masterFilter);
                    oscHarm.start(now);
                    oscHarm.stop(now + releaseTime);
                }

                osc.frequency.setValueAtTime(baseFreq, now);

                // 包络与音量应用权重
                gain.gain.setValueAtTime(0, now);
                gain.gain.linearRampToValueAtTime(weight * maxVolume, now + attackTime);
                gain.gain.exponentialRampToValueAtTime(0.001, now + releaseTime);

                osc.connect(gain);
                gain.connect(masterFilter);
                
                osc.start(now);
                osc.stop(now + releaseTime);
            });
        }

        document.getElementById('audioToggle').addEventListener('click', (e) => {
            initAudio();
            isAudioEnabled = !isAudioEnabled;
            e.target.innerText = isAudioEnabled ? 'Sound On' : 'Enable Sound';
            e.target.classList.toggle('active');
            if(isAudioEnabled) {
                // 混合两个颜色的权重
                const wStart = getColorWeights(colorStart);
                const wEnd = getColorWeights(colorEnd);
                const finalWeights = {
                    guitar: (wStart.guitar + wEnd.guitar) / 2,
                    flute: (wStart.flute + wEnd.flute) / 2,
                    piano: (wStart.piano + wEnd.piano) / 2
                };
                // 判断是否小调 (取平均色相)
                const avgHue = (wStart.hue + wEnd.hue) / 2;
                const isMinorTone = (avgHue < 0.15 || avgHue > 0.85);
                playTone(3, 1.0, finalWeights, isMinorTone);
            }
        });

        // ================= 2. Three.js 核心 =================
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x0a0a0f, 0.0015);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 140;

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        let particleSystem = null;
        let positionsArray = null;
        let targetPositions = [];
        let velocities = []; 
        let currentWord = "SYNTHESIA";
        let colorStart = "#00ffcc";
        let colorEnd = "#ff007f";
        
        let targetCohesion = 1.0;
        let currentCohesion = 1.0; 
        let targetScale = 1.0;
        let currentScale = 1.0; 
        
        const mouse3D = new THREE.Vector3(0, 0, 0);
        const raycaster = new THREE.Raycaster();
        const mouse2D = new THREE.Vector2(0, 0);

        // ================= 3. 粒子生成 =================
        function updateParticles(word, hexStart, hexEnd, isNewText = false) {
            const c = document.createElement('canvas');
            const ctx = c.getContext('2d');
            c.width = 800; c.height = 300;
            ctx.fillStyle = 'white';
            
            let baseFontSize = 160;
            if (word.length > 5) baseFontSize = 160 * (5 / word.length);
            
            ctx.font = `bold ${baseFontSize}px "Outfit", sans-serif`;
            ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
            ctx.fillText(word, 400, 150);

            const imageData = ctx.getImageData(0, 0, c.width, c.height).data;
            const newTargets = [];
            const newColors = [];

            const cStart = new THREE.Color(hexStart);
            const cEnd = new THREE.Color(hexEnd);
            const tempColor = new THREE.Color();

            for (let y = 0; y < c.height; y += 3) {
                for (let x = 0; x < c.width; x += 3) {
                    if (imageData[(y * c.width + x) * 4 + 3] > 128) {
                        newTargets.push({ x: (x - 400) * 0.5, y: -(y - 150) * 0.5, z: (Math.random() - 0.5) * 15 });
                        tempColor.copy(cStart).lerp(cEnd, x / 800);
                        newColors.push(tempColor.r, tempColor.g, tempColor.b);
                    }
                }
            }

            if (particleSystem && isNewText) {
                if (newTargets.length > targetPositions.length) {
                    const diff = newTargets.length - targetPositions.length;
                    const pos = particleSystem.geometry.attributes.position.array;
                    const col = particleSystem.geometry.attributes.color.array;
                    
                    const newPos = new Float32Array(pos.length + diff * 3);
                    newPos.set(pos);
                    for(let i=0; i<diff; i++) {
                        newPos[pos.length + i*3] = (Math.random()-0.5)*100;
                        newPos[pos.length + i*3+1] = (Math.random()-0.5)*100;
                        newPos[pos.length + i*3+2] = (Math.random()-0.5)*100;
                    }
                    particleSystem.geometry.setAttribute('position', new THREE.BufferAttribute(newPos, 3));
                    
                    const newCol = new Float32Array(col.length + diff * 3);
                    newCol.set(col);
                    for(let i=0; i<diff; i++) {
                        newCol[col.length + i*3] = 1; newCol[col.length + i*3+1] = 1; newCol[col.length + i*3+2] = 1;
                    }
                    particleSystem.geometry.setAttribute('color', new THREE.BufferAttribute(newCol, 3));
                }
                
                const colorArray = particleSystem.geometry.attributes.color.array;
                for(let i=0; i<Math.min(newColors.length, colorArray.length); i++) {
                    colorArray[i] = newColors[i];
                }
                particleSystem.geometry.attributes.color.needsUpdate = true;

                targetPositions = newTargets;
                while(velocities.length < newTargets.length) velocities.push({ x: 0, y: 0, z: 0 });
                positionsArray = particleSystem.geometry.attributes.position.array;

            } else {
                if (particleSystem) {
                    scene.remove(particleSystem);
                    particleSystem.geometry.dispose();
                    particleSystem.material.dispose();
                }
                const initPositions = new Float32Array(newTargets.length * 3);
                velocities = [];
                for (let i = 0; i < newTargets.length; i++) {
                    initPositions[i*3] = (Math.random() - 0.5) * 200;
                    initPositions[i*3+1] = (Math.random() - 0.5) * 200;
                    initPositions[i*3+2] = (Math.random() - 0.5) * 200;
                    velocities.push({ x: (Math.random()-0.5)*2, y: (Math.random()-0.5)*2, z: (Math.random()-0.5)*2 });
                }

                const geometry = new THREE.BufferGeometry();
                geometry.setAttribute('position', new THREE.BufferAttribute(initPositions, 3));
                geometry.setAttribute('color', new THREE.Float32BufferAttribute(newColors, 3));
                
                const material = new THREE.PointsMaterial({
                    size: 1.5, transparent: true, opacity: 0.85, vertexColors: true,
                    blending: THREE.AdditiveBlending, depthWrite: false
                });

                particleSystem = new THREE.Points(geometry, material);
                scene.add(particleSystem);
                
                targetPositions = newTargets;
                positionsArray = particleSystem.geometry.attributes.position.array;
            }
        }

        updateParticles(currentWord, colorStart, colorEnd, false);

        // ================= 4. UI 监听 =================
        document.getElementById('textInput').addEventListener('input', (e) => {
            if (e.target.value.trim() !== "") {
                currentWord = e.target.value;
                updateParticles(currentWord, colorStart, colorEnd, true);
                if (isAudioEnabled) {
                    const wStart = getColorWeights(colorStart);
                    const wEnd = getColorWeights(colorEnd);
                    const finalWeights = {
                        guitar: (wStart.guitar + wEnd.guitar) / 2,
                        flute: (wStart.flute + wEnd.flute) / 2,
                        piano: (wStart.piano + wEnd.piano) / 2
                    };
                    const avgHue = (wStart.hue + wEnd.hue) / 2;
                    const isMinorTone = (avgHue < 0.15 || avgHue > 0.85);
                    playTone(currentWord.length, currentCohesion, finalWeights, isMinorTone);
                }
            }
        });

        document.getElementById('cohesionInput').addEventListener('input', (e) => {
            targetCohesion = e.target.value / 200;
        });

        document.getElementById('scaleInput').addEventListener('input', (e) => {
            targetScale = e.target.value;
        });

        document.getElementById('colorStart').addEventListener('input', (e) => {
            colorStart = e.target.value;
            updateParticles(currentWord, colorStart, colorEnd, true);
        });

        document.getElementById('colorEnd').addEventListener('input', (e) => {
            colorEnd = e.target.value;
            updateParticles(currentWord, colorStart, colorEnd, true);
        });

        // ================= 5. 鼠标监听与音效触发 =================
        let lastToneTime = 0;
        
        window.addEventListener('mousemove', (e) => {
            mouse2D.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse2D.y = -(e.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse2D, camera);
            const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
            const intersection = new THREE.Vector3();
            raycaster.ray.intersectPlane(plane, intersection);
            mouse3D.copy(intersection);

            const now = Date.now();
            if (now - lastToneTime > 120) { 
                const index = Math.floor(((mouse2D.y + 1) / 2) * 9);
                const safeIndex = Math.max(0, Math.min(8, index));
                
                // 混合双色权重
                const wStart = getColorWeights(colorStart);
                const wEnd = getColorWeights(colorEnd);
                const finalWeights = {
                    guitar: (wStart.guitar + wEnd.guitar) / 2,
                    flute: (wStart.flute + wEnd.flute) / 2,
                    piano: (wStart.piano + wEnd.piano) / 2
                };
                const avgHue = (wStart.hue + wEnd.hue) / 2;
                const isMinorTone = (avgHue < 0.15 || avgHue > 0.85);

                playTone(safeIndex, currentCohesion, finalWeights, isMinorTone);
                lastToneTime = now;
            }
        });

        // ================= 6. 物理引擎与音频滤波器 =================
        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);
            if (!particleSystem) return;

            currentCohesion += (targetCohesion - currentCohesion) * 0.15;
            currentScale += (targetScale - currentScale) * 0.08; 

            if (masterFilter && audioCtx) {
                const targetFilterFreq = 500 + (currentCohesion * 3000);
                masterFilter.frequency.setTargetAtTime(targetFilterFreq, audioCtx.currentTime, 0.1);
            }

            particleSystem.rotation.y += (mouse2D.x * 0.2 - particleSystem.rotation.y) * 0.05;
            particleSystem.rotation.x += (mouse2D.y * 0.2 - particleSystem.rotation.x) * 0.05;
            
            particleSystem.scale.set(currentScale, currentScale, currentScale);

            for (let i = 0; i < positionsArray.length; i += 3) {
                const idx = i / 3;
                let px = positionsArray[i];
                let py = positionsArray[i+1];
                let pz = positionsArray[i+2];

                let vx = velocities[idx].x;
                let vy = velocities[idx].y;
                let vz = velocities[idx].z;

                if (currentCohesion > 0.05) {
                    const target = targetPositions[idx] || {x:0, y:0, z:0};
                    const stiffness = 0.08 * currentCohesion;
                    const damping = 0.85; 

                    vx += (target.x - px) * stiffness;
                    vy += (target.y - py) * stiffness;
                    vz += (target.z - pz) * stiffness;

                    vx *= damping; vy *= damping; vz *= damping;

                    const dx = px - mouse3D.x;
                    const dy = py - mouse3D.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    
                    if (dist < 25 && dist > 0) {
                        const force = (25 - dist) / 25; 
                        vx += (dx / dist) * Math.pow(force, 2) * 4; 
                        vy += (dy / dist) * Math.pow(force, 2) * 4;
                    }

                } else {
                    vx *= 0.99; vy *= 0.99; vz *= 0.99;
                    
                    const dx = px - mouse3D.x;
                    const dy = py - mouse3D.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 40) {
                         vx += (dx / dist) * 0.5;
                         vy += (dy / dist) * 0.5;
                    }
                }

                px += vx; py += vy; pz += vz;

                velocities[idx].x = vx;
                velocities[idx].y = vy;
                velocities[idx].z = vz;

                positionsArray[i] = px;
                positionsArray[i+1] = py;
                positionsArray[i+2] = pz;
            }

            particleSystem.geometry.attributes.position.needsUpdate = true;
            renderer.render(scene, camera);
        }

        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

st.markdown("""
    <style>
        .block-container {padding: 0rem !important;}
        header {visibility: hidden;}
        iframe {height: 100vh !important;}
    </style>
""", unsafe_allow_html=True)

components.html(html_code, height=800, scrolling=False)