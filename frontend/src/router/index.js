import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Layout from '@/views/Layout.vue'
import Dashboard from '@/views/Dashboard.vue'
import Tasks from '@/views/Tasks.vue'
import PerfResults from '@/views/PerfResults.vue'
import QualityResults from '@/views/QualityResults.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: Tasks
      },
      {
        path: 'perf-results',
        name: 'PerfResults',
        component: PerfResults
      },
      {
        path: 'quality-results',
        name: 'QualityResults',
        component: QualityResults
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router