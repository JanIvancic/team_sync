<template>
  <div class="session-container">
    <button @click="createSession">Create Session</button>
    <div class="join-group">
      <input v-model="joinId" placeholder="Enter session code" />
      <button @click="joinSession">Join</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return { joinId: '' }
  },
  methods: {
    async createSession() {
      try {
        const res = await axios.post('/session')
        this.$emit('session-created', { id: res.data.session_id, admin: true })
      } catch (error) {
        console.error('Error creating session:', error)
        alert('Failed to create session. Please try again.')
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
.session-container {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.join-group {
  margin-top: 10px;
}
</style>
