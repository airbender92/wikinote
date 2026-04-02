<script setup>
import { ref, onMounted, computed } from 'vue'
import MarkdownIt from 'markdown-it'
import Fuse from 'fuse.js'
import menuConfig from './menuConfig.js'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function(str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return ''
  }
})

const menu = ref(menuConfig)
const currentPath = ref('')
const markdownContent = ref('')
const searchQuery = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const menuCollapsed = ref(false)
const darkMode = ref(false)

// 计算属性：获取当前文档的上一篇和下一篇
const prevNextDocs = computed(() => {
  const allDocs = []
  const flattenMenu = (items) => {
    items.forEach(item => {
      if (item.path) {
        allDocs.push(item)
      }
      if (item.children) {
        flattenMenu(item.children)
      }
    })
  }
  flattenMenu(menu.value)
  
  const currentIndex = allDocs.findIndex(doc => doc.path === currentPath.value)
  return {
    prev: currentIndex > 0 ? allDocs[currentIndex - 1] : null,
    next: currentIndex < allDocs.length - 1 ? allDocs[currentIndex + 1] : null
  }
})

// 递归查找菜单项的完整路径（包括所有祖先路径）
const findItemFullPath = (items, targetId, parentPath = '') => {
  for (const item of items) {
    // 检查当前项是否是目标项
    if (item.id === targetId) {
      // 如果是绝对路径且以目录分隔符结尾（目录路径）
      if (item.path && item.path.startsWith('/') && item.path.endsWith('/')) {
        return item.path
      }
      // 如果是绝对路径且不以目录分隔符结尾（文件路径）
      else if (item.path && item.path.startsWith('/')) {
        return item.path
      }
      // 如果是相对路径
      else if (item.path && item.path.startsWith('./')) {
        return `${parentPath}/${item.path.substring(2)}`.replace(/\/\//g, '/')
      }
      // 如果没有路径，返回null
      return null
    }
    
    // 检查子项
    if (item.children) {
      // 计算当前项的路径（用于子项）
      let currentItemPath = parentPath
      if (item.path) {
        if (item.path.startsWith('./')) {
          // 相对路径：基于父级路径构建
          currentItemPath = `${parentPath}/${item.path.substring(2)}`.replace(/\/\//g, '/')
        } else if (item.path.startsWith('/')) {
          // 绝对路径：直接使用
          currentItemPath = item.path
          // 如果是文件路径，提取目录部分
          if (item.path.endsWith('.md')) {
            const lastSlashIndex = item.path.lastIndexOf('/')
            if (lastSlashIndex !== -1) {
              currentItemPath = item.path.substring(0, lastSlashIndex)
            }
          }
        }
      }
      
      const foundPath = findItemFullPath(item.children, targetId, currentItemPath)
      if (foundPath) return foundPath
    }
  }
  return null
}

// 递归查找菜单项本身
const findMenuItem = (items, id) => {
  for (const item of items) {
    if (item.id === id) {
      return item
    }
    if (item.children) {
      const found = findMenuItem(item.children, id)
      if (found) return found
    }
  }
  return null
}

// 加载Markdown文件 - 使用菜单项ID
const loadMarkdown = async (itemId) => {
  try {
    // 查找菜单项
    const item = findMenuItem(menu.value, itemId)
    if (!item || !item.path) {
      console.error('Menu item not found or has no path:', itemId)
      return
    }
    
    // 获取完整路径（递归包含所有祖先路径）
    const fullPath = findItemFullPath(menu.value, itemId)
    if (!fullPath) {
      console.error('Could not determine full path for item:', itemId)
      return
    }
    
    console.log('Loading markdown from:', fullPath)
    const response = await fetch(fullPath)
    if (response.ok) {
      const content = await response.text()
      markdownContent.value = md.render(content)
      currentPath.value = fullPath
      showSearchResults.value = false
    } else {
      console.error(`Failed to load ${fullPath}: HTTP ${response.status}`)
    }
  } catch (error) {
    console.error('Failed to load markdown:', error)
  }
}

// 处理菜单点击 - 传递菜单项ID
const handleMenuClick = (item) => {
  // 如果有子菜单，只展开/折叠
  if (item.children) {
    item.expanded = !item.expanded
  } else if (item.id) {
    // 使用菜单项ID加载文档
    loadMarkdown(item.id)
  }
}

// 搜索功能
const handleSearch = () => {
  if (!searchQuery.value) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }

  const allDocs = []
  const flattenMenu = (items) => {
    items.forEach(item => {
      if (item.path) {
        allDocs.push({...item, id: item.id}) // 确保有id
      }
      if (item.children) {
        flattenMenu(item.children)
      }
    })
  }
  flattenMenu(menu.value)

  const fuse = new Fuse(allDocs, {
    keys: ['name'],
    threshold: 0.3
  })

  searchResults.value = fuse.search(searchQuery.value)
  showSearchResults.value = true
}

// 处理搜索结果点击
const handleSearchResultClick = (result) => {
  loadMarkdown(result.item.id)
}

// 切换菜单展开/收起
const toggleMenu = () => {
  menuCollapsed.value = !menuCollapsed.value
}

// 切换深色模式
const toggleDarkMode = () => {
  darkMode.value = !darkMode.value
  document.documentElement.classList.toggle('dark', darkMode.value)
}

// 获取第一个可用的文档ID
const getFirstDocId = () => {
  const findFirstDoc = (items) => {
    for (const item of items) {
      if (item.path) {
        return item.id
      }
      if (item.children) {
        const result = findFirstDoc(item.children)
        if (result) return result
      }
    }
    return null
  }
  
  return findFirstDoc(menu.value)
}

// 初始加载
onMounted(() => {
  const firstDocId = getFirstDocId()
  if (firstDocId) {
    loadMarkdown(firstDocId)
  }
})
</script>

<template>
  <div class="app">
    <!-- 顶部导航栏 -->
    <header class="navbar">
      <div class="navbar-left">
        <button class="menu-toggle" @click="toggleMenu" aria-label="Toggle menu">
          ☰
        </button>
        <h1 class="app-title">Markdown 知识点文档系统</h1>
      </div>
      <div class="navbar-right">
        <div class="search-container">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索知识点..."
            class="search-input"
            @input="handleSearch"
            @focus="handleSearch"
            aria-label="Search"
          />
          <div v-if="showSearchResults && searchResults.length > 0" class="search-results">
            <div
              v-for="result in searchResults"
              :key="result.item.id"
              class="search-result-item"
              @click="handleSearchResultClick(result)"
            >
              {{ result.item.name }}
            </div>
          </div>
        </div>
        <button class="dark-mode-toggle" @click="toggleDarkMode" aria-label="Toggle dark mode">
          {{ darkMode ? '🌞' : '🌙' }}
        </button>
      </div>
    </header>

    <div class="main-container">
      <!-- 左侧菜单 -->
      <aside :class="['sidebar', { 'collapsed': menuCollapsed }]">
        <nav class="menu">
          <ul class="menu-list">
            <li
              v-for="item in menu"
              :key="item.id"
              class="menu-item"
            >
              <div
                class="menu-item-header"
                @click="handleMenuClick(item)"
              >
                <span class="menu-icon">{{ item.icon }}</span>
                <span class="menu-name">{{ item.name }}</span>
                <span v-if="item.children" class="menu-toggle-icon">
                  {{ item.expanded ? '▼' : '▶' }}
                </span>
              </div>
              <ul v-if="item.children && item.expanded" class="sub-menu">
                <li
                  v-for="subItem in item.children"
                  :key="subItem.id"
                  class="sub-menu-item"
                >
                  <div
                    class="sub-menu-item-header"
                    @click="handleMenuClick(subItem)"
                  >
                    <span class="sub-menu-name">{{ subItem.name }}</span>
                    <span v-if="subItem.children" class="menu-toggle-icon">
                      {{ subItem.expanded ? '▼' : '▶' }}
                    </span>
                  </div>
                  <ul v-if="subItem.children && subItem.expanded" class="sub-sub-menu">
                    <li
                      v-for="subSubItem in subItem.children"
                      :key="subSubItem.id"
                      class="sub-sub-menu-item"
                      :class="{ 'active': subSubItem.path === currentPath }"
                    >
                      <div
                        class="sub-sub-menu-item-header"
                        @click="handleMenuClick(subSubItem)"
                      >
                        <span class="sub-sub-menu-name">{{ subSubItem.name }}</span>
                      </div>
                    </li>
                  </ul>
                </li>
              </ul>
            </li>
          </ul>
        </nav>
      </aside>

      <!-- 右侧内容区 -->
      <main class="content">
        <div class="markdown-container">
          <div v-html="markdownContent" class="markdown-content"></div>
          
          <!-- 上一篇/下一篇导航 -->
          <div class="prev-next-nav">
            <a v-if="prevNextDocs.prev" @click="loadMarkdown(prevNextDocs.prev.id)" class="prev-doc">
              ← {{ prevNextDocs.prev.name }}
            </a>
            <a v-if="prevNextDocs.next" @click="loadMarkdown(prevNextDocs.next.id)" class="next-doc">
              {{ prevNextDocs.next.name }} →
            </a>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style>
/* 样式保持不变 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --text-primary: #333333;
  --text-secondary: #666666;
  --border-color: #e0e0e0;
  --accent-color: #4CAF50;
  --accent-hover: #45a049;
  --hover-bg: #f5f5f5;
  --active-bg: #e8f5e8;
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  --sidebar-width: 280px;
  --sidebar-width-collapsed: 60px;
  --navbar-height: 60px;
  --transition: all 0.3s ease;
}

.dark {
  --bg-primary: #1e1e1e;
  --bg-secondary: #2d2d2d;
  --text-primary: #e0e0e0;
  --text-secondary: #b0b0b0;
  --border-color: #404040;
  --accent-color: #66bb6a;
  --accent-hover: #4caf50;
  --hover-bg: #2d2d2d;
  --active-bg: #2e7d32;
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  line-height: 1.6;
  color: var(--text-primary);
  background-color: var(--bg-secondary);
  transition: var(--transition);
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.navbar {
  background-color: var(--bg-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
  height: var(--navbar-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: var(--transition);
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.menu-toggle {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: var(--transition);
  color: var(--text-primary);
}

.menu-toggle:hover {
  background-color: var(--hover-bg);
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  transition: var(--transition);
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.search-container {
  position: relative;
}

.search-input {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 14px;
  width: 300px;
  outline: none;
  transition: var(--transition);
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.search-input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 0 0 8px 8px;
  box-shadow: var(--shadow);
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
  transition: var(--transition);
}

.search-result-item {
  padding: 10px 15px;
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-primary);
}

.search-result-item:hover {
  background-color: var(--hover-bg);
}

.dark-mode-toggle {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: var(--transition);
  color: var(--text-primary);
}

.dark-mode-toggle:hover {
  background-color: var(--hover-bg);
}

/* 主容器 */
.main-container {
  flex: 1;
  display: flex;
}

/* 左侧菜单 */
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--bg-primary);
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  transition: var(--transition);
  height: calc(100vh - var(--navbar-height));
  position: sticky;
  top: var(--navbar-height);
}

