import pandas as pd
import sys
import os
import math
from math import ceil,exp

def create_template_file(index, home, away, season, template_file):
    #first create the home pcsp file from the template file
    out_file = f"pcspDir\\{season}\\{'0' if index < 100 else ''}{'0' if index < 10 else ''}{index} {home}{away}{season}.pcsp"
    open(out_file,'w').close() #creates the file
    with open(template_file, 'r') as fp_in, open(out_file, 'w') as fp_out: #copy template file to out file
        for line in fp_in:
            fp_out.write(line)
    with open(out_file, 'r') as file:
        # Read the contents of the file into a list of lines
        lines = file.readlines()

    return out_file, lines

def create_template_files(df_match, df_ratings,season, template_file_3f,template_file_4f_3rows,template_file_4f,template_file_5f,template_file_5f_3rows,template_file_5f_4rows,  match_url_arr):
    index = 0
    for ind,row in df_match.iterrows():
        #define row values for current row
        match_url = row['match_url'] #read from column 'match url'
        match_url_arr.append(match_url)
        home = row['home_team']
        away = row['away_team']
        # Print out match index and teams for debugging
        print( f"Doing match {index + 1}: {home} vs {away}, match_url: {match_url}")
        home_fmn = row['home_formation']
        away_fmn = row['away_formation']
        # home_team = row['home_xi_names']
        home_team = row['home_xi_sofifa_ids']
        # away_team = row['away_xi_names']
        away_team = row['away_xi_sofifa_ids']
        home_seq = row['home_sequence']
        away_seq = row['away_sequence']
        #define whether it is 3 levels i.e 4-3-3/4-5-1... ,or 4 levels i.e 4-2-3-1/4-4-1-1...
        is3levels_home = False
        is4levels_home = False
        is5levels_home = False
        is3levels_away = False
        is4levels_away = False
        is5levels_away = False
        #instantiate
        def_H,mid_H = 0,0 #for 3 levels, Home
        def_4H, midDef_4H, mid_4H = 0,0,0 #for 4 levels Home, in this case def_4H replaces mid_H
        def_5H, midDef_5H, mid_5H, midFor_5H = 0,0,0,0
        def_A,mid_A = 0,0 #for 3 levels, Home
        def_4A,midDef_4A, mid_4A = 0,0,0 #for 4 levels Away, in this case def_4A replaces mid_A
        def_5A, midDef_5A, mid_5A, midFor_5A = 0,0,0,0 
        #address formatting issue for formations
        if len(home_fmn) == 5 or '-0' in home_fmn: #means 3 levels
            is3levels_home = True
            posArray = home_fmn.split('-')
            def_H,mid_H, for_H = int(posArray[0]),int(posArray[1]), int(posArray[2]) - 2000 
        else: #means 4 levels
            if len(home_fmn) == 7:
                is4levels_home = True
                posArray = home_fmn.split('-')
                def_4H,midDef_4H, mid_4H, for_4H = int(posArray[0]),int(posArray[1]),int(posArray[2]), int(posArray[3])
            else:
               is5levels_home = True
               posArray = home_fmn.split('-')
               def_5H,midDef_5H, mid_5H, midFor_5H, for_5H = int(posArray[0]),int(posArray[1]),int(posArray[2]), int(posArray[3]), int(posArray[4]) 

        if len(away_fmn) == 5 or '-0' in away_fmn: #means 3 levels
        # if "/" in away_fmn: #means 3 levels
            is3levels_away = True
            posArray = away_fmn.split('-')
            def_A,mid_A,for_A = int(posArray[0]),int(posArray[1]),int(posArray[2]) - 2000 
        else: #means 4 levels
            if len(away_fmn) == 7:
                is4levels_away = True
                posArray = away_fmn.split('-')
                def_4A,midDef_4A, mid_4A,for_4A = int(posArray[0]),int(posArray[1]),int(posArray[2]), int(posArray[3])
            else:
               is5levels_away = True
               posArray = away_fmn.split('-')
               def_5A,midDef_5A, mid_5A, midFor_5A, for_5A = int(posArray[0]),int(posArray[1]),int(posArray[2]), int(posArray[3]), int(posArray[4]) 
        
        if (is3levels_home and is3levels_away):
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperIdHome = home_team[0]
            defenderPositionsHome = homePositions[1:1 + def_H]
            defenderIdsHome = home_team[1:1 + def_H]
            midfielderPositionsHome = homePositions[1 + def_H:1 + def_H +mid_H]
            midfielderIdsHome = home_team[1 + def_H:1 + def_H +mid_H]
            forwardPositionsHome = homePositions[1 + def_H+mid_H:]
            forwardIdsHome = home_team[1 + def_H+mid_H:]
            
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperIdAway = away_team[0]
            defenderPositionsAway = awayPositions[1:1 + def_A]
            defenderIdsAway = away_team[1:1 + def_A]
            midfielderPositionsAway = awayPositions[1 + def_A:1 + def_A +mid_A]
            midfielderIdsAway = away_team[1 + def_A:1 + def_A +mid_A]
            forwardPositionsAway = awayPositions[1 + def_A+mid_A:]
            forwardIdsAway = away_team[1 + def_A + mid_A:]
            ##generate home pcsp file using 3 levels template
            
            
            out_file, lines = create_template_file(index, home, away, season, template_file_3f)
            index = index + 1
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            #TODO modify Goalkeeper ratings in pcsp file
            #home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home)].values
            gk_home_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdHome)))].values            
            short_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_away_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdAway)))].values
            gk_handling_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 49 - 1
            atk_def_line = 56 - 1
            atk_freekick_def_line = 58 - 1
            atk_mid_line = 66 - 1
            atk_freekick_mid_line = 68 - 1
            atk_for_line = 71 - 1
            atk_freekick_for_line = 73 - 1
            def_kep_line = 78 - 1
            distToKep_line = 91 - 1

            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"

            prob_to_lose_away_forwards, aggression_away_forwards = create_prob_to_lose(forwardIdsAway, df_ratings, away)
            prob_to_lose_away_midfielders, aggression_away_midfielders = create_prob_to_lose(midfielderIdsAway, df_ratings, away)
            prob_to_lose_away_defenders, aggression_away_defenders = create_prob_to_lose(defenderIdsAway, df_ratings, away)


            freekick_def_home = create_free_kick_rating(defenderIdsHome, df_ratings, home, rely_skills='skill_long_passing')
            freekick_mid_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')                          
            freekick_for_home = create_free_kick_rating(forwardIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')

            lines = modify_atkDef(home, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home)
            lines = modify_atkMid(3, home, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsHome, df_ratings, midfielderIdsHome, prob_to_lose_away_midfielders, aggression_away_midfielders, freekick_mid_home)
            lines = modify_atkFor(3, home, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home)
            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         

            out_file, lines = create_template_file(index, away, home, season, template_file_3f)
            index = index + 1
            
            short_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_handling_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"

            
            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)
            

            freekick_def_away = create_free_kick_rating(defenderIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_mid_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_for_away = create_free_kick_rating(forwardIdsAway, df_ratings, away, 'skill_fk_accuracy')


            lines = modify_atkDef(away, lines, atk_def_line, atk_freekick_def_line, defenderPositionsAway, df_ratings, defenderIdsAway, prob_to_lose_home_forwards, aggression_home_forwards, freekick_def_away)
            lines = modify_atkMid(3, away, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away) 
            lines = modify_atkFor(3, away, lines, atk_for_line, atk_freekick_for_line, forwardPositionsAway, df_ratings, forwardIdsAway, prob_to_lose_home_defenders, aggression_home_defenders, freekick_for_away)

            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)

        elif (is4levels_home and is4levels_away):
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperIdHome = home_team[0]
            defenderPositionsHome = homePositions[1:1 + def_4H]
            defenderIdsHome = home_team[1:1 + def_4H]
            midDefPositionsHome = homePositions[1 + def_4H:1 + def_4H +midDef_4H]
            midDefIdsHome = home_team[1 + def_4H:1 + def_4H +midDef_4H]
            midfielderPositionsHome = homePositions[1 + def_4H + midDef_4H:1 + def_4H +midDef_4H + mid_4H]
            midfielderIdsHome = home_team[1 + def_4H + midDef_4H:1 + def_4H +midDef_4H + mid_4H]
            forwardPositionsHome = homePositions[1 + def_4H +midDef_4H + mid_4H:]
            forwardIdsHome = home_team[1 + def_4H +midDef_4H + mid_4H:]
            
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperIdAway = away_team[0]
            defenderPositionsAway = awayPositions[1:1 + def_4A]
            defenderIdsAway = away_team[1:1 + def_4A]
            midDefPositionsAway = awayPositions[1 + def_4A:1 + def_4A +midDef_4A]
            midDefIdsAway = away_team[1 + def_4A:1 + def_4A +midDef_4A]
            midfielderPositionsAway = awayPositions[1 + def_4A +midDef_4A:1 + def_4A +midDef_4A +mid_4A]
            midfielderIdsAway = away_team[1 + def_4A:1 + def_4A +midDef_4A +mid_4A]
            forwardPositionsAway = awayPositions[1 + def_4A +midDef_4A +mid_4A:]
            forwardIdsAway = away_team[1 + def_4A +midDef_4A +mid_4A:]
            
            
            out_file, lines = create_template_file(index, home, away, season, template_file_4f)
            index = index + 1
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            #TODO modify Goalkeeper ratings in pcsp file
            #home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home)].value
            gk_home_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdHome)))].values

            short_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]

            gk_away_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdAway)))].values

            gk_handling_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 50 - 1
            atk_def_line = 56 - 1
            atk_freekick_def_line = 58 - 1
            atk_middef_line = 67 - 1
            atk_freekick_middef_line = 69 - 1
            atk_mid_line = 72 - 1
            atk_freekick_mid_line = 74 - 1
            atk_for_line = 77 - 1
            atk_freekick_for_line = 79 - 1
            def_kep_line = 83 - 1
            distToKep_line = 97 - 1

            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating

            prob_to_lose_away_forwards,  aggression_away_forwards= create_prob_to_lose(forwardIdsAway, df_ratings, away)
            prob_to_lose_away_middeffielders,  aggression_away_middeffielders = create_prob_to_lose(midDefIdsAway, df_ratings, away)
            prob_to_lose_away_midfielders,  aggression_away_midfielders = create_prob_to_lose(midfielderIdsAway, df_ratings, away)
            prob_to_lose_away_defenders, aggression_away_defenders = create_prob_to_lose(defenderIdsAway, df_ratings, away)
            
            freekick_def_home = create_free_kick_rating(defenderIdsHome, df_ratings, home, 'skill_long_passing')
            freekick_middef_home = create_free_kick_rating(midDefIdsHome, df_ratings, home, 'skill_long_passing')     
            freekick_mid_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, 'skill_fk_accuracy')
            freekick_for_home = create_free_kick_rating(forwardIdsHome, df_ratings, home, 'skill_fk_accuracy')

            lines = modify_atkDef(home, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home)
            lines = modify_atkMid(4, home, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsHome, df_ratings, midfielderIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_mid_home)
            lines = modify_atkFor(4, home, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home)
            lines = modify_atkMidDef(home, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_midfielders, aggression_away_midfielders, freekick_middef_home)
            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         
            
            out_file, lines = create_template_file(index, away, home, season, template_file_4f)
            index = index + 1
            
            short_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_handling_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"

            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            prob_to_lose_home_middeffielders,  aggression_home_middeffielders = create_prob_to_lose(midDefIdsHome, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)

            
            freekick_def_away = create_free_kick_rating(defenderIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_middef_away = create_free_kick_rating(midDefIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_mid_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_for_away = create_free_kick_rating(forwardIdsAway, df_ratings, away, 'skill_fk_accuracy')


            lines = modify_atkDef(away, lines, atk_def_line, atk_freekick_def_line, defenderPositionsAway, df_ratings, defenderIdsAway, prob_to_lose_home_forwards, aggression_home_forwards, freekick_def_away)
            lines = modify_atkMid(4, away, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_middeffielders, aggression_home_middeffielders, freekick_mid_away)
            lines = modify_atkFor(4, away, lines, atk_for_line, atk_freekick_for_line, forwardPositionsAway, df_ratings, forwardIdsAway, prob_to_lose_home_defenders, aggression_home_defenders, freekick_for_away)
            lines = modify_atkMidDef(away, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsAway, df_ratings, midDefIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_middef_away)

            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)

        elif (is5levels_home and is5levels_away):
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperIdHome = home_team[0]
            defenderPositionsHome = homePositions[1:1 + def_5H]
            defenderIdsHome = home_team[1:1 + def_5H]
            midDefPositionsHome = homePositions[1 + def_5H:1 + def_5H +midDef_5H]
            midDefIdsHome = home_team[1 + def_5H:1 + def_5H +midDef_5H]
            midfielderPositionsHome = homePositions[1 + def_5H + midDef_5H:1 + def_5H +midDef_5H + mid_5H]
            midfielderIdsHome = home_team[1 + def_5H + midDef_5H:1 + def_5H +midDef_5H + mid_5H]
            midForPositionsHome = homePositions[1 + def_5H + midDef_5H + mid_5H:1 + def_5H +midDef_5H + mid_5H + midFor_5H]
            midForIdsHome = home_team[1 + def_5H + midDef_5H + mid_5H:1 + def_5H +midDef_5H + mid_5H + midFor_5H]
            forwardPositionsHome = homePositions[1 + def_5H +midDef_5H + mid_5H + midFor_5H:]
            forwardIdsHome = home_team[1 + def_5H +midDef_5H + mid_5H + midFor_5H:]
            
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperIdAway = away_team[0]
            defenderPositionsAway = awayPositions[1:1 + def_5A]
            defenderIdsAway = away_team[1:1 + def_5A]
            midDefPositionsAway = awayPositions[1 + def_5A:1 + def_5A +midDef_5A]
            midDefIdsAway = away_team[1 + def_5A:1 + def_5A +midDef_5A]
            midfielderPositionsAway = awayPositions[1 + def_5A +midDef_5A:1 + def_5A +midDef_5A +mid_5A]
            midfielderIdsAway = away_team[1 + def_5A +midDef_5A:1 + def_5A +midDef_5A +mid_5A]
            midForPositionsAway = awayPositions[1 + def_5A +midDef_5A +mid_5A:1 + def_5A +midDef_5A +mid_5A + midFor_5A]
            midForIdsAway = away_team[1 + def_5A+midDef_5A +mid_5A:1 + def_5A +midDef_5A +mid_5A + midFor_5A]
            forwardPositionsAway = awayPositions[1 + def_5A +midDef_5A +mid_5A + midFor_5A:]
            forwardIdsAway = away_team[1 + def_5A +midDef_5A +mid_5A + midFor_5A:]
            
            
            out_file, lines = create_template_file(index, home, away, season, template_file_5f)
            index = index + 1
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            gk_home_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdHome)))].values

            short_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]

            gk_away_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdAway)))].values

            gk_handling_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 51 - 1
            atk_def_line = 57 - 1
            atk_freekick_def_line = 59 - 1
            atk_middef_line = 68 - 1
            atk_freekick_middef_line = 70 - 1
            atk_mid_line = 73 - 1
            atk_freekick_mid_line = 75 - 1
            atk_midFor_line = 78- 1
            atk_freekick_midFor_line = 80 - 1 
            atk_for_line = 83 - 1
            atk_freekick_for_line = 85 - 1
            def_kep_line = 90 - 1
            distToKep_line = 105 - 1

            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating

            prob_to_lose_away_forwards,  aggression_away_forwards= create_prob_to_lose(forwardIdsAway, df_ratings, away)
            prob_to_lose_away_middeffielders,  aggression_away_middeffielders = create_prob_to_lose(midDefIdsAway, df_ratings, away)
            prob_to_lose_away_midfielders,  aggression_away_midfielders = create_prob_to_lose(midfielderIdsAway, df_ratings, away)
            prob_to_lose_away_midforfielders,  aggression_away_midforfielders = create_prob_to_lose(midForIdsAway, df_ratings, away)
            prob_to_lose_away_defenders, aggression_away_defenders = create_prob_to_lose(defenderIdsAway, df_ratings, away)
            
            freekick_def_home = create_free_kick_rating(defenderIdsHome, df_ratings, home, 'skill_long_passing')
            freekick_middef_home = create_free_kick_rating(midDefIdsHome, df_ratings, home, 'skill_long_passing')     
            freekick_mid_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, 'skill_fk_accuracy')
            freekick_midfor_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, 'skill_fk_accuracy')
            freekick_for_home = create_free_kick_rating(forwardIdsHome, df_ratings, home, 'skill_fk_accuracy')

            lines = modify_atkDef(home, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home)
            lines = modify_atkMid(5, home, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsHome, df_ratings, midfielderIdsHome, prob_to_lose_away_midfielders, aggression_away_midfielders, freekick_mid_home)
            lines = modify_atkFor(5, home, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home)
            lines = modify_atkMidDef(home, lines, atk_middef_line, atk_freekick_middef_line, midForPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_midforfielders, aggression_away_midforfielders, freekick_middef_home)
            lines = modify_atkMidFor(home, lines, atk_midFor_line, atk_freekick_midFor_line, midForPositionsHome, df_ratings, midForIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_midfor_home)
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         
            
            out_file, lines = create_template_file(index, away, home, season, template_file_5f)
            index = index + 1
            
            short_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_handling_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"

            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            prob_to_lose_home_middeffielders,  aggression_home_middeffielders = create_prob_to_lose(midDefIdsHome, df_ratings, home)
            prob_to_lose_home_midforfielders,  aggression_home_midforfielders = create_prob_to_lose(midForIdsHome, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)

            freekick_def_away = create_free_kick_rating(defenderIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_middef_away = create_free_kick_rating(midDefIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_mid_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_for_away = create_free_kick_rating(forwardIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_midfor_away = create_free_kick_rating(midForIdsAway, df_ratings, away, 'skill_fk_accuracy')

            lines = modify_atkDef(away, lines, atk_def_line, atk_freekick_def_line, defenderPositionsAway, df_ratings, defenderIdsAway, prob_to_lose_home_forwards, aggression_home_forwards, freekick_def_away)
            lines = modify_atkMid(5, away, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away)
            lines = modify_atkFor(5, away, lines, atk_for_line, atk_freekick_for_line, forwardPositionsAway, df_ratings, forwardIdsAway, prob_to_lose_home_defenders, aggression_home_defenders, freekick_for_away)
            lines = modify_atkMidDef(away, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsAway, df_ratings, midDefIdsAway, prob_to_lose_home_midforfielders, aggression_home_midforfielders, freekick_middef_away)
            lines = modify_atkMidFor(away, lines, atk_midFor_line, atk_freekick_midFor_line, midForPositionsAway, df_ratings, midForIdsHome, prob_to_lose_home_middeffielders, aggression_home_middeffielders, freekick_midfor_away)
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
                
        elif (is3levels_home and is5levels_away):
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperIdHome = home_team[0]
            defenderPositionsHome = homePositions[1:1 + def_H]
            defenderIdsHome = home_team[1:1 + def_H]
            midfielderPositionsHome = homePositions[1 + def_H:1 + def_H +mid_H]
            midfielderIdsHome = home_team[1 + def_H:1 + def_H +mid_H]
            forwardPositionsHome = homePositions[1 + def_H+mid_H:]
            forwardIdsHome = home_team[1 + def_H+mid_H:]
            midDefPositionsHome = midfielderPositionsHome
            midDefIdsHome = midfielderIdsHome
            midForPositionsHome = midfielderPositionsHome
            midForIdsHome = midfielderIdsHome
            
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperIdAway = away_team[0]
            defenderPositionsAway = awayPositions[1:1 + def_5A]
            defenderIdsAway = away_team[1:1 + def_5A]
            midDefPositionsAway = awayPositions[1 + def_5A:1 + def_5A +midDef_5A]
            midDefIdsAway = away_team[1 + def_5A:1 + def_5A +midDef_5A]
            midfielderPositionsAway = awayPositions[1 + def_5A +midDef_5A:1 + def_5A +midDef_5A +mid_5A]
            midfielderIdsAway = away_team[1 + def_5A +midDef_5A:1 + def_5A +midDef_5A +mid_5A]
            midForPositionsAway = awayPositions[1 + def_5A +midDef_5A +mid_5A:1 + def_5A +midDef_5A +mid_5A + midFor_5A]
            midForIdsAway = away_team[1 + def_5A+midDef_5A +mid_5A:1 + def_5A +midDef_5A +mid_5A + midFor_5A]
            forwardPositionsAway = awayPositions[1 + def_5A +midDef_5A +mid_5A + midFor_5A:]
            forwardIdsAway = away_team[1 + def_5A +midDef_5A +mid_5A + midFor_5A:]
            
            out_file, lines = create_template_file(index, home, away, season, template_file_5f_3rows)
            index = index + 1
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            gk_home_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdHome)))].values
            short_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_away_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdAway)))].values
            gk_handling_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 51 - 1
            atk_def_line = 57 - 1
            atk_freekick_def_line = 59 - 1
            atk_middef_line = 68 - 1
            atk_freekick_middef_line = 70 - 1
            atk_mid_line = 73 - 1
            atk_freekick_mid_line = 75 - 1
            atk_midFor_line = 78- 1
            atk_freekick_midFor_line = 80 - 1 
            atk_for_line = 83 - 1
            atk_freekick_for_line = 85 - 1
            def_kep_line = 90 - 1
            distToKep_line = 105 - 1

            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating
            prob_to_lose_away_forwards, aggression_away_forwards = create_prob_to_lose(forwardIdsAway, df_ratings, away)

            # prob to lose calculated based on average of all midfielders
            midfielderTotal = midfielderIdsAway.copy()
            midfielderTotal.extend(midDefIdsAway)
            midfielderTotal.extend(midForIdsAway)
            prob_to_lose_away_midfielders, aggression_away_midfielders = create_prob_to_lose(midfielderTotal, df_ratings, away)
            prob_to_lose_away_defenders, aggression_away_defenders = create_prob_to_lose(defenderIdsAway, df_ratings, away)

            freekick_def_home = create_free_kick_rating(defenderIdsHome, df_ratings, home, rely_skills='skill_long_passing')
            freekick_mid_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')
            freekick_for_home = create_free_kick_rating(forwardIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')
            freekick_middef_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, 'skill_long_passing')
            freekick_midfor_home = freekick_mid_home

            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)
            prob_to_lose_away_middeffielders,  aggression_away_middeffielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            prob_to_lose_away_midforfielders,  aggression_away_midforfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            
            lines = modify_atkDef(home, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home)
            lines = modify_atkMid(5, home, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsHome, df_ratings, midfielderIdsHome, prob_to_lose_away_midfielders, aggression_away_midfielders, freekick_mid_home)
            lines = modify_atkFor(5, home, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home)
            lines = modify_atkMidDef(home, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_middef_home)
            lines = modify_atkMidFor(home, lines, atk_midFor_line, atk_freekick_midFor_line, midDefPositionsHome, df_ratings, midForIdsHome, prob_to_lose_away_midforfielders, aggression_away_midforfielders, freekick_midfor_home)

            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         

            out_file, lines = create_template_file(index, away, home, season, template_file_5f)
            index = index + 1
            
            short_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_handling_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"

            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            prob_to_lose_home_middeffielders,  aggression_home_middeffielders = create_prob_to_lose(midDefIdsHome, df_ratings, home)
            prob_to_lose_home_midforfielders,  aggression_home_midforfielders = create_prob_to_lose(midForIdsHome, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)

            freekick_def_away = create_free_kick_rating(defenderIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_middef_away = create_free_kick_rating(midDefIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_mid_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_for_away = create_free_kick_rating(forwardIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_midfor_away = create_free_kick_rating(midForIdsAway, df_ratings, away, 'skill_fk_accuracy')

            lines = modify_atkDef(away, lines, atk_def_line, atk_freekick_def_line, defenderPositionsAway, df_ratings, defenderIdsAway, prob_to_lose_home_forwards, aggression_home_forwards, freekick_def_away)
            lines = modify_atkMid(5, away, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away)
            lines = modify_atkFor(5, away, lines, atk_for_line, atk_freekick_for_line, forwardPositionsAway, df_ratings, forwardIdsAway, prob_to_lose_home_defenders, aggression_home_defenders, freekick_for_away)
            lines = modify_atkMidDef(away, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsAway, df_ratings, midDefIdsAway, prob_to_lose_home_midforfielders, aggression_home_midforfielders, freekick_middef_away)
            lines = modify_atkMidFor(away, lines, atk_midFor_line, atk_freekick_midFor_line, midForPositionsAway, df_ratings, midForIdsAway, prob_to_lose_home_middeffielders, aggression_home_middeffielders, freekick_midfor_away)
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
                
        elif (is5levels_home and is3levels_away):
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperIdAway = away_team[0]
            defenderPositionsAway = awayPositions[1:1 + def_A]
            defenderIdsAway = away_team[1:1 + def_A]
            midfielderPositionsAway = awayPositions[1 + def_A:1 + def_A +mid_A]
            midfielderIdsAway = away_team[1 + def_A:1 + def_A +mid_A]
            midDefPositionsAway = midfielderPositionsAway
            midDefIdsAway = midfielderIdsAway
            midForPositionsAway = midfielderPositionsAway
            midForIdsAway = midfielderIdsAway
            forwardPositionsAway = awayPositions[1 + def_A+mid_A:]
            forwardIdsAway = away_team[1 + def_A+mid_A:]
            
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperIdHome = home_team[0]
            defenderPositionsHome = homePositions[1:1 + def_5H]
            defenderIdsHome = home_team[1:1 + def_5H]
            midDefPositionsHome = homePositions[1 + def_5H:1 + def_5H +midDef_5H]
            midDefIdsHome = home_team[1 + def_5H:1 + def_5H +midDef_5H]
            midfielderPositionsHome = homePositions[1 + def_5H + midDef_5H:1 + def_5H +midDef_5H + mid_5H]
            midfielderIdsHome = home_team[1 + def_5H + midDef_5H:1 + def_5H +midDef_5H + mid_5H]
            midForPositionsHome = homePositions[1 + def_5H +midDef_5H +mid_5H:1 + def_5H +midDef_5H +mid_5H + midFor_5H]
            midForIdsHome = home_team[1 + def_5H +midDef_5H +mid_5H:1 + def_5H +midDef_5H +mid_5H + midFor_5H]
            forwardPositionsHome = homePositions[1 + def_5H +midDef_5H + mid_5H + midFor_5H:]
            forwardIdsHome = home_team[1 + def_5H +midDef_5H + mid_5H + midFor_5H:]
            
            out_file, lines = create_template_file(index, home, away, season, template_file_5f)
            index = index + 1
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            #TODO modify Goalkeeper ratings in pcsp file
            #home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home)].value
            gk_home_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdHome)))].values

            short_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]

            gk_away_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdAway)))].values

            gk_handling_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 51 - 1
            atk_def_line = 57 - 1
            atk_freekick_def_line = 59 - 1
            atk_middef_line = 68 - 1
            atk_freekick_middef_line = 70 - 1
            atk_mid_line = 73 - 1
            atk_freekick_mid_line = 75 - 1
            atk_midFor_line = 78- 1
            atk_freekick_midFor_line = 80 - 1 
            atk_for_line = 83 - 1
            atk_freekick_for_line = 85 - 1
            def_kep_line = 90 - 1
            distToKep_line = 105 - 1

            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating

            prob_to_lose_away_forwards,  aggression_away_forwards= create_prob_to_lose(forwardIdsAway, df_ratings, away)
            prob_to_lose_away_middeffielders,  aggression_away_middeffielders = create_prob_to_lose(midDefIdsAway, df_ratings, away)
            prob_to_lose_away_midfielders,  aggression_away_midfielders = create_prob_to_lose(midfielderIdsAway, df_ratings, away)
            prob_to_lose_away_midforfielders,  aggression_away_midforfielders = create_prob_to_lose(midForIdsAway, df_ratings, away)
            prob_to_lose_away_defenders, aggression_away_defenders = create_prob_to_lose(defenderIdsAway, df_ratings, away)
            
            freekick_def_home = create_free_kick_rating(defenderIdsHome, df_ratings, home, 'skill_long_passing')
            freekick_middef_home = create_free_kick_rating(midDefIdsHome, df_ratings, home, 'skill_long_passing')     
            freekick_mid_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, 'skill_fk_accuracy')
            freekick_midfor_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, 'skill_fk_accuracy')
            freekick_for_home = create_free_kick_rating(forwardIdsHome, df_ratings, home, 'skill_fk_accuracy')

            lines = modify_atkDef(home, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home)
            lines = modify_atkMid(5, home, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsHome, df_ratings, midfielderIdsHome, prob_to_lose_away_midfielders, aggression_away_midfielders, freekick_mid_home)
            lines = modify_atkFor(5, home, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home)
            lines = modify_atkMidDef(home, lines, atk_middef_line, atk_freekick_middef_line, midForPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_midforfielders, aggression_away_midforfielders, freekick_middef_home)
            lines = modify_atkMidFor(home, lines, atk_midFor_line, atk_freekick_midFor_line, midForPositionsHome, df_ratings, midForIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_midfor_home)
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
            
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         
            out_file, lines = create_template_file(index, away, home, season, template_file_5f_3rows)
            index = index + 1
            

            short_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_handling_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            
            # consider midfielders as whole to get prob to lose
            midfielderTotal = midfielderIdsHome.copy()
            midfielderTotal.extend(midDefIdsHome)
            midfielderTotal.extend(midForIdsHome)

            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderTotal, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)
            prob_to_lose_home_middeffielders,  aggression_home_middeffielders = create_prob_to_lose(midfielderTotal, df_ratings, home)
            prob_to_lose_home_midforfielders,  aggression_home_midforfielders = create_prob_to_lose(midfielderTotal, df_ratings, home)
            
            freekick_def_away = create_free_kick_rating(defenderIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_mid_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy')  
            freekick_for_away = create_free_kick_rating(forwardIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_middef_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, rely_skills='skill_long_passing')
            freekick_midfor_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy') 
            
            lines = modify_atkDef(away, lines, atk_def_line, atk_freekick_def_line, defenderPositionsAway, df_ratings, defenderIdsAway, prob_to_lose_home_forwards, aggression_home_forwards, freekick_def_away)
            lines = modify_atkMid(5, away, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away) 
            lines = modify_atkFor(5, away, lines, atk_for_line, atk_freekick_for_line, forwardPositionsAway, df_ratings, forwardIdsAway, prob_to_lose_home_defenders, aggression_home_defenders, freekick_for_away)
            lines = modify_atkMidDef(away, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsAway, df_ratings, midDefIdsAway, prob_to_lose_home_middeffielders, aggression_home_middeffielders, freekick_middef_away)
            lines = modify_atkMidFor(away, lines, atk_midFor_line, atk_freekick_midFor_line, midForPositionsAway, df_ratings, midForIdsAway, prob_to_lose_home_midforfielders, aggression_home_midforfielders, freekick_midfor_away)
            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
            
        elif (is4levels_home and is5levels_away):
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperIdHome = home_team[0]
            defenderPositionsHome = homePositions[1:1 + def_4H]
            defenderIdsHome = home_team[1:1 + def_4H]
            midDefPositionsHome = homePositions[1 + def_4H:1 + def_4H +midDef_4H]
            midDefIdsHome = home_team[1 + def_4H:1 + def_4H +midDef_4H]
            midfielderPositionsHome = homePositions[1 + def_4H + midDef_4H:1 + def_4H +midDef_4H + mid_4H]
            midfielderIdsHome = home_team[1 + def_4H + midDef_4H:1 + def_4H +midDef_4H + mid_4H]
            midForPositionsHome = midfielderPositionsHome
            midForIdsHome = midfielderIdsHome
            forwardPositionsHome = homePositions[1 + def_4H +midDef_4H + mid_4H:]
            forwardIdsHome = home_team[1 + def_4H +midDef_4H + mid_4H:]
            
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperIdAway = away_team[0]
            defenderPositionsAway = awayPositions[1:1 + def_5A]
            defenderIdsAway = away_team[1:1 + def_5A]
            midDefPositionsAway = awayPositions[1 + def_5A:1 + def_5A +midDef_5A]
            midDefIdsAway = away_team[1 + def_5A:1 + def_5A +midDef_5A]
            midfielderPositionsAway = awayPositions[1 + def_5A +midDef_5A:1 + def_5A +midDef_5A +mid_5A]
            midfielderIdsAway = away_team[1 + def_5A +midDef_5A:1 + def_5A +midDef_5A +mid_5A]
            midForPositionsAway = awayPositions[1 + def_5A +midDef_5A +mid_5A:1 + def_5A +midDef_5A +mid_5A + midFor_5A]
            midForIdsAway = away_team[1 + def_5A+midDef_5A +mid_5A:1 + def_5A +midDef_5A +mid_5A + midFor_5A]
            forwardPositionsAway = awayPositions[1 + def_5A +midDef_5A +mid_5A + midFor_5A:]
            forwardIdsAway = away_team[1 + def_5A +midDef_5A +mid_5A + midFor_5A:]
            
            out_file, lines = create_template_file(index, home, away, season, template_file_5f_4rows)
            index = index + 1
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            gk_home_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdHome)))].values
            short_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_away_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdAway)))].values
            gk_handling_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 51 - 1
            atk_def_line = 57 - 1
            atk_freekick_def_line = 59 - 1
            atk_middef_line = 68 - 1
            atk_freekick_middef_line = 70 - 1
            atk_mid_line = 73 - 1
            atk_freekick_mid_line = 75 - 1
            atk_midFor_line = 78- 1
            atk_freekick_midFor_line = 80 - 1 
            atk_for_line = 83 - 1
            atk_freekick_for_line = 85 - 1
            def_kep_line = 90 - 1
            distToKep_line = 105 - 1

            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating
            prob_to_lose_away_forwards, aggression_away_forwards = create_prob_to_lose(forwardIdsAway, df_ratings, away)

            # prob to lose calculated based on average of midfielders + forMidfielders
            midfielderTotal = midfielderIdsAway.copy()
            midfielderTotal.extend(midForIdsAway)
            prob_to_lose_away_midfielders, aggression_away_midfielders = create_prob_to_lose(midfielderTotal, df_ratings, away)
            prob_to_lose_away_middeffielders, aggression_away_middeffielders = create_prob_to_lose(midDefIdsAway, df_ratings, away)
            prob_to_lose_away_midforfielders, aggression_away_midforfielders = prob_to_lose_away_middeffielders, aggression_away_middeffielders
            prob_to_lose_away_defenders, aggression_away_defenders = create_prob_to_lose(defenderIdsAway, df_ratings, away)

            freekick_def_home = create_free_kick_rating(defenderIdsHome, df_ratings, home, rely_skills='skill_long_passing')
            freekick_mid_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')
            freekick_for_home = create_free_kick_rating(forwardIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')
            freekick_middef_home = create_free_kick_rating(midDefIdsHome, df_ratings, home, 'skill_long_passing')
            freekick_midfor_home = freekick_mid_home

            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)
            prob_to_lose_home_middeffielders,  aggression_home_middeffielders = create_prob_to_lose(midDefIdsHome, df_ratings, home)
            prob_to_lose_home_midforfielders,  aggression_home_midforfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            
            lines = modify_atkDef(home, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home)
            lines = modify_atkMid(5, home, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsHome, df_ratings, midfielderIdsHome, prob_to_lose_away_midfielders, aggression_away_midfielders, freekick_mid_home)
            lines = modify_atkFor(5, home, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home)
            lines = modify_atkMidDef(home, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_midforfielders, aggression_away_midforfielders, freekick_middef_home)
            lines = modify_atkMidFor(home, lines, atk_midFor_line, atk_freekick_midFor_line, midForPositionsHome, df_ratings, midForIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_midfor_home)

            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         

            out_file, lines = create_template_file(index, away, home, season, template_file_5f)
            index = index + 1

            short_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_handling_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"

            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            prob_to_lose_home_middeffielders,  aggression_home_middeffielders = create_prob_to_lose(midDefIdsHome, df_ratings, home)
            prob_to_lose_home_midforfielders,  aggression_home_midforfielders = create_prob_to_lose(midForIdsHome, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)

            freekick_def_away = create_free_kick_rating(defenderIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_middef_away = create_free_kick_rating(midDefIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_mid_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_for_away = create_free_kick_rating(forwardIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_midfor_away = create_free_kick_rating(midForIdsAway, df_ratings, away, 'skill_fk_accuracy')

            lines = modify_atkDef(away, lines, atk_def_line, atk_freekick_def_line, defenderPositionsAway, df_ratings, defenderIdsAway, prob_to_lose_home_forwards, aggression_home_forwards, freekick_def_away)
            lines = modify_atkMid(5, away, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away)
            lines = modify_atkFor(5, away, lines, atk_for_line, atk_freekick_for_line, forwardPositionsAway, df_ratings, forwardIdsAway, prob_to_lose_home_defenders, aggression_home_defenders, freekick_for_away)
            lines = modify_atkMidDef(away, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsAway, df_ratings, midDefIdsAway, prob_to_lose_home_midforfielders, aggression_home_midforfielders, freekick_middef_away)
            lines = modify_atkMidFor(away, lines, atk_midFor_line, atk_freekick_midFor_line, midForPositionsAway, df_ratings, midForIdsAway, prob_to_lose_home_middeffielders, aggression_home_middeffielders, freekick_midfor_away)
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
          
        elif (is5levels_home and is4levels_away):
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperIdAway = away_team[0]
            defenderPositionsAway = awayPositions[1:1 + def_4A]
            defenderIdsAway = away_team[1:1 + def_4A]
            midDefPositionsAway = awayPositions[1 + def_4A:1 + def_4A +midDef_4A]
            midDefIdsAway = away_team[1 + def_4A:1 + def_4A +midDef_4A]
            midfielderPositionsAway = awayPositions[1 + def_4A + midDef_4A:1 + def_4A +midDef_4A + mid_4A]
            midfielderIdsAway = away_team[1 + def_4A + midDef_4A:1 + def_4A +midDef_4A + mid_4A]
            midForPositionsAway = midfielderPositionsAway
            midForIdsAway = midfielderIdsAway
            forwardPositionsAway = awayPositions[1 + def_4A +midDef_4A + mid_4A:]
            forwardIdsAway = away_team[1 + def_4A +midDef_4A + mid_4A:]
            
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperIdHome = home_team[0]
            defenderPositionsHome = homePositions[1:1 + def_5H]
            defenderIdsHome = home_team[1:1 + def_5H]
            midDefPositionsHome = homePositions[1 + def_5H:1 + def_5H +midDef_5H]
            midDefIdsHome = home_team[1 + def_5H:1 + def_5H +midDef_5H]
            midfielderPositionsHome = homePositions[1 + def_5H +midDef_5H:1 + def_5H +midDef_5H +mid_5H]
            midfielderIdsHome = home_team[1 + def_5H +midDef_5H:1 + def_5H +midDef_5H +mid_5H]
            midForPositionsHome = homePositions[1 + def_5H +midDef_5H+mid_5H:1 + def_5H +midDef_5H+mid_5H + midFor_5H]
            midForIdsHome = home_team[1 + def_5H+midDef_5H +mid_5H:1 + def_5H +midDef_5H +mid_5H + midFor_5H]
            forwardPositionsHome = homePositions[1 + def_5H +midDef_5H +mid_5H + midFor_5H:]
            forwardIdsHome = home_team[1 + def_5A +midDef_5H +mid_5H + midFor_5H:]
            
            out_file, lines = create_template_file(index, home, away, season, template_file_5f)
            index = index + 1
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            
            
            gk_home_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdHome)))].values
            short_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_away_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdAway)))].values
            gk_handling_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 51 - 1
            atk_def_line = 57 - 1
            atk_freekick_def_line = 59 - 1
            atk_middef_line = 68 - 1
            atk_freekick_middef_line = 70 - 1
            atk_mid_line = 73 - 1
            atk_freekick_mid_line = 75 - 1
            atk_midFor_line = 78- 1
            atk_freekick_midFor_line = 80 - 1 
            atk_for_line = 83 - 1
            atk_freekick_for_line = 85 - 1
            def_kep_line = 90 - 1
            distToKep_line = 105 - 1

            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating

            prob_to_lose_away_forwards,  aggression_away_forwards= create_prob_to_lose(forwardIdsAway, df_ratings, away)
            prob_to_lose_away_middeffielders,  aggression_away_middeffielders = create_prob_to_lose(midDefIdsAway, df_ratings, away)
            prob_to_lose_away_midfielders,  aggression_away_midfielders = create_prob_to_lose(midfielderIdsAway, df_ratings, away)
            prob_to_lose_away_midforfielders,  aggression_away_midforfielders = create_prob_to_lose(midForIdsAway, df_ratings, away)
            prob_to_lose_away_defenders, aggression_away_defenders = create_prob_to_lose(defenderIdsAway, df_ratings, away)
            
            freekick_def_home = create_free_kick_rating(defenderIdsHome, df_ratings, home, 'skill_long_passing')
            freekick_middef_home = create_free_kick_rating(midDefIdsHome, df_ratings, home, 'skill_long_passing')     
            freekick_mid_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, 'skill_fk_accuracy')
            freekick_midfor_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, 'skill_fk_accuracy')
            freekick_for_home = create_free_kick_rating(forwardIdsHome, df_ratings, home, 'skill_fk_accuracy')

            lines = modify_atkDef(home, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home)
            lines = modify_atkMid(5, home, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsHome, df_ratings, midfielderIdsHome, prob_to_lose_away_midfielders, aggression_away_midfielders, freekick_mid_home)
            lines = modify_atkFor(5, home, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home)
            lines = modify_atkMidDef(home, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_midforfielders, aggression_away_midforfielders, freekick_middef_home)
            lines = modify_atkMidFor(home, lines, atk_midFor_line, atk_freekick_midFor_line, midForPositionsHome, df_ratings, midForIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_midfor_home)
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         

            out_file, lines = create_template_file(index, away, home, season, template_file_5f_4rows)
            index = index + 1

            short_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_handling_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"

            # consider midfielders as whole to get prob to lose
            midfielderTotal = midfielderIdsHome.copy()
            midfielderTotal.extend(midForIdsHome)

            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderTotal, df_ratings, home)
            prob_to_lose_home_middeffielders,  aggression_home_middeffielders = create_prob_to_lose(midDefIdsHome, df_ratings, home)
            prob_to_lose_home_midforfielders,  aggression_home_midforfielders = create_prob_to_lose(midfielderTotal, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)

            freekick_def_away = create_free_kick_rating(defenderIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_middef_away = create_free_kick_rating(midDefIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_mid_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_for_away = create_free_kick_rating(forwardIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_midfor_away = create_free_kick_rating(midForIdsAway, df_ratings, away, 'skill_fk_accuracy')

            lines = modify_atkDef(away, lines, atk_def_line, atk_freekick_def_line, defenderPositionsAway, df_ratings, defenderIdsAway, prob_to_lose_home_forwards, aggression_home_forwards, freekick_def_away)
            lines = modify_atkMid(5, away, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away)
            lines = modify_atkFor(5, away, lines, atk_for_line, atk_freekick_for_line, forwardPositionsAway, df_ratings, forwardIdsAway, prob_to_lose_home_defenders, aggression_home_defenders, freekick_for_away)
            lines = modify_atkMidDef(away, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsAway, df_ratings, midDefIdsAway, prob_to_lose_home_midforfielders, aggression_home_midforfielders, freekick_middef_away)
            lines = modify_atkMidFor(away, lines, atk_midFor_line, atk_freekick_midFor_line, midForPositionsAway, df_ratings, midForIdsAway, prob_to_lose_home_middeffielders, aggression_home_middeffielders, freekick_midfor_away)
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
        
        elif (is3levels_home and is4levels_away):
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperIdHome = home_team[0]
            defenderPositionsHome = homePositions[1:1 + def_H]
            defenderIdsHome = home_team[1:1 + def_H]
            midfielderPositionsHome = homePositions[1 + def_H:1 + def_H +mid_H]
            midfielderIdsHome = home_team[1 + def_H:1 + def_H +mid_H]
            midDefPositionsHome = midfielderPositionsHome
            midDefIdsHome = midfielderIdsHome
            forwardPositionsHome = homePositions[1 + def_H+mid_H:]
            forwardIdsHome = home_team[1 + def_H+mid_H:]
            
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperIdAway = away_team[0]
            defenderPositionsAway = awayPositions[1:1 + def_4A]
            defenderIdsAway = away_team[1:1 + def_4A]
            midDefPositionsAway = awayPositions[1 + def_4A:1 + def_4A +midDef_4A]
            midDefIdsAway = away_team[1 + def_4A:1 + def_4A +midDef_4A]
            midfielderPositionsAway = awayPositions[1 + def_4A +midDef_4A:1 + def_4A +midDef_4A +mid_4A]
            midfielderIdsAway = away_team[1 + def_4A:1 + def_4A +midDef_4A +mid_4A]
            forwardPositionsAway = awayPositions[1 + def_4A +midDef_4A +mid_4A:]
            forwardIdsAway = away_team[1 + def_4A +midDef_4A +mid_4A:]
            ##generate home pcsp file using 3 levels template
            
            
            out_file, lines = create_template_file(index, home, away, season, template_file_4f_3rows)
            index = index + 1
            # out_file, lines = create_template_files(index, home, away, season, template_file_3f)
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            #TODO modify Goalkeeper ratings in pcsp file
            #home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home)].value
            gk_home_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdHome)))].values
            short_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_away_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdAway)))].values
            gk_handling_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 50 - 1
            atk_def_line = 56 - 1
            atk_freekick_def_line = 58 - 1
            atk_middef_line = 67 - 1
            atk_freekick_middef_line = 69 - 1
            atk_mid_line = 72 - 1
            atk_freekick_mid_line = 74 - 1
            atk_for_line = 77 - 1
            atk_freekick_for_line = 79 - 1
            def_kep_line = 83 - 1
            distToKep_line = 97 - 1

            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating


            prob_to_lose_away_forwards, aggression_away_forwards = create_prob_to_lose(forwardIdsAway, df_ratings, away)

            # prob to lose calculated based on average of all midfielders
            midfielderTotal = midfielderIdsAway.copy()
            midfielderTotal.extend(midDefIdsAway)
            prob_to_lose_away_midfielders, aggression_away_midfielders = create_prob_to_lose(midfielderTotal, df_ratings, away)
            prob_to_lose_away_defenders, aggression_away_defenders = create_prob_to_lose(defenderIdsAway, df_ratings, away)


            freekick_def_home = create_free_kick_rating(defenderIdsHome, df_ratings, home, rely_skills='skill_long_passing')
            freekick_mid_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')
            freekick_for_home = create_free_kick_rating(forwardIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')
            freekick_middef_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, 'skill_long_passing')

            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)
            prob_to_lose_away_middeffielders,  aggression_away_middeffielders = create_prob_to_lose(midfielderIdsHome, df_ratings, home)

            lines = modify_atkDef(home, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home)
            lines = modify_atkMid(4, home, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsHome, df_ratings, midfielderIdsHome, prob_to_lose_away_midfielders, aggression_away_midfielders, freekick_mid_home)
            lines = modify_atkFor(4, home, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home)
            lines = modify_atkMidDef(home, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_middef_home)
            # lines = modify_atkMidDef(home, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_middef_home)

            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         

            out_file, lines = create_template_file(index, away, home, season, template_file_4f)
            index = index + 1

            short_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_handling_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50

            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"

            # Calculate probability to lose posession to home team forwards
            # Calculate also the aggression rating

            # mid, middef calculated based on opponent team's mid fielder only
            # prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            # prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderNamesHome, df_ratings, home)
            # prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)
            # prob_to_lose_away_middeffielders,  aggression_away_middeffielders = create_prob_to_lose(midfielderNamesHome, df_ratings, home)
            

            freekick_def_away = create_free_kick_rating(defenderIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_mid_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_for_away = create_free_kick_rating(forwardIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_middef_away = create_free_kick_rating(midDefIdsAway, df_ratings, away, 'skill_long_passing')
            
            
            lines = modify_atkDef(away, lines, atk_def_line, atk_freekick_def_line, defenderPositionsAway, df_ratings, defenderIdsAway, prob_to_lose_home_forwards, aggression_home_forwards, freekick_def_away)
            lines = modify_atkMid(4, away, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away)
            lines = modify_atkFor(4, away, lines, atk_for_line, atk_freekick_for_line, forwardPositionsAway, df_ratings, forwardIdsAway, prob_to_lose_home_defenders, aggression_home_defenders, freekick_for_away)
            lines = modify_atkMidDef(away, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsAway, df_ratings, midDefIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_middef_away)

            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)

        elif (is4levels_home and is3levels_away):
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperIdAway = away_team[0]
            defenderPositionsAway = awayPositions[1:1 + def_A]
            defenderIdsAway = away_team[1:1 + def_A]
            midfielderPositionsAway = awayPositions[1 + def_A:1 + def_A +mid_A]
            midfielderIdsAway = away_team[1 + def_A:1 + def_A +mid_A]
            midDefPositionsAway = midfielderPositionsAway
            midDefIdsAway = midfielderIdsAway
            forwardPositionsAway = awayPositions[1 + def_A+mid_A:]
            forwardIdsAway = away_team[1 + def_A+mid_A:]
            
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperIdHome = home_team[0]
            defenderPositionsHome = homePositions[1:1 + def_4H]
            defenderIdsHome = home_team[1:1 + def_4H]
            midDefPositionsHome = homePositions[1 + def_4H:1 + def_4H +midDef_4H]
            midDefIdsHome = home_team[1 + def_4H:1 + def_4H +midDef_4H]
            midfielderPositionsHome = homePositions[1 + def_4H + midDef_4H:1 + def_4H +midDef_4H + mid_4H]
            midfielderIdsHome = home_team[1 + def_4H + midDef_4H:1 + def_4H +midDef_4H + mid_4H]
            forwardPositionsHome = homePositions[1 + def_4H +midDef_4H + mid_4H:]
            forwardIdsHome = home_team[1 + def_4H +midDef_4H + mid_4H:]

            
            out_file, lines = create_template_file(index, home, away, season, template_file_4f)
            index = index + 1
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            #TODO modify Goalkeeper ratings in pcsp file
            #home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home)].values
        
            gk_home_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdHome)))].values
            short_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_away_ratings_row = df_ratings.loc[(lambda df: df['sofifa_id'] == int(float(goalkeeperIdAway)))].values
            gk_handling_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50
            # Define the line number of AtkKep and DefKep in the file

           # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 50 - 1
            atk_def_line = 56 - 1
            atk_freekick_def_line = 58 - 1
            atk_middef_line = 67 - 1
            atk_freekick_middef_line = 69 - 1
            atk_mid_line = 72 - 1
            atk_freekick_mid_line = 74 - 1
            atk_for_line = 77 - 1
            atk_freekick_for_line = 79 - 1
            def_kep_line = 83 - 1
            distToKep_line = 97 - 1


            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating


            prob_to_lose_away_forwards, aggression_away_forwards = create_prob_to_lose(forwardIdsAway, df_ratings, away)
            # The prob to lose is the same for mid fielders and mid def fielders
            prob_to_lose_away_midfielders, aggression_away_midfielders = create_prob_to_lose(midfielderIdsAway, df_ratings, away)
            prob_to_lose_away_middeffielders, aggression_away_middeffielders = create_prob_to_lose(midfielderIdsAway, df_ratings, away)
            prob_to_lose_away_defenders, aggression_away_defenders = create_prob_to_lose(defenderIdsAway, df_ratings, away)


            freekick_def_home = create_free_kick_rating(defenderIdsHome, df_ratings, home, rely_skills='skill_long_passing')
            freekick_mid_home = create_free_kick_rating(midfielderIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')                             
            freekick_for_home = create_free_kick_rating(forwardIdsHome, df_ratings, home, rely_skills='skill_fk_accuracy')
            freekick_middef_home = create_free_kick_rating(midDefIdsHome, df_ratings, home, rely_skills='skill_long_passing')

            
            lines = modify_atkDef(home, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home)
            lines = modify_atkMid(4, home, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsHome, df_ratings, midfielderIdsHome, prob_to_lose_away_midfielders, aggression_away_midfielders, freekick_mid_home)
            lines = modify_atkFor(4, home, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home)
            lines = modify_atkMidDef(home, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_middef_home)
            
            
            # Open the file in write mode and write the modified content

            with open(out_file, 'w') as file:
                file.writelines(lines)
            
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         
            out_file, lines = create_template_file(index, away, home, season, template_file_4f_3rows)
            index = index + 1

            short_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
            long_pass_rating = gk_away_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
            gk_handling_rating = gk_home_ratings_row[0][df_ratings.columns.get_loc('gk_handling')]
            if (pd.isna(gk_handling_rating)):
                gk_handling_rating = 50
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({int(gk_handling_rating)}, C);\n"
            prob_to_lose_home_forwards, aggression_home_forwards = create_prob_to_lose(forwardIdsHome, df_ratings, home)
            
            # consider midfielders as whole to get prob to lose
            midfielderTotal = midfielderIdsHome.copy()
            midfielderTotal.extend(midDefIdsHome)

            prob_to_lose_home_midfielders, aggression_home_midfielders = create_prob_to_lose(midfielderTotal, df_ratings, home)
            prob_to_lose_home_defenders, aggression_home_defenders = create_prob_to_lose(defenderIdsHome, df_ratings, home)
            prob_to_lose_home_middeffielders,  aggression_home_middeffielders = create_prob_to_lose(midfielderTotal, df_ratings, home)

            
            freekick_def_away = create_free_kick_rating(defenderIdsAway, df_ratings, away, 'skill_long_passing')
            freekick_mid_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, 'skill_fk_accuracy')  
            freekick_for_away = create_free_kick_rating(forwardIdsAway, df_ratings, away, 'skill_fk_accuracy')
            freekick_middef_away = create_free_kick_rating(midfielderIdsAway, df_ratings, away, rely_skills='skill_long_passing')
        

            lines = modify_atkDef(away, lines, atk_def_line, atk_freekick_def_line, defenderPositionsAway, df_ratings, defenderIdsAway, prob_to_lose_home_forwards, aggression_home_forwards, freekick_def_away)
            lines = modify_atkMid(4, away, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away) 
            lines = modify_atkFor(4, away, lines, atk_for_line, atk_freekick_for_line, forwardPositionsAway, df_ratings, forwardIdsAway, prob_to_lose_home_defenders, aggression_home_defenders, freekick_for_away)
            lines = modify_atkMidDef(away, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsAway, df_ratings, midDefIdsAway, prob_to_lose_home_middeffielders, aggression_home_middeffielders, freekick_middef_away)

            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)

        else:
            print("Unknown formation")
            sys.exit(1)
    return match_url_arr
    
