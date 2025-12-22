<template>
  <div class="layout-container">
    <!-- 左侧面板 - 桑基图 -->
    <div class="left-panel">
      <div class="sankey-section">
        <div class="feature-container" data-container="prompt">
          <div class="scroll-container" ref="scrollContainer1">
            <div class="feature-charts">
              <!-- 连续特征图表 -->
              <div v-for="(featureData, featureName) in distributionData?.continuous" 
                   :key="'continuous-'+featureName" 
                   class="feature-chart"
                   ref="continuousCharts">
                <h3>{{ featureName }} (连续)</h3>
                <svg :width="chartWidth" :height="chartHeight" ref="continuousSvgs"></svg>
              </div>
              
              <!-- 离散特征图表 -->
              <div v-for="(featureData, featureName) in distributionData?.discrete" 
                   :key="'discrete-'+featureName" 
                   class="feature-chart"
                   ref="discreteCharts">
                <h3>{{ featureName }} (离散)</h3>
                <svg :width="chartWidth" :height="chartHeight" ref="discreteSvgs"></svg>
              </div>
            </div>
          </div>

        </div>
      </div>
      
      <div class="sankey-section">
        <div class="feature-container" data-container="corpus">
          <div class="scroll-container" ref="scrollContainer2">
            <div class="feature-charts">
              <!-- 连续特征图表 -->
              <div v-for="(featureData, featureName) in distributionDataCorpus?.continuous" 
                   :key="'continuous-'+featureName" 
                   class="feature-chart"
                   ref="continuousCharts2">
                <h3>{{ featureName }} (连续)</h3>
                <svg :width="chartWidth" :height="chartHeight" ref="continuousSvgs2"></svg>
              </div>
              
              <!-- 离散特征图表 -->
              <div v-for="(featureData, featureName) in distributionDataCorpus?.discrete" 
                   :key="'discrete-'+featureName" 
                   class="feature-chart"
                   ref="discreteCharts2">
                <h3>{{ featureName }} (离散)</h3>
                <svg :width="chartWidth" :height="chartHeight" ref="discreteSvgs2"></svg>
              </div>
            </div>
          </div>

        </div>
      </div>
      <div class="sankey-section">
        <div class="feature-control" style="height: 400px;">
          <!-- Prompt特征选择 -->
          <div class="data-source-section">
            <div class="section-header">
              <h3>Prompt特征条件</h3>
              <button 
                @click="clearFeatures('prompt')" 
                class="clear-btn"
                :disabled="!selectedFeatures.prompt.length">
                清空Prompt
              </button>
            </div>
            <div v-if="selectedFeatures.prompt.length === 0" class="empty-state">
              <p>点击Prompt图表中的条形以添加筛选条件</p>
            </div>
            <div v-else class="tags-container">
              <div v-for="(feature, index) in selectedFeatures.prompt" 
                  :key="'prompt-'+index" 
                  class="feature-tag">
                <span class="tag-content">
                  <span class="feature-name">{{ feature.featureName }}</span>
                  <span class="value-range">{{ feature.valueRange }}</span>
                  <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                </span>
                <button @click="removeFeature('prompt', index)" class="tag-remove">×</button>
              </div>
            </div>
          </div>

          <!-- Corpus特征选择 -->
          <div class="data-source-section">
            <div class="section-header">
              <h3>Corpus特征条件</h3>
              <button 
                @click="clearFeatures('corpus')" 
                class="clear-btn"
                :disabled="!selectedFeatures.corpus.length">
                清空Corpus
              </button>
            </div>
            <div v-if="selectedFeatures.corpus.length === 0" class="empty-state">
              <p>点击Corpus图表中的条形以添加筛选条件</p>
            </div>
            <div v-else class="tags-container">
              <div v-for="(feature, index) in selectedFeatures.corpus" 
                  :key="'corpus-'+index" 
                  class="feature-tag">
                <span class="tag-content">
                  <span class="feature-name">{{ feature.featureName }}</span>
                  <span class="value-range">{{ feature.valueRange }}</span>
                  <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                </span>
                <button @click="removeFeature('corpus', index)" class="tag-remove">×</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 中间面板 - 数据列表 -->
    <div class="center-panel">
      <div class="center-content">
        <!-- 上部分显示Prompt -->
        <div class="prompt-list">
          <h2>Prompt List</h2>
          <div v-if="currentPrompts.length === 0" class="empty-state">
            <p>加载中...</p>
          </div>
          <div v-else class="scrollable-list">
            <div v-for="(prompt, index) in currentPrompts" :key="index" class="list-item">
              <div class="item-id">#{{ promptIds[index] }}</div>
              <div class="item-content">{{ prompt }}</div>
            </div>
          </div>
        </div>
        <div class="corpus-list">
          <h2>Corpus List</h2>
          <div v-if="currentCorpus.length === 0" class="empty-state">
            <p>加载中...</p>
          </div>
          <div v-else class="scrollable-list">
            <div v-for="(corpus, index) in currentCorpus" :key="index" class="list-item">
              <div class="item-id">#{{ corpusIds[index] }}</div>
              <div class="item-content">{{ corpus }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as d3 from 'd3'
import { ref, onMounted,  watch,nextTick } from 'vue'

// 图表尺寸常量
const chartWidth = 320
const chartHeight = 400
// const containerHeight = 250

// 数据引用
const promptIds = ref(Array.from({length: 660}, (_, i) => i))
const corpusIds = ref(Array.from({length: 660}, (_, i) => i))
const currentPrompts = ref([])
const currentCorpus = ref([])
const distributionData = ref(null)
const distributionDataCorpus = ref(null)


const selectedFeatures = ref({
  prompt: [], // 存储prompt的特征选择
  corpus: []  // 存储corpus的特征选择
})


const barBorders = ref({
  prompt: {}, // 结构: { "特征名-值范围": true/false }
  corpus: {}
})

function createBarEventHandlers(isContinuous, dataSource, featureName, tooltip) {
  return {
    mouseover: function(event, d) {
      d3.select(this)
        .attr("opacity", 1)
        .attr("stroke", "#333")
        .attr("stroke-width", 1.5);

      tooltip.transition()
        .duration(200)
        .style("opacity", .9);
      tooltip.html(`
        <div><strong>区间:</strong> ${isContinuous ? `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : d.label}</div>
        <div><strong>数量:</strong> ${d.count}</div>
        <div><strong>鲁棒性:</strong> ${d.robustness.toFixed(2)}</div>
      `)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");
    },
    mouseout: function() {
      const d = d3.select(this).datum();
      const valueRange = isContinuous ? 
        `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : 
        d.label || d.value_name;
      
      const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
      
      if (!isSelected) {
        d3.select(this)
          .attr("opacity", 0.7)
          .attr("stroke", "none");
      }
      
      tooltip.transition()
        .duration(500)
        .style("opacity", 0);
    }
  };
}

function createChart(svgElement, featureName, featureData, isContinuous, dataSource) {
  const margin = { top: 30, right: 10, bottom: 10, left: 20 };
  const innerWidth = chartWidth - margin.left - margin.right;
  const innerHeight = chartHeight - margin.top - margin.bottom;

  // 清除现有内容
  d3.select(svgElement).selectAll("*").remove();

  // 创建工具提示div
  const tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0)
    .style("position", "absolute")
    .style("background", "white")
    .style("border", "1px solid #ddd")
    .style("border-radius", "4px")
    .style("padding", "8px")
    .style("pointer-events", "none")
    .style("font-size", "12px")
    .style("box-shadow", "0 2px 4px rgba(0,0,0,0.2)");

  let displayData, y, yTicks;

  // 处理数据
  if (isContinuous) {
    const values = featureData.values.map(d => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const step = (max - min) / 10;

    displayData = Array.from({ length: 10 }, (_, i) => {
      const start = min + i * step;
      const end = start + step;
      const items = featureData.values.filter(d =>
        d.value >= start && d.value < end
      );
      return {
        start,
        end,
        count: items.length,
        robustness: items.reduce((sum, d) => sum + d.robustness, 0) / (items.length || 1),
      };
    });

    yTicks = d3.range(min, max + step, step);
    y = d3.scaleLinear()
      .domain([min, max])
      .range([margin.top, margin.top + innerHeight]);
  } else {
    displayData = featureData.map(d => ({
      label: d.value_name,
      count: d.count,
      robustness: d.avg_robustness,
    }));

    y = d3.scaleBand()
      .domain(displayData.map(d => d.label))
      .range([margin.top, margin.top + innerHeight])
      .padding(0.2);
  }

  const svg = d3.select(svgElement)
    .attr("width", chartWidth)
    .attr("height", chartHeight);

  const xCount = d3.scaleLinear()
    .domain([0, d3.max(displayData, d => d.count)])
    .range([0, innerWidth / 2 - 10]);

  const xRobustness = d3.scaleLinear()
    .domain([0, 1])
    .range([0, innerWidth / 2 - 10]);

  // 添加Y轴
  svg.append("g")
    .attr("class", "y-axis")
    .attr("transform", `translate(${margin.left},0)`)
    .call(
      isContinuous
        ? d3.axisLeft(y).tickValues(yTicks).tickFormat(d => d.toFixed(1))
        : d3.axisLeft(y)
    )
    .selectAll("text")
    .style("text-anchor", "middle")
    .attr("dx", "-2px")
    .style("font-size", "15px");

  const barPadding = 4;
  const eventHandlers = createBarEventHandlers(isContinuous, dataSource, featureName, tooltip);

  // 添加左侧条形图
  svg.selectAll(".bar-count")
    .data(displayData)
    .join("rect")
    .attr("class", "bar-count")
    .attr("x", d => margin.left + innerWidth / 2 - xCount(d.count))
    .attr("y", d => isContinuous ? y(d.start) : y(d.label))
    .attr("width", d => xCount(d.count))
    .attr("height", d => isContinuous ? Math.abs(y(d.end) - y(d.start)) - barPadding : y.bandwidth())
    .attr("fill", "#4e79a7")
    .attr("opacity", 0.7)
    .attr('data-source', dataSource)
    .attr('data-feature', featureName)
    .attr('data-range', d => isContinuous ? 
      `${Number(d.start).toFixed(2)}-${Number(d.end).toFixed(2)}` : 
      String(d.label).trim())
    .on("mouseover", eventHandlers.mouseover)
    .on("mouseout", eventHandlers.mouseout)
    .on("click", d => handleBarClick(d, isContinuous, dataSource, featureName));

  // 添加右侧条形图
  svg.selectAll(".bar-robustness")
    .data(displayData)
    .join("rect")
    .attr("class", "bar-robustness")
    .attr("x", margin.left + innerWidth / 2)
    .attr("y", d => isContinuous ? y(d.start) : y(d.label))
    .attr("width", d => xRobustness(d.robustness))
    .attr("height", d => isContinuous ? Math.abs(y(d.end) - y(d.start)) - barPadding : y.bandwidth())
    .attr("fill", "#e15759")
    .attr("opacity", 0.7)
    .attr('data-source', dataSource)
    .attr('data-feature', featureName)
    .attr('data-range', d => isContinuous ? 
      `${Number(d.start).toFixed(2)}-${Number(d.end).toFixed(2)}` : 
      String(d.label).trim())
    .on("mouseover", eventHandlers.mouseover)
    .on("mouseout", eventHandlers.mouseout)
    .on("click", d => handleBarClick(d, isContinuous, dataSource, featureName));

  // 添加中线
  svg.append("line")
    .attr("x1", margin.left + innerWidth / 2)
    .attr("x2", margin.left + innerWidth / 2)
    .attr("y1", margin.top)
    .attr("y2", margin.top + innerHeight)
    .attr("stroke", "#999")
    .attr("stroke-width", 1)
    .attr("stroke-dasharray", "2,2");

  updateBarBorders(svg, isContinuous, dataSource, featureName);
}

// 通用数据获取函数
async function fetchData(endpoint, body) {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    return await response.json();
  } catch (error) {
    console.error(`数据获取失败 (${endpoint}):`, error);
    return null;
  }
}

