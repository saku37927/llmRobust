<template>
  <div class="main-layout">
    <!-- 全局加载遮罩 -->
    <div v-if="loading" class="global-loading-overlay">
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="loading-text">数据加载中...</div>
      </div>
    </div>
    
    <!-- 选择状态栏移到最上方 -->
      <div class="center-blank">
        <div class="global-section-header">
          <h3>选择状态</h3>
          <div class="button-group">
          <!-- Prompt选择状态下拉 -->
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
          <!-- Corpus选择状态下拉 -->
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
            <!-- 攻击方式选择 -->
            <div class="attack-methods-section">
              <button class="icon-btn" @click="toggleAttackMethodsPanel">
                <el-icon><Edit /></el-icon>
                攻击方式选择
              </button>
            </div>
          </div>
        </div>
    </div>
    
    <!-- 攻击方式选择面板 -->
    <div v-if="attackMethodsPanelOpen" class="attack-methods-panel">
      <div class="attack-methods-header">
        <h4>选择攻击方式</h4>
        <button @click="toggleAttackMethodsPanel" class="close-attack-methods">×</button>
      </div>
      <div class="attack-methods-content">
        <div class="attack-method-item" v-for="method in attackMethods" :key="method.key">
          <label class="attack-method-label">
            <input 
              type="checkbox" 
              v-model="selectedAttackMethods" 
              :value="method.key"
              class="attack-method-checkbox"
            />
            <span class="attack-method-name">{{ method.name }}</span>
            <span class="attack-method-desc">{{ method.description }}</span>
          </label>
        </div>
        <div class="attack-methods-actions">
          <button 
            class="submit-attack-methods" 
            @click="submitAttackMethods"
            :disabled="selectedAttackMethods.length === 0"
          >
            提交选择 ({{ selectedAttackMethods.length }})
          </button>
          <button class="clear-attack-methods" @click="clearAttackMethods">
            清空选择
          </button>
        </div>
      </div>
    </div>
    <!-- 顶部：prompt特征图 -->
    <div class="top-feature">
      <div class="feature-container" data-container="prompt" style="width: 100%; position: relative;">
        <!-- 特征图表加载遮罩 -->
        <div v-if="loading" class="feature-loading-overlay">
          <div class="feature-loading-spinner">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <div class="loading-text">特征数据加载中...</div>
          </div>
        </div>
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
        <div class="center-blank">
          <div class="projection-row">
            <!-- A区：Prompt投影 -->
            <div class="projection-panel">
              <div class="panel-header">
                Prompt 投影
                <div class="panel-tools">
                  <button
                    class="tool-btn"
                    :class="{active: promptDragMode}"
                    @click="togglePromptDrag"
                  >拖拽</button>
                  <button
                    class="tool-btn"
                    :class="{active: promptLassoMode}"
                    @click="togglePromptLasso"
                  >套索</button>
                  <button
                    class="tool-btn"
                    @click="zoomPromptIn"
                    title="放大投影点"
                  >放大</button>
                  <button
                    class="tool-btn"
                    @click="zoomPromptOut"
                    title="缩小投影点"
                  >缩小</button>
                  <button
                    class="tool-btn select-btn"
                    :class="{active: promptLassoMode && promptLassoResults.length > 0}"
                    @click="applyPromptLassoSelection"
                    :disabled="!promptLassoMode || promptLassoResults.length === 0 || loading"
                    title="应用套索选择"
                  >
                    <el-icon v-if="loading"><Loading /></el-icon>
                    <span v-else>选择</span>
                  </button>
                </div>
              </div>
              <div class="panel-content">
                <svg
                  width="100%"
                  height="100%"
                  viewBox="0 0 400 300"
                  @mousedown="promptDragMode ? onPromptSvgMousedown($event) : (promptLassoMode ? onPromptLassoDown($event) : null)"
                  @wheel="promptDragMode ? onPromptSvgWheel($event) : null"
                  @click="hidePromptTooltip"
                >
                  <g :transform="promptTransform">
                    <g v-for="item in currentPrompts" :key="item.id">
                      <circle
                        v-if="item.x !== null && item.y !== null"
                        :cx="projectX(item.x, 'prompt')"
                        :cy="projectY(item.y, 'prompt')"
                        :r="2.5 * promptPointScale"
                        :fill="robustnessColorStyle(item.robustness, promptRobustnessRange[0], promptRobustnessRange[1]).color"
                        :stroke="selectedPromptId === item.id ? '#222' : 'none'"
                        :stroke-width="selectedPromptId === item.id ? 2 : 0"
                        style="cursor:pointer"
                        @click.stop="showPromptTooltip(item, $event)"
                      />
                    </g>
                  </g>

                  <polyline v-if="promptLassoPoints.length" :points="promptLassoPoints.map(p=>p.join(',')).join(' ')" fill="none" stroke="#999" stroke-width="2" stroke-dasharray="5,5" />


                  <defs>
                    <filter id="shadow-prompt" x="-20%" y="-20%" width="140%" height="140%">
                      <feDropShadow dx="2" dy="2" stdDeviation="2" flood-color="#bbb"/>
                    </filter>
                  </defs>
                </svg>  
              </div>

            </div>
            <!-- 中间控制区域 -->
            <div class="center-control-area">
              <!-- 攻击方式选择区域 -->
              <div class="attack-methods-section">
                <div class="attack-methods-header">
                  <h3>攻击方式选择</h3>
                  <div class="select-all-checkbox" @click="toggleSelectAll">
                    <span class="select-all-icon">{{ allSelected ? '✓' : '☐' }}</span>
                  </div>
                </div>
                <div class="attack-methods-list">
                  <div 
                    v-for="method in attackMethods" 
                    :key="method.key" 
                    class="attack-method-item"
                  >
                    <div class="attack-method-content">
                      <span class="attack-method-name">{{ method.name }}</span>
                      <input 
                        type="checkbox" 
                        :value="method.key" 
                        v-model="selectedAttackMethods"
                        class="attack-method-checkbox"
                      />
                    </div>
                  </div>
                </div>
                <div class="attack-methods-actions">
                  <div class="global-robustness-display">
                    <span class="global-robustness-label">全局鲁棒性:</span>
                    <span 
                      class="global-robustness-value" 
                      :style="{ color: globalRobustnessColor }"
                    >
                      {{ globalRobustnessText }}
                    </span>
                  </div>
                  <button class="submit-btn" @click="submitAttackMethods" :disabled="loading">
                    <el-icon v-if="loading"><Loading /></el-icon>
                    <span v-if="!loading">提交选择</span>
                    <span v-else>加载中...</span>
                  </button>
                </div>
              </div>
              
              <!-- 图例区域 -->
              <div class="legends-container">
                <div class="legend-section">
                  <!-- <h4>Prompt图例</h4> -->
                  <svg :width="80" :height="legendVHeight">
                    <g v-for="(val, idx) in legendVValuesPrompt" :key="idx">
                      <rect x="26" :y="15 + idx * (legendVBlockHeight + legendVGap)" width="22" :height="legendVBlockHeight" :fill="robustnessColorStyle(val, promptRobustnessRange[0], promptRobustnessRange[1]).color" stroke="#ccc" rx="2" />
                      <text x="35" :y="10 + idx * (legendVBlockHeight + legendVGap) + legendVBlockHeight + 18" font-size="12" fill="#222" text-anchor="middle">{{ legendVLabelsPrompt[idx] }}</text>
                    </g>
                  </svg>
                </div>
                
                <div class="legend-section">
                  <!-- <h4>Corpus图例</h4> -->
                  <svg :width="80" :height="legendVHeight">
                    <g v-for="(val, idx) in legendVValuesCorpus" :key="idx">
                      <rect x="26" :y="15 + idx * (legendVBlockHeight + legendVGap)" width="22" :height="legendVBlockHeight" :fill="robustnessColorStyle(val, corpusRobustnessRange[0], corpusRobustnessRange[1]).color" stroke="#ccc" rx="2" />
                      <text x="35" :y="10 + idx * (legendVBlockHeight + legendVGap) + legendVBlockHeight + 18" font-size="12" fill="#222" text-anchor="middle">{{ legendVLabelsCorpus[idx] }}</text>
                    </g>
                  </svg>
                </div>
              </div>
            </div>
            <!-- B区：Corpus投影 -->
            <div class="projection-panel">
              <div class="panel-header">
                  Corpus 投影
                  <div class="panel-tools">
                    <button
                      class="tool-btn"
                      :class="{active: corpusDragMode}"
                      @click="toggleCorpusDrag"
                    >拖拽</button>
                    <button
                      class="tool-btn"
                      :class="{active: corpusLassoMode}"
                      @click="toggleCorpusLasso"
                    >套索</button>
                    <button
                      class="tool-btn"
                      @click="zoomCorpusIn"
                      title="放大投影点"
                    >放大</button>
                    <button
                      class="tool-btn"
                      @click="zoomCorpusOut"
                      title="缩小投影点"
                    >缩小</button>
                    <button
                      class="tool-btn select-btn"
                      :class="{active: corpusLassoMode && corpusLassoResults.length > 0}"
                      @click="applyCorpusLassoSelection"
                      :disabled="!corpusLassoMode || corpusLassoResults.length === 0 || loading"
                      title="应用套索选择"
                    >
                      <el-icon v-if="loading"><Loading /></el-icon>
                      <span v-else>选择</span>
                    </button>
                  </div>
                </div>
              <div class="panel-content">
                <svg
                  width="100%"
                  height="100%"
                  viewBox="0 0 400 300"
                  @mousedown="corpusDragMode ? onCorpusSvgMousedown($event) : (corpusLassoMode ? onCorpusLassoDown($event) : null)"
                  @wheel="corpusDragMode ? onCorpusSvgWheel($event) : null"
                  @click="hideCorpusTooltip"
                >
                                    <g :transform="corpusTransform">
                    <g v-for="item in currentCorpus" :key="item.id">
                      <circle
                        v-if="item.x !== null && item.y !== null"
                        :cx="projectX(item.x, 'corpus')"
                        :cy="projectY(item.y, 'corpus')"
                        :r="2.5 * corpusPointScale"
                        :fill="robustnessColorStyle(item.robustness, corpusRobustnessRange[0], corpusRobustnessRange[1]).color"
                        :stroke="selectedCorpusId === item.id ? '#222' : 'none'"
                        :stroke-width="selectedCorpusId === item.id ? 2 : 0"
                        style="cursor:pointer"
                        @click.stop="showCorpusTooltip(item, $event)"
                      />
                    </g>
                  </g>

                  <polyline v-if="corpusLassoPoints.length" :points="corpusLassoPoints.map(p=>p.join(',')).join(' ')" fill="none" stroke="#999" stroke-width="2" stroke-dasharray="5,5" />
                  <!-- 套索结果弹出框 -->

                  <defs>
                    <filter id="shadow-corpus" x="-20%" y="-20%" width="140%" height="140%">
                      <feDropShadow dx="2" dy="2" stdDeviation="2" flood-color="#bbb"/>
                    </filter>
                  </defs>
                </svg>

              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="globalHistoryPanelOpen" 
           class="global-history-panel-side draggable-panel"
           :style="{ left: panelX + 'px', top: panelY + 'px', width: panelWidth + 'px', height: panelHeight + 'px' }"
           :class="{ 'is-dragging': isDragging }">
        <!-- 调整大小手柄 -->
        <div class="resize-handle nw" @mousedown="startResizeHistory('nw', $event)"></div>
        <div class="resize-handle ne" @mousedown="startResizeHistory('ne', $event)"></div>
        <div class="resize-handle sw" @mousedown="startResizeHistory('sw', $event)"></div>
        <div class="resize-handle se" @mousedown="startResizeHistory('se', $event)"></div>
        <div class="resize-handle n" @mousedown="startResizeHistory('n', $event)"></div>
        <div class="resize-handle s" @mousedown="startResizeHistory('s', $event)"></div>
        <div class="resize-handle w" @mousedown="startResizeHistory('w', $event)"></div>
        <div class="resize-handle e" @mousedown="startResizeHistory('e', $event)"></div>
        <div class="history-header drag-handle" @mousedown="startDrag">
          <div class="drag-indicator">⋮⋮</div>
          <h4>历史记录</h4>
          <button class="close-history" @click="toggleHistoryPanelGlobal">×</button>
        </div>
        <div class="history-list">
          <!-- 表头 -->
          <div class="history-table-header">
            <div class="header-cell id-cell">ID</div>
            <div class="header-cell time-cell">时间</div>
            <div class="header-cell prompt-cell">Prompt选择</div>
            <div class="header-cell corpus-cell">Corpus选择</div>
            <div class="header-cell attack-cell">攻击方法</div>
            <div class="header-cell action-cell">操作</div>
          </div>
          <!-- 记录行 -->
          <div v-for="(record, index) in globalFeatureHistory"
               :key="'global-history-'+index"
               class="history-table-row">
            <!-- ID列 -->
            <div class="table-cell id-cell">
              {{ index + 1 }}
            </div>
            <!-- 时间列 -->
            <div class="table-cell time-cell">
              <template v-if="editingGlobalHistoryName === index">
                <input v-model="record.name"
                       @blur="saveGlobalHistoryName(index, record.name)"
                       @keyup.enter="saveGlobalHistoryName(index, record.name)"
                       class="history-name-input" />
              </template>
              <template v-else>
                <span @click="editGlobalHistoryName(index)" class="editable-time">
                  {{ record.name || formatTime(record.timestamp) }}
                </span>
              </template>
            </div>
            <!-- Prompt选择列 -->
            <div class="table-cell prompt-cell">
              <div class="selection-summary" @click="toggleHistoryDropdown(index, 'prompt')">
                <span class="count">{{ record.features.promptFeatures.length }}项</span>
                <span class="dropdown-icon" :class="{ open: openHistoryDropdowns[index]?.prompt }">▼</span>
              </div>
              <div v-if="openHistoryDropdowns[index]?.prompt" class="dropdown-content">
                <div v-for="(featureGroup, featureName) in groupFeatures(record.features.promptFeatures)"
                     :key="'prompt-'+featureName"
                     class="feature-group">
                  <div class="feature-name">{{ featureName }} ({{ featureGroup.length }})</div>
                  <div class="feature-items">
                    <span v-for="(feature, idx) in featureGroup"
                          :key="idx"
                          class="feature-item">
                      {{ feature.valueRange }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <!-- Corpus选择列 -->
            <div class="table-cell corpus-cell">
              <div class="selection-summary" @click="toggleHistoryDropdown(index, 'corpus')">
                <span class="count">{{ record.features.corpusFeatures.length }}项</span>
                <span class="dropdown-icon" :class="{ open: openHistoryDropdowns[index]?.corpus }">▼</span>
              </div>
              <div v-if="openHistoryDropdowns[index]?.corpus" class="dropdown-content">
                <div v-for="(featureGroup, featureName) in groupFeatures(record.features.corpusFeatures)"
                     :key="'corpus-'+featureName"
                     class="feature-group">
                  <div class="feature-name">{{ featureName }} ({{ featureGroup.length }})</div>
                  <div class="feature-items">
                    <span v-for="(feature, idx) in featureGroup"
                          :key="idx"
                          class="feature-item">
                      {{ feature.valueRange }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <!-- 攻击方法列 -->
            <div class="table-cell attack-cell">
              <div class="selection-summary" @click="toggleHistoryDropdown(index, 'attack')">
                <span class="count">{{ (record.attackMethods || []).length }}项</span>
                <span class="dropdown-icon" :class="{ open: openHistoryDropdowns[index]?.attack }">▼</span>
              </div>
              <div v-if="openHistoryDropdowns[index]?.attack" class="dropdown-content">
                <div v-if="(record.attackMethods || []).length === 0" class="no-attack-methods">
                  未选择攻击方法
                </div>
                <div v-else class="attack-methods">
                  <span v-for="method in record.attackMethods"
                        :key="method"
                        class="attack-method-item">
                    {{ getAttackMethodName(method) }}
                  </span>
                </div>
              </div>
            </div>
            <!-- 操作列 -->
            <div class="table-cell action-cell">
              <button class="history-apply-btn"
                      @click="applyGlobalHistoryRecord(index)"
                      :disabled="globalHistoryApplyLoading === index"
                      title="应用此记录">
                <el-icon v-if="globalHistoryApplyLoading === index"><Loading /></el-icon>
                <el-icon v-else><Check /></el-icon>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 底部：corpus特征图 -->
    <div class="bottom-feature">
      <div class="feature-container" data-container="corpus" style="width: 100%; position: relative;">
        <!-- 特征图表加载遮罩 -->
        <div v-if="loading" class="feature-loading-overlay">
          <div class="feature-loading-spinner">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <div class="loading-text">特征数据加载中...</div>
          </div>
        </div>
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
  
  <!-- 全局弹出框 -->
  <!-- Prompt投影点弹窗 -->
  <div 
      v-if="promptTooltip.visible"
      class="global-popup prompt-tooltip"
      :style="{
        left: promptTooltip.screenX + 'px',
        top: promptTooltip.screenY + 'px',
        width: promptTooltip.width + 'px',
        height: promptTooltip.height + 'px'
      }"
      @mousedown.stop
      @click.stop
    >
    <div class="resize-handle nw" @mousedown="startResize(promptTooltip, 'nw', $event)"></div>
    <div class="resize-handle ne" @mousedown="startResize(promptTooltip, 'ne', $event)"></div>
    <div class="resize-handle sw" @mousedown="startResize(promptTooltip, 'sw', $event)"></div>
    <div class="resize-handle se" @mousedown="startResize(promptTooltip, 'se', $event)"></div>
    <div class="resize-handle n" @mousedown="startResize(promptTooltip, 'n', $event)"></div>
    <div class="resize-handle s" @mousedown="startResize(promptTooltip, 's', $event)"></div>
    <div class="resize-handle w" @mousedown="startResize(promptTooltip, 'w', $event)"></div>
    <div class="resize-handle e" @mousedown="startResize(promptTooltip, 'e', $event)"></div>

    <div class="popup-header" @mousedown="startGlobalTooltipDrag(promptTooltip, $event)">
      <span class="popup-title">投影点详情</span>
      <button @click.stop="closePromptTooltip" @mousedown.stop class="popup-close">×</button>
    </div>
    <div class="popup-content">
      <div class="popup-row">
        <span class="popup-label">ID: {{ promptTooltip.data.id }}</span>
        <span class="popup-value">{{ promptTooltip.data.robustness }}</span>
      </div>
      <div class="popup-text">{{ promptTooltip.data.text }}</div>
    </div>
  </div>

  <!-- Corpus投影点弹窗 -->
  <div 
    v-if="corpusTooltip.visible"
    class="global-popup corpus-tooltip"
    :style="{
      left: corpusTooltip.screenX + 'px',
      top: corpusTooltip.screenY + 'px',
      width: corpusTooltip.width + 'px',
      height: corpusTooltip.height + 'px'
    }"
    @mousedown.stop
    @click.stop
  >
    <div class="resize-handle nw" @mousedown="startResize(corpusTooltip, 'nw', $event)"></div>
    <div class="resize-handle ne" @mousedown="startResize(corpusTooltip, 'ne', $event)"></div>
    <div class="resize-handle sw" @mousedown="startResize(corpusTooltip, 'sw', $event)"></div>
    <div class="resize-handle se" @mousedown="startResize(corpusTooltip, 'se', $event)"></div>
    <div class="resize-handle n" @mousedown="startResize(corpusTooltip, 'n', $event)"></div>
    <div class="resize-handle s" @mousedown="startResize(corpusTooltip, 's', $event)"></div>
    <div class="resize-handle w" @mousedown="startResize(corpusTooltip, 'w', $event)"></div>
    <div class="resize-handle e" @mousedown="startResize(corpusTooltip, 'e', $event)"></div>

    <div class="popup-header" @mousedown="startGlobalTooltipDrag(corpusTooltip, $event)">
      <span class="popup-title">投影点详情</span>
      <button @click.stop="closeCorpusTooltip" @mousedown.stop class="popup-close">×</button>
    </div>
    <div class="popup-content">
      <div class="popup-row">
        <span class="popup-label">ID: {{ corpusTooltip.data.id }}</span>
        <span class="popup-value">{{ corpusTooltip.data.robustness }}</span>
      </div>
      <div class="popup-text">{{ corpusTooltip.data.text }}</div>
    </div>
  </div>

  <!-- Prompt套索结果弹窗 -->
  <div 
    v-if="promptLassoPopup.visible"
    class="global-popup lasso-popup prompt-lasso"
    :style="{
      left: promptLassoPopup.x + 'px',
      top: promptLassoPopup.y + 'px',
      width: promptLassoPopup.width + 'px',
      height: promptLassoPopup.height + 'px'
    }"
    @mousedown.stop
    @click.stop
  >
    <div class="resize-handle nw" @mousedown="startResize(promptLassoPopup, 'nw', $event)"></div>
    <div class="resize-handle ne" @mousedown="startResize(promptLassoPopup, 'ne', $event)"></div>
    <div class="resize-handle sw" @mousedown="startResize(promptLassoPopup, 'sw', $event)"></div>
    <div class="resize-handle se" @mousedown="startResize(promptLassoPopup, 'se', $event)"></div>
    <div class="resize-handle n" @mousedown="startResize(promptLassoPopup, 'n', $event)"></div>
    <div class="resize-handle s" @mousedown="startResize(promptLassoPopup, 's', $event)"></div>
    <div class="resize-handle w" @mousedown="startResize(promptLassoPopup, 'w', $event)"></div>
    <div class="resize-handle e" @mousedown="startResize(promptLassoPopup, 'e', $event)"></div>

    <div class="popup-header" @mousedown="startGlobalLassoPopupDrag(promptLassoPopup, $event)">
      <span class="popup-title">套索选中 ({{ promptLassoPopup.data.length }}项)</span>
      <button class="sort-btn" @click="cyclePromptLassoSort" :title="promptLassoSortState==='robustnessDesc'?'鲁棒性降序':promptLassoSortState==='robustnessAsc'?'鲁棒性升序':'ID排序'">
        <el-icon>
          <Sort v-if="promptLassoSortState==='robustnessDesc'" />
          <Sort v-else-if="promptLassoSortState==='robustnessAsc'" style="transform:rotate(180deg)" />
          <Sort v-else style="color:#bbb" />
        </el-icon>
      </button>
      <button @click.stop="closePromptLassoPopup" @mousedown.stop class="popup-close">×</button>
    </div>
    <div class="popup-content-split" @mousedown.stop>
      <!-- 左侧：特征统计信息 -->
      <div class="popup-left-panel">
        <div v-if="promptLassoPopup.featureStats" class="feature-stats-section">
          <div class="stats-header">特征统计</div>
          <!-- 调试信息 -->
          <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
            调试: featureStats存在，连续特征: {{ Object.keys(promptLassoPopup.featureStats.continuous || {}).length }}个，
            离散特征: {{ Object.keys(promptLassoPopup.featureStats.discrete || {}).length }}个
          </div>
          
          <!-- 连续特征统计 -->
          <div v-if="Object.keys(promptLassoPopup.featureStats.continuous).length > 0" class="stats-block">
            <div class="stats-subheader">连续特征</div>
            <div v-for="(stats, featureName) in promptLassoPopup.featureStats.continuous" :key="'continuous-'+featureName" class="stats-item">
              <div class="stats-feature-name">{{ featureName }}</div>
              <div class="stats-values">
                <span class="stats-value">平均: {{ stats.average }}</span>
                <span class="stats-value">范围: {{ stats.min }}~{{ stats.max }}</span>
                <span class="stats-value">标准差: {{ stats.std }}</span>
              </div>
            </div>
          </div>
          
          <!-- 离散特征统计 -->
          <div v-if="Object.keys(promptLassoPopup.featureStats.discrete).length > 0" class="stats-block">
            <div class="stats-subheader">离散特征</div>
            <div v-for="(stats, featureName) in promptLassoPopup.featureStats.discrete" :key="'discrete-'+featureName" class="stats-item">
              <div class="stats-feature-name">{{ featureName }}</div>
              <div class="stats-distribution">
                <div v-for="item in stats.distribution.slice(0, 3)" :key="'dist-'+item.value" class="dist-item">
                  <span class="dist-value">{{ getDiscreteFeatureDescription(featureName, item.value, 'prompt') }}</span>
                  <span class="dist-count">{{ item.count }}({{ item.percentage }}%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧：项目列表 -->
      <div class="popup-right-panel">
        <div class="items-header">选中项目 ({{ promptLassoPopup.data.length }})</div>
        <div class="items-scroll-area">
      <div v-for="(item, index) in sortedPromptLassoData" :key="'lasso-prompt-'+index" class="popup-item" @click="showPromptTooltipFromLasso(item, $event)">
        <div class="popup-row">
          <span class="popup-label">ID: {{ item.id }}</span>
          <span class="popup-value">{{ item.robustness.toFixed(4) }}</span>
        </div>
        <div class="popup-text">{{ item.text }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Corpus套索结果弹窗 -->
  <div 
    v-if="corpusLassoPopup.visible"
    class="global-popup lasso-popup corpus-lasso"
    :style="{
      left: corpusLassoPopup.x + 'px',
      top: corpusLassoPopup.y + 'px',
      width: corpusLassoPopup.width + 'px',
      height: corpusLassoPopup.height + 'px'
    }"
    @mousedown.stop
    @click.stop
  > 
    <div class="resize-handle nw" @mousedown="startResize(corpusLassoPopup, 'nw', $event)"></div>
    <div class="resize-handle ne" @mousedown="startResize(corpusLassoPopup, 'ne', $event)"></div>
    <div class="resize-handle sw" @mousedown="startResize(corpusLassoPopup, 'sw', $event)"></div>
    <div class="resize-handle se" @mousedown="startResize(corpusLassoPopup, 'se', $event)"></div>
    <div class="resize-handle n" @mousedown="startResize(corpusLassoPopup, 'n', $event)"></div>
    <div class="resize-handle s" @mousedown="startResize(corpusLassoPopup, 's', $event)"></div>
    <div class="resize-handle w" @mousedown="startResize(corpusLassoPopup, 'w', $event)"></div>
    <div class="resize-handle e" @mousedown="startResize(corpusLassoPopup, 'e', $event)"></div>

    <div class="popup-header" @mousedown="startGlobalLassoPopupDrag(corpusLassoPopup, $event)">
      <span class="popup-title">套索选中 ({{ corpusLassoPopup.data.length }}项)</span>
      <button class="sort-btn" @click="cycleCorpusLassoSort" :title="corpusLassoSortState==='robustnessDesc'?'鲁棒性降序':corpusLassoSortState==='robustnessAsc'?'鲁棒性升序':'ID排序'">
        <el-icon>
          <Sort v-if="corpusLassoSortState==='robustnessDesc'" />
          <Sort v-else-if="corpusLassoSortState==='robustnessAsc'" style="transform:rotate(180deg)" />
          <Sort v-else style="color:#bbb" />
        </el-icon>
      </button>
      <button @click.stop="closeCorpusLassoPopup" @mousedown.stop class="popup-close">×</button>
    </div>
    <div class="popup-content-split" @mousedown.stop>
      <!-- 左侧：特征统计信息 -->
      <div class="popup-left-panel">
        <div v-if="corpusLassoPopup.featureStats" class="feature-stats-section">
          <div class="stats-header">特征统计</div>
          <!-- 调试信息 -->
          <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
            调试: featureStats存在，连续特征: {{ Object.keys(corpusLassoPopup.featureStats.continuous || {}).length }}个，
            离散特征: {{ Object.keys(corpusLassoPopup.featureStats.discrete || {}).length }}个
          </div>
          
          <!-- 连续特征统计 -->
          <div v-if="Object.keys(corpusLassoPopup.featureStats.continuous).length > 0" class="stats-block">
            <div class="stats-subheader">连续特征</div>
            <div v-for="(stats, featureName) in corpusLassoPopup.featureStats.continuous" :key="'continuous-'+featureName" class="stats-item">
              <div class="stats-feature-name">{{ featureName }}</div>
              <div class="stats-values">
                <span class="stats-value">平均: {{ stats.average }}</span>
                <span class="stats-value">范围: {{ stats.min }}~{{ stats.max }}</span>
                <span class="stats-value">标准差: {{ stats.std }}</span>
              </div>
            </div>
          </div>
          
          <!-- 离散特征统计 -->
          <div v-if="Object.keys(corpusLassoPopup.featureStats.discrete).length > 0" class="stats-block">
            <div class="stats-subheader">离散特征</div>
            <div v-for="(stats, featureName) in corpusLassoPopup.featureStats.discrete" :key="'discrete-'+featureName" class="stats-item">
              <div class="stats-feature-name">{{ featureName }}</div>
              <div class="stats-distribution">
                <div v-for="item in stats.distribution.slice(0, 3)" :key="'dist-'+item.value" class="dist-item">
                  <span class="dist-value">{{ getDiscreteFeatureDescription(featureName, item.value, 'corpus') }}</span>
                  <span class="dist-count">{{ item.count }}({{ item.percentage }}%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧：项目列表 -->
      <div class="popup-right-panel">
        <div class="items-header">选中项目 ({{ corpusLassoPopup.data.length }})</div>
        <div class="items-scroll-area">
      <div v-for="(item, index) in sortedCorpusLassoData" :key="'lasso-corpus-'+index" class="popup-item" @click="showCorpusTooltipFromLasso(item, $event)">
        <div class="popup-row">
          <span class="popup-label">ID: {{ item.id }}</span>
          <span class="popup-value">{{ item.robustness.toFixed(4) }}</span>
        </div>
        <div class="popup-text">{{ item.text }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as d3 from 'd3'
import { ref, onMounted, onBeforeUnmount, watch,nextTick, computed, reactive } from 'vue'
import { toRaw } from 'vue'
import { Check, Delete, Refresh, Timer, Edit, Loading, Sort } from '@element-plus/icons-vue'
import { ref as vueRef } from 'vue'


// 添加缺失的变量定义
const selectedPromptId = ref(null)
const selectedCorpusId = ref(null)

const promptDragMode = ref(false)
const promptLassoMode = ref(false)
const corpusDragMode = ref(false)
const corpusLassoMode = ref(false)

// 投影点缩放比例
const promptPointScale = ref(1.0)
const corpusPointScale = ref(1.0)

function togglePromptDrag() {
  if (!promptDragMode.value) {
    promptDragMode.value = true
    promptLassoMode.value = false
  } else {
    promptDragMode.value = false
  }
}
function togglePromptLasso() {
  if (!promptLassoMode.value) {
    promptLassoMode.value = true
    promptDragMode.value = false
    // 清除之前的结果
    promptLassoPoints.value = []
    promptLassoResults.value = []
    promptLassoPopup.visible = false
    promptLassoPopup.x = 0
    promptLassoPopup.y = 0
    promptLassoPopup.data = []
    promptLassoPopup.featureStats = null
  } else {
    promptLassoMode.value = false
    // 清除套索痕迹和弹出框
    promptLassoPoints.value = []
    promptLassoResults.value = []
    promptLassoPopup.visible = false
    promptLassoPopup.x = 0
    promptLassoPopup.y = 0
    promptLassoPopup.data = []
    promptLassoPopup.featureStats = null
  }
}
// corpus区同理
function toggleCorpusDrag() {
  if (!corpusDragMode.value) {
    corpusDragMode.value = true
    corpusLassoMode.value = false
  } else {
    corpusDragMode.value = false
  }
}
function toggleCorpusLasso() {
  if (!corpusLassoMode.value) {
    corpusLassoMode.value = true
    corpusDragMode.value = false
    // 清除之前的结果
    corpusLassoPoints.value = []
    corpusLassoResults.value = []
    corpusLassoPopup.visible = false
    corpusLassoPopup.x = 0
    corpusLassoPopup.y = 0
    corpusLassoPopup.data = []
    corpusLassoPopup.featureStats = null
  } else {
    corpusLassoMode.value = false
    // 清除套索痕迹和弹出框
    corpusLassoPoints.value = []
    corpusLassoResults.value = []
    corpusLassoPopup.visible = false
    corpusLassoPopup.x = 0
    corpusLassoPopup.y = 0
    corpusLassoPopup.data = []
    corpusLassoPopup.featureStats = null
  }
}

// 投影点缩放函数
function zoomPromptIn() {
  promptPointScale.value = Math.min(promptPointScale.value * 1.2, 3.0) // 最大放大3倍
}

function zoomPromptOut() {
  promptPointScale.value = Math.max(promptPointScale.value / 1.2, 0.3) // 最小缩小到0.3倍
}

function zoomCorpusIn() {
  corpusPointScale.value = Math.min(corpusPointScale.value * 1.2, 3.0) // 最大放大3倍
}

function zoomCorpusOut() {
  corpusPointScale.value = Math.max(corpusPointScale.value / 1.2, 0.3) // 最小缩小到0.3倍
}

const promptTransform = ref('translate(0,0) scale(1)')
let dragStart = null, dragLast = null, promptScale = 1, promptOffset = {x:0, y:0}

// 节流工具函数
function throttle(fn, delay) {
  let last = 0;
  return function(...args) {
    const now = Date.now();
    if (now - last > delay) {
      last = now;
      fn.apply(this, args);
    }
  };
}

function onPromptSvgMousedown(e) {
  if (!promptDragMode.value) return
  const svg = e.currentTarget
  const pt = svg.createSVGPoint()
  pt.x = e.clientX
  pt.y = e.clientY
  const svgP = pt.matrixTransform(svg.getScreenCTM().inverse())
  dragStart = {x: svgP.x, y: svgP.y}
  dragLast = {...promptOffset}
  window.addEventListener('mousemove', throttledPromptMousemove)
  window.addEventListener('mouseup', onPromptSvgMouseup)
}
const throttledPromptMousemove = throttle(onPromptSvgMousemove, 16)

function onPromptSvgMousemove(e) {
  if (!dragStart) return
  const svg = document.querySelector('.projection-panel:first-child svg')
  if (!svg) return
  const pt = svg.createSVGPoint()
  pt.x = e.clientX
  pt.y = e.clientY
  const svgP = pt.matrixTransform(svg.getScreenCTM().inverse())
  const dx = svgP.x - dragStart.x
  const dy = svgP.y - dragStart.y
  promptOffset.x = dragLast.x + dx
  promptOffset.y = dragLast.y + dy
  updatePromptTransform()
}
function onPromptSvgMouseup() {
  dragStart = null
  window.removeEventListener('mousemove', throttledPromptMousemove)
  window.removeEventListener('mouseup', onPromptSvgMouseup)
}
function onPromptSvgWheel(e) {
  if (!promptDragMode.value) return
  e.preventDefault()
  promptScale *= e.deltaY < 0 ? 1.1 : 0.9
  updatePromptTransform()
}
function updatePromptTransform() {
  promptTransform.value = `translate(${promptOffset.x},${promptOffset.y}) scale(${promptScale})`
}

const corpusTransform = ref('translate(0,0) scale(1)')
let corpusdragStart = null, corpusdragLast = null, corpusScale = 1, corpusOffset = {x:0, y:0}

function onCorpusSvgMousedown(e) {
  if (!corpusDragMode.value) return
  const svg = e.currentTarget
  const pt = svg.createSVGPoint()
  pt.x = e.clientX
  pt.y = e.clientY
  const svgP = pt.matrixTransform(svg.getScreenCTM().inverse())
  corpusdragStart = {x: svgP.x, y: svgP.y}
  corpusdragLast = {...corpusOffset}
  window.addEventListener('mousemove', throttledCorpusMousemove)
  window.addEventListener('mouseup', onCorpusSvgMouseup)
}
const throttledCorpusMousemove = throttle(onCorpusSvgMousemove, 16)

function onCorpusSvgMousemove(e) {
  if (!corpusdragStart) return
  const svg = document.querySelector('.projection-panel:last-child svg')
  if (!svg) return
  const pt = svg.createSVGPoint()
  pt.x = e.clientX
  pt.y = e.clientY
  const svgP = pt.matrixTransform(svg.getScreenCTM().inverse())
  const dx = svgP.x - corpusdragStart.x
  const dy = svgP.y - corpusdragStart.y
  corpusOffset.x = corpusdragLast.x + dx
  corpusOffset.y = corpusdragLast.y + dy
  updateCorpusTransform()
}
function onCorpusSvgMouseup() {
  corpusdragStart = null
  window.removeEventListener('mousemove', throttledCorpusMousemove)
  window.removeEventListener('mouseup', onCorpusSvgMouseup)
}
function onCorpusSvgWheel(e) {
  if (!corpusDragMode.value) return
  e.preventDefault()
  corpusScale *= e.deltaY < 0 ? 1.1 : 0.9
  updateCorpusTransform()
}
function updateCorpusTransform() {
  corpusTransform.value = `translate(${corpusOffset.x},${corpusOffset.y}) scale(${corpusScale})`
}


const promptLassoPoints = ref([])
const promptLassoResults = ref([])

function onPromptLassoDown(e) {
  if (!promptLassoMode.value) return
  // 清除之前的套索痕迹和弹出框
  promptLassoPoints.value = []
  promptLassoResults.value = []
  promptLassoPopup.visible = false
  promptLassoPopup.x = 0
  promptLassoPopup.y = 0
  promptLassoPopup.data = []
  promptLassoPopup.featureStats = null
  
  const svg = e.currentTarget
  const pt = svg.createSVGPoint()
  pt.x = e.clientX
  pt.y = e.clientY
  // 反算到SVG坐标（考虑当前transform）
  const ctm = svg.getScreenCTM()
  const inv = ctm.inverse()
  const svgP = pt.matrixTransform(inv)
  promptLassoPoints.value = [[svgP.x, svgP.y]]
  window.addEventListener('mousemove', onPromptLassoMove)
  window.addEventListener('mouseup', onPromptLassoUp)
}
function onPromptLassoMove(e) {
  const svg = document.querySelector('.projection-panel:first-child svg')
  if (!svg) return
  const pt = svg.createSVGPoint()
  pt.x = e.clientX
  pt.y = e.clientY
  // 反算到SVG坐标（考虑当前transform）
  const ctm = svg.getScreenCTM()
  const inv = ctm.inverse()
  const svgP = pt.matrixTransform(inv)
  promptLassoPoints.value.push([svgP.x, svgP.y])
}
function onPromptLassoUp() {
  window.removeEventListener('mousemove', onPromptLassoMove)
  window.removeEventListener('mouseup', onPromptLassoUp)
  // 确保套索至少有3个点才进行判断
  if (promptLassoPoints.value.length < 3) {
    promptLassoPoints.value = []
    promptLassoResults.value = []
    promptLassoPopup.featureStats = null
    return
  }
  // 判断哪些点在套索内
  const poly = promptLassoPoints.value
  const insideItems = currentPrompts.value.filter(item => {
    const x = item.x
    const y = item.y
    if (x === null || y === null) return false
    // 将原始数据坐标投影到SVG坐标（考虑当前缩放/平移）
    const svgX = projectX(x, 'prompt') * promptScale + promptOffset.x
    const svgY = projectY(y, 'prompt') * promptScale + promptOffset.y
    return pointInPolygon([svgX, svgY], poly)
  })
  if (insideItems.length > 0) {
    // 计算套索中心点用于显示弹出框
    const centerX = poly.reduce((sum, p) => sum + p[0], 0) / poly.length
    const centerY = poly.reduce((sum, p) => sum + p[1], 0) / poly.length
    // 确保弹出框不会超出边界
    const popupWidth = 600
    const popupHeight = Math.min(500, Math.max(400, insideItems.length * 15 + 100))
    const adjustedX = Math.max(20, Math.min(centerX, 400 - popupWidth - 20))
    const adjustedY = Math.max(popupHeight + 20, Math.min(centerY, 300 - 20))
    promptLassoResults.value = insideItems
    const newData = insideItems.map(item => ({
      id: item.id,
      text: item.text,
      robustness: item.robustness,
      features: item.features // 添加特征信息
    }))
    promptLassoPopup.data = newData
    const svg = document.querySelector('.projection-panel:first-child svg')
    if (!svg) return
    const rect = svg.getBoundingClientRect()
    promptLassoPopup.x = rect.left + adjustedX
    promptLassoPopup.y = rect.top + adjustedY
    promptLassoPopup.visible = true
    
    // 新增：计算并高亮特征统计
    const lassoStats = calculateLassoFeatureStats(insideItems, 'prompt')
    console.log('Prompt套索特征统计:', lassoStats)
    if (lassoStats) {
      highlightLassoFeatureStats(lassoStats, 'prompt')
      // 将统计信息存储到弹窗中供显示
      promptLassoPopup.featureStats = lassoStats
      console.log('已设置promptLassoPopup.featureStats:', promptLassoPopup.featureStats)
    }
  } else {
    promptLassoPoints.value = []
    promptLassoResults.value = []
    promptLassoPopup.featureStats = null
  }
}
// 判断点是否在多边形内
function pointInPolygon(point, vs) {
  let x = point[0], y = point[1], inside = false
  for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
    let xi = vs[i][0], yi = vs[i][1]
    let xj = vs[j][0], yj = vs[j][1]
    let intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi)
    if (intersect) inside = !inside
  }
  return inside
}



const corpusLassoPoints = ref([])
const corpusLassoResults = ref([])
// const corpusLassoPopup = reactive({ visible: false, x: 0, y: 0, data: [], isDragging: false, isActuallyDragging: false, dragStartX: 0, dragStartY: 0 })

function onCorpusLassoDown(e) {
  if (!corpusLassoMode.value) return
  corpusLassoPoints.value = []
  corpusLassoResults.value = []
  corpusLassoPopup.visible = false
  corpusLassoPopup.x = 0
  corpusLassoPopup.y = 0
  corpusLassoPopup.data = []
  corpusLassoPopup.featureStats = null
  const svg = e.currentTarget
  const pt = svg.createSVGPoint()
  pt.x = e.clientX
  pt.y = e.clientY
  // 反算到SVG坐标（考虑当前transform）
  const ctm = svg.getScreenCTM()
  const inv = ctm.inverse()
  const svgP = pt.matrixTransform(inv)
  corpusLassoPoints.value = [[svgP.x, svgP.y]]
  window.addEventListener('mousemove', onCorpusLassoMove)
  window.addEventListener('mouseup', onCorpusLassoUp)
}
function onCorpusLassoMove(e) {
  const svg = document.querySelector('.projection-panel:last-child svg')
  if (!svg) return
  const pt = svg.createSVGPoint()
  pt.x = e.clientX
  pt.y = e.clientY
  // 反算到SVG坐标（考虑当前transform）
  const ctm = svg.getScreenCTM()
  const inv = ctm.inverse()
  const svgP = pt.matrixTransform(inv)
  corpusLassoPoints.value.push([svgP.x, svgP.y])
}
function onCorpusLassoUp() {
  window.removeEventListener('mousemove', onCorpusLassoMove)
  window.removeEventListener('mouseup', onCorpusLassoUp)
  if (corpusLassoPoints.value.length < 3) {
    corpusLassoPoints.value = []
    corpusLassoResults.value = []
    corpusLassoPopup.featureStats = null
    return
  }
  const poly = corpusLassoPoints.value
  const insideItems = currentCorpus.value.filter(item => {
    const x = item.x
    const y = item.y
    if (x === null || y === null) return false
    // 将原始数据坐标投影到SVG坐标（考虑当前缩放/平移）
    const svgX = projectX(x, 'corpus') * corpusScale + corpusOffset.x
    const svgY = projectY(y, 'corpus') * corpusScale + corpusOffset.y
    return pointInPolygon([svgX, svgY], poly)
  })
  if (insideItems.length > 0) {
    const centerX = poly.reduce((sum, p) => sum + p[0], 0) / poly.length
    const centerY = poly.reduce((sum, p) => sum + p[1], 0) / poly.length
    const popupWidth = 600
    const popupHeight = Math.min(500, Math.max(400, insideItems.length * 15 + 100))
    const adjustedX = Math.max(20, Math.min(centerX, 400 - popupWidth - 20))
    const adjustedY = Math.max(popupHeight + 20, Math.min(centerY, 300 - 20))
    corpusLassoResults.value = insideItems
    const svg = document.querySelector('.projection-panel:last-child svg')
    if (!svg) return
    corpusLassoPopup.x = svg.getBoundingClientRect().left + adjustedX
    corpusLassoPopup.y = svg.getBoundingClientRect().top + adjustedY
    corpusLassoPopup.visible = true
    corpusLassoPopup.data = insideItems.map(item => ({
      id: item.id,
      text: item.text,
      robustness: item.robustness,
      features: item.features // 添加特征信息
    }))
    
    // 新增：计算并高亮特征统计
    const lassoStats = calculateLassoFeatureStats(insideItems, 'corpus')
    console.log('Corpus套索特征统计:', lassoStats)
    if (lassoStats) {
      highlightLassoFeatureStats(lassoStats, 'corpus')
      // 将统计信息存储到弹窗中供显示
      corpusLassoPopup.featureStats = lassoStats
      console.log('已设置corpusLassoPopup.featureStats:', corpusLassoPopup.featureStats)
    }
  } else {
    corpusLassoPoints.value = []
    corpusLassoResults.value = []
    corpusLassoPopup.featureStats = null
  }
}

// 新增：应用Prompt套索选择
async function applyPromptLassoSelection() {
  if (!promptLassoMode.value || promptLassoResults.value.length === 0) return
  
  loading.value = true
  try {
    // 获取套索选中的prompt IDs
    const selectedPromptIds = promptLassoResults.value.map(item => item.id)
    
    // 更新promptIds为套索选中的ID
    promptIds.value = selectedPromptIds
    
    // 重新获取数据
    await Promise.all([
      fetchTextData(),
      fetchFeatureDistribution(),
      fetchCorpusFeatureDistribution()
    ])
    
    // 清除套索状态
    promptLassoMode.value = false
    promptLassoPoints.value = []
    promptLassoResults.value = []
    promptLassoPopup.visible = false
    promptLassoPopup.featureStats = null
    
    // 清除特征高亮
    clearFeatureHighlights('prompt')
    
    console.log(`已应用Prompt套索选择，选中${selectedPromptIds.length}个项目`)
  } catch (error) {
    console.error('应用Prompt套索选择失败:', error)
  } finally {
    loading.value = false
  }
}

// 新增：应用Corpus套索选择
async function applyCorpusLassoSelection() {
  if (!corpusLassoMode.value || corpusLassoResults.value.length === 0) return
  
  loading.value = true
  try {
    // 获取套索选中的corpus IDs
    const selectedCorpusIds = corpusLassoResults.value.map(item => item.id)
    
    // 更新corpusIds为套索选中的ID
    corpusIds.value = selectedCorpusIds
    
    // 重新获取数据
    await Promise.all([
      fetchTextData(),
      fetchFeatureDistribution(),
      fetchCorpusFeatureDistribution()
    ])
    
    // 清除套索状态
    corpusLassoMode.value = false
    corpusLassoPoints.value = []
    corpusLassoResults.value = []
    corpusLassoPopup.visible = false
    corpusLassoPopup.featureStats = null
    
    // 清除特征高亮
    clearFeatureHighlights('corpus')
    
    console.log(`已应用Corpus套索选择，选中${selectedCorpusIds.length}个项目`)
  } catch (error) {
    console.error('应用Corpus套索选择失败:', error)
  } finally {
    loading.value = false
  }
}

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
const selectedAttackMethods = ref(['charswap', 'deletion', 'easydata', 'embedding', 'swap', 'synonym', 'wordnet'])


const selectedFeatures = ref({
  prompt: [], // 存储prompt的特征选择
  corpus: []  // 存储corpus的特征选择
})


const barBorders = ref({
  prompt: {}, // 结构: { "特征名-值范围": true/false }
  corpus: {}
})

// 新增：投影点高亮特征
const highlightedFeatures = ref({
  prompt: {}, // 结构: { "特征名-值范围": true/false }
  corpus: {}
})

// 新增：根据投影点高亮特征条形
function highlightFeaturesFromProjectionPoint(item, dataSource) {
  if (!item.features) return
  
  // 清除之前的高亮
  clearFeatureHighlights(dataSource)
  
  // 分析特征并高亮对应的条形
  Object.entries(item.features).forEach(([featureName, featureInfo]) => {
    const value = featureInfo.value
    const description = featureInfo.description
    
    // 根据特征类型确定值范围
    let valueRange
    if (description.includes('连续值')) {
      // 连续特征，需要找到对应的区间
      valueRange = findContinuousFeatureRange(featureName, value, dataSource)
    } else {
      // 离散特征，直接使用描述
      valueRange = description
    }
    
    if (valueRange) {
      // 设置高亮状态
      highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`] = true
      
      // 更新图表显示
      updateFeatureBarHighlight(dataSource, featureName, valueRange, true)
    }
  })
}

// 新增：清除特征高亮
function clearFeatureHighlights(dataSource) {
  // 清除所有高亮状态
  Object.keys(highlightedFeatures.value[dataSource]).forEach(key => {
    const [featureName, valueRange] = key.split('-', 2)
    updateFeatureBarHighlight(dataSource, featureName, valueRange, false)
  })
  
  // 重置高亮状态
  highlightedFeatures.value[dataSource] = {}
  
  // 强制更新所有图表的边框状态
  const container = document.querySelector(`.feature-container[data-container="${dataSource}"]`)
  if (container) {
    d3.select(container).selectAll('.bar-count, .bar-robustness')
      .attr('stroke', 'none')
      .attr('stroke-width', 0)
      .attr('stroke-dasharray', null)
      .attr('opacity', 0.7)
  }
}

// 新增：查找连续特征对应的区间
function findContinuousFeatureRange(featureName, value, dataSource) {
  const currentDistributionData = dataSource === 'prompt' ? distributionData.value : distributionDataCorpus.value
  
  if (!currentDistributionData || !currentDistributionData.continuous || !currentDistributionData.continuous[featureName]) {
    return null
  }
  
  const featureData = currentDistributionData.continuous[featureName]
  const values = featureData.values
  
  // 找到包含该值的区间
  for (const dataPoint of values) {
    if (dataPoint.value === value) {
      // 找到对应的区间
      const allValues = values.map(d => d.value)
      const min = Math.min(...allValues)
      const max = Math.max(...allValues)
      const step = (max - min) / 10
      
      for (let i = 0; i < 10; i++) {
        const start = min + i * step
        const end = start + step
        if (value >= start && value < end) {
          return `${start.toFixed(2)}-${end.toFixed(2)}`
        }
      }
      break
    }
  }
  
  return null
}

// 新增：更新特征条形高亮状态
function updateFeatureBarHighlight(dataSource, featureName, valueRange, isHighlighted) {
  const container = document.querySelector(`.feature-container[data-container="${dataSource}"]`)
  if (!container) return
  
  // 查找对应的条形
  d3.select(container).selectAll('.bar-count, .bar-robustness')
    .filter(function() {
      const bar = d3.select(this)
      const barDataSource = bar.attr('data-source')
      const barFeature = bar.attr('data-feature')
      const barRange = bar.attr('data-range')
      
      return barDataSource === dataSource && 
             barFeature === featureName && 
             barRange === valueRange
    })
    .attr('stroke', isHighlighted ? '#ff6b6b' : 'none')
    .attr('stroke-width', isHighlighted ? 3 : 0)
    .attr('stroke-dasharray', isHighlighted ? '5,5' : null)
    .attr('opacity', isHighlighted ? 1 : 0.7)
}

function createChart(svgElement, featureName, featureData, isContinuous,dataSource) {
  console.log(dataSource)
  const margin = { top: 10, right: 10, bottom: 10, left: 8 };
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
      // 获取当前条形的值范围
      const valueRange = isContinuous ? 
        `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : 
        d.label || d.value_name;
      const isHighlighted = highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`];
      
      // 只有在非高亮状态下才应用悬停样式
      if (!isHighlighted) {
        d3.select(this)
          .attr("opacity", 1)
          .attr("stroke", "#333")
          .attr("stroke-width", 1.5);
      }

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
      // 检查是否已被选中或高亮
      const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
      const isHighlighted = highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`];
      // 只有未选中且未高亮的条形才恢复默认样式
      if (!isSelected && !isHighlighted) {
        d3.select(this)
          .attr("opacity", 0.7)
          .attr("stroke", "none")
          .attr("stroke-width", 0);
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
      // 获取当前条形的值范围
      const valueRange = isContinuous ? 
        `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : 
        d.label || d.value_name;
      const isHighlighted = highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`];
      
      // 只有在非高亮状态下才应用悬停样式
      if (!isHighlighted) {
        d3.select(this)
          .attr("opacity", 1)
          .attr("stroke", "#333")
          .attr("stroke-width", 1.5);
      }

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
      
      // 检查是否已被选中或高亮
      const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
      const isHighlighted = highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`];
      
      // 只有未选中且未高亮的条形才恢复默认样式
      if (!isSelected && !isHighlighted) {
        d3.select(this)
          .attr("opacity", 0.7)
          .attr("stroke", "none")
          .attr("stroke-width", 0);
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
        const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
        const isHighlighted = highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`];
        
        if (isHighlighted) return "#ff6b6b"; // 高亮状态：红色
        if (isSelected) return "#333"; // 选中状态：深灰色
        return "none";
      })
      .attr("stroke-width", d => {
        const valueRange = isContinuous ? `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : d.label;
        const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
        const isHighlighted = highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`];
        
        if (isHighlighted) return 3; // 高亮状态：粗边框
        if (isSelected) return 1.5; // 选中状态：中等边框
        return 0;
      })
      .attr("stroke-dasharray", d => {
        const valueRange = isContinuous ? `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : d.label;
        const isHighlighted = highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`];
        
        if (isHighlighted) return "5,5"; // 高亮状态：虚线
        return "3,2"; // 选中状态：虚线
      })
      .attr("opacity", d => {
        const valueRange = isContinuous ? `${d.start.toFixed(2)}-${d.end.toFixed(2)}` : d.label;
        const isSelected = barBorders.value[dataSource][`${featureName}-${valueRange}`];
        const isHighlighted = highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`];
        
        if (isHighlighted || isSelected) return 1; // 高亮或选中状态：不透明
        return 0.7; // 默认状态：半透明
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
      body: JSON.stringify({ 
        ids: promptIds.value,
        corpus_ids: corpusIds.value,  // 新增：传递corpus_ids
        selected_attack_methods: selectedAttackMethods.value
      })
    });
    currentPrompts.value = promptData.prompt || [];
    console.log('更新后的 prompts:', currentPrompts.value);
    
    // 显示prompt特征向量信息
    if (currentPrompts.value.length > 0) {
      console.log('=== Prompt特征向量信息 ===');
      currentPrompts.value.forEach((prompt, index) => {
        if (index < 3) { // 只显示前3个prompt的特征信息
          console.log(`Prompt ID ${prompt.id}:`);
          console.log(`  文本: ${prompt.text}`);
          console.log(`  鲁棒性: ${prompt.robustness}`);
          if (prompt.features) {
            console.log('  特征向量:');
            Object.entries(prompt.features).forEach(([featureName, featureInfo]) => {
              console.log(`    ${featureName}: ${featureInfo.description}`);
            });
          }
          console.log('---');
        }
      });
      if (currentPrompts.value.length > 3) {
        console.log(`... 还有 ${currentPrompts.value.length - 3} 个prompt`);
      }
    }

    
    const corpusData = await fetchWithRetry('http://127.0.0.1:5000/get_corpus_data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        ids: corpusIds.value,
        prompt_ids: promptIds.value,  // 新增：传递prompt_ids
        selected_attack_methods: selectedAttackMethods.value
      })
    });
    currentCorpus.value = corpusData.corpus || [];
    console.log('更新后的 corpus:', currentCorpus.value);
    
    // 显示corpus特征向量信息
    if (currentCorpus.value.length > 0) {
      console.log('=== Corpus特征向量信息 ===');
      currentCorpus.value.forEach((corpus, index) => {
        if (index < 3) { // 只显示前3个corpus的特征信息
          console.log(`Corpus ID ${corpus.id}:`);
          console.log(`  文本: ${corpus.text}`);
          console.log(`  鲁棒性: ${corpus.robustness}`);
          if (corpus.features) {
            console.log('  特征向量:');
            Object.entries(corpus.features).forEach(([featureName, featureInfo]) => {
              console.log(`    ${featureName}: ${featureInfo.description}`);
            });
          }
          console.log('---');
        }
      });
      if (currentCorpus.value.length > 3) {
        console.log(`... 还有 ${currentCorpus.value.length - 3} 个corpus`);
      }
    }

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
        corpus_ids: corpusIds.value,
        selected_attack_methods: selectedAttackMethods.value
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
        corpus_ids: corpusIds.value,
        selected_attack_methods: selectedAttackMethods.value
      })
    });
    distributionDataCorpus.value = data.distribution;
    console.log("更新后的 corpus 特征分布数据：", distributionDataCorpus.value);
  } catch (error) {
    console.error('获取特征分布失败:', error);
    distributionDataCorpus.value = null;
  }
}

// 新增：优化的鲁棒性数据更新函数，只更新鲁棒性值，不重新获取投影坐标
async function fetchRobustnessDataOnly() {
  try {
    // 只获取鲁棒性数据，保持现有的投影坐标
    const promptData = await fetchWithRetry('http://127.0.0.1:5000/get_prompt_data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        ids: promptIds.value,
        corpus_ids: corpusIds.value,
        selected_attack_methods: selectedAttackMethods.value,
        robustness_only: true
      })
    });
    
    const corpusData = await fetchWithRetry('http://127.0.0.1:5000/get_corpus_data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        ids: corpusIds.value,
        prompt_ids: promptIds.value,
        selected_attack_methods: selectedAttackMethods.value,
        robustness_only: true
      })
    });
    
    // 只更新鲁棒性值，保持现有的投影坐标和其他数据
    if (promptData.prompt && currentPrompts.value.length > 0) {
      const newPromptData = promptData.prompt || [];
      currentPrompts.value.forEach(existingPrompt => {
        const newPrompt = newPromptData.find(p => p.id === existingPrompt.id);
        if (newPrompt) {
          existingPrompt.robustness = newPrompt.robustness;
        }
      });
    }
    
    if (corpusData.corpus && currentCorpus.value.length > 0) {
      const newCorpusData = corpusData.corpus || [];
      currentCorpus.value.forEach(existingCorpus => {
        const newCorpus = newCorpusData.find(c => c.id === existingCorpus.id);
        if (newCorpus) {
          existingCorpus.robustness = newCorpus.robustness;
        }
      });
    }
    
    console.log('鲁棒性数据更新完成');
  } catch (error) {
    console.error('鲁棒性数据更新失败:', error);
  }
}

// 修改监听器，使用 nextTick
watch([distributionData, distributionDataCorpus], async () => {
  console.log('数据变化，准备重新初始化图表')
  // 等待一小段时间确保 DOM 完全更新
  await new Promise(resolve => setTimeout(resolve, 100))
  await initChartsWithDataAttribute()
}, { deep: true })

// 注释掉自动监听攻击方式变化，改为手动提交时触发
// watch(selectedAttackMethods, async () => {
//   console.log('攻击方式选择变化，重新获取数据:', selectedAttackMethods.value)
//   loading.value = true
//   try {
//     await Promise.all([
//       fetchTextData(),
//       fetchFeatureDistribution(),
//       fetchCorpusFeatureDistribution()
//     ])
//     console.log('攻击方式变化后数据获取完成')
//   } catch (error) {
//     console.error('攻击方式变化后数据获取失败:', error)
//   } finally {
//     loading.value = false
//   }
// }, { deep: true })

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
  
  // 初始化ID数组
  initialIds.prompt.value = Array.from({length: 660}, (_, i) => i)
  initialIds.corpus.value = Array.from({length: 660}, (_, i) => i)
  

  
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
    
    // 更新投影尺寸
    updateProjectionSize()
    
    // 监听窗口大小变化
    window.addEventListener('resize', updateProjectionSize)
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

// 组件卸载时清理事件监听器
onBeforeUnmount(() => {
  // 清理窗口大小变化监听器
  window.removeEventListener('resize', updateProjectionSize)
  
  // 清理拖拽相关的事件监听器
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})

const loading = ref(false)

const initialIds = {
  prompt: ref([]),
  corpus: ref([])
}





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


// 鲁棒性染色函数：根据当前数据的鲁棒性最小值和最大值动态划分区间
function robustnessColorStyle(val, min = null, max = null) {
  // 动态区间：如果未传入min/max，则默认0.6分界
  if (min === null || max === null || min === max) {
    // 兼容老逻辑
    let color = ''
    if (val >= 0.6) {
      const t = (val - 0.6) / 0.4
      color = interpolateColor('#b3d1ff', '#0047ab', t)
    } else {
      const t = (0.6 - val) / 0.6
      color = interpolateColor('#ffd6d6', '#b22222', t)
    }
    return { color }
  }
  // 新逻辑：按[min, max]线性插值
  const t = (val - min) / (max - min)
  // 0.5为分界，低于中值为红色区间，高于为蓝色区间
  if (t >= 0.5) {
    // 蓝色区间
    const t2 = (t - 0.5) * 2
    return { color: interpolateColor('#b3d1ff', '#0047ab', t2) }
  } else {
    // 红色区间
    const t2 = (0.5 - t) * 2
    return { color: interpolateColor('#ffd6d6', '#b22222', t2) }
  }
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
const globalFeatureHistory = ref([]) // [{timestamp, name, features: {promptFeatures, corpusFeatures}, attackMethods: [], dataSnapshot: {...}}]
const globalHistoryPanelOpen = ref(false)
const globalHistoryApplyLoading = ref(null)
const openHistoryDropdowns = ref({}) // 新的下拉状态管理
const editingGlobalHistoryName = ref(null)

// 拖动相关变量
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const panelX = ref(330) // 初始X位置
const panelY = ref(0)   // 初始Y位置
const panelWidth = ref(600) // 历史记录窗口宽度，与套索弹出框一致
const panelHeight = ref(400) // 历史记录窗口高度

// 攻击方式选择相关
const attackMethodsPanelOpen = ref(false)
const attackMethods = ref([
  { key: 'charswap', name: 'CharSwap', description: '字符交换攻击' },
  { key: 'deletion', name: 'Deletion', description: '字符删除攻击' },
  { key: 'easydata', name: 'EasyData', description: '简单数据攻击' },
  { key: 'embedding', name: 'Embedding', description: '嵌入攻击' },
  { key: 'swap', name: 'Swap', description: '词汇交换攻击' },
  { key: 'synonym', name: 'Synonym', description: '同义词替换攻击' },
  { key: 'wordnet', name: 'WordNet', description: 'WordNet攻击' }
])

// 计算属性：是否全选
const allSelected = computed(() => {
  return selectedAttackMethods.value.length === attackMethods.value.length
})

// 攻击方式选择方法
const toggleAttackMethodsPanel = () => {
  attackMethodsPanelOpen.value = !attackMethodsPanelOpen.value
}

const submitAttackMethods = async () => {
  if (selectedAttackMethods.value.length === 0) return
  
  loading.value = true
  try {
    console.log('选中的攻击方式:', selectedAttackMethods.value)
    console.log('攻击方式详情:', selectedAttackMethods.value.map(key => {
      const method = attackMethods.value.find(m => m.key === key)
      return { key, name: method.name, description: method.description }
    }))
    
    // 先缓存攻击方式选择状态
    const historyRecord = {
      timestamp: Date.now(),
      name: `攻击方式选择 - ${formatTime(Date.now())}`,
      features: {
        promptFeatures: JSON.parse(JSON.stringify(selectedFeatures.value.prompt)),
        corpusFeatures: JSON.parse(JSON.stringify(selectedFeatures.value.corpus))
      },
      attackMethods: [...selectedAttackMethods.value], // 保存攻击方法选择
      dataSnapshot: null // 稍后填充
    }
    
    // 使用优化的函数：只更新鲁棒性数据，不重新获取投影坐标
    await Promise.all([
      fetchRobustnessDataOnly(),
      fetchFeatureDistribution(),
      fetchCorpusFeatureDistribution()
    ])
    
    // 缓存应用后的数据快照
    historyRecord.dataSnapshot = {
      promptIds: [...promptIds.value],
      corpusIds: [...corpusIds.value],
      currentPrompts: JSON.parse(JSON.stringify(currentPrompts.value)),
      currentCorpus: JSON.parse(JSON.stringify(currentCorpus.value)),
      distributionData: JSON.parse(JSON.stringify(distributionData.value)),
      distributionDataCorpus: JSON.parse(JSON.stringify(distributionDataCorpus.value)),
      promptFeatures: JSON.parse(JSON.stringify(selectedFeatures.value.prompt)),
      corpusFeatures: JSON.parse(JSON.stringify(selectedFeatures.value.corpus)),
      selectedAttackMethods: [...selectedAttackMethods.value] // 保存攻击方式状态
    }
    
    // 添加到历史记录
    globalFeatureHistory.value.push(historyRecord)
    if (globalFeatureHistory.value.length > 10) {
      globalFeatureHistory.value.shift()
    }
    
    console.log('攻击方式提交成功，数据已更新并保存到历史记录')
    attackMethodsPanelOpen.value = false
  } catch (error) {
    console.error('提交攻击方式失败:', error)
  } finally {
    loading.value = false
  }
}

const clearAttackMethods = () => {
  selectedAttackMethods.value = []
  console.log('已清空攻击方式选择')
}

// 全选/全不选方法
const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedAttackMethods.value = []
  } else {
    selectedAttackMethods.value = attackMethods.value.map(method => method.key)
  }
}

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
    attackMethods: [...selectedAttackMethods.value], // 添加攻击方法信息
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
      corpusFeatures: JSON.parse(JSON.stringify(corpusRaw)),
      selectedAttackMethods: [...selectedAttackMethods.value] // 保存攻击方式状态
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
  // 清空攻击方式选择
  selectedAttackMethods.value = []
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

// 拖动相关方法
const startDrag = (event) => {
  isDragging.value = true
  dragStartX.value = event.clientX - panelX.value
  dragStartY.value = event.clientY - panelY.value
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  event.preventDefault()
}

const onDrag = (event) => {
  if (!isDragging.value) return
  panelX.value = event.clientX - dragStartX.value
  panelY.value = event.clientY - dragStartY.value
  
  // 限制拖动范围，防止面板拖出视窗
  const maxX = window.innerWidth - 340 // 面板宽度
  const maxY = window.innerHeight - 100 // 留一些底部空间
  
  panelX.value = Math.max(0, Math.min(panelX.value, maxX))
  panelY.value = Math.max(0, Math.min(panelY.value, maxY))
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 历史记录窗口调整大小方法
const startResizeHistory = (direction, event) => {
  event.preventDefault()
  event.stopPropagation()
  const startX = event.clientX
  const startY = event.clientY
  const startWidth = panelWidth.value
  const startHeight = panelHeight.value
  const startLeft = panelX.value
  const startTop = panelY.value
  
  const onResizeMove = (e) => {
    let dx = e.clientX - startX
    let dy = e.clientY - startY
    let newWidth = startWidth
    let newHeight = startHeight
    let newLeft = startLeft
    let newTop = startTop
    
    if (direction.includes('e')) newWidth = Math.max(240, startWidth + dx)
    if (direction.includes('s')) newHeight = Math.max(200, startHeight + dy)
    if (direction.includes('w')) {
      newWidth = Math.max(240, startWidth - dx)
      newLeft = startLeft + dx
    }
    if (direction.includes('n')) {
      newHeight = Math.max(200, startHeight - dy)
      newTop = startTop + dy
    }
    
    // 限制在视窗范围内
    newWidth = Math.min(newWidth, window.innerWidth - newLeft - 10)
    newHeight = Math.min(newHeight, window.innerHeight - newTop - 10)
    
    panelWidth.value = newWidth
    panelHeight.value = newHeight
    panelX.value = newLeft
    panelY.value = newTop
  }
  
  const onResizeUp = () => {
    document.removeEventListener('mousemove', onResizeMove)
    document.removeEventListener('mouseup', onResizeUp)
  }
  
  document.addEventListener('mousemove', onResizeMove)
  document.addEventListener('mouseup', onResizeUp)
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
    
    // 恢复攻击方式选择状态
    if (record.dataSnapshot.selectedAttackMethods) {
      selectedAttackMethods.value = [...record.dataSnapshot.selectedAttackMethods]
    } else if (record.attackMethods) {
      // 兼容旧版本历史记录
      selectedAttackMethods.value = [...record.attackMethods]
    }
    
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
// 新的历史记录下拉切换方法
const toggleHistoryDropdown = (index, type) => {
  if (!openHistoryDropdowns.value[index]) {
    openHistoryDropdowns.value[index] = { prompt: false, corpus: false, attack: false }
  }
  openHistoryDropdowns.value[index][type] = !openHistoryDropdowns.value[index][type]
}

// 获取攻击方法名称
const getAttackMethodName = (methodKey) => {
  const method = attackMethods.value.find(m => m.key === methodKey)
  return method ? method.name : methodKey
}

// 新增：全局下拉状态
const globalPromptDropdownOpen = vueRef(false)
const globalCorpusDropdownOpen = vueRef(false)

const projectionWidth = ref(400)
const projectionHeight = ref(300)

// 动态获取容器尺寸
function updateProjectionSize() {
  const promptPanel = document.querySelector('.projection-panel .panel-content')
  // const corpusPanel = document.querySelector('.projection-panel:nth-child(2) .panel-content')
  
  if (promptPanel) {
    const rect = promptPanel.getBoundingClientRect()
    projectionWidth.value = rect.width
    projectionHeight.value = rect.height
  }
}

function getXYRange(arr, key) {
  const vals = arr.filter(d => d[key] !== null).map(d => d[key])
  if (vals.length === 0) return [0, 1]
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  return min === max ? [min-1, max+1] : [min, max]
}
const promptXRange = ref([0,1])
const promptYRange = ref([0,1])
const corpusXRange = ref([0,1])
const corpusYRange = ref([0,1])

function updateProjectionRanges() {
  promptXRange.value = getXYRange(currentPrompts.value, 'x')
  promptYRange.value = getXYRange(currentPrompts.value, 'y')
  corpusXRange.value = getXYRange(currentCorpus.value, 'x')
  corpusYRange.value = getXYRange(currentCorpus.value, 'y')
}

function projectX(x, type) {
  const [minX, maxX] = type==='prompt' ? promptXRange.value : corpusXRange.value
  return ((x-minX)/(maxX-minX))* (400-40) + 20
}
function projectY(y, type) {
  const [minY, maxY] = type==='prompt' ? promptYRange.value : corpusYRange.value
  return ((y-minY)/(maxY-minY))* (300-40) + 20
}

// 替换原有的 reactive 弹窗对象定义
const promptTooltip = reactive({ visible: false, data: {}, screenX: 0, screenY: 0, isDragging: false, isActuallyDragging: false, dragStartX: 0, dragStartY: 0, width: 400, height: 600 })
const corpusTooltip = reactive({ visible: false, data: {}, screenX: 0, screenY: 0, isDragging: false, isActuallyDragging: false, dragStartX: 0, dragStartY: 0, width: 400, height: 600 })
const promptLassoPopup = reactive({ visible: false, x: 0, y: 0, data: [], featureStats: null, isDragging: false, isActuallyDragging: false, dragStartX: 0, dragStartY: 0, width: 600, height: 500 })
const corpusLassoPopup = reactive({ visible: false, x: 0, y: 0, data: [], featureStats: null, isDragging: false, isActuallyDragging: false, dragStartX: 0, dragStartY: 0, width: 600, height: 500 })

// 新增：弹窗缩放方法
function startResize(popup, direction, event) {
  event.preventDefault();
  event.stopPropagation();
  const startX = event.clientX;
  const startY = event.clientY;
  const startWidth = popup.width;
  const startHeight = popup.height;
  const startLeft = popup.screenX !== undefined ? popup.screenX : popup.x;
  const startTop = popup.screenY !== undefined ? popup.screenY : popup.y;
  function onMove(e) {
    let dx = e.clientX - startX;
    let dy = e.clientY - startY;
    let newWidth = startWidth, newHeight = startHeight;
    let newLeft = startLeft, newTop = startTop;
    if (direction.includes('e')) newWidth = Math.max(240, startWidth + dx);
    if (direction.includes('s')) newHeight = Math.max(120, startHeight + dy);
    if (direction.includes('w')) {
      newWidth = Math.max(240, startWidth - dx);
      newLeft = startLeft + dx;
    }
    if (direction.includes('n')) {
      newHeight = Math.max(120, startHeight - dy);
      newTop = startTop + dy;
    }
    newWidth = Math.min(newWidth, window.innerWidth - newLeft - 10);
    newHeight = Math.min(newHeight, window.innerHeight - newTop - 10);
    if (popup.screenX !== undefined) {
      popup.width = newWidth;
      popup.height = newHeight;
      popup.screenX = newLeft;
      popup.screenY = newTop;
    } else {
      popup.width = newWidth;
      popup.height = newHeight;
      popup.x = newLeft;
      popup.y = newTop;
    }
  }
  function onUp() {
    window.removeEventListener('mousemove', onMove);
    window.removeEventListener('mouseup', onUp);
  }
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
}

function showPromptTooltip(item, event) {
  promptTooltip.visible = true
  promptTooltip.data = item
  // 使用页面坐标，而不是SVG坐标
  promptTooltip.screenX = event.clientX + 10
  promptTooltip.screenY = event.clientY - 80
  selectedPromptId.value = item.id
  
  // 高亮对应的特征条形
  highlightFeaturesFromProjectionPoint(item, 'prompt')
}

// 从套索弹窗中显示prompt详细信息
function showPromptTooltipFromLasso(item, event) {
  promptTooltip.visible = true
  promptTooltip.data = item
  // 使用页面坐标，而不是SVG坐标
  promptTooltip.screenX = event.clientX + 10
  promptTooltip.screenY = event.clientY - 80
  selectedPromptId.value = item.id
  
  // 高亮对应的特征条形
  highlightFeaturesFromProjectionPoint(item, 'prompt')
}
function hidePromptTooltip() {
  if (!promptTooltip.isActuallyDragging) {
    promptTooltip.visible = false
    selectedPromptId.value = null
    // 清除高亮
    clearFeatureHighlights('prompt')
  }
}
function showCorpusTooltip(item, event) {
  corpusTooltip.visible = true
  corpusTooltip.data = item
  // 使用页面坐标，而不是SVG坐标
  corpusTooltip.screenX = event.clientX + 10
  corpusTooltip.screenY = event.clientY - 80
  selectedCorpusId.value = item.id
  
  // 高亮对应的特征条形
  highlightFeaturesFromProjectionPoint(item, 'corpus')
}

// 从套索弹窗中显示corpus详细信息
function showCorpusTooltipFromLasso(item, event) {
  corpusTooltip.visible = true
  corpusTooltip.data = item
  // 使用页面坐标，而不是SVG坐标
  corpusTooltip.screenX = event.clientX + 10
  corpusTooltip.screenY = event.clientY - 80
  selectedCorpusId.value = item.id
  
  // 高亮对应的特征条形
  highlightFeaturesFromProjectionPoint(item, 'corpus')
}
function hideCorpusTooltip() {
  if (!corpusTooltip.isActuallyDragging) {
    corpusTooltip.visible = false
    selectedCorpusId.value = null
    // 清除高亮
    clearFeatureHighlights('corpus')
  }
}

// 统一的关闭函数
function closePromptTooltip() {
  hidePromptTooltip()
}

function closeCorpusTooltip() {
  hideCorpusTooltip()
}

function closePromptLassoPopup() {
  promptLassoPopup.visible = false
  promptLassoPopup.isActuallyDragging = false
  // 清除特征高亮
  clearFeatureHighlights('prompt')
}

function closeCorpusLassoPopup() {
  corpusLassoPopup.visible = false
  corpusLassoPopup.isActuallyDragging = false
  // 清除特征高亮
  clearFeatureHighlights('corpus')
}



// 全局弹出框拖拽函数
function startGlobalTooltipDrag(tooltip, event) {
  tooltip.isDragging = true
  tooltip.isActuallyDragging = false
  tooltip.dragStartX = event.clientX - tooltip.screenX
  tooltip.dragStartY = event.clientY - tooltip.screenY

  function onMove(e) {
    if (!tooltip.isDragging) return
    
    let newX = e.clientX - tooltip.dragStartX
    let newY = e.clientY - tooltip.dragStartY
    
    // 边界检查 - 确保弹出框不会完全移出视窗
    const maxX = window.innerWidth - 200 // 窗口宽度 - 弹出框宽度
    const maxY = window.innerHeight - 60  // 窗口高度 - 弹出框高度
    newX = Math.max(0, Math.min(newX, maxX))
    newY = Math.max(0, Math.min(newY, maxY))
    
    tooltip.screenX = newX
    tooltip.screenY = newY
    tooltip.isActuallyDragging = true
    
    e.preventDefault()
    e.stopPropagation()
  }

  function onUp() {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
    setTimeout(() => {
      tooltip.isDragging = false
      tooltip.isActuallyDragging = false
    }, 100) // 增加延迟确保拖拽状态正确重置
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
  
  event.preventDefault()
  event.stopPropagation()
}

function startGlobalLassoPopupDrag(popup, event) {
  popup.isDragging = true
  popup.isActuallyDragging = false
  popup.dragStartX = event.clientX - popup.x
  popup.dragStartY = event.clientY - popup.y

  function onMove(e) {
    if (!popup.isDragging) return
    
    let newX = e.clientX - popup.dragStartX
    let newY = e.clientY - popup.dragStartY
    
    // 边界检查 - 确保弹出框不会完全移出视窗
    const maxX = window.innerWidth - 280 // 窗口宽度 - 弹出框宽度
    const maxY = window.innerHeight - 200 // 窗口高度 - 弹出框高度
    newX = Math.max(0, Math.min(newX, maxX))
    newY = Math.max(0, Math.min(newY, maxY))
    
    popup.x = newX
    popup.y = newY
    popup.isActuallyDragging = true
    
    e.preventDefault()
    e.stopPropagation()
  }

  function onUp() {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
    setTimeout(() => {
      popup.isDragging = false
      popup.isActuallyDragging = false
    }, 100) // 增加延迟确保拖拽状态正确重置
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
  
  event.preventDefault()
  event.stopPropagation()
}

// 监听数据变化自动更新投影范围
watch([currentPrompts, currentCorpus], updateProjectionRanges, {deep:true})



// 竖直鲁棒性图例参数
const legendVSteps = 10
const legendVBlockHeight = 20
const legendVGap = 16
const legendVHeight = 10 + legendVSteps * legendVBlockHeight + (legendVSteps - 1) * legendVGap + 22

// Prompt专用图例
const legendVValuesPrompt = computed(() => {
  const [min, max] = promptRobustnessRange.value
  return Array.from({length: legendVSteps}, (_,i)=> min + i*(max-min)/legendVSteps)
})
const legendVLabelsPrompt = computed(() => {
  const [min, max] = promptRobustnessRange.value
  return Array.from({length: legendVSteps}, (_,i)=>{
    const start = (min + i*(max-min)/legendVSteps).toFixed(3)
    const end = (min + (i+1)*(max-min)/legendVSteps).toFixed(3)
    return i===legendVSteps-1 ? `${start}~${max.toFixed(3)}` : `${start}~${end}`
  })
})
// Corpus专用图例
const legendVValuesCorpus = computed(() => {
  const [min, max] = corpusRobustnessRange.value
  return Array.from({length: legendVSteps}, (_,i)=> min + i*(max-min)/legendVSteps)
})
const legendVLabelsCorpus = computed(() => {
  const [min, max] = corpusRobustnessRange.value
  return Array.from({length: legendVSteps}, (_,i)=>{
    const start = (min + i*(max-min)/legendVSteps).toFixed(3)
    const end = (min + (i+1)*(max-min)/legendVSteps).toFixed(3)
    return i===legendVSteps-1 ? `${start}~${max.toFixed(3)}` : `${start}~${end}`
  })
})

const sortedPromptLassoData = computed(() => {
  if (promptLassoSortState.value === 'robustnessDesc') {
    return [...(promptLassoPopup.data || [])].sort((a, b) => b.robustness - a.robustness)
  } else if (promptLassoSortState.value === 'robustnessAsc') {
    return [...(promptLassoPopup.data || [])].sort((a, b) => a.robustness - b.robustness)
  } else {
    return [...(promptLassoPopup.data || [])].sort((a, b) => a.id - b.id)
  }
})
const sortedCorpusLassoData = computed(() => {
  if (corpusLassoSortState.value === 'robustnessDesc') {
    return [...(corpusLassoPopup.data || [])].sort((a, b) => b.robustness - a.robustness)
  } else if (corpusLassoSortState.value === 'robustnessAsc') {
    return [...(corpusLassoPopup.data || [])].sort((a, b) => a.robustness - b.robustness)
  } else {
    return [...(corpusLassoPopup.data || [])].sort((a, b) => a.id - b.id)
  }
})

function cyclePromptLassoSort() {
  if (promptLassoSortState.value === 'id') promptLassoSortState.value = 'robustnessDesc'
  else if (promptLassoSortState.value === 'robustnessDesc') promptLassoSortState.value = 'robustnessAsc'
  else promptLassoSortState.value = 'id'
}
function cycleCorpusLassoSort() {
  if (corpusLassoSortState.value === 'id') corpusLassoSortState.value = 'robustnessDesc'
  else if (corpusLassoSortState.value === 'robustnessDesc') corpusLassoSortState.value = 'robustnessAsc'
  else corpusLassoSortState.value = 'id'
}



// 计算prompt/corpus投影点鲁棒性区间
const promptRobustnessRange = computed(() => {
  if (!currentPrompts.value.length) return [0, 1]
  const vals = currentPrompts.value.map(d => d.robustness).filter(v => v !== undefined && v !== null)
  if (!vals.length) return [0, 1]
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  return min === max ? [min-0.01, max+0.01] : [min, max]
})
const corpusRobustnessRange = computed(() => {
  if (!currentCorpus.value.length) return [0, 1]
  const vals = currentCorpus.value.map(d => d.robustness).filter(v => v !== undefined && v !== null)
  if (!vals.length) return [0, 1]
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  return min === max ? [min-0.01, max+0.01] : [min, max]
})

// 全局鲁棒性计算
const globalRobustness = computed(() => {
  const allRobustnessValues = []
  
  // 收集所有prompt的鲁棒性值
  if (currentPrompts.value.length > 0) {
    currentPrompts.value.forEach(prompt => {
      if (prompt.robustness !== undefined && prompt.robustness !== null) {
        allRobustnessValues.push(prompt.robustness)
      }
    })
  }
  
  // 收集所有corpus的鲁棒性值
  if (currentCorpus.value.length > 0) {
    currentCorpus.value.forEach(corpus => {
      if (corpus.robustness !== undefined && corpus.robustness !== null) {
        allRobustnessValues.push(corpus.robustness)
      }
    })
  }
  
  if (allRobustnessValues.length === 0) return null
  
  // 计算平均值
  const average = allRobustnessValues.reduce((sum, val) => sum + val, 0) / allRobustnessValues.length
  return average
})

// 全局鲁棒性显示文本
const globalRobustnessText = computed(() => {
  if (globalRobustness.value === null) return '--'
  return globalRobustness.value.toFixed(3)
})

// 全局鲁棒性颜色
const globalRobustnessColor = computed(() => {
  if (globalRobustness.value === null) return '#666'
  
  // 使用与图例相同的染色方式
  // 获取当前所有数据的鲁棒性范围
  const allValues = []
  if (currentPrompts.value.length > 0) {
    currentPrompts.value.forEach(p => {
      if (p.robustness !== undefined && p.robustness !== null) {
        allValues.push(p.robustness)
      }
    })
  }
  if (currentCorpus.value.length > 0) {
    currentCorpus.value.forEach(c => {
      if (c.robustness !== undefined && c.robustness !== null) {
        allValues.push(c.robustness)
      }
    })
  }
  
  if (allValues.length === 0) return '#666'
  
  const min = Math.min(...allValues)
  const max = Math.max(...allValues)
  const range = min === max ? [min-0.01, max+0.01] : [min, max]
  
  return robustnessColorStyle(globalRobustness.value, range[0], range[1]).color
})

// 新增：套索特征统计计算函数
function calculateLassoFeatureStats(lassoItems, dataSource) {
  console.log(`计算${dataSource}套索特征统计，项目数量:`, lassoItems?.length)
  if (!lassoItems || lassoItems.length === 0) return null
  
  const stats = {
    continuous: {},
    discrete: {}
  }
  
  // 获取当前分布数据用于特征名称映射
  const currentDistributionData = dataSource === 'prompt' ? distributionData.value : distributionDataCorpus.value
  console.log(`${dataSource}分布数据:`, currentDistributionData)
  
  // 处理连续特征
  if (currentDistributionData?.continuous) {
    Object.keys(currentDistributionData.continuous).forEach(featureName => {
      const values = lassoItems
        .map(item => item.features?.[featureName]?.value)
        .filter(val => val !== undefined && val !== null)
      
      if (values.length > 0) {
        const avg = values.reduce((sum, val) => sum + val, 0) / values.length
        const min = Math.min(...values)
        const max = Math.max(...values)
        const std = Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / values.length)
        
        stats.continuous[featureName] = {
          count: values.length,
          average: avg.toFixed(4),
          min: min.toFixed(4),
          max: max.toFixed(4),
          std: std.toFixed(4),
          values: values
        }
      }
    })
  }
  
  // 处理离散特征
  if (currentDistributionData?.discrete) {
    Object.keys(currentDistributionData.discrete).forEach(featureName => {
      const valueCounts = {}
      const totalCount = lassoItems.length
      
      lassoItems.forEach(item => {
        const featureValue = item.features?.[featureName]?.value
        if (featureValue !== undefined && featureValue !== null) {
          valueCounts[featureValue] = (valueCounts[featureValue] || 0) + 1
        }
      })
      
      if (Object.keys(valueCounts).length > 0) {
        stats.discrete[featureName] = {
          totalCount,
          distribution: Object.entries(valueCounts).map(([value, count]) => ({
            value: parseInt(value),
            count,
            percentage: ((count / totalCount) * 100).toFixed(1)
          })).sort((a, b) => b.count - a.count), // 按数量降序排列
          dominantValue: Object.entries(valueCounts).reduce((a, b) => valueCounts[a[0]] > valueCounts[b[0]] ? a : b)[0]
        }
      }
    })
  }
  
  console.log(`${dataSource}最终统计结果:`, stats)
  return stats
}

// 新增：高亮套索特征统计结果
function highlightLassoFeatureStats(lassoStats, dataSource) {
  if (!lassoStats) return
  
  // 清除之前的高亮
  clearFeatureHighlights(dataSource)
  
  // 高亮连续特征的平均值区间
  Object.entries(lassoStats.continuous).forEach(([featureName, stats]) => {
    const avgValue = parseFloat(stats.average)
    const valueRange = findContinuousFeatureRange(featureName, avgValue, dataSource)
    
    if (valueRange) {
      highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`] = true
      updateFeatureBarHighlight(dataSource, featureName, valueRange, true)
    }
  })
  
  // 高亮离散特征的主要分布
  Object.entries(lassoStats.discrete).forEach(([featureName, stats]) => {
    // 高亮占比最高的前2个值
    const topValues = stats.distribution.slice(0, 2)
    topValues.forEach(item => {
      const valueRange = getDiscreteFeatureDescription(featureName, item.value, dataSource)
      if (valueRange) {
        highlightedFeatures.value[dataSource][`${featureName}-${valueRange}`] = true
        updateFeatureBarHighlight(dataSource, featureName, valueRange, true)
      }
    })
  })
}

