# backend/team_logic.py

import numpy as np
import pandas as pd
from itertools import combinations

def calculate_similarity(user1, user2, characteristics):
    """Calculate similarity between two users based on selected characteristics"""
    # Convert to numpy arrays for vectorized operations
    scores1 = np.array([user1[char] for char in characteristics])
    scores2 = np.array([user2[char] for char in characteristics])
    
    # Calculate Euclidean distance
    distance = np.linalg.norm(scores1 - scores2)
    # Convert distance to similarity (1 = identical, 0 = completely different)
    similarity = 1 / (1 + distance)
    
    # For homogeneous teams, we want high similarity (close to 1)
    # For heterogeneous teams, we want low similarity (close to 0)
    return similarity

def calculate_thi(team, similarity_matrix, user_indices):
    """Calculate Team Heterogeneity Index for a team"""
    if len(team) < 2:
        return 0
    
    # Get all pairs of team members
    pairs = list(combinations(team, 2))
    total_similarity = 0
    
    for pair in pairs:
        # Get indices in the similarity matrix
        idx1 = user_indices[pair[0]]
        idx2 = user_indices[pair[1]]
        total_similarity += similarity_matrix[idx1][idx2]
    
    # Average similarity
    avg_similarity = total_similarity / len(pairs)
    # THI is 1 - average similarity (higher THI = more heterogeneous)
    return 1 - avg_similarity

def calculate_team_metrics(team, characteristics):
    """Calculate metrics for a team based on the selected characteristics"""
    metrics = {
        'avg_similarity': 0,
        'thi': 0  # Team Heterogeneity Index
    }
    
    if len(team) < 2:
        return metrics
    
    # Calculate average similarity
    total_similarity = 0
    pairs = 0
    
    for i in range(len(team)):
        for j in range(i+1, len(team)):
            similarity = calculate_similarity(team[i], team[j], characteristics)
            total_similarity += similarity
            pairs += 1
    
    if pairs > 0:
        metrics['avg_similarity'] = total_similarity / pairs
        metrics['thi'] = 1 - metrics['avg_similarity']  # THI is 1 - average similarity
    
    return metrics

def make_teams(users, team_size, team_approach, characteristics, similarity_threshold):
    print(f"Starting team generation with {len(users)} users")
    print(f"Team size: {team_size}, Approach: {team_approach}")
    print(f"Characteristics: {characteristics}")
    print(f"User data: {users}")
    
    # Convert DataFrame to list of dictionaries if it's not already
    if isinstance(users, pd.DataFrame):
        users_list = users.reset_index().to_dict('records')
    else:
        users_list = users
    print(f"Converted user data: {users_list}")
    
    # Calculate similarity matrix
    similarity_matrix = np.zeros((len(users_list), len(users_list)))
    for i in range(len(users_list)):
        for j in range(i+1, len(users_list)):
            similarity = calculate_similarity(users_list[i], users_list[j], characteristics)
            similarity_matrix[i][j] = similarity
            similarity_matrix[j][i] = similarity
    
    print("Similarity matrix:")
    print(similarity_matrix)
    
    # Calculate number of teams needed
    num_teams = len(users_list) // team_size
    if len(users_list) % team_size != 0:
        num_teams += 1
    
    print(f"Creating {num_teams} teams")
    
    teams = []
    used_indices = set()
    
    if team_approach == 'homogeni':
        # For homogeneous teams, sort users by their average skill level
        user_avg_skills = []
        for i, user in enumerate(users_list):
            avg_skill = np.mean([float(user.get(char, 0)) for char in characteristics])
            user_avg_skills.append((i, avg_skill))
        
        # Sort by average skill level
        user_avg_skills.sort(key=lambda x: x[1])
        sorted_indices = [x[0] for x in user_avg_skills]
        
        # Create teams with similar skill levels
        current_team = []
        for i in sorted_indices:
            if i not in used_indices:
                user = users_list[i]
                current_team.append(user.get('id', str(i)))
                used_indices.add(i)
                
                if len(current_team) == team_size:
                    teams.append(current_team)
                    current_team = []
        
        # Add any remaining users to the last team
        if current_team:
            teams.append(current_team)
    
    else:  # heterogeneous
        # For heterogeneous teams, sort users by their average skill level
        user_avg_skills = []
        for i, user in enumerate(users_list):
            avg_skill = np.mean([float(user.get(char, 0)) for char in characteristics])
            user_avg_skills.append((i, avg_skill))
        
        # Sort by average skill level
        user_avg_skills.sort(key=lambda x: x[1])
        sorted_indices = [x[0] for x in user_avg_skills]
        
        # Create teams with diverse skill levels
        current_team = []
        while len(used_indices) < len(users_list):
            if not current_team:
                # Start with highest skill user
                for i in reversed(sorted_indices):
                    if i not in used_indices:
                        user = users_list[i]
                        current_team.append(user.get('id', str(i)))
                        used_indices.add(i)
                        break
            else:
                # Find most different user
                current_avg = np.mean([
                    np.mean([float(users_list[sorted_indices.index(j)].get(char, 0)) for char in characteristics])
                    for j in [sorted_indices.index(int(uid)) for uid in current_team]
                ])
                
                best_idx = -1
                max_diff = -1
                for i in sorted_indices:
                    if i not in used_indices:
                        user_avg = np.mean([float(users_list[i].get(char, 0)) for char in characteristics])
                        diff = abs(user_avg - current_avg)
                        if diff > max_diff:
                            max_diff = diff
                            best_idx = i
                
                if best_idx != -1:
                    user = users_list[best_idx]
                    current_team.append(user.get('id', str(best_idx)))
                    used_indices.add(best_idx)
            
            if len(current_team) == team_size:
                teams.append(current_team)
                current_team = []
        
        # Add any remaining users to the last team
        if current_team:
            teams.append(current_team)
    
    print(f"Final teams: {teams}")
    return teams




