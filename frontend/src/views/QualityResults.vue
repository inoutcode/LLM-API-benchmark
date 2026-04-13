<template>
  <div class="quality-results">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型质量测试结果</span>
          <el-button @click="loadResults">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="任务">
          <el-select v-model="filters.task_id" placeholder="全部任务" clearable style="width: 300px">
            <el-option
              v-for="task in tasks"
              :key="task.id"
              :label="task.name"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadResults">查询</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 结果表格 -->
      <el-table :data="results" style="width: 100%" border stripe>
        <el-table-column prop="execution_time" label="执行时间" min-width="140">
          <template #default="{ row }">
            {{ formatDate(row.execution_time) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="overall_rating" label="总体评级" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getRatingType(row.overall_rating)">
              {{ row.overall_rating || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="1.基础设施侦察" min-width="180">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.infrastructure_recon">{{ row.infrastructure_recon }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="2.模型列表枚举" min-width="180">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.models_enumerated">{{ row.models_enumerated }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="3.Token注入检测" min-width="180">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.token_injection">{{ row.token_injection }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="4.Prompt提取" min-width="180">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.prompt_extraction">{{ row.prompt_extraction }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="5.指令冲突+身份替换" min-width="200">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.instruction_override">{{ row.instruction_override }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="6.越狱测试" min-width="180">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.jailbreak_test">{{ row.jailbreak_test }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="7.上下文长度扫描" min-width="200">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.context_boundary">{{ row.context_boundary }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="8.工具调用改写" min-width="180">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.tool_call_substitution">{{ row.tool_call_substitution }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="9.错误响应泄漏" min-width="180">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.error_response_leakage">{{ row.error_response_leakage }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="10.流完整性" min-width="180">
          <template #default="{ row }">
            <div class="risk-item" v-if="row.stream_integrity">{{ row.stream_integrity }}</div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" min-width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewReport(row)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 报告查看对话框 -->
    <el-dialog v-model="reportDialogVisible" title="测试报告" width="80%">
      <div v-if="reportContent" class="report-content">
        <pre>{{ reportContent }}</pre>
      </div>
      <el-empty v-else description="无法加载报告内容" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { resultAPI, taskAPI } from '@/utils/api'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

const tasks = ref([])
const results = ref([])

const filters = reactive({
  task_id: null,
  dateRange: null
})

const reportDialogVisible = ref(false)
const reportContent = ref('')

const loadTasks = async () => {
  try {
    const res = await taskAPI.getTasks({ type: 'quality_test' })
    tasks.value = res.tasks
  } catch (error) {
    console.error('Failed to load tasks:', error)
  }
}

const loadResults = async () => {
  try {
    const params = {}
    
    if (filters.task_id) {
      params.task_id = filters.task_id
    }
    
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_time = dayjs(filters.dateRange[0]).toISOString()
      params.end_time = dayjs(filters.dateRange[1]).toISOString()
    }
    
    const res = await resultAPI.getQualityResults(params)
    results.value = res.results
  } catch (error) {
    console.error('Failed to load results:', error)
  }
}

const viewReport = async (row) => {
  try {
    const res = await resultAPI.getQualityResultRaw(row.id)
    reportContent.value = res.content
    reportDialogVisible.value = true
  } catch (error) {
    console.error('Failed to load report:', error)
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

const getTagType = (value) => {
  if (!value) return 'info'
  if (value.includes('clean') || value.includes('passed') || value.includes('failed')) {
    return 'success'
  }
  if (value.includes('HIGH')) {
    return 'danger'
  }
  if (value.includes('leaks')) {
    return 'warning'
  }
  return 'info'
}

const getRatingType = (rating) => {
  if (!rating) return 'info'
  if (rating.includes('HIGH')) return 'danger'
  if (rating.includes('MEDIUM')) return 'warning'
  if (rating.includes('LOW')) return 'success'
  return 'info'
}

onMounted(() => {
  loadTasks()
  loadResults()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form {
  margin-bottom: 20px;
}

.risk-summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.risk-item {
  word-break: break-word;
  line-height: 1.5;
}

.report-content {
  background-color: #f5f5f5;
  padding: 20px;
  border-radius: 4px;
  overflow: auto;
  max-height: 600px;
}

.report-content pre {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}
</style>