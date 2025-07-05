<template>
  <div id="app">
    <Session @session-created="onSessionCreated" />

    <div v-if="sessionId" class="session-banner">
      <p>Session Code: <strong>{{ sessionId }}</strong></p>
      <p v-if="isAdmin">Share this code with participants to join.</p>
    </div>

    <SurveyForm
      v-if="sessionId"
      :sessionId="sessionId"
      :isAdmin="isAdmin"
      @surveys-updated="onSurveysUpdated"
    />

    <div v-if="sessionId && isAdmin" class="admin-tools">
      <p>Responses: {{ surveys.length }}</p>
      <button @click="fetchTeams" :disabled="surveys.length < minResponses">
        Generate Teams
      </button>
      <p v-if="surveys.length < minResponses" class="hint">Waiting for more responses...</p>
    </div>

    <TeamGraph v-if="teams.length" :teams="teams" />
  </div>
</template>

<script>
import Session from './components/Session.vue'
import SurveyForm from './components/SurveyForm.vue'
import TeamGraph from './components/TeamGraph.vue'
import axios from 'axios'

export default {
  components: { Session, SurveyForm, TeamGraph },
  data() {
    return {
      sessionId: null,
      isAdmin: false,
      surveys: [],
      teams: [],
      minResponses: 1
    }
  },
  methods: {
    onSessionCreated({ id, admin }) {
      this.sessionId = id
      this.isAdmin = admin
      if (admin) this.pollSurveys()
    },
    onSurveysUpdated(list) {
      this.surveys = list
    },
    async pollSurveys() {
      this.surveyInterval = setInterval(async () => {
        try {
          const res = await axios.get(`/session/${this.sessionId}/surveys`)
          this.surveys = res.data
        } catch (error) {
          console.error('Error polling surveys:', error)
        }
      }, 3000)
    },
    async fetchTeams() {
      try {
        const res = await axios.post(`/session/${this.sessionId}/teams`)
        this.teams = res.data.teams
        clearInterval(this.surveyInterval)
      } catch (error) {
        console.error('Error fetching teams:', error)
      }
    }
  },
  beforeUnmount() {
    clearInterval(this.surveyInterval)
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 20px;
}

button {
  background-color: #4CAF50;
  border: none;
  color: white;
  padding: 10px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 4px;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

input, select {
  padding: 8px;
  margin: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.session-banner {
  margin-bottom: 20px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.admin-tools {
  margin-top: 20px;
}

.hint {
  font-size: 0.9em;
  color: #888;
}
</style>