def create_prob_to_lose(id_array, df_ratings, curr_team):
    no_of_forwards = len(id_array)
    combined_ratings = 0
    aggression_ratings = 0
    for ind in range(no_of_forwards):
        curr_team_ratings_row = df_ratings.loc[(df_ratings['sofifa_id'] == int(float(id_array[ind])))].values
        interception_ratings = curr_team_ratings_row[0][df_ratings.columns.get_loc('mentality_interceptions')]
        standing_tackle_ratings = curr_team_ratings_row[0][df_ratings.columns.get_loc('defending_standing_tackle')]
        sliding_tackle_ratings = curr_team_ratings_row[0][df_ratings.columns.get_loc('defending_sliding_tackle')]
        max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
        combined_ratings = combined_ratings + max_rating_out_of_the_three
                
        aggression_ratings = aggression_ratings + int(curr_team_ratings_row[0][df_ratings.columns.get_loc('mentality_aggression')])
    prob_to_lose_curr_team = math.ceil(combined_ratings / no_of_forwards)
    aggression_curr_team = math.ceil(aggression_ratings / no_of_forwards)
    return prob_to_lose_curr_team, aggression_curr_team

def create_free_kick_rating(id_array, df_ratings, curr_team, rely_skills):
    freekick_def_home = 0
    for ind in range(len(id_array)):
        home_defender_ratings_row = df_ratings.loc[(df_ratings['sofifa_id'] == int(float(id_array[ind])))].values
        lp = home_defender_ratings_row[0][df_ratings.columns.get_loc(rely_skills)]
        freekick_def_home = freekick_def_home + int(lp)
    freekick_def_home = math.ceil(freekick_def_home / len(id_array))

    return freekick_def_home
    
