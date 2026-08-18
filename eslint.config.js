import js from '@eslint/js';

export default [
  js.configs.recommended,
  {
    files: ["**/*.{js,ts,mjs,cjs}"],
    languageOptions: {
      ecmaVersion: "latest"
    },
    rules: {
      "no-unused-vars": "warn",
      "no-console": "off"
    }
  }
];