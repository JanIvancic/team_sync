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
    
    # Convert DataFrame to list of dictionaries
    users_list = users.to_dict('records')
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
    
    # Sort users by their average similarity to others
    user_avg_similarities = np.mean(similarity_matrix, axis=1)
    sorted_indices = np.argsort(user_avg_similarities)
    
    if team_approach == 'homogeni':
        # For homogeneous teams, we want similar users together
        sorted_indices = sorted_indices[::-1]  # Reverse to get most similar first
    else:
        # For heterogeneous teams, we want diverse users together
        pass  # Keep the original order
    
    # Create teams
    for team_idx in range(num_teams):
        team = []
        print(f"Started team {team_idx + 1}")
        
        # Find the first unused user
        for i in range(len(sorted_indices)):
            if sorted_indices[i] not in used_indices:
                team.append(users_list[sorted_indices[i]])
                used_indices.add(sorted_indices[i])
                print(f"Added user index {sorted_indices[i]} to team {team_idx + 1}")
                break
        
        # Add more users to the team based on approach
        while len(team) < team_size and len(used_indices) < len(users_list):
            best_score = float('-inf') if team_approach == 'homogeni' else float('inf')
            best_idx = -1
            
            for i in range(len(users_list)):
                if i not in used_indices:
                    # Calculate average similarity to current team
                    avg_similarity = np.mean([similarity_matrix[i][j] for j in used_indices])
                    
                    if team_approach == 'homogeni':
                        if avg_similarity > best_score:
                            best_score = avg_similarity
                            best_idx = i
                    else:
                        if avg_similarity < best_score:
                            best_score = avg_similarity
                            best_idx = i
            
            if best_idx != -1:
                team.append(users_list[best_idx])
                used_indices.add(best_idx)
                print(f"Added user index {best_idx} to team {team_idx + 1}")
        
        # Calculate team metrics
        metrics = calculate_team_metrics(team, characteristics)
        teams.append({
            'members': team,
            'metrics': metrics
        })
        print(f"Processing team {team_idx + 1}:")
        for member in team:
            print(f"Adding user: {member}")
    
    print(f"Final teams: {teams}")
    return teams




