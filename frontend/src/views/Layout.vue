<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo">
        <h3>测试管理后台</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        
        <el-menu-item index="/perf-results">
          <el-icon><TrendCharts /></el-icon>
          <span>压力测试结果</span>
        </el-menu-item>
        
        <el-menu-item index="/quality-results">
          <el-icon><Document /></el-icon>
          <span>质量测试结果</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header>
        <div class="header-content">
          <h3>{{ pageTitle }}</h3>
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              <el-icon><User /></el-icon>
              {{ username }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { authAPI } from '@/utils/api'

const router = useRouter()
const route = useRoute()
const username = ref(localStorage.getItem('username') || 'admin')

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/': '仪表盘',
    '/tasks': '任务管理',
    '/perf-results': '压力测试结果',
    '/quality-results': '质量测试结果'
  }
  return titles[route.path] || '模型质量测试管理后台'
})

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      await authAPI.logout()
      localStorage.removeItem('token')
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      if (error !== 'cancel') {
        console.error('Logout failed:', error)
      }
    }
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
}

.logo h3 {
  color: #fff;
  margin: 0;
  font-size: 16px;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #606266;
}

.el-main {
  background-color: #f5f5f5;
  padding: 20px;
}
</style>