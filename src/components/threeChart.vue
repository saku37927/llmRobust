<template>
  <div class="layout-container">
    <!-- 左侧面板 - 桑基图 -->
    <div class="left-panel">
      <div class="sankey-section">
        <!-- 特征分布图容器 -->
        <div ref="chart" class="chart-area">
          <div class="feature-container" data-container="prompt">
            <div class="scroll-container" ref="scrollContainer1">
              <div class="feature-charts">
                <!-- 连续特征图表 -->
                <div v-for="(featureData, featureName) in distributionData?.continuous" 
                     :key="'continuous-'+featureName" 
                     class="feature-chart">
                  <h3>{{ featureName }} (连续)</h3>
                  <svg :width="chartWidth" :height="chartHeight">
                    <!-- 这里放置SVG图表内容 -->
                  </svg>
                </div>
                
                <!-- 离散特征图表 -->
                <div v-for="(featureData, featureName) in distributionData?.discrete" 
                     :key="'discrete-'+featureName" 
                     class="feature-chart">
                  <h3>{{ featureName }} (离散)</h3>
                  <svg :width="chartWidth" :height="chartHeight">
                    <!-- 这里放置SVG图表内容 -->
                  </svg>
                </div>
              </div>
            </div>
            <!-- 滑块控制 -->
            <input type="range" class="feature-slider" 
                   :min="0" 
                   :max="totalWidth - containerWidth" 
                   v-model="scrollPosition"
                   @input="handleScroll">
          </div>
        </div>
      </div>
      
      <div class="sankey-section">
        <!-- 同上，为第二个图表容器 -->
        <div ref="chart2" class="chart-area">
          <!-- 类似的结构 -->
        </div>
      </div>
    </div>

    <!-- 中间面板 - 数据列表 (保持不变) -->
    <div class="center-panel">
      <!-- ...原有代码... -->
    </div>
  </div>
</template>

<script setup>
import * as d3 from 'd3'
import { ref, onMounted, computed } from 'vue'

// 图表尺寸常量
const chartWidth = 380
const chartHeight = 220
const containerWidth = 800
const containerHeight = 250

// 数据引用
const distributionData = ref(null)
const distributionDataCorpus = ref(null)
const scrollPosition = ref(0)
const totalWidth = computed(() => {
  if (!distributionData.value) return 0
  const continuousCount = Object.keys(distributionData.value.continuous).length
  const discreteCount = Object.keys(distributionData.value.discrete).length
  return (continuousCount + discreteCount) * (chartWidth + 20) + 20
})

// 滚动处理
function handleScroll() {
  const scrollContainer = document.querySelector('.scroll-container')
  if (scrollContainer) {
    scrollContainer.scrollLeft = scrollPosition.value
  }
}

