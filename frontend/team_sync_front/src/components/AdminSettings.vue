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
      
      <div class="form-group">
        <label>Team Size:</label>
        <input type="number" v-model="settings.teamSize" min="2" max="10" required />
      </div>
      
      <div class="form-group">
        <label>Team Approach:</label>
        <select v-model="settings.teamApproach" required>
          <option value="homogeni">Homogeneous (similar skills)</option>
          <option value="heterogeni">Heterogeneous (diverse skills)</option>
        </select>
      </div>
      
      <div class="form-group">
        <label>Characteristics to Consider:</label>
        <div class="checkbox-group">
          <label v-for="char in characteristics" :key="char.value">
            <input type="checkbox" v-model="settings.characteristics" :value="char.value" />
            {{ char.label }}
          </label>
        </div>
      </div>
      
      <div class="form-group">
        <label>Similarity Threshold (%):</label>
        <input type="number" v-model="settings.similarityThreshold" min="0" max="100" required />
      </div>
      
      <button type="submit" class="primary-button" :disabled="!isValid">Save Settings & Get Session Code</button>
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
        showTeamsToUsers: true,
        teamSize: 4,
        teamApproach: "homogeni",
        characteristics: ["tech_skills", "comm_skills", "creative_skills", "leadership_skills"],
        similarityThreshold: 50
      },
      characteristics: [
        { label: "Technical Skills", value: "tech_skills" },
        { label: "Communication Skills", value: "comm_skills" },
        { label: "Creative Skills", value: "creative_skills" },
        { label: "Leadership Skills", value: "leadership_skills" }
      ]
    }
  },
  computed: {
    isValid() {
      return (
        this.settings.teamSize >= 2 &&
        this.settings.teamSize <= 10 &&
        this.settings.teamApproach &&
        this.settings.characteristics.length > 0 &&
        this.settings.similarityThreshold >= 0 &&
        this.settings.similarityThreshold <= 100
      );
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
      if (!this.isValid) {
        alert('Please fill in all required fields with valid values');
        return;
      }
      
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

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

input[type="number"],
select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 5px;
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

.primary-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
