/**
 * Glow Button - Premium button with animated glow effects
 */

import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface GlowButtonProps {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  icon?: ReactNode;
  loading?: boolean;
}

export const GlowButton: React.FC<GlowButtonProps> = ({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  size = 'md',
  className = '',
  icon,
  loading = false,
}) => {
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm gap-1.5',
    md: 'px-6 py-3 text-base gap-2',
    lg: 'px-8 py-4 text-lg gap-3',
  };

  const variantClasses = {
    primary: `
      bg-gradient-to-r from-ai-primary to-ai-secondary text-white
      hover:shadow-glow-md
    `,
    secondary: `
      bg-white text-ai-primary border-2 border-ai-primary/30
      hover:border-ai-primary hover:bg-ai-primary/5 hover:shadow-glow-sm
    `,
    ghost: `
      bg-transparent text-ai-primary
      hover:bg-ai-primary/10
    `,
  };

  const isDisabled = disabled || loading;

  return (
    <motion.button
      onClick={onClick}
      disabled={isDisabled}
      whileHover={!isDisabled ? { scale: 1.02 } : undefined}
      whileTap={!isDisabled ? { scale: 0.98 } : undefined}
      className={`
        relative inline-flex items-center justify-center font-semibold rounded-xl
        transition-all duration-300 overflow-hidden
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      {/* Animated gradient overlay for primary */}
      {variant === 'primary' && !isDisabled && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-ai-secondary to-ai-primary opacity-0"
          whileHover={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        />
      )}

      {/* Content */}
      <span className="relative z-10 flex items-center gap-2">
        {loading ? (
          <motion.div
            className="w-5 h-5 border-2 border-current border-t-transparent rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
        ) : (
          icon
        )}
        {children}
      </span>

      {/* Shimmer effect on hover */}
      {variant === 'primary' && !isDisabled && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
          initial={{ x: '-100%' }}
          whileHover={{ x: '100%' }}
          transition={{ duration: 0.6 }}
        />
      )}
    </motion.button>
  );
};