// 新增：获取离散特征的描述文本
function getDiscreteFeatureDescription(featureName, value, dataSource) {
  const currentDistributionData = dataSource === 'prompt' ? distributionData.value : distributionDataCorpus.value
  
  if (!currentDistributionData?.discrete?.[featureName]) return null
  
  const featureData = currentDistributionData.discrete[featureName]
  const matchingItem = featureData.find(item => item.value === value)
  
  return matchingItem ? matchingItem.value_name : null
}



// ... existing code ...

// 套索弹窗排序相关
const promptLassoSortState = ref('id') // 'id' | 'robustnessDesc' | 'robustnessAsc'
const corpusLassoSortState = ref('id')
// ... existing code ...
</script>

<style scoped>
/* 全局加载遮罩 */
.global-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner-ring {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* 特征图表加载遮罩 */
.feature-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  border-radius: 8px;
}

.feature-loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-icon {
  font-size: 24px;
  color: #409eff;
  animation: spin 1s linear infinite;
}

/* 主布局 */
.main-layout {
  display: flex;
  flex-direction: column;
  height: 98vh;
  width: 99.5vw;
  background: #f5f6fa;
  position: relative;
}

/* 特征区域 */
.top-feature, .bottom-feature {
  flex: 0 0 280px;
  min-height: 280px;
  background: transparent; /* 移除背景 */
  border: none;            /* 去除边框 */
  border-radius: 0;        /* 去除圆角 */
  box-shadow: none;        /* 去除阴影 */
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;               /* 贴合布局，不留外边距 */
}

