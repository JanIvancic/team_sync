const esbuild = require('esbuild')
const vuePlugin = require('esbuild-plugin-vue3')

esbuild.build({
  entryPoints: ['src/main.js'],
  bundle: true,
  outfile: 'dist/bundle.js',
  minify: true,
  plugins: [vuePlugin()],
  loader: {
    '.vue': 'vue',
    '.js': 'jsx'
  }
}).catch(() => process.exit(1)) 