<template>
  <div>
    <button @click="createSession">Create Session</button>
    <input v-model="joinId" placeholder="Session code" style="margin-left:10px"/>
    <button @click="joinSession" style="margin-left:5px">Join</button>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SessionManager',
  data() {
    return { joinId: '' }
  },
  methods: {
    async createSession() {
      try {
        console.log('Creating new session...');
        const res = await axios.post('/api/session');
        console.log('Session created response:', res.data);

        // Set admin flag in localStorage
        localStorage.setItem('isAdminFlow', 'true');

        // Create payload with session data
        const payload = {
          id: res.data.id,
          isAdmin: true,
          settingsConfirmed: false,
          settings: res.data.settings || {
            anonymousMode: false,
            showTeamsToUsers: true,
            teamSize: 4,
            teamApproach: "homogeni",
            characteristics: ["tech_skills", "comm_skills", "creative_skills", "leadership_skills"],
            similarityThreshold: 50
          }
        };
        
        console.log('Emitting session-created with payload:', payload);
        this.$emit('session-created', payload);
      } catch (error) {
        console.error('Error creating session:', error);
        if (error.response) {
          alert(`Failed to create session: ${error.response.data.error || 'Unknown error'}`);
        } else {
          alert('Failed to create session. Please check your connection and try again.');
        }
      }
    },
    
    async joinSession() {
      if (!this.joinId) {
        alert('Please enter a session code');
        return;
      }
      
      try {
        // Verify the session exists
        const res = await axios.get(`/api/session/${this.joinId}`);
        
        // Create payload with session data
        const payload = {
          id: this.joinId,
          isAdmin: false,
          settingsConfirmed: true,
          settings: res.data.settings || {
            anonymousMode: false,
            showTeamsToUsers: true,
            teamSize: 4,
            teamApproach: "homogeni",
            characteristics: ["tech_skills", "comm_skills", "creative_skills", "leadership_skills"],
            similarityThreshold: 50
          }
        };
        
        this.$emit('session-created', payload);
      } catch (error) {
        console.error('Error joining session:', error);
        if (error.response) {
          if (error.response.status === 404) {
            alert('Session not found. Please check the session code and try again.');
          } else {
            alert(`Failed to join session: ${error.response.data.error || 'Unknown error'}`);
          }
        } else {
          alert('Failed to join session. Please check your connection and try again.');
        }
      }
    }
  }
}
</script>

<style scoped>
div {
  margin-bottom: 20px;
}
</style>