// 统一的文本数据获取函数
async function fetchTextData() {
  const [promptData, corpusData] = await Promise.all([
    fetchData('http://127.0.0.1:5000/get_prompt_data', { ids: promptIds.value }),
    fetchData('http://127.0.0.1:5000/get_corpus_data', { ids: corpusIds.value })
  ]);
  
  currentPrompts.value = promptData?.prompt || [];
  currentCorpus.value = corpusData?.corpus || [];
}

// 统一的特征分布获取函数
async function fetchFeatureDistribution(type) {
  const endpoint = type === 'prompt' 
    ? 'http://localhost:5000/api/prompt_feature_distribution'
    : 'http://localhost:5000/api/corpus_feature_distribution';
    
  const data = await fetchData(endpoint, {
    prompt_ids: promptIds.value,
    corpus_ids: corpusIds.value
  });
  
  if (type === 'prompt') {
    distributionData.value = data?.distribution;
  } else {
    distributionDataCorpus.value = data?.distribution;
  }
}

// 统一的图表创建函数
async function initChartsWithDataAttribute() {
  await nextTick();
  console.log('开始初始化图表...');
  
  // 处理 Prompt 和 Corpus 数据
  const dataSources = [
    { data: distributionData.value, type: 'prompt' },
    { data: distributionDataCorpus.value, type: 'corpus' }
  ];
  
  for (const { data, type } of dataSources) {
    if (!data) continue;
    
    const container = document.querySelector(`[data-container="${type}"]`);
    if (!container) continue;
    
    const svgs = container.querySelectorAll('.feature-chart svg');
    let index = 0;
    
    // 处理连续特征
    Object.entries(data.continuous || {}).forEach(([featureName, featureData]) => {
      if (svgs[index]) {
        createChart(svgs[index], featureName, featureData, true, type);
        index++;
      }
    });
    
    // 处理离散特征
    Object.entries(data.discrete || {}).forEach(([featureName, featureData]) => {
      if (svgs[index]) {
        createChart(svgs[index], featureName, featureData, false, type);
        index++;
      }
    });
  }
}

