<template>
  <div style="margin-top:20px">
    <div v-if="submitted" class="success-message">
      Survey submitted successfully! Thank you for your participation.
    </div>
    <form v-else @submit.prevent="submitSurvey">
      <div v-if="!anonymousMode" style="margin-bottom:15px">
        <label for="name">Your Name:</label>
        <input type="text" id="name" v-model="survey.name" :required="!anonymousMode">
      </div>
      <div v-else style="margin-bottom:15px">
        <p class="anonymous-notice">Anonymous Mode: Your responses will be recorded without your name</p>
      </div>
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
  name: 'SurveyForm',
  props: {
    sessionId: {
      type: String,
      required: true
    },
    isAdmin: {
      type: Boolean,
      default: false
    },
    anonymousMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      submitted: false,
      survey: {
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
  mounted() {
    console.log('SurveyForm mounted with anonymousMode:', this.anonymousMode);
    // Initialize name field only if not in anonymous mode
    if (!this.anonymousMode) {
      this.survey.name = '';
    }
  },
  methods: {
    async submitSurvey() {
      try {
        // Generate a unique user ID if in anonymous mode
        if (this.anonymousMode) {
          const userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          this.survey.id = userId;
          this.survey.name = `Anonymous User ${userId.substring(5, 10)}`; // Add a readable name for the backend
          sessionStorage.setItem('currentUserId', userId);
        } else if (this.survey.name) {
          // In named mode, use the name as the ID
          this.survey.id = this.survey.name;
          sessionStorage.setItem('currentUserId', this.survey.name);
        }
        
        // Validate required fields
        if (!this.validateSurvey()) {
          alert('Please fill in all required fields');
          return;
        }
        
        const response = await axios.post(`/api/session/${this.sessionId}/survey`, this.survey);
        
        if (response.data && response.data.currentUser) {
          // Store the current user ID from the response
          sessionStorage.setItem('currentUserId', response.data.currentUser);
        }
        
        this.$emit('surveys-updated', response.data);
        this.submitted = true;
        
        // Store in sessionStorage that this user has submitted
        sessionStorage.setItem(`survey_submitted_${this.sessionId}`, 'true');
        
      } catch (error) {
        console.error('Error submitting survey:', error);
        if (error.response) {
          alert(`Failed to submit survey: ${error.response.data.error || 'Unknown error'}`);
        } else {
          alert('Failed to submit survey. Please check your connection and try again.');
        }
      }
    },
    
    validateSurvey() {
      // Check if all required fields are filled
      for (const field of this.fields) {
        if (field.props && field.props.required && !this.survey[field.key]) {
          return false;
        }
      }
      
      // Name is only required in named mode
      if (!this.anonymousMode && !this.survey.name) {
        return false;
      }
      
      return true;
    }
  },
  created() {
    // Check if user has already submitted a survey for this session
    if (sessionStorage.getItem(`survey_submitted_${this.sessionId}`) === 'true') {
      this.submitted = true;
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

input[type="text"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

select {
  width: 100%;
  padding: 8px;
}

button {
  align-self: center;
  margin-top: 20px;
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.anonymous-notice {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  color: #666;
  font-style: italic;
  text-align: center;
}

.success-message {
  padding: 20px;
  background-color: #dff0d8;
  color: #3c763d;
  border-radius: 4px;
  text-align: center;
  margin-bottom: 20px;
  border: 1px solid #d6e9c6;
}
</style>
