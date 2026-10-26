import { nodeResolve } from '@rollup/plugin-node-resolve';
import terser from '@rollup/plugin-terser';

// The card ships inside the integration: the build output goes straight into
// custom_components/magister_school/www, which is served as a static path and
// registered as a Lovelace resource on setup.
export default {
  input: 'src/magister-school-card.js',
  output: {
    file: '../custom_components/magister_school/www/magister-school-card.js',
    format: 'es',
    sourcemap: false,
  },
  plugins: [
    nodeResolve(),
    terser(),
  ],
};
