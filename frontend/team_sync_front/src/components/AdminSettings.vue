<template>
  <div class="admin-settings">
    <h2>Session Settings</h2>
    <form @submit.prevent="saveSettings">
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="settings.anonymousMode" />
          Anonymous Mode (users don't need to enter their names)
        </label>
      </div>
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="settings.showTeamsToUsers" />
          Show generated teams to users
        </label>
      </div>
      <button type="submit" class="primary-button">Save Settings & Get Session Code</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'AdminSettings',
  data() {
    return {
      settings: {
        anonymousMode: false,
        showTeamsToUsers: true
      }
    }
  },
  created() {
    console.log('AdminSettings component created');
  },
  mounted() {
    console.log('AdminSettings component mounted');
  },
  methods: {
    saveSettings() {
      console.log('Saving settings:', this.settings);
      this.$emit('settings-saved', this.settings);
    }
  }
}
</script>

<style scoped>
.admin-settings {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  text-align: left;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: flex;
  align-items: center;
  font-weight: normal;
  cursor: pointer;
}

input[type="checkbox"] {
  margin-right: 10px;
}

.primary-button {
  display: block;
  width: 100%;
  margin-top: 20px;
  padding: 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.primary-button:hover {
  background-color: #45a049;
}
</style>
