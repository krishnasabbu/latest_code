import { RouterProvider } from '@tanstack/react-router'
import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import './i18n'
import reportWebVitals from './reportWebVitals'
import { router } from './router'
import { initData } from './setup/init_data'
import './static/globals.css'
import './static/index.css'
import * as migration from './stores/migration'
import { CHATBOX_BUILD_PLATFORM, CHATBOX_BUILD_TARGET } from './variables'

// ==========执行初始化==============
async function initializeApp() {
  // 按需加载 polyfill
  await import('./setup/load_polyfill')

  // Sentry 初始化
  await import('./setup/sentry_init')

  // GA4 初始化
  await import('./setup/ga_init')

  // 引入保护代码
  await import('./setup/protect')

  // 引入移动端安全区域代码，主要为了解决异形屏幕的问题
  if (CHATBOX_BUILD_TARGET === 'mobile_app' && CHATBOX_BUILD_PLATFORM === 'ios') {
    await import('./setup/mobile_safe_area')
  }

  // 解决移动端浏览器地址栏导致高度计算问题
  await import('./setup/mobile_browser_viewport_height')

  // 初始化数据
  await initData()
  
  // 数据迁移
  await migration.migrate()

  // 最后执行 storage 清理
  await import('./setup/storage_clear')

}

// ==========渲染节点==============
// 等待初始化完成后再渲染
initializeApp().then(() => {
  const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement)
  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  )
})

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals()
