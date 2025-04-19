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

        // IMPORTANT: Force admin to go to settings first
        // We're setting a flag in localStorage to indicate that we're in the admin flow
        localStorage.setItem('isAdminFlow', 'true');

        const payload = { id: res.data.id, admin: true };
        console.log('Emitting session-created with payload:', payload);
        this.$emit('session-created', payload);
      } catch (error) {
        console.error('Error creating session:', error)
        console.error('Error details:', error.response ? error.response.data : 'No response data')
        console.error('Error status:', error.response ? error.response.status : 'No status')
        alert(`Failed to create session. Error: ${error.message}`)
      }
    },
    joinSession() {
      if (!this.joinId) return
      this.$emit('session-created', { id: this.joinId, admin: false })
    }
  }
}
</script>

<style scoped>
div {
  margin-bottom: 20px;
}
</style>
