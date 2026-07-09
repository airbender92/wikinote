import './style.less'

// rem 自适应逻辑
function initRem() {
  const cw = document.documentElement.clientWidth
  const fontSize = (cw / 375) * 100
  document.documentElement.style.fontSize = fontSize + 'px'
}

initRem()
window.addEventListener('resize', initRem)