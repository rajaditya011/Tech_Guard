import { useEffect, useRef } from 'react';

export default function RiskGauge({ score = 0, size = 'large' }) {
  const canvasRef = useRef(null);
  const dimensions = size === 'large' ? 180 : 48;
  const lineWidth = size === 'large' ? 12 : 4;

  const getRiskColor = (s) => {
    if (s >= 76) return 'var(--accent-red)';
    if (s >= 51) return 'var(--accent-amber)';
    if (s >= 26) return 'var(--accent-amber)';
    return 'var(--accent-emerald)';
  };

  const getRiskLabel = (s) => {
    if (s >= 76) return 'CRITICAL';
    if (s >= 51) return 'HIGH';
    if (s >= 26) return 'MEDIUM';
    return 'LOW';
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const center = dimensions / 2;
    const radius = center - lineWidth;
    
    let animationFrame;
    let currentScore = 0; // Starts from 0 to animate up

    const draw = () => {
      ctx.clearRect(0, 0, dimensions, dimensions);

      // Background Arc
      ctx.beginPath();
      ctx.arc(center, center, radius, 0.75 * Math.PI, 2.25 * Math.PI);
      ctx.strokeStyle = 'rgba(255,255,255,0.06)';
      ctx.lineWidth = lineWidth;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Progress calculation
      const diff = score - currentScore;
      if (Math.abs(diff) > 0.5) {
        currentScore += diff * 0.1;
      } else {
        currentScore = score;
      }

      // Foreground Arc
      const scoreAngle = 0.75 * Math.PI + (currentScore / 100) * 1.5 * Math.PI;
      ctx.beginPath();
      ctx.arc(center, center, radius, 0.75 * Math.PI, scoreAngle);
      
      const style = getComputedStyle(document.documentElement);
      const color = currentScore >= 76 ? style.getPropertyValue('--accent-red').trim()
        : currentScore >= 26 ? style.getPropertyValue('--accent-amber').trim()
        : style.getPropertyValue('--accent-emerald').trim();
      ctx.strokeStyle = color || '#10b981';
      ctx.lineWidth = lineWidth;
      ctx.lineCap = 'round';
      ctx.stroke();

      if (currentScore !== score) {
        animationFrame = requestAnimationFrame(draw);
      }
    };

    draw();

    return () => cancelAnimationFrame(animationFrame);
  }, [score, dimensions, lineWidth]);

  if (size === 'small') {
    return (
      <div className="flex items-center gap-2" id="risk-gauge-small">
        <canvas ref={canvasRef} width={dimensions} height={dimensions} />
        <span className="text-xs font-mono" style={{ color: getRiskColor(score) }}>{score}</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center" id="risk-gauge-large">
      <div className="relative">
        <canvas ref={canvasRef} width={dimensions} height={dimensions} />
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color: getRiskColor(score) }}>{score}</span>
          <span className="text-xs font-mono uppercase" style={{ color: 'var(--text-tertiary)' }}>{getRiskLabel(score)}</span>
        </div>
      </div>
    </div>
  );
}
