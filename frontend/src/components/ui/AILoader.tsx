/**
 * AI Loader - Premium loading animations for AI operations
 * Multiple variants: spinner, dots, neural, brain
 */

import { motion } from 'framer-motion';

interface AILoaderProps {
  variant?: 'spinner' | 'dots' | 'neural' | 'brain';
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export const AILoader: React.FC<AILoaderProps> = ({
  variant = 'neural',
  size = 'md',
  text,
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  // Neural Network Animation
  if (variant === 'neural') {
    return (
      <div className="flex flex-col items-center gap-4">
        <div className={`relative ${sizeClasses[size]}`}>
          {/* Outer ring */}
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-ai-primary/30"
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          />
          {/* Middle ring */}
          <motion.div
            className="absolute inset-1 rounded-full border-2 border-ai-secondary/40"
            animate={{ rotate: -360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          />
          {/* Inner pulsing core */}
          <motion.div
            className="absolute inset-2 rounded-full bg-gradient-to-br from-ai-primary to-ai-secondary"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.7, 1, 0.7],
            }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          />
          {/* Glowing particles */}
          {[0, 1, 2, 3].map((i) => (
            <motion.div
              key={i}
              className="absolute w-1.5 h-1.5 rounded-full bg-ai-accent"
              style={{
                top: '50%',
                left: '50%',
                transformOrigin: 'center',
              }}
              animate={{
                x: [0, Math.cos((i * Math.PI) / 2) * 20, 0],
                y: [0, Math.sin((i * Math.PI) / 2) * 20, 0],
                opacity: [0, 1, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.3,
                ease: 'easeInOut',
              }}
            />
          ))}
        </div>
        {text && (
          <motion.p
            className={`text-gray-600 font-medium ${textSizeClasses[size]}`}
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {text}
          </motion.p>
        )}
      </div>
    );
  }

  // Dots Animation
  if (variant === 'dots') {
    return (
      <div className="flex flex-col items-center gap-4">
        <div className="flex gap-2">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-3 h-3 rounded-full bg-gradient-to-br from-ai-primary to-ai-secondary"
              animate={{
                y: [0, -12, 0],
                scale: [1, 1.2, 1],
              }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                delay: i * 0.15,
                ease: 'easeInOut',
              }}
            />
          ))}
        </div>
        {text && (
          <p className={`text-gray-600 font-medium ${textSizeClasses[size]}`}>
            {text}
          </p>
        )}
      </div>
    );
  }

  // Brain Animation (AI thinking)
  if (variant === 'brain') {
    return (
      <div className="flex flex-col items-center gap-4">
        <div className={`relative ${sizeClasses[size]}`}>
          <motion.div
            className="absolute inset-0 rounded-full bg-gradient-to-br from-ai-primary/20 to-ai-secondary/20"
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          />
          <motion.div
            className="absolute inset-2 rounded-full bg-gradient-to-br from-ai-primary to-ai-secondary flex items-center justify-center"
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          >
            <svg
              className="w-1/2 h-1/2 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
            </svg>
          </motion.div>
          {/* Synapse lines */}
          {[0, 60, 120, 180, 240, 300].map((angle, i) => (
            <motion.div
              key={i}
              className="absolute w-0.5 h-4 bg-gradient-to-t from-ai-primary to-transparent"
              style={{
                top: '50%',
                left: '50%',
                transformOrigin: 'bottom center',
                transform: `rotate(${angle}deg) translateY(-100%)`,
              }}
              animate={{ opacity: [0.2, 1, 0.2] }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: i * 0.15,
              }}
            />
          ))}
        </div>
        {text && (
          <motion.p
            className={`text-gray-600 font-medium ${textSizeClasses[size]}`}
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {text}
          </motion.p>
        )}
      </div>
    );
  }

  // Default Spinner
  return (
    <div className="flex flex-col items-center gap-4">
      <div className={`ai-loader ${sizeClasses[size]}`} />
      {text && (
        <p className={`text-gray-600 font-medium ${textSizeClasses[size]}`}>
          {text}
        </p>
      )}
    </div>
  );
};
