/**
 * Animated Card - Premium card with framer-motion animations
 */

import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  variant?: 'default' | 'glow' | 'glass';
  onClick?: () => void;
  hover?: boolean;
}

export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  className = '',
  delay = 0,
  variant = 'default',
  onClick,
  hover = true,
}) => {
  const baseClasses = {
    default: 'bg-white rounded-2xl border border-gray-100 shadow-premium',
    glow: 'bg-white rounded-2xl border border-ai-primary/20 shadow-premium',
    glass: 'glass-card rounded-2xl',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.5,
        delay,
        ease: [0.25, 0.46, 0.45, 0.94],
      }}
      whileHover={
        hover
          ? {
              y: -4,
              boxShadow:
                variant === 'glow'
                  ? '0 0 30px rgba(99, 102, 241, 0.3)'
                  : '0 10px 40px rgba(0, 0, 0, 0.1)',
            }
          : undefined
      }
      whileTap={onClick ? { scale: 0.98 } : undefined}
      onClick={onClick}
      className={`${baseClasses[variant]} transition-colors ${className} ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      {children}
    </motion.div>
  );
};

// Stagger container for multiple cards
export const AnimatedCardContainer: React.FC<{
  children: ReactNode;
  className?: string;
}> = ({ children, className = '' }) => {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: {
          opacity: 1,
          transition: {
            staggerChildren: 0.1,
          },
        },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

// Individual item variant for stagger animation
export const StaggerItem: React.FC<{
  children: ReactNode;
  className?: string;
}> = ({ children, className = '' }) => {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: {
          opacity: 1,
          y: 0,
          transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] },
        },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};
