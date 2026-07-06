import React, { useEffect, useRef } from 'react';

/**
 * Full-screen canvas particle system — amber + blue constellation
 * with drifting legal symbol overlays.
 */
export default function ParticleCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let animId;
    let W = window.innerWidth;
    let H = window.innerHeight;

    const resize = () => {
      W = window.innerWidth;
      H = window.innerHeight;
      canvas.width  = W;
      canvas.height = H;
    };
    resize();
    window.addEventListener('resize', resize);

    // ---- Particle config ----
    const N_PARTICLES = 90;
    const CONNECT_DIST = 140;
    const particles = [];

    class Particle {
      constructor() { this.reset(true); }

      reset(initial = false) {
        this.x  = Math.random() * W;
        this.y  = initial ? Math.random() * H : -10;
        this.vx = (Math.random() - 0.5) * 0.35;
        this.vy = (Math.random() - 0.5) * 0.35;
        this.r  = Math.random() * 1.8 + 0.6;
        // 70% amber, 30% blue
        this.isAmber = Math.random() < 0.70;
        this.alpha = Math.random() * 0.5 + 0.2;
        this.pulseSpeed = Math.random() * 0.02 + 0.008;
        this.pulseOffset = Math.random() * Math.PI * 2;
      }

      update(t) {
        this.x += this.vx;
        this.y += this.vy;
        // pulse alpha
        this.currentAlpha = this.alpha + Math.sin(t * this.pulseSpeed + this.pulseOffset) * 0.12;

        // wrap
        if (this.x < -20) this.x = W + 20;
        if (this.x > W + 20) this.x = -20;
        if (this.y < -20) this.y = H + 20;
        if (this.y > H + 20) this.y = -20;
      }

      draw() {
        const color = this.isAmber
          ? `rgba(251, 191, 36, ${this.currentAlpha})`
          : `rgba(59, 130, 246, ${this.currentAlpha * 0.75})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.shadowBlur = this.r * 6;
        ctx.shadowColor = color;
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    }

    for (let i = 0; i < N_PARTICLES; i++) particles.push(new Particle());

    // ---- Floating legal symbols ----
    const SYMBOLS = ['⚖', '§', '¶', '⚡', '◈'];
    const floats = Array.from({ length: 8 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      symbol: SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)],
      size: Math.random() * 18 + 10,
      vx: (Math.random() - 0.5) * 0.15,
      vy: -(Math.random() * 0.2 + 0.08),
      alpha: Math.random() * 0.04 + 0.02,
      rot: Math.random() * Math.PI * 2,
      rotSpeed: (Math.random() - 0.5) * 0.003,
    }));

    let t = 0;
    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      t++;

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < CONNECT_DIST) {
            const opacity = (1 - dist / CONNECT_DIST) * 0.18;
            const isAmber = particles[i].isAmber && particles[j].isAmber;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = isAmber
              ? `rgba(251, 191, 36, ${opacity})`
              : `rgba(59, 130, 246, ${opacity * 0.7})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }

      // Draw & update particles
      particles.forEach((p) => { p.update(t); p.draw(); });

      // Draw floating legal symbols
      floats.forEach((f) => {
        f.x += f.vx;
        f.y += f.vy;
        f.rot += f.rotSpeed;

        if (f.y < -40) {
          f.y = H + 40;
          f.x = Math.random() * W;
        }
        if (f.x < -40) f.x = W + 40;
        if (f.x > W + 40) f.x = -40;

        // Pulse alpha
        const pulse = f.alpha + Math.sin(t * 0.008 + f.x) * 0.015;

        ctx.save();
        ctx.translate(f.x, f.y);
        ctx.rotate(f.rot);
        ctx.globalAlpha = pulse;
        ctx.font = `${f.size}px 'Outfit', sans-serif`;
        ctx.fillStyle = '#FBBF24';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(f.symbol, 0, 0);
        ctx.restore();
        ctx.globalAlpha = 1;
      });

      animId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
        opacity: 0.85,
      }}
    />
  );
}
