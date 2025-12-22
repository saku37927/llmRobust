<template>
    <div class="main-layout">
      <!-- 顶部：prompt特征图 -->
      <div class="top-feature">
        <div class="feature-container" data-container="prompt" style="width: 100vw;">
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
      <!-- 中间内容区 -->
      <div class="middle-row">
        <!-- 左侧：选择状态 -->
        <div class="left-status">
          <div class="prompt-status">
            <div class="section-header">
              <h3>prompt选择状态</h3>
              <div class="button-group">
                <button 
                  @click="submitFeatures('prompt')" 
                  class="icon-btn"
                  :disabled="!selectedFeatures.prompt.length"
                  :title="'提交选择'">
                  <el-icon><Check /></el-icon>
                </button>
                <button 
                  @click="clearFeatures('prompt')" 
                  class="icon-btn"
                  :disabled="!selectedFeatures.prompt.length"
                  :title="'清空Prompt'">
                  <el-icon><Delete /></el-icon>
                </button>
              </div>
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
          <div class="corpus-status">
            <div class="section-header">
              <h3>corpus选择状态</h3>
              <div class="button-group">
                <button 
                  @click="submitFeatures('corpus')" 
                  class="icon-btn"
                  :disabled="!selectedFeatures.corpus.length"
                  :title="'提交选择'">
                  <el-icon><Check /></el-icon>
                </button>
                <button 
                  @click="clearFeatures('corpus')" 
                  class="icon-btn"
                  :disabled="!selectedFeatures.corpus.length"
                  :title="'清空Corpus'">
                  <el-icon><Delete /></el-icon>
                </button>
              </div>
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
        <!-- 中间：空白 -->
        <div class="center-blank">
          <div class="blank-content"></div>
        </div>
        <!-- 右侧：列表 -->
        <div class="right-list horizontal-lists">
          <div class="prompt-list horizontal-list-item">
            <div class="list-header">
              <h2>prompt列表</h2>
              <button class="sort-btn" @click="cyclePromptSort" :title="promptSortState==='robustnessDesc'?'鲁棒性降序':promptSortState==='robustnessAsc'?'鲁棒性升序':'ID排序'">
                <el-icon>
                  <Sort v-if="promptSortState==='robustnessDesc'" />
                  <Sort v-else-if="promptSortState==='robustnessAsc'" style="transform:rotate(180deg)" />
                  <Sort v-else style="color:#bbb" />
                </el-icon>
              </button>
            </div>
            <div v-if="currentPrompts.length === 0" class="empty-state">
              <p>加载中...</p>
            </div>
            <div v-else class="scrollable-list">
              <div v-for="item in sortedPrompts" :key="item.id" class="list-item row-flex">
                <div class="item-id">ID: {{ item.id }}</div>
                <div class="item-content">{{ item.text }}</div>
                <div class="item-robustness" :style="robustnessColorStyle(item.robustness)">{{ item.robustness.toFixed(4) }}</div>
              </div>
            </div>
          </div>
          <div class="corpus-list horizontal-list-item">
            <div class="list-header">
              <h2>corpus列表</h2>
              <button class="sort-btn" @click="cycleCorpusSort" :title="corpusSortState==='robustnessDesc'?'鲁棒性降序':corpusSortState==='robustnessAsc'?'鲁棒性升序':'ID排序'">
                <el-icon>
                  <Sort v-if="corpusSortState==='robustnessDesc'" />
                  <Sort v-else-if="corpusSortState==='robustnessAsc'" style="transform:rotate(180deg)" />
                  <Sort v-else style="color:#bbb" />
                </el-icon>
              </button>
            </div>
            <div v-if="currentCorpus.length === 0" class="empty-state">
              <p>加载中...</p>
            </div>
            <div v-else class="scrollable-list">
              <div v-for="item in sortedCorpus" :key="item.id" class="list-item row-flex">
                <div class="item-id">ID: {{ item.id }}</div>
                <div class="item-content">{{ item.text }}</div>
                <div class="item-robustness" :style="robustnessColorStyle(item.robustness)">{{ item.robustness.toFixed(4) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 底部：corpus特征图 -->
      <div class="bottom-feature">
        <div class="feature-container" data-container="corpus" style="width: 100vw;">
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
    </div>
  </template>
  
  <script setup>
  import * as d3 from 'd3'
  import { ref, onMounted,  watch,nextTick, computed } from 'vue'
  import { toRaw } from 'vue'
  import { Sort, Check, Delete } from '@element-plus/icons-vue'
  
  // 图表尺寸常量
  const chartWidth =150
  const chartHeight = 200
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
  
  const promptSortState = ref('id') // 'id' | 'robustnessDesc' | 'robustnessAsc'
  const corpusSortState = ref('id')
  
  const sortedPrompts = computed(() => {
    if (promptSortState.value === 'robustnessDesc') {
      return [...currentPrompts.value].sort((a, b) => b.robustness - a.robustness)
    } else if (promptSortState.value === 'robustnessAsc') {
      return [...currentPrompts.value].sort((a, b) => a.robustness - b.robustness)
    } else {
      return [...currentPrompts.value].sort((a, b) => a.id - b.id)
    }
  })
  const sortedCorpus = computed(() => {
    if (corpusSortState.value === 'robustnessDesc') {
      return [...currentCorpus.value].sort((a, b) => b.robustness - a.robustness)
    } else if (corpusSortState.value === 'robustnessAsc') {
      return [...currentCorpus.value].sort((a, b) => a.robustness - b.robustness)
    } else {
      return [...currentCorpus.value].sort((a, b) => a.id - b.id)
    }
  })
  
  function cyclePromptSort() {
    if (promptSortState.value === 'id') promptSortState.value = 'robustnessDesc'
    else if (promptSortState.value === 'robustnessDesc') promptSortState.value = 'robustnessAsc'
    else promptSortState.value = 'id'
  }
  function cycleCorpusSort() {
    if (corpusSortState.value === 'id') corpusSortState.value = 'robustnessDesc'
    else if (corpusSortState.value === 'robustnessDesc') corpusSortState.value = 'robustnessAsc'
    else corpusSortState.value = 'id'
  }
  
  function createChart(svgElement, featureName, featureData, isContinuous,dataSource) {
    console.log(dataSource)
    const margin = { top: 10, right: 10, bottom: 10, left: 20 };
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
  
    let displayData, y;
    // let displayData, y, yTicks;
  
    if (isContinuous) {
      // 连续特征处理
      const values = featureData.values.map(d => d.value);
      const min = Math.min(...values);
      const max = Math.max(...values);
      const step = (max - min) / 10;
  
      // 构造10个区间
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
  
      // y为线性比例尺
      // yTicks = d3.range(min, max + step, step);
      
      y = d3.scaleLinear()
        .domain([min, max])
        .range([margin.top, margin.top + innerHeight]);
    } else {
      // 离散特征处理
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
  
    // 计算鲁棒性最小值和最大值
    const robustnessValues = displayData.map(d => d.robustness);
    const minRobustness = Math.min(...robustnessValues);
    const maxRobustness = Math.max(...robustnessValues);
  
    // 鲁棒性条形图比例尺：下界为minRobustness，上界为maxRobustness
    const xRobustness = d3.scaleLinear()
      .domain([minRobustness, maxRobustness])
      .range([0, innerWidth / 2 - 10]);
  
    // 添加Y轴
    // svg.append("g")
    //   .attr("class", "y-axis")
    //   .attr("transform", `translate(${margin.left},0)`)
    //   .call(
    //     isContinuous
    //       ? d3.axisLeft(y).tickValues(yTicks).tickFormat(d => d.toFixed(1))
    //       : d3.axisLeft(y)
    //   )
    //   .selectAll("text")
    //   .style("text-anchor", "middle")
    //   .attr("dx", "-2px")
    //   .style("font-size", "15px");
  
    const barPadding = 4;
  
    // 添加交互功能到左侧条形图
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
      .attr('data-source', dataSource)  // 新增
      .attr('data-feature', featureName) // 新增
      .attr('data-range', d => {
          // 统一转为保留两位小数的格式
          if (isContinuous) {
            return `${Number(d.start).toFixed(2)}-${Number(d.end).toFixed(2)}`;
          }
          return String(d.label).trim(); // 离散值去除首尾空格
        })
      .on("mouseover", function(event, d) {
        // 高亮当前条形
        d3.select(this)
          .attr("opacity", 1)
          .attr("stroke", "#333")
          .attr("stroke-width", 1.5);
  
        // 显示工具提示
        tooltip.transition()
          .duration(200)
          .style("opacity", .9);
        tooltip.html(`
          <div><strong>区间:</strong> ${isContinuous ? `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : d.label}</div>
          <div><strong>数量:</strong> ${d.count}</div>
          <div><strong>鲁棒性:</strong> ${d.robustness.toFixed(4)}</div>
        `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        // 获取当前条形对应的数据
        const d = d3.select(this).datum();
        
        // 计算当前条形的值范围（与点击逻辑一致）
        const valueRange = isContinuous ? 
          `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : 
          d.label || d.value_name;
        
        // 检查是否已被选中
        const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
        
        // 只有未选中的条形才恢复默认样式
        if (!isSelected) {
          d3.select(this)
            .attr("opacity", 0.7)
            .attr("stroke", "none");
        }
        
        // 无论是否选中都隐藏工具提示
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
      })
      .on("click", function(event, d) {
        handleBarClick(d);
  
      });
      
  
    // 添加交互功能到右侧条形图
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
      .attr('data-source', dataSource)  // 新增
      .attr('data-feature', featureName) // 新增
      .attr('data-range', d => {
        // 统一转为保留两位小数的格式
        if (isContinuous) {
          return `${Number(d.start).toFixed(2)}-${Number(d.end).toFixed(2)}`;
        }
        return String(d.label).trim(); // 离散值去除首尾空格
      })// 新增
      .on("mouseover", function(event, d) {
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
          <div><strong>鲁棒性:</strong> ${d.robustness.toFixed(4)}</div>
        `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        // 获取当前条形对应的数据
        const d = d3.select(this).datum();
        
        // 计算当前条形的值范围（与点击逻辑一致）
        const valueRange = isContinuous ? 
          `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : 
          d.label || d.value_name;
        
        // 检查是否已被选中
        const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
        
        // 只有未选中的条形才恢复默认样式
        if (!isSelected) {
          d3.select(this)
            .attr("opacity", 0.7)
            .attr("stroke", "none");
        }
        
        // 无论是否选中都隐藏工具提示
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
      })
      .on("click", function(event, d) {
        handleBarClick(d);
  
      });
  
    // 添加中线
    svg.append("line")
      .attr("x1", margin.left + innerWidth / 2)
      .attr("x2", margin.left + innerWidth / 2)
      .attr("y1", margin.top)
      .attr("y2", margin.top + innerHeight)
      .attr("stroke", "#999")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "2,2");
  
    // 临时添加检查函数
  
    // 更新条形图的绘制逻辑，添加高亮状态
    const updateBarBorders = () => {
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
    };
  
    // 修改点击事件处理
    const handleBarClick = (d) => {
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
    
    // 必须这样赋值才能触发响应式更新
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
            robustness: d.robustness.toFixed(6)
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
    updateBarBorders();
  };
  
    updateBarBorders();
  }
  
  
  // 修改后的初始化图表函数
  async function initChartsWithDataAttribute() {
    // 等待 Vue 完成 DOM 更新
    await nextTick()
    
    console.log('开始初始化图表...')
    
    // Prompt 特征图表
    if (distributionData.value) {1
      const dataSource = 'prompt'
      console.log("处理 Prompt 数据:", distributionData.value)
      
      const promptContainer = document.querySelector('[data-container="prompt"]')
      console.log("Prompt 容器:", promptContainer)
      
      if (promptContainer) {
        const svgs = promptContainer.querySelectorAll('.feature-chart svg')
        console.log("找到的 Prompt SVG 元素数量:", svgs.length)
        
        let index = 0
        
        // 连续特征
        Object.entries(distributionData.value.continuous || {}).forEach(([featureName, featureData]) => {
          // console.log(`处理 Prompt 连续特征 ${featureName}, index: ${index}`)
          if (svgs[index]) {
            createChart(svgs[index], featureName, featureData, true,dataSource)
            index++
          } else {
            console.warn(`Prompt 连续特征 ${featureName} 没有找到对应的 SVG 元素`)
          }
        })
        
        // 离散特征
        Object.entries(distributionData.value.discrete || {}).forEach(([featureName, featureData]) => {
          // console.log(`处理 Prompt 离散特征 ${featureName}, index: ${index}`)
          if (svgs[index]) {
            createChart(svgs[index], featureName, featureData, false,dataSource)
            index++
          } else {
            console.warn(`Prompt 离散特征 ${featureName} 没有找到对应的 SVG 元素`)
          }
        })
      }
    }
    
    // Corpus 特征图表
    if (distributionDataCorpus.value) {
      const dataSource = 'corpus'
      console.log("处理 Corpus 数据:", distributionDataCorpus.value)
      
      const corpusContainer = document.querySelector('[data-container="corpus"]')
      console.log("Corpus 容器:", corpusContainer)
      
      if (corpusContainer) {
        const svgs = corpusContainer.querySelectorAll('.feature-chart svg')
        console.log("找到的 Corpus SVG 元素数量:", svgs.length)
        
        let index = 0
        
        // 连续特征
        Object.entries(distributionDataCorpus.value.continuous || {}).forEach(([featureName, featureData]) => {
          // console.log(`处理 Corpus 连续特征 ${featureName}, index: ${index}`)
          if (svgs[index]) {
            createChart(svgs[index], featureName, featureData, true,dataSource)
            index++
          } else {
            console.warn(`Corpus 连续特征 ${featureName} 没有找到对应的 SVG 元素`)
          }
        })
        
        // 离散特征
        Object.entries(distributionDataCorpus.value.discrete || {}).forEach(([featureName, featureData]) => {
          // console.log(`处理 Corpus 离散特征 ${featureName}, index: ${index}`)
          if (svgs[index]) {
            createChart(svgs[index], featureName, featureData, false,dataSource)
            index++
          } else {
            console.warn(`Corpus 离散特征 ${featureName} 没有找到对应的 SVG 元素`)
          }
        })
      }
    }
  }
  // const continuousFeatures = new Set([
  //   '语义模糊度', '语法复杂度', '词汇复杂度', '歧义性',
  //   '困惑度', '语言流畅性', '情感刺激性', '无关信息量','长度','冗余度','极性词数量','词汇多样性','标点','特殊字符','模糊性','否定词含量'
  // ])
  
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
  // 安全查询DOM元素
  // function safeQuery(selector) {
  //   const elements = document.querySelectorAll(selector);
  //   return Array.from(elements).filter(el => el !== null);
  // }
  // 数据获取方法
  async function fetchTextData() {
    try {
      const promptResponse = await fetch('http://127.0.0.1:5000/get_prompt_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: promptIds.value })
      });
      const promptData = await promptResponse.json();
      currentPrompts.value = promptData.prompt || [];
      console.log('更新后的 prompts:', currentPrompts.value);
      
      const corpusResponse = await fetch('http://127.0.0.1:5000/get_corpus_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: corpusIds.value })
      });
      const corpusData = await corpusResponse.json();
      currentCorpus.value = corpusData.corpus || [];
      console.log('更新后的 corpus:', currentCorpus.value);
    } catch (error) {
      console.error('数据获取失败:', error);
    }
  }
  
  async function fetchFeatureDistribution() {
    try {
      const response = await fetch('http://localhost:5000/api/prompt_feature_distribution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt_ids: promptIds.value,
          corpus_ids: corpusIds.value
        })
      });
      const data = await response.json();
      distributionData.value = data.distribution;
      console.log("更新后的 prompt 特征分布数据：", distributionData.value);
    } catch (error) {
      console.error('获取特征分布失败:', error);
    }
  }
  
  async function fetchCorpusFeatureDistribution() {
    try {
      const response = await fetch('http://localhost:5000/api/corpus_feature_distribution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt_ids: promptIds.value,
          corpus_ids: corpusIds.value
        })
      });
      const data = await response.json();
      distributionDataCorpus.value = data.distribution;
      console.log("更新后的 corpus 特征分布数据：", distributionDataCorpus.value);
    } catch (error) {
      console.error('获取特征分布失败:', error);
    }
  }
  
  // 修改监听器，使用 nextTick
  watch([distributionData, distributionDataCorpus], async () => {
    console.log('数据变化，准备重新初始化图表')
    // 等待一小段时间确保 DOM 完全更新
    await new Promise(resolve => setTimeout(resolve, 100))
    await initChartsWithDataAttribute()
  }, { deep: true })
  
  // 修改 onMounted
  onMounted(async () => {
    console.log('组件挂载完成')
    
    await Promise.all([
      fetchTextData(),
      fetchFeatureDistribution(),
      fetchCorpusFeatureDistribution()
    ])
    
    console.log('数据获取完成')
    
    // 确保数据加载完成后再初始化图表
    await new Promise(resolve => setTimeout(resolve, 200))
    await initChartsWithDataAttribute()
  })
  
  const submitFeatures = async (dataSource) => {
    const rawData = toRaw(selectedFeatures.value[dataSource]);
    console.log(`${dataSource} 当前选择状态:`, rawData);
    
    try {
      const response = await fetch('http://localhost:5000/api/filter_by_features', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selectedFeatures: rawData,
          dataSource: dataSource
        })
      });
      
      const result = await response.json();
      if (result.success) {
        console.log(`筛选后的${dataSource} IDs:`, result.filtered_ids);
        
        // 更新对应的ID列表
        if (dataSource === 'prompt') {
          promptIds.value = result.filtered_ids;
          console.log('更新后的 promptIds:', promptIds.value);
        } else {
          corpusIds.value = result.filtered_ids;
          console.log('更新后的 corpusIds:', corpusIds.value);
        }
        
        // 重新获取特征分布数据
        await Promise.all([
          fetchFeatureDistribution(),
          fetchCorpusFeatureDistribution()
        ]);
        
        // 重新获取文本数据
        await fetchTextData();
        
        console.log('数据更新完成');
      } else {
        console.error('筛选失败:', result.error);
      }
    } catch (error) {
      console.error('请求失败:', error);
    }
  };
  
  // 鲁棒性染色函数：0.6及以上蓝色，以下红色，线性插值
  function robustnessColorStyle(val) {
    let color = ''
    if (val >= 0.6) {
      // 蓝色区间：#b3d1ff(浅) ~ #0047ab(深)
      const t = (val - 0.6) / 0.4
      color = interpolateColor('#b3d1ff', '#0047ab', t)
    } else {
      // 红色区间：#ffd6d6(浅) ~ #b22222(深)
      const t = (0.6 - val) / 0.6
      color = interpolateColor('#ffd6d6', '#b22222', t)
    }
    return { color }
  }
  
  // 线性插值颜色
  function interpolateColor(color1, color2, t) {
    // color1, color2: '#rrggbb', t: 0~1
    const c1 = [parseInt(color1.slice(1,3),16),parseInt(color1.slice(3,5),16),parseInt(color1.slice(5,7),16)]
    const c2 = [parseInt(color2.slice(1,3),16),parseInt(color2.slice(3,5),16),parseInt(color2.slice(5,7),16)]
    const c = c1.map((v,i)=>Math.round(v+(c2[i]-v)*t))
    return `rgb(${c[0]},${c[1]},${c[2]})`
  }
  </script>
  
  <style scoped>
  .main-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
  }
  .top-feature {
    flex: 0 0 250px;
    min-height: 250px;
    border-bottom: 1px solid #ddd;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .bottom-feature {
    flex: 0 0 250px;
    min-height: 250px;
    border-top: 1px solid #ddd;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .middle-row {
    flex: 1 1 auto;
    display: flex;
    flex-direction: row;
    min-height: 0;
    min-width: 0;
    height: 500px;
    max-height: 800px;
  }
  .left-status {
    flex: 0 0 220px;
    min-width: 220px;
    border-right: none;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: stretch;
  }
  .prompt-status, .corpus-status {
    flex: 1 1 0;
    border-bottom: 1px solid #ddd;
    padding: 16px 8px;
    min-height: 120px;
    border: 1px solid #ddd;
  }
  .corpus-status {
    border-bottom: none;
  }
  .center-blank {
    flex: 1 1 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    border-right: none;
    border-left: none;
  }
  .blank-content {
    font-size: 28px;
    color: #222;
  }
  .right-list {
    flex: 0 0 1400px;
    min-width: 1400px;
    max-width: 1400px;
    display: flex;
    flex-direction: column;
  }
  .right-list.horizontal-lists {
    display: flex;
    flex-direction: row;
    width: 1400px;
    min-width: 1400px;
    max-width: 1400px;
    height: 100%;
    border: 1px solid #ddd;
    background: none;
  }
  .horizontal-list-item {
    flex: 1 1 0;
    min-width: 0;
    border-right: 1px solid #ddd;
    padding: 16px 8px;
    min-height: 120px;
    display: flex;
    flex-direction: column;
  }
  .horizontal-list-item:last-child {
    border-right: none;
  }
  .prompt-list, .corpus-list {
    flex: 1 1 0;
    border-bottom: 1px solid #ddd;
    padding: 16px 8px;
    min-height: 120px;
    min-width: 0;
    display: flex;
    flex-direction: column;
    margin-bottom: 10px;
  }
  .corpus-list {
    border-bottom: none;
  }
  .prompt-list.horizontal-list-item h2,
  .corpus-list.horizontal-list-item h2 {
    margin: 0 0 8px 0;
    padding: 8px;
    background-color: #f0f0f0;
    border-radius: 4px;
    font-size: 16px;
  }
  /* 布局容器样式 */
  .layout-container {
    display: flex;
    height: 100vh;
    width: 100%;
  }
  
  
  
  /* 桑基图区域样式 */
  .sankey-section {
    flex: 1;
    margin: 4px;
    background-color: white;
    display: flex;
    flex-direction: column;
    /* border: 1px solid #999; */
  }
  
  /* 特征图表容器样式 */
  .feature-container {
    width: 2200px;
    height: 100%;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
    margin: 10px;
  }
  .feature-control {
    width: 2200px;
    height: 100%;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
    margin-left: 10px;
    margin-right: 10px;
  }
  
  .scroll-container {
    width: 100%;
    height: 100%;
    /* overflow-x: auto; */
    /* overflow-y: hidden; */
    scroll-behavior: smooth;
  }
  
  .feature-charts {
    display: flex;
    flex-wrap: wrap; /* 允许自动换行 */
    height: 100%;
    width: 100%;
    padding: 2px;
  }
  
  .feature-chart {
    flex: 0 0 auto;
    width: 150px;
    height: 200px;
    margin-right: 2px;
    margin-bottom: 10px; /* 新增：下方间距 */
    padding: 2px;
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
  
  .button-group {
    display: flex;
    gap: 8px;
  }
  
  .icon-btn {
    background: #f0f0f0;
    border: none;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 16px;
    color: #4e79a7;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .icon-btn:disabled {
    color: #bbb;
    cursor: not-allowed;
    background: #f5f5f5;
  }
  .icon-btn:hover:not(:disabled) {
    background: #e3f0ff;
    color: #2c4c6b;
  }
  .icon-btn .el-icon {
    font-size: 18px;
  }
  
  .tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .feature-tag {
    display: inline-flex;
    align-items: center;
    background: linear-gradient(90deg, #e3f0ff 0%, #f8faff 100%);
    border: 1.5px solid #4e79a7;
    border-radius: 18px;
    padding: 6px 14px 6px 16px;
    font-size: 14px;
    line-height: 1.2;
    box-shadow: 0 2px 8px rgba(78,121,167,0.08);
    margin-bottom: 6px;
    margin-right: 6px;
    transition: box-shadow 0.2s, border-color 0.2s;
  }
  
  .feature-tag:hover {
    box-shadow: 0 4px 12px rgba(78,121,167,0.18);
    border-color: #2c4c6b;
  }
  
  .data-source-section:nth-child(2) .feature-tag,
  .corpus-status .feature-tag {
    border-color: #e15759;
    background: linear-gradient(90deg, #ffeaea 0%, #fff8f8 100%);
  }
  
  .button-group button {
    border-radius: 6px;
    border: none;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
    margin-left: 4px;
    transition: background 0.2s, color 0.2s;
  }
  
  .submit-btn {
    background: #4e79a7;
    color: #fff;
  }
  
  .submit-btn:hover:not(:disabled) {
    background: #2c4c6b;
  }
  
  .clear-btn {
    background: #f5f5f5;
    color: #e15759;
  }
  
  .clear-btn:hover:not(:disabled) {
    background: #ffeaea;
    color: #b12a34;
  }
  
  .section-header h3 {
    font-size: 16px;
    font-weight: bold;
    border-left: 4px solid #4e79a7;
    padding-left: 8px;
    margin-right: 8px;
    color: #222;
  }
  
  .corpus-status .section-header h3 {
    border-left-color: #e15759;
  }
  
  .section-header {
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 10px;
    padding-bottom: 4px;
  }
  
  .empty-state {
    color: #bbb;
    text-align: center;
    padding: 24px 0;
    font-style: italic;
    font-size: 15px;
    letter-spacing: 1px;
  }
  
  .prompt-status, .corpus-status {
    background: #ffffff;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(78,121,167,0.04);
    border: 1px solid #e0e0e0;
    margin-bottom: 16px;
  }
  
  .feature-name {
    font-weight: bold;
    color: #222;
  }
  
  .value-range {
    color: #4e79a7;
    font-weight: 500;
  }
  
  .corpus-status .value-range {
    color: #e15759;
  }
  
  .stats {
    color: #888;
    font-size: 12px;
    margin-left: 4px;
  }
  
  .tag-remove {
    background: none;
    border: none;
    color: #bbb;
    cursor: pointer;
    font-size: 18px;
    margin-left: 8px;
    padding: 0 4px;
    transition: color 0.2s;
  }
  
  .tag-remove:hover {
    color: #e15759;
  }
  
  .tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    max-height: 120px;
    overflow-y: auto;
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
  
  .top-feature .feature-container,
  .bottom-feature .feature-container {
    width: 100vw !important;
    min-width: 100vw;
    max-width: 100vw;
  }
  .right-list.horizontal-lists {
    display: flex;
    flex-direction: row;
    width: 1400px;
    min-width: 1400px;
    max-width: 1400px;
    height: 100%;
    border: 1px solid #ddd;
    background: none;
  }
  .horizontal-list-item {
    flex: 1 1 0;
    min-width: 0;
    border-right: 1px solid #ddd;
    padding: 16px 8px;
    min-height: 120px;
    display: flex;
    flex-direction: column;
  }
  .horizontal-list-item:last-child {
    border-right: none;
  }
  .prompt-list.horizontal-list-item h2,
  .corpus-list.horizontal-list-item h2 {
    margin: 0 0 8px 0;
    padding: 8px;
    background-color: #f0f0f0;
    border-radius: 4px;
    font-size: 16px;
  }
  .row-flex {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .item-content {
    flex: 1;
    padding-right: 16px;
  }
  .item-robustness {
    width: 80px;
    text-align: center;
    border-radius: 4px;
    background: #fff;
    font-weight: bold;
    font-family: monospace;
    font-size: 14px;
    transition: color 0.2s;
  }
  
  .list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .sort-btn {
    background: #f0f0f0;
    border: none;
    border-radius: 6px;
    padding: 2px 6px;
    font-size: 16px;
    color: #4e79a7;
    cursor: pointer;
    margin-left: 8px;
    transition: background 0.2s, color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .sort-btn:hover {
    background: #e3f0ff;
    color: #2c4c6b;
  }
  .sort-btn .el-icon {
    font-size: 18px;
  }
  .item-id {
    font-weight: bold;
    margin-right: 10px;
    color: #555;
    font-size: 12px;
    min-width: 60px;
  }
  </style>








from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import json
import os
from collections import defaultdict
import numpy as np
from scipy import stats  # 添加这行导入

app = Flask(__name__)
CORS(app)

# 配置文件路径
PROMPT_FILE_PATH = r"D:\Desktop\LLM_Robust_Front\data\prompt\prompt_sorted.json"
CORPUS_FILE_PATH = r"D:\Desktop\LLM_Robust_Front\data\corpus\corpus_sorted.json"

# 加载数据文件
with open(r'D:\Desktop\LLM_Robust_Front\data\feature\prompt_feature_updated_final.json', 'r') as f:
    prompt_features = json.load(f)

with open('D:/Desktop/LLM_Robust_Front/data/feature/corpus_feature_updated.json', 'r') as f:
    corpus_features = json.load(f)

# with open('D:/Desktop/LLM_Robust_Front/data/final_result.json', 'r') as f:

with open(r'D:\Desktop\LLM_Robust_Front\data\flan_output\original\attack_contrast_result.json', 'r') as f:
    final_results = json.load(f)

# 定义离散特征及其可能的值
DISCRETE_FEATURES = {
    '文体': {
        0: '无明显文体特征',
        1: '书面用语',
        2: '口头用语',
        3: '礼貌用语',
        4: '动词短语',
        5: '恶劣用语'
    },
    '句型': {
        0: '无明显特征',
        1: '疑问句',
        2: '祈使句',
        3: '陈述句'
    },
    '语言文化风格': {
        0: '无明显特征',
        1: '美国文化',
        2: '东方文化',
        3: '拉丁文化',
        4: '欧洲文化'
    },
    '反向输出': {
        0: '无',
        1: '有'
    },
    '语态': {
        0: '无',
        1: '第一人称',
        2: '第二人称',
        3: '第三人称'
    },
    '时态': {
        0: '无',
        1: '现在时',
        2: '过去时',
        3: '未来时'
    },
    '情态': {
        0: '无',
        1: 'must',
        2: 'should',
        3: 'may',
        4: 'could',
        5: 'might',
        6: 'can',
        7: 'will',
        8: 'would',
        9: 'shall'
    },
    '思维链格式': {
        0: '无',
        1: '存在思维链格式'
    },
    '是否有例子': {
        0: '无例子',
        1: '有例子',
        2: '多例子'
    }
    
}

# 定义离散特征及其可能的值
CORPUS_DISCRETE_FEATURES = {
    '文体': {
        0: '无明显文体特征',
        1: '书面用语',
        2: '口头用语',
        3: '礼貌用语',
        4: '动词短语',
        5: '恶劣用语'
    },
    '句型': {
        0: '无明显特征',
        1: '疑问句',
        2: '祈使句',
        3: '陈述句'
    },
    '语言文化风格': {
        0: '无明显特征',
        1: '美国文化',
        2: '东方文化',
        3: '拉丁文化',
        4: '欧洲文化'
    },
    '语态': {
        0: '无',
        1: '第一人称',
        2: '第二人称',
        3: '第三人称'
    },
    '时态': {
        0: '无',
        1: '现在时',
        2: '过去时',
        3: '未来时'
    },
    '领域': {
        0: '无明显特征',
        1: '教育',
        2: '科学',
        3: '文化',
        4: '体育'
        }
}

# 定义特征向量中各个维度对应的特征
PROMPT_FEATURE_DIMENSIONS = {
    '文体': 0,
    '句型': 1,
    '语言文化风格': 3,  # 注意: 第4个维度索引是3
    '反向输出': 10,     # 第11个维度索引是10
    '语态': 12,        # 第13个维度索引是12
    '时态': 13,        # 第14个维度索引是13
    '情态': 14,        # 第15个维度索引是14
    '是否有例子': 18,   # 第18个维度索引是17
    '思维链格式': 17    # 第19个维度索引是18
}

CONTINUOUS_FEATURES = {
    '语义模糊度': {'index': 2 },  # 第5个特征(索引4)，分10个区间
    '语法复杂度': {'index': 4},  # 第6个特征(索引5)，分5个区间
    '词汇复杂度': {'index': 5}, 
    '长度': {'index': 6}, 
    '歧义性': {'index': 7}, 
    '冗余度': {'index': 8}, 
    '语法流畅性':{'index': 9},
    '情绪刺激性': {'index': 11}, 
    '无关信息量': {'index': 15}, 
    '否定词含量': {'index': 16}, 
}

CORPUS_FEATURE_DIMENSIONS = {
    '句型': 6,
    '语态': 8,        # 第13个维度索引是12
    '时态': 7,        # 第14个维度索引是13
    '文体': 12,
    '语言文化风格': 13,  # 注意: 第4个维度索引是3
    '领域': 14,        # 第15个维度索引是14
}
CORPUS_CONTINUOUS_FEATURES = {
    '词汇多样性': {'index': 5 },  # 第5个特征(索引4)，分10个区间
    '语法复杂度': {'index': 0},  # 第6个特征(索引5)，分5个区间
    '词汇复杂度': {'index': 1}, 
    '长度': {'index': 2}, 
    '极性词数量': {'index': 4}, 
    '冗余度': {'index': 3}, 
    '标点':{'index': 9},
    '特殊字符': {'index': 10}, 
    '语义模糊度': {'index': 11}, 
}



@app.route('/api/prompt_feature_distribution', methods=['POST'])
def get_prompt_feature_distribution():
    data = request.get_json()
    prompt_ids = data.get('prompt_ids', [])
    corpus_ids = data.get('corpus_ids', [])
    
    # 预处理：构建快速查询结构
    prompt_id_set = set(prompt_ids)
    corpus_id_set = set(corpus_ids)
    
    # 构建(prompt_id, corpus_id) -> accuracy的映射
    result_map = {
        (r['prompt_id'], r['corpus_id']): r['accuracy']
        for r in final_results
        if r['prompt_id'] in prompt_id_set and r['corpus_id'] in corpus_id_set
    }
    
    # 构建prompt_id -> feature_vector的映射
    feature_map = {
        pf['id']: pf['vector']
        for pf in prompt_features
        if pf['id'] in prompt_id_set
    }
    
    # 结果数据结构
    distribution = {
        'discrete': {},
        'continuous': {}
    }
    
    # 1. 处理离散特征
    for feature_name, value_map in DISCRETE_FEATURES.items():
        feature_index = PROMPT_FEATURE_DIMENSIONS[feature_name]  # 假设有预定义的维度映射
        feature_stats = defaultdict(lambda: {
            'count': 0,
            'total_robustness': 0,
            'prompt_ids': []  # 新增：记录属于该特征值的prompt_id
        })
        
        # 统计每个特征值
        for prompt_id, vector in feature_map.items():
            value = vector[feature_index]
            if value in value_map:  # 只统计预定义的特征值
                # 计算该prompt_id在所有corpus_ids下的平均鲁棒性
                accuracies = [
                    result_map[(prompt_id, cid)]
                    for cid in corpus_ids
                    if (prompt_id, cid) in result_map
                ]
                
                if accuracies:
                    avg_robustness = sum(accuracies) / len(accuracies)
                    feature_stats[value]['count'] += 1
                    feature_stats[value]['total_robustness'] += avg_robustness
                    feature_stats[value]['prompt_ids'].append(prompt_id)  # 记录prompt_id
        
        # 整理结果
        discrete_result = []
        for value, value_name in value_map.items():
            stats = feature_stats.get(value, {
                'count': 0,
                'total_robustness': 0,
                'prompt_ids': []
            })
            discrete_result.append({
                'value': value,
                'value_name': value_name,
                'count': stats['count'],
                'avg_robustness': round(stats['total_robustness'] / stats['count'], 4) if stats['count'] > 0 else None,
                'prompt_ids': stats['prompt_ids']  # 新增：返回prompt_id列表
            })
        
        distribution['discrete'][feature_name] = discrete_result
    
    # 2. 处理连续特征（改为返回所有值）
    for feature_name, config in CONTINUOUS_FEATURES.items():
        feature_index = config['index']
        feature_values = []
        
        # 收集所有prompt的该特征值及其鲁棒性
        for prompt_id, vector in feature_map.items():
            value = vector[feature_index]
            
            # 计算该prompt在所有corpus下的平均鲁棒性
            accuracies = [
                result_map[(prompt_id, cid)]
                for cid in corpus_ids
                if (prompt_id, cid) in result_map
            ]
            
            if accuracies:
                avg_robustness = sum(accuracies) / len(accuracies)
                feature_values.append({
                    'value': value,
                    'robustness': avg_robustness,
                    'prompt_id': prompt_id  # 可选，便于追踪数据来源
                })
        
        # 按特征值排序（可选）
        feature_values.sort(key=lambda x: x['value'])
        
        # 计算全局统计量
        values = [x['value'] for x in feature_values]
        robustnesses = [x['robustness'] for x in feature_values]
        
        distribution['continuous'][feature_name] = {
            'values': feature_values,  # 所有原始数据点
            'statistics': {
                'value_mean': np.mean(values) if values else None,
                'value_std': np.std(values) if values else None,
                'robustness_mean': np.mean(robustnesses) if robustnesses else None,
                'robustness_std': np.std(robustnesses) if robustnesses else None,
                'count': len(feature_values)
            }
        }
    
    return jsonify({
        'success': True,
        'distribution': distribution
    })


@app.route('/api/corpus_feature_distribution', methods=['POST'])
def get_corpus_feature_distribution():
    data = request.get_json()
    prompt_ids = data.get('prompt_ids', [])
    corpus_ids = data.get('corpus_ids', [])
    
    # 预处理：构建快速查询结构
    prompt_id_set = set(prompt_ids)
    corpus_id_set = set(corpus_ids)
    
    # 构建(prompt_id, corpus_id) -> accuracy的映射
    result_map = {
        (r['prompt_id'], r['corpus_id']): r['accuracy']
        for r in final_results
        if r['prompt_id'] in prompt_id_set and r['corpus_id'] in corpus_id_set
    }
    
    # 构建corpus_id -> feature_vector的映射
    feature_map = {
        pf['id']: pf['vector']
        for pf in corpus_features
        if pf['id'] in corpus_id_set
    }
    
    # 结果数据结构
    distribution = {
        'discrete': {},
        'continuous': {}
    }
    
    # 1. 处理离散特征
    for feature_name, value_map in CORPUS_DISCRETE_FEATURES.items():
        feature_index = CORPUS_FEATURE_DIMENSIONS[feature_name]
        feature_stats = defaultdict(lambda: {
            'count': 0,
            'total_robustness': 0,
            'corpus_ids': []  # 新增：记录属于该特征值的corpus_id
        })
        
        # 统计每个特征值
        for corpus_id, vector in feature_map.items():
            value = vector[feature_index]
            if value in value_map:
                # 计算该corpus_id在所有prompt_ids下的平均鲁棒性
                accuracies = [
                    result_map[(pid, corpus_id)]
                    for pid in prompt_ids
                    if (pid, corpus_id) in result_map
                ]
                
                if accuracies:
                    avg_robustness = sum(accuracies) / len(accuracies)
                    feature_stats[value]['count'] += 1
                    feature_stats[value]['total_robustness'] += avg_robustness
                    feature_stats[value]['corpus_ids'].append(corpus_id)  # 记录corpus_id
        
        # 整理结果
        discrete_result = []
        for value, value_name in value_map.items():
            stats = feature_stats.get(value, {
                'count': 0,
                'total_robustness': 0,
                'corpus_ids': []
            })
            discrete_result.append({
                'value': value,
                'value_name': value_name,
                'count': stats['count'],
                'avg_robustness': round(stats['total_robustness'] / stats['count'], 4) if stats['count'] > 0 else None,
                'corpus_ids': stats['corpus_ids']  # 新增：返回corpus_id列表
            })
        
        distribution['discrete'][feature_name] = discrete_result
    
    # 2. 处理连续特征（保持不变）
    for feature_name, config in CORPUS_CONTINUOUS_FEATURES.items():
        feature_index = config['index']
        feature_values = []
        
        for corpus_id, vector in feature_map.items():
            value = vector[feature_index]
            
            accuracies = [
                result_map[(pid, corpus_id)]
                for pid in prompt_ids
                if (pid, corpus_id) in result_map
            ]
            
            if accuracies:
                avg_robustness = sum(accuracies) / len(accuracies)
                feature_values.append({
                    'value': value,
                    'robustness': avg_robustness,
                    'corpus_id': corpus_id
                })
        
        feature_values.sort(key=lambda x: x['value'])
        
        values = [x['value'] for x in feature_values]
        robustnesses = [x['robustness'] for x in feature_values]
        
        distribution['continuous'][feature_name] = {
            'values': feature_values,
            'statistics': {
                'value_mean': np.mean(values) if values else None,
                'value_std': np.std(values) if values else None,
                'robustness_mean': np.mean(robustnesses) if robustnesses else None,
                'robustness_std': np.std(robustnesses) if robustnesses else None,
                'count': len(feature_values)
            }
        }
    
    return jsonify({
        'success': True,
        'distribution': distribution
    })



def calculate_prompt_robustness(prompt_ids, corpus_ids):
    # 预处理：将列表转换为集合提高查找效率
    prompt_ids_set = set(prompt_ids)
    corpus_ids_set = set(corpus_ids)
    
    # 预处理：构建prompt_id到特征向量的映射
    prompt_feature_map = {
        pf['id']: pf['vector'] 
        for pf in prompt_features 
        if pf['id'] in prompt_ids_set
    }
    
    # 预处理：构建(prompt_id, corpus_id)到accuracy的映射
    result_map = {
        (res['prompt_id'], res['corpus_id']): res['accuracy']
        for res in final_results 
        if res['prompt_id'] in prompt_ids_set and res['corpus_id'] in corpus_ids_set
    }
    
    # 结果字典，存储所有离散特征的鲁棒性值
    all_robustness = {}
    
    # 对每个离散特征计算鲁棒性
    for feature_name, feature_values in DISCRETE_FEATURES.items():
        dimension_index = PROMPT_FEATURE_DIMENSIONS[feature_name]
        feature_robustness = {}
        
        # 按特征值分组计算
        value_groups = defaultdict(list)
        for prompt_id, vector in prompt_feature_map.items():
            value = vector[dimension_index]
            if value in feature_values:  # 只处理预定义的特征值
                value_groups[value].append(prompt_id)
        
        # 对每个特征值计算鲁棒性
        for value, value_name in feature_values.items():
            matching_prompt_ids = value_groups.get(value, [])
            
            # 计算所有相关组合的accuracy
            accuracies = [
                result_map[(pid, cid)]
                for pid in matching_prompt_ids
                for cid in corpus_ids
                if (pid, cid) in result_map
            ]
            
            # 计算均值
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                feature_robustness[value_name] = round(avg_accuracy, 2)
            else:
                feature_robustness[value_name] = None
        
        all_robustness[feature_name] = feature_robustness
    
    return all_robustness

def calculate_corpus_robustness(prompt_ids, corpus_ids):
    # 预处理：将列表转换为集合提高查找效率
    prompt_ids_set = set(prompt_ids)
    corpus_ids_set = set(corpus_ids)
    
    # 预处理：构建prompt_id到特征向量的映射
    corpus_feature_map = {
        pf['id']: pf['vector'] 
        for pf in corpus_features 
        if pf['id'] in corpus_ids_set
    }
    
    # 预处理：构建(prompt_id, corpus_id)到accuracy的映射
    result_map = {
        (res['prompt_id'], res['corpus_id']): res['accuracy']
        for res in final_results 
        if res['prompt_id'] in prompt_ids_set and res['corpus_id'] in corpus_ids_set
    }
    
    # 结果字典，存储所有离散特征的鲁棒性值
    all_robustness = {}
    
    # 对每个离散特征计算鲁棒性
    for feature_name, feature_values in CORPUS_DISCRETE_FEATURES.items():
        dimension_index = CORPUS_FEATURE_DIMENSIONS[feature_name]
        feature_robustness = {}
        
        # 按特征值分组计算
        value_groups = defaultdict(list)
        for corpus_id, vector in corpus_feature_map.items():
            value = vector[dimension_index]
            if value in feature_values:  # 只处理预定义的特征值
                value_groups[value].append(corpus_id)
        
        # 对每个特征值计算鲁棒性
        for value, value_name in feature_values.items():
            matching_corpus_ids = value_groups.get(value, [])
            
            # 计算所有相关组合的accuracy
            accuracies = [
                result_map[(pid, cid)]
                for cid in matching_corpus_ids
                for pid in prompt_ids
                if (cid, pid) in result_map
            ]
            
            # 计算均值
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                feature_robustness[value_name] = round(avg_accuracy, 2)
            else:
                feature_robustness[value_name] = None
        
        all_robustness[feature_name] = feature_robustness
    
    return all_robustness

# 加载数据函数
def load_data(file_path):
    """加载JSON文件内容"""
    try:
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件失败: {e}")
        return []

# 数据缓存
prompt_data = load_data(PROMPT_FILE_PATH)
corpus_data = load_data(CORPUS_FILE_PATH)

# 根据ID获取prompt数据
@app.route('/get_prompt_data', methods=['POST'])
def get_prompt_data():
    try:
        data = request.json
        ids = data.get('ids', [])
        # 统计每个 prompt_id 的 accuracy
        robustness_map = {}
        for res in final_results:
            pid = res['prompt_id']
            if pid in ids:
                robustness_map.setdefault(pid, []).append(res['accuracy'])
        robustness_avg = {k: sum(v)/len(v) for k, v in robustness_map.items()}

        result = []
        for item in prompt_data:
            if 'prompt_id' in item and item['prompt_id'] in ids:
                result.append({
                    'id': item['prompt_id'],
                    'text': item['prompt'],
                    'robustness': round(robustness_avg.get(item['prompt_id'], 0), 3)
                })
        return jsonify({
            'success': True,
            'prompt': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'prompt': []
        }), 500

# 根据ID获取corpus数据
@app.route('/get_corpus_data', methods=['POST'])
def get_corpus_data():
    try:
        data = request.json
        ids = data.get('ids', [])
        # 统计每个 corpus_id 的 accuracy
        robustness_map = {}
        for res in final_results:
            cid = res['corpus_id']
            if cid in ids:
                robustness_map.setdefault(cid, []).append(res['accuracy'])
        robustness_avg = {k: sum(v)/len(v) for k, v in robustness_map.items()}

        result = []
        for item in corpus_data:
            if 'corpus_id' in item and item['corpus_id'] in ids:
                result.append({
                    'id': item['corpus_id'],
                    'text': item['corpus'],
                    'robustness': round(robustness_avg.get(item['corpus_id'], 0), 3)
                })
        return jsonify({
            'success': True,
            'corpus': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'corpus': []
        }), 500

# 刷新数据
@app.route('/refresh_data', methods=['GET'])
def refresh_data():
    global prompt_data, corpus_data
    prompt_data = load_data(PROMPT_FILE_PATH)
    corpus_data = load_data(CORPUS_FILE_PATH)
    return jsonify({
        'success': True,
        'message': '数据已刷新'
    })

@app.route('/get_prompt_robustness_data', methods=['POST'])
def get_prompt_robustness_data():
    if request.method == 'POST':
        data = request.get_json()
        prompt_ids = data.get('prompt_ids', [])
        corpus_ids = data.get('corpus_ids', [])
        
        # print(f"接收到的prompt_ids: {prompt_ids}")
        # print(f"接收到的corpus_ids: {corpus_ids}")

        # 计算所有离散特征的鲁棒性值
        robustness_results = calculate_prompt_robustness(prompt_ids, corpus_ids)
        
        return jsonify({
            "robustness_values": robustness_results
        })

@app.route('/get_corpus_robustness_data', methods=['GET', 'POST'])
def get_corpus_robustness_data():
    if request.method == 'POST':
        data = request.get_json()
        prompt_ids = data.get('prompt_ids', [])
        corpus_ids = data.get('corpus_ids', [])
        
        # print(f"接收到的prompt_ids: {prompt_ids}")
        # print(f"接收到的corpus_ids: {corpus_ids}")

        # 计算所有离散特征的鲁棒性值
        robustness_results = calculate_corpus_robustness(prompt_ids, corpus_ids)
        
        return jsonify({
            "robustness_values": robustness_results
        })
    
@app.route('/get_feature_correlations', methods=['POST'])
def get_feature_correlations():
    """计算特征与鲁棒性的相关性"""
    try:
        data = request.get_json()
        data_source_type = data.get('dataSourcetype', 'prompt')  # 默认处理prompt特征
        prompt_ids = data.get('prompt_ids', [])
        corpus_ids = data.get('corpus_ids', [])
        
        # 数据校验
        if not prompt_ids and not corpus_ids:
            return jsonify({'success': False, 'error': '必须提供prompt_ids或corpus_ids'})
        
        # 预处理ID列表
        prompt_id_set = set(map(int, prompt_ids))
        corpus_id_set = set(map(int, corpus_ids))
        
        print(f"要处理的数据来源类型: {data_source_type}")
        # 根据请求类型选择处理逻辑
        if data_source_type == 'prompt':
            return handle_prompt_features(prompt_id_set, corpus_id_set)
        elif data_source_type == 'corpus':
            return handle_corpus_features(prompt_id_set, corpus_id_set)
        else:
            return jsonify({'success': False, 'error': f'未知的dataSourceType: {data_source_type}'})
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            # 'traceback': traceback.format_exc()
        }), 500

def handle_prompt_features(prompt_id_set, corpus_id_set):
    """处理prompt特征相关性计算"""
    # 计算prompt的平均鲁棒性
    robustness_map = defaultdict(list)
    for res in final_results:
        if res['prompt_id'] in prompt_id_set and res['corpus_id'] in corpus_id_set:
            robustness_map[res['prompt_id']].append(res['accuracy'])
    
    prompt_robustness = {
        pid: np.mean(accuracies) if accuracies else None
        for pid, accuracies in robustness_map.items()
    }
    
    # 准备prompt特征数据
    prompt_features_filtered = [
        pf for pf in prompt_features 
        if pf['id'] in prompt_id_set
    ]
    
    # 计算prompt特征相关性
    prompt_results = calculate_feature_correlations(
        prompt_features_filtered, 
        prompt_robustness,
        DISCRETE_FEATURES,
        PROMPT_FEATURE_DIMENSIONS,
        CONTINUOUS_FEATURES
    )
    
    return jsonify({
        'success': True,
        'data_source_type': 'prompt',
        'correlations': prompt_results
    })

def handle_corpus_features(prompt_id_set, corpus_id_set):
    """处理corpus特征相关性计算"""
    # 计算corpus的平均鲁棒性
    robustness_map = defaultdict(list)
    for res in final_results:
        if res['prompt_id'] in prompt_id_set and res['corpus_id'] in corpus_id_set:
            robustness_map[res['corpus_id']].append(res['accuracy'])
    
    corpus_robustness = {
        cid: np.mean(accuracies) if accuracies else None
        for cid, accuracies in robustness_map.items()
    }
    
    # 准备corpus特征数据
    corpus_features_filtered = [
        cf for cf in corpus_features 
        if cf['id'] in corpus_id_set
    ]
    
    # 计算corpus特征相关性
    corpus_results = calculate_feature_correlations(
        corpus_features_filtered,
        corpus_robustness,
        CORPUS_DISCRETE_FEATURES,
        CORPUS_FEATURE_DIMENSIONS,
        CORPUS_CONTINUOUS_FEATURES
    )
    
    return jsonify({
        'success': True,
        'data_source_type': 'corpus',
        'correlations': corpus_results
    })

def calculate_feature_correlations(features, robustness_map, discrete_feats, discrete_dims, continuous_feats):
    """通用特征相关性计算函数"""
    results = {'discrete': {}, 'continuous': {}}
    
    # 离散特征计算
    for feat_name, value_map in discrete_feats.items():
        feat_idx = discrete_dims[feat_name]
        groups = defaultdict(list)
        
        for feat in features:
            if feat['id'] in robustness_map:
                value = feat['vector'][feat_idx]
                if value in value_map:
                    groups[value].append(robustness_map[feat['id']])
        
        # 计算ANOVA
        if len(groups) >= 2:
            f_val, p_val = stats.f_oneway(*[np.array(x) for x in groups.values()])
            eta_sq = f_val / (f_val + (len(features) - len(groups)))
            results['discrete'][feat_name] = {
                'effect_size': eta_sq,
                'p_value': p_val,
                'method': 'ANOVA'
            }
    
    # 连续特征计算
    for feat_name, config in continuous_feats.items():
        feat_idx = config['index']
        x = []
        y = []
        
        for feat in features:
            if feat['id'] in robustness_map:
                x_val = feat['vector'][feat_idx]
                if not np.isnan(x_val):
                    x.append(x_val)
                    y.append(robustness_map[feat['id']])
        
        if len(x) >= 2:
            # 计算Spearman
            rho, p_val = stats.spearmanr(x, y)
            results['continuous'][feat_name] = {
                'correlation': rho,
                'p_value': p_val,
                'method': 'Spearman'
            }
    
    return results

@app.route('/api/filter_by_features', methods=['POST'])
def filter_by_features():
    try:
        data = request.get_json()
        selected_features = data.get('selectedFeatures', {})
        data_source = data.get('dataSource', 'prompt')  # 'prompt' 或 'corpus'
        print(f"筛选的数据来源: {data_source}")
        print(f"筛选的特征: {selected_features}")
        
        # 获取所有ID
        all_ids = set()
        if data_source == 'prompt':
            all_ids = {pf['id'] for pf in prompt_features}
            feature_dimensions = PROMPT_FEATURE_DIMENSIONS
            continuous_features = CONTINUOUS_FEATURES
            feature_data = prompt_features
        else:
            all_ids = {cf['id'] for cf in corpus_features}
            feature_dimensions = CORPUS_FEATURE_DIMENSIONS
            continuous_features = CORPUS_CONTINUOUS_FEATURES
            feature_data = corpus_features
        
        # 存储每个特征的匹配ID集合
        feature_matches = defaultdict(set)
        
        # 遍历每个选择的条件
        for feature in selected_features:
            feature_name = feature['featureName']
            value_range = feature['valueRange']
            is_continuous = feature['isContinuous']
            
            # 获取特征索引
            if is_continuous:
                feature_index = continuous_features[feature_name]['index']
            else:
                feature_index = feature_dimensions[feature_name]
            
            print(f"\n处理特征 {feature_name}, 维度索引: {feature_index}")
            
            # 处理连续特征
            if is_continuous:
                min_val, max_val = map(float, value_range.split('-'))
                matching_ids = set()
                for item in feature_data:
                    feature_value = item['vector'][feature_index]
                    if min_val <= feature_value < max_val:
                        matching_ids.add(item['id'])
                print(f"连续特征 {feature_name} 在范围 {value_range} 内找到 {len(matching_ids)} 个匹配项")
                if len(matching_ids) > 0:
                    print(f"匹配的ID示例: {sorted(list(matching_ids))[:5]}")  # 只显示前5个ID
            # 处理离散特征
            else:
                # 获取特征值映射
                if data_source == 'prompt':
                    value_map = DISCRETE_FEATURES[feature_name]
                else:
                    value_map = CORPUS_DISCRETE_FEATURES[feature_name]
                
                # 将文本描述映射到数值
                value = None
                for num, text in value_map.items():
                    if text == value_range:
                        value = num
                        break
                
                if value is None:
                    print(f"警告：特征 {feature_name} 的值 {value_range} 没有找到对应的数值映射")
                    continue
                
                matching_ids = set()
                for item in feature_data:
                    if item['vector'][feature_index] == value:
                        matching_ids.add(item['id'])
                print(f"离散特征 {feature_name} 值 {value_range} (数值: {value}) 找到 {len(matching_ids)} 个匹配项")
                if len(matching_ids) > 0:
                    print(f"匹配的ID示例: {sorted(list(matching_ids))[:5]}")  # 只显示前5个ID
            
            # 存储这个特征的匹配结果（使用集合的并集）
            feature_matches[feature_name].update(matching_ids)
        
        # 计算所有特征的交集
        if feature_matches:
            filtered_ids = set.intersection(*feature_matches.values())
            print(f"\n所有特征的交集结果:")
            print(f"最终筛选出的ID数量: {len(filtered_ids)}")
            if filtered_ids:
                print(f"筛选出的ID: {sorted(list(filtered_ids))}")
        else:
            filtered_ids = set()
            print("没有提供任何特征条件")
        
        # 转换为列表并排序
        result_ids = sorted(list(filtered_ids))
        
        return jsonify({
            'success': True,
            'filtered_ids': result_ids
        })
        
    except Exception as e:
        print(f"筛选过程出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)

















    <template>
  <div class="main-layout">
    <!-- 顶部：prompt特征图 -->
    <div class="top-feature">
      <div class="feature-container" data-container="prompt" style="width: 100vw;">
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
    <!-- 中间内容区 -->
    <div class="middle-row">
      <!-- 左侧：选择状态 -->
      <div class="left-status">
        <div class="prompt-status">
          <div class="section-header">
            <h3>prompt选择状态</h3>
            <div class="button-group">
              <button 
                @click="submitFeatures('prompt')" 
                class="icon-btn"
                :disabled="!selectedFeatures.prompt.length"
                :title="'提交选择'">
                <el-icon><Check /></el-icon>
              </button>
              <button 
                @click="clearFeatures('prompt')" 
                class="icon-btn"
                :disabled="!selectedFeatures.prompt.length"
                :title="'清空Prompt'">
                <el-icon><Delete /></el-icon>
              </button>
            </div>
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
        <div class="corpus-status">
          <div class="section-header">
            <h3>corpus选择状态</h3>
            <div class="button-group">
              <button 
                @click="submitFeatures('corpus')" 
                class="icon-btn"
                :disabled="!selectedFeatures.corpus.length"
                :title="'提交选择'">
                <el-icon><Check /></el-icon>
              </button>
              <button 
                @click="clearFeatures('corpus')" 
                class="icon-btn"
                :disabled="!selectedFeatures.corpus.length"
                :title="'清空Corpus'">
                <el-icon><Delete /></el-icon>
              </button>
            </div>
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
      <!-- 中间：空白 -->
      <div class="center-blank">
        <div class="blank-content"></div>
      </div>
      <!-- 右侧：列表 -->
      <div class="right-list horizontal-lists">
        <div class="prompt-list horizontal-list-item">
          <div class="list-header">
            <h2>prompt列表</h2>
            <button class="sort-btn" @click="cyclePromptSort" :title="promptSortState==='robustnessDesc'?'鲁棒性降序':promptSortState==='robustnessAsc'?'鲁棒性升序':'ID排序'">
              <el-icon>
                <Sort v-if="promptSortState==='robustnessDesc'" />
                <Sort v-else-if="promptSortState==='robustnessAsc'" style="transform:rotate(180deg)" />
                <Sort v-else style="color:#bbb" />
              </el-icon>
            </button>
          </div>
          <div v-if="currentPrompts.length === 0" class="empty-state">
            <p>加载中...</p>
          </div>
          <div v-else class="scrollable-list">
            <div v-for="item in sortedPrompts" :key="item.id" class="list-item row-flex">
              <div class="item-id">ID: {{ item.id }}</div>
              <div class="item-content">{{ item.text }}</div>
              <div class="item-robustness" :style="robustnessColorStyle(item.robustness)">{{ item.robustness.toFixed(4) }}</div>
            </div>
          </div>
        </div>
        <div class="corpus-list horizontal-list-item">
          <div class="list-header">
            <h2>corpus列表</h2>
            <button class="sort-btn" @click="cycleCorpusSort" :title="corpusSortState==='robustnessDesc'?'鲁棒性降序':corpusSortState==='robustnessAsc'?'鲁棒性升序':'ID排序'">
              <el-icon>
                <Sort v-if="corpusSortState==='robustnessDesc'" />
                <Sort v-else-if="corpusSortState==='robustnessAsc'" style="transform:rotate(180deg)" />
                <Sort v-else style="color:#bbb" />
              </el-icon>
            </button>
          </div>
          <div v-if="currentCorpus.length === 0" class="empty-state">
            <p>加载中...</p>
          </div>
          <div v-else class="scrollable-list">
            <div v-for="item in sortedCorpus" :key="item.id" class="list-item row-flex">
              <div class="item-id">ID: {{ item.id }}</div>
              <div class="item-content">{{ item.text }}</div>
              <div class="item-robustness" :style="robustnessColorStyle(item.robustness)">{{ item.robustness.toFixed(4) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 底部：corpus特征图 -->
    <div class="bottom-feature">
      <div class="feature-container" data-container="corpus" style="width: 100vw;">
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
  </div>
</template>

<script setup>
import * as d3 from 'd3'
import { ref, onMounted,  watch,nextTick, computed } from 'vue'
import { toRaw } from 'vue'
import { Sort, Check, Delete } from '@element-plus/icons-vue'

// 图表尺寸常量
const chartWidth =150
const chartHeight = 200
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

const promptSortState = ref('id') // 'id' | 'robustnessDesc' | 'robustnessAsc'
const corpusSortState = ref('id')

const sortedPrompts = computed(() => {
  if (promptSortState.value === 'robustnessDesc') {
    return [...currentPrompts.value].sort((a, b) => b.robustness - a.robustness)
  } else if (promptSortState.value === 'robustnessAsc') {
    return [...currentPrompts.value].sort((a, b) => a.robustness - b.robustness)
  } else {
    return [...currentPrompts.value].sort((a, b) => a.id - b.id)
  }
})
const sortedCorpus = computed(() => {
  if (corpusSortState.value === 'robustnessDesc') {
    return [...currentCorpus.value].sort((a, b) => b.robustness - a.robustness)
  } else if (corpusSortState.value === 'robustnessAsc') {
    return [...currentCorpus.value].sort((a, b) => a.robustness - b.robustness)
  } else {
    return [...currentCorpus.value].sort((a, b) => a.id - b.id)
  }
})

function cyclePromptSort() {
  if (promptSortState.value === 'id') promptSortState.value = 'robustnessDesc'
  else if (promptSortState.value === 'robustnessDesc') promptSortState.value = 'robustnessAsc'
  else promptSortState.value = 'id'
}
function cycleCorpusSort() {
  if (corpusSortState.value === 'id') corpusSortState.value = 'robustnessDesc'
  else if (corpusSortState.value === 'robustnessDesc') corpusSortState.value = 'robustnessAsc'
  else corpusSortState.value = 'id'
}

function createChart(svgElement, featureName, featureData, isContinuous,dataSource) {
  console.log(dataSource)
  const margin = { top: 10, right: 10, bottom: 10, left: 20 };
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

  let displayData, y;
  // let displayData, y, yTicks;

  if (isContinuous) {
    // 连续特征处理
    const values = featureData.values.map(d => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const step = (max - min) / 10;

    // 构造10个区间
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

    // y为线性比例尺
    // yTicks = d3.range(min, max + step, step);
    
    y = d3.scaleLinear()
      .domain([min, max])
      .range([margin.top, margin.top + innerHeight]);
  } else {
    // 离散特征处理
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

  // 计算鲁棒性最小值和最大值
  const robustnessValues = displayData.map(d => d.robustness);
  const minRobustness = Math.min(...robustnessValues);
  const maxRobustness = Math.max(...robustnessValues);

  // 鲁棒性条形图比例尺：下界为minRobustness，上界为maxRobustness
  const xRobustness = d3.scaleLinear()
    .domain([minRobustness, maxRobustness])
    .range([0, innerWidth / 2 - 10]);

  // 添加Y轴
  // svg.append("g")
  //   .attr("class", "y-axis")
  //   .attr("transform", `translate(${margin.left},0)`)
  //   .call(
  //     isContinuous
  //       ? d3.axisLeft(y).tickValues(yTicks).tickFormat(d => d.toFixed(1))
  //       : d3.axisLeft(y)
  //   )
  //   .selectAll("text")
  //   .style("text-anchor", "middle")
  //   .attr("dx", "-2px")
  //   .style("font-size", "15px");

  const barPadding = 4;

  // 添加交互功能到左侧条形图
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
    .attr('data-source', dataSource)  // 新增
    .attr('data-feature', featureName) // 新增
    .attr('data-range', d => {
        // 统一转为保留两位小数的格式
        if (isContinuous) {
          return `${Number(d.start).toFixed(2)}-${Number(d.end).toFixed(2)}`;
        }
        return String(d.label).trim(); // 离散值去除首尾空格
      })
    .on("mouseover", function(event, d) {
      // 高亮当前条形
      d3.select(this)
        .attr("opacity", 1)
        .attr("stroke", "#333")
        .attr("stroke-width", 1.5);

      // 显示工具提示
      tooltip.transition()
        .duration(200)
        .style("opacity", .9);
      tooltip.html(`
        <div><strong>区间:</strong> ${isContinuous ? `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : d.label}</div>
        <div><strong>数量:</strong> ${d.count}</div>
        <div><strong>鲁棒性:</strong> ${d.robustness.toFixed(4)}</div>
      `)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");
    })
    .on("mouseout", function() {
      // 获取当前条形对应的数据
      const d = d3.select(this).datum();
      
      // 计算当前条形的值范围（与点击逻辑一致）
      const valueRange = isContinuous ? 
        `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : 
        d.label || d.value_name;
      
      // 检查是否已被选中
      const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
      
      // 只有未选中的条形才恢复默认样式
      if (!isSelected) {
        d3.select(this)
          .attr("opacity", 0.7)
          .attr("stroke", "none");
      }
      
      // 无论是否选中都隐藏工具提示
      tooltip.transition()
        .duration(500)
        .style("opacity", 0);
    })
    .on("click", function(event, d) {
      handleBarClick(d);

    });
    

  // 添加交互功能到右侧条形图
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
    .attr('data-source', dataSource)  // 新增
    .attr('data-feature', featureName) // 新增
    .attr('data-range', d => {
      // 统一转为保留两位小数的格式
      if (isContinuous) {
        return `${Number(d.start).toFixed(2)}-${Number(d.end).toFixed(2)}`;
      }
      return String(d.label).trim(); // 离散值去除首尾空格
    })// 新增
    .on("mouseover", function(event, d) {
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
        <div><strong>鲁棒性:</strong> ${d.robustness.toFixed(4)}</div>
      `)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 28) + "px");
    })
    .on("mouseout", function() {
      // 获取当前条形对应的数据
      const d = d3.select(this).datum();
      
      // 计算当前条形的值范围（与点击逻辑一致）
      const valueRange = isContinuous ? 
        `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : 
        d.label || d.value_name;
      
      // 检查是否已被选中
      const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
      
      // 只有未选中的条形才恢复默认样式
      if (!isSelected) {
        d3.select(this)
          .attr("opacity", 0.7)
          .attr("stroke", "none");
      }
      
      // 无论是否选中都隐藏工具提示
      tooltip.transition()
        .duration(500)
        .style("opacity", 0);
    })
    .on("click", function(event, d) {
      handleBarClick(d);

    });

  // 添加中线
  svg.append("line")
    .attr("x1", margin.left + innerWidth / 2)
    .attr("x2", margin.left + innerWidth / 2)
    .attr("y1", margin.top)
    .attr("y2", margin.top + innerHeight)
    .attr("stroke", "#999")
    .attr("stroke-width", 1)
    .attr("stroke-dasharray", "2,2");

  // 临时添加检查函数

  // 更新条形图的绘制逻辑，添加高亮状态
  const updateBarBorders = () => {
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
  };

  // 修改点击事件处理
  const handleBarClick = (d) => {
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
  
  // 必须这样赋值才能触发响应式更新
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
          robustness: d.robustness.toFixed(6)
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
  updateBarBorders();
};

  updateBarBorders();
}


// 修改后的初始化图表函数
async function initChartsWithDataAttribute() {
  // 等待 Vue 完成 DOM 更新
  await nextTick()
  
  console.log('开始初始化图表...')
  
  // Prompt 特征图表
  if (distributionData.value) {1
    const dataSource = 'prompt'
    console.log("处理 Prompt 数据:", distributionData.value)
    
    const promptContainer = document.querySelector('[data-container="prompt"]')
    console.log("Prompt 容器:", promptContainer)
    
    if (promptContainer) {
      const svgs = promptContainer.querySelectorAll('.feature-chart svg')
      console.log("找到的 Prompt SVG 元素数量:", svgs.length)
      
      let index = 0
      
      // 连续特征
      Object.entries(distributionData.value.continuous || {}).forEach(([featureName, featureData]) => {
        // console.log(`处理 Prompt 连续特征 ${featureName}, index: ${index}`)
        if (svgs[index]) {
          createChart(svgs[index], featureName, featureData, true,dataSource)
          index++
        } else {
          console.warn(`Prompt 连续特征 ${featureName} 没有找到对应的 SVG 元素`)
        }
      })
      
      // 离散特征
      Object.entries(distributionData.value.discrete || {}).forEach(([featureName, featureData]) => {
        // console.log(`处理 Prompt 离散特征 ${featureName}, index: ${index}`)
        if (svgs[index]) {
          createChart(svgs[index], featureName, featureData, false,dataSource)
          index++
        } else {
          console.warn(`Prompt 离散特征 ${featureName} 没有找到对应的 SVG 元素`)
        }
      })
    }
  }
  
  // Corpus 特征图表
  if (distributionDataCorpus.value) {
    const dataSource = 'corpus'
    console.log("处理 Corpus 数据:", distributionDataCorpus.value)
    
    const corpusContainer = document.querySelector('[data-container="corpus"]')
    console.log("Corpus 容器:", corpusContainer)
    
    if (corpusContainer) {
      const svgs = corpusContainer.querySelectorAll('.feature-chart svg')
      console.log("找到的 Corpus SVG 元素数量:", svgs.length)
      
      let index = 0
      
      // 连续特征
      Object.entries(distributionDataCorpus.value.continuous || {}).forEach(([featureName, featureData]) => {
        // console.log(`处理 Corpus 连续特征 ${featureName}, index: ${index}`)
        if (svgs[index]) {
          createChart(svgs[index], featureName, featureData, true,dataSource)
          index++
        } else {
          console.warn(`Corpus 连续特征 ${featureName} 没有找到对应的 SVG 元素`)
        }
      })
      
      // 离散特征
      Object.entries(distributionDataCorpus.value.discrete || {}).forEach(([featureName, featureData]) => {
        // console.log(`处理 Corpus 离散特征 ${featureName}, index: ${index}`)
        if (svgs[index]) {
          createChart(svgs[index], featureName, featureData, false,dataSource)
          index++
        } else {
          console.warn(`Corpus 离散特征 ${featureName} 没有找到对应的 SVG 元素`)
        }
      })
    }
  }
}
// const continuousFeatures = new Set([
//   '语义模糊度', '语法复杂度', '词汇复杂度', '歧义性',
//   '困惑度', '语言流畅性', '情感刺激性', '无关信息量','长度','冗余度','极性词数量','词汇多样性','标点','特殊字符','模糊性','否定词含量'
// ])

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
// 安全查询DOM元素
// function safeQuery(selector) {
//   const elements = document.querySelectorAll(selector);
//   return Array.from(elements).filter(el => el !== null);
// }
// 添加重试函数
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // 指数退避
    }
  }
}

// 修改数据获取方法
async function fetchTextData() {
  try {
    const promptData = await fetchWithRetry('http://127.0.0.1:5000/get_prompt_data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: promptIds.value })
    });
    currentPrompts.value = promptData.prompt || [];
    console.log('更新后的 prompts:', currentPrompts.value);
    
    const corpusData = await fetchWithRetry('http://127.0.0.1:5000/get_corpus_data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: corpusIds.value })
    });
    currentCorpus.value = corpusData.corpus || [];
    console.log('更新后的 corpus:', currentCorpus.value);
  } catch (error) {
    console.error('数据获取失败:', error);
    // 设置默认值
    currentPrompts.value = [];
    currentCorpus.value = [];
  }
}

async function fetchFeatureDistribution() {
  try {
    const data = await fetchWithRetry('http://127.0.0.1:5000/api/prompt_feature_distribution', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt_ids: promptIds.value,
        corpus_ids: corpusIds.value
      })
    });
    distributionData.value = data.distribution;
    console.log("更新后的 prompt 特征分布数据：", distributionData.value);
  } catch (error) {
    console.error('获取特征分布失败:', error);
    distributionData.value = null;
  }
}