def modify_atkDef(curr_team, lines, atk_def_line, atk_freekick_def_line, defenderPositionsHome, df_ratings, defenderIdsHome, prob_to_lose_away_forwards, aggression_away_forwards, freekick_def_home):
            lines[atk_def_line] = "AtkDef = "
            lines[atk_freekick_def_line] = "AtkFreeKickDef = "
            for ind,pos in enumerate(defenderPositionsHome):
                def_ratings_row = df_ratings.loc[(df_ratings['sofifa_id'] == int(float(defenderIdsHome[ind])))].values
                sp = def_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
                lp = def_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
                if (pos == "L"):
                    lines[39 - 1] = lines[39 - 1][:24] + "1" + lines[39 - 1][25:]
                elif (pos == "LR"):
                    lines[39 - 1] = lines[39 - 1][:27] + "1" + lines[39 - 1][28:]
                elif (pos == "CL"):
                    lines[39 - 1] = lines[39 - 1][:30] + "1" + lines[39 - 1][31:]
                elif (pos == "C"):
                    lines[39 - 1] = lines[39 - 1][:33] + "1" + lines[39 - 1][34:]
                elif (pos == "CR"):
                    lines[39 - 1] = lines[39 - 1][:36] + "1" + lines[39 - 1][37:]
                elif (pos == "RL"):
                    lines[39 - 1] = lines[39 - 1][:39] + "1" + lines[39 - 1][40:]
                elif (pos == "R"):
                    lines[39 - 1] = lines[39 - 1][:42] + "1" + lines[39 - 1][43:]
                else:
                    print("wrong position")
                    sys.exit(1)
                if ind == 0:
                    lines[atk_def_line] = lines[atk_def_line] + f"[pos[{pos}] == 1]Def({sp}, {lp}, {prob_to_lose_away_forwards}, {aggression_away_forwards}, {pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[pos[{pos}] == 1]FKDef({freekick_def_home}, {pos})"
                else:
                    lines[atk_def_line] = lines[atk_def_line] + f"[] [pos[{pos}] == 1]Def({sp}, {lp}, {prob_to_lose_away_forwards}, {aggression_away_forwards}, {pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[] [pos[{pos}] == 1]FKDef({freekick_def_home}, {pos})"
            lines[atk_def_line] = lines[atk_def_line] + ";"                
            lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + ";"
            return lines

