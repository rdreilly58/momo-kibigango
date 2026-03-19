/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        peach: {
          50: "#FDF8F3",
          100: "#FBF1E7",
          200: "#F5D4BE",
          300: "#F0B895",
          400: "#EBA26D",
          500: "#E68C45",
          600: "#D4693A",
          700: "#A83D2A",
          800: "#7C2D20",
          900: "#501E17",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
