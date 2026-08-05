const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    "./src/jinja_ui_kit/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: colors.blue,
        danger: colors.red,
        success: colors.green,
        neutral: colors.gray,
      },
    },
  },
}
