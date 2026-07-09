import resolve from '@rollup/plugin-node-resolve'
import less from 'rollup-plugin-less'
import serve from 'rollup-plugin-serve'
import livereload from 'rollup-plugin-livereload'

export default {
  input: 'src/main.js',

  output: {
    file: 'dist/bundle.js',
    format: 'iife',
  },

  plugins: [
    resolve(),

    // 支持 less → css
    less({
      output: 'dist/bundle.css'
    }),

    // 本地服务 + 热更新
    serve({
      open: true,
      contentBase: ['dist', 'src']
    }),
    livereload()
  ]
}