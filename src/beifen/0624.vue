<template>
    <div class="main-layout">
      <div v-if="loading" class="loading-mask">
        <span>加载中...</span>
      </div>
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
                <!-- <button 
                  @click="submitFeatures('prompt')" 
                  class="icon-btn"
                  :disabled="!selectedFeatures.prompt.length"
                  :title="'提交选择'">
                  <el-icon><Check /></el-icon>
                </button> -->
                <button 
                  @click="clearFeatures('prompt')" 
                  class="icon-btn"
                  :disabled="!selectedFeatures.prompt.length"
                  :title="'清空Prompt'">
                  <el-icon><Delete /></el-icon>
                </button>
                <!-- <button 
                  @click="restoreInitialState('prompt')" 
                  class="icon-btn"
                  :disabled="!hasInitialState('prompt')"
                  :title="'恢复初始状态'">
                  <el-icon><Refresh /></el-icon>
                </button>
                <button 
                  @click="toggleHistoryPanel('prompt')" 
                  class="icon-btn"
                  :title="'历史记录'">
                  <el-icon><Timer /></el-icon>
                </button> -->
              </div>
            </div>
            <div class="status-container">
              <div class="main-status">
                <div v-if="selectedFeatures.prompt.length === 0" class="empty-state">
                  <p>点击Prompt图表中的条形以添加筛选条件</p>
                </div>
                <div v-else class="tags-container">
                  <div v-for="(featureGroup, featureName) in groupedPromptFeatures" 
                      :key="'prompt-'+featureName" 
                      class="feature-tag">
                    <div class="tag-header" @click="toggleFeatureDropdown('prompt', featureName)">
                      <span class="tag-content">
                        <span class="feature-name">{{ featureName }}</span>
                        <span class="feature-count">({{ featureGroup.length }})</span>
                      </span>
                      <span class="dropdown-icon" :class="{ 'open': openDropdowns.prompt[featureName] }">▼</span>
                    </div>
                    <div v-if="openDropdowns.prompt[featureName]" class="feature-dropdown">
                      <div v-for="(feature, index) in featureGroup" 
                          :key="'prompt-'+featureName+'-'+index" 
                          class="dropdown-item">
                        <span class="value-range">{{ feature.valueRange }}</span>
                        <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                        <button @click="removeFeature('prompt', getFeatureIndex('prompt', feature))" class="tag-remove">×</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="history-panel" :class="{ open: historyPanelOpen.prompt }">
                <div class="history-header">
                  <h4>历史记录</h4>
                  <button v-if="historyPanelOpen.prompt" class="close-history" @click="toggleHistoryPanel('prompt')">×</button>
                </div>
                <div class="history-list">
                  <div v-for="(record, index) in featureHistory.prompt"
                       :key="'prompt-history-'+index"
                       class="history-item">
                    <div class="history-main-row" @click="toggleHistoryDropdown('prompt', index)">
                      <span class="history-name">
                        <template v-if="editingHistoryName.prompt === index">
                          <input v-model="record.name"
                                 @blur="saveHistoryName('prompt', index, record.name)"
                                 @keyup.enter="saveHistoryName('prompt', index, record.name)"
                                 class="history-name-input" />
                        </template>
                        <template v-else>
                          {{ record.name || formatTime(record.timestamp) }}
                        </template>
                      </span>
                      <span class="history-count">{{ record.features.length }}个特征</span>
                      <button class="history-edit-btn" @click.stop="editHistoryName('prompt', index)">
                        <el-icon><Edit /></el-icon>
                      </button>
                      <button class="history-apply-btn"
                              @click.stop="applyHistoryRecord('prompt', index)"
                              :disabled="historyApplyLoading.prompt === index">
                        <el-icon v-if="historyApplyLoading.prompt === index"><Loading /></el-icon>
                        <el-icon v-else><Check /></el-icon>
                      </button>
                      <span class="dropdown-icon" :class="{ open: openHistoryDropdowns.prompt[index] }">▼</span>
                    </div>
                    <!-- 下拉内容单独块状显示 -->
                    <div v-if="openHistoryDropdowns.prompt[index]" class="history-dropdown-block">
                      <div v-for="(featureGroup, featureName) in groupFeatures(record.features)"
                           :key="'history-feature-'+featureName"
                           class="feature-tag">
                        <div class="tag-header" @click.stop="toggleHistoryFeatureDropdown('prompt', index, featureName)">
                          <span class="feature-name">{{ featureName }}</span>
                          <span class="feature-count">({{ featureGroup.length }})</span>
                          <span class="dropdown-icon" :class="{ open: openHistoryFeatureDropdowns.prompt[index]?.[featureName] }">▼</span>
                        </div>
                        <div v-if="openHistoryFeatureDropdowns.prompt[index]?.[featureName]" class="feature-dropdown">
                          <div v-for="(feature, idx) in featureGroup"
                               :key="'history-feature-'+featureName+'-'+idx"
                               class="dropdown-item">
                            <span class="value-range">{{ feature.valueRange }}</span>
                            <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="corpus-status">
            <div class="section-header">
              <h3>corpus选择状态</h3>
              <div class="button-group">
                <!-- <button 
                  @click="submitFeatures('corpus')" 
                  class="icon-btn"
                  :disabled="!selectedFeatures.corpus.length"
                  :title="'提交选择'">
                  <el-icon><Check /></el-icon>
                </button> -->
                <button 
                  @click="clearFeatures('corpus')" 
                  class="icon-btn"
                  :disabled="!selectedFeatures.corpus.length"
                  :title="'清空Corpus'">
                  <el-icon><Delete /></el-icon>
                </button>
                <!-- <button 
                  @click="restoreInitialState('corpus')" 
                  class="icon-btn"
                  :disabled="!hasInitialState('corpus')"
                  :title="'恢复初始状态'">
                  <el-icon><Refresh /></el-icon>
                </button>
                <button 
                  @click="toggleHistoryPanel('corpus')" 
                  class="icon-btn"
                  :title="'历史记录'">
                  <el-icon><Timer /></el-icon>
                </button> -->
              </div>
            </div>
            <div class="status-container">
              <div class="main-status">
                <div v-if="selectedFeatures.corpus.length === 0" class="empty-state">
                  <p>点击Corpus图表中的条形以添加筛选条件</p>
                </div>
                <div v-else class="tags-container">
                  <div v-for="(featureGroup, featureName) in groupedCorpusFeatures" 
                      :key="'corpus-'+featureName" 
                      class="feature-tag">
                    <div class="tag-header" @click="toggleFeatureDropdown('corpus', featureName)">
                      <span class="tag-content">
                        <span class="feature-name">{{ featureName }}</span>
                        <span class="feature-count">({{ featureGroup.length }})</span>
                      </span>
                      <span class="dropdown-icon" :class="{ 'open': openDropdowns.corpus[featureName] }">▼</span>
                    </div>
                    <div v-if="openDropdowns.corpus[featureName]" class="feature-dropdown">
                      <div v-for="(feature, index) in featureGroup" 
                          :key="'corpus-'+featureName+'-'+index" 
                          class="dropdown-item">
                        <span class="value-range">{{ feature.valueRange }}</span>
                        <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                        <button @click="removeFeature('corpus', getFeatureIndex('corpus', feature))" class="tag-remove">×</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="history-panel" :class="{ 'open': historyPanelOpen.corpus }">
                <div class="history-header">
                  <h4>历史记录</h4>
                  <button class="close-history" @click="toggleHistoryPanel('corpus')">×</button>
                </div>
                <div class="history-list">
                  <div v-for="(record, index) in featureHistory.corpus"
                       :key="'corpus-history-'+index"
                       class="history-item"
                       @click="restoreHistoryState('corpus', index)">
                    <span class="history-time">{{ formatTime(record.timestamp) }}</span>
                    <span class="history-count">{{ record.features.length }}个特征</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 中间：空白 -->
        <div class="center-blank">
          <div class="global-section-header">
            <h3>选择状态</h3>
            <div class="button-group">
              <button class="icon-btn" @click="submitAllFeatures" :disabled="!selectedFeatures.prompt.length && !selectedFeatures.corpus.length || loading">
                <el-icon v-if="!loading"><Check /></el-icon>
                <el-icon v-else><Loading /></el-icon>
                提交选择
              </button>
              <button class="icon-btn" @click="clearAllFeatures" :disabled="(!selectedFeatures.prompt.length && !selectedFeatures.corpus.length) || loading">
                <el-icon><Delete /></el-icon>
                清空
              </button>
              <button class="icon-btn" @click="restoreInitialStateAll" :disabled="loading">
                <el-icon><Refresh /></el-icon>
                恢复初始状态
              </button>
              <button class="icon-btn" @click="toggleHistoryPanelGlobal" :disabled="loading">
                <el-icon><Timer /></el-icon>
                历史记录
              </button>
            </div>
          </div>
          <div class="blank-content"></div>
        </div>
        <div v-if="globalHistoryPanelOpen" class="global-history-panel-side">
          <div class="history-header">
            <h4>历史记录</h4>
            <button class="close-history" @click="toggleHistoryPanelGlobal">×</button>
          </div>
          <div class="history-list">
            <div v-for="(record, index) in globalFeatureHistory"
                 :key="'global-history-'+index"
                 class="history-item">
              <div class="history-main-row" @click="toggleGlobalHistoryDropdown(index)">
                <span class="history-name">
                  <template v-if="editingGlobalHistoryName === index">
                    <input v-model="record.name"
                           @blur="saveGlobalHistoryName(index, record.name)"
                           @keyup.enter="saveGlobalHistoryName(index, record.name)"
                           class="history-name-input" />
                  </template>
                  <template v-else>
                    {{ record.name || formatTime(record.timestamp) }}
                  </template>
                </span>
                <span class="history-count">Prompt: {{ record.features.promptFeatures.length }}，Corpus: {{ record.features.corpusFeatures.length }}</span>
                <button class="history-edit-btn" @click.stop="editGlobalHistoryName(index)">
                  <el-icon><Edit /></el-icon>
                </button>
                <button class="history-apply-btn"
                        @click.stop="applyGlobalHistoryRecord(index)"
                        :disabled="globalHistoryApplyLoading === index">
                  <el-icon v-if="globalHistoryApplyLoading === index"><Loading /></el-icon>
                  <el-icon v-else><Check /></el-icon>
                </button>
                <span class="dropdown-icon" :class="{ open: openGlobalHistoryDropdowns[index] }">▼</span>
              </div>
              <div v-if="openGlobalHistoryDropdowns[index]" class="history-dropdown-block">
                <div class="history-type-block">
                  <div class="history-type-title">Prompt特征</div>
                  <div v-for="(featureGroup, featureName) in groupFeatures(record.features.promptFeatures)"
                       :key="'global-history-prompt-'+featureName"
                       class="feature-tag">
                    <div class="tag-header" @click.stop="toggleGlobalHistoryFeatureDropdown(index, 'prompt', featureName)">
                      <span class="feature-name">{{ featureName }}</span>
                      <span class="feature-count">({{ featureGroup.length }})</span>
                      <span class="dropdown-icon" :class="{ open: openGlobalHistoryFeatureDropdowns[index]?.prompt?.[featureName] }">▼</span>
                    </div>
                    <div v-if="openGlobalHistoryFeatureDropdowns[index]?.prompt?.[featureName]" class="feature-dropdown">
                      <div v-for="(feature, idx) in featureGroup"
                           :key="'global-history-prompt-'+featureName+'-'+idx"
                           class="dropdown-item">
                        <span class="value-range">{{ feature.valueRange }}</span>
                        <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="history-type-block">
                  <div class="history-type-title">Corpus特征</div>
                  <div v-for="(featureGroup, featureName) in groupFeatures(record.features.corpusFeatures)"
                       :key="'global-history-corpus-'+featureName"
                       class="feature-tag">
                    <div class="tag-header" @click.stop="toggleGlobalHistoryFeatureDropdown(index, 'corpus', featureName)">
                      <span class="feature-name">{{ featureName }}</span>
                      <span class="feature-count">({{ featureGroup.length }})</span>
                      <span class="dropdown-icon" :class="{ open: openGlobalHistoryFeatureDropdowns[index]?.corpus?.[featureName] }">▼</span>
                    </div>
                    <div v-if="openGlobalHistoryFeatureDropdowns[index]?.corpus?.[featureName]" class="feature-dropdown">
                      <div v-for="(feature, idx) in featureGroup"
                           :key="'global-history-corpus-'+featureName+'-'+idx"
                           class="dropdown-item">
                        <span class="value-range">{{ feature.valueRange }}</span>
                        <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
  import { Sort, Check, Delete, Refresh, Timer, Edit, Loading } from '@element-plus/icons-vue'
  
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
  const removeFeature = async (dataSource, index) => {
    loading.value = true
    const feature = selectedFeatures.value[dataSource][index];
    const key = `${feature.featureName}-${feature.valueRange}`;
    delete barBorders.value[dataSource][key];
    selectedFeatures.value[dataSource].splice(index, 1);
    // 精准更新（只需更新被移除的特征）
    updateChartBorders(dataSource, feature.featureName, feature.valueRange);
    loading.value = false
  }
  
  // 修改后的clearFeatures
  const clearFeatures = async (dataSource, setLoading = true) => {
    if (setLoading) loading.value = true
    barBorders.value = { ...barBorders.value, [dataSource]: {} }
    selectedFeatures.value = { ...selectedFeatures.value, [dataSource]: [] }
    // 全量更新当前数据源
    document.querySelectorAll(`.feature-container[data-container="${dataSource}"] svg`)
      .forEach(svg => {
        d3.select(svg).selectAll(".bar-count, .bar-robustness")
          .attr("stroke", "none")
          .attr("opacity", 0.7)
          .attr("stroke-width", 0)
      })
    if (setLoading) loading.value = false
  }
  
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
  const initialCache = {
    promptIds: [],
    corpusIds: [],
    prompts: [],
    corpus: [],
    distribution: null,
    distributionCorpus: null
  }
  
  onMounted(async () => {
    console.log('组件挂载完成')
    try {
      await Promise.all([
        fetchTextData(),
        fetchFeatureDistribution(),
        fetchCorpusFeatureDistribution()
      ])
      console.log('数据获取完成')
      // 缓存初始数据
      initialCache.promptIds = [...promptIds.value]
      initialCache.corpusIds = [...corpusIds.value]
      initialCache.prompts = JSON.parse(JSON.stringify(currentPrompts.value))
      initialCache.corpus = JSON.parse(JSON.stringify(currentCorpus.value))
      initialCache.distribution = JSON.parse(JSON.stringify(distributionData.value))
      initialCache.distributionCorpus = JSON.parse(JSON.stringify(distributionDataCorpus.value))
      // 确保数据加载完成后再初始化图表
      await new Promise(resolve => setTimeout(resolve, 200))
      await initChartsWithDataAttribute()
    } catch (error) {
      console.error('初始化失败:', error)
    }
  })
  
  // 添加历史记录相关的状态
  const featureHistory = ref({
    prompt: [],
    corpus: []
  })
  
  const historyPanelOpen = ref({
    prompt: false,
    corpus: false
  })
  
  const loading = ref(false)
  
  const initialIds = {
    prompt: ref([]),
    corpus: ref([])
  }
  
  onMounted(() => {
    initialIds.prompt.value = Array.from({length: 660}, (_, i) => i)
    initialIds.corpus.value = Array.from({length: 660}, (_, i) => i)
  })
  
  // 检查是否有初始状态
  // const hasInitialState = (dataSource) => {
  //   return initialIds[dataSource].value.length > 0
  // }
  
  // 恢复初始状态
  // const restoreInitialState = async (dataSource) => {
  //   loading.value = true
  //   await clearFeatures(dataSource, false)
  //   promptIds.value = [...initialCache.promptIds]
  //   corpusIds.value = [...initialCache.corpusIds]
  //   currentPrompts.value = JSON.parse(JSON.stringify(initialCache.prompts))
  //   currentCorpus.value = JSON.parse(JSON.stringify(initialCache.corpus))
  //   distributionData.value = JSON.parse(JSON.stringify(initialCache.distribution))
  //   distributionDataCorpus.value = JSON.parse(JSON.stringify(initialCache.distributionCorpus))
  //   // 重新渲染图表
  //   await nextTick()
  //   await initChartsWithDataAttribute()
  //   loading.value = false
  // }
  
  // 切换历史面板
  const toggleHistoryPanel = async (dataSource) => {
    loading.value = true
    historyPanelOpen.value[dataSource] = !historyPanelOpen.value[dataSource]
    loading.value = false
  }
  
  // 格式化时间
  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  
  // 历史记录条下拉状态
  const openHistoryDropdowns = ref({ prompt: {}, corpus: {} })
  const openHistoryFeatureDropdowns = ref({ prompt: {}, corpus: {} })
  const editingHistoryName = ref({ prompt: null, corpus: null })
  const historyApplyLoading = ref({ prompt: null, corpus: null })
  
  // 历史记录缓存结构
  const historyCache = ref({ prompt: [], corpus: [] })
  
  const editHistoryName = (dataSource, index) => {
    editingHistoryName.value[dataSource] = index
  }
  const saveHistoryName = (dataSource, index, newName) => {
    featureHistory.value[dataSource][index].name = newName
    editingHistoryName.value[dataSource] = null
  }
  const toggleHistoryDropdown = (dataSource, index) => {
    openHistoryDropdowns.value[dataSource][index] = !openHistoryDropdowns.value[dataSource][index]
  }
  const toggleHistoryFeatureDropdown = (dataSource, historyIndex, featureName) => {
    if (!openHistoryFeatureDropdowns.value[dataSource][historyIndex]) {
      openHistoryFeatureDropdowns.value[dataSource][historyIndex] = {}
    }
    openHistoryFeatureDropdowns.value[dataSource][historyIndex][featureName] =
      !openHistoryFeatureDropdowns.value[dataSource][historyIndex]?.[featureName]
  }
  const applyHistoryRecord = async (dataSource, index) => {
    historyApplyLoading.value[dataSource] = index
    // 直接用缓存恢复所有数据（完全等同于初始化缓存恢复）
    const cache = historyCache.value[dataSource][index]
    if (cache) {
      selectedFeatures.value[dataSource] = JSON.parse(JSON.stringify(featureHistory.value[dataSource][index].features))
      promptIds.value = [...cache.promptIds]
      corpusIds.value = [...cache.corpusIds]
      currentPrompts.value = JSON.parse(JSON.stringify(cache.prompts))
      currentCorpus.value = JSON.parse(JSON.stringify(cache.corpus))
      distributionData.value = JSON.parse(JSON.stringify(cache.distribution))
      distributionDataCorpus.value = JSON.parse(JSON.stringify(cache.distributionCorpus))
      await nextTick()
      await initChartsWithDataAttribute()
    }
    historyApplyLoading.value[dataSource] = null
  }
  // 分组函数
  const groupFeatures = (features) => {
    const groups = {}
    features.forEach(feature => {
      if (!groups[feature.featureName]) {
        groups[feature.featureName] = []
      }
      groups[feature.featureName].push(feature)
    })
    return groups
  }
  // 修改提交函数，添加历史记录
  // const submitFeatures = async (dataSource) => {
  //   loading.value = true
  //   const rawData = toRaw(selectedFeatures.value[dataSource])
  //   try {
  //     const response = await fetch('http://127.0.0.1:5000/api/filter_by_features', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify({
  //         selectedFeatures: rawData,
  //         dataSource: dataSource
  //       })
  //     })
  //     const result = await response.json()
  //     if (result.success) {
  //       if (dataSource === 'prompt') {
  //         promptIds.value = result.filtered_ids
  //       } else {
  //         corpusIds.value = result.filtered_ids
  //       }
  //       await Promise.all([
  //         fetchFeatureDistribution(),
  //         fetchCorpusFeatureDistribution()
  //       ])
  //       await fetchTextData()
  //       // 只有此时，界面数据才是"本次选择"后的快照，应该在这里缓存
  //       featureHistory.value[dataSource].push({
  //         timestamp: Date.now(),
  //         name: formatTime(Date.now()),
  //         features: JSON.parse(JSON.stringify(rawData))
  //       })
  //       historyCache.value[dataSource].push({
  //         promptIds: [...promptIds.value],
  //         corpusIds: [...corpusIds.value],
  //         prompts: JSON.parse(JSON.stringify(currentPrompts.value)),
  //         corpus: JSON.parse(JSON.stringify(currentCorpus.value)),
  //         distribution: JSON.parse(JSON.stringify(distributionData.value)),
  //         distributionCorpus: JSON.parse(JSON.stringify(distributionDataCorpus.value))
  //       })
  //       if (featureHistory.value[dataSource].length > 10) {
  //         featureHistory.value[dataSource].shift()
  //         historyCache.value[dataSource].shift()
  //       }
  //     } else {
  //       console.error('筛选失败:', result.error)
  //     }
  //   } catch (error) {
  //     console.error('请求失败:', error)
  //   }
  //   loading.value = false
  // }
  
  // 恢复历史状态
  const restoreHistoryState = async (dataSource, index) => {
    loading.value = true
    const historyState = featureHistory.value[dataSource][index]
    if (historyState) {
      selectedFeatures.value[dataSource] = JSON.parse(JSON.stringify(historyState.features))
      // 更新所有图表的边框状态
      Object.keys(selectedFeatures.value[dataSource]).forEach(feature => {
        const featureData = selectedFeatures.value[dataSource].find(f => f.featureName === feature)
        if (featureData) {
          updateChartBorders(dataSource, feature, featureData.valueRange)
        }
      })
    }
    loading.value = false
  }
  
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
  
  // 添加新的响应式变量
  const openDropdowns = ref({
    prompt: {},
    corpus: {}
  })
  
  // 添加计算属性来对特征进行分组
  const groupedPromptFeatures = computed(() => {
    const groups = {}
    selectedFeatures.value.prompt.forEach(feature => {
      if (!groups[feature.featureName]) {
        groups[feature.featureName] = []
      }
      groups[feature.featureName].push(feature)
    })
    return groups
  })
  
  const groupedCorpusFeatures = computed(() => {
    const groups = {}
    selectedFeatures.value.corpus.forEach(feature => {
      if (!groups[feature.featureName]) {
        groups[feature.featureName] = []
      }
      groups[feature.featureName].push(feature)
    })
    return groups
  })
  
  // 添加下拉框切换函数
  const toggleFeatureDropdown = (dataSource, featureName) => {
    openDropdowns.value[dataSource][featureName] = !openDropdowns.value[dataSource][featureName]
  }
  
  // 添加获取特征索引的辅助函数
  const getFeatureIndex = (dataSource, feature) => {
    return selectedFeatures.value[dataSource].findIndex(f => 
      f.featureName === feature.featureName && 
      f.valueRange === feature.valueRange
    )
  }
  
  // 全局历史记录相关变量
  const globalFeatureHistory = ref([]) // [{timestamp, name, features: {promptFeatures, corpusFeatures}, dataSnapshot: {...}}]
  const globalHistoryPanelOpen = ref(false)
  const globalHistoryApplyLoading = ref(null)
  const openGlobalHistoryDropdowns = ref({})
  const openGlobalHistoryFeatureDropdowns = ref({})
  const editingGlobalHistoryName = ref(null)
  
  // 全局按钮方法
  const submitAllFeatures = async () => {
    loading.value = true
    const promptRaw = toRaw(selectedFeatures.value.prompt)
    const corpusRaw = toRaw(selectedFeatures.value.corpus)
  
    // 新增：判断未选择的那一侧id用默认id集合
    const promptIdsToSend = promptRaw.length > 0 ? promptIds.value : initialIds.prompt.value
    const corpusIdsToSend = corpusRaw.length > 0 ? corpusIds.value : initialIds.corpus.value
  
    // 先缓存选择状态
    const historyRecord = {
      timestamp: Date.now(),
      name: formatTime(Date.now()),
      features: {
        promptFeatures: JSON.parse(JSON.stringify(promptRaw)),
        corpusFeatures: JSON.parse(JSON.stringify(corpusRaw))
      },
      dataSnapshot: null // 稍后填充
    }
    try {
      // 提交prompt
      const promptRes = await fetch('http://127.0.0.1:5000/api/filter_by_features', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selectedFeatures: promptRaw, dataSource: 'prompt', prompt_ids: promptIdsToSend, corpus_ids: corpusIdsToSend })
      })
      const promptResult = await promptRes.json()
      if (promptResult.success) {
        promptIds.value = promptResult.filtered_ids
      }
      // 提交corpus
      const corpusRes = await fetch('http://127.0.0.1:5000/api/filter_by_features', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selectedFeatures: corpusRaw, dataSource: 'corpus', prompt_ids: promptIdsToSend, corpus_ids: corpusIdsToSend })
      })
      const corpusResult = await corpusRes.json()
      if (corpusResult.success) {
        corpusIds.value = corpusResult.filtered_ids
      }
      await Promise.all([
        fetchFeatureDistribution(),
        fetchCorpusFeatureDistribution()
      ])
      await fetchTextData()
      // 再缓存应用后的数据快照
      historyRecord.dataSnapshot = {
        promptIds: [...promptIds.value],
        corpusIds: [...corpusIds.value],
        currentPrompts: JSON.parse(JSON.stringify(currentPrompts.value)),
        currentCorpus: JSON.parse(JSON.stringify(currentCorpus.value)),
        distributionData: JSON.parse(JSON.stringify(distributionData.value)),
        distributionDataCorpus: JSON.parse(JSON.stringify(distributionDataCorpus.value)),
        promptFeatures: JSON.parse(JSON.stringify(promptRaw)),
        corpusFeatures: JSON.parse(JSON.stringify(corpusRaw))
      }
      globalFeatureHistory.value.push(historyRecord)
      if (globalFeatureHistory.value.length > 10) {
        globalFeatureHistory.value.shift()
      }
    } catch (e) {
      console.error(e)
    }
    loading.value = false
  }
  const clearAllFeatures = async () => {
    loading.value = true
    barBorders.value = { prompt: {}, corpus: {} }
    selectedFeatures.value = { prompt: [], corpus: [] }
    document.querySelectorAll('.feature-container svg').forEach(svg => {
      d3.select(svg).selectAll('.bar-count, .bar-robustness')
        .attr('stroke', 'none')
        .attr('opacity', 0.7)
        .attr('stroke-width', 0)
    })
    loading.value = false
  }
  const restoreInitialStateAll = async () => {
    loading.value = true
    await clearAllFeatures()
    promptIds.value = [...initialCache.promptIds]
    corpusIds.value = [...initialCache.corpusIds]
    currentPrompts.value = JSON.parse(JSON.stringify(initialCache.prompts))
    currentCorpus.value = JSON.parse(JSON.stringify(initialCache.corpus))
    distributionData.value = JSON.parse(JSON.stringify(initialCache.distribution))
    distributionDataCorpus.value = JSON.parse(JSON.stringify(initialCache.distributionCorpus))
    await nextTick()
    await initChartsWithDataAttribute()
    loading.value = false
  }
  const toggleHistoryPanelGlobal = () => {
    globalHistoryPanelOpen.value = !globalHistoryPanelOpen.value
  }
  const applyGlobalHistoryRecord = async (index) => {
    globalHistoryApplyLoading.value = index
    const record = globalFeatureHistory.value[index]
    if (record && record.dataSnapshot) {
      selectedFeatures.value.prompt = JSON.parse(JSON.stringify(record.dataSnapshot.promptFeatures))
      selectedFeatures.value.corpus = JSON.parse(JSON.stringify(record.dataSnapshot.corpusFeatures))
      promptIds.value = [...record.dataSnapshot.promptIds]
      corpusIds.value = [...record.dataSnapshot.corpusIds]
      currentPrompts.value = JSON.parse(JSON.stringify(record.dataSnapshot.currentPrompts))
      currentCorpus.value = JSON.parse(JSON.stringify(record.dataSnapshot.currentCorpus))
      distributionData.value = JSON.parse(JSON.stringify(record.dataSnapshot.distributionData))
      distributionDataCorpus.value = JSON.parse(JSON.stringify(record.dataSnapshot.distributionDataCorpus))
      await nextTick()
      await initChartsWithDataAttribute()
    }
    globalHistoryApplyLoading.value = null
  }
  const editGlobalHistoryName = (index) => {
    editingGlobalHistoryName.value = index
  }
  const saveGlobalHistoryName = (index, newName) => {
    globalFeatureHistory.value[index].name = newName
    editingGlobalHistoryName.value = null
  }
  const toggleGlobalHistoryDropdown = (index) => {
    openGlobalHistoryDropdowns.value[index] = !openGlobalHistoryDropdowns.value[index]
  }
  const toggleGlobalHistoryFeatureDropdown = (historyIndex, type, featureName) => {
    if (!openGlobalHistoryFeatureDropdowns.value[historyIndex]) {
      openGlobalHistoryFeatureDropdowns.value[historyIndex] = { prompt: {}, corpus: {} }
    }
    openGlobalHistoryFeatureDropdowns.value[historyIndex][type][featureName] =
      !openGlobalHistoryFeatureDropdowns.value[historyIndex][type][featureName]
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
    position: relative;
  }
  .left-status {
    flex: 0 0 330px;
    min-width: 330px;
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
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    border-right: none;
    border-left: none;
    width: 100%;
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
    gap: 2px;
  }
  
  .icon-btn {
    background: #f0f0f0;
    border: none;
    border-radius: 6px;
    padding: 2px 4px;
    font-size: 15px;
    color: #4e79a7;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    height: 28px;
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
  
  /* 新增样式 */
  .tag-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    width: 100%;
  }
  
  .dropdown-icon {
    font-size: 12px;
    color: #666;
    transition: transform 0.2s;
  }
  
  .dropdown-icon.open {
    transform: rotate(180deg);
  }
  
  .feature-dropdown {
    margin-top: 8px;
    padding: 8px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  
  .dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 8px;
    margin-bottom: 4px;
    background: white;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  
  .dropdown-item:last-child {
    margin-bottom: 0;
  }
  
  .feature-count {
    color: #666;
    font-size: 12px;
    margin-left: 4px;
  }
  
  /* 修改现有样式 */
  .feature-tag {
    width: 100%;
    margin-bottom: 8px;
  }
  
  .tag-content {
    display: flex;
    align-items: center;
    flex: 1;
  }
  
  /* 新增样式 */
  .status-container {
    position: relative;
    display: flex;
    height: calc(100% - 80px);
    z-index: 1;
  }
  .main-status {
    flex: 1;
    position: relative;
    z-index: 2;
    background: #fff;
  }
  .history-panel {
    position: absolute;
    right: 0;
    top: -80px;
    width: 300px;
    height: 400px;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(78,121,167,0.04);
    z-index: 3;
    overflow: visible;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
  }
  .history-panel.open {
    opacity: 1;
    z-index: 3;
    transform: translateX(320px);
    pointer-events: auto;
  }
  
  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 12px 8px 8px 8px;
    border-bottom: 1px solid #e0e0e0;
    background: none;
  }
  
  .history-header h4 {
    margin: 0;
    color: #333;
    font-size: 16px;
    font-weight: bold;
    border-left: 4px solid #4e79a7;
    padding-left: 8px;
    margin-right: 8px;
  }
  
  .close-history {
    background: none;
    border: none;
    color: #bbb;
    cursor: pointer;
    font-size: 18px;
    padding: 0 4px;
    border-radius: 6px;
    transition: color 0.2s, background 0.2s;
  }
  .close-history:hover {
    color: #e15759;
    background: #ffeaea;
  }
  
  .history-list {
    padding: 8px;
    max-height: 320px;
    overflow-y: auto;
  }
  
  .history-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px;
    margin-bottom: 6px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: #fff;
    font-size: 14px;
    transition: box-shadow 0.2s, border-color 0.2s;
    cursor: pointer;
  }
  .history-item:hover {
    box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    border-color: #4e79a7;
  }
  
  .history-time {
    color: #555;
    font-size: 12px;
    margin-right: 10px;
    font-weight: bold;
  }
  
  .history-count {
    color: #666;
    font-size: 13px;
  }
  
  .loading-mask {
    position: fixed;
    left: 0; top: 0; right: 0; bottom: 0;
    background: rgba(255,255,255,0.7);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: #4e79a7;
  }
  
  .history-main-row {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }
  .history-name-input {
    font-size: 14px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 2px 6px;
    width: 120px;
  }
  .history-edit-btn, .history-apply-btn {
    background: none;
    border: none;
    color: #4e79a7;
    cursor: pointer;
    font-size: 16px;
    padding: 0 4px;
    border-radius: 6px;
    transition: color 0.2s, background 0.2s;
  }
  .history-edit-btn:hover {
    color: #e15759;
    background: #e3f0ff;
  }
  .history-apply-btn:disabled {
    color: #bbb;
    cursor: not-allowed;
  }
  .history-feature-dropdown {
    margin-top: 8px;
    padding: 8px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  .history-dropdown-block {
    margin-top: 8px;
    margin-bottom: 12px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
    padding: 10px 8px 8px 8px;
  }
  
  .global-history-panel {
    position: absolute;
    right: 0;
    top: -80px;
    width: 300px;
    height: 400px;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(78,121,167,0.04);
    z-index: 3;
    overflow: visible;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
  }
  .global-history-panel.open {
    opacity: 1;
    z-index: 3;
    transform: translateX(320px);
    pointer-events: auto;
  }
  
  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 12px 8px 8px 8px;
    border-bottom: 1px solid #e0e0e0;
    background: none;
  }
  
  .history-header h4 {
    margin: 0;
    color: #333;
    font-size: 16px;
    font-weight: bold;
    border-left: 4px solid #4e79a7;
    padding-left: 8px;
    margin-right: 8px;
  }
  
  .close-history {
    background: none;
    border: none;
    color: #bbb;
    cursor: pointer;
    font-size: 18px;
    padding: 0 4px;
    border-radius: 6px;
    transition: color 0.2s, background 0.2s;
  }
  .close-history:hover {
    color: #e15759;
    background: #ffeaea;
  }
  
  .history-list {
    padding: 8px;
    max-height: 320px;
    overflow-y: auto;
  }
  
  .history-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px;
    margin-bottom: 6px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: #fff;
    font-size: 14px;
    transition: box-shadow 0.2s, border-color 0.2s;
    cursor: pointer;
  }
  .history-item:hover {
    box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    border-color: #4e79a7;
  }
  
  .history-time {
    color: #555;
    font-size: 12px;
    margin-right: 10px;
    font-weight: bold;
  }
  
  .history-count {
    color: #666;
    font-size: 13px;
  }
  
  .history-main-row {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }
  .history-name-input {
    font-size: 14px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 2px 6px;
    width: 120px;
  }
  .history-edit-btn, .history-apply-btn {
    background: none;
    border: none;
    color: #4e79a7;
    cursor: pointer;
    font-size: 16px;
    padding: 0 4px;
    border-radius: 6px;
    transition: color 0.2s, background 0.2s;
  }
  .history-edit-btn:hover {
    color: #e15759;
    background: #e3f0ff;
  }
  .history-apply-btn:disabled {
    color: #bbb;
    cursor: not-allowed;
  }
  .history-feature-dropdown {
    margin-top: 8px;
    padding: 8px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  .history-dropdown-block {
    margin-top: 8px;
    margin-bottom: 12px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
    padding: 10px 8px 8px 8px;
  }
  
  .history-type-block {
    margin-bottom: 12px;
  }
  
  .history-type-title {
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 8px;
  }
  
  .feature-tag {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 10px;
    background: #f8f8f8;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    margin-bottom: 4px;
  }
  
  .feature-tag:hover {
    background: #e3f0ff;
  }
  
  .dropdown-icon {
    font-size: 12px;
    color: #666;
    transition: transform 0.2s;
  }
  
  .dropdown-icon.open {
    transform: rotate(180deg);
  }
  
  .feature-dropdown {
    margin-top: 8px;
    padding: 8px;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
  }
  
  .dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 8px;
    margin-bottom: 4px;
    background: white;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  
  .dropdown-item:last-child {
    margin-bottom: 0;
  }
  
  .feature-count {
    color: #666;
    font-size: 12px;
    margin-left: 4px;
  }
  
  .global-history-panel-side {
    position: absolute;
    top: 0;
    left: 330px; /* left-status宽度 */
    width: 340px;
    height: 100%;
    background: #fff;
    border-left: 1px solid #e0e0e0;
    box-shadow: -2px 0 8px rgba(78,121,167,0.08);
    z-index: 10;
    overflow-y: auto;
    transition: left 0.3s;
  }
  
  .global-section-header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 8px 0;
    border-bottom: 1px solid #e0e0e0;
    background: #fff;
    margin-bottom: 0;
    box-sizing: border-box;
  }
  .global-section-header h3 {
    margin: 0;
    color: #333;
    font-size: 18px;
    font-weight: bold;
    border-left: 4px solid #4e79a7;
    padding-left: 8px;
    margin-right: 8px;
  }
  .button-group {
    display: flex;
    gap: 8px;
  }
  </style>
  
  
  
  <!-- todo -->
   <!-- 目前有一个问题是，当我选择特征获取选择区间内的鲁棒性和分布数据时，如果只选择了prompt的特征，就只能将prompt的id传给后端，而corpus的id显示为空，相同如果只选择corpus的特征，那么只会传递corpus的id而prompt的id会为空。我需要在处理选择特征的操作时，若只选择了prompt或corpus的特征，那么没选择特征的要使用默认的id集合也就是0到659（660个全部的id） -->














   <template>
    <div class="main-layout">
      <div v-if="loading" class="loading-mask">
        <span>加载中...</span>
      </div>
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
  
        <!-- 中间：空白 -->
        <div class="center-blank">
          <div class="global-section-header">
            <h3>选择状态</h3>
            <div class="button-group">
              <!-- 新增：Prompt选择状态下拉 -->
              <div class="global-status-dropdown" style="position:relative;">
                <button class="icon-btn" @click="globalPromptDropdownOpen = !globalPromptDropdownOpen">
                  Prompt已选{{ selectedFeatures.prompt.length }}项
                  <span class="dropdown-icon" :class="{ open: globalPromptDropdownOpen }">▼</span>
                </button>
                <div v-if="globalPromptDropdownOpen" class="global-status-dropdown-content">
                  <div v-if="selectedFeatures.prompt.length === 0" class="empty-state">无已选Prompt特征</div>
                  <div v-else class="tags-container">
                    <div v-for="(featureGroup, featureName) in groupedPromptFeatures" :key="'global-prompt-'+featureName" class="feature-tag">
                      <div class="tag-header" @click="toggleFeatureDropdown('prompt', featureName)">
                        <span class="tag-content">
                          <span class="feature-name">{{ featureName }}</span>
                          <span class="feature-count">({{ featureGroup.length }})</span>
                        </span>
                        <span class="dropdown-icon" :class="{ 'open': openDropdowns.prompt[featureName] }">▼</span>
                      </div>
                      <div v-if="openDropdowns.prompt[featureName]" class="feature-dropdown">
                        <div v-for="(feature, index) in featureGroup" :key="'global-prompt-'+featureName+'-'+index" class="dropdown-item">
                          <span class="value-range">{{ feature.valueRange }}</span>
                          <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                          <button @click="removeFeature('prompt', getFeatureIndex('prompt', feature))" class="tag-remove">×</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <!-- 新增：Corpus选择状态下拉 -->
              <div class="global-status-dropdown" style="position:relative;">
                <button class="icon-btn" @click="globalCorpusDropdownOpen = !globalCorpusDropdownOpen">
                  Corpus已选{{ selectedFeatures.corpus.length }}项
                  <span class="dropdown-icon" :class="{ open: globalCorpusDropdownOpen }">▼</span>
                </button>
                <div v-if="globalCorpusDropdownOpen" class="global-status-dropdown-content">
                  <div v-if="selectedFeatures.corpus.length === 0" class="empty-state">无已选Corpus特征</div>
                  <div v-else class="tags-container">
                    <div v-for="(featureGroup, featureName) in groupedCorpusFeatures" :key="'global-corpus-'+featureName" class="feature-tag">
                      <div class="tag-header" @click="toggleFeatureDropdown('corpus', featureName)">
                        <span class="tag-content">
                          <span class="feature-name">{{ featureName }}</span>
                          <span class="feature-count">({{ featureGroup.length }})</span>
                        </span>
                        <span class="dropdown-icon" :class="{ 'open': openDropdowns.corpus[featureName] }">▼</span>
                      </div>
                      <div v-if="openDropdowns.corpus[featureName]" class="feature-dropdown">
                        <div v-for="(feature, index) in featureGroup" :key="'global-corpus-'+featureName+'-'+index" class="dropdown-item">
                          <span class="value-range">{{ feature.valueRange }}</span>
                          <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                          <button @click="removeFeature('corpus', getFeatureIndex('corpus', feature))" class="tag-remove">×</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <!-- 原有全局操作按钮 -->
              <button class="icon-btn" @click="submitAllFeatures" :disabled="!selectedFeatures.prompt.length && !selectedFeatures.corpus.length || loading">
                <el-icon v-if="!loading"><Check /></el-icon>
                <el-icon v-else><Loading /></el-icon>
                提交选择
              </button>
              <button class="icon-btn" @click="clearAllFeatures" :disabled="(!selectedFeatures.prompt.length && !selectedFeatures.corpus.length) || loading">
                <el-icon><Delete /></el-icon>
                清空
              </button>
              <button class="icon-btn" @click="restoreInitialStateAll" :disabled="loading">
                <el-icon><Refresh /></el-icon>
                恢复初始状态
              </button>
              <button class="icon-btn" @click="toggleHistoryPanelGlobal" :disabled="loading">
                <el-icon><Timer /></el-icon>
                历史记录
              </button>
            </div>
          </div>
          <div class="blank-content"></div>
        </div>
        <div v-if="globalHistoryPanelOpen" class="global-history-panel-side">
          <div class="history-header">
            <h4>历史记录</h4>
            <button class="close-history" @click="toggleHistoryPanelGlobal">×</button>
          </div>
          <div class="history-list">
            <div v-for="(record, index) in globalFeatureHistory"
                 :key="'global-history-'+index"
                 class="history-item">
              <div class="history-main-row" @click="toggleGlobalHistoryDropdown(index)">
                <span class="history-name">
                  <template v-if="editingGlobalHistoryName === index">
                    <input v-model="record.name"
                           @blur="saveGlobalHistoryName(index, record.name)"
                           @keyup.enter="saveGlobalHistoryName(index, record.name)"
                           class="history-name-input" />
                  </template>
                  <template v-else>
                    {{ record.name || formatTime(record.timestamp) }}
                  </template>
                </span>
                <span class="history-count">Prompt: {{ record.features.promptFeatures.length }}，Corpus: {{ record.features.corpusFeatures.length }}</span>
                <button class="history-edit-btn" @click.stop="editGlobalHistoryName(index)">
                  <el-icon><Edit /></el-icon>
                </button>
                <button class="history-apply-btn"
                        @click.stop="applyGlobalHistoryRecord(index)"
                        :disabled="globalHistoryApplyLoading === index">
                  <el-icon v-if="globalHistoryApplyLoading === index"><Loading /></el-icon>
                  <el-icon v-else><Check /></el-icon>
                </button>
                <span class="dropdown-icon" :class="{ open: openGlobalHistoryDropdowns[index] }">▼</span>
              </div>
              <div v-if="openGlobalHistoryDropdowns[index]" class="history-dropdown-block">
                <div class="history-type-block">
                  <div class="history-type-title">Prompt特征</div>
                  <div v-for="(featureGroup, featureName) in groupFeatures(record.features.promptFeatures)"
                       :key="'global-history-prompt-'+featureName"
                       class="feature-tag">
                    <div class="tag-header" @click.stop="toggleGlobalHistoryFeatureDropdown(index, 'prompt', featureName)">
                      <span class="feature-name">{{ featureName }}</span>
                      <span class="feature-count">({{ featureGroup.length }})</span>
                      <span class="dropdown-icon" :class="{ open: openGlobalHistoryFeatureDropdowns[index]?.prompt?.[featureName] }">▼</span>
                    </div>
                    <div v-if="openGlobalHistoryFeatureDropdowns[index]?.prompt?.[featureName]" class="feature-dropdown">
                      <div v-for="(feature, idx) in featureGroup"
                           :key="'global-history-prompt-'+featureName+'-'+idx"
                           class="dropdown-item">
                        <span class="value-range">{{ feature.valueRange }}</span>
                        <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="history-type-block">
                  <div class="history-type-title">Corpus特征</div>
                  <div v-for="(featureGroup, featureName) in groupFeatures(record.features.corpusFeatures)"
                       :key="'global-history-corpus-'+featureName"
                       class="feature-tag">
                    <div class="tag-header" @click.stop="toggleGlobalHistoryFeatureDropdown(index, 'corpus', featureName)">
                      <span class="feature-name">{{ featureName }}</span>
                      <span class="feature-count">({{ featureGroup.length }})</span>
                      <span class="dropdown-icon" :class="{ open: openGlobalHistoryFeatureDropdowns[index]?.corpus?.[featureName] }">▼</span>
                    </div>
                    <div v-if="openGlobalHistoryFeatureDropdowns[index]?.corpus?.[featureName]" class="feature-dropdown">
                      <div v-for="(feature, idx) in featureGroup"
                           :key="'global-history-corpus-'+featureName+'-'+idx"
                           class="dropdown-item">
                        <span class="value-range">{{ feature.valueRange }}</span>
                        <span class="stats">({{ feature.count }}, {{ feature.robustness }})</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
  import { Sort, Check, Delete, Refresh, Timer, Edit, Loading } from '@element-plus/icons-vue'
  import { ref as vueRef } from 'vue'
  
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
  const removeFeature = async (dataSource, index) => {
    loading.value = true
    const feature = selectedFeatures.value[dataSource][index];
    const key = `${feature.featureName}-${feature.valueRange}`;
    delete barBorders.value[dataSource][key];
    selectedFeatures.value[dataSource].splice(index, 1);
    // 精准更新（只需更新被移除的特征）
    updateChartBorders(dataSource, feature.featureName, feature.valueRange);
    loading.value = false
  }
  
  // 修改后的clearFeatures
  
  
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
  const initialCache = {
    promptIds: [],
    corpusIds: [],
    prompts: [],
    corpus: [],
    distribution: null,
    distributionCorpus: null
  }
  
  onMounted(async () => {
    console.log('组件挂载完成')
    try {
      await Promise.all([
        fetchTextData(),
        fetchFeatureDistribution(),
        fetchCorpusFeatureDistribution()
      ])
      console.log('数据获取完成')
      // 缓存初始数据
      initialCache.promptIds = [...promptIds.value]
      initialCache.corpusIds = [...corpusIds.value]
      initialCache.prompts = JSON.parse(JSON.stringify(currentPrompts.value))
      initialCache.corpus = JSON.parse(JSON.stringify(currentCorpus.value))
      initialCache.distribution = JSON.parse(JSON.stringify(distributionData.value))
      initialCache.distributionCorpus = JSON.parse(JSON.stringify(distributionDataCorpus.value))
      // 确保数据加载完成后再初始化图表
      await new Promise(resolve => setTimeout(resolve, 200))
      await initChartsWithDataAttribute()
    } catch (error) {
      console.error('初始化失败:', error)
    }
  })
  
  
  
  
  
  const loading = ref(false)
  
  const initialIds = {
    prompt: ref([]),
    corpus: ref([])
  }
  
  onMounted(() => {
    initialIds.prompt.value = Array.from({length: 660}, (_, i) => i)
    initialIds.corpus.value = Array.from({length: 660}, (_, i) => i)
  })
  
  // 检查是否有初始状态
  // const hasInitialState = (dataSource) => {
  //   return initialIds[dataSource].value.length > 0
  // }
  
  // 恢复初始状态
  // const restoreInitialState = async (dataSource) => {
  //   loading.value = true
  //   await clearFeatures(dataSource, false)
  //   promptIds.value = [...initialCache.promptIds]
  //   corpusIds.value = [...initialCache.corpusIds]
  //   currentPrompts.value = JSON.parse(JSON.stringify(initialCache.prompts))
  //   currentCorpus.value = JSON.parse(JSON.stringify(initialCache.corpus))
  //   distributionData.value = JSON.parse(JSON.stringify(initialCache.distribution))
  //   distributionDataCorpus.value = JSON.parse(JSON.stringify(initialCache.distributionCorpus))
  //   // 重新渲染图表
  //   await nextTick()
  //   await initChartsWithDataAttribute()
  //   loading.value = false
  // }
  
  
  
  // 格式化时间
  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  }
  
  
  
  
  // 分组函数
  const groupFeatures = (features) => {
    const groups = {}
    features.forEach(feature => {
      if (!groups[feature.featureName]) {
        groups[feature.featureName] = []
      }
      groups[feature.featureName].push(feature)
    })
    return groups
  }
  
  
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
  
  // 添加新的响应式变量
  const openDropdowns = ref({
    prompt: {},
    corpus: {}
  })
  
  // 添加计算属性来对特征进行分组
  const groupedPromptFeatures = computed(() => {
    const groups = {}
    selectedFeatures.value.prompt.forEach(feature => {
      if (!groups[feature.featureName]) {
        groups[feature.featureName] = []
      }
      groups[feature.featureName].push(feature)
    })
    return groups
  })
  
  const groupedCorpusFeatures = computed(() => {
    const groups = {}
    selectedFeatures.value.corpus.forEach(feature => {
      if (!groups[feature.featureName]) {
        groups[feature.featureName] = []
      }
      groups[feature.featureName].push(feature)
    })
    return groups
  })
  
  // 添加下拉框切换函数
  const toggleFeatureDropdown = (dataSource, featureName) => {
    openDropdowns.value[dataSource][featureName] = !openDropdowns.value[dataSource][featureName]
  }
  
  // 添加获取特征索引的辅助函数
  const getFeatureIndex = (dataSource, feature) => {
    return selectedFeatures.value[dataSource].findIndex(f => 
      f.featureName === feature.featureName && 
      f.valueRange === feature.valueRange
    )
  }
  
  // 全局历史记录相关变量
  const globalFeatureHistory = ref([]) // [{timestamp, name, features: {promptFeatures, corpusFeatures}, dataSnapshot: {...}}]
  const globalHistoryPanelOpen = ref(false)
  const globalHistoryApplyLoading = ref(null)
  const openGlobalHistoryDropdowns = ref({})
  const openGlobalHistoryFeatureDropdowns = ref({})
  const editingGlobalHistoryName = ref(null)
  
  // 全局按钮方法
  const submitAllFeatures = async () => {
    loading.value = true
    const promptRaw = toRaw(selectedFeatures.value.prompt)
    const corpusRaw = toRaw(selectedFeatures.value.corpus)
  
    // 新增：判断未选择的那一侧id用默认id集合
    const promptIdsToSend = promptRaw.length > 0 ? promptIds.value : initialIds.prompt.value
    const corpusIdsToSend = corpusRaw.length > 0 ? corpusIds.value : initialIds.corpus.value
  
    // 先缓存选择状态
    const historyRecord = {
      timestamp: Date.now(),
      name: formatTime(Date.now()),
      features: {
        promptFeatures: JSON.parse(JSON.stringify(promptRaw)),
        corpusFeatures: JSON.parse(JSON.stringify(corpusRaw))
      },
      dataSnapshot: null // 稍后填充
    }
    try {
      // 提交prompt
      const promptRes = await fetch('http://127.0.0.1:5000/api/filter_by_features', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selectedFeatures: promptRaw, dataSource: 'prompt', prompt_ids: promptIdsToSend, corpus_ids: corpusIdsToSend })
      })
      const promptResult = await promptRes.json()
      if (promptResult.success) {
        promptIds.value = promptResult.filtered_ids
      }
      // 提交corpus
      const corpusRes = await fetch('http://127.0.0.1:5000/api/filter_by_features', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selectedFeatures: corpusRaw, dataSource: 'corpus', prompt_ids: promptIdsToSend, corpus_ids: corpusIdsToSend })
      })
      const corpusResult = await corpusRes.json()
      if (corpusResult.success) {
        corpusIds.value = corpusResult.filtered_ids
      }
      await Promise.all([
        fetchFeatureDistribution(),
        fetchCorpusFeatureDistribution()
      ])
      await fetchTextData()
      // 再缓存应用后的数据快照
      historyRecord.dataSnapshot = {
        promptIds: [...promptIds.value],
        corpusIds: [...corpusIds.value],
        currentPrompts: JSON.parse(JSON.stringify(currentPrompts.value)),
        currentCorpus: JSON.parse(JSON.stringify(currentCorpus.value)),
        distributionData: JSON.parse(JSON.stringify(distributionData.value)),
        distributionDataCorpus: JSON.parse(JSON.stringify(distributionDataCorpus.value)),
        promptFeatures: JSON.parse(JSON.stringify(promptRaw)),
        corpusFeatures: JSON.parse(JSON.stringify(corpusRaw))
      }
      globalFeatureHistory.value.push(historyRecord)
      if (globalFeatureHistory.value.length > 10) {
        globalFeatureHistory.value.shift()
      }
    } catch (e) {
      console.error(e)
    }
    loading.value = false
  }
  const clearAllFeatures = async () => {
    loading.value = true
    barBorders.value = { prompt: {}, corpus: {} }
    selectedFeatures.value = { prompt: [], corpus: [] }
    document.querySelectorAll('.feature-container svg').forEach(svg => {
      d3.select(svg).selectAll('.bar-count, .bar-robustness')
        .attr('stroke', 'none')
        .attr('opacity', 0.7)
        .attr('stroke-width', 0)
    })
    loading.value = false
  }
  const restoreInitialStateAll = async () => {
    loading.value = true
    await clearAllFeatures()
    promptIds.value = [...initialCache.promptIds]
    corpusIds.value = [...initialCache.corpusIds]
    currentPrompts.value = JSON.parse(JSON.stringify(initialCache.prompts))
    currentCorpus.value = JSON.parse(JSON.stringify(initialCache.corpus))
    distributionData.value = JSON.parse(JSON.stringify(initialCache.distribution))
    distributionDataCorpus.value = JSON.parse(JSON.stringify(initialCache.distributionCorpus))
    await nextTick()
    await initChartsWithDataAttribute()
    loading.value = false
  }
  const toggleHistoryPanelGlobal = () => {
    globalHistoryPanelOpen.value = !globalHistoryPanelOpen.value
  }
  const applyGlobalHistoryRecord = async (index) => {
    globalHistoryApplyLoading.value = index
    const record = globalFeatureHistory.value[index]
    if (record && record.dataSnapshot) {
      selectedFeatures.value.prompt = JSON.parse(JSON.stringify(record.dataSnapshot.promptFeatures))
      selectedFeatures.value.corpus = JSON.parse(JSON.stringify(record.dataSnapshot.corpusFeatures))
      promptIds.value = [...record.dataSnapshot.promptIds]
      corpusIds.value = [...record.dataSnapshot.corpusIds]
      currentPrompts.value = JSON.parse(JSON.stringify(record.dataSnapshot.currentPrompts))
      currentCorpus.value = JSON.parse(JSON.stringify(record.dataSnapshot.currentCorpus))
      distributionData.value = JSON.parse(JSON.stringify(record.dataSnapshot.distributionData))
      distributionDataCorpus.value = JSON.parse(JSON.stringify(record.dataSnapshot.distributionDataCorpus))
      await nextTick()
      await initChartsWithDataAttribute()
    }
    globalHistoryApplyLoading.value = null
  }
  const editGlobalHistoryName = (index) => {
    editingGlobalHistoryName.value = index
  }
  const saveGlobalHistoryName = (index, newName) => {
    globalFeatureHistory.value[index].name = newName
    editingGlobalHistoryName.value = null
  }
  const toggleGlobalHistoryDropdown = (index) => {
    openGlobalHistoryDropdowns.value[index] = !openGlobalHistoryDropdowns.value[index]
  }
  const toggleGlobalHistoryFeatureDropdown = (historyIndex, type, featureName) => {
    if (!openGlobalHistoryFeatureDropdowns.value[historyIndex]) {
      openGlobalHistoryFeatureDropdowns.value[historyIndex] = { prompt: {}, corpus: {} }
    }
    openGlobalHistoryFeatureDropdowns.value[historyIndex][type][featureName] =
      !openGlobalHistoryFeatureDropdowns.value[historyIndex][type][featureName]
  }
  
  // 新增：全局下拉状态
  const globalPromptDropdownOpen = vueRef(false)
  const globalCorpusDropdownOpen = vueRef(false)
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
    position: relative;
  }
  .left-status {
    flex: 0 0 330px;
    min-width: 330px;
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
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    border-right: none;
    border-left: none;
    width: 100%;
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
    gap: 2px;
  }
  
  .icon-btn {
    background: #f0f0f0;
    border: none;
    border-radius: 6px;
    padding: 2px 4px;
    font-size: 15px;
    color: #4e79a7;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    height: 28px;
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
  
  /* 新增样式 */
  .tag-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    width: 100%;
  }
  
  .dropdown-icon {
    font-size: 12px;
    color: #666;
    transition: transform 0.2s;
  }
  
  .dropdown-icon.open {
    transform: rotate(180deg);
  }
  
  .feature-dropdown {
    margin-top: 8px;
    padding: 8px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  
  .dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 8px;
    margin-bottom: 4px;
    background: white;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  
  .dropdown-item:last-child {
    margin-bottom: 0;
  }
  
  .feature-count {
    color: #666;
    font-size: 12px;
    margin-left: 4px;
  }
  
  /* 修改现有样式 */
  .feature-tag {
    width: 100%;
    margin-bottom: 8px;
  }
  
  .tag-content {
    display: flex;
    align-items: center;
    flex: 1;
  }
  
  /* 新增样式 */
  .status-container {
    position: relative;
    display: flex;
    height: calc(100% - 80px);
    z-index: 1;
  }
  .main-status {
    flex: 1;
    position: relative;
    z-index: 2;
    background: #fff;
  }
  .history-panel {
    position: absolute;
    right: 0;
    top: -80px;
    width: 300px;
    height: 400px;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(78,121,167,0.04);
    z-index: 3;
    overflow: visible;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
  }
  .history-panel.open {
    opacity: 1;
    z-index: 3;
    transform: translateX(320px);
    pointer-events: auto;
  }
  
  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 12px 8px 8px 8px;
    border-bottom: 1px solid #e0e0e0;
    background: none;
  }
  
  .history-header h4 {
    margin: 0;
    color: #333;
    font-size: 16px;
    font-weight: bold;
    border-left: 4px solid #4e79a7;
    padding-left: 8px;
    margin-right: 8px;
  }
  
  .close-history {
    background: none;
    border: none;
    color: #bbb;
    cursor: pointer;
    font-size: 18px;
    padding: 0 4px;
    border-radius: 6px;
    transition: color 0.2s, background 0.2s;
  }
  .close-history:hover {
    color: #e15759;
    background: #ffeaea;
  }
  
  .history-list {
    padding: 8px;
    max-height: 320px;
    overflow-y: auto;
  }
  
  .history-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px;
    margin-bottom: 6px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: #fff;
    font-size: 14px;
    transition: box-shadow 0.2s, border-color 0.2s;
    cursor: pointer;
  }
  .history-item:hover {
    box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    border-color: #4e79a7;
  }
  
  .history-time {
    color: #555;
    font-size: 12px;
    margin-right: 10px;
    font-weight: bold;
  }
  
  .history-count {
    color: #666;
    font-size: 13px;
  }
  
  .loading-mask {
    position: fixed;
    left: 0; top: 0; right: 0; bottom: 0;
    background: rgba(255,255,255,0.7);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: #4e79a7;
  }
  
  .history-main-row {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }
  .history-name-input {
    font-size: 14px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 2px 6px;
    width: 120px;
  }
  .history-edit-btn, .history-apply-btn {
    background: none;
    border: none;
    color: #4e79a7;
    cursor: pointer;
    font-size: 16px;
    padding: 0 4px;
    border-radius: 6px;
    transition: color 0.2s, background 0.2s;
  }
  .history-edit-btn:hover {
    color: #e15759;
    background: #e3f0ff;
  }
  .history-apply-btn:disabled {
    color: #bbb;
    cursor: not-allowed;
  }
  .history-feature-dropdown {
    margin-top: 8px;
    padding: 8px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  .history-dropdown-block {
    margin-top: 8px;
    margin-bottom: 12px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
    padding: 10px 8px 8px 8px;
  }
  
  .global-history-panel {
    position: absolute;
    right: 0;
    top: -80px;
    width: 300px;
    height: 400px;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(78,121,167,0.04);
    z-index: 3;
    overflow: visible;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
  }
  .global-history-panel.open {
    opacity: 1;
    z-index: 3;
    transform: translateX(320px);
    pointer-events: auto;
  }
  
  .history-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 12px 8px 8px 8px;
    border-bottom: 1px solid #e0e0e0;
    background: none;
  }
  
  .history-header h4 {
    margin: 0;
    color: #333;
    font-size: 16px;
    font-weight: bold;
    border-left: 4px solid #4e79a7;
    padding-left: 8px;
    margin-right: 8px;
  }
  
  .close-history {
    background: none;
    border: none;
    color: #bbb;
    cursor: pointer;
    font-size: 18px;
    padding: 0 4px;
    border-radius: 6px;
    transition: color 0.2s, background 0.2s;
  }
  .close-history:hover {
    color: #e15759;
    background: #ffeaea;
  }
  
  .history-list {
    padding: 8px;
    max-height: 320px;
    overflow-y: auto;
  }
  
  .history-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px;
    margin-bottom: 6px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: #fff;
    font-size: 14px;
    transition: box-shadow 0.2s, border-color 0.2s;
    cursor: pointer;
  }
  .history-item:hover {
    box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    border-color: #4e79a7;
  }
  
  .history-time {
    color: #555;
    font-size: 12px;
    margin-right: 10px;
    font-weight: bold;
  }
  
  .history-count {
    color: #666;
    font-size: 13px;
  }
  
  .history-main-row {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
  }
  .history-name-input {
    font-size: 14px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 2px 6px;
    width: 120px;
  }
  .history-edit-btn, .history-apply-btn {
    background: none;
    border: none;
    color: #4e79a7;
    cursor: pointer;
    font-size: 16px;
    padding: 0 4px;
    border-radius: 6px;
    transition: color 0.2s, background 0.2s;
  }
  .history-edit-btn:hover {
    color: #e15759;
    background: #e3f0ff;
  }
  .history-apply-btn:disabled {
    color: #bbb;
    cursor: not-allowed;
  }
  .history-feature-dropdown {
    margin-top: 8px;
    padding: 8px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  .history-dropdown-block {
    margin-top: 8px;
    margin-bottom: 12px;
    background: #f8f8f8;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
    padding: 10px 8px 8px 8px;
  }
  
  .history-type-block {
    margin-bottom: 12px;
  }
  
  .history-type-title {
    font-size: 14px;
    font-weight: bold;
    margin-bottom: 8px;
  }
  
  .feature-tag {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 10px;
    background: #f8f8f8;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    margin-bottom: 4px;
  }
  
  .feature-tag:hover {
    background: #e3f0ff;
  }
  
  .dropdown-icon {
    font-size: 12px;
    color: #666;
    transition: transform 0.2s;
  }
  
  .dropdown-icon.open {
    transform: rotate(180deg);
  }
  
  .feature-dropdown {
    margin-top: 8px;
    padding: 8px;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
  }
  
  .dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 8px;
    margin-bottom: 4px;
    background: white;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  
  .dropdown-item:last-child {
    margin-bottom: 0;
  }
  
  .feature-count {
    color: #666;
    font-size: 12px;
    margin-left: 4px;
  }
  
  .global-history-panel-side {
    position: absolute;
    top: 0;
    left: 330px; /* left-status宽度 */
    width: 340px;
    height: 100%;
    background: #fff;
    border-left: 1px solid #e0e0e0;
    box-shadow: -2px 0 8px rgba(78,121,167,0.08);
    z-index: 10;
    overflow-y: auto;
    transition: left 0.3s;
  }
  
  .global-section-header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 8px 0;
    border-bottom: 1px solid #e0e0e0;
    background: #fff;
    margin-bottom: 0;
    box-sizing: border-box;
  }
  .global-section-header h3 {
    margin: 0;
    color: #333;
    font-size: 18px;
    font-weight: bold;
    border-left: 4px solid #4e79a7;
    padding-left: 8px;
    margin-right: 8px;
  }
  .button-group {
    display: flex;
    gap: 8px;
  }
  
  .global-status-dropdown-content {
    position: absolute;
    top: 36px;
    left: 0;
    min-width: 320px;
    max-width: 420px;
    background: #fff;
    border: 1.5px solid #4e79a7;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(78,121,167,0.10);
    z-index: 100;
    padding: 12px 10px 10px 10px;
    margin-top: 2px;
  }
  .global-status-dropdown .icon-btn {
    min-width: 120px;
    justify-content: flex-start;
  }
  </style>
  
  
  
  <!-- todo -->
   <!-- 目前有一个问题是，当我选择特征获取选择区间内的鲁棒性和分布数据时，如果只选择了prompt的特征，就只能将prompt的id传给后端，而corpus的id显示为空，相同如果只选择corpus的特征，那么只会传递corpus的id而prompt的id会为空。我需要在处理选择特征的操作时，若只选择了prompt或corpus的特征，那么没选择特征的要使用默认的id集合也就是0到659（660个全部的id） -->