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
const currentPath = ref('/docs/前端知识/HTML/基础标签.md')
const markdownContent = ref('')
const searchQuery = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const menuCollapsed = ref(false)

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

// 加载Markdown文件
const loadMarkdown = async (path) => {
  try {
    const response = await fetch(path)
    if (response.ok) {
      const content = await response.text()
      markdownContent.value = md.render(content)
      currentPath.value = path
      showSearchResults.value = false
    }
  } catch (error) {
    console.error('Failed to load markdown:', error)
  }
}

// 处理菜单点击
const handleMenuClick = (item) => {
  if (item.path) {
    loadMarkdown(item.path)
  } else if (item.children) {
    item.expanded = !item.expanded
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
        allDocs.push(item)
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
  loadMarkdown(result.item.path)
}

// 切换菜单展开/收起
const toggleMenu = () => {
  menuCollapsed.value = !menuCollapsed.value
}

// 初始加载
onMounted(() => {
  loadMarkdown(currentPath.value)
})
</script>

<template>
  <div class="app">
    <!-- 顶部导航栏 -->
    <header class="navbar">
      <div class="navbar-left">
        <button class="menu-toggle" @click="toggleMenu">
          {{ menuCollapsed ? '☰' : '☰' }}
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
            <a v-if="prevNextDocs.prev" @click="loadMarkdown(prevNextDocs.prev.path)" class="prev-doc">
              ← {{ prevNextDocs.prev.name }}
            </a>
            <a v-if="prevNextDocs.next" @click="loadMarkdown(prevNextDocs.next.path)" class="next-doc">
              {{ prevNextDocs.next.name }} →
            </a>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f5f5f5;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.navbar {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
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
  padding: 5px;
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.search-container {
  position: relative;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 14px;
  width: 300px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #4CAF50;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
}

.search-result-item {
  padding: 10px 15px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-result-item:hover {
  background-color: #f5f5f5;
}

/* 主容器 */
.main-container {
  flex: 1;
  display: flex;
}

/* 左侧菜单 */
.sidebar {
  width: 280px;
  background-color: #fff;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 60px;
}

.menu-list {
  list-style: none;
  padding: 20px 0;
}

.menu-item {
  margin-bottom: 5px;
}

.menu-item-header {
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.menu-item-header:hover {
  background-color: #f5f5f5;
}

.menu-icon {
  font-size: 16px;
}

.menu-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.menu-toggle-icon {
  font-size: 12px;
  color: #666;
}

.sub-menu {
  list-style: none;
  padding-left: 20px;
}

.sub-menu-item {
  margin-bottom: 3px;
}

.sub-menu-item-header {
  padding: 8px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.sub-menu-item-header:hover {
  background-color: #f5f5f5;
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
  margin-bottom: 2px;
}

.sub-sub-menu-item-header {
  padding: 6px 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 12px;
}

.sub-sub-menu-item-header:hover {
  background-color: #f5f5f5;
}

.sub-sub-menu-item.active {
  background-color: #e8f5e8;
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
  padding: 10px;
  justify-content: center;
}

/* 右侧内容区 */
.content {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  background-color: #f5f5f5;
}

.markdown-container {
  max-width: 800px;
  margin: 0 auto;
  background-color: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.markdown-content {
  line-height: 1.8;
}

.markdown-content h1 {
  font-size: 28px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.markdown-content h2 {
  font-size: 24px;
  margin-top: 30px;
  margin-bottom: 15px;
}

.markdown-content h3 {
  font-size: 20px;
  margin-top: 20px;
  margin-bottom: 10px;
}

.markdown-content p {
  margin-bottom: 15px;
}

.markdown-content ul,
.markdown-content ol {
  margin-bottom: 15px;
  padding-left: 30px;
}

.markdown-content li {
  margin-bottom: 5px;
}

.markdown-content code {
  background-color: #f4f4f4;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
}

.markdown-content pre {
  background-color: #f4f4f4;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
  margin-bottom: 15px;
}

.markdown-content pre code {
  background: none;
  padding: 0;
}

.markdown-content a {
  color: #4CAF50;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.markdown-content img {
  max-width: 100%;
  height: auto;
  border-radius: 5px;
  margin: 15px 0;
}

/* 上一篇/下一篇导航 */
.prev-next-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.prev-doc,
.next-doc {
  color: #4CAF50;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.prev-doc:hover,
.next-doc:hover {
  color: #45a049;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    padding: 0 10px;
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
    top: 60px;
    bottom: 0;
    z-index: 99;
    transform: translateX(-100%);
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .content {
    padding: 20px;
  }
  
  .markdown-container {
    padding: 20px;
  }
}
</style>
