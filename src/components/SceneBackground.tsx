import { useEffect, useRef } from 'react';
import * as THREE from 'three';

/**
 * Global fullscreen Three.js background — two floating metallic objects:
 * a cube pinned bottom-right, an octahedron pinned top-left.
 * Particles and light shafts spread across the full viewport.
 */
export function SceneBackground() {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = mountRef.current;
    if (!el) return;

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(60, el.clientWidth / el.clientHeight, 0.1, 200);
    camera.position.set(0, 0, 12);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(el.clientWidth, el.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.8;
    el.appendChild(renderer.domElement);

    // --- Procedural environment cubemap for reflections ---
    const cubeRT = new THREE.WebGLCubeRenderTarget(128);
    const cubeCamera = new THREE.CubeCamera(0.1, 100, cubeRT);
    const envScene = new THREE.Scene();
    const envGeo = new THREE.SphereGeometry(50, 16, 16);
    const envMat = new THREE.ShaderMaterial({
      side: THREE.BackSide,
      uniforms: {
        colorTop: { value: new THREE.Color(0x8899aa) },
        colorMid: { value: new THREE.Color(0xcccccc) },
        colorBot: { value: new THREE.Color(0x556677) },
      },
      vertexShader: `
        varying vec3 vWorldPos;
        void main() {
          vec4 wp = modelMatrix * vec4(position, 1.0);
          vWorldPos = wp.xyz;
          gl_Position = projectionMatrix * viewMatrix * wp;
        }
      `,
      fragmentShader: `
        uniform vec3 colorTop;
        uniform vec3 colorMid;
        uniform vec3 colorBot;
        varying vec3 vWorldPos;
        void main() {
          float y = normalize(vWorldPos).y;
          vec3 col = mix(colorBot, colorMid, smoothstep(-0.5, 0.0, y));
          col = mix(col, colorTop, smoothstep(0.0, 0.6, y));
          gl_FragColor = vec4(col, 1.0);
        }
      `,
    });
    envScene.add(new THREE.Mesh(envGeo, envMat));
    cubeCamera.update(renderer, envScene);

    // --- Procedural brushed-metal textures ---
    const TEX_SIZE = 512;

    // Normal map: horizontal brushed-metal grain
    const normalCanvas = document.createElement('canvas');
    normalCanvas.width = TEX_SIZE;
    normalCanvas.height = TEX_SIZE;
    const nCtx = normalCanvas.getContext('2d')!;
    // Base neutral normal (128,128,255)
    nCtx.fillStyle = 'rgb(128,128,255)';
    nCtx.fillRect(0, 0, TEX_SIZE, TEX_SIZE);
    // Horizontal brush strokes — perturb the normal in Y direction
    for (let y = 0; y < TEX_SIZE; y++) {
      const strength = Math.random() * 40 - 20; // -20 to +20
      const g = Math.round(128 + strength);
      nCtx.strokeStyle = `rgb(128,${g},255)`;
      nCtx.globalAlpha = 0.3 + Math.random() * 0.4;
      nCtx.beginPath();
      nCtx.moveTo(0, y);
      nCtx.lineTo(TEX_SIZE, y);
      nCtx.stroke();
    }
    // Add some random fine scratches at slight angles
    nCtx.globalAlpha = 0.15;
    for (let i = 0; i < 60; i++) {
      const y1 = Math.random() * TEX_SIZE;
      const y2 = y1 + (Math.random() - 0.5) * 30;
      const gVal = Math.round(128 + (Math.random() - 0.5) * 50);
      nCtx.strokeStyle = `rgb(${Math.round(128 + (Math.random() - 0.5) * 30)},${gVal},255)`;
      nCtx.lineWidth = 0.5 + Math.random();
      nCtx.beginPath();
      nCtx.moveTo(0, y1);
      nCtx.lineTo(TEX_SIZE, y2);
      nCtx.stroke();
    }
    nCtx.globalAlpha = 1;
    const normalMap = new THREE.CanvasTexture(normalCanvas);
    normalMap.wrapS = normalMap.wrapT = THREE.RepeatWrapping;

    // Roughness map: varying micro-roughness for realistic metal surface
    const roughCanvas = document.createElement('canvas');
    roughCanvas.width = TEX_SIZE;
    roughCanvas.height = TEX_SIZE;
    const rCtx = roughCanvas.getContext('2d')!;
    // Base roughness ~0.15 (mapped as gray)
    rCtx.fillStyle = 'rgb(38,38,38)';
    rCtx.fillRect(0, 0, TEX_SIZE, TEX_SIZE);
    // Horizontal brush lines vary roughness
    for (let y = 0; y < TEX_SIZE; y++) {
      const v = Math.round(30 + Math.random() * 25);
      rCtx.strokeStyle = `rgb(${v},${v},${v})`;
      rCtx.globalAlpha = 0.4 + Math.random() * 0.3;
      rCtx.beginPath();
      rCtx.moveTo(0, y);
      rCtx.lineTo(TEX_SIZE, y);
      rCtx.stroke();
    }
    // Random smudges / fingerprint-like patches
    rCtx.globalAlpha = 0.08;
    for (let i = 0; i < 12; i++) {
      const cx = Math.random() * TEX_SIZE;
      const cy = Math.random() * TEX_SIZE;
      const r = 20 + Math.random() * 60;
      const v = Math.round(50 + Math.random() * 40);
      rCtx.fillStyle = `rgb(${v},${v},${v})`;
      rCtx.beginPath();
      rCtx.ellipse(cx, cy, r, r * 0.4, Math.random() * Math.PI, 0, Math.PI * 2);
      rCtx.fill();
    }
    rCtx.globalAlpha = 1;
    const roughnessMap = new THREE.CanvasTexture(roughCanvas);
    roughnessMap.wrapS = roughnessMap.wrapT = THREE.RepeatWrapping;

    // Shared brushed-metal material
    const metalMat = new THREE.MeshStandardMaterial({
      color: 0xc8c8c8,
      metalness: 1.0,
      roughness: 0.18,
      roughnessMap: roughnessMap,
      normalMap: normalMap,
      normalScale: new THREE.Vector2(0.4, 0.4),
      envMap: cubeRT.texture,
      envMapIntensity: 1.8,
    });

    // --- Cube: bottom-right ---
    const CUBE_X = 6.5;
    const CUBE_Y = -4;
    const cubeGeo = new THREE.BoxGeometry(1.2, 1.2, 1.2);
    const cube = new THREE.Mesh(cubeGeo, metalMat);
    cube.position.set(CUBE_X, CUBE_Y, 0);
    scene.add(cube);

    // Cube edge highlight
    const cubeEdgeGeo = new THREE.EdgesGeometry(cubeGeo);
    const edgeLineMat = new THREE.LineBasicMaterial({
      color: 0xff6600,
      transparent: true,
      opacity: 0.4,
    });
    const cubeEdges = new THREE.LineSegments(cubeEdgeGeo, edgeLineMat);
    cubeEdges.position.copy(cube.position);
    scene.add(cubeEdges);

    // --- Octahedron: top-left ---
    const OCT_X = -6;
    const OCT_Y = 3.5;
    const octGeo = new THREE.OctahedronGeometry(0.9);
    const octahedron = new THREE.Mesh(octGeo, metalMat);
    octahedron.position.set(OCT_X, OCT_Y, -1);
    scene.add(octahedron);

    // Octahedron edge highlight
    const octEdgeGeo = new THREE.EdgesGeometry(octGeo);
    const octEdgeLineMat = new THREE.LineBasicMaterial({
      color: 0xff6600,
      transparent: true,
      opacity: 0.3,
    });
    const octEdges = new THREE.LineSegments(octEdgeGeo, octEdgeLineMat);
    octEdges.position.copy(octahedron.position);
    scene.add(octEdges);

    // --- Lights: white/cool tones for clean chrome look ---
    const keyLight = new THREE.PointLight(0xffffff, 50, 30);
    keyLight.position.set(CUBE_X + 2, CUBE_Y + 2, 4);
    scene.add(keyLight);

    const fillLight = new THREE.PointLight(0xddeeff, 25, 25);
    fillLight.position.set(CUBE_X - 3, CUBE_Y, -2);
    scene.add(fillLight);

    const octKeyLight = new THREE.PointLight(0xffffff, 35, 25);
    octKeyLight.position.set(OCT_X - 2, OCT_Y + 1, 3);
    scene.add(octKeyLight);

    const octFillLight = new THREE.PointLight(0xddeeff, 18, 18);
    octFillLight.position.set(OCT_X + 2, OCT_Y - 1, -1);
    scene.add(octFillLight);

    const centerLight = new THREE.PointLight(0xffffff, 12, 30);
    centerLight.position.set(0, 0, 6);
    scene.add(centerLight);

    scene.add(new THREE.AmbientLight(0x444455, 0.6));

    // --- Scattered particles across viewport ---
    const particleCount = 80;
    const particleGeo = new THREE.BufferGeometry();
    const pPositions = new Float32Array(particleCount * 3);
    const pSpeeds = new Float32Array(particleCount);
    const pPhase = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      pPositions[i * 3] = (Math.random() - 0.5) * 22;
      pPositions[i * 3 + 1] = (Math.random() - 0.5) * 16;
      pPositions[i * 3 + 2] = (Math.random() - 0.5) * 6 - 2;
      pSpeeds[i] = 0.2 + Math.random() * 0.5;
      pPhase[i] = Math.random() * Math.PI * 2;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(pPositions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0xff8833,
      size: 0.04,
      transparent: true,
      opacity: 0.5,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // --- Subtle light shafts near both objects ---
    const shaftMat = new THREE.SpriteMaterial({
      color: 0xff6600,
      transparent: true,
      opacity: 0.03,
      blending: THREE.AdditiveBlending,
    });
    const shafts: THREE.Sprite[] = [];
    const shaftAnchors = [
      { x: CUBE_X, y: CUBE_Y },
      { x: OCT_X, y: OCT_Y },
    ];
    for (const anchor of shaftAnchors) {
      for (let i = 0; i < 2; i++) {
        const s = new THREE.Sprite(shaftMat.clone());
        s.scale.set(0.15, 10 + Math.random() * 6, 1);
        s.position.set(
          anchor.x + (Math.random() - 0.5) * 3,
          anchor.y + (Math.random() - 0.5) * 4,
          -1
        );
        scene.add(s);
        shafts.push(s);
      }
    }

    // --- Mouse parallax ---
    let mouseX = 0;
    let mouseY = 0;
    const onMouseMove = (e: MouseEvent) => {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    window.addEventListener('mousemove', onMouseMove);

    // --- Resize ---
    const onResize = () => {
      camera.aspect = el.clientWidth / el.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(el.clientWidth, el.clientHeight);
    };
    window.addEventListener('resize', onResize);

    // --- Scroll ---
    let scrollY = 0;
    const onScroll = () => { scrollY = window.scrollY; };
    window.addEventListener('scroll', onScroll);

    // --- Animate ---
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);
      const t = Date.now() * 0.001;

      // Cube: slow rotate + gentle float
      cube.rotation.x = t * 0.1 + Math.sin(t * 0.3) * 0.15;
      cube.rotation.y = t * 0.15;
      cube.rotation.z = Math.sin(t * 0.2) * 0.08;
      cube.position.y = CUBE_Y + Math.sin(t * 0.5) * 0.2 - scrollY * 0.002;

      cubeEdges.rotation.copy(cube.rotation);
      cubeEdges.position.set(CUBE_X, cube.position.y, 0);

      // Octahedron: different rotation speed + float
      octahedron.rotation.x = t * 0.08 + Math.cos(t * 0.25) * 0.2;
      octahedron.rotation.y = t * 0.12;
      octahedron.rotation.z = Math.cos(t * 0.18) * 0.1;
      octahedron.position.y = OCT_Y + Math.sin(t * 0.4 + 1.5) * 0.25 - scrollY * 0.001;

      octEdges.rotation.copy(octahedron.rotation);
      octEdges.position.set(OCT_X, octahedron.position.y, -1);

      // Subtle camera parallax
      camera.position.x += (mouseX * 0.3 - camera.position.x) * 0.02;
      camera.position.y += (-mouseY * 0.2 - camera.position.y) * 0.02;
      camera.lookAt(0, 0, 0);

      // Orbit key light around cube
      keyLight.position.x = CUBE_X + Math.cos(t * 0.4) * 3;
      keyLight.position.z = Math.sin(t * 0.4) * 3 + 2;
      keyLight.position.y = CUBE_Y + 2 + Math.sin(t * 0.25) * 1;

      // Orbit light around octahedron
      octKeyLight.position.x = OCT_X + Math.cos(t * 0.35 + 2) * 2.5;
      octKeyLight.position.z = Math.sin(t * 0.35 + 2) * 2.5 + 1;

      // Particles gentle drift
      const pos = particles.geometry.attributes.position as THREE.BufferAttribute;
      for (let i = 0; i < particleCount; i++) {
        pos.array[i * 3 + 1] += Math.sin(t * pSpeeds[i] + pPhase[i]) * 0.002;
      }
      pos.needsUpdate = true;

      // Shafts pulse
      shafts.forEach((s, i) => {
        s.material.opacity = 0.02 + Math.sin(t * 0.2 + i * 1.5) * 0.015;
      });

      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', onResize);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('scroll', onScroll);

      cubeRT.dispose();
      normalMap.dispose();
      roughnessMap.dispose();
      cubeGeo.dispose();
      cubeEdgeGeo.dispose();
      octGeo.dispose();
      octEdgeGeo.dispose();
      metalMat.dispose();
      edgeLineMat.dispose();
      octEdgeLineMat.dispose();
      envGeo.dispose();
      envMat.dispose();
      particleGeo.dispose();
      particleMat.dispose();
      shafts.forEach((s) => s.material.dispose());

      renderer.dispose();
      if (el.contains(renderer.domElement)) {
        el.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
    />
  );
}
