<template>
  <div class="tasks">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </template>
      
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="name" label="任务名称" min-width="200" />
        
        <el-table-column prop="task_type" label="任务类型" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.task_type === 'perf_test' ? 'success' : 'warning'">
              {{ row.task_type === 'perf_test' ? '压力测试' : '质量测试' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="schedule_type" label="调度类型" min-width="120">
          <template #default="{ row }">
            {{ getScheduleLabel(row.schedule_type) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="is_enabled" label="状态" min-width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_enabled"
              @change="handleEnableChange(row)"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="执行状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="last_run_time" label="最后执行" min-width="160">
          <template #default="{ row }">
            {{ row.last_run_time ? formatDate(row.last_run_time) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="next_run_time" label="下次执行" min-width="160">
          <template #default="{ row }">
            {{ row.next_run_time ? formatDate(row.next_run_time) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" min-width="320">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleRun(row)"
              :disabled="row.status === 'running'"
            >
              执行
            </el-button>
            <el-button
              size="small"
              type="warning"
              @click="handleStop(row)"
              :disabled="row.status !== 'running'"
            >
              停止
            </el-button>
            <el-button
              size="small"
              type="info"
              @click="viewLiveLog(row)"
              :disabled="row.status !== 'running'"
            >
              查看日志
            </el-button>
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建/编辑任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑任务' : '新建任务'"
      width="600px"
    >
      <el-form :model="taskForm" :rules="rules" ref="taskFormRef" label-width="120px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="任务类型" prop="task_type">
          <el-radio-group v-model="taskForm.task_type" :disabled="isEdit">
            <el-radio label="perf_test">服务压力测试</el-radio>
            <el-radio label="quality_test">模型质量测试</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 压力测试配置 -->
        <template v-if="taskForm.task_type === 'perf_test'">
          <el-form-item label="API URL" prop="config.url">
            <el-input v-model="taskForm.config.url" placeholder="https://api.example.com" />
          </el-form-item>
          
          <el-form-item label="API Key" prop="config.api_key">
            <el-input v-model="taskForm.config.api_key" type="password" placeholder="sk-xxxx" />
          </el-form-item>
          
          <el-form-item label="模型名称" prop="config.model">
            <el-input v-model="taskForm.config.model" placeholder="gpt-3.5-turbo" />
          </el-form-item>
          
          <el-form-item label="并发数">
            <el-input-number v-model="taskForm.config.parallel" :min="1" :max="1000" />
          </el-form-item>
          
          <el-form-item label="请求数">
            <el-input-number v-model="taskForm.config.number" :min="1" :max="1000" />
          </el-form-item>
          
          <el-divider>高级配置</el-divider>
          
          <el-form-item label="最小提示长度">
            <el-input-number v-model="taskForm.config.min_prompt_length" :min="1" :max="1000" />
          </el-form-item>
          
          <el-form-item label="最大提示长度">
            <el-input-number v-model="taskForm.config.max_prompt_length" :min="1" :max="10000" />
          </el-form-item>
          
          <el-form-item label="最小生成Token数">
            <el-input-number v-model="taskForm.config.min_tokens" :min="1" :max="10000" />
          </el-form-item>
          
          <el-form-item label="最大生成Token数">
            <el-input-number v-model="taskForm.config.max_tokens" :min="1" :max="10000" />
          </el-form-item>
          
          <el-form-item label="连接超时(秒)">
            <el-input-number v-model="taskForm.config.connect_timeout" :min="1" :max="600" />
          </el-form-item>
          
          <el-form-item label="读取超时(秒)">
            <el-input-number v-model="taskForm.config.read_timeout" :min="1" :max="600" />
          </el-form-item>
        </template>
        
        <!-- 质量测试配置 -->
        <template v-if="taskForm.task_type === 'quality_test'">
          <el-form-item label="API URL" prop="config.url">
            <el-input v-model="taskForm.config.url" placeholder="https://relay.example.com/v1" />
          </el-form-item>
          
          <el-form-item label="API Key" prop="config.api_key">
            <el-input v-model="taskForm.config.api_key" type="password" placeholder="sk-xxxx" />
          </el-form-item>
          
          <el-form-item label="Audit 路径">
            <el-input v-model="taskForm.config.audit_path" placeholder="audit.py 所在目录" />
          </el-form-item>
        </template>
        
        <el-divider>调度设置</el-divider>
        
        <el-form-item label="调度类型">
          <el-radio-group v-model="taskForm.schedule_type">
            <el-radio label="manual">手动执行</el-radio>
            <el-radio label="cron">Cron 表达式</el-radio>
            <el-radio label="interval">固定间隔</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="taskForm.schedule_type === 'cron'" label="Cron 表达式">
          <el-input v-model="taskForm.cron_expression" placeholder="0 */30 * * * *" />
          <div class="form-tip">格式：秒 分 时 日 月 周</div>
        </el-form-item>
        
        <el-form-item v-if="taskForm.schedule_type === 'interval'" label="间隔时间">
          <el-input-number v-model="taskForm.interval_seconds" :min="60" :step="60" />
          <span style="margin-left: 10px">秒</span>
        </el-form-item>
        
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="taskForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
          />
        </el-form-item>
        
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="taskForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
          />
        </el-form-item>
        
        <el-form-item label="立即启用">
          <el-switch v-model="taskForm.is_enabled" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 实时日志查看对话框 -->
    <el-dialog
      v-model="logDialogVisible"
      title="实时执行日志"
      width="80%"
      :close-on-click-modal="false"
      @close="closeLogDialog"
    >
      <div class="log-header">
        <span>任务: {{ currentLogTask?.name }}</span>
        <el-switch v-model="autoScroll" active-text="自动滚动" />
      </div>
      <pre ref="logContentRef" class="log-content">{{ logContent }}</pre>
      <template #footer>
        <el-button @click="refreshLog">手动刷新</el-button>
        <el-button type="primary" @click="logDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskAPI } from '@/utils/api'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

const tasks = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const taskFormRef = ref(null)
const editingTaskId = ref(null)

// 实时日志相关
const logDialogVisible = ref(false)
const logContent = ref('')
const logContentRef = ref(null)
const currentLogTask = ref(null)
const autoScroll = ref(true)
let logRefreshTimer = null

const taskForm = reactive({
  name: '',
  task_type: 'perf_test',
  config: {
    url: '',
    api_key: '',
    model: '',
    parallel: 8,
    number: 50,
    min_prompt_length: 10,
    max_prompt_length: 20,
    min_tokens: 128,
    max_tokens: 128,
    connect_timeout: 60,
    read_timeout: 120,
    audit_path: ''
  },
  schedule_type: 'manual',
  cron_expression: '',
  interval_seconds: 1800,
  start_time: null,
  end_time: null,
  is_enabled: false
})

const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  task_type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  'config.url': [{ required: true, message: '请输入 API URL', trigger: 'blur' }],
  'config.api_key': [{ required: true, message: '请输入 API Key', trigger: 'blur' }]
}

const loadTasks = async () => {
  try {
    const res = await taskAPI.getTasks()
    tasks.value = res.tasks
  } catch (error) {
    console.error('Failed to load tasks:', error)
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingTaskId.value = row.id
  
  const parsedConfig = JSON.parse(row.config)
  
  Object.assign(taskForm, {
    name: row.name,
    task_type: row.task_type,
    config: {
      // 默认值
      url: '',
      api_key: '',
      model: '',
      parallel: 8,
      number: 50,
      min_prompt_length: 10,
      max_prompt_length: 20,
      min_tokens: 128,
      max_tokens: 128,
      connect_timeout: 60,
      read_timeout: 120,
      audit_path: '',
      // 覆盖为实际值
      ...parsedConfig
    },
    schedule_type: row.schedule_type,
    cron_expression: row.cron_expression || '',
    interval_seconds: row.interval_seconds || 1800,
    start_time: row.start_time ? new Date(row.start_time) : null,
    end_time: row.end_time ? new Date(row.end_time) : null,
    is_enabled: row.is_enabled
  })
  
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!taskFormRef.value) return
  
  await taskFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const data = {
          name: taskForm.name,
          task_type: taskForm.task_type,
          config: JSON.stringify(taskForm.config),
          schedule_type: taskForm.schedule_type,
          cron_expression: taskForm.cron_expression,
          interval_seconds: taskForm.interval_seconds,
          start_time: taskForm.start_time ? dayjs(taskForm.start_time).toISOString() : null,
          end_time: taskForm.end_time ? dayjs(taskForm.end_time).toISOString() : null,
          is_enabled: taskForm.is_enabled
        }
        
        if (isEdit.value) {
          await taskAPI.updateTask(editingTaskId.value, data)
          ElMessage.success('任务更新成功')
        } else {
          await taskAPI.createTask(data)
          ElMessage.success('任务创建成功')
        }
        
        dialogVisible.value = false
        loadTasks()
      } catch (error) {
        console.error('Failed to save task:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await taskAPI.deleteTask(row.id)
    ElMessage.success('任务删除成功')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete task:', error)
    }
  }
}

const handleRun = async (row) => {
  try {
    await taskAPI.runTask(row.id)
    ElMessage.success('任务已开始执行')
    loadTasks()
  } catch (error) {
    console.error('Failed to run task:', error)
  }
}

const handleStop = async (row) => {
  try {
    await taskAPI.stopTask(row.id)
    ElMessage.success('任务已停止')
    loadTasks()
  } catch (error) {
    console.error('Failed to stop task:', error)
  }
}

// 实时日志查看
const viewLiveLog = async (row) => {
  currentLogTask.value = row
  logContent.value = ''
  logDialogVisible.value = true
  
  // 立即加载一次
  await refreshLog()
  
  // 启动定时刷新（每 2 秒）
  logRefreshTimer = setInterval(async () => {
    await refreshLog()
  }, 2000)
}

const refreshLog = async () => {
  if (!currentLogTask.value) return
  
  try {
    const response = await fetch(`/api/tasks/${currentLogTask.value.id}/output-content`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await response.json()
    
    if (data.exists) {
      logContent.value = data.content
      
      // 自动滚动到底部
      if (autoScroll.value && logContentRef.value) {
        await nextTick()
        logContentRef.value.scrollTop = logContentRef.value.scrollHeight
      }
    }
    
    // 如果任务不再是 running 状态，停止刷新
    if (currentLogTask.value) {
      await loadTasks()
      const updatedTask = tasks.value.find(t => t.id === currentLogTask.value.id)
      if (updatedTask && updatedTask.status !== 'running') {
        closeLogDialog()
        ElMessage.info('任务执行完成')
      }
    }
  } catch (error) {
    console.error('Failed to refresh log:', error)
  }
}

const closeLogDialog = () => {
  if (logRefreshTimer) {
    clearInterval(logRefreshTimer)
    logRefreshTimer = null
  }
  logDialogVisible.value = false
  currentLogTask.value = null
}

const handleEnableChange = async (row) => {
  try {
    await taskAPI.updateTask(row.id, { is_enabled: row.is_enabled })
    ElMessage.success(row.is_enabled ? '任务已启用' : '任务已禁用')
  } catch (error) {
    row.is_enabled = !row.is_enabled
    console.error('Failed to update task:', error)
  }
}

const resetForm = () => {
  Object.assign(taskForm, {
    name: '',
    task_type: 'perf_test',
    config: {
      url: '',
      api_key: '',
      model: '',
      parallel: 8,
      number: 50,
      min_prompt_length: 10,
      max_prompt_length: 20,
      min_tokens: 128,
      max_tokens: 128,
      connect_timeout: 60,
      read_timeout: 120,
      audit_path: ''
    },
    schedule_type: 'manual',
    cron_expression: '',
    interval_seconds: 1800,
    start_time: null,
    end_time: null,
    is_enabled: false
  })
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

const getScheduleLabel = (type) => {
  const labels = {
    manual: '手动执行',
    cron: 'Cron',
    interval: '固定间隔'
  }
  return labels[type] || type
}

const getStatusLabel = (status) => {
  const labels = {
    idle: '空闲',
    running: '运行中',
    success: '成功',
    failed: '失败'
  }
  return labels[status] || status
}

const getStatusType = (status) => {
  const types = {
    idle: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.log-content {
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 4px;
  overflow: auto;
  max-height: 500px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>