/**
 * Cursor Glow Effect - Subtle light following cursor
 * Lightweight implementation with smooth performance
 */

import { useEffect, useRef } from 'react';

export const CursorGlow = () => {
  const glowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const glow = glowRef.current;
    if (!glow) return;

    let animationFrame: number;
    let currentX = 0;
    let currentY = 0;
    let targetX = 0;
    let targetY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      targetX = e.clientX;
      targetY = e.clientY;
      glow.classList.add('active');
    };

    const handleMouseLeave = () => {
      glow.classList.remove('active');
    };

    const animate = () => {
      // Smooth lerp for fluid movement
      currentX += (targetX - currentX) * 0.1;
      currentY += (targetY - currentY) * 0.1;

      glow.style.left = `${currentX}px`;
      glow.style.top = `${currentY}px`;

      animationFrame = requestAnimationFrame(animate);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);
    animate();

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
      cancelAnimationFrame(animationFrame);
    };
  }, []);

  return <div ref={glowRef} className="cursor-glow" />;
};
