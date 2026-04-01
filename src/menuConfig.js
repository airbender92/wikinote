export default [
  {
    id: 'frontend',
    name: '前端知识',
    icon: '📱',
    expanded: true,
    children: [
      {
        id: 'html',
        name: 'HTML',
        children: [
          {
            id: 'html-basic',
            name: '基础标签',
            path: '/docs/前端知识/HTML/基础标签.md'
          },
          {
            id: 'html-form',
            name: '表单元素',
            path: '/docs/前端知识/HTML/表单元素.md'
          }
        ]
      },
      {
        id: 'css',
        name: 'CSS',
        children: [
          {
            id: 'css-selector',
            name: '选择器',
            path: '/docs/前端知识/CSS/选择器.md'
          }
        ]
      },
      {
        id: 'js',
        name: 'JavaScript',
        children: [
          {
            id: 'js-variable',
            name: '变量类型',
            path: '/docs/前端知识/JavaScript/变量类型.md'
          },
          {
            id: 'js-scope',
            name: '作用域',
            path: '/docs/前端知识/JavaScript/作用域.md'
          }
        ]
      }
    ]
  },
  {
    id: 'backend',
    name: '后端知识',
    icon: '💻',
    expanded: false,
    children: [
      {
        id: 'nodejs',
        name: 'Node.js',
        children: []
      },
      {
        id: 'python',
        name: 'Python',
        children: []
      }
    ]
  },
  {
    id: 'network',
    name: '计算机网络基础',
    icon: '🌐',
    expanded: false,
    children: [
      {
        id: 'network-outline',
        name: '大纲',
        path: '/docs/计算机网络基础/大纲.md'
      },
      {
        id: 'what-is-network',
        name: '什么是计算机网络',
        path: '/docs/计算机网络基础/什么是计算机网络.md'
      },
      {
        id: 'network-function',
        name: '网络的主要功能',
        path: '/docs/计算机网络基础/网络的主要功能.md'
      }
    ]
  }
]