.top-feature {
  border-bottom: 1px solid #e0e0e0;
  margin-top: 8px; /* 与全局选择区域保持间隔，防止重叠 */
}

.bottom-feature {
  border-top: 1px solid #e0e0e0;
}

/* 中间内容区 */
.middle-row {
  flex: 1 1 auto;
  display: flex;
  flex-direction: row;
  min-height: 0;
  min-width: 0;
  position: relative;
  border: none;
  border-radius: 0;
  box-shadow: none;
}

.center-blank {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  border: none;
  border-radius: 0;
  box-shadow: none;
  width: 100%;
}

/* 全局头部 */
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

/* 全局下拉菜单 */
.global-status-dropdown {
  position: relative;
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

/* 投影区域 */
.projection-row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: stretch;
  width: 100%;
  height: 100%;
  gap: 5px;
  position: relative;
}

.projection-panel {
   flex: 1 1 0;
   display: flex;
   flex-direction: column;
   border: 1px solid #e0e0e0;
   border-radius: 15px;                    /* 添加圆角 */
   box-shadow: 0 2px 8px rgba(0,0,0,0.08); /* 添加阴影 */
   margin: 8px;
   background: #fff;
   position: relative;
   overflow: hidden;    
 }

/* 中间控制区域 */
.center-control-area {
  flex: 0 0 260px;
  display: flex;
  flex-direction: column;
  margin: 8px;
  padding: px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  gap: 0px;
}

