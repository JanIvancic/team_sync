<template>
  <div id="app">
    <!-- Initial session creation/joining -->
    <div v-if="!sessionId">
      <Session @session-created="onSessionCreated" />
    </div>

    <!-- ADMIN FLOW -->
    <div v-else-if="isAdmin && !settingsConfirmed">
      <h2>Admin Settings</h2>
      <AdminSettings @settings-saved="onSettingsSaved" />
    </div>

    <!-- ADMIN AFTER SETTINGS -->
    <div v-else-if="isAdmin && settingsConfirmed">
      <div class="session-info">
        <h3>Session Code: <span class="session-code">{{ sessionId }}</span></h3>
        <p>Share this code with participants to join this session</p>
        <div class="settings-summary">
          <p><strong>Anonymous Mode:</strong> {{ sessionSettings.anonymousMode ? 'Enabled' : 'Disabled' }}</p>
          <p><strong>Show Teams to Users:</strong> {{ sessionSettings.showTeamsToUsers ? 'Enabled' : 'Disabled' }}</p>
        </div>
      </div>

      <div style="margin-top:20px">
        <p>Responses: {{ surveys.length }}</p>
        <div class="team-settings">
          <h3>Team Generation Settings</h3>
          <div class="setting-group">
            <label>Team Size:</label>
            <input type="number" v-model="sessionSettings.teamSize" min="2" max="10">
          </div>
          <div class="setting-group">
            <label>Team Approach:</label>
            <select v-model="sessionSettings.teamApproach">
              <option value="homogeni">Homogeneous</option>
              <option value="heterogeni">Heterogeneous</option>
            </select>
          </div>
          <div class="setting-group">
            <label>Characteristics:</label>
            <select v-model="sessionSettings.characteristics" multiple>
              <option value="tech_skills">Technical Skills</option>
              <option value="comm_skills">Communication Skills</option>
              <option value="creative_skills">Creative Skills</option>
              <option value="leadership_skills">Leadership Skills</option>
            </select>
          </div>
          <div class="setting-group">
            <label>Similarity Threshold (%):</label>
            <input type="number" v-model="sessionSettings.similarityThreshold" min="0" max="100">
          </div>
        </div>
        <button @click="generateTeams" :disabled="surveys.length < 2">
          Generate Teams
        </button>
      </div>

      <div v-if="teams.length" class="teams-container">
        <h2>Generated Teams</h2>
        <div class="teams-list">
          <div v-for="(team, index) in teams" :key="index" class="team-card">
            <h3>Team {{ index + 1 }}</h3>
            <ul>
              <li v-for="(member, memberIndex) in team.members" :key="memberIndex">
                {{ member.name }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <TeamGraph 
        v-if="teams.length" 
        :teams="teams" 
        :anonymousMode="sessionSettings.anonymousMode" 
      />
    </div>

    <!-- PARTICIPANT FLOW -->
    <div v-else>
      <div class="session-info">
        <h3>Joined Session: <span class="session-code">{{ sessionId }}</span></h3>
      </div>

      <SurveyForm
        :sessionId="sessionId"
        :isAdmin="isAdmin"
        :anonymousMode="sessionSettings.anonymousMode"
        @surveys-updated="onSurveysUpdated"
      />

      <div v-if="teams.length && sessionSettings.showTeamsToUsers" class="teams-container">
        <h2>Generated Teams</h2>
        <div class="teams-list">
          <div 
            v-for="(team, index) in teams" 
            :key="index" 
            class="team-card"
          >
            <h3>Team {{ index + 1 }}</h3>
            <ul>
              <li 
                v-for="(member, idx) in team.members" 
                :key="member.id"
                :class="{ 
                  'current-user': isCurrentUser(member),
                  'anonymous-user': sessionSettings.anonymousMode
                }"
              >
                <template v-if="sessionSettings.anonymousMode">
                  Member {{ idx + 1 }}
                  <span v-if="isCurrentUser(member)" class="you-badge">(You)</span>
                </template>
                <template v-else>
                  {{ member.name }}
                  <span v-if="isCurrentUser(member)" class="you-badge">(You)</span>
                </template>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <TeamGraph 
        v-if="teams.length" 
        :teams="teams" 
        :anonymousMode="sessionSettings.anonymousMode" 
      />
    </div>
  </div>
</template>

<script>
import Session from './components/Session.vue'
import SurveyForm from './components/SurveyForm.vue'
import TeamGraph from './components/TeamGraph.vue'
import AdminSettings from './components/AdminSettings.vue'
import axios from 'axios'

// Configure axios to use the correct base URL
axios.defaults.baseURL = process.env.NODE_ENV === 'production' 
  ? 'https://team-sync-app-8aa47d5c9ba6.herokuapp.com'  // Production URL
  : 'http://localhost:5000';  // Development URL