.sidebar.collapsed {
  width: var(--sidebar-width-collapsed);
}

.menu-list {
  list-style: none;
  padding: 20px 0;
}

.menu-item {
  margin-bottom: 2px;
}

.menu-item-header {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: var(--transition);
  border-radius: 0 8px 8px 0;
  margin-right: 10px;
  color: var(--text-primary);
}

.menu-item-header:hover {
  background-color: var(--hover-bg);
}

.menu-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.menu-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.menu-toggle-icon {
  font-size: 12px;
  color: var(--text-secondary);
  transition: var(--transition);
}

.sub-menu {
  list-style: none;
  padding-left: 24px;
}

.sub-menu-item {
  margin-bottom: 1px;
}

.sub-menu-item-header {
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: var(--transition);
  border-radius: 0 8px 8px 0;
  margin-right: 10px;
  color: var(--text-primary);
}

.sub-menu-item-header:hover {
  background-color: var(--hover-bg);
}

.sub-menu-name {
  flex: 1;
  font-size: 13px;
}

.sub-sub-menu {
  list-style: none;
  padding-left: 20px;
}

.sub-sub-menu-item {
  margin-bottom: 1px;
}

.sub-sub-menu-item-header {
  padding: 8px 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: var(--transition);
  font-size: 12px;
  border-radius: 0 8px 8px 0;
  margin-right: 10px;
  color: var(--text-primary);
}