/* 攻击方式选择区域 */
.attack-methods-section {
  display: flex;
  flex-direction: column;
}

.attack-methods-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
  padding-bottom: 2px;
  border-bottom: 1px solid #e0e0e0;
}

.attack-methods-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.select-all-checkbox {
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #4e79a7;
}

.select-all-icon {
  font-size: 16px;
  margin-right: 4px;
}

.attack-methods-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 0px;
}

.attack-method-item {
  display: flex;
  align-items: center;
}

.attack-method-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 6px 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.attack-method-name {
  font-size: 13px;
  color: #333;
  flex: 1;
}

.attack-method-checkbox {
  margin-left: 8px;
}

.attack-methods-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.global-robustness-display {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.global-robustness-label {
  color: #666;
  font-weight: 500;
}

.global-robustness-value {
  font-weight: bold;
  font-size: 14px;
  padding: 2px 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #e0e0e0;
}

.submit-btn {
  background: #4e79a7;
  color: white;
  border: none;
  border-radius: 6px;
  /* margin-top: 10px; */
  margin-right: 5px;
  padding: 4px 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover {
  background: #3a5f85;
}

/* 图例容器 */
.legends-container {
  display: flex;
  justify-content: space-around;
  
  gap: 20px;
}

.legend-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.legend-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  text-align: center;
}

.panel-header {
  height: 40px;
  font-size: 20px;
  font-weight: bold;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background: #fff;
}

.panel-tools {
  display: flex;
  gap: 8px;
  margin-right: 10px;
}

.tool-btn {
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: #e3f0ff;
  color: #4e79a7;
  border-color: #4e79a7;
}

.tool-btn.active {
  background: #4e79a7;
  color: white;
  border-color: #4e79a7;
}

.tool-btn.select-btn {
  background: #fff3cd;
  border-color: #ffc107;
  color: #856404;
  font-weight: bold;
}

.tool-btn.select-btn:hover:not(:disabled) {
  background: #ffeaa7;
  border-color: #f39c12;
  color: #6c5ce7;
}

.tool-btn.select-btn.active {
  background: #28a745;
  color: white;
  border-color: #28a745;
}

.tool-btn.select-btn:disabled {
  background: #f8f9fa;
  border-color: #dee2e6;
  color: #6c757d;
  cursor: not-allowed;
}

.panel-content {
  flex: 1 1 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.panel-content svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* 投影图例 */
.projection-legend-corner {
  position: absolute;
  left: 10px;
  bottom: 10px;
  width: 70px;
  z-index: 2;
  background: rgba(255,255,255,0.95);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 4px 0 2px 0;
}

/* 特征图表容器 */
.feature-container {
  width: 100%;
  height: 100%;
  min-height: 260px;
  border: none;
  border-radius: 0;
  box-shadow: none;
  position: relative;
  margin: 2 0 0 2; /* 去除顶部间隔 */
}

.scroll-container {
  width: 100%;
  height: 100%;
  min-height: 260px;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  /* 隐藏滚动条（跨浏览器） */
  scrollbar-width: none;          /* Firefox */
  -ms-overflow-style: none;       /* IE 10+ */
}

/* Chrome、Safari */
.scroll-container::-webkit-scrollbar {
  width: 0;
  height: 0;
}
.scroll-container::-webkit-scrollbar-thumb {
  background: transparent;
}
.scroll-container::-webkit-scrollbar-track {
  background: transparent;
}

.feature-charts {
  display: flex;
  flex-wrap: nowrap; /* 禁止换行，横向滚动 */
  height: 100%;
  width: max-content;
  padding: 0 12px 12px 12px; /* 顶部padding设为0，底部保持 */
  background: transparent; /* 统一使用父级背景色 */
  border-radius: 8px;
  margin: 0 8px; /* 去除与容器顶部的间隔 */
}

.feature-chart {
  flex: 0 0 130px;
  width: 130px;
  height: 260px;
  margin-right: 8px;
  margin-top: 0px;
  /* margin-bottom: 12px; */
  padding: 8px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.feature-chart:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
  border-color: #4e79a7;
}

.feature-chart h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  text-align: center;
  color: #333;
  font-weight: 600;
  padding: 4px 8px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 6px;
  border: 1px solid #dee2e6;
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

/* 图表元素样式 */
.bar-count, .bar-robustness {
  transition: opacity 0.2s;
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

/* 特征标签样式 */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
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
  width: 100%;
}

.feature-tag:hover {
  box-shadow: 0 4px 12px rgba(78,121,167,0.18);
  border-color: #2c4c6b;
}

.tag-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  width: 100%;
}

.tag-content {
  display: flex;
  align-items: center;
  flex: 1;
}

.feature-name {
  font-weight: bold;
  color: #222;
}

.value-range {
  color: #4e79a7;
  font-weight: 500;
}

.feature-count {
  color: #666;
  font-size: 12px;
  margin-left: 4px;
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

.empty-state {
  color: #bbb;
  text-align: center;
  padding: 24px 0;
  font-style: italic;
  font-size: 15px;
  letter-spacing: 1px;
}

/* 历史记录面板 */
.global-history-panel-side {
  position: fixed;
  min-width: 240px;
  min-height: 200px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(78,121,167,0.15);
  z-index: 1000;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.global-history-panel-side.is-dragging {
  box-shadow: 0 8px 30px rgba(78,121,167,0.25);
  cursor: grabbing;
}

.draggable-panel {
  user-select: none;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 12px 8px 8px 8px;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.drag-handle {
  cursor: grab;
  position: relative;
}

.drag-handle:active {
  cursor: grabbing;
}

.drag-indicator {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  font-size: 18px;
  font-weight: bold;
  letter-spacing: 2px;
  writing-mode: vertical-lr;
  text-orientation: mixed;
}

.history-header h4 {
  margin: 0;
  color: #333;
  font-size: 20px;
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
  font-size: 22px;
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
  height: calc(100% - 60px); /* 减去头部高度 */
  overflow-y: auto;
}

/* 表格式历史记录样式 */
.history-table-header {
  display: grid;
  grid-template-columns: 40px 120px 1fr 1fr 1fr 60px;
  gap: 8px;
  padding: 8px 4px;
  background: #f5f5f5;
  border-bottom: 2px solid #e0e0e0;
  font-weight: bold;
  font-size: 16px;
  color: #666;
  margin-bottom: 4px;
  border-radius: 4px 4px 0 0;
}

.history-table-row {
  display: grid;
  grid-template-columns: 40px 120px 1fr 1fr 1fr 60px;
  gap: 8px;
  padding: 8px 4px;
  margin-bottom: 4px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  background: #fff;
  font-size: 16px;
  transition: all 0.2s;
  position: relative;
}

.history-table-row:hover {
  background: #f9f9f9;
  border-color: #4e79a7;
  box-shadow: 0 2px 4px rgba(78,121,167,0.1);
}

.header-cell, .table-cell {
  display: flex;
  align-items: center;
  padding: 4px;
  overflow: hidden;
}

.id-cell {
  justify-content: center;
  font-weight: bold;
  color: #666;
}

.time-cell {
  font-size: 15px;
}

.editable-time {
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 3px;
  transition: background 0.2s;
  word-break: break-all;
  line-height: 1.2;
}

.editable-time:hover {
  background: #e3f0ff;
  color: #4e79a7;
}



.selection-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 3px;
  transition: background 0.2s;
  width: 100%;
}

.selection-summary:hover {
  background: #f0f0f0;
}

.count {
  font-size: 15px;
  color: #666;
}

.dropdown-icon {
  font-size: 14px;
  color: #999;
  transition: transform 0.2s;
}

.dropdown-icon.open {
  transform: rotate(180deg);
}

.dropdown-content {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  margin-top: 2px;
}

.feature-group {
  margin-bottom: 8px;
}

.feature-name {
  font-weight: bold;
  font-size: 15px;
  color: #333;
  margin-bottom: 4px;
}

.feature-items {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.feature-item {
  background: #e3f0ff;
  color: #4e79a7;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 14px;
  border: 1px solid #d0e7ff;
}

.no-attack-methods {
  color: #999;
  font-style: italic;
  font-size: 15px;
  text-align: center;
  padding: 8px;
}

.attack-methods {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.attack-method-item {
  /* background: #fff2e6; */
  color: #d2691e;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 14px;
  /* border: 1px solid #ffe4cc; */
}

.history-apply-btn {
  background: none;
  border: none;
  color: #4e79a7;
  cursor: pointer;
  font-size: 20px;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-apply-btn:hover:not(:disabled) {
  background: #e3f0ff;
  color: #2c5aa0;
}

.history-apply-btn:disabled {
  color: #bbb;
  cursor: not-allowed;
}

/* 旧样式保留用于兼容 */
.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  margin-bottom: 6px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #fff;
  font-size: 18px;
  transition: box-shadow 0.2s, border-color 0.2s;
  cursor: pointer;
}

.history-item:hover {
  box-shadow: 0 2px 5px rgba(0,0,0,0.08);
  border-color: #4e79a7;
}

.history-main-row {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.history-name-input {
  font-size: 18px;
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
  font-size: 20px;
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
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}

/* 加载遮罩 */
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

/* 全局弹出框样式 */
.global-popup {
  position: fixed;
  z-index: 10000;
  background: #f8f8f8;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  overflow: hidden;
  user-select: none;
  min-width: 240px;
  min-height: 120px;
  resize: none;
  box-sizing: border-box;
  transition: box-shadow 0.2s, transform 0.1s;
}

.global-popup:active {
  box-shadow: 0 6px 20px rgba(0,0,0,0.3);
  transform: scale(1.01);
}

.prompt-tooltip, .corpus-tooltip {
  width: 400px;
  height: 600px;
}

.prompt-tooltip {
  border: 1px solid #4e79a7;
}

.corpus-tooltip {
  border: 1px solid #e15759;
}

.lasso-popup {
  width: 600px;
  height: 500px;
  min-width: 1200px;
  min-height: 1000px;
}

.prompt-lasso {
  border: 1.5px solid #4e79a7;
}

.corpus-lasso {
  border: 1.5px solid #e15759;
}

.popup-header {
  height: 24px;
  background: #f0f0f0;
  border-radius: 8px 8px 0 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  border-bottom: 1px solid #e0e0e0;
  cursor: move;
  font-size: 24px;
  font-weight: bold;
  color: #222;
}

.popup-header:hover {
  background: #e8e8e8;
}

.popup-header:active {
  cursor: grabbing;
  background: #e0e0e0;
}

.popup-title {
  flex: 1;
}

.popup-close {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  padding: 2px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
  z-index: 10001;
  position: relative;
}

.popup-close:hover {
  background: #e15759;
  color: white;
}

.popup-close:active {
  background: #b22222;
  color: white;
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

/* 弹出框内容 */
.popup-content {
  padding: 8px;
  height: calc(100% - 24px);
  display: flex;
  flex-direction: column;
}

.popup-content-split {
  height: calc(100% - 24px);
  display: flex;
  flex-direction: row;
  overflow: hidden;
}

.popup-left-panel {
  flex: 0 0 45%;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  padding: 8px;
  background: #f8f9fa;
}

.popup-right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.items-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.popup-scroll-area {
  height: calc(100% - 24px);
  overflow-y: auto;
  padding: 8px;
}

.popup-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.popup-label {
  font-size: 24px;
  font-weight: bold;
  color: #555;
}

.popup-value {
  font-size: 24px;
  font-weight: bold;
  font-family: monospace;
}

.prompt-tooltip .popup-value,
.prompt-lasso .popup-value {
  color: #4e79a7;
}

.corpus-tooltip .popup-value,
.corpus-lasso .popup-value {
  color: #e15759;
}

.popup-text {
  font-size: 24px;
  color: #333;
  font-family: monospace;
  line-height: 1.2;
  word-break: break-word;
  flex: 1;
  overflow: hidden;
}

.popup-item {
  margin-bottom: 8px;
  padding: 8px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.popup-item:hover {
  background: #f8f9fa;
  border-color: #4e79a7;
  box-shadow: 0 2px 8px rgba(78, 121, 167, 0.2);
  transform: translateY(-1px);
}

.popup-item:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(78, 121, 167, 0.3);
}

.corpus-lasso .popup-item:hover {
  border-color: #e15759;
  box-shadow: 0 2px 8px rgba(225, 87, 89, 0.2);
}

.corpus-lasso .popup-item:active {
  box-shadow: 0 1px 4px rgba(225, 87, 89, 0.3);
}

.popup-item:last-child {
  margin-bottom: 0;
}

/* 特征统计样式 */
.feature-stats-section {
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.popup-left-panel .feature-stats-section {
  margin-bottom: 0;
  padding: 8px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.stats-header {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 2px solid #4e79a7;
}

.popup-left-panel .stats-header {
  font-size: 24px;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #4e79a7;
}

.stats-block {
  margin-bottom: 12px;
}

.stats-subheader {
  font-size: 24px;
  font-weight: bold;
  color: #555;
  margin-bottom: 8px;
  padding: 4px 8px;
  background: #e3f0ff;
  border-radius: 4px;
}

.popup-left-panel .stats-subheader {
  font-size: 24px;
  margin-bottom: 6px;
  padding: 3px 6px;
}

.stats-item {
  margin-bottom: 8px;
  padding: 6px 8px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.popup-left-panel .stats-item {
  margin-bottom: 6px;
  padding: 4px 6px;
}

.stats-feature-name {
  font-size: 24px;
  font-weight: bold;
  color: #4e79a7;
  margin-bottom: 4px;
}

.popup-left-panel .stats-feature-name {
  font-size: 24px;
  margin-bottom: 3px;
}

.stats-values {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.popup-left-panel .stats-values {
  gap: 4px;
}

.stats-value {
  font-size: 24px;
  color: #666;
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid #e0e0e0;
}

.popup-left-panel .stats-value {
  font-size: 24px;
  padding: 1px 4px;
}

.stats-distribution {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 24px;
  padding: 2px 6px;
  background: #f8f9fa;
  border-radius: 3px;
  border: 1px solid #e0e0e0;
}

.popup-left-panel .dist-item {
  font-size: 24px;
  padding: 1px 4px;
  margin-bottom: 2px;
}

.dist-value {
  color: #333;
  font-weight: 500;
}

.dist-count {
  color: #666;
  font-family: monospace;
}

.items-header {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 16px 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #e0e0e0;
}

.popup-right-panel .items-header {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
  padding: 8px;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.popup-right-panel .popup-text {
  font-size: 24px;
  line-height: 1.1;
}

/* Corpus套索弹窗的特殊样式 */
.corpus-lasso .stats-header {
  border-bottom-color: #e15759;
}

.corpus-lasso .stats-subheader {
  background: #ffeaea;
}

.corpus-lasso .stats-feature-name {
  color: #e15759;
}

/* 滚动条样式 */
.popup-scroll-area::-webkit-scrollbar,
.items-scroll-area::-webkit-scrollbar {
  width: 6px;
}

.popup-scroll-area::-webkit-scrollbar-track,
.items-scroll-area::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.popup-scroll-area::-webkit-scrollbar-thumb,
.items-scroll-area::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.popup-scroll-area::-webkit-scrollbar-thumb:hover,
.items-scroll-area::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Firefox滚动条样式 */
.popup-scroll-area,
.items-scroll-area {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

/* 缩放手柄 */
.resize-handle {
  position: absolute;
  z-index: 10;
  background: transparent;
}

.resize-handle.n, .resize-handle.s {
  left: 8px; right: 8px; height: 8px; cursor: ns-resize;
}

.resize-handle.n { top: -4px; }
.resize-handle.s { bottom: -4px; }

.resize-handle.e, .resize-handle.w {
  top: 8px; bottom: 8px; width: 8px; cursor: ew-resize;
}

.resize-handle.e { right: -4px; }
.resize-handle.w { left: -4px; }

.resize-handle.nw, .resize-handle.ne, .resize-handle.sw, .resize-handle.se {
  width: 14px; height: 14px; background: #bbb3; border-radius: 3px;
}

.resize-handle.nw { top: -7px; left: -7px; cursor: nwse-resize; }
.resize-handle.ne { top: -7px; right: -7px; cursor: nesw-resize; }
.resize-handle.sw { bottom: -7px; left: -7px; cursor: nesw-resize; }
.resize-handle.se { bottom: -7px; right: -7px; cursor: nwse-resize; }

.prompt-tooltip .popup-text,
.corpus-tooltip .popup-text {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 12px;
  margin-top: 12px;
  font-size: 18px;
  color: #333;
  font-family: monospace;
  line-height: 1.4;
  word-break: break-all;
}

/* 攻击方式选择面板样式 */
.attack-methods-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  max-height: 70vh;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.attack-methods-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  /* padding: 16px 20px; */
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.attack-methods-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.close-attack-methods {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-attack-methods:hover {
  color: #333;
}

.attack-methods-content {
  padding: 20px;
  max-height: 50vh;
  overflow-y: auto;
}

.attack-method-item {
  margin-bottom: 6px;
}

.attack-method-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.attack-method-label:hover {
  background-color: #f8f9fa;
}

.attack-method-checkbox {
  margin-right: 12px;
  width: 16px;
  height: 16px;
}

.attack-method-name {
  font-weight: 600;
  color: #333;
  margin-right: 8px;
  min-width: 100px;
}

.attack-method-desc {
  color: #666;
  font-size: 14px;
}

.attack-methods-actions {
  display: flex;
  gap: 2px;
  margin-top: 2px;
  padding-top: 2px;
  border-top: 1px solid #e9ecef;
}

.submit-attack-methods {
  flex: 1;
  padding: 10px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.submit-attack-methods:hover:not(:disabled) {
  background: #0056b3;
}

.submit-attack-methods:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.clear-attack-methods {
  padding: 10px 16px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.clear-attack-methods:hover {
  background: #545b62;
}

.attack-methods-section {
  margin-left: 8px;
}

/* 攻击方式选择中间区域样式 */
.attack-methods-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.attack-methods-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.select-all-checkbox {
  cursor: pointer;
  padding: 2px;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.select-all-checkbox:hover {
  background-color: #f0f0f0;
}

.select-all-icon {
  font-size: 16px;
  color: #007bff;
  font-weight: bold;
}

.attack-methods-list {
  flex: 1;
  margin-bottom: 4px;
}

.attack-methods-middle .attack-method-item {
  margin-bottom: 4px;
  padding: 2px 0;
}

.attack-methods-middle .attack-method-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  padding: 4px;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.attack-methods-middle .attack-method-content:hover {
  background-color: #f8f9fa;
}

.attack-methods-middle .attack-method-checkbox {
  width: 14px;
  height: 10px;
  cursor: pointer;
}

.attack-methods-middle .attack-method-name {
  font-weight: 500;
  min-width: auto;
}

.attack-methods-middle .attack-methods-actions {
  display: flex;
  justify-content: center;
  padding-top: 12px;
  border-top: 1px solid #eee;
  margin-top: auto;
}

.attack-methods-middle .submit-attack-methods {
  background: #007bff;
  color: white;
  border: 1px solid #007bff;
  border-radius: 4px;
  padding: 2px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  flex: none;
}

.attack-methods-middle .submit-attack-methods:hover {
  background: #0056b3;
  border-color: #0056b3;
}
</style>


