<template>
  <div class="graph-container">
    <h2>Teams</h2>
    <div ref="cy" class="graph"></div>
  </div>
</template>

<script>
import cytoscape from 'cytoscape'

export default {
  props: ['teams'],
  mounted() {
    this.renderGraph()
  },
  watch: {
    teams: {
      handler() {
        this.renderGraph()
      },
      deep: true
    }
  },
  methods: {
    renderGraph() {
      const elements = []
      
      // Create nodes and edges for each team
      this.teams.forEach((team, t) => {
        // Add nodes for each team member
        team.forEach(u => {
          elements.push({ 
            data: { 
              id: u, 
              label: u, 
              team: t 
            } 
          })
        })
        
        // Add edges between team members
        for (let i = 0; i < team.length; i++) {
          for (let j = i + 1; j < team.length; j++) {
            elements.push({
              data: { 
                id: `${team[i]}-${team[j]}`,
                source: team[i], 
                target: team[j] 
              }
            })
          }
        }
      })
      
      // Create the graph
      cytoscape({
        container: this.$refs.cy,
        elements,
        style: [
          { 
            selector: 'node', 
            style: { 
              'label': 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'font-size': '12px',
              'color': '#fff',
              'text-outline-width': 1,
              'text-outline-color': '#888',
              'width': 40,
              'height': 40
            } 
          },
          { 
            selector: 'edge', 
            style: { 
              'line-color': '#ccc',
              'width': 2,
              'curve-style': 'bezier'
            } 
          },
          { 
            selector: '[team = 0]', 
            style: { 
              'background-color': '#0074D9',
              'text-outline-color': '#0074D9'
            } 
          },
          { 
            selector: '[team = 1]', 
            style: { 
              'background-color': '#FF4136',
              'text-outline-color': '#FF4136'
            } 
          },
          { 
            selector: '[team = 2]', 
            style: { 
              'background-color': '#2ECC40',
              'text-outline-color': '#2ECC40'
            } 
          },
          { 
            selector: '[team = 3]', 
            style: { 
              'background-color': '#FFDC00',
              'text-outline-color': '#FFDC00'
            } 
          }
        ],
        layout: { 
          name: 'cose',
          animate: true,
          nodeDimensionsIncludeLabels: true,
          refresh: 20,
          fit: true,
          padding: 30,
          randomize: true,
          componentSpacing: 100,
          nodeRepulsion: 400000,
          nodeOverlap: 10,
          idealEdgeLength: 100,
          edgeElasticity: 100,
          nestingFactor: 5,
          gravity: 80,
          numIter: 1000,
          initialTemp: 200,
          coolingFactor: 0.95,
          minTemp: 1.0
        }
      })
    }
  }
}
</script>

<style scoped>
.graph-container {
  margin-top: 30px;
}

.graph {
  width: 100%;
  height: 400px;
  margin-top: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
