<template>
  <div class="team-graph">
    <h3>Team Network</h3>
    <div ref="graphContainer" class="graph-container"></div>
  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'TeamGraph',
  props: {
    teams: {
      type: Array,
      required: true
    },
    anonymousMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      width: 800,
      height: 600,
      simulation: null,
      svg: null
    }
  },
  mounted() {
    this.initGraph();
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
  },
  watch: {
    teams: {
      handler: 'updateGraph',
      deep: true
    }
  },
  methods: {
    handleResize() {
      this.width = this.$refs.graphContainer.clientWidth;
      this.height = this.$refs.graphContainer.clientHeight;
      this.initGraph();
    },
    initGraph() {
      // Clear any existing graph
      if (this.svg) {
        this.svg.remove();
      }

      // Create SVG container
      this.svg = d3.select(this.$refs.graphContainer)
        .append('svg')
        .attr('width', this.width)
        .attr('height', this.height)
        .call(d3.zoom()
          .scaleExtent([0.5, 4])
          .on('zoom', (event) => {
            this.svg.selectAll('g').attr('transform', event.transform);
          }));

      // Initialize simulation
      this.simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(this.width / 2, this.height / 2));

      this.updateGraph();
    },
    updateGraph() {
      if (!this.teams || this.teams.length === 0) return;

      // Prepare nodes and links
      const nodes = [];
      const links = [];
      const nodeMap = new Map();

      // Create nodes and links for each team
      this.teams.forEach((team, teamIndex) => {
        // Each team is already an array of members
        team.forEach((member, memberIndex) => {
          const nodeId = `${teamIndex}-${memberIndex}`;
          const node = {
            id: nodeId,
            name: this.anonymousMode ? `Member ${memberIndex + 1}` : (member.name || `Member ${memberIndex + 1}`),
            team: teamIndex,
            x: Math.random() * this.width,
            y: Math.random() * this.height
          };
          nodes.push(node);
          nodeMap.set(nodeId, node);

          // Create links between team members
          for (let i = 0; i < memberIndex; i++) {
            links.push({
              source: `${teamIndex}-${i}`,
              target: nodeId
            });
          }
        });
      });

      // Clear existing elements
      this.svg.selectAll('*').remove();

      // Create links
      const link = this.svg.append('g')
        .selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', 2);

      // Create nodes
      const node = this.svg.append('g')
        .selectAll('g')
        .data(nodes)
        .enter()
        .append('g')
        .call(d3.drag()
          .on('start', this.dragstarted)
          .on('drag', this.dragged)
          .on('end', this.dragended));

      // Add circles to nodes
      node.append('circle')
        .attr('r', 25)
        .attr('fill', d => d3.schemeCategory10[d.team % 10])
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);

      // Add text labels
      node.append('text')
        .text(d => d.name)
        .attr('x', 0)
        .attr('y', 35)
        .attr('text-anchor', 'middle')
        .style('font-size', '14px')
        .style('font-weight', 'bold')
        .style('fill', '#333');

      // Update simulation
      this.simulation
        .nodes(nodes)
        .on('tick', () => {
          link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

          node.attr('transform', d => `translate(${d.x},${d.y})`);
        });

      this.simulation.force('link').links(links);
    },
    dragstarted(event, d) {
      if (!event.active) this.simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    },
    dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    },
    dragended(event, d) {
      if (!event.active) this.simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }
}
</script>

<style scoped>
.team-graph {
  margin-top: 20px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.graph-container {
  width: 100%;
  height: 600px;
  border: 1px solid #eee;
  border-radius: 4px;
  overflow: hidden;
}

svg {
  width: 100%;
  height: 100%;
}

@media (max-width: 768px) {
  .graph-container {
    height: 400px;
  }
}
</style>
