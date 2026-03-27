import js from '@eslint/js';
import prettier from 'eslint-config-prettier';
import prettierPlugin from 'eslint-plugin-prettier';

/** @type {import("eslint").Linter.Config[]} */
export default [
  js.configs.recommended, // Base recommended JS rules
  prettier, // Disables ESLint rules that conflict with Prettier
  {
    plugins: {
      prettier: prettierPlugin,
    },
    rules: {
      'prettier/prettier': 'error', // Runs Prettier as an ESLint rule
    },
    ignores: ['node_modules', 'dist', 'build'], // Files/folders to ignore
  },
];
