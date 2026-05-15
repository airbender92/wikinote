import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { copyFileSync, mkdirSync, readdirSync, existsSync } from 'fs'

// 复制指定目录到dist
function copyDir(src, dest) {
  if (!existsSync(dest)) {
    mkdirSync(dest, { recursive: true })
  }
  
  const files = readdirSync(src, { withFileTypes: true })
  for (const file of files) {
    const srcPath = resolve(src, file.name)
    const destPath = resolve(dest, file.name)
    
    if (file.isDirectory()) {
      copyDir(srcPath, destPath)
    } else {
      copyFileSync(srcPath, destPath)
    }
  }
}

// 自定义插件：构建后复制目录
function copyAssetsPlugin() {
  return {
    name: 'copy-assets',
    closeBundle() {
      const srcDir = resolve(__dirname, 'assets')
      const destDir = resolve(__dirname, 'dist/assets')
      copyDir(srcDir, destDir)
      console.log('Assets directory copied to dist/assets')
      
      const docsDir = resolve(__dirname, 'docs')
      const docsDestDir = resolve(__dirname, 'dist/docs')
      copyDir(docsDir, docsDestDir)
      console.log('Docs directory copied to dist/docs')
    }
  }
}

// 自定义插件：打印开发服务器地址
function printServerUrlPlugin() {
  return {
    name: 'print-server-url',
    configureServer(server) {
      server.httpServer?.once('listening', () => {
        const address = server.httpServer?.address()
        const port = typeof address === 'object' ? address?.port : 5173
        console.log('')
        console.log('🚀 开发服务器已启动:')
        console.log(`   本地访问: http://localhost:${port}`)
        console.log(`   网络访问: http://0.0.0.0:${port}`)
        console.log('')
      })
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), copyAssetsPlugin(), printServerUrlPlugin()],
  server: {
    port: 5173,
    strictPort: true,
    host: true
  }
})