.sub-sub-menu-item-header:hover {
  background-color: var(--hover-bg);
}

.sub-sub-menu-item.active {
  background-color: var(--active-bg);
  font-weight: 500;
}

.sub-sub-menu-name {
  flex: 1;
}

.sidebar.collapsed .menu-name,
.sidebar.collapsed .sub-menu-name,
.sidebar.collapsed .sub-sub-menu-name,
.sidebar.collapsed .menu-toggle-icon {
  display: none;
}

.sidebar.collapsed .menu-item-header,
.sidebar.collapsed .sub-menu-item-header,
.sidebar.collapsed .sub-sub-menu-item-header {
  padding: 12px;
  justify-content: center;
  margin-right: 0;
  border-radius: 4px;
}

/* 右侧内容区 */
.content {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  background-color: var(--bg-secondary);
  transition: var(--transition);
  min-height: calc(100vh - var(--navbar-height));
}

.markdown-container {
  max-width: 850px;
  margin: 0 auto;
  background-color: var(--bg-primary);
  padding: 40px;
  border-radius: 8px;
  box-shadow: var(--shadow);
  transition: var(--transition);
}

.markdown-content {
  line-height: 1.8;
  text-align: left;
}

.markdown-content h1 {
  font-size: 32px;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  transition: var(--transition);
}

