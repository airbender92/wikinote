const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const pinyinLib = require('pinyin');
const readdir = promisify(fs.readdir);
const stat = promisify(fs.stat);

// 配置项 - 可以根据需要调整
const CONFIG = {
  docDir: 'docs', // 文档目录
  outputPath: 'src/menuConfig.js', // 输出路径
  defaultIcons: {
    '计算机网络基础': '🌐',
    '数据结构与算法': '📚',
    '操作系统基础': '🚀',
    'Java核心语法': '☕',
    'Java Web开发': '☕',
    'Spring Boot': '🌱',
    'SQL数据库': '📊',
    'NoSQL数据库': '📊',
    'RESTful API设计': '🔌',
    'Webpack': '📦'
  },
  defaultExpanded: false, // 默认是否展开
  sortFunction: (a, b) => {
    // 自定义排序函数
    if (a.name === '大纲') return -1;
    if (b.name === '大纲') return 1;
    return a.name.localeCompare(b.name);
  },
  customNameMapping: {
    // 自定义名称映射
    'index.md': '大纲',
    'README.md': '概述'
  }
};

// 生成唯一ID - 使用拼音转换处理中文
function generateId(name, parentPath = '') {
  try {
    // 检查 pinyinLib 是否是函数
    const pinyinFunc = typeof pinyinLib === 'function' ? pinyinLib : 
                      (pinyinLib.default || pinyinLib.pinyin);
    
    // 将中文转换为拼音，保留英文、数字和连字符
    const pinyinName = pinyinFunc(name, {
      style: pinyinLib.STYLE_NORMAL || 1, // 兼容不同版本
      separator: '-'
    }).join('-');
    
    // 清理拼音字符串：只保留字母、数字和连字符
    const cleanPinyin = pinyinName
      .toLowerCase()
      .replace(/[^a-z0-9-]/g, '')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
    
    // 如果拼音为空（纯特殊字符），使用数字哈希
    if (!cleanPinyin) {
      const hash = name.split('').reduce((acc, char) => {
        return acc + char.charCodeAt(0);
      }, 0);
      return `item-${hash}`;
    }
    
    // 如果有父路径，组合成层级ID
    if (parentPath) {
      return `${parentPath}-${cleanPinyin}`;
    }
    
    return cleanPinyin;
  } catch (error) {
    console.warn(`⚠️  ID生成警告: ${name}`, error.message);
    // 回退方案：使用哈希
    const hash = name.split('').reduce((acc, char) => {
      return acc + char.charCodeAt(0);
    }, 0);
    return `fallback-${hash}`;
  }
}

// 处理文件名：移除.md后缀，将-和_转换为空格，首字母大写
function formatName(fileName) {
  if (fileName.endsWith('.md')) {
    fileName = fileName.replace(/\.md$/, '');
  }
  return fileName
    .replace(/-/g, ' ')
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// 递归扫描目录，生成菜单结构
async function scanDirectory(dirPath, relativePath = '') {
  const items = [];
  const entries = await readdir(dirPath, { withFileTypes: true });

  // 先处理目录，再处理文件，保证目录在前
  const directories = entries.filter(entry => entry.isDirectory());
  const files = entries.filter(entry => entry.isFile() && entry.name.endsWith('.md'));

  // 处理子目录
  for (const dir of directories) {
    const dirName = dir.name;
    const dirPathFull = path.join(dirPath, dirName);
    const relativeDirPath = path.join(relativePath, dirName);
    
    // 获取子目录中的所有项目
    const children = await scanDirectory(dirPathFull, relativeDirPath);
    
    if (children.length > 0) {
      const menuName = formatName(dirName);
      const id = generateId(path.join(relativeDirPath, dirName));
      items.push({
        id,
        name: menuName,
        path: `/docs/${relativeDirPath}/`,
        children,
        expanded: CONFIG.defaultExpanded
      });
    }
  }

  // 处理Markdown文件
  for (const file of files) {
    const fileName = file.name;
    const filePath = path.join(dirPath, fileName);
    const relativeFilePath = path.join(relativePath, fileName);
    
    const menuName = formatName(fileName);
    const id = generateId(path.join(relativePath, fileName));
    
    items.push({
      id,
      name: menuName,
      path: `/docs/${relativeFilePath}`
    });
  }

  return items;
}

// 生成顶层菜单项
async function generateMenuConfig() {
  try {
    const topLevelItems = [];
    
    // 扫描doc目录下的所有一级目录
    const docPath = path.join(process.cwd(), CONFIG.docDir);
    const entries = await readdir(docPath, { withFileTypes: true });
    const directories = entries.filter(entry => entry.isDirectory());
    
    for (const dir of directories) {
      const dirName = dir.name;
      const dirPath = path.join(docPath, dirName);
      
      // 生成唯一的顶层ID
      const id = generateId(dirName);
      const menuName = formatName(dirName);
      const icon = CONFIG.defaultIcons[menuName] || '📄';
      
      // 扫描子目录
      const children = await scanDirectory(dirPath, dirName);
      
      if (children.length > 0) {
        topLevelItems.push({
          id,
          name: menuName,
          icon,
          expanded: CONFIG.defaultExpanded,
          children
        });
      }
    }
    
    // 生成JavaScript配置文件内容
    const configContent = `// 此文件由 generateMenuConfig.js 自动生成
// 请不要手动修改，如需修改请调整生成脚本

export default ${JSON.stringify(topLevelItems, null, 2)};`;

    // 写入文件
    fs.writeFileSync(CONFIG.outputPath, configContent);
    console.log(`✅ 菜单配置文件已成功生成到 ${CONFIG.outputPath}`);
    console.log(`📊 共生成 ${topLevelItems.length} 个顶层菜单项`);
    
    // 显示生成的结构预览
    console.log('\n📋 生成的菜单结构预览:');
    topLevelItems.forEach(item => {
      console.log(`- ${item.name} (${item.children.length} 个子项)`);
    });
    
  } catch (error) {
    console.error('❌ 生成菜单配置文件时出错:', error);
    process.exit(1);
  }
}

// 执行生成
generateMenuConfig();