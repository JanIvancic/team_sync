

<template>
  <div class="teams-container">
    <div v-for="(team, index) in teams" :key="index" class="team-card">
      <h3>Team {{ index + 1 }}</h3>
      <div class="team-metrics">
        <div>Average Similarity: {{ (team.metrics.avg_similarity * 100).toFixed(1) }}%</div>
        <div>THI: {{ (team.metrics.thi * 100).toFixed(1) }}%</div>
      </div>
      <div class="team-members">
        <div v-for="member in team.members" :key="member.memberIndex" class="member-card">
          <div class="member-header">
            <h4>{{ member.name }}</h4>
            <div class="member-role">{{ member.preferred_role }}</div>
          </div>
          <div class="member-skills">
            <div v-for="skill in ['tech_skills', 'comm_skills', 'creative_skills', 'leadership_skills']" 
                 :key="skill" 
                 class="skill-bar">
              <div class="skill-label">{{ skill.replace('_', ' ').toUpperCase() }}</div>
              <div class="skill-value">
                <div class="skill-fill" :style="{ width: (member[skill] / 5 * 100) + '%' }"></div>
                <span>{{ member[skill] }}/5</span>
              </div>
            </div>
          </div>
          <div class="member-traits">
            <div class="trait" v-for="trait in ['pressure_handling', 'team_satisfaction', 'flexibility']" 
                 :key="trait">
              {{ trait.replace('_', ' ').toUpperCase() }}: {{ member[trait] }}/5
            </div>
            <div class="trait">Conflict Management: {{ member.conflict_management }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    teams: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
.teams-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 20px;
}

.team-card {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 15px;
  flex: 1;
  min-width: 300px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.team-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px;
  background: #e0e0e0;
  border-radius: 4px;
}

.team-members {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.member-card {
  background: white;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.member-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.member-role {
  background: #e3f2fd;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
}

.member-skills {
  margin-bottom: 10px;
}

.skill-bar {
  margin-bottom: 8px;
}

.skill-label {
  font-size: 0.9em;
  margin-bottom: 4px;
}

.skill-value {
  display: flex;
  align-items: center;
  gap: 10px;
}

.skill-fill {
  background: #4caf50;
  height: 8px;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.member-traits {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
  font-size: 0.9em;
}

.trait {
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
}
</style> 