<template>
  <div style="margin-top:20px">
    <form @submit.prevent="submitSurvey">
      <div v-for="field in fields" :key="field.key" style="margin-bottom:15px">
        <label>{{ field.label }}</label>
        <component
          :is="field.type === 'slider' ? 'input' : 'select'"
          v-model="survey[field.key]"
          v-bind="field.props"
        >
          <option v-for="opt in field.options || []" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </component>
      </div>
      <button type="submit">Submit Survey</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: ['sessionId', 'isAdmin'],
  data() {
    return {
      survey: {
        name: '',
        tech_skills: 3,
        comm_skills: 3,
        creative_skills: 3,
        leadership_skills: 3,
        preferred_role: null,
        pressure_handling: 3,
        team_satisfaction: 3,
        flexibility: 3,
        leadership_frequency: 3,
        idea_frequency: 3,
        self_learning_readiness: 3,
        conflict_management: null
      },
      fields: [
        { key: 'name', label: 'Your Name', type: 'text', props: { type: 'text', required: true } },
        { key: 'tech_skills', label: 'Tech Skills (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        { key: 'comm_skills', label: 'Comm Skills (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        { key: 'creative_skills', label: 'Creative Skills (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        { key: 'leadership_skills', label: 'Leadership Skills (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        {
          key: 'preferred_role',
          label: 'Preferred Role',
          type: 'select',
          options: [
            { label: 'Leader', value: 'leader' },
            { label: 'Tech Support', value: 'tech_support' },
            { label: 'Analyst', value: 'analyst' },
            { label: 'Presenter', value: 'presenter' },
            { label: 'Any', value: 'any' }
          ]
        },
        { key: 'pressure_handling', label: 'Pressure Handling (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        { key: 'team_satisfaction', label: 'Team Satisfaction (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        { key: 'flexibility', label: 'Flexibility (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        { key: 'leadership_frequency', label: 'Leadership Frequency (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        { key: 'idea_frequency', label: 'Idea Frequency (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        { key: 'self_learning_readiness', label: 'Self-Learning Readiness (1-5)', type: 'slider', props: { type: 'range', min:1, max:5 } },
        {
          key: 'conflict_management',
          label: 'Conflict Management',
          type: 'select',
          options: [
            { label: 'Avoid', value: 'avoid' },
            { label: 'Hesitant', value: 'hesitant' },
            { label: 'Compromise', value: 'compromise' },
            { label: 'Talk', value: 'talk' },
            { label: 'Active', value: 'active' }
          ]
        }
      ]
    }
  },
  methods: {
    async submitSurvey() {
      try {
        await axios.post(`/session/${this.sessionId}/survey`, this.survey)
        if (this.isAdmin) {
          const res = await axios.get(`/session/${this.sessionId}/surveys`)
          this.$emit('surveys-updated', res.data)
        } else {
          alert('Survey submitted successfully!')
        }
      } catch (error) {
        console.error('Error submitting survey:', error)
        alert('Failed to submit survey. Please try again.')
      }
    }
  }
}
</script>

<style scoped>
form {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  max-width: 500px;
  margin: 0 auto;
}

div {
  width: 100%;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input[type="range"] {
  width: 100%;
}

select {
  width: 100%;
  padding: 8px;
}

button {
  align-self: center;
  margin-top: 20px;
}
</style>
