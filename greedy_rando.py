import argparse
from pathlib import Path
from typing import List, Optional
import pandas as pd
import streamlit

# read in the two csv files
# generate dicts
# loop over n iterations:
    # for each iteration, randomly shuffle the list of users
    # loop over users:
        # for each user, loop over sessions in order of preference
            # if session has space, assign user to session and break
    # calculate score for iteration
    # if score is best score, save assignments
# write out best assignments to csv

def main(argv: Optional[List[str]] = None) -> int:
    n_iter = 10
    n_prefs = 5
    
    session_cap_dict_raw = {}
    assignments_best = {}
    score_best = -1

    parser = argparse.ArgumentParser(
        description="Try to generate an optimal set of employee-session assignments."
    )
    parser.add_argument("user_pref_csv", type=Path, help="Path to user preferences csv")
    parser.add_argument("session_cap_csv", type=Path, help="Path to session capacities csv")
    args = parser.parse_args(argv)

    user_pref_df = pd.read_csv(args.user_pref_csv)
    session_cap_df = pd.read_csv(args.session_cap_csv)
    print("Successfully loaded in csv's.")

    for _, row in session_cap_df.iterrows():
        if row['session_id'] not in session_cap_dict_raw:
            session_cap_dict_raw[row['session_id']] = {}
        session_cap_dict_raw[row['session_id']][row['slot']] = row['capacity']
    print("Successfully built session cap dictionary.")

    print("Iterating through random assignments...")
    for i in range(n_iter):
        print(f"Running iteration {i}")

        # shuffle the rows of user_pref_df:
        shuffled_df = user_pref_df.sample(frac=1).reset_index(drop=True)
        # print(shuffled_df)

        # copy the session capacity dict for this iteration
        session_cap_dict_iter = {k: v.copy() for k, v in session_cap_dict_raw.items()}
        
        # blank assignments dict for this iteration
        assignments_iter = {}

        score = 0

        for _, row in shuffled_df.iterrows():
            user_id = row['user_id']
            user_slot = row['slot']
            
            preferences = { j: row[f'preference_{j}'] for j in range(1, n_prefs + 1) if pd.notna(row[f'preference_{j}'])}
            # print(preferences)

            if user_id not in assignments_iter:
                assignments_iter[user_id] = {}
            if user_slot in assignments_iter[user_id]:
                raise ValueError("Duplicate slot for user in preferences.")
            assignments_iter[user_id][user_slot] = None
            # continue

            for pref, session_id in preferences.items():
                
                if session_id not in session_cap_dict_iter:
                    raise ValueError(f"Session ID {session_id} in preferences for user {user_id} not found in session capacities csv.")
                if user_slot not in session_cap_dict_iter[session_id]:
                    raise ValueError(f"Slot {user_slot} for session ID {session_id} in preferences for user {user_id} not found in session capacities csv.")
                
                ## make sure user hasn't been assigned to this session already in another slot
                # print(f"\nChecking assignments for user {user_id} and user_slot {user_slot} and session_id {session_id}")
                already_assigned = False
                for other_slot, assigned_session in assignments_iter[user_id].items():
                    # print(f"User {user_id} assigned to session {assigned_session} in slot {other_slot}")
                    if assigned_session == session_id:
                        already_assigned = True
                
                if not already_assigned:
                    capacity = session_cap_dict_iter[session_id][user_slot]
                    if capacity > 0:
                        assignments_iter[user_id][user_slot] = session_id
                        session_cap_dict_iter[session_id][user_slot] -= 1
                        score_diff = n_prefs - pref + 1
                        score += score_diff
                        # print(f"Assigned user {user_id} to session {session_id} for slot {user_slot} with preference {pref}. Incrementing score by {score_diff}\n")
                        break

            if assignments_iter[user_id][user_slot] is None:
                raise ValueError(f"Could not assign user {user_id} to any session for slot {user_slot}!.\n")
                
        # print(assignments_iter)

        if score > score_best:
            score_best = score
            assignments_best = assignments_iter
            # print("New best score: ", score_best)

    print(assignments_best)
    print("Best score after all iterations: ", score_best)

    # write out assignments_best to csv
    output_rows = []
    for user_id, slots in assignments_best.items():
        for slot, session_id in slots.items():
            output_rows.append({'user_id': user_id, 'slot': slot, 'assigned_session': session_id})
    output_df = pd.DataFrame(output_rows)
    output_df.to_csv("best_assignments.csv", index=False)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
