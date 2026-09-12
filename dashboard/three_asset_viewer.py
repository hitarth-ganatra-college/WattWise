"""
Interactive 3D WebGL Asset Inspector for Wind Turbines and Solar Arrays
========================================================================
Renders rotatable, real-time 3D models using Three.js inside Streamlit components.
- Wind Turbine: Rotatable 3D tower, nacelle, hub, and 3 spinning blades animated at SCADA RPM.
- Solar Panel: Rotatable 3D solar table with tilt angle, grid cells, sunbeams, and dust soiling opacity.
"""

import streamlit as st
import streamlit.components.v1 as components

def render_3d_wind_turbine(rpm: float = 15.0, gearbox_temp: float = 65.0, health_status: str = "Healthy", height: int = 420):
    """Render a realistic 3D Wind Turbine model with natural grass floor, dirt, cloudy sky, and rotatable blades."""
    
    speed_factor = max(0.01, min(0.35, (rpm / 1800.0) * 0.18)) if rpm > 0 else 0.002
    gearbox_color = "0xef4444" if gearbox_temp > 80 else ("0xf59e0b" if gearbox_temp > 65 else "0xe2e8f0")

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; font-family: 'Segoe UI', Tahoma, sans-serif; }}
        #info {{
            position: absolute; top: 12px; left: 12px; color: #0f172a; font-size: 12px;
            background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(8px);
            padding: 10px 14px; border-radius: 8px; border: 1px solid #cbd5e1;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info">
        <b style="color:#0f172a; font-size:13px;">3D INDUSTRIAL WIND TURBINE</b><br>
        Generator Speed: <b>{rpm:.1f} RPM</b><br>
        Gearbox Temp: <b>{gearbox_temp:.1f} °C</b><br>
        Health Status: <b>{health_status}</b><br>
        <span style="color:#64748b; font-size:10px;">Drag to rotate | Scroll to zoom</span>
    </div>
    <script>
        const scene = new THREE.Scene();
        // Natural Cloudy Sky background gradient & fog
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
        controls.maxPolarAngle = Math.PI / 2 - 0.02; // Don't clip through ground

        // Natural Sunlight & Ambient Environment
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
        scene.add(ambientLight);

        const sunLight = new THREE.DirectionalLight(0xfffbeb, 1.2);
        sunLight.position.set(15, 25, 12);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 1024;
        sunLight.shadow.mapSize.height = 1024;
        scene.add(sunLight);

        // Ground Floor - Natural Green Grass with Dirt Sub-layer
        const grassGeo = new THREE.PlaneGeometry(60, 60);
        const grassMat = new THREE.MeshStandardMaterial({{ color: 0x4d7c0f, roughness: 0.9 }});
        const grass = new THREE.Mesh(grassGeo, grassMat);
        grass.rotation.x = -Math.PI / 2;
        grass.receiveShadow = true;
        scene.add(grass);

        // Dirt mound patch under turbine base
        const dirtGeo = new THREE.CylinderGeometry(4.5, 5.5, 0.15, 32);
        const dirtMat = new THREE.MeshStandardMaterial({{ color: 0x78350f, roughness: 0.95 }});
        const dirt = new THREE.Mesh(dirtGeo, dirtMat);
        dirt.position.y = 0.07;
        dirt.receiveShadow = true;
        scene.add(dirt);

        // Concrete Base Foundation
        const baseGeo = new THREE.CylinderGeometry(1.6, 2.0, 0.5, 32);
        const baseMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, roughness: 0.7 }});
        const base = new THREE.Mesh(baseGeo, baseMat);
        base.position.y = 0.4;
        base.castShadow = true;
        scene.add(base);

        // Tower (Tapered Steel Cylinder)
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

        // Aerodynamic Rotor Hub Cone
        const hubGeo = new THREE.ConeGeometry(0.85, 1.4, 32);
        hubGeo.rotateX(Math.PI / 2);
        const hubMat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.2, metalness: 0.5 }});

        const rotorGroup = new THREE.Group();
        rotorGroup.position.set(0, 13.5, -1.45);
        scene.add(rotorGroup);

        const hub = new THREE.Mesh(hubGeo, hubMat);
        rotorGroup.add(hub);

        // Aerodynamic Blades with Red Safety Tips
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

            // Red tip on blade
            const tipGeo = new THREE.BoxGeometry(0.29, 0.8, 0.09);
            tipGeo.translate(0, 6.8, 0);
            const tip = new THREE.Mesh(tipGeo, tipMat);
            bladeGroup.add(tip);

            rotorGroup.add(bladeGroup);
        }}

        // Animation Loop
        function animate() {{
            requestAnimationFrame(animate);
            rotorGroup.rotation.z += {speed_factor};
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>"""
    
    components.html(html_code, height=height, scrolling=False)


def render_3d_solar_panel(soiling_factor: float = 1.0, irradiance: float = 850.0, panel_temp: float = 45.0, health_status: str = "Healthy", height: int = 420):
    """Render a realistic 3D Photovoltaic Solar Array with dynamic cell textures, aluminum borders, steel mounts, grass floor, and natural sky."""
    
    dust_opacity = max(0.0, min(0.65, (1.0 - soiling_factor) * 2.2))

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; font-family: 'Segoe UI', Tahoma, sans-serif; }}
        #info {{
            position: absolute; top: 12px; left: 12px; color: #0f172a; font-size: 12px;
            background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(8px);
            padding: 10px 14px; border-radius: 8px; border: 1px solid #cbd5e1;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info">
        <b style="color:#0f172a; font-size:13px;">3D COMMERCIAL SOLAR PV ARRAY</b><br>
        Solar Irradiance: <b>{irradiance:.1f} W/m²</b><br>
        Module Temp: <b>{panel_temp:.1f} °C</b><br>
        Soiling Ratio: <b>{soiling_factor:.2f}</b> (1.0 = Clean)<br>
        Health Status: <b>{health_status}</b><br>
        <span style="color:#64748b; font-size:10px;">Drag to rotate | Scroll to zoom</span>
    </div>
    <script>
        const scene = new THREE.Scene();
        // Natural Cloudy Sky & Atmospheric Fog
        scene.background = new THREE.Color(0xdbeafe);
        scene.fog = new THREE.FogExp2(0xdbeafe, 0.012);

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

        // Natural Sunlight & Skylight
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
        scene.add(ambientLight);

        const sunLight = new THREE.DirectionalLight(0xfffbeb, 1.3);
        sunLight.position.set(14, 22, 10);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 1024;
        sunLight.shadow.mapSize.height = 1024;
        scene.add(sunLight);

        // Ground Floor - Natural Grass with Dirt Bed underneath
        const grassGeo = new THREE.PlaneGeometry(50, 50);
        const grassMat = new THREE.MeshStandardMaterial({{ color: 0x4d7c0f, roughness: 0.95 }});
        const grass = new THREE.Mesh(grassGeo, grassMat);
        grass.rotation.x = -Math.PI / 2;
        grass.receiveShadow = true;
        scene.add(grass);

        // Dirt Ground Bed underneath Solar Rack
        const dirtBedGeo = new THREE.BoxGeometry(14, 0.05, 8);
        const dirtBedMat = new THREE.MeshStandardMaterial({{ color: 0x78350f, roughness: 0.9 }});
        const dirtBed = new THREE.Mesh(dirtBedGeo, dirtBedMat);
        dirtBed.position.set(0, 0.025, 0);
        dirtBed.receiveShadow = true;
        scene.add(dirtBed);

        // Dynamic Canvas Texture Generator for Photorealistic Silicon Solar Cells
        function createSolarTexture() {{
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 512;
            const ctx = canvas.getContext('2d');

            // Deep Blue Silicon Base
            ctx.fillStyle = '#0a192f';
            ctx.fillRect(0, 0, 512, 512);

            // Cell divisions (6x10 grid per module)
            ctx.strokeStyle = '#1e3a8a';
            ctx.lineWidth = 3;
            const cellW = 512 / 6;
            const cellH = 512 / 10;
            for (let x = 0; x <= 6; x++) {{
                ctx.beginPath();
                ctx.moveTo(x * cellW, 0);
                ctx.lineTo(x * cellW, 512);
                ctx.stroke();
            }}
            for (let y = 0; y <= 10; y++) {{
                ctx.beginPath();
                ctx.moveTo(0, y * cellH);
                ctx.lineTo(512, y * cellH);
                ctx.stroke();
            }}

            // Silver Busbars (Main electrical collector lines)
            ctx.strokeStyle = '#cbd5e1';
            ctx.lineWidth = 5;
            for (let b of [128, 256, 384]) {{
                ctx.beginPath();
                ctx.moveTo(0, b);
                ctx.lineTo(512, b);
                ctx.stroke();
            }}

            // Fine Grid Collector Fingers
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 1;
            for (let f = 0; f < 512; f += 12) {{
                ctx.beginPath();
                ctx.moveTo(f, 0);
                ctx.lineTo(f, 512);
                ctx.stroke();
            }}

            const texture = new THREE.CanvasTexture(canvas);
            return texture;
        }}

        const solarTexture = createSolarTexture();

        // Galvanized Steel Support Legs & Racking Frame
        const legMat = new THREE.MeshStandardMaterial({{ color: 0x64748b, metalness: 0.85, roughness: 0.3 }});
        
        for (let x of [-4.5, 0, 4.5]) {{
            // Front leg
            const legFront = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 1.4, 16), legMat);
            legFront.position.set(x, 0.7, 1.2);
            legFront.castShadow = true;
            scene.add(legFront);

            // Rear leg
            const legRear = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.8, 16), legMat);
            legRear.position.set(x, 1.4, -1.2);
            legRear.castShadow = true;
            scene.add(legRear);
        }}

        // Main Solar Array Rack Group (Tilted at 25 degrees)
        const arrayGroup = new THREE.Group();
        arrayGroup.position.set(0, 2.0, 0);
        arrayGroup.rotation.x = Math.PI / 7; // 25° Optimal Solar Tilt
        scene.add(arrayGroup);

        // Aluminum Rack Support Rails
        const railMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, metalness: 0.9, roughness: 0.2 }});
        for (let z of [-1.5, 0, 1.5]) {{
            const rail = new THREE.Mesh(new THREE.BoxGeometry(11.8, 0.08, 0.1), railMat);
            rail.position.set(0, -0.06, z);
            arrayGroup.add(rail);
        }}

        // REALISTIC SOLAR MODULES (4x2 Array)
        const panelWidth = 2.6;
        const panelHeight = 2.2;
        const rows = 2;
        const cols = 4;

        // Photovoltaic Silicon Cell Surface Material
        const pvCellMat = new THREE.MeshStandardMaterial({{
            map: solarTexture,
            roughness: 0.15,
            metalness: 0.75
        }});

        // Silver Aluminum Frame Border Material
        const frameMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, metalness: 0.95, roughness: 0.15 }});

        for (let r = 0; r < rows; r++) {{
            for (let c = 0; c < cols; c++) {{
                const xPos = (c - (cols - 1) / 2) * (panelWidth + 0.08);
                const zPos = (r - (rows - 1) / 2) * (panelHeight + 0.08);

                const singlePanelGroup = new THREE.Group();
                singlePanelGroup.position.set(xPos, 0, zPos);

                // Aluminum Outer Border Frame
                const frameMesh = new THREE.Mesh(new THREE.BoxGeometry(panelWidth, 0.06, panelHeight), frameMat);
                frameMesh.castShadow = true;
                singlePanelGroup.add(frameMesh);

                // Silicon PV Cell Surface Mesh
                const pvSurface = new THREE.Mesh(new THREE.BoxGeometry(panelWidth - 0.08, 0.07, panelHeight - 0.08), pvCellMat);
                pvSurface.position.y = 0.01;
                singlePanelGroup.add(pvSurface);

                // Soiling / Dust Layer (if dirty)
                if ({dust_opacity} > 0.05) {{
                    const dustMat = new THREE.MeshStandardMaterial({{
                        color: 0xd97706,
                        transparent: true,
                        opacity: {dust_opacity},
                        roughness: 0.95
                    }});
                    const dustLayer = new THREE.Mesh(new THREE.PlaneGeometry(panelWidth - 0.08, panelHeight - 0.08), dustMat);
                    dustLayer.rotation.x = -Math.PI / 2;
                    dustLayer.position.y = 0.055;
                    singlePanelGroup.add(dustLayer);
                }}

                arrayGroup.add(singlePanelGroup);
            }}
        }}

        // Animation Loop - Slow Showcase Orbit
        function animate() {{
            requestAnimationFrame(animate);
            arrayGroup.rotation.y += 0.0015;
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>"""
    
    components.html(html_code, height=height, scrolling=False)

