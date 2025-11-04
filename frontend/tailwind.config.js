module.exports = {
  darkMode: 'class',
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#40E0D0',
          600: '#33c9bb',
          500: '#40E0D0',
        },
        accent: '#FF9F42',
        bg: '#FFF9F2',
        muted: '#6B7280',
        success: '#16A34A',
        danger: '#FF5C5C',
      },
      borderRadius: {
        sm: '8px',
        base: '12px',
        lg: '20px',
      },
      boxShadow: {
        soft: '0 6px 18px rgba(2,6,23,0.08)',
        medium: '0 10px 30px rgba(2,6,23,0.12)',
        large: '0 20px 50px rgba(2,6,23,0.16)',
      },
      fontFamily: {
        sans: ['Poppins', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        serif: ['Merriweather', 'Georgia', 'serif'],
      },
      spacing: {
        base: '8px',
      },
    },
  },
  plugins: [],
}
