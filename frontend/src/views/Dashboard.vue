<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background-color: #409EFF">
            <el-icon size="30"><List /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_tasks }}</div>
            <div class="stat-label">总任务数</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background-color: #67C23A">
            <el-icon size="30"><CircleCheck /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.enabled_tasks }}</div>
            <div class="stat-label">启用任务</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background-color: #E6A23C">
            <el-icon size="30"><Loading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.running_tasks }}</div>
            <div class="stat-label">运行中</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background-color: #F56C6C">
            <el-icon size="30"><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_perf_results + stats.total_quality_results }}</div>
            <div class="stat-label">测试结果</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近压力测试结果</span>
          </template>
          <el-table :data="recentPerfResults" style="width: 100%">
            <el-table-column prop="execution_time" label="执行时间" min-width="140">
              <template #default="{ row }">
                {{ formatDate(row.execution_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="task_name" label="任务名称" min-width="150">
              <template #default="{ row }">
                <span 
                  v-if="row.task_name" 
                  class="task-link" 
                  @click="goToPerfResults(row.task_id)"
                >
                  {{ row.task_name }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="avg_latency" label="平均延迟" min-width="100">
              <template #default="{ row }">
                {{ row.avg_latency?.toFixed(2) }}s
              </template>
            </el-table-column>
            <el-table-column prop="rps" label="RPS" min-width="80">
              <template #default="{ row }">
                {{ row.rps?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="success_rate" label="成功率" min-width="80">
              <template #default="{ row }">
                <el-tag :type="row.success_rate >= 95 ? 'success' : 'danger'">
                  {{ row.success_rate?.toFixed(1) }}%
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近质量测试结果</span>
          </template>
          <el-table :data="recentQualityResults" style="width: 100%">
            <el-table-column prop="execution_time" label="执行时间" min-width="140">
              <template #default="{ row }">
                {{ formatDate(row.execution_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="task_name" label="任务名称" min-width="150">
              <template #default="{ row }">
                <span 
                  v-if="row.task_name" 
                  class="task-link" 
                  @click="goToQualityResults(row.task_id)"
                >
                  {{ row.task_name }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="overall_rating" label="总体评级" min-width="120">
              <template #default="{ row }">
                <el-tag :type="getRatingType(row.overall_rating)">
                  {{ row.overall_rating }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { resultAPI } from '@/utils/api'
import { List, CircleCheck, Loading, TrendCharts } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

const router = useRouter()

const stats = ref({
  total_tasks: 0,
  enabled_tasks: 0,
  running_tasks: 0,
  total_perf_results: 0,
  total_quality_results: 0
})

const recentPerfResults = ref([])
const recentQualityResults = ref([])

const loadData = async () => {
  try {
    const [statsRes, perfRes, qualityRes] = await Promise.all([
      resultAPI.getStatistics(),
      resultAPI.getPerfResults({ limit: 5 }),
      resultAPI.getQualityResults({ limit: 5 })
    ])
    
    stats.value = statsRes
    recentPerfResults.value = perfRes.results
    recentQualityResults.value = qualityRes.results
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  // 后端返回的已经是本地时间（北京时间），直接格式化显示
  let normalizedDate = date
  if (!date.includes('T')) {
    normalizedDate = date.replace(' ', 'T')
  }
  return dayjs(normalizedDate).format('YYYY-MM-DD HH:mm')
}

const getRatingType = (rating) => {
  if (rating?.includes('HIGH')) return 'danger'
  if (rating?.includes('MEDIUM')) return 'warning'
  return 'success'
}

const goToPerfResults = (taskId) => {
  router.push({
    path: '/perf-results',
    query: { task_id: taskId }
  })
}

const goToQualityResults = (taskId) => {
  router.push({
    path: '/quality-results',
    query: { task_id: taskId }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 20px;
  flex-shrink: 0;
}

.stat-icon .el-icon {
  font-size: 30px;
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.task-link {
  color: #409EFF;
  cursor: pointer;
  text-decoration: underline;
}

.task-link:hover {
  color: #66b1ff;
}
</style>