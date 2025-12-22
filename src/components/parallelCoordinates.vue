


<template>
    <div>
      <div id="parallel-coordinates"></div>
    </div>
  </template>
  
  <script>
  import * as d3 from 'd3';
  
  export default {
    name: 'ParallelCoordinates',
    data() {
      return {
        data: [],
        dimensions: [],
        width: 800,
        height: 500,
        margin: { top: 30, right: 30, bottom: 30, left: 60 }
      };
    },
    mounted() {
      this.fetchData();
    },
    methods: {
      async fetchData() {
        try {
          const response = await fetch('http://localhost:5000/get_prompt_data', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: [] }) // 获取所有数据
          });
          
          const result = await response.json();
          if (result.success) {
            this.data = result.data;
            this.drawParallelCoordinates();
          } else {
            console.error('Error fetching data:', result.error);
          }
        } catch (error) {
          console.error('Fetch error:', error);
        }
      },
      drawParallelCoordinates() {
  // 清除之前的图表
  d3.select('#parallel-coordinates').selectAll('*').remove();

  if (this.data.length === 0) return;
  
  // 创建维度数组
  this.dimensions = [];
  
  // 添加vector的各个维度
  const vectorLength = this.data[0].vector.length;
  for (let i = 0; i < vectorLength; i++) {
    this.dimensions.push({
      name: `F${i}`,
      index: i,
      type: 'number'
    });
  }
  
  // 添加accuracy维度
  this.dimensions.push({
    name: 'Accuracy',
    index: 'accuracy',
    type: 'number'
  });

  // 计算实际绘图尺寸
  const innerWidth = this.width - this.margin.left - this.margin.right;
  const innerHeight = this.height - this.margin.top - this.margin.bottom;

  // 创建SVG
  const svg = d3.select('#parallel-coordinates')
    .append('svg')
    .attr('width', this.width)
    .attr('height', this.height)
    .append('g')
    .attr('transform', `translate(${this.margin.left},${this.margin.top})`);

  // 创建比例尺
  const x = d3.scalePoint()
    .domain(this.dimensions.map(d => d.name))
    .range([0, innerWidth])
    .padding(0.5);

  const y = {};
  this.dimensions.forEach(dim => {
    // 获取该维度的所有值
    const values = this.data.map(d => {
      const val = dim.index === 'accuracy' ? d.accuracy : d.vector[dim.index];
      return +val; // 确保转换为数字
    });
    
    // 计算值域范围，确保有最小间隔
    const extent = d3.extent(values);
    const range = extent[1] - extent[0];
    const padding = range * 0.1; // 添加10%的padding
    
    y[dim.name] = d3.scaleLinear()
      .domain([extent[0] - padding, extent[1] + padding])
      .range([innerHeight, 0]);
  });

  // 创建线条生成器
  const line = d3.line()
    .defined(d => !isNaN(d.value))
    .x(d => x(d.dimension))
    .y(d => y[d.dimension](d.value));

  // 绘制线条
  svg.selectAll(".line")
    .data(this.data)
    .enter()
    .append("path")
    .attr("class", "line")
    .attr("d", d => {
      const points = this.dimensions.map(dim => {
        const value = dim.index === 'accuracy' 
          ? d.accuracy 
          : d.vector[dim.index];
        return {
          dimension: dim.name,
          value: +value // 确保转换为数字
        };
      });
      return line(points);
    })
    .style("stroke", (d, i) => d3.schemeCategory10[i % 10])
    .style("stroke-width", 1)
    .style("fill", "none")
    .style("opacity", 0.5);

  // 添加坐标轴
  this.dimensions.forEach(dim => {
    svg.append("g")
      .attr("class", "axis")
      .attr("transform", `translate(${x(dim.name)},0)`)
      .call(d3.axisLeft(y[dim.name]).ticks(5));
  });

  // 添加维度标签
  svg.selectAll(".dimension-label")
    .data(this.dimensions)
    .enter()
    .append("text")
    .attr("class", "dimension-label")
    .attr("x", d => x(d.name))
    .attr("y", -15)
    .attr("text-anchor", "middle")
    .text(d => d.name);
}
    }
  };
  </script>
  
  <style scoped>
  #line {
    margin: 20px;
  }
  
  .line {
    stroke-width: 1.5;
    stroke-opacity: 0.7;
    fill: none;
  }
  
  .axis path,
  .axis line {
    fill: none;
    stroke: #ccc;
    shape-rendering: crispEdges;
  }
  
  .axis text {
    font-size: 10px;
  }
  
  .dimension-label {
    font-size: 12px;
    font-weight: bold;
  }
  </style>