// 修改监听器，使用 nextTick
watch([distributionData, distributionDataCorpus], async () => {
  console.log('数据变化，准备重新初始化图表');
  // 等待一小段时间确保 DOM 完全更新
  await new Promise(resolve => setTimeout(resolve, 100));
  await initChartsWithDataAttribute();
}, { deep: true });

// 修改 onMounted
onMounted(async () => {
  console.log('组件挂载完成');
  
  await Promise.all([
    fetchTextData(),
    fetchFeatureDistribution('prompt'),
    fetchFeatureDistribution('corpus')
  ]);
  
  console.log('数据获取完成');
  
  // 确保数据加载完成后再初始化图表
  await new Promise(resolve => setTimeout(resolve, 200));
  await initChartsWithDataAttribute();
});

// 修改后的removeFeature
function removeFeature(dataSource, index) {
  const feature = selectedFeatures.value[dataSource][index];
  const key = `${feature.featureName}-${feature.valueRange}`;
  
  delete barBorders.value[dataSource][key];
  selectedFeatures.value[dataSource].splice(index, 1);
  
  // 精准更新（只需更新被移除的特征）
  updateChartBorders(dataSource, feature.featureName, feature.valueRange);
}

// 修改后的clearFeatures
const clearFeatures = (dataSource) => {
  barBorders.value = { ...barBorders.value, [dataSource]: {} };
  selectedFeatures.value = { ...selectedFeatures.value, [dataSource]: [] };
  
  // 全量更新当前数据源
  document.querySelectorAll(`.feature-container[data-container="${dataSource}"] svg`)
    .forEach(svg => {
      d3.select(svg).selectAll(".bar-count, .bar-robustness")
        .attr("stroke", "none")
        .attr("opacity", 0.7)
        .attr("stroke-width", 0);
    });
};