async function fetchCorpusFeatureDistribution() {
  try {
    const data = await fetchWithRetry('http://127.0.0.1:5000/api/corpus_feature_distribution', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt_ids: promptIds.value,
        corpus_ids: corpusIds.value
      })
    });
    distributionDataCorpus.value = data.distribution;
    console.log("更新后的 corpus 特征分布数据：", distributionDataCorpus.value);
  } catch (error) {
    console.error('获取特征分布失败:', error);
    distributionDataCorpus.value = null;
  }
}

// 修改监听器，使用 nextTick
watch([distributionData, distributionDataCorpus], async () => {
  console.log('数据变化，准备重新初始化图表')
  // 等待一小段时间确保 DOM 完全更新
  await new Promise(resolve => setTimeout(resolve, 100))
  await initChartsWithDataAttribute()
}, { deep: true })

// 修改组件挂载逻辑
onMounted(async () => {
  console.log('组件挂载完成')
  
  try {
    await Promise.all([
      fetchTextData(),
      fetchFeatureDistribution(),
      fetchCorpusFeatureDistribution()
    ])
    
    console.log('数据获取完成')
    
    // 确保数据加载完成后再初始化图表
    await new Promise(resolve => setTimeout(resolve, 200))
    await initChartsWithDataAttribute()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

const submitFeatures = async (dataSource) => {
  const rawData = toRaw(selectedFeatures.value[dataSource]);
  console.log(`${dataSource} 当前选择状态:`, rawData);
  
  try {
    const response = await fetch('http://127.0.0.1:5000/api/filter_by_features', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        selectedFeatures: rawData,
        dataSource: dataSource
      })
    });
    
    const result = await response.json();
    if (result.success) {
      console.log(`筛选后的${dataSource} IDs:`, result.filtered_ids);
      
      // 更新对应的ID列表
      if (dataSource === 'prompt') {
        promptIds.value = result.filtered_ids;
        console.log('更新后的 promptIds:', promptIds.value);
      } else {
        corpusIds.value = result.filtered_ids;
        console.log('更新后的 corpusIds:', corpusIds.value);
      }
      
      // 重新获取特征分布数据
      await Promise.all([
        fetchFeatureDistribution(),
        fetchCorpusFeatureDistribution()
      ]);
      
      // 重新获取文本数据
      await fetchTextData();
      
      console.log('数据更新完成');
    } else {
      console.error('筛选失败:', result.error);
    }
  } catch (error) {
    console.error('请求失败:', error);
  }
};

