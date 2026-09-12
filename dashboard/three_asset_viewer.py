"""
Interactive 3D WebGL Asset Inspector for Wind Turbines and Solar Arrays
========================================================================
Renders rotatable, real-time 3D models using Three.js inside Streamlit components.
- Wind Turbine: Rotatable 3D tower, nacelle, hub, and 3 spinning blades animated at SCADA RPM.
- Solar Panel: Rotatable 3D solar table with tilt angle, grid cells, sunbeams, and dust soiling opacity.
"""

import time
import streamlit as st
import streamlit.components.v1 as components

def render_3d_wind_turbine(rpm: float = 15.0, gearbox_temp: float = 65.0, health_status: str = "Healthy", height: int = 460):
    """Render a realistic 3D Wind Turbine model with scattered perimeter callout cards and dynamic SVG leader lines to origin points."""
    
    speed_factor = max(0.01, min(0.35, (rpm / 1800.0) * 0.18)) if rpm > 0 else 0.002
    gearbox_color = "0xef4444" if gearbox_temp > 80 else ("0xf59e0b" if gearbox_temp > 65 else "0xe2e8f0")
    badge_color = "#ef4444" if gearbox_temp > 80 else ("#f59e0b" if gearbox_temp > 65 else "#10b981")
    ts = time.time()

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <!-- Cache buster timestamp: {ts} -->
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; font-family: 'Segoe UI', Tahoma, sans-serif; }}
        #info {{
            position: absolute; top: 14px; left: 14px; color: #0f172a; font-size: 14px; line-height: 1.6;
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px);
            padding: 16px 20px; border-radius: 12px; border: 2px solid #cbd5e1;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15); z-index: 10; min-width: 220px;
        }}
        .annotation {{
            position: absolute; pointer-events: none;
            background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(8px);
            border: 1.5px solid rgba(56, 189, 248, 0.7); color: #ffffff;
            padding: 6px 12px; border-radius: 8px; font-size: 11px; line-height: 1.4;
            box-shadow: 0 6px 18px rgba(0,0,0,0.35); white-space: nowrap; z-index: 5;
        }}
        .annotation-title {{ font-weight: 800; color: #38bdf8; font-size: 11.5px; margin-bottom: 2px; letter-spacing: 0.3px; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info">
        <b style="color:#0f172a; font-size:15px; letter-spacing:0.3px;">3D INDUSTRIAL WIND TURBINE</b><br>
        Generator Speed: <b>{rpm:.1f} RPM</b><br>
        Gearbox Temp: <b>{gearbox_temp:.1f} °C</b><br>
        Health Status: <b style="color:{badge_color};">{health_status}</b><br>
        <span style="color:#64748b; font-size:11px;">Drag to rotate | Scroll to zoom</span>
    </div>

    <!-- SVG Canvas Overlay for Leader Lines -->
    <svg id="svg-overlay" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:4;">
        <line id="line-nacelle" stroke="{badge_color}" stroke-width="2.5" stroke-dasharray="6,4" />
        <circle id="dot-nacelle" r="6" fill="{badge_color}" stroke="#ffffff" stroke-width="1.5" />

        <line id="line-rotor" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4" />
        <circle id="dot-rotor" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />

        <line id="line-tower" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4" />
        <circle id="dot-tower" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />

        <line id="line-base" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4" />
        <circle id="dot-base" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />
    </svg>

    <!-- Perimeter-Scattered Callout Badges -->
    <div id="anno-nacelle" class="annotation" style="top: 14px; right: 14px;">
        <div class="annotation-title">GEARBOX & GENERATOR HOUSING</div>
        <div>Temp: <b style="color:{badge_color};">{gearbox_temp:.1f} °C</b></div>
    </div>

    <div id="anno-rotor" class="annotation" style="top: 85px; right: 14px;">
        <div class="annotation-title">AERODYNAMIC ROTOR & BLADES</div>
        <div>Rotor Speed: <b>{rpm:.1f} RPM</b></div>
    </div>

    <div id="anno-tower" class="annotation" style="bottom: 14px; right: 14px;">
        <div class="annotation-title">STEEL SUPPORT TOWER</div>
        <div>13m Tapered Tubular Steel</div>
    </div>

    <div id="anno-base" class="annotation" style="bottom: 14px; left: 14px;">
        <div class="annotation-title">FOUNDATION BASE</div>
        <div>Concrete Anchor Pad</div>
    </div>

    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xdbeafe);
        scene.fog = new THREE.FogExp2(0xdbeafe, 0.015);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 9, 24);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.maxPolarAngle = Math.PI / 2 - 0.02;

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
        scene.add(ambientLight);

        const sunLight = new THREE.DirectionalLight(0xfffbeb, 1.2);
        sunLight.position.set(15, 25, 12);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 1024;
        sunLight.shadow.mapSize.height = 1024;
        scene.add(sunLight);

        // Ground Floor
        const grassGeo = new THREE.PlaneGeometry(60, 60);
        const grassMat = new THREE.MeshStandardMaterial({{ color: 0x3d5c2e, roughness: 0.95 }});
        const grass = new THREE.Mesh(grassGeo, grassMat);
        grass.rotation.x = -Math.PI / 2;
        grass.receiveShadow = true;
        scene.add(grass);

        // Dirt Patch
        const dirtGeo = new THREE.CylinderGeometry(4.5, 5.5, 0.15, 32);
        const dirtMat = new THREE.MeshStandardMaterial({{ color: 0x5a534c, roughness: 0.9 }});
        const dirt = new THREE.Mesh(dirtGeo, dirtMat);
        dirt.position.y = 0.07;
        dirt.receiveShadow = true;
        scene.add(dirt);

        // Concrete Base
        const baseGeo = new THREE.CylinderGeometry(1.6, 2.0, 0.5, 32);
        const baseMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, roughness: 0.7 }});
        const base = new THREE.Mesh(baseGeo, baseMat);
        base.position.y = 0.4;
        base.castShadow = true;
        scene.add(base);

        // Tower
        const towerGeo = new THREE.CylinderGeometry(0.55, 1.0, 13, 32);
        const towerMat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.25, metalness: 0.3 }});
        const tower = new THREE.Mesh(towerGeo, towerMat);
        tower.position.y = 6.9;
        tower.castShadow = true;
        scene.add(tower);

        // Nacelle Housing
        const nacelleGeo = new THREE.BoxGeometry(1.8, 1.5, 3.8);
        const nacelleMat = new THREE.MeshStandardMaterial({{ color: {gearbox_color}, roughness: 0.3, metalness: 0.4 }});
        const nacelle = new THREE.Mesh(nacelleGeo, nacelleMat);
        nacelle.position.set(0, 13.5, 0.4);
        nacelle.castShadow = true;
        scene.add(nacelle);

        // Hub & Blades
        const hubGeo = new THREE.ConeGeometry(0.85, 1.4, 32);
        hubGeo.rotateX(Math.PI / 2);
        const hubMat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.2, metalness: 0.5 }});

        const rotorGroup = new THREE.Group();
        rotorGroup.position.set(0, 13.5, -1.45);
        scene.add(rotorGroup);

        const hub = new THREE.Mesh(hubGeo, hubMat);
        rotorGroup.add(hub);

        const bladeMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, roughness: 0.15 }});
        const tipMat = new THREE.MeshStandardMaterial({{ color: 0xdc2626 }});

        for (let i = 0; i < 3; i++) {{
            const bladeGroup = new THREE.Group();
            bladeGroup.rotation.z = (i * Math.PI * 2) / 3;

            const bladeGeo = new THREE.BoxGeometry(0.28, 7.2, 0.08);
            bladeGeo.translate(0, 3.6, 0);
            const blade = new THREE.Mesh(bladeGeo, bladeMat);
            blade.castShadow = true;
            bladeGroup.add(blade);

            const tipGeo = new THREE.BoxGeometry(0.29, 0.8, 0.09);
            tipGeo.translate(0, 6.8, 0);
            const tip = new THREE.Mesh(tipGeo, tipMat);
            bladeGroup.add(tip);

            rotorGroup.add(bladeGroup);
        }}

        // Scattered Annotations & Leader Line Connectors
        const annotations = [
            {{
                card: document.getElementById('anno-nacelle'),
                line: document.getElementById('line-nacelle'),
                dot: document.getElementById('dot-nacelle'),
                position: new THREE.Vector3(0, 13.8, 0.4)
            }},
            {{
                card: document.getElementById('anno-rotor'),
                line: document.getElementById('line-rotor'),
                dot: document.getElementById('dot-rotor'),
                position: new THREE.Vector3(0, 13.5, -1.45)
            }},
            {{
                card: document.getElementById('anno-tower'),
                line: document.getElementById('line-tower'),
                dot: document.getElementById('dot-tower'),
                position: new THREE.Vector3(0, 7.0, 0)
            }},
            {{
                card: document.getElementById('anno-base'),
                line: document.getElementById('line-base'),
                dot: document.getElementById('dot-base'),
                position: new THREE.Vector3(0, 0.4, 0)
            }}
        ];

        function updateAnnotations() {{
            const tempV = new THREE.Vector3();
            annotations.forEach(anno => {{
                if (!anno.card || !anno.line || !anno.dot) return;
                tempV.copy(anno.position);
                tempV.project(camera);

                if (tempV.z >= 1) {{
                    anno.card.style.display = 'none';
                    anno.line.style.display = 'none';
                    anno.dot.style.display = 'none';
                    return;
                }}

                anno.card.style.display = 'block';
                anno.line.style.display = 'block';
                anno.dot.style.display = 'block';

                const originX = (tempV.x * .5 + .5) * window.innerWidth;
                const originY = (tempV.y * -.5 + .5) * window.innerHeight;

                const rect = anno.card.getBoundingClientRect();
                const cardX = (rect.left < window.innerWidth / 2) ? rect.right : rect.left;
                const cardY = rect.top + rect.height / 2;

                anno.line.setAttribute('x1', cardX);
                anno.line.setAttribute('y1', cardY);
                anno.line.setAttribute('x2', originX);
                anno.line.setAttribute('y2', originY);

                anno.dot.setAttribute('cx', originX);
                anno.dot.setAttribute('cy', originY);
            }});
        }}

        // Animation Loop
        function animate() {{
            requestAnimationFrame(animate);
            rotorGroup.rotation.z += {speed_factor};
            controls.update();
            updateAnnotations();
            renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
            updateAnnotations();
        }});
    </script>
