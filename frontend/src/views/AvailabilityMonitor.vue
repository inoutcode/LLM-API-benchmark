<template>
  <div class="availability-monitor">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>服务可用性监控</span>
          <el-button @click="loadResults">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="模型">
          <el-select v-model="filters.model" placeholder="全部模型" clearable style="width: 200px">
            <el-option
              v-for="model in models"
              :key="model"
              :label="model"
              :value="model"
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

      <!-- 图表区域 -->
      <div v-if="chartData.labels.length > 0" class="charts-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span>平均延迟对比</span>
              </template>
              <div ref="avgLatencyChart" style="height: 350px"></div>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span>P99延迟对比</span>
              </template>
              <div ref="p99LatencyChart" style="height: 350px"></div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span>平均TTFT对比</span>
              </template>
              <div ref="avgTTFTChart" style="height: 350px"></div>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span>RPS对比</span>
              </template>
              <div ref="rpsChart" style="height: 350px"></div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span>生成速度对比</span>
              </template>
              <div ref="genToksChart" style="height: 350px"></div>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span>成功率对比</span>
              </template>
              <div ref="successRateChart" style="height: 350px"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <el-empty v-else description="暂无数据" />

      <!-- 结果列表 -->
      <el-divider content-position="left">
        <el-icon><Document /></el-icon>
        执行历史
      </el-divider>

      <el-table :data="results" style="width: 100%">
        <el-table-column prop="execution_time" label="执行时间" min-width="160">
          <template #default="{ row }">
            {{ formatDate(row.execution_time) }}
          </template>
        </el-table-column>

        <el-table-column prop="model_name" label="模型名称" min-width="150" />

        <el-table-column prop="channel_name" label="渠道" min-width="120" />

        <el-table-column prop="concurrency" label="并发数" width="90" />

        <el-table-column prop="avg_latency" label="平均延迟" width="100">
          <template #default="{ row }">
            {{ row.avg_latency?.toFixed(2) }}s
          </template>
        </el-table-column>

        <el-table-column prop="p99_latency" label="P99延迟" width="100">
          <template #default="{ row }">
            {{ row.p99_latency?.toFixed(2) }}s
          </template>
        </el-table-column>

        <el-table-column prop="avg_ttft" label="平均TTFT" width="100">
          <template #default="{ row }">
            {{ row.avg_ttft?.toFixed(2) }}s
          </template>
        </el-table-column>

        <el-table-column prop="rps" label="RPS" width="100">
          <template #default="{ row }">
            {{ row.rps?.toFixed(2) }}
          </template>
        </el-table-column>

        <el-table-column prop="gen_toks" label="生成速度" width="100">
          <template #default="{ row }">
            {{ row.gen_toks?.toFixed(2) }}
          </template>
        </el-table-column>

        <el-table-column prop="success_rate" label="成功率" width="100">
          <template #default="{ row }">
            <el-tag :type="row.success_rate >= 95 ? 'success' : 'danger'">
              {{ row.success_rate?.toFixed(1) }}%
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { resultAPI } from '@/utils/api'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import * as echarts from 'echarts'
import { Refresh, Document } from '@element-plus/icons-vue'

dayjs.extend(utc)
dayjs.extend(timezone)

const models = ref([])
const results = ref([])
const chartData = ref({
  labels: [],
  datasets: {}
})

const filters = reactive({
  model: '',
  dateRange: [
    dayjs().subtract(1, 'day').toDate(),
    dayjs().toDate()
  ]
})

const avgLatencyChart = ref(null)
const p99LatencyChart = ref(null)
const avgTTFTChart = ref(null)
const rpsChart = ref(null)
const genToksChart = ref(null)
const successRateChart = ref(null)

let charts = []

const loadModels = async () => {
  try {
    const res = await resultAPI.getAvailabilityModels()
    models.value = res.models
  } catch (error) {
    console.error('Failed to load models:', error)
  }
}

const loadResults = async () => {
  try {
    const params = {}

    if (filters.model) {
      params.model = filters.model
    }

    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_time = dayjs(filters.dateRange[0]).toISOString()
      params.end_time = dayjs(filters.dateRange[1]).toISOString()
    }

    const [resultsRes, chartRes] = await Promise.all([
      resultAPI.getAvailabilityResults(params),
      resultAPI.getAvailabilityChartData(params)
    ])

    results.value = resultsRes.results
    chartData.value = chartRes.chart_data

    await nextTick()
    renderCharts()
  } catch (error) {
    console.error('Failed to load results:', error)
  }
}