// 鲁棒性染色函数：0.6及以上蓝色，以下红色，线性插值
function robustnessColorStyle(val) {
  let color = ''
  if (val >= 0.6) {
    // 蓝色区间：#b3d1ff(浅) ~ #0047ab(深)
    const t = (val - 0.6) / 0.4
    color = interpolateColor('#b3d1ff', '#0047ab', t)
  } else {
    // 红色区间：#ffd6d6(浅) ~ #b22222(深)
    const t = (0.6 - val) / 0.6
    color = interpolateColor('#ffd6d6', '#b22222', t)
  }
  return { color }
}

// 线性插值颜色
function interpolateColor(color1, color2, t) {
  // color1, color2: '#rrggbb', t: 0~1
  const c1 = [parseInt(color1.slice(1,3),16),parseInt(color1.slice(3,5),16),parseInt(color1.slice(5,7),16)]
  const c2 = [parseInt(color2.slice(1,3),16),parseInt(color2.slice(3,5),16),parseInt(color2.slice(5,7),16)]
  const c = c1.map((v,i)=>Math.round(v+(c2[i]-v)*t))
  return `rgb(${c[0]},${c[1]},${c[2]})`
}
</script>

<style scoped>
.main-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
}
.top-feature {
  flex: 0 0 250px;
  min-height: 250px;
  border-bottom: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
}
.bottom-feature {
  flex: 0 0 250px;
  min-height: 250px;
  border-top: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
}
.middle-row {
  flex: 1 1 auto;
  display: flex;
  flex-direction: row;
  min-height: 0;
  min-width: 0;
  height: 500px;
  max-height: 800px;
}
.left-status {
  flex: 0 0 300px;
  min-width: 300px;
  border-right: none;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
}
.prompt-status, .corpus-status {
  flex: 1 1 0;
  border-bottom: 1px solid #ddd;
  padding: 16px 8px;
  min-height: 120px;
  border: 1px solid #ddd;
}
.corpus-status {
  border-bottom: none;
}
.center-blank {
  flex: 1 1 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: none;
  border-left: none;
}
.blank-content {
  font-size: 28px;
  color: #222;
}
.right-list {
  flex: 0 0 1400px;
  min-width: 1400px;
  max-width: 1400px;
  display: flex;
  flex-direction: column;
}
.right-list.horizontal-lists {
  display: flex;
  flex-direction: row;
  width: 1400px;
  min-width: 1400px;
  max-width: 1400px;
  height: 100%;
  border: 1px solid #ddd;
  background: none;
}
.horizontal-list-item {
  flex: 1 1 0;
  min-width: 0;
  border-right: 1px solid #ddd;
  padding: 16px 8px;
  min-height: 120px;
  display: flex;
  flex-direction: column;
}
.horizontal-list-item:last-child {
  border-right: none;
}
.prompt-list, .corpus-list {
  flex: 1 1 0;
  border-bottom: 1px solid #ddd;
  padding: 16px 8px;
  min-height: 120px;
  min-width: 0;
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
}
.corpus-list {
  border-bottom: none;
}
.prompt-list.horizontal-list-item h2,
.corpus-list.horizontal-list-item h2 {
  margin: 0 0 8px 0;
  padding: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 16px;
}
/* 布局容器样式 */
.layout-container {
  display: flex;
  height: 100vh;
  width: 100%;
}