</body>
</html>"""
    
    components.html(html_code, height=height, scrolling=False)


def render_3d_solar_panel(soiling_factor: float = 1.0, irradiance: float = 850.0, panel_temp: float = 45.0, health_status: str = "Healthy", height: int = 460):
    """Render a realistic 3D Photovoltaic Solar Array with scattered perimeter callout cards and dynamic SVG leader lines to origin points."""
    
    dust_opacity = max(0.0, min(0.32, (1.0 - soiling_factor) * 0.7))
    badge_color = "#ef4444" if health_status == "Critical" else ("#f59e0b" if health_status == "Warning" else "#10b981")
    ts = time.time()

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <!-- Cache buster timestamp: {ts} -->
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; font-family: 'Segoe UI', Tahoma, sans-serif; }}
        #info {{
            position: absolute; top: 14px; left: 14px; color: #0f172a; font-size: 14px; line-height: 1.6;
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px);
            padding: 16px 20px; border-radius: 12px; border: 2px solid #cbd5e1;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15); z-index: 10; min-width: 220px;
        }}
        .annotation {{
            position: absolute; pointer-events: none;
            background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(8px);
            border: 1.5px solid rgba(56, 189, 248, 0.7); color: #ffffff;
            padding: 6px 12px; border-radius: 8px; font-size: 11px; line-height: 1.4;
            box-shadow: 0 6px 18px rgba(0,0,0,0.35); white-space: nowrap; z-index: 5;
        }}
        .annotation-title {{ font-weight: 800; color: #38bdf8; font-size: 11.5px; margin-bottom: 2px; letter-spacing: 0.3px; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info">
        <b style="color:#0f172a; font-size:15px; letter-spacing:0.3px;">3D COMMERCIAL SOLAR PV ARRAY</b><br>
        Solar Irradiance: <b>{irradiance:.1f} W/m²</b><br>
        Module Temp: <b>{panel_temp:.1f} °C</b><br>
        Soiling Ratio: <b>{soiling_factor:.2f}</b> (1.0 = Clean)<br>
        Health Status: <b style="color:{badge_color};">{health_status}</b><br>
        <span style="color:#64748b; font-size:11px;">Drag to rotate | Scroll to zoom</span>
    </div>

    <!-- SVG Canvas Overlay for Leader Lines -->
    <svg id="svg-overlay-solar" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:4;">
        <line id="line-modules" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4" />
        <circle id="dot-modules" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />

        <line id="line-soiling" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6,4" />
        <circle id="dot-soiling" r="6" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5" />

        <line id="line-mount" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4" />
        <circle id="dot-mount" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />
    </svg>

    <!-- Perimeter-Scattered Component Callout Badges -->
    <div id="anno-modules" class="annotation" style="top: 14px; right: 14px;">
        <div class="annotation-title">SILICON PV MODULES ARRAY</div>
        <div>Irradiance: <b>{irradiance:.1f} W/m²</b></div>
    </div>

    <div id="anno-soiling" class="annotation" style="top: 85px; right: 14px;">
        <div class="annotation-title">SURFACE DUST SOILING LAYER</div>
        <div>Soiling Ratio: <b>{soiling_factor:.2f}</b></div>
    </div>

    <div id="anno-mount" class="annotation" style="bottom: 14px; left: 14px;">
        <div class="annotation-title">GALVANIZED STEEL MOUNT</div>
        <div>25° Optimal Tilt Rack</div>
    </div>

    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xdce9f5);
        scene.fog = new THREE.FogExp2(0xdce9f5, 0.012);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 6, 15);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.maxPolarAngle = Math.PI / 2 - 0.02;

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
        scene.add(ambientLight);

        const sunLight = new THREE.DirectionalLight(0xfffbeb, 1.35);
        sunLight.position.set(14, 22, 10);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 1024;
        sunLight.shadow.mapSize.height = 1024;
        scene.add(sunLight);

        // Ground Floor - Natural Meadow
        const grassGeo = new THREE.PlaneGeometry(50, 50);
        const grassMat = new THREE.MeshStandardMaterial({{ color: 0x3d5c2e, roughness: 0.95 }});
        const grass = new THREE.Mesh(grassGeo, grassMat);
        grass.rotation.x = -Math.PI / 2;
        grass.receiveShadow = true;
        scene.add(grass);

        // Gravel / Concrete Foundation Pad
        const dirtBedGeo = new THREE.BoxGeometry(14, 0.05, 8);
        const dirtBedMat = new THREE.MeshStandardMaterial({{ color: 0x5a534c, roughness: 0.85 }});
        const dirtBed = new THREE.Mesh(dirtBedGeo, dirtBedMat);
        dirtBed.position.set(0, 0.025, 0);
        dirtBed.receiveShadow = true;
        scene.add(dirtBed);

        // Photorealistic Blue Silicon Solar Texture Generator
        function createSolarTexture() {{
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 512;
            const ctx = canvas.getContext('2d');

            // Rich Silicon Blue Base
            ctx.fillStyle = '#0a1d3d';
            ctx.fillRect(0, 0, 512, 512);

            const cols = 6;
            const rows = 10;
            const cellW = 512 / cols;
            const cellH = 512 / rows;

            // Draw individual silicon cell wafers with specular blue fill
            for (let c = 0; c < cols; c++) {{
                for (let r = 0; r < rows; r++) {{
                    ctx.fillStyle = '#0f2952';
                    ctx.fillRect(c * cellW + 1.5, r * cellH + 1.5, cellW - 3, cellH - 3);
                }}
            }}

            // Cell boundaries (subtle blue lines)
            ctx.strokeStyle = '#1e40af';
            ctx.lineWidth = 1.5;
            for (let x = 0; x <= cols; x++) {{
                ctx.beginPath();
                ctx.moveTo(x * cellW, 0);
                ctx.lineTo(x * cellW, 512);
                ctx.stroke();
            }}
            for (let y = 0; y <= rows; y++) {{
                ctx.beginPath();
                ctx.moveTo(0, y * cellH);
                ctx.lineTo(512, y * cellH);
                ctx.stroke();
            }}

            // Bright Silver Busbars (3 main vertical conductors per cell column)
            ctx.strokeStyle = '#f1f5f9';
            ctx.lineWidth = 2.5;
            for (let c = 0; c < cols; c++) {{
                for (let offRatio of [0.25, 0.5, 0.75]) {{
                    const bx = c * cellW + cellW * offRatio;
                    ctx.beginPath();
                    ctx.moveTo(bx, 0);
                    ctx.lineTo(bx, 512);
                    ctx.stroke();
                }}
            }}

            // Micro finger conductors (thin horizontal silver grid)
            ctx.strokeStyle = 'rgba(241, 245, 249, 0.22)';
            ctx.lineWidth = 1;
            for (let y = 3; y < 512; y += 6) {{
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(512, y);
                ctx.stroke();
            }}

            return new THREE.CanvasTexture(canvas);
        }}

        const solarTexture = createSolarTexture();

        // Main Solar Array Rack Group
        const arrayGroup = new THREE.Group();
        arrayGroup.position.set(0, 2.0, 0);
        arrayGroup.rotation.x = Math.PI / 7;
        scene.add(arrayGroup);

        // Support Legs
        const legMat = new THREE.MeshStandardMaterial({{ color: 0x64748b, metalness: 0.85, roughness: 0.3 }});
        for (let x of [-4.5, 0, 4.5]) {{
            const legFront = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.4, 16), legMat);
            legFront.position.set(x, -0.7, 1.2);
            legFront.rotation.x = -Math.PI / 7;
            legFront.castShadow = true;
            arrayGroup.add(legFront);

            const legRear = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.8, 16), legMat);
            legRear.position.set(x, -1.4, -1.2);
            legRear.rotation.x = -Math.PI / 7;
            legRear.castShadow = true;
            arrayGroup.add(legRear);
        }}

        // Support Rails
        const railMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, metalness: 0.9, roughness: 0.2 }});
        for (let z of [-1.5, 0, 1.5]) {{
            const rail = new THREE.Mesh(new THREE.BoxGeometry(11.8, 0.08, 0.1), railMat);
            rail.position.set(0, -0.06, z);
            arrayGroup.add(rail);
        }}

        // Solar Modules Array
        const panelWidth = 2.6;
        const panelHeight = 2.2;
        const rows = 2;
        const cols = 4;

        const pvCellMat = new THREE.MeshStandardMaterial({{ 
            map: solarTexture, 
            roughness: 0.1, 
            metalness: 0.3,
            color: 0xffffff 
        }});
        const frameMat = new THREE.MeshStandardMaterial({{ color: 0xd1d5db, metalness: 0.95, roughness: 0.15 }});

        for (let r = 0; r < rows; r++) {{
            for (let c = 0; c < cols; c++) {{
                const xPos = (c - (cols - 1) / 2) * (panelWidth + 0.08);
                const zPos = (r - (rows - 1) / 2) * (panelHeight + 0.08);

                const singlePanelGroup = new THREE.Group();
                singlePanelGroup.position.set(xPos, 0, zPos);

                const frameMesh = new THREE.Mesh(new THREE.BoxGeometry(panelWidth, 0.06, panelHeight), frameMat);
                frameMesh.castShadow = true;
                singlePanelGroup.add(frameMesh);

                const pvSurface = new THREE.Mesh(new THREE.BoxGeometry(panelWidth - 0.08, 0.07, panelHeight - 0.08), pvCellMat);
                pvSurface.position.y = 0.01;
                singlePanelGroup.add(pvSurface);

                if ({dust_opacity} > 0.02) {{
                    const dustMat = new THREE.MeshStandardMaterial({{
                        color: 0x9f9788, transparent: true, opacity: {dust_opacity}, roughness: 0.95
                    }});
                    const dustLayer = new THREE.Mesh(new THREE.PlaneGeometry(panelWidth - 0.08, panelHeight - 0.08), dustMat);
                    dustLayer.rotation.x = -Math.PI / 2;
                    dustLayer.position.y = 0.055;
                    singlePanelGroup.add(dustLayer);
                }}

                arrayGroup.add(singlePanelGroup);
            }}
        }}

        // Scattered Annotations Mapping for Solar Array
        const annotations = [
            {{
                card: document.getElementById('anno-modules'),
                line: document.getElementById('line-modules'),
                dot: document.getElementById('dot-modules'),
                position: new THREE.Vector3(0, 2.4, 0)
            }},
            {{
                card: document.getElementById('anno-soiling'),
                line: document.getElementById('line-soiling'),
                dot: document.getElementById('dot-soiling'),
                position: new THREE.Vector3(-2.8, 1.8, 0.4)
            }},
            {{
                card: document.getElementById('anno-mount'),
                line: document.getElementById('line-mount'),
                dot: document.getElementById('dot-mount'),
                position: new THREE.Vector3(4.5, 0.8, -1.0)
            }}
        ];

        function updateAnnotations() {{
            const tempV = new THREE.Vector3();
            annotations.forEach(anno => {{
                if (!anno.card || !anno.line || !anno.dot) return;
                tempV.copy(anno.position);
                tempV.project(camera);

                if (tempV.z >= 1) {{
                    anno.card.style.display = 'none';
                    anno.line.style.display = 'none';
                    anno.dot.style.display = 'none';
                    return;
                }}

                anno.card.style.display = 'block';
                anno.line.style.display = 'block';
                anno.dot.style.display = 'block';

                const originX = (tempV.x * .5 + .5) * window.innerWidth;
                const originY = (tempV.y * -.5 + .5) * window.innerHeight;

                const rect = anno.card.getBoundingClientRect();
                const cardX = (rect.left < window.innerWidth / 2) ? rect.right : rect.left;
                const cardY = rect.top + rect.height / 2;

                anno.line.setAttribute('x1', cardX);
                anno.line.setAttribute('y1', cardY);
                anno.line.setAttribute('x2', originX);
                anno.line.setAttribute('y2', originY);

                anno.dot.setAttribute('cx', originX);
                anno.dot.setAttribute('cy', originY);
            }});
        }}

        // Animation Loop
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            updateAnnotations();
            renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
            updateAnnotations();
        }});
    </script>
</body>
</html>"""
    
    components.html(html_code, height=height, scrolling=False)

