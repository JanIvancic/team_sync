<template>
  <div class="graph-container">
    <h2>Team Visualization</h2>
    <div ref="cy" class="cytoscape-container"></div>
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
      console.log('Rendering graph with teams:', this.teams);

      // Check if teams data is valid
      if (!this.teams || !Array.isArray(this.teams) || this.teams.length === 0) {
        console.error('Invalid teams data:', this.teams);
        return;
      }

      const elements = []

      // Create nodes and edges for each team
      this.teams.forEach((team, t) => {
        console.log(`Processing team ${t}:`, team);

        // Skip empty teams
        if (!team || !Array.isArray(team) || team.length === 0) {
          console.warn(`Team ${t} is empty or invalid`);
          return;
        }

        // Add nodes for each team member
        team.forEach(u => {
          if (!u) {
            console.warn('Skipping undefined team member');
            return;
          }

          console.log(`Adding node for team member: ${u}`);
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
            if (!team[i] || !team[j]) continue;

            console.log(`Adding edge between ${team[i]} and ${team[j]}`);
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

      console.log('Generated graph elements:', elements);

      // Don't render if no elements
      if (elements.length === 0) {
        console.warn('No elements to render in graph');
        return;
      }

      // Create the graph
      try {
        const cy = cytoscape({
          container: this.$refs.cy,
          elements,
          style: [
            {
              selector: 'node',
              style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'font-size': '14px',
                'color': '#fff',
                'text-outline-width': 2,
                'text-outline-color': '#888',
                'width': 60,
                'height': 60,
                'font-weight': 'bold'
              }
            },
            {
              selector: 'edge',
              style: {
                'line-color': '#999',
                'width': 3,
                'curve-style': 'bezier',
                'opacity': 0.8
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
            padding: 50,
            randomize: true,
            componentSpacing: 150,
            nodeRepulsion: 800000,  // Increased for better spacing
            nodeOverlap: 20,
            idealEdgeLength: 150,   // Increased for better spacing
            edgeElasticity: 200,    // Increased for better spacing
            nestingFactor: 5,
            gravity: 100,           // Increased for better cohesion
            numIter: 2000,          // More iterations for better layout
            initialTemp: 250,
            coolingFactor: 0.95,
            minTemp: 1.0
          }
        });

        // Center the graph after it's rendered
        setTimeout(() => {
          cy.center();
          cy.fit();
        }, 500);

        console.log('Graph rendered successfully');
      } catch (error) {
        console.error('Error rendering graph:', error);
      }
    }
  }
}
</script>

<style scoped>
.graph-container {
  margin: 30px 0;
}

.cytoscape-container {
  width: 100%;
  height: 500px;
  margin-top: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
}
</style>