/* 桑基图区域样式 */
.sankey-section {
  flex: 1;
  margin: 4px;
  background-color: white;
  display: flex;
  flex-direction: column;
  /* border: 1px solid #999; */
}

/* 特征图表容器样式 */
.feature-container {
  width: 2200px;
  height: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  margin: 10px;
}
.feature-control {
  width: 2200px;
  height: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  margin-left: 10px;
  margin-right: 10px;
}

.scroll-container {
  width: 100%;
  height: 100%;
  /* overflow-x: auto; */
  /* overflow-y: hidden; */
  scroll-behavior: smooth;
}

.feature-charts {
  display: flex;
  flex-wrap: wrap; /* 允许自动换行 */
  height: 100%;
  width: 100%;
  padding: 2px;
}

.feature-chart {
  flex: 0 0 auto;
  width: 150px;
  height: 200px;
  margin-right: 2px;
  margin-bottom: 10px; /* 新增：下方间距 */
  padding: 2px;
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

.button-group {
  display: flex;
  gap: 8px;
}

.icon-btn {
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 16px;
  color: #4e79a7;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-btn:disabled {
  color: #bbb;
  cursor: not-allowed;
  background: #f5f5f5;
}
.icon-btn:hover:not(:disabled) {
  background: #e3f0ff;
  color: #2c4c6b;
}
.icon-btn .el-icon {
  font-size: 18px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(90deg, #e3f0ff 0%, #f8faff 100%);
  border: 1.5px solid #4e79a7;
  border-radius: 18px;
  padding: 6px 14px 6px 16px;
  font-size: 14px;
  line-height: 1.2;
  box-shadow: 0 2px 8px rgba(78,121,167,0.08);
  margin-bottom: 6px;
  margin-right: 6px;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.feature-tag:hover {
  box-shadow: 0 4px 12px rgba(78,121,167,0.18);
  border-color: #2c4c6b;
}

.data-source-section:nth-child(2) .feature-tag,
.corpus-status .feature-tag {
  border-color: #e15759;
  background: linear-gradient(90deg, #ffeaea 0%, #fff8f8 100%);
}

.button-group button {
  border-radius: 6px;
  border: none;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 500;
  margin-left: 4px;
  transition: background 0.2s, color 0.2s;
}

.submit-btn {
  background: #4e79a7;
  color: #fff;
}

.submit-btn:hover:not(:disabled) {
  background: #2c4c6b;
}

.clear-btn {
  background: #f5f5f5;
  color: #e15759;
}

.clear-btn:hover:not(:disabled) {
  background: #ffeaea;
  color: #b12a34;
}

.section-header h3 {
  font-size: 16px;
  font-weight: bold;
  border-left: 4px solid #4e79a7;
  padding-left: 8px;
  margin-right: 8px;
  color: #222;
}

.corpus-status .section-header h3 {
  border-left-color: #e15759;
}

.section-header {
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 10px;
  padding-bottom: 4px;
}

.empty-state {
  color: #bbb;
  text-align: center;
  padding: 24px 0;
  font-style: italic;
  font-size: 15px;
  letter-spacing: 1px;
}

.prompt-status, .corpus-status {
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(78,121,167,0.04);
  border: 1px solid #e0e0e0;
  margin-bottom: 16px;
}

.feature-name {
  font-weight: bold;
  color: #222;
}

.value-range {
  color: #4e79a7;
  font-weight: 500;
}

.corpus-status .value-range {
  color: #e15759;
}

.stats {
  color: #888;
  font-size: 12px;
  margin-left: 4px;
}

.tag-remove {
  background: none;
  border: none;
  color: #bbb;
  cursor: pointer;
  font-size: 18px;
  margin-left: 8px;
  padding: 0 4px;
  transition: color 0.2s;
}

.tag-remove:hover {
  color: #e15759;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 400px;
  overflow-y: auto;
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

.top-feature .feature-container,
.bottom-feature .feature-container {
  width: 100vw !important;
  min-width: 100vw;
  max-width: 100vw;
}
.right-list.horizontal-lists {
  display: flex;
  flex-direction: row;
  width: 1400px;
  min-width: 1400px;
  max-width: 1400px;
  height: 100%;
  border: 1px solid #ddd;
  background: none;
}
.horizontal-list-item {
  flex: 1 1 0;
  min-width: 0;
  border-right: 1px solid #ddd;
  padding: 16px 8px;
  min-height: 120px;
  display: flex;
  flex-direction: column;
}
.horizontal-list-item:last-child {
  border-right: none;
}
.prompt-list.horizontal-list-item h2,
.corpus-list.horizontal-list-item h2 {
  margin: 0 0 8px 0;
  padding: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 16px;
}
.row-flex {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.item-content {
  flex: 1;
  padding-right: 16px;
}
.item-robustness {
  width: 80px;
  text-align: center;
  border-radius: 4px;
  background: #fff;
  font-weight: bold;
  font-family: monospace;
  font-size: 14px;
  transition: color 0.2s;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.sort-btn {
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  padding: 2px 6px;
  font-size: 16px;
  color: #4e79a7;
  cursor: pointer;
  margin-left: 8px;
  transition: background 0.2s, color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sort-btn:hover {
  background: #e3f0ff;
  color: #2c4c6b;
}
.sort-btn .el-icon {
  font-size: 18px;
}
.item-id {
  font-weight: bold;
  margin-right: 10px;
  color: #555;
  font-size: 12px;
  min-width: 60px;
}
</style>