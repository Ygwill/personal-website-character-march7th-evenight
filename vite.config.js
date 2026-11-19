import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import character from './src/data/character.js'

// 标题 / 描述在构建时从 character.js 注入，换角色不用改 index.html
function htmlMeta() {
  const title = `${character.name} · 崩坏：星穹铁道角色页`
  const desc = `${character.name}（${character.pathName} · ${character.elementName}）角色资料页，`
    + '文本与数值取自官方解包索引，推导规则与未采信来源见页面「数据溯源」。'
  return {
    name: 'html-meta',
    transformIndexHtml(html) {
      return html.replace('<!--TITLE-->', title).replace('<!--DESC-->', desc)
    },
  }
}

// base 用相对路径，便于部署到 /<角色名>/ 这类子路径下
export default defineConfig({
  plugins: [htmlMeta(), vue()],
  base: './',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: { host: '127.0.0.1', port: 5177 },
  // 构建时刻注入页脚，方便判断线上是不是旧包（不是运行时时间）
  define: { __BUILD_AT__: JSON.stringify(new Date().toISOString().replace('T', ' ').slice(0, 16)) },
  build: { outDir: 'dist', assetsDir: 'assets', sourcemap: false },
})
