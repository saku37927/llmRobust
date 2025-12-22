<template>
  <div id="app">
    <SankeyDiagram />
    <!-- <threedChart /> -->
    <!-- <parallelCoordinates/> -->
  </div>
</template>

<script>
import SankeyDiagram from './components/SankeyDiagram.vue'
// import parallelCoordinates from './components/parallelCoordinates.vue';
// import threedChart from './components/threeChart.vue'

export default {
  name: 'App',
  components: {
    SankeyDiagram
    // threedChart,
    // parallelCoordinates
}
}
</script>