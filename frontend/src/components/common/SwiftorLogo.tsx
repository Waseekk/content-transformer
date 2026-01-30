/**
 * SwiftorLogo - Animated logo component with multiple animation variants
 *
 * Variants:
 * 1. typewriter - Smooth typewriter reveal (for Login page)
 * 2. stepReveal - Step-by-step letter reveal (for Dashboard page)
 * 3. colorShift - Matte black/white color animation (for Navbar)
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import './SwiftorLogo.css';

type LogoVariant = 'typewriter' | 'stepReveal' | 'colorShift';

interface SwiftorLogoProps {
  variant: LogoVariant;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  showTagline?: boolean;
}

const sizeClasses = {
  sm: 'h-6',
  md: 'h-10',
  lg: 'h-14',
  xl: 'h-20',
};

export const SwiftorLogo: React.FC<SwiftorLogoProps> = ({
  variant,
  size = 'md',
  className = '',
  showTagline = false,
}) => {
  const [isAnimating, setIsAnimating] = useState(true);

  useEffect(() => {
    // Reset animation on mount
    setIsAnimating(false);
    const timer = setTimeout(() => setIsAnimating(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const heightClass = sizeClasses[size];

  if (variant === 'typewriter') {
    return (
      <div className={`swiftor-logo-container ${className}`}>
        <div className={`typewriter-logo ${isAnimating ? 'animate' : ''}`}>
          <img
            src="/swiftor-logo.png"
            alt="Swiftor"
            className={`${heightClass} w-auto`}
          />
        </div>
        {showTagline && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5 }}
            className="text-sm font-semibold tagline-shimmer mt-2"
          >
            AI Powered Clean and Credible News
          </motion.p>
        )}
      </div>
    );
  }

  if (variant === 'stepReveal') {
    return (
      <div className={`swiftor-logo-container ${className}`}>
        <div className={`step-reveal-logo ${isAnimating ? 'animate' : ''}`}>
          <img
            src="/swiftor-logo.png"
            alt="Swiftor"
            className={`${heightClass} w-auto`}
          />
        </div>
        {showTagline && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="text-sm font-semibold tagline-shimmer mt-2"
          >
            AI Powered Clean and Credible News
          </motion.p>
        )}
      </div>
    );
  }

  if (variant === 'colorShift') {
    return (
      <div className={`swiftor-logo-container color-shift-container ${className}`}>
        <div className="color-shift-logo">
          <img
            src="/swiftor-logo.png"
            alt="Swiftor"
            className={`${heightClass} w-auto`}
          />
        </div>
      </div>
    );
  }

  // Default fallback
  return (
    <img
      src="/swiftor-logo.png"
      alt="Swiftor"
      className={`${heightClass} w-auto ${className}`}
    />
  );
};

export default SwiftorLogo;
