import { useEffect, useRef } from 'react';

export default function Starfield() {
  const bgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!bgRef.current) return;
    const starBg = bgRef.current;
    
    // Clear existing stars to prevent duplicates in strict mode
    starBg.innerHTML = '';
    
    const numStars = 400; // Increased star count 
    
    for (let i = 0; i < numStars; i++) {
        const star = document.createElement('div');
        star.classList.add('star-particle');
        
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        
        // Real stars are tiny, sharp points of light (0.5 to 2.5px mostly)
        const size = Math.random() * 2 + 0.5;
        
        star.style.left = `${x}%`;
        star.style.top = `${y}%`;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        
        // Subtle color variations
        const colors = ['#ffffff', '#e5f3ff', '#fff4e5', '#ffeded'];
        star.style.background = colors[Math.floor(Math.random() * colors.length)];
        
        // Twinkle durations: some fast, some slow
        const duration = Math.random() * 4 + 2; 
        const delay = Math.random() * 5;
        star.style.animation = `twinkle ${duration}s infinite alternate ${delay}s ease-in-out`;
        
        starBg.appendChild(star);
    }
  }, []);

  return <div id="star-field" className="star-bg layer" ref={bgRef}></div>;
}