def modify_atkMid(num_level, curr_team, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away):
            if num_level == 3:
                num_line = 40
            else:
                num_line = 41

            lines[atk_mid_line] = "AtkMid = "
            lines[atk_freekick_mid_line] = "AtkFreeKickMid = "
            for ind,pos in enumerate(midfielderPositionsAway):
                mid_ratings_row = df_ratings.loc[(df_ratings['sofifa_id'] == int(float(midfielderIdsAway[ind])))].values
                sp = mid_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
                lp = mid_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
                ls = mid_ratings_row[0][df_ratings.columns.get_loc('power_long_shots')]
                if (pos == "L"):
                    lines[num_line - 1] = lines[num_line - 1][:24] + "1" + lines[num_line - 1][25:]
                elif (pos == "LR"):
                    lines[num_line - 1] = lines[num_line - 1][:27] + "1" + lines[num_line - 1][28:]
                elif (pos == "CL"):
                    lines[num_line - 1] = lines[num_line - 1][:30] + "1" + lines[num_line - 1][31:]
                elif (pos == "C"):
                    lines[num_line - 1] = lines[num_line - 1][:33] + "1" + lines[num_line - 1][34:]
                elif (pos == "CR"):
                    lines[num_line - 1] = lines[num_line - 1][:36] + "1" + lines[num_line - 1][37:]
                elif (pos == "RL"):
                    lines[num_line - 1] = lines[num_line - 1][:39] + "1" + lines[num_line - 1][40:]
                elif (pos == "R"):
                    lines[num_line - 1] = lines[num_line - 1][:42] + "1" + lines[num_line - 1][43:]
                else:
                    print("wrong position")
                    sys.exit(1)
                if ind == 0:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[pos[{pos}] == 1]Mid({sp}, {lp}, {ls},{prob_to_lose_home_midfielders}, {aggression_home_midfielders}, {pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[pos[{pos}] == 1]FKMid({freekick_mid_away}, {pos})"
                else:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[] [pos[{pos}] == 1]Mid({sp}, {lp}, {ls},{prob_to_lose_home_midfielders}, {aggression_home_midfielders}, {pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[] [pos[{pos}] == 1]FKMid({freekick_mid_away}, {pos})"
            lines[atk_mid_line] = lines[atk_mid_line] + ";"
            lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + ";"
            return lines

def modify_atkMidFor(curr_team, lines, atk_mid_line, atk_freekick_mid_line, midfielderPositionsAway, df_ratings, midfielderIdsAway, prob_to_lose_home_midfielders, aggression_home_midfielders, freekick_mid_away):
            num_line = 42
            lines[atk_mid_line] = "AtkMidFor = "
            lines[atk_freekick_mid_line] = "AtkFreeKickMidFor = "
            for ind,pos in enumerate(midfielderPositionsAway):
                mid_ratings_row = df_ratings.loc[(df_ratings['sofifa_id'] == int(float(midfielderIdsAway[ind])))].values
                sp = mid_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
                lp = mid_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
                ls = mid_ratings_row[0][df_ratings.columns.get_loc('power_long_shots')]
                if (pos == "L"):
                    lines[num_line - 1] = lines[num_line - 1][:27] + "1" + lines[num_line - 1][28:]
                elif (pos == "LR"):
                    lines[num_line - 1] = lines[num_line - 1][:30] + "1" + lines[num_line - 1][31:]
                elif (pos == "CL"):
                    lines[num_line - 1] = lines[num_line - 1][:33] + "1" + lines[num_line - 1][34:]
                elif (pos == "C"):
                    lines[num_line - 1] = lines[num_line - 1][:36] + "1" + lines[num_line - 1][37:]
                elif (pos == "CR"):
                    lines[num_line - 1] = lines[num_line - 1][:39] + "1" + lines[num_line - 1][40:]
                elif (pos == "RL"):
                    lines[num_line - 1] = lines[num_line - 1][:42] + "1" + lines[num_line - 1][43:]
                elif (pos == "R"):
                    lines[num_line - 1] = lines[num_line - 1][:45] + "1" + lines[num_line - 1][46:]
                else:
                    print("wrong position")
                    sys.exit(1)
                if ind == 0:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[pos[{pos}] == 1]MidFor({sp}, {lp},{ls}, {prob_to_lose_home_midfielders}, {aggression_home_midfielders}, {pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[pos[{pos}] == 1]FKMidFor({freekick_mid_away}, {pos})"
                else:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[] [pos[{pos}] == 1]MidFor({sp}, {lp},{ls}, {prob_to_lose_home_midfielders}, {aggression_home_midfielders}, {pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[] [pos[{pos}] == 1]FKMidFor({freekick_mid_away}, {pos})"
            lines[atk_mid_line] = lines[atk_mid_line] + ";"
            lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + ";"
            return lines

def modify_atkFor(num_level, curr_team, lines, atk_for_line, atk_freekick_for_line, forwardPositionsHome, df_ratings, forwardIdsHome, prob_to_lose_away_defenders, aggression_away_defenders, freekick_for_home):
            if num_level == 3:
                num_line1 = 41
                num_line2 = 91
            elif num_level == 4:
                num_line1 = 42
                num_line2 = 97
            else:
                num_line1 = 43
                num_line2 = 105

            lines[atk_for_line] = "AtkFor = "
            lines[atk_freekick_for_line] = "AtkFreeKickFor = "
            for ind,pos in enumerate(forwardPositionsHome):
                for_ratings_row = df_ratings.loc[(df_ratings['sofifa_id'] == int(float(forwardIdsHome[ind])))].values
                sp = for_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
                lp = for_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
                ls = for_ratings_row[0][df_ratings.columns.get_loc('power_long_shots')]
                fi = for_ratings_row[0][df_ratings.columns.get_loc('attacking_finishing')]
                vo = for_ratings_row[0][df_ratings.columns.get_loc('attacking_volleys')]
                dr = for_ratings_row[0][df_ratings.columns.get_loc('skill_dribbling')]
                he = for_ratings_row[0][df_ratings.columns.get_loc('attacking_heading_accuracy')]
                if (pos == "L"):
                    lines[num_line1 - 1] = lines[num_line1 - 1][:24] + "1" + lines[num_line1 - 1][25:]
                    lines[num_line2 - 1] = lines[num_line2  - 1][:24] + "4" + lines[num_line2  - 1][25:]
                elif (pos == "LR"):
                    lines[num_line1 - 1] = lines[num_line1 - 1][:27] + "1" + lines[num_line1 - 1][28:]
                    lines[num_line2  - 1] = lines[num_line2  - 1][:27] + "4" + lines[num_line2  - 1][28:]
                elif (pos == "CL"):
                    lines[num_line1 - 1] = lines[num_line1 - 1][:30] + "1" + lines[num_line1 - 1][31:]
                    lines[num_line2  - 1] = lines[num_line2  - 1][:30] + "4" + lines[num_line2  - 1][31:]
                elif (pos == "C"):
                    lines[num_line1 - 1] = lines[num_line1 - 1][:33] + "1" + lines[num_line1 - 1][34:]
                    lines[num_line2  - 1] = lines[num_line2  - 1][:33] + "4" + lines[num_line2  - 1][34:]
                elif (pos == "CR"):
                    lines[num_line1 - 1] = lines[num_line1 - 1][:36] + "1" + lines[num_line1 - 1][37:]
                    lines[num_line2  - 1] = lines[num_line2  - 1][:36] + "4" + lines[num_line2  - 1][37:]
                elif (pos == "RL"):
                    lines[num_line1 - 1] = lines[num_line1 - 1][:39] + "1" + lines[num_line1 - 1][40:]
                    lines[num_line2  - 1] = lines[num_line2  - 1][:39] + "4" + lines[num_line2  - 1][40:]
                elif (pos == "R"):
                    lines[num_line1 - 1] = lines[num_line1 - 1][:42] + "1" + lines[num_line1 - 1][43:]
                    lines[num_line2  - 1] = lines[num_line2  - 1][:42] + "4" + lines[num_line2  - 1][43:]
                else:
                    print("wrong position")
                    sys.exit(1)
                if ind == 0:
                    lines[atk_for_line] = lines[atk_for_line] + f"[pos[{pos}] == 1]For({sp}, {lp},{fi},{ls},{vo},{he},{dr}, {prob_to_lose_away_defenders}, {aggression_away_defenders}, {pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[pos[{pos}] == 1]FKFor({freekick_for_home}, {pos})"
                else:
                    lines[atk_for_line] = lines[atk_for_line] + f"[] [pos[{pos}] == 1]For({sp}, {lp},{fi},{ls},{vo},{he},{dr}, {prob_to_lose_away_defenders}, {aggression_away_defenders}, {pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[] [pos[{pos}] == 1]FKFor({freekick_for_home}, {pos})"
            lines[atk_for_line] = lines[atk_for_line] + ";"
            lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + ";"
            return lines

def modify_atkMidDef(curr_team, lines, atk_middef_line, atk_freekick_middef_line, midDefPositionsHome, df_ratings, midDefIdsHome, prob_to_lose_away_middeffielders, aggression_away_middeffielders, freekick_middef_home):
            lines[atk_middef_line] = "AtkMidDef = "
            lines[atk_freekick_middef_line] = "AtkFreeKickMidDef = "
            for ind,pos in enumerate(midDefPositionsHome):
                middef_ratings_row = df_ratings.loc[(df_ratings['sofifa_id'] == int(float(midDefIdsHome[ind])))].values
                sp = middef_ratings_row[0][df_ratings.columns.get_loc('attacking_short_passing')]
                lp = middef_ratings_row[0][df_ratings.columns.get_loc('skill_long_passing')]
                if (pos == "L"):
                    lines[40 - 1] = lines[40 - 1][:27] + "1" + lines[40 - 1][28:]
                elif (pos == "LR"):
                    lines[40 - 1] = lines[40 - 1][:30] + "1" + lines[40 - 1][31:]
                elif (pos == "CL"):
                    lines[40 - 1] = lines[40 - 1][:33] + "1" + lines[40 - 1][34:]
                elif (pos == "C"):
                    lines[40 - 1] = lines[40 - 1][:36] + "1" + lines[40 - 1][37:]
                elif (pos == "CR"):
                    lines[40 - 1] = lines[40 - 1][:39] + "1" + lines[40 - 1][40:]
                elif (pos == "RL"):
                    lines[40 - 1] = lines[40 - 1][:42] + "1" + lines[40 - 1][43:]
                elif (pos == "R"):
                    lines[40 - 1] = lines[40 - 1][:45] + "1" + lines[40 - 1][46:]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_middef_line] = lines[atk_middef_line] + f"[pos[{pos}] == 1]MidDef({sp}, {lp},{prob_to_lose_away_middeffielders}, {aggression_away_middeffielders}, {pos})"
                    lines[atk_freekick_middef_line] = lines[atk_freekick_middef_line] + f"[pos[{pos}] == 1]FKMidDef({freekick_middef_home}, {pos})"
                else:
                    lines[atk_middef_line] = lines[atk_middef_line] + f"[] [pos[{pos}] == 1]MidDef({sp}, {lp},{prob_to_lose_away_middeffielders}, {aggression_away_middeffielders}, {pos})"
                    lines[atk_freekick_middef_line] = lines[atk_freekick_middef_line] + f"[] [pos[{pos}] == 1]FKMidDef({freekick_middef_home}, {pos})"
            lines[atk_middef_line] = lines[atk_middef_line] + ";"
            lines[atk_freekick_middef_line] = lines[atk_freekick_middef_line] + ";"
            return lines

def softmax(z):
    """Compute softmax values for each sets of scores in z."""
    exponents = [math.exp(value) for value in z]
    exp_sum = sum(exponents)
    return [exp_value / exp_sum for exp_value in exponents]