export default {
  name: 'App',
  components: { Session, SurveyForm, TeamGraph, AdminSettings },
  data() {
    return {
      sessionId: null,
      isAdmin: false,
      settingsConfirmed: false,
      currentUser: null,
      sessionSettings: {
        anonymousMode: false,
        showTeamsToUsers: true,
        teamSize: 4,
        teamApproach: "homogeni",
        characteristics: ["tech_skills", "comm_skills", "creative_skills", "leadership_skills"],
        similarityThreshold: 50
      },
      surveys: [],
      teams: [],
      minResponses: 1,
      pollInterval: null
    }
  },
  computed: {
    myTeam() {
      if (!this.teams || !this.teams.length) {
        console.log('No teams available');
        return null;
      }

      const currentUserId = sessionStorage.getItem('currentUserId');
      console.log('Looking for team with current user:', currentUserId);

      // First check if we have a valid user ID
      if (!currentUserId) {
        console.log('No current user ID found in sessionStorage');
        return null;
      }

      const team = this.teams.find(team => {
        if (!team.members) {
          console.log('Team has no members:', team);
          return false;
        }

        const hasCurrentUser = team.members.some(member => {
          if (!member || !member.id) {
            console.log('Invalid member:', member);
            return false;
          }
          const matches = member.id === currentUserId;
          console.log('Checking member:', member.id, 'against current:', currentUserId, 'matches:', matches);
          return matches;
        });

        console.log('Team check result:', {
          teamMembers: team.members.map(m => m.id),
          hasCurrentUser
        });
        return hasCurrentUser;
      });

      console.log('Found team:', team);
      return team;
    }
  },
  created() {
    // Generate a unique ID for this browser tab
    this.browserTabId = 'tab_' + Math.random().toString(36).substr(2, 9);
    console.log('Browser tab ID:', this.browserTabId);
  },
  methods: {
    onSessionCreated(data) {
      this.sessionId = data.id;
      this.isAdmin = data.isAdmin;
      this.settingsConfirmed = data.settingsConfirmed;
      this.sessionSettings = data.settings || this.sessionSettings;
      
      // Store current user ID
      if (data.currentUser) {
        sessionStorage.setItem('currentUserId', data.currentUser);
        this.currentUser = data.currentUser;
      }
      
      // Start polling for surveys and teams if not admin
      if (!this.isAdmin) {
        this.startPolling();
      }
    },

    onSettingsSaved(settings) {
      console.log('Settings saved:', settings);
      
      // Update settings
      this.sessionSettings = { ...settings };
      
      // Confirm settings
      this.settingsConfirmed = true;
      
      console.log('Settings confirmed:', {
        settingsConfirmed: this.settingsConfirmed,
        settings: this.sessionSettings
      });

      // Save settings to backend
      this.saveSessionSettings();
      
      // Start polling for surveys
      this.startPolling();
    },

    async saveSessionSettings() {
      try {
        console.log('Saving settings to backend:', this.sessionSettings);
        const settingsToSave = {
          anonymous_mode: this.sessionSettings.anonymousMode,
          show_teams_to_users: this.sessionSettings.showTeamsToUsers,
          team_size: this.sessionSettings.teamSize,
          team_approach: this.sessionSettings.teamApproach,
          characteristics: this.sessionSettings.characteristics,
          similarity_threshold: this.sessionSettings.similarityThreshold
        };
        console.log('Formatted settings for backend:', settingsToSave);
        await axios.post(`/api/session/${this.sessionId}/settings`, settingsToSave);
      } catch (error) {
        console.error('Error saving settings:', error);
      }
    },

    startPolling() {
      // Clear any existing polling
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
      }
      
      // Start polling every 3 seconds
      this.pollInterval = setInterval(() => {
        this.pollSurveys();
        this.pollTeams();
      }, 3000);
    },

    pollSurveys() {
      axios.get(`/api/session/${this.sessionId}/surveys`)
        .then(response => {
          this.surveys = response.data;
        })
        .catch(error => {
          console.error('Error polling surveys:', error);
        });
    },
    
    pollTeams() {
      axios.get(`/api/session/${this.sessionId}/teams`)
        .then(response => {
          if (response.data && response.data.teams) {
            this.teams = response.data.teams;
          }
        })
        .catch(error => {
          console.error('Error polling teams:', error);
        });
    },

    onSurveysUpdated(data) {
      console.log('Survey updated with data:', data);
      
      if (this.isAdmin) {
        this.surveys = data;
      } else {
        // Store the current user ID from the backend response
        if (data.user_id) {
          console.log('Setting current user ID from response:', data.user_id);
          sessionStorage.setItem('currentUserId', data.user_id);
          this.currentUser = data.user_id;
        } else if (data.survey && data.survey.user_id) {
          // If user_id is not in the root, try to get it from the survey
          console.log('Setting current user ID from survey:', data.survey.user_id);
          sessionStorage.setItem('currentUserId', data.survey.user_id);
          this.currentUser = data.survey.user_id;
        } else {
          console.warn('No user ID found in survey response:', data);
        }
        
        // Add the new survey to the list
        if (data.survey) {
          this.surveys.push(data.survey);
        }
      }
      
      // Generate teams if we have enough surveys
      if (this.surveys.length >= this.sessionSettings.teamSize) {
        this.generateTeams();
      }
    },

    async generateTeams() {
      try {
        console.log('Generating teams with settings:', this.sessionSettings);
        // Convert characteristics Proxy to plain array
        const characteristics = Array.isArray(this.sessionSettings.characteristics) 
          ? [...this.sessionSettings.characteristics]  // Create a new plain array
          : ["tech_skills", "comm_skills", "creative_skills", "leadership_skills"];
        
        const settings = {
          team_size: parseInt(this.sessionSettings.teamSize),
          team_approach: this.sessionSettings.teamApproach,
          characteristics: characteristics,
          similarity_threshold: parseInt(this.sessionSettings.similarityThreshold),
          anonymous_mode: this.sessionSettings.anonymousMode,
          show_teams_to_users: this.sessionSettings.showTeamsToUsers
        };
        console.log('Sending settings to backend:', settings);
        const res = await axios.post(`/api/session/${this.sessionId}/teams`, {
          settings: settings
        });
        
        if (res.data && res.data.teams) {
          // Transform the teams data to ensure it has the correct structure
          this.teams = res.data.teams.map(team => {
            // If team is already an array of members, wrap it in a members property
            if (Array.isArray(team)) {
              return {
                members: team.map((member, index) => ({
                  id: member.id || `member-${index}`,
                  name: this.sessionSettings.anonymousMode ? `Member ${index + 1}` : (member.name || `Member ${index + 1}`)
                }))
              };
            }
            // If team is an object with members array, ensure each member has required properties
            if (team.members) {
              return {
                members: team.members.map((member, index) => ({
                  id: member.id || `member-${index}`,
                  name: this.sessionSettings.anonymousMode ? `Member ${index + 1}` : (member.name || `Member ${index + 1}`)
                }))
              };
            }
            return team;
          });
          console.log('Teams generated:', this.teams);
        } else {
          console.error('Invalid team data:', res.data);
        }
      } catch (error) {
        console.error('Error generating teams:', error);
        alert('Failed to generate teams. Please try again.');
      }
    },

    formatMemberName(member) {
      if (this.sessionSettings.anonymousMode) {
        return `Member ${member.memberIndex + 1}`;
      }
      // Check if member is a string (old format) or an object (new format)
      if (typeof member === 'string') {
        return member;
      }
      // For new format, member is an object with name property
      return member.name || 'Anonymous';
    },

    isCurrentUser(member) {
      const currentUserId = sessionStorage.getItem('currentUserId');
      if (!currentUserId || !member) return false;
      
      if (this.sessionSettings.anonymousMode) {
        return member.id === currentUserId;
      } else {
        return member.name === currentUserId;
      }
    }
  },
  beforeDestroy() {
    // Clear polling interval when component is destroyed
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
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

.session-info {
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.session-code {
  font-size: 24px;
  font-weight: bold;
  color: #4CAF50;
  background-color: #e8f5e9;
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px dashed #4CAF50;
}

.settings-summary {
  margin-top: 15px;
  padding: 10px;
  background-color: #f1f8e9;
  border-radius: 4px;
  text-align: left;
}

.settings-summary p {
  margin: 5px 0;
}

.teams-container {
  margin: 20px 0;
}

.teams-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.team-card {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  min-width: 200px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.team-card h3 {
  margin-top: 0;
  color: #4CAF50;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 10px;
}

.team-card ul {
  list-style-type: none;
  padding: 0;
  text-align: left;
}

.team-card li {
  padding: 5px 0;
  border-bottom: 1px dashed #e9ecef;
}

.team-settings {
  margin-top: 20px;
  padding: 15px;
  background-color: #f1f8e9;
  border-radius: 4px;
  text-align: left;
}

.setting-group {
  margin-bottom: 10px;
}

.setting-group label {
  display: block;
  margin-bottom: 5px;
}

.current-user {
  font-weight: bold;
  color: #4CAF50;
  background-color: #e8f5e9;
  padding: 5px 10px;
  border-radius: 4px;
  margin: 2px 0;
}

.you-badge {
  font-size: 0.8em;
  color: #666;
  margin-left: 5px;
}

.anonymous-user {
  font-family: monospace;
  color: #666;
}

.teams-container {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.teams-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 15px;
}

.team-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  min-width: 200px;
}

.team-card h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.team-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.team-card li {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.team-card li:last-child {
  border-bottom: none;
}
</style>
