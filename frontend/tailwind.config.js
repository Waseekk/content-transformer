/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Premium AI Color Palette
      colors: {
        ai: {
          primary: '#6366f1',    // Indigo - main AI color
          secondary: '#8b5cf6',  // Purple - secondary
          accent: '#06b6d4',     // Cyan - accents
          glow: '#a855f7',       // Purple glow
          dark: '#0f0f23',       // Deep dark
          surface: '#1a1a2e',    // Card surface
        },
        premium: {
          cream: '#FAF8F5',
          warm: '#F5F3F0',
          gold: '#f59e0b',
        }
      },
      // Custom Animations
      animation: {
        'gradient-x': 'gradient-x 15s ease infinite',
        'gradient-y': 'gradient-y 15s ease infinite',
        'gradient-xy': 'gradient-xy 15s ease infinite',
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'shimmer': 'shimmer 2s linear infinite',
        'spin-slow': 'spin 8s linear infinite',
        'bounce-slow': 'bounce 3s infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'fade-in-up': 'fadeInUp 0.5s ease-out',
        'fade-in-down': 'fadeInDown 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.4s ease-out',
        'slide-in-left': 'slideInLeft 0.4s ease-out',
        'neural-pulse': 'neuralPulse 2s ease-in-out infinite',
        'typing': 'typing 1.5s steps(20) infinite',
      },
      keyframes: {
        'gradient-y': {
          '0%, 100%': {
            'background-size': '400% 400%',
            'background-position': 'center top'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'center center'
          }
        },
        'gradient-x': {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          }
        },
        'gradient-xy': {
          '0%, 100%': {
            'background-size': '400% 400%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          }
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' }
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(99, 102, 241, 0.5), 0 0 20px rgba(99, 102, 241, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.8), 0 0 40px rgba(99, 102, 241, 0.5)' }
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' }
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' }
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' }
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' }
        },
        neuralPulse: {
          '0%, 100%': { opacity: '0.4', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' }
        },
        typing: {
          '0%': { width: '0' },
          '50%': { width: '100%' },
          '100%': { width: '0' }
        }
      },
      // Premium Shadows
      boxShadow: {
        'glow-sm': '0 0 15px rgba(99, 102, 241, 0.3)',
        'glow-md': '0 0 30px rgba(99, 102, 241, 0.4)',
        'glow-lg': '0 0 50px rgba(99, 102, 241, 0.5)',
        'glow-purple': '0 0 30px rgba(168, 85, 247, 0.4)',
        'glow-cyan': '0 0 30px rgba(6, 182, 212, 0.4)',
        'premium': '0 4px 20px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.1)',
        'premium-lg': '0 10px 40px rgba(0, 0, 0, 0.1), 0 0 1px rgba(0, 0, 0, 0.1)',
        'inner-glow': 'inset 0 0 20px rgba(99, 102, 241, 0.1)',
      },
      // Premium Border Radius
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      // Backdrop Blur
      backdropBlur: {
        xs: '2px',
      },
      // Font Family
      fontFamily: {
        bengali: ['Noto Sans Bengali', 'SolaimanLipi', 'Kalpurush', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
