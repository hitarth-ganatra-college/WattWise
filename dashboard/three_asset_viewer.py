"""
Interactive 3D WebGL Asset Inspector for Wind Turbines and Solar Arrays
========================================================================
Renders rotatable, real-time 3D models using Three.js inside Streamlit components.
- Wind Turbine: Rotatable 3D tower, nacelle, hub, and 3 spinning blades animated at SCADA RPM.
- Solar Panel: Rotatable 3D solar table with tilt angle, grid cells, sunbeams, and dust soiling opacity.
"""

import streamlit as st
import streamlit.components.v1 as components

def render_3d_wind_turbine(rpm: float = 15.0, gearbox_temp: float = 65.0, health_status: str = "Healthy", height: int = 380):
    """Render a rotatable 3D Wind Turbine model with live rotating blades and thermal heatmap."""
    
    speed_factor = max(0.01, min(0.3, (rpm / 1800.0) * 0.15)) if rpm > 0 else 0.002
    gearbox_color = "0xef4444" if gearbox_temp > 80 else ("0xf59e0b" if gearbox_temp > 65 else "0x0284c7")

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background: #0f172a; font-family: sans-serif; }}
        #info {{ position: absolute; top: 10px; left: 10px; color: #f8fafc; font-size: 11px; background: rgba(15,23,42,0.8); padding: 8px 12px; border-radius: 6px; border: 1px solid #334155; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info">
        <b>3D WIND TURBINE INSPECTOR</b><br>
        Generator Speed: {rpm:.1f} RPM<br>
        Gearbox Temp: {gearbox_temp:.1f} °C<br>
        Status: {health_status}<br>
        <span style="color:#94a3b8; font-size:10px;">Drag to rotate | Scroll to zoom</span>
    </div>
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0f172a);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 8, 22);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(10, 20, 15);
        scene.add(dirLight);

        // Ground Plane
        const groundGeo = new THREE.PlaneGeometry(40, 40);
        const groundMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.8 }});
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        scene.add(ground);

        // Turbine Base / Foundation
        const baseGeo = new THREE.CylinderGeometry(1.5, 1.8, 0.6, 32);
        const baseMat = new THREE.MeshStandardMaterial({{ color: 0x64748b }});
        const base = new THREE.Mesh(baseGeo, baseMat);
        base.position.y = 0.3;
        scene.add(base);

        // Tower
        const towerGeo = new THREE.CylinderGeometry(0.5, 0.9, 12, 32);
        const towerMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, roughness: 0.3 }});
        const tower = new THREE.Mesh(towerGeo, towerMat);
        tower.position.y = 6.3;
        scene.add(tower);

        // Nacelle (Gearbox / Generator Housing)
        const nacelleGeo = new THREE.BoxGeometry(1.6, 1.4, 3.5);
        const nacelleMat = new THREE.MeshStandardMaterial({{ color: {gearbox_color}, roughness: 0.2, metalness: 0.5 }});
        const nacelle = new THREE.Mesh(nacelleGeo, nacelleMat);
        nacelle.position.set(0, 12.5, 0.4);
        scene.add(nacelle);

        // Rotor Hub
        const hubGeo = new THREE.ConeGeometry(0.8, 1.2, 32);
        hubGeo.rotateX(Math.PI / 2);
        const hubMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a, metalness: 0.8 }});
        const hub = new THREE.Mesh(hubGeo, hubMat);
        hub.position.set(0, 12.5, -1.4);
        scene.add(hub);

        // Rotor Group (Hub + 3 Blades)
        const rotorGroup = new THREE.Group();
        rotorGroup.position.set(0, 12.5, -1.4);
        scene.add(rotorGroup);

        // Blades
        const bladeGeo = new THREE.BoxGeometry(0.25, 6.5, 0.08);
        bladeGeo.translate(0, 3.25, 0);
        const bladeMat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.1 }});

        for (let i = 0; i < 3; i++) {{
            const blade = new THREE.Mesh(bladeGeo, bladeMat);
            blade.rotation.z = (i * Math.PI * 2) / 3;
            rotorGroup.add(blade);
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


def render_3d_solar_panel(soiling_factor: float = 1.0, irradiance: float = 850.0, panel_temp: float = 45.0, health_status: str = "Healthy", height: int = 380):
    """Render a rotatable 3D Solar Panel Array with cell grid, sunbeams, and dust layer opacity."""
    
    dust_opacity = max(0.0, min(0.7, (1.0 - soiling_factor) * 2.0))
    dust_color = "0xd97706" if dust_opacity > 0.3 else "0xf59e0b"

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background: #0f172a; font-family: sans-serif; }}
        #info {{ position: absolute; top: 10px; left: 10px; color: #f8fafc; font-size: 11px; background: rgba(15,23,42,0.8); padding: 8px 12px; border-radius: 6px; border: 1px solid #334155; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="info">
        <b>3D SOLAR ARRAY INSPECTOR</b><br>
        Irradiance: {irradiance:.1f} W/m²<br>
        Panel Temp: {panel_temp:.1f} °C<br>
        Soiling Ratio: {soiling_factor:.2f} (1.0 = Clean)<br>
        Status: {health_status}<br>
        <span style="color:#94a3b8; font-size:10px;">Drag to rotate | Scroll to zoom</span>
    </div>
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0f172a);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 6, 14);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
        scene.add(ambientLight);

        const sunLight = new THREE.DirectionalLight(0xfffbeb, 1.2);
        sunLight.position.set(12, 18, 10);
        scene.add(sunLight);

        // Ground Plane (Desert / Soil)
        const groundGeo = new THREE.PlaneGeometry(30, 30);
        const groundMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.9 }});
        const ground = new THREE.Mesh(groundGeo, groundMat);
        ground.rotation.x = -Math.PI / 2;
        scene.add(ground);

        // Array Support Frame / Legs
        const legMat = new THREE.MeshStandardMaterial({{ color: 0x475569, metalness: 0.7 }});
        
        for (let x of [-4, 4]) {{
            for (let z of [-2, 2]) {{
                const legGeo = new THREE.CylinderGeometry(0.12, 0.12, 3, 16);
                const leg = new THREE.Mesh(legGeo, legMat);
                leg.position.set(x, 1.5, z);
                scene.add(leg);
            }}
        }}

        // Solar Array Table Group (Tilted at 25 degrees)
        const arrayGroup = new THREE.Group();
        arrayGroup.position.set(0, 3, 0);
        arrayGroup.rotation.x = Math.PI / 7; // ~25 deg tilt
        scene.add(arrayGroup);

        // Frame
        const frameGeo = new THREE.BoxGeometry(10.2, 0.2, 5.2);
        const frameMat = new THREE.MeshStandardMaterial({{ color: 0x334155, metalness: 0.8 }});
        const frame = new THREE.Mesh(frameGeo, frameMat);
        arrayGroup.add(frame);

        // Blue Silicon PV Panels
        const panelGeo = new THREE.BoxGeometry(9.8, 0.1, 4.8);
        const panelMat = new THREE.MeshStandardMaterial({{ color: 0x0284c7, roughness: 0.1, metalness: 0.6 }});
        const panel = new THREE.Mesh(panelGeo, panelMat);
        panel.position.y = 0.1;
        arrayGroup.add(panel);

        // Grid Lines Overlay
        const gridHelper = new THREE.GridHelper(9.6, 12, 0x38bdf8, 0x0284c7);
        gridHelper.position.y = 0.16;
        gridHelper.rotation.x = Math.PI / 2;
        arrayGroup.add(gridHelper);

        // Soiling Dust Layer Overlay (Opacity changes with soiling factor)
        if ({dust_opacity} > 0.05) {{
            const dustGeo = new THREE.PlaneGeometry(9.8, 4.8);
            const dustMat = new THREE.MeshStandardMaterial({{
                color: {dust_color},
                transparent: true,
                opacity: {dust_opacity},
                roughness: 0.9
            }});
            const dustLayer = new THREE.Mesh(dustGeo, dustMat);
            dustLayer.rotation.x = -Math.PI / 2;
            dustLayer.position.y = 0.18;
            arrayGroup.add(dustLayer);
        }}

        // Sunbeam Vector Cylinder
        const beamGeo = new THREE.CylinderGeometry(0.05, 0.4, 12, 16);
        const beamMat = new THREE.MeshBasicMaterial({{ color: 0xfef08a, transparent: true, opacity: 0.3 }});
        const beam = new THREE.Mesh(beamGeo, beamMat);
        beam.position.set(6, 9, 5);
        beam.rotation.z = -Math.PI / 6;
        scene.add(beam);

        // Animation Loop
        function animate() {{
            requestAnimationFrame(animate);
            arrayGroup.rotation.y += 0.002; // slow rotatable showcase
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
