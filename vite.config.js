import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { copyFileSync, mkdirSync, readdirSync, existsSync } from 'fs'

// 复制docs目录到dist
function copyDocsDir() {
  const srcDir = resolve(__dirname, 'docs')
  const destDir = resolve(__dirname, 'dist/docs')
  
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
  
  copyDir(srcDir, destDir)
  console.log('Docs directory copied to dist/docs')
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    writeBundle: () => {
      copyDocsDir()
    }
  }
})
