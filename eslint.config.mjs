import js from "@eslint/js";
import globals from "globals";

export default [
  { ignores: [".venv/", "node_modules/", "**/*.min.*"] },
  js.configs.recommended,
  {
    linterOptions: { reportUnusedDisableDirectives: "error" },
    rules: {
      curly: ["error", "multi-line"],
      eqeqeq: ["error", "always"],
      "no-implicit-coercion": "error",
      "no-implicit-globals": "error",
      "no-param-reassign": "error",
      "no-shadow": "error",
      "no-use-before-define": ["error", { functions: false }],
      "no-var": "error",
      "object-shorthand": "error",
      "prefer-const": "error",
    },
  },
  {
    // Shipped to browsers as a classic <script>: no modules, no Node.
    files: ["src/jinja_ui_kit/dist/**/*.js"],
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: "script",
      globals: globals.browser,
    },
    rules: { strict: ["error", "function"] },
  },
  {
    files: ["tailwind.config.js"],
    languageOptions: { sourceType: "commonjs", globals: globals.node },
  },
];
