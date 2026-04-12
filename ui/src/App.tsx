import { useEffect } from 'react';
import gsap from 'gsap';

import Starfield from './components/Starfield';
import ShootingStars from './components/ShootingStars';
import GoldDust from './components/GoldDust';
import FeatureCards from './components/FeatureCards';
import TechStack from './components/TechStack';
import Architecture from './components/Architecture';
import DemoSection from './components/DemoSection';
import Footer from './components/Footer';

export default function App() {
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = -(e.clientY / window.innerHeight) * 2 + 1;
      
      const dustOffset = 25;
      const starOffset = 15;
      
      gsap.to('#canvas-dust-container', {
          x: x * dustOffset,
          y: -y * dustOffset,
          duration: 0.3,
          ease: "power2.out"
      });
      
      gsap.to('#star-field', {
          x: x * starOffset,
          y: -y * starOffset,
          duration: 0.4,
          ease: "power2.out"
      });
    };

    window.addEventListener("mousemove", handleMouseMove);

    // Scroll-triggered fade-in animations
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    document.querySelectorAll('.fade-in-section').forEach((el) => {
      observer.observe(el);
    });

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      observer.disconnect();
    };
  }, []);

  return (
    <>
      <Starfield />
      <ShootingStars />
      <main id="app-container">
          <div className="scroll-canvas-wrapper">
              <GoldDust />
              
              <nav className="ui-overlay glassmorphism">
                  <div className="brand">HOMEGUARDIAN</div>
                  <div className="nav-links">
                      <a href="#features">FEATURES</a>
                      <a href="#architecture">ARCHITECTURE</a>
                      <a href="#demo">DEMO</a>
                  </div>
              </nav>
              
              <section className="hero-text mix-diff">
                  <div className="hero-tag">ADAPTIVE INTELLIGENCE SECURITY</div>
                  <h1>HomeGuardian<span className="hero-ai">AI</span></h1>
                  <p>Understanding behavior, not just detecting movement</p>
                  <div className="hero-divider"></div>
                  <div className="hero-stats">
                      <div className="stat-item">
                          <span className="stat-value">14</span>
                          <span className="stat-label">Day Baseline</span>
                      </div>
                      <div className="stat-divider"></div>
                      <div className="stat-item">
                          <span className="stat-value">4</span>
                          <span className="stat-label">Phase Prediction</span>
                      </div>
                      <div className="stat-divider"></div>
                      <div className="stat-item">
                          <span className="stat-value">≤5s</span>
                          <span className="stat-label">Pre-Event Clip</span>
                      </div>
                  </div>
              </section>

              <div className="scroll-indicator">
                  <span>Explore</span>
                  <div className="chevron"></div>
              </div>
          </div>

          {/* Scrollable Content Sections */}
          <div className="content-sections">
              <FeatureCards />
              <Architecture />
              <DemoSection />
              <TechStack />
              <Footer />
          </div>
      </main>
    </>
  );
}
