import { useEffect, useRef } from 'react';
import gsap from 'gsap';

export default function ShootingStars() {
  const layerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!layerRef.current) return;
    const shootingStarLayer = layerRef.current;
    let isActive = true;
    let isPaused = false;
    let timeoutId: ReturnType<typeof setTimeout>;

    function spawnShootingStar() {
      if (!isActive || isPaused) return;

      const s = document.createElement('div');
      s.classList.add('shooting-star');

      const startX = window.innerWidth * 0.4 + Math.random() * window.innerWidth;
      const startY = Math.random() * (window.innerHeight * 0.5) - 200;

      s.style.left = `${startX}px`;
      s.style.top = `${startY}px`;

      const angle = 45 + (Math.random() * 10 - 5);
      s.style.transform = `rotate(${angle}deg)`;

      shootingStarLayer.appendChild(s);

      const distance = window.innerWidth + 800;
      const duration = Math.random() * 1.5 + 1.8;

      gsap.fromTo(s,
        { x: 0, y: 0, opacity: 0 },
        {
          x: -distance,
          y: distance,
          opacity: 1,
          duration,
          ease: 'power1.in',
          onComplete: () => {
            gsap.to(s, {
              opacity: 0,
              duration: 0.2,
              ease: 'power1.out',
              onComplete: () => s.remove(),
            });
          },
        }
      );

      scheduleNext();
    }

    function scheduleNext() {
      if (!isActive || isPaused) return;
      clearTimeout(timeoutId);
      timeoutId = setTimeout(spawnShootingStar, Math.random() * 4000 + 3000);
    }

    // Pause when tab is hidden, resume with a fresh delay when visible
    function handleVisibility() {
      if (document.hidden) {
        isPaused = true;
        clearTimeout(timeoutId);
      } else {
        isPaused = false;
        // Fresh delay so they don't bunch up on return
        scheduleNext();
      }
    }

    document.addEventListener('visibilitychange', handleVisibility);

    // Initial spawn
    timeoutId = setTimeout(spawnShootingStar, 1500);

    return () => {
      isActive = false;
      clearTimeout(timeoutId);
      document.removeEventListener('visibilitychange', handleVisibility);
      if (layerRef.current) {
        layerRef.current.innerHTML = '';
      }
    };
  }, []);

  return <div id="shooting-star-layer" ref={layerRef}></div>;
}
