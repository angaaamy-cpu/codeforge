/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
        arabic: ['Cairo', 'Tajawal', 'sans-serif'],
      },
      colors: {
        ink: {
          950: '#0a0b0f', 900: '#0e1015', 850: '#13161d',
          800: '#181c25', 750: '#1d2230', 700: '#252b3a',
          600: '#3a4252', 500: '#5b6478', 400: '#8a93a6',
          300: '#b4bcc9', 200: '#d7dce4', 100: '#eef1f5',
        },
        brand: {
          50: '#eefcff', 100: '#d4f9ff', 200: '#a8f1ff', 300: '#6ce4ff',
          400: '#22d3ee', 500: '#06b6d4', 600: '#0891b2', 700: '#0e7490',
          800: '#155e75', 900: '#164e63',
        },
        emerald: { 400: '#34d399', 500: '#10b981', 600: '#059669' },
        amber:  { 400: '#fbbf24', 500: '#f59e0b', 600: '#d97706' },
        rose:   { 400: '#fb7185', 500: '#f43f5e', 600: '#e11d48' },
      },
      keyframes: {
        'fade-in':   { '0%': { opacity: 0, transform: 'translateY(4px)' }, '100%': { opacity: 1, transform: 'translateY(0)' } },
        'slide-in':  { '0%': { opacity: 0, transform: 'translateX(-8px)' }, '100%': { opacity: 1, transform: 'translateX(0)' } },
        'pulse-soft':{ '0%,100%': { opacity: 1 }, '50%': { opacity: 0.5 } },
        'spin-slow': { to: { transform: 'rotate(360deg)' } },
        'shimmer':   { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
      },
      animation: {
        'fade-in': 'fade-in 0.25s ease-out',
        'slide-in': 'slide-in 0.3s ease-out',
        'pulse-soft': 'pulse-soft 1.6s ease-in-out infinite',
        'spin-slow': 'spin-slow 1.2s linear infinite',
        shimmer: 'shimmer 2s linear infinite',
      },
    },
  },
  plugins: [],
}