// 更新所有图表的边框状态
// 替换原来的updateAllChartBorders
function updateChartBorders(dataSource, featureName, valueRange) {
  // 1. 找到匹配的SVG容器
  const container = document.querySelector(
    `.feature-container[data-container="${dataSource}"]`
  );
  if (!container) return;


  // 3. 然后只重新绘制当前选中的条形
  d3.select(container).selectAll(`.bar-count, .bar-robustness`)
    .filter(function() {
      const bar = d3.select(this);
      if(bar.attr('data-source')===dataSource && bar.attr('data-feature')===featureName && bar.attr('data-range')===valueRange) 
      { console.log(bar.attr('data-source')); console.log(bar.attr('data-feature')); console.log(bar.attr('data-range')); return true; }

      return bar.attr('data-feature') === featureName && 
             bar.attr('data-range') === valueRange;
    })
    .attr("opacity", 0.7)
    .attr("stroke-width", 0)
    .attr("stroke-dasharray", null)
    .attr("stroke", "none");
}

// 更新条形图的边框状态
function updateBarBorders(svg, isContinuous, dataSource, featureName) {
  svg.selectAll(".bar-count, .bar-robustness")
    .attr("stroke", d => {
      const valueRange = isContinuous ? `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : d.label;
      return barBorders.value[dataSource][`${featureName}-${valueRange}`] ? "#333" : "none";
    })
    .attr("stroke-width", 1.5)
    .attr("stroke-dasharray", "3,2")
    .attr("opacity", d => {
      const valueRange = isContinuous ? `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : d.label;
      return barBorders.value[dataSource][`${featureName}-${valueRange}`] ? 1 : 0.7;
    });
}