const renderCharts = () => {
  charts.forEach(chart => chart.dispose())
  charts = []

  if (chartData.value.labels.length === 0) return

  const colors = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#48b8d0'
  ]

  const channels = Object.keys(chartData.value.datasets)

  const baseOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: channels,
      top: 10,
      type: 'scroll'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: 60,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.value.labels,
      axisLabel: {
        rotate: 45,
        interval: Math.floor(chartData.value.labels.length / 10) || 0
      }
    },
    yAxis: {
      type: 'value'
    }
  }

  // 平均延迟图表
  if (avgLatencyChart.value) {
    const chart = echarts.init(avgLatencyChart.value)
    const series = channels.map((channel, index) => ({
      name: channel,
      type: 'line',
      data: chartData.value.datasets[channel].avg_latency,
      smooth: true,
      itemStyle: { color: colors[index % colors.length] }
    }))
    chart.setOption({
      ...baseOption,
      yAxis: { ...baseOption.yAxis, name: '延迟(s)' },
      series
    })
    charts.push(chart)
  }

  // P99延迟图表
  if (p99LatencyChart.value) {
    const chart = echarts.init(p99LatencyChart.value)
    const series = channels.map((channel, index) => ({
      name: channel,
      type: 'line',
      data: chartData.value.datasets[channel].p99_latency,
      smooth: true,
      itemStyle: { color: colors[index % colors.length] }
    }))
    chart.setOption({
      ...baseOption,
      yAxis: { ...baseOption.yAxis, name: '延迟(s)' },
      series
    })
    charts.push(chart)
  }

  // TTFT图表
  if (avgTTFTChart.value) {
    const chart = echarts.init(avgTTFTChart.value)
    const series = channels.map((channel, index) => ({
      name: channel,
      type: 'line',
      data: chartData.value.datasets[channel].avg_ttft,
      smooth: true,
      itemStyle: { color: colors[index % colors.length] }
    }))
    chart.setOption({
      ...baseOption,
      yAxis: { ...baseOption.yAxis, name: 'TTFT(s)' },
      series
    })
    charts.push(chart)
  }

  // RPS图表
  if (rpsChart.value) {
    const chart = echarts.init(rpsChart.value)
    const series = channels.map((channel, index) => ({
      name: channel,
      type: 'line',
      data: chartData.value.datasets[channel].rps,
      smooth: true,
      itemStyle: { color: colors[index % colors.length] }
    }))
    chart.setOption({
      ...baseOption,
      yAxis: { ...baseOption.yAxis, name: 'RPS' },
      series
    })
    charts.push(chart)
  }

  // 生成速度图表
  if (genToksChart.value) {
    const chart = echarts.init(genToksChart.value)
    const series = channels.map((channel, index) => ({
      name: channel,
      type: 'line',
      data: chartData.value.datasets[channel].gen_toks,
      smooth: true,
      itemStyle: { color: colors[index % colors.length] }
    }))
    chart.setOption({
      ...baseOption,
      yAxis: { ...baseOption.yAxis, name: '生成速度(tokens/s)' },
      series
    })
    charts.push(chart)
  }

  // 成功率图表
  if (successRateChart.value) {
    const chart = echarts.init(successRateChart.value)
    const series = channels.map((channel, index) => ({
      name: channel,
      type: 'line',
      data: chartData.value.datasets[channel].success_rate,
      smooth: true,
      itemStyle: { color: colors[index % colors.length] }
    }))
    chart.setOption({
      ...baseOption,
      yAxis: { ...baseOption.yAxis, name: '成功率(%)', min: 0, max: 100 },
      series
    })
    charts.push(chart)
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  let normalizedDate = date
  if (!date.includes('T')) {
    normalizedDate = date.replace(' ', 'T')
  }
  return dayjs(normalizedDate).format('YYYY-MM-DD HH:mm')
}

onMounted(async () => {
  await loadModels()
  loadResults()
})

window.addEventListener('resize', () => {
  charts.forEach(chart => chart.resize())
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

.charts-section {
  margin-bottom: 20px;
}
</style>