.markdown-content h2 {
  font-size: 26px;
  margin-top: 32px;
  margin-bottom: 18px;
  color: var(--text-primary);
  transition: var(--transition);
}

.markdown-content h3 {
  font-size: 22px;
  margin-top: 24px;
  margin-bottom: 12px;
  color: var(--text-primary);
  transition: var(--transition);
}

.markdown-content p {
  margin-bottom: 18px;
  color: var(--text-primary);
  transition: var(--transition);
}

.markdown-content ul,
.markdown-content ol {
  margin-bottom: 18px;
  padding-left: 32px;
  color: var(--text-primary);
  transition: var(--transition);
}

.markdown-content li {
  margin-bottom: 8px;
}

.markdown-content code {
  background-color: var(--hover-bg);
  padding: 3px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Courier New', Courier, monospace;
  font-size: 14px;
  color: var(--text-primary);
  transition: var(--transition);
}

.markdown-content pre {
  background-color: var(--hover-bg);
  padding: 18px;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 18px;
  transition: var(--transition);
  border: 1px solid var(--border-color);
}

.markdown-content pre code {
  background: none;
  padding: 0;
}

.markdown-content a {
  color: var(--accent-color);
  text-decoration: none;
  transition: var(--transition);
}

.markdown-content a:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

.markdown-content img {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 20px 0;
  box-shadow: var(--shadow);
}

/* 上一篇/下一篇导航 */
.prev-next-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 48px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  transition: var(--transition);
}

.prev-doc,
.next-doc {
  color: var(--accent-color);
  text-decoration: none;
  font-size: 14px;
  transition: var(--transition);
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.prev-doc:hover,
.next-doc:hover {
  color: var(--accent-hover);
  background-color: var(--hover-bg);
  text-decoration: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    padding: 0 15px;
  }
  
  .app-title {
    font-size: 16px;
  }
  
  .search-input {
    width: 200px;
  }
  
  .sidebar {
    position: fixed;
    left: 0;
    top: var(--navbar-height);
    bottom: 0;
    z-index: 99;
    transform: translateX(-100%);
    height: calc(100vh - var(--navbar-height));
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .content {
    padding: 20px;
  }
  
  .markdown-container {
    padding: 24px;
  }
  
  .markdown-content h1 {
    font-size: 28px;
  }
  
  .markdown-content h2 {
    font-size: 24px;
  }
  
  .markdown-content h3 {
    font-size: 20px;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>