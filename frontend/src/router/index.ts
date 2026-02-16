import { createRouter, createWebHistory } from 'vue-router'
import { setupLayouts } from 'virtual:generated-layouts'
import routes from 'virtual:generated-pages'
import { useAuthStore } from '@/store/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: setupLayouts(routes),
})

let isInitialized = false

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  
  // Initialization: attempt silent refresh once
  if (!isInitialized) {
    await authStore.init()
    isInitialized = true
  }
  
  console.log('Router Guide - To:', to.path, 'IsAuthenticated:', authStore.isAuthenticated);
  
  // Public pages that don't require auth
  const publicPages = ['/login']
  const authRequired = !publicPages.includes(to.path)
  
  if (authRequired && !authStore.isAuthenticated) {
    console.log('Auth required but not authenticated, redirecting to /login');
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    console.log('Already authenticated, redirecting from /login to /');
    next('/')
  } else {
    next()
  }
})

export default router
