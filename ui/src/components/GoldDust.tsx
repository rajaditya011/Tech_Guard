import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function GoldDust() {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mountRef.current) return;
    const dustContainer = mountRef.current;
    
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    dustContainer.appendChild(renderer.domElement);
    
    const particleCount = 2000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const velocities: {x: number, y: number, z: number}[] = []; 
    
    for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 20;    
        positions[i * 3 + 1] = (Math.random() - 0.5) * 20; 
        positions[i * 3 + 2] = (Math.random() - 0.5) * 20; 
        
        velocities.push({
            x: (Math.random() - 0.5) * 0.005,
            y: (Math.random() - 0.5) * 0.005,
            z: (Math.random() - 0.5) * 0.005
        });
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const material = new THREE.PointsMaterial({
        color: 0xE5C07B, 
        size: 0.035,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });
    
    const particles = new THREE.Points(geometry, material);
    scene.add(particles);
    camera.position.z = 5;
    
    let animationFrameId: number;

    function animateThreeJS() {
        animationFrameId = requestAnimationFrame(animateThreeJS);
        
        const positions = particles.geometry.attributes.position.array as Float32Array;
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] += velocities[i].x;
            positions[i * 3 + 1] += velocities[i].y;
            positions[i * 3 + 2] += velocities[i].z;
            
            if (Math.abs(positions[i * 3]) > 10) velocities[i].x *= -1;
            if (Math.abs(positions[i * 3 + 1]) > 10) velocities[i].y *= -1;
            if (Math.abs(positions[i * 3 + 2]) > 10) velocities[i].z *= -1;
        }
        
        particles.geometry.attributes.position.needsUpdate = true;
        particles.rotation.y += 0.001;
        particles.rotation.x += 0.0005;
        
        renderer.render(scene, camera);
    }
    
    animateThreeJS();
    
    const handleResize = () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (dustContainer && renderer.domElement) {
        dustContainer.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      renderer.dispose();
    };
  }, []);

  return <div id="canvas-dust-container" ref={mountRef}></div>;
}