// 处理条形图点击事件
function handleBarClick(d, isContinuous, dataSource, featureName) {
  const valueRange = isContinuous ? `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : d.label;
  const featureKey = `${featureName}-${valueRange}`;
  
  // 创建新对象确保响应式更新
  const newBorders = {
    ...barBorders.value,
    [dataSource]: {
      ...barBorders.value[dataSource],
      [featureKey]: !barBorders.value[dataSource]?.[featureKey]
    }
  };
  
  // 更新边框状态
  barBorders.value = newBorders;
  
  // 更新选择集合
  if (newBorders[dataSource][featureKey]) {
    selectedFeatures.value = {
      ...selectedFeatures.value,
      [dataSource]: [
        ...(selectedFeatures.value[dataSource] || []),
        {
          featureName,
          isContinuous,
          valueRange,
          count: d.count,
          robustness: d.robustness.toFixed(2)
        }
      ]
    };
  } else {
    selectedFeatures.value = {
      ...selectedFeatures.value,
      [dataSource]: (selectedFeatures.value[dataSource] || []).filter(
        item => !(item.featureName === featureName && item.valueRange === valueRange)
      )
    };
  }
  
  // 立即更新视图
  updateBarBorders(d3.select(this.parentNode), isContinuous, dataSource, featureName);
}
</script>

<style scoped>
/* 布局容器样式 */
.layout-container {
  display: flex;
  height: 100vh;
  width: 100%;
}

.left-panel {
  flex: 2250px;
  height: 1384px;
  display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
}

.center-panel {
  flex: 0 0 20%;
  border: 1px solid #ccc;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

/* 桑基图区域样式 */
.sankey-section {
  flex: 1;
  margin: 4px;
  background-color: white;
  display: flex;
  flex-direction: column;
}

/* 特征图表容器样式 */
.feature-container {
  width: 2250px;
  height: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  margin: 10px;
}

/* 特征控制面板样式 - 合并了重复的样式定义 */
.feature-control {
  width: 2250px;
  height: 100%;
  padding: 15px;
  background-color: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow-y: auto;
  position: relative;
  margin: 10px;
}

.scroll-container {
  width: 100%;
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
}

.feature-charts {
  display: flex;
  height: 100%;
  width: max-content;
  padding: 10px;
}

.feature-chart {
  flex: 0 0 auto;
  width: 320px;
  height: 400px;
  margin-right: 20px;
  padding: 10px;
  background: white;
  /* border: 1px solid #eee; */
  border-radius: 4px;
}

.feature-chart h3 {
  margin: 0 0 10px 0;
  font-size: 14px;
  text-align: center;
  color: #333;
}

/* 滑块样式 */
.feature-slider {
  width: calc(100% - 20px);
  margin: 5px 10px;
  height: 8px;
  -webkit-appearance: none;
  background: #ddd;
  border-radius: 4px;
  outline: none;
}

.feature-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #4e79a7;
  border-radius: 50%;
  cursor: pointer;
}

.feature-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #4e79a7;
  border-radius: 50%;
  cursor: pointer;
}

/* 滚动条样式 */
.scroll-container::-webkit-scrollbar {
  height: 8px;
}

.scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.scroll-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.scroll-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 数据列表样式 */
.center-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 10px;
}

.prompt-list, .corpus-list {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
}

.prompt-list h2, .corpus-list h2 {
  margin: 0 0 8px 0;
  padding: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 16px;
}

.scrollable-list {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #f8f8f8;
  padding: 4px;
}

.list-item {
  padding: 8px;
  margin-bottom: 6px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: white;
}

.item-id {
  font-weight: bold;
  margin-bottom: 4px;
  color: #555;
  font-size: 12px;
}

.item-content {
  font-size: 14px;
  line-height: 1.4;
  word-break: break-word;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
  font-style: italic;
}

/* 图表元素样式 */
.bar-count {
  fill: #4e79a7;
  opacity: 0.7;
}

.robustness-line {
  stroke: #e15759;
  stroke-width: 1.5;
  fill: none;
}

.robustness-dot {
  fill: #e15759;
}

.x-axis text,
.y-axis-count text,
.y-axis-robustness text,
.legend text {
  font-size: 10px;
}
.tooltip {
  position: absolute;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  pointer-events: none;
  font-size: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  z-index: 1000;
  max-width: 200px;
}

.bar-count, .bar-robustness {
  transition: opacity 0.2s;
}
.feature-control {
  padding: 15px;
  background-color: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow-y: auto;
}

.data-source-section {
  margin-bottom: 20px;
}

.data-source-section h3 {
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
  margin-bottom: 12px;
}

.selected-features-list {
  max-height: 150px;
  overflow-y: auto;
  margin-bottom: 15px;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 5px;
}

.feature-item {
  padding: 8px;
  margin-bottom: 8px;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  transition: all 0.2s;
}

.feature-item:hover {
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* 为不同数据源添加不同颜色标识 */
.selected-features-list.prompt-list .feature-item {
  border-left: 3px solid #4e79a7;
}

.selected-features-list.corpus-list .feature-item {
  border-left: 3px solid #e15759;
}

/* 其他样式保持不变... */
.feature-control {
  padding: 15px;
  background-color: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow-y: auto;
}

.data-source-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-header h3 {
  margin: 0;
  color: #333;
  font-size: 16px;
}

.clear-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 13px;
  padding: 2px 8px;
  border-radius: 4px;
}

.clear-btn:hover {
  color: #e15759;
}

.clear-btn:disabled {
  color: #ddd;
  cursor: not-allowed;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag {
  display: inline-flex;
  align-items: center;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 15px;
  padding: 4px 8px 4px 12px;
  font-size: 13px;
  line-height: 1;
  transition: all 0.2s;
}

.feature-tag:hover {
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.tag-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.feature-name {
  font-weight: bold;
  color: #333;
}

.value-range {
  color: #4e79a7;
}

.stats {
  color: #666;
  font-size: 12px;
}

.tag-remove {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  margin-left: 6px;
  padding: 0 4px;
}

.tag-remove:hover {
  color: #e15759;
}

.empty-state {
  color: #999;
  text-align: center;
  padding: 20px;
  font-style: italic;
  font-size: 14px;
}

/* 为不同数据源添加不同颜色标识 */
.data-source-section:nth-child(1) .feature-tag {
  border-left: 3px solid #4e79a7;
}

.data-source-section:nth-child(2) .feature-tag {
  border-left: 3px solid #e15759;
}
.bar-count, .bar-robustness {
  transition: stroke 0.2s;
}

.bar-count[stroke="#333"] {
  stroke: #333;
  stroke-width: 1.5;
  stroke-dasharray: 3,2;
}

.bar-robustness[stroke="#333"] {
  stroke: #333;
  stroke-width: 1.5;
  stroke-dasharray: 3,2;
}
</style>