// 创建单个图表
function createChart(svgElement, featureName, featureData, isContinuous) {
  const margin = {top: 20, right: 20, bottom: 40, left: 40}
  const innerWidth = chartWidth - margin.left - margin.right
  const innerHeight = chartHeight - margin.top - margin.bottom

  // 数据处理
  let displayData;
    if (isContinuous) {
      // 连续特征分为10个区间
      const values = featureData.values.map(d => d.value);
      const min = Math.min(...values);
      const max = Math.max(...values);
      const step = (max - min) / 10;
      
      displayData = Array.from({length: 10}, (_, i) => {
        const start = min + i * step;
        const end = start + step;
        const items = featureData.values.filter(d => 
          d.value >= start && d.value < end
        );
        return {
          label: `${start.toFixed(1)}-${end.toFixed(1)}`,
          count: items.length,
          robustness: items.reduce((sum, d) => sum + d.robustness, 0) / (items.length || 1)
        };
      });
    } else {
      // 离散特征直接使用
      displayData = featureData.map(d => ({
        label: d.value_name,
        count: d.count,
        robustness: d.avg_robustness
      }));
    }
    
    // 创建比例尺
    const x = d3.scaleBand()
      .domain(displayData.map(d => d.label))
      .range([margin.left, margin.left + innerWidth])
      .padding(0.1);
    
    const yCount = d3.scaleLinear()
      .domain([0, d3.max(displayData, d => d.count)])
      .range([margin.top + innerHeight, margin.top]);
    
    const yRobustness = d3.scaleLinear()
      .domain([0, 1])
      .range([margin.top + innerHeight, margin.top]);
    
    // 绘制数量条形图
    chart.selectAll(".bar-count")
      .data(displayData)
      .join("rect")
        .attr("class", "bar-count")
        .attr("x", d => x(d.label))
        .attr("y", d => yCount(d.count))
        .attr("width", x.bandwidth())
        .attr("height", d => margin.top + innerHeight - yCount(d.count))
        .attr("fill", "#4e79a7")
        .attr("opacity", 0.7);
    
    // 绘制鲁棒性折线/点
    if (isContinuous) {
      const line = d3.line()
        .x(d => x(d.label) + x.bandwidth()/2)
        .y(d => yRobustness(d.robustness));
      
      chart.append("path")
        .datum(displayData)
        .attr("class", "robustness-line")
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", "#e15759")
        .attr("stroke-width", 1.5);
    } else {
      chart.selectAll(".robustness-dot")
        .data(displayData)
        .join("circle")
          .attr("class", "robustness-dot")
          .attr("cx", d => x(d.label) + x.bandwidth()/2)
          .attr("cy", d => yRobustness(d.robustness))
          .attr("r", 3)
          .attr("fill", "#e15759");
    }
    
    // 添加X轴
    chart.append("g")
      .attr("class", "x-axis")
      .attr("transform", `translate(0,${margin.top + innerHeight})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end")
        .style("font-size", "10px");
    
    // 添加左侧Y轴（数量）
    chart.append("g")
      .attr("class", "y-axis-count")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(yCount).ticks(5))
      .selectAll("text")
        .style("font-size", "10px");
    
    // 添加右侧Y轴（鲁棒性）
    chart.append("g")
      .attr("class", "y-axis-robustness")
      .attr("transform", `translate(${margin.left + innerWidth},0)`)
      .call(d3.axisRight(yRobustness).ticks(5))
      .selectAll("text")
        .style("font-size", "10px");
    
    // 添加图例
    const legend = chart.append("g")
      .attr("class", "legend")
      .attr("transform", `translate(${width - 120},${margin.top})`);
    
    legend.append("rect")
      .attr("width", 10)
      .attr("height", 10)
      .attr("fill", "#4e79a7");
    
    legend.append("text")
      .attr("x", 15)
      .attr("y", 10)
      .text("数量")
      .style("font-size", "10px");
    
    if (isContinuous) {
      legend.append("path")
        .attr("d", "M0,5 L20,5")
        .attr("stroke", "#e15759")
        .attr("stroke-width", 1.5)
        .attr("transform", "translate(0,20)");
    } else {
      legend.append("circle")
        .attr("cx", 5)
        .attr("cy", 20)
        .attr("r", 3)
        .attr("fill", "#e15759");
    }
    
    legend.append("text")
      .attr("x", 15)
      .attr("y", 25)
      .text("鲁棒性")
      .style("font-size", "10px");
}

// 初始化图表
function initCharts() {
  if (distributionData.value) {
    const svgElements = document.querySelectorAll('.feature-chart svg')
    let index = 0
    
    // 处理连续特征
    for (const [featureName, featureData] of Object.entries(distributionData.value.continuous)) {
      createChart(svgElements[index++], featureName, featureData, true)
    }
    
    // 处理离散特征
    for (const [featureName, featureData] of Object.entries(distributionData.value.discrete)) {
      createChart(svgElements[index++], featureName, featureData, false)
    }
  }
}

// 在数据加载后初始化图表
onMounted(async () => {
  await fetchFeatureDistribution()
  initCharts()
})
</script>

<style scoped>
/* 特征图表容器样式 */
.feature-container {
  width: 800px;
  height: 250px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.scroll-container {
  width: 100%;
  height: calc(100% - 30px);
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
}

.feature-charts {
  display: flex;
  height: 100%;
  width: max-content;
}

.feature-chart {
  flex: 0 0 auto;
  width: 380px;
  height: 220px;
  margin-right: 20px;
  padding: 10px;
  background: #f8f8f8;
  border: 1px solid #eee;
}

.feature-chart h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  text-align: center;
}

/* 滑块样式 */
.feature-slider {
  width: calc(100% - 20px);
  margin: 5px 10px;
  height: 8px;
}

/* 滚动条样式 */
.scroll-container::-webkit-scrollbar {
  height: 8px;
}

.scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.scroll-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

/* 其他原有样式保持不变 */
/* ... */
</style>