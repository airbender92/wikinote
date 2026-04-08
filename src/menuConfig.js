export default [
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
      },
      {
        id: 'network-classification',
        name: '网络分类',
        path: '/docs/计算机网络基础/网络分类.md'
      },
      {
        id: 'network-performance',
        name: '网络性能指标',
        path: '/docs/计算机网络基础/网络性能指标.md'
      },
      {
        id: 'network-protocol',
        name: '网络体系结构与协议',
        path: '/docs/计算机网络基础/网络体系结构与协议',
        children: [
          {
            id: 'network-protocol-structure',
            name: '协议三要素',
            path: '/docs/计算机网络基础/网络体系结构与协议/协议三要素.md',
          },
          {
            id: 'network-protocol-protocol',
            name: '分层思想的好处',
            path: '/docs/计算机网络基础/网络体系结构与协议/分层思想的好处.md',
          },
          {
            id: 'network-protocol-osi',
            name: 'OSI七层模型',
            path: '/docs/计算机网络基础/网络体系结构与协议/OSI 七层模型.md',
          },
          {
            id: 'network-protocol-tcp-ip',
            name: 'TCP/IP四层模型',
            path: './TCP&IP 四层模型.md',
          },
          {
            id: 'data-structure-transport',
            name: '数据封装与解封装',
            path: './数据封装与解封装.md',
          },
        ]
      },
      {
        id: 'network-protocol-physical',
        name: '物理层',
        path: '/docs/计算机网络基础/物理层',
        children: [
          {
            id: 'network-protocol-physical-role',
            name: '作用',
            path: './作用.md',
          },
          {
            id: 'transport-mediums',
            name: '传输介质',
            path: './传输介质.md',
          },
          {
            id: 'communication-method',
            name: '通信方式',
            path: './通信方式.md',
          },
          {
            id: 'data-transfer-method',
            name: '数据传输方式',
            path: './数据传输方式.md',
          },
          {
            id: 'channel-multiplexing-technology',
            name: '信道复用技术',
            path: './信道复用技术.md',
          },
        ]
      },
      {
        id: 'network-protocol-link',
        name: '数据链路层',
        path: '/docs/计算机网络基础/数据链路层',
        children: [
          {
            id: 'network-protocol-link-role',
            name: '作用',
            path: './作用.md',
          },
          {
            id: 'frame-method',
            name: '成帧方法',
            path: './成帧方法.md',
          },
          {
            id: 'error-control-method',
            name: '差错控制',
            path: './差错控制.md',
          },
          {
            id: 'flow-control-method',
            name: '流量控制',
            path: './流量控制.md',
          },
          {
            id: 'local-area-network',
            name: '局域网技术',
            path: './局域网技术.md',
          },
          {
            id: 'network-device',
            name: '设备',
            path: './设备.md',
          },
        ]
      },
      {
        id: 'network-protocol-network',
        name: '网络层',
        path: '/docs/计算机网络基础/网络层',
        children: [
          {
            id: 'network-protocol-network-role',
            name: '作用',
            path: './作用.md',
          },
          {
            id: 'ip-protocol',
            name: 'IP协议',
            path: './IP 协议.md',
          },
          {
            id: 'subnetting',
            name: '子网划分与超网',
            path: './子网划分与超网.md',
          },
          {
            id: 'arp-rarp',
            name: 'ARP 与 RARP',
            path: './ARP 与 RARP.md',
          },
          {
            id: 'icmp-protocol',
            name: 'ICMP 互联网控制报文协议',
            path: './ICMP互联网控制报文协议.md',
          },
          {
            id: 'routing-protocol',
            name: '路由协议',
            path: './路由协议.md',
          },
          {
            id: 'network-device',
            name: '设备',
            path: './设备.md',
          },
        ]
      },
      {
        id: 'network-protocol-transport',
        name: '传输层',
        path: '/docs/计算机网络基础/传输层',
        children: [
          {
            id: 'network-protocol-transport-role',
            name: '作用',
            path: './作用.md',
          },
          {
            id: 'port-number',
            name: '端口号',
            path: './端口号.md',
          },
          {
            id: 'udp-protocol',
            name: 'UDP 协议',
            path: './UDP协议.md',
          },
          {
            id: 'tcp-protocol',
            name: 'TCP 协议',
            path: './TCP协议.md',
          },
          {
            id: 'tcp-three-way-handshake',
            name: 'TCP 三次握手',
            path: './TCP三次握手.md',
          },
          {
            id: 'tcp-four-way-way',
            name: 'TCP 四次挥手',
            path: './TCP四次挥手.md',
          },
          {
            id: 'tcp-reliability-protocol-management',
            name: 'TCP 可靠传输机制',
            path: './TCP可靠传输机制.md',
          },
        ]
      },
      {
        id: 'network-protocol-application',
        name: '应用层',
        path: '/docs/计算机网络基础/应用层',
        children: [
          {
            id: 'application-layer-protocol',
            name: '应用层协议',
            path: './常见应用层协议.md',
          },
          {
            id: 'http-protocol-focus',
            name: 'HTTP 协议重点',
            path: './HTTP协议重点.md',
          },
          {
            id: 'https-protocol-focus',
            name: 'HTTPS 协议重点',
            path: './HTTPS协议重点.md',
          },
          {
            id: 'dns-protocol-focus',
            name: 'DNS 解析过程',
            path: './DNS解析过程.md',
          },
        ]
      }
    ]
  },
  {
    id: 'data-structure',
    name: '数据结构与算法',
    icon: '📚',
    expanded: false,
    children: [
      {
        id: 'data-structure-outline',
        name: '大纲',
        path: '/docs/数据结构与算法/大纲.md'
      }
    ]
  },
  {
    id: 'os',
    name: '操作系统基础',
    icon: '🚀',
    expanded: false,
    children: [
      {
        id: 'os-outline',
        name: '大纲',
        path: '/docs/操作系统基础/大纲.md'
      }
    ]
  },
  {
    id: 'java',
    name: 'Java核心语法',
    icon: 'Java',
    expanded: false,
    children: [
      {
        id: 'java-outline',
        name: '大纲',
        path: '/docs/Java核心语法/大纲.md'
      }
    ]
  },
  {
    id: 'java-web',
    name: 'Java Web开发',
    icon: 'Java',
    expanded: false,
    children: [
      {
        id: 'java-web-outline',
        name: '大纲',
        path: '/docs/Java Web开发入门/大纲.md'
      }
    ]
  },
  {
    id: 'spring-boot',
    name: 'Spring Boot',
    icon: 'Java',
    expanded: false,
    children: [
      {
        id: 'spring-boot-outline',
        name: '大纲',
        path: '/docs/Spring Boot/大纲.md'
      }
    ]
  },
  {
    id: 'sql',
    name: 'SQL数据库',
    icon: 'SQL',
    expanded: false,
    children: [
      {
        id: 'sql-outline',
        name: '大纲',
        path: '/docs/SQL与关系型数据库/大纲.md'
      }
    ]
  },
  {
    id: 'nosql',
    name: 'NoSQL数据库',
    icon: 'SQL',
    expanded: false,
    children: [
      {
        id: 'nosql-outline',
        name: '大纲',
        path: '/docs/NoSQL入门/大纲.md'
      }
    ]
  },
  {
    id: 'restful',
    name: 'RESTful API设计',
    icon: 'API',
    expanded: false,
    children: [
      {
        id: 'restful-outline',
        name: '大纲',
        path: '/docs/RESTful API设计/大纲.md'
      }
    ]
  },
]