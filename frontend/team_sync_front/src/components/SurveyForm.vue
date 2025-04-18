<template>
  <div style="margin-top:20px">
    <form @submit.prevent="submitSurvey">
      <!-- Name field only shown when not in anonymous mode -->
      <div v-if="!anonymousMode" style="margin-bottom:15px">
        <label>{{ fields[0].label }}</label>
        <input
          type="text"
          v-model="survey.name"
          :required="!anonymousMode"
        >
      </div>

      <!-- All other fields always shown -->
      <div v-for="field in fields.filter(f => f.key !== 'name')" :key="field.key" style="margin-bottom:15px">
        <label>{{ field.label }}</label>
        <component
          :is="getComponentType(field.type)"
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
  props: {
    sessionId: String,
    isAdmin: Boolean,
    anonymousMode: {
      type: Boolean,
      default: false
    }
  },
  created() {
    console.log('SurveyForm created with anonymousMode:', this.anonymousMode);
    // Generate a random name for anonymous users
    if (this.anonymousMode) {
      this.survey.name = `Anonymous-${Math.floor(Math.random() * 10000)}`;
      console.log('Generated anonymous name:', this.survey.name);
    }
  },
  mounted() {
    console.log('SurveyForm mounted with anonymousMode:', this.anonymousMode);
  },
  data() {
    return {
      hasSubmitted: false,
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
        { key: 'name', label: 'Your Name', type: 'text', props: { type: 'text', required: false } },
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
  watch: {
    anonymousMode(newVal) {
      console.log('anonymousMode changed to:', newVal);
    }
  },
  computed: {
    visibleFields() {
      // Filter out the name field if in anonymous mode
      console.log('Anonymous mode:', this.anonymousMode);
      const result = this.anonymousMode
        ? this.fields.filter(field => field.key !== 'name')
        : this.fields;
      console.log('Visible fields:', result.map(f => f.key));
      return result;
    }
  },
  methods: {
    getComponentType(type) {
      // Return the appropriate component type based on the field type
      switch(type) {
        case 'text':
          return 'input';
        case 'slider':
          return 'input';
        case 'select':
          return 'select';
        default:
          return 'input';
      }
    },
    async submitSurvey() {
      if (this.hasSubmitted) {
        alert('You have already submitted a survey for this session.');
        return;
      }

      try {
        console.log('Submitting survey:', this.survey);
        await axios.post(`/api/session/${this.sessionId}/survey`, this.survey);
        this.hasSubmitted = true;
        this.$emit('surveys-updated', this.survey);
        alert('Survey submitted successfully!');
      } catch (error) {
        console.error('Error submitting survey:', error);
        alert('Failed to submit survey. Please try again.');
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
