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
div {
  margin-bottom: 20px;
}
</style>
