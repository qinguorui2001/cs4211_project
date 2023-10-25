import pandas as pd
import sys
import os
from math import ceil,exp
import subprocess
from openpyxl import Workbook
#Create probability for every season
def readfile(season):
    df_match = pd.read_csv(f"matches/epl_matches_{season}.csv")
    df_ratings = pd.read_csv(f"eplratings/epl_ratings_{season}.csv")
    template_file_3f = '3rowTemplate.pcsp'
    template_file_4f = '4rowsTemplate.pcsp'

    # Verify input file
    if not os.path.isfile(template_file_3f):
        print("error: {} does not exist".format(template_file_3f))
        sys.exit(1)
    if not os.path.isfile(template_file_4f):
        print("error: {} does not exist".format(template_file_4f))
        sys.exit(1)
    
    match_url_arr = []
    
    # Generate PCSP files
    for index, row in df_match.iterrows():
        #define row values for current row
        match_url = row['match_url'] #read from column 'match url'
        match_url_arr.append(match_url)
        home = row['home_team']
        away = row['away_team']
        # Print out match index and teams for debugging
        print( f"Doing match {index + 1}: {home} vs {away}, match_url: {match_url}")
        home_fmn = row['home_formation']
        away_fmn = row['away_formation']
        home_team = row['home_xi_names']
        away_team = row['away_xi_names']
        home_seq = row['home_sequence']
        away_seq = row['away_sequence']
        #define whether it is 3 levels i.e 4-3-3/4-5-1... ,or 4 levels i.e 4-2-3-1/4-4-1-1...
        is3levels_home = False
        is4levels_home = False
        is3levels_away = False
        is4levels_away = False
        #instantiate
        def_H,mid_H = 0 #for 3 levels, Home
        def_4H, midDef_4H, mid_4H = 0 #for 4 levels Home, in this case def_4H replaces mid_H
        def_A,mid_A = 0 #for 3 levels, Home
        def_4A,midDef_4A, mid_4A = 0 #for 4 levels Away, in this case def_4A replaces mid_A
        #address formatting issue for formations
        if "/" in home_fmn: #means 3 levels
            #print("Is 3 levels Home")
            is3levels_home = True
            posArray = home_fmn.split('/')
            def_H,mid_H = posArray[0],posArray[1]
        else: #means 4 levels
            #print("Is 4 levels")
            is4levels_home = True
            posArray = home_fmn.split('/')
            def_4H,midDef_4H, mid_4H = posArray[0],posArray[1],posArray[2]
           
        if "/" in away_fmn: #means 3 levels
            is3levels_away = True
            posArray = away_fmn.split('/')
            def_A,mid_A,for_A = posArray[0],posArray[1],int(posArray[2]) - 2000 
        else: #means 4 levels
            is4levels_away = True
            posArray = away_fmn.split('/')
            def_4A,midDef_4A, mid_4A,for_4A = posArray[0],posArray[1],posArray[2], posArray[3]
        
        if (is3levels_home and is3levels_away):
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperNameHome = home_team[0]
            defenderPositionsHome = homePositions[1:def_H]
            defenderNamesHome = home_team[1:def_H]
            midfielderPositionsHome = homePositions[def_H:def_H +mid_H]
            midfielderNamesHome = home_team[def_H:def_H +mid_H]
            forwardPositionsHome = homePositions[def_H+mid_H:]
            forwardNamesHome = home_team[def_H+mid_H:]
            
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperNameAway = away_team[0]
            defenderPositionsAway = awayPositions[1:def_A]
            defenderNamesAway = away_team[1:def_A]
            midfielderPositionsAway = awayPositions[def_A:def_A +mid_A]
            midfielderNamesAway = away_team[def_A:def_A +mid_A]
            forwardPositionsAway = awayPositions[def_A+mid_A:]
            forwardNamesAway = away_team[def_A + mid_A:]
            ##generate home pcsp file using 3 levels template
            
            #first create the home pcsp file from the template file
            out_file = f"pcspDir//{home}{away}{season}.pcsp"
            open(out_file,'w').close() #creates the file
            with open(template_file_3f, 'r') as fp_in, open(out_file, 'w') as fp_out: #copy template file to out file
                for line in fp_in:
                    fp_out.write(line)
            with open(out_file, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
            
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            #TODO modify Goalkeeper ratings in pcsp file
            #home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home)].values
            gk_home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) and (df_ratings['long_name'] == goalkeeperNameHome)].values
            short_pass_rating = gk_home_ratings_row[0]['short_passing']
            long_pass_rating = gk_home_ratings_row[0]['long_passing']
            gk_away_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) and (df_ratings['long_name'] == goalkeeperNameAway)].values
            gk_handling_rating = gk_away_ratings_row[0]['gk_handling']
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
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({gk_handling_rating}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating
            no_of_forwards = len(forwardNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_forwards):
                away_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == forwardNamesAway[ind])].values
                interception_ratings = away_forward_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_forward_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_forward_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_forward_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_forwards = math.ceil(combined_ratings / no_of_forwards)
            aggression_away_forwards = math.ceil(aggression_ratings / no_of_forwards)
            
            # Calculate probability to lose posession to away team midfielders
            no_of_midfielders = len(midfielderNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_midfielders):
                away_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midfielderNamesAway[ind])].values
                interception_ratings = away_midfielder_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_midfielder_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_midfielder_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_midfielder_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_midfielders = math.ceil(combined_ratings / no_of_midfielders)
            aggression_away_midfielders = math.ceil(aggression_ratings / no_of_midfielders)
            
            # Calculate probability to lose posession to away team defenders
            no_of_defenders = len(defenderNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_defenders):
                away_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == defenderNamesAway[ind])].values
                interception_ratings = away_defender_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_defender_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_defender_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_defender_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_defenders = math.ceil(combined_ratings / no_of_defenders)
            aggression_away_defenders = math.ceil(aggression_ratings / no_of_defenders)
            
            freekick_def_home = 0
            for ind in range(len(defenderNamesHome)):
                home_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                lp = home_defender_ratings_row[0]['long_passing']
                freekick_def_home = freekick_def_home + int(lp)
            freekick_def_home = math.ceil(freekick_def_home / len(defenderNamesHome))
            
            freekick_mid_home = 0
            for ind in range(len(midfielderNamesHome)):
                home_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midfielderNamesHome[ind])].values
                fk = home_midfielder_ratings_row[0]['skill_fk_accuracy']
                freekick_mid_home = freekick_mid_home + int(fk)
            freekick_mid_home = math.ceil(freekick_mid_home / len(midfielderNamesHome))
            
            freekick_for_home = 0
            for ind in range(len(forwardNamesHome)):
                home_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == forwardNamesHome[ind])].values
                fk = home_forward_ratings_row[0]['skill_fk_accuracy']
                freekick_for_home = freekick_for_home + int(fk)
            freekick_for_home = math.ceil(freekick_for_home / len(forwardNamesHome))
            
            lines[atk_def_line] = "AtkDef = "
            lines[atk_freekick_def_line] = "AtkFreeKickDef = "
            for ind,pos in enumerate(defenderPositionsHome):
                def_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                sp = def_ratings_row[0]['short_passing']
                lp = def_ratings_row[0]['long_passing']
                if (pos == "L"):
                    lines[39 - 1] = lines[39 - 1][24:] + "1" + lines[39 - 1][:25]
                elif (pos == "LR"):
                    lines[39 - 1] = lines[39 - 1][27:] + "1" + lines[39 - 1][:28]
                elif (pos == "CL"):
                    lines[39 - 1] = lines[39 - 1][30:] + "1" + lines[39 - 1][:31]
                elif (pos == "C"):
                    lines[39 - 1] = lines[39 - 1][33:] + "1" + lines[39 - 1][:34]
                elif (pos == "CR"):
                    lines[39 - 1] = lines[39 - 1][36:] + "1" + lines[39 - 1][:37]
                elif (pos == "RL"):
                    lines[39 - 1] = lines[39 - 1][39:] + "1" + lines[39 - 1][:40]
                elif (pos == "R"):
                    lines[39 - 1] = lines[39 - 1][42:] + "1" + lines[39 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_def_line] = lines[atk_def_line] + f"[pos[{pos}] == 1]Def({sp, lp, prob_to_lose_away_forwards, aggression_away_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[pos[{pos}] == 1]FKDef({freekick_def_home, pos})"
                else:
                    lines[atk_def_line] = lines[atk_def_line] + f"[] [pos[{pos}] == 1]Def({sp, lp, prob_to_lose_away_forwards, aggression_away_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[] [pos[{pos}] == 1]FKDef({freekick_def_home, pos})"

            lines[atk_mid_line] = "AtkMid = "
            lines[atk_freekick_mid_line] = "AtkFreeKickMid = "
            for ind,pos in enumerate(midfielderPositionsHome):
                #TODO modify midfielder ratings in pcsp file
                mid_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midfielderNamesHome[ind])].values
                sp = mid_ratings_row[0]['attacking_short_passing']
                lp = mid_ratings_row[0]['attacking_long_passing']
                ls = mid_ratings_row[0]['power_long_shots']
                if (pos == "L"):
                    lines[40 - 1] = lines[40 - 1][24:] + "1" + lines[40 - 1][:25]
                elif (pos == "LR"):
                    lines[40 - 1] = lines[40 - 1][27:] + "1" + lines[40 - 1][:28]
                elif (pos == "CL"):
                    lines[40 - 1] = lines[40 - 1][30:] + "1" + lines[40 - 1][:31]
                elif (pos == "C"):
                    lines[40 - 1] = lines[40 - 1][33:] + "1" + lines[40 - 1][:34]
                elif (pos == "CR"):
                    lines[40 - 1] = lines[40 - 1][36:] + "1" + lines[40 - 1][:37]
                elif (pos == "RL"):
                    lines[40 - 1] = lines[40 - 1][39:] + "1" + lines[40 - 1][:40]
                elif (pos == "R"):
                    lines[40 - 1] = lines[40 - 1][42:] + "1" + lines[40 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[pos[{pos}] == 1]Mid({sp, lp, ls,prob_to_lose_away_midfielders, aggression_away_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[pos[{pos}] == 1]FKMid({freekick_mid_home, pos})"
                else:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[] [pos[{pos}] == 1]Mid({sp, lp,ls, prob_to_lose_away_midfielders, aggression_away_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[] [pos[{pos}] == 1]FKMid({freekick_mid_home, pos})"
            for ind,pos in enumerate(forwardPositionsHome):
            #TODO modify forward ratings in pcsp file
                for_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == forwardNamesHome[ind])].values
                sp = for_ratings_row[0]['attacking_short_passing']
                lp = for_ratings_row[0]['attacking_long_passing']
                ls = for_ratings_row[0]['power_long_shots']
                fi = for_ratings_row[0]['attacking_finishing']
                vo = for_ratings_row[0]['attacking_volleys']
                dr = for_ratings_row[0]['skill_dribbling']
                he = for_ratings_row[0]['attacking_heading_accuracy']
                if (pos == "L"):
                    lines[41 - 1] = lines[41 - 1][24:] + "1" + lines[41 - 1][:25]
                    lines[91 - 1] = lines[91 - 1][24:] + "4" + lines[91 - 1][:25]
                elif (pos == "LR"):
                    lines[41 - 1] = lines[41 - 1][27:] + "1" + lines[41 - 1][:28]
                    lines[91 - 1] = lines[91 - 1][27:] + "4" + lines[91 - 1][:28]
                elif (pos == "CL"):
                    lines[41 - 1] = lines[41 - 1][30:] + "1" + lines[41 - 1][:31]
                    lines[91 - 1] = lines[91 - 1][30:] + "4" + lines[91 - 1][:31]
                elif (pos == "C"):
                    lines[41 - 1] = lines[41 - 1][33:] + "1" + lines[41 - 1][:34]
                    lines[91 - 1] = lines[91 - 1][33:] + "4" + lines[91 - 1][:34]
                elif (pos == "CR"):
                    lines[41 - 1] = lines[41 - 1][36:] + "1" + lines[41 - 1][:37]
                    lines[91 - 1] = lines[91 - 1][36:] + "4" + lines[91 - 1][:37]
                elif (pos == "RL"):
                    lines[41 - 1] = lines[41 - 1][39:] + "1" + lines[41 - 1][:40]
                    lines[91 - 1] = lines[91 - 1][39:] + "4" + lines[91 - 1][:40]
                elif (pos == "R"):
                    lines[41 - 1] = lines[41 - 1][42:] + "1" + lines[41 - 1][:43]
                    lines[91 - 1] = lines[91 - 1][42:] + "1" + lines[91 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_for_line] = lines[atk_for_line] + f"[pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr,prob_to_lose_away_defenders, aggression_away_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[pos[{pos}] == 1]FKFor({freekick_for_home, pos})"
                else:
                    lines[atk_for_line] = lines[atk_for_line] + f"[] [pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr, prob_to_lose_away_defenders, aggression_away_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[] [pos[{pos}] == 1]FKFor({freekick_for_home, pos})"
            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         
            #then create the away pcsp file from the template file
            out_file = f"path/to/output/{away}{home}{season}.pcsp"
            open(out_file,'w').close() #creates the file
            with open(template_file_3f, 'r') as fp_in, open(out_file, 'w') as fp_out: #copy template file to out file
                for line in fp_in:
                    fp_out.write(line)
            with open(out_file, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
            
            # Calculate probability to lose posession to home team forwards
            # Calculate also the aggression rating
            no_of_forwards = len(forwardNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_forwards):
                home_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == forwardNamesHome[ind])].values
                interception_ratings = home_forward_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = home_forward_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = home_forward_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(home_forward_ratings_row[0]['mentality_aggression'])
            prob_to_lose_home_forwards = math.ceil(combined_ratings / no_of_forwards)
            aggression_home_forwards = math.ceil(aggression_ratings / no_of_forwards)
            
            # Calculate probability to lose posession to home team midfielders
            no_of_midfielders = len(midfielderNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_midfielders):
                home_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midfielderNamesHome[ind])].values
                interception_ratings = home_midfielder_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = home_midfielder_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = home_midfielder_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(home_midfielder_ratings_row[0]['mentality_aggression'])
            prob_to_lose_home_midfielders = math.ceil(combined_ratings / no_of_midfielders)
            aggression_home_midfielders = math.ceil(aggression_ratings / no_of_midfielders)
            
            # Calculate probability to lose posession to home team defenders
            no_of_defenders = len(defenderNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_defenders):
                home_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                interception_ratings = home_defender_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = home_defender_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = home_defender_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(home_defender_ratings_row[0]['mentality_aggression'])
            prob_to_lose_home_defenders = math.ceil(combined_ratings / no_of_defenders)
            aggression_home_defenders = math.ceil(aggression_ratings / no_of_defenders)
            
            freekick_def_away = 0
            for ind in range(len(defenderNamesAway)):
                away_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == defenderNamesAway[ind])].values
                lp = away_defender_ratings_row[0]['long_passing']
                freekick_def_away = freekick_def_away + int(lp)
            freekick_def_away = math.ceil(freekick_def_away / len(defenderNamesAway))
            
            freekick_mid_away = 0
            for ind in range(len(midfielderNamesAway)):
                away_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midfielderNamesAway[ind])].values
                fk = away_midfielder_ratings_row[0]['skill_fk_accuracy']
                freekick_mid_away = freekick_mid_away + int(fk)
            freekick_mid_away = math.ceil(freekick_mid_away / len(midfielderNamesAway))
            
            freekick_for_away = 0
            for ind in range(len(forwardNamesAway)):
                away_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == forwardNamesAway[ind])].values
                fk = away_forward_ratings_row[0]['skill_fk_accuracy']
                freekick_for_away = freekick_for_away + int(fk)
            freekick_for_away = math.ceil(freekick_for_away / len(forwardNamesAway))
            
            lines[atk_def_line] = "AtkDef = "
            lines[atk_freekick_def_line] = "AtkFreeKickDef = "
            for ind,pos in enumerate(defenderPositionsAway):
                def_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == defenderNamesAway[ind])].values
                sp = def_ratings_row[0]['short_passing']
                lp = def_ratings_row[0]['long_passing']
                if (pos == "L"):
                    lines[39 - 1] = lines[39 - 1][24:] + "1" + lines[39 - 1][:25]
                elif (pos == "LR"):
                    lines[39 - 1] = lines[39 - 1][27:] + "1" + lines[39 - 1][:28]
                elif (pos == "CL"):
                    lines[39 - 1] = lines[39 - 1][30:] + "1" + lines[39 - 1][:31]
                elif (pos == "C"):
                    lines[39 - 1] = lines[39 - 1][33:] + "1" + lines[39 - 1][:34]
                elif (pos == "CR"):
                    lines[39 - 1] = lines[39 - 1][36:] + "1" + lines[39 - 1][:37]
                elif (pos == "RL"):
                    lines[39 - 1] = lines[39 - 1][39:] + "1" + lines[39 - 1][:40]
                elif (pos == "R"):
                    lines[39 - 1] = lines[39 - 1][42:] + "1" + lines[39 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_def_line] = lines[atk_def_line] + f"[pos[{pos}] == 1]Def({sp, lp, prob_to_lose_home_forwards, aggression_home_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[pos[{pos}] == 1]FKDef({freekick_def_away, pos})"
                else:
                    lines[atk_def_line] = lines[atk_def_line] + f"[] [pos[{pos}] == 1]Def({sp, lp, prob_to_lose_home_forwards, aggression_home_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[] [pos[{pos}] == 1]FKDef({freekick_def_away, pos})"

            lines[atk_mid_line] = "AtkMid = "
            lines[atk_freekick_mid_line] = "AtkFreeKickMid = "
            for ind,pos in enumerate(midfielderPositionsAway):
                #TODO modify midfielder ratings in pcsp file
                mid_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midfielderNamesAway[ind])].values
                sp = mid_ratings_row[0]['attacking_short_passing']
                lp = mid_ratings_row[0]['attacking_long_passing']
                ls = mid_ratings_row[0]['power_long_shots']
                if (pos == "L"):
                    lines[40 - 1] = lines[40 - 1][24:] + "1" + lines[40 - 1][:25]
                elif (pos == "LR"):
                    lines[40 - 1] = lines[40 - 1][27:] + "1" + lines[40 - 1][:28]
                elif (pos == "CL"):
                    lines[40 - 1] = lines[40 - 1][30:] + "1" + lines[40 - 1][:31]
                elif (pos == "C"):
                    lines[40 - 1] = lines[40 - 1][33:] + "1" + lines[40 - 1][:34]
                elif (pos == "CR"):
                    lines[40 - 1] = lines[40 - 1][36:] + "1" + lines[40 - 1][:37]
                elif (pos == "RL"):
                    lines[40 - 1] = lines[40 - 1][39:] + "1" + lines[40 - 1][:40]
                elif (pos == "R"):
                    lines[40 - 1] = lines[40 - 1][42:] + "1" + lines[40 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[pos[{pos}] == 1]Mid({sp, lp, ls,prob_to_lose_home_midfielders, aggression_home_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[pos[{pos}] == 1]FKMid({freekick_mid_away, pos})"
                else:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[] [pos[{pos}] == 1]Mid({sp, lp,ls, prob_to_lose_home_midfielders, aggression_home_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[] [pos[{pos}] == 1]FKMid({freekick_mid_away, pos})"
            for ind,pos in enumerate(forwardPositionsAway):
            #TODO modify forward ratings in pcsp file
                for_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == forwardNamesAway[ind])].values
                sp = for_ratings_row[0]['attacking_short_passing']
                lp = for_ratings_row[0]['attacking_long_passing']
                ls = for_ratings_row[0]['power_long_shots']
                fi = for_ratings_row[0]['attacking_finishing']
                vo = for_ratings_row[0]['attacking_volleys']
                dr = for_ratings_row[0]['skill_dribbling']
                he = for_ratings_row[0]['attacking_heading_accuracy']
                if (pos == "L"):
                    lines[41 - 1] = lines[41 - 1][24:] + "1" + lines[41 - 1][:25]
                    lines[91 - 1] = lines[91 - 1][24:] + "4" + lines[91 - 1][:25]
                elif (pos == "LR"):
                    lines[41 - 1] = lines[41 - 1][27:] + "1" + lines[41 - 1][:28]
                    lines[91 - 1] = lines[91 - 1][27:] + "4" + lines[91 - 1][:28]
                elif (pos == "CL"):
                    lines[41 - 1] = lines[41 - 1][30:] + "1" + lines[41 - 1][:31]
                    lines[91 - 1] = lines[91 - 1][30:] + "4" + lines[91 - 1][:31]
                elif (pos == "C"):
                    lines[41 - 1] = lines[41 - 1][33:] + "1" + lines[41 - 1][:34]
                    lines[91 - 1] = lines[91 - 1][33:] + "4" + lines[91 - 1][:34]
                elif (pos == "CR"):
                    lines[41 - 1] = lines[41 - 1][36:] + "1" + lines[41 - 1][:37]
                    lines[91 - 1] = lines[91 - 1][36:] + "4" + lines[91 - 1][:37]
                elif (pos == "RL"):
                    lines[41 - 1] = lines[41 - 1][39:] + "1" + lines[41 - 1][:40]
                    lines[91 - 1] = lines[91 - 1][39:] + "4" + lines[91 - 1][:40]
                elif (pos == "R"):
                    lines[41 - 1] = lines[41 - 1][42:] + "1" + lines[41 - 1][:43]
                    lines[91 - 1] = lines[91 - 1][42:] + "1" + lines[91 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_for_line] = lines[atk_for_line] + f"[pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr,prob_to_lose_home_defenders, aggression_home_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[pos[{pos}] == 1]FKFor({freekick_for_away, pos})"
                else:
                    lines[atk_for_line] = lines[atk_for_line] + f"[] [pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr, prob_to_lose_home_defenders, aggression_home_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[] [pos[{pos}] == 1]FKFor({freekick_for_away, pos})"
            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)

        else if (is4levels_home and is4levels_away):
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperNameHome = home_team[0]
            defenderPositionsHome = homePositions[1:def_4H]
            defenderNamesHome = home_team[1:def_4H]
            midDefPositionsHome = homePositions[def_4H:def_4H +midDef_4H]
            midDefNamesHome = home_team[def_4H:def_4H +midDef_4H]
            midfielderPositionsHome = homePositions[def_4H + midDef_4H:def_4H +midDef_4H + mid_4H]
            midfielderNamesHome = home_team[def_4H + midDef_4H:def_4H +midDef_4H + mid_4H]
            forwardPositionsHome = homePositions[def_4H +midDef_4H + mid_4H:]
            forwardNamesHome = home_team[def_4H +midDef_4H + mid_4H:]
            
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperNameAway = away_team[0]
            defenderPositionsAway = awayPositions[1:def_4A]
            defenderNamesAway = away_team[1:def_4A]
            midDefPositionsAway = awayPositions[def_4A:def_4A +midDef_4A]
            midDefNamesAway = away_team[def_4A:def_4A +midDef_4A]
            midfielderPositionsAway = awayPositions[def_4A +midDef_4A:def_4A +midDef_4A +mid_4A]
            midfielderNamesAway = away_team[def_4A:def_4A +midDef_4A +mid_4A]
            forwardPositionsAway = awayPositions[def_4A +midDef_4A +mid_4A:]
            forwardNamesAway = away_team[def_4A +midDef_4A +mid_4A:]
            
            #first create the home pcsp file from the template file
            out_file = f"pcspDir\\{home}{away}{season}.pcsp"
            open(out_file,'w').close() #creates the file
            with open(template_file_4f, 'r') as fp_in, open(out_file, 'w') as fp_out: #copy template file to out file
                for line in fp_in:
                    fp_out.write(line)
            with open(out_file, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
            
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            #TODO modify Goalkeeper ratings in pcsp file
            #home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home)].values
            gk_home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) and (df_ratings['long_name'] == goalkeeperNameHome)].values
            short_pass_rating = gk_home_ratings_row[0]['short_passing']
            long_pass_rating = gk_home_ratings_row[0]['long_passing']
            gk_away_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) and (df_ratings['long_name'] == goalkeeperNameAway)].values
            gk_handling_rating = gk_away_ratings_row[0]['gk_handling']
            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line = 50 - 1
            atk_def_line = 56 - 1
            atk_freekick_def_line = 58 - 1
            atk_middef_line = 67 - 1
            atk_freekick_middef_line = 69 - 1
            atk_mid_line = 72 - 1
            atk_freekick_mid_line = 74 - 1
            atk_for_line = 77 - 1
            atk_freekick_for_line = 78 - 1
            def_kep_line = 82 - 1
            distToKep_line = 96 - 1
            # Update the rating of the AtkKep row
            lines[atk_kep_line] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({gk_handling_rating}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating
            no_of_forwards = len(forwardNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_forwards):
                away_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == forwardNamesAway[ind])].values
                interception_ratings = away_forward_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_forward_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_forward_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_forward_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_forwards = math.ceil(combined_ratings / no_of_forwards)
            aggression_away_forwards = math.ceil(aggression_ratings / no_of_forwards)
            
            # Calculate probability to lose posession to away team midfielders
            no_of_middeffielders = len(midDefNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_middeffielders):
                away_middef_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midDefNamesAway[ind])].values
                interception_ratings = away_middef_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_middef_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_middef_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_middef_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_middeffielders = math.ceil(combined_ratings / no_of_middeffielders)
            aggression_away_middeffielders = math.ceil(aggression_ratings / no_of_middeffielders)
            
            # Calculate probability to lose posession to away team defensive midfielders
            no_of_midfielders = len(midfielderNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_midfielders):
                away_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midfielderNamesAway[ind])].values
                interception_ratings = away_midfielder_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_midfielder_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_midfielder_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_midfielder_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_midfielders = math.ceil(combined_ratings / no_of_midfielders)
            aggression_away_midfielders = math.ceil(aggression_ratings / no_of_midfielders)
            
            # Calculate probability to lose posession to away team defenders
            no_of_defenders = len(defenderNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_defenders):
                away_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == defenderNamesAway[ind])].values
                interception_ratings = away_defender_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_defender_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_defender_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_defender_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_defenders = math.ceil(combined_ratings / no_of_defenders)
            aggression_away_defenders = math.ceil(aggression_ratings / no_of_defenders)
            
            freekick_def_home = 0
            for ind in range(len(defenderNamesHome)):
                home_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                lp = home_defender_ratings_row[0]['attacking_long_passing']
                freekick_def_home = freekick_def_home + int(lp)
            freekick_def_home = math.ceil(freekick_def_home / len(defenderNamesHome))
            
            freekick_middef_home = 0
            for ind in range(len(midDefNamesHome)):
                home_middeffielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midDefNamesHome[ind])].values
                fk = home_middeffielder_ratings_row[0]['attacking_long_passing']
                freekick_middef_home = freekick_middef_home + int(fk)
            freekick_middef_home = math.ceil(freekick_middef_home / len(midDefNamesHome))
            
            freekick_mid_home = 0
            for ind in range(len(midfielderNamesHome)):
                home_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midfielderNamesHome[ind])].values
                fk = home_midfielder_ratings_row[0]['skill_fk_accuracy']
                freekick_mid_home = freekick_mid_home + int(fk)
            freekick_mid_home = math.ceil(freekick_mid_home / len(midfielderNamesHome))
            
            freekick_for_home = 0
            for ind in range(len(forwardNamesHome)):
                home_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == forwardNamesHome[ind])].values
                fk = home_forward_ratings_row[0]['skill_fk_accuracy']
                freekick_for_home = freekick_for_home + int(fk)
            freekick_for_home = math.ceil(freekick_for_home / len(forwardNamesHome))
            
            lines[atk_def_line] = "AtkDef = "
            lines[atk_freekick_def_line] = "AtkFreeKickDef = "
            for ind,pos in enumerate(defenderPositionsHome):
                def_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                sp = def_ratings_row[0]['attacking_short_passing']
                lp = def_ratings_row[0]['attacking_long_passing']
                if (pos == "L"):
                    lines[39 - 1] = lines[39 - 1][24:] + "1" + lines[39 - 1][:25]
                elif (pos == "LR"):
                    lines[39 - 1] = lines[39 - 1][27:] + "1" + lines[39 - 1][:28]
                elif (pos == "CL"):
                    lines[39 - 1] = lines[39 - 1][30:] + "1" + lines[39 - 1][:31]
                elif (pos == "C"):
                    lines[39 - 1] = lines[39 - 1][33:] + "1" + lines[39 - 1][:34]
                elif (pos == "CR"):
                    lines[39 - 1] = lines[39 - 1][36:] + "1" + lines[39 - 1][:37]
                elif (pos == "RL"):
                    lines[39 - 1] = lines[39 - 1][39:] + "1" + lines[39 - 1][:40]
                elif (pos == "R"):
                    lines[39 - 1] = lines[39 - 1][42:] + "1" + lines[39 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_def_line] = lines[atk_def_line] + f"[pos[{pos}] == 1]Def({sp, lp, prob_to_lose_away_forwards, aggression_away_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[pos[{pos}] == 1]FKDef({freekick_def_home, pos})"
                else:
                    lines[atk_def_line] = lines[atk_def_line] + f"[] [pos[{pos}] == 1]Def({sp, lp, prob_to_lose_away_forwards, aggression_away_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[] [pos[{pos}] == 1]FKDef({freekick_def_home, pos})"
            
            lines[atk_middef_line] = "AtkMidDef = "
            lines[atk_freekick_middef_line] = "AtkFreeKickMidDef = "
            for ind,pos in enumerate(midDefPositionsHome):
                #TODO modify midfielder ratings in pcsp file
                middef_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midDefNamesHome[ind])].values
                sp = middef_ratings_row[0]['attacking_short_passing']
                lp = middef_ratings_row[0]['attacking_long_passing']
                if (pos == "L"):
                    lines[40 - 1] = lines[40 - 1][24:] + "1" + lines[40 - 1][:25]
                elif (pos == "LR"):
                    lines[40 - 1] = lines[40 - 1][27:] + "1" + lines[40 - 1][:28]
                elif (pos == "CL"):
                    lines[40 - 1] = lines[40 - 1][30:] + "1" + lines[40 - 1][:31]
                elif (pos == "C"):
                    lines[40 - 1] = lines[40 - 1][33:] + "1" + lines[40 - 1][:34]
                elif (pos == "CR"):
                    lines[40 - 1] = lines[40 - 1][36:] + "1" + lines[40 - 1][:37]
                elif (pos == "RL"):
                    lines[40 - 1] = lines[40 - 1][39:] + "1" + lines[40 - 1][:40]
                elif (pos == "R"):
                    lines[40 - 1] = lines[40 - 1][42:] + "1" + lines[40 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_middef_line] = lines[atk_middef_line] + f"[pos[{pos}] == 1]MidDef({sp, lp, prob_to_lose_away_middeffielders, aggression_away_middeffielders, pos})"
                    lines[atk_freekick_middef_line] = lines[atk_freekick_middef_line] + f"[pos[{pos}] == 1]FKMidDef({freekick_middef_home, pos})"
                else:
                    lines[atk_middef_line] = lines[atk_middef_line] + f"[] [pos[{pos}] == 1]MidDef({sp, lp,prob_to_lose_away_middeffielders, aggression_away_middeffielders, pos})"
                    lines[atk_freekick_middef_line] = lines[atk_freekick_middef_line] + f"[] [pos[{pos}] == 1]FKMidDef({freekick_middef_home, pos})"
            
            lines[atk_mid_line] = "AtkMid = "
            lines[atk_freekick_mid_line] = "AtkFreeKickMid = "
            for ind,pos in enumerate(midfielderPositionsHome):
                #TODO modify midfielder ratings in pcsp file
                mid_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midfielderNamesHome[ind])].values
                sp = mid_ratings_row[0]['attacking_short_passing']
                lp = mid_ratings_row[0]['attacking_long_passing']
                ls = mid_ratings_row[0]['power_long_shots']
                if (pos == "L"):
                    lines[41 - 1] = lines[41 - 1][24:] + "1" + lines[41 - 1][:25]
                elif (pos == "LR"):
                    lines[41 - 1] = lines[41 - 1][27:] + "1" + lines[41 - 1][:28]
                elif (pos == "CL"):
                    lines[41 - 1] = lines[41 - 1][30:] + "1" + lines[41 - 1][:31]
                elif (pos == "C"):
                    lines[41 - 1] = lines[41 - 1][33:] + "1" + lines[41 - 1][:34]
                elif (pos == "CR"):
                    lines[41 - 1] = lines[41 - 1][36:] + "1" + lines[41 - 1][:37]
                elif (pos == "RL"):
                    lines[41 - 1] = lines[41 - 1][39:] + "1" + lines[41 - 1][:40]
                elif (pos == "R"):
                    lines[41 - 1] = lines[41 - 1][42:] + "1" + lines[41 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[pos[{pos}] == 1]Mid({sp, lp, ls,prob_to_lose_away_midfielders, aggression_away_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[pos[{pos}] == 1]FKMid({freekick_mid_home, pos})"
                else:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[] [pos[{pos}] == 1]Mid({sp, lp,ls, prob_to_lose_away_midfielders, aggression_away_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[] [pos[{pos}] == 1]FKMid({freekick_mid_home, pos})"
            for ind,pos in enumerate(forwardPositionsHome):
            #TODO modify forward ratings in pcsp file
                for_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == forwardNamesHome[ind])].values
                sp = for_ratings_row[0]['attacking_short_passing']
                lp = for_ratings_row[0]['attacking_long_passing']
                ls = for_ratings_row[0]['power_long_shots']
                fi = for_ratings_row[0]['attacking_finishing']
                vo = for_ratings_row[0]['attacking_volleys']
                dr = for_ratings_row[0]['skill_dribbling']
                he = for_ratings_row[0]['attacking_heading_accuracy']
                if (pos == "L"):
                    lines[42 - 1] = lines[42 - 1][24:] + "1" + lines[42 - 1][:25]
                    lines[96 - 1] = lines[96 - 1][24:] + "4" + lines[96 - 1][:25]
                elif (pos == "LR"):
                    lines[42 - 1] = lines[42 - 1][27:] + "1" + lines[42 - 1][:28]
                    lines[96 - 1] = lines[96 - 1][27:] + "4" + lines[96 - 1][:28]
                elif (pos == "CL"):
                    lines[42 - 1] = lines[42 - 1][30:] + "1" + lines[42 - 1][:31]
                    lines[96 - 1] = lines[96 - 1][30:] + "4" + lines[96 - 1][:31]
                elif (pos == "C"):
                    lines[42 - 1] = lines[42 - 1][33:] + "1" + lines[42 - 1][:34]
                    lines[96 - 1] = lines[96 - 1][33:] + "4" + lines[96 - 1][:34]
                elif (pos == "CR"):
                    lines[42 - 1] = lines[42 - 1][36:] + "1" + lines[42 - 1][:37]
                    lines[96 - 1] = lines[96 - 1][36:] + "4" + lines[96 - 1][:37]
                elif (pos == "RL"):
                    lines[42 - 1] = lines[42 - 1][39:] + "1" + lines[42 - 1][:40]
                    lines[96 - 1] = lines[96 - 1][39:] + "4" + lines[96 - 1][:40]
                elif (pos == "R"):
                    lines[42 - 1] = lines[42 - 1][42:] + "1" + lines[42 - 1][:43]
                    lines[96 - 1] = lines[96 - 1][42:] + "1" + lines[96 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_for_line] = lines[atk_for_line] + f"[pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr,prob_to_lose_away_defenders, aggression_away_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[pos[{pos}] == 1]FKFor({freekick_for_home, pos})"
                else:
                    lines[atk_for_line] = lines[atk_for_line] + f"[] [pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr, prob_to_lose_away_defenders, aggression_away_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[] [pos[{pos}] == 1]FKFor({freekick_for_home, pos})"
            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         
            #then create the away pcsp file from the template file
            out_file = f"pcspDir\\{away}{home}{season}.pcsp"
            open(out_file,'w').close() #creates the file
            with open(template_file_4f, 'r') as fp_in, open(out_file, 'w') as fp_out: #copy template file to out file
                for line in fp_in:
                    fp_out.write(line)
            with open(out_file, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
            
            # Calculate probability to lose posession to home team forwards
            # Calculate also the aggression rating
            no_of_forwards = len(forwardNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_forwards):
                home_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == forwardNamesHome[ind])].values
                interception_ratings = home_forward_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = home_forward_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = home_forward_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(home_forward_ratings_row[0]['mentality_aggression'])
            prob_to_lose_home_forwards = math.ceil(combined_ratings / no_of_forwards)
            aggression_home_forwards = math.ceil(aggression_ratings / no_of_forwards)
            
            # Calculate probability to lose posession to home team midfielders
            no_of_midfielders = len(midfielderNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_midfielders):
                home_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midfielderNamesHome[ind])].values
                interception_ratings = home_midfielder_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = home_midfielder_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = home_midfielder_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(home_midfielder_ratings_row[0]['mentality_aggression'])
            prob_to_lose_home_midfielders = math.ceil(combined_ratings / no_of_midfielders)
            aggression_home_midfielders = math.ceil(aggression_ratings / no_of_midfielders)
            
            # Calculate probability to lose posession to away team midfielders
            no_of_middeffielders = len(midDefNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_middeffielders):
                away_middef_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midDefNamesHome[ind])].values
                interception_ratings = away_middef_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_middef_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_middef_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_middef_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_middeffielders = math.ceil(combined_ratings / no_of_middeffielders)
            aggression_away_middeffielders = math.ceil(aggression_ratings / no_of_middeffielders)
            
            # Calculate probability to lose posession to home team defenders
            no_of_defenders = len(defenderNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_defenders):
                home_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                interception_ratings = home_defender_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = home_defender_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = home_defender_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(home_defender_ratings_row[0]['mentality_aggression'])
            prob_to_lose_home_defenders = math.ceil(combined_ratings / no_of_defenders)
            aggression_home_defenders = math.ceil(aggression_ratings / no_of_defenders)
            
            freekick_def_away = 0
            for ind in range(len(defenderNamesAway)):
                away_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == defenderNamesAway[ind])].values
                lp = away_defender_ratings_row[0]['long_passing']
                freekick_def_away = freekick_def_away + int(lp)
            freekick_def_away = math.ceil(freekick_def_away / len(defenderNamesAway))
            
            freekick_middef_away = 0
            for ind in range(len(midDefNamesAway)):
                away_middeffielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midDefNamesAway[ind])].values
                fk = away_middeffielder_ratings_row[0]['attacking_long_passing']
                freekick_middef_away = freekick_middef_away + int(fk)
            freekick_middef_away = math.ceil(freekick_middef_away / len(midDefNamesAway))
            
            freekick_mid_away = 0
            for ind in range(len(midfielderNamesAway)):
                away_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midfielderNamesAway[ind])].values
                fk = away_midfielder_ratings_row[0]['skill_fk_accuracy']
                freekick_mid_away = freekick_mid_away + int(fk)
            freekick_mid_away = math.ceil(freekick_mid_away / len(midfielderNamesAway))
            
            freekick_for_away = 0
            for ind in range(len(forwardNamesAway)):
                away_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == forwardNamesAway[ind])].values
                fk = away_forward_ratings_row[0]['skill_fk_accuracy']
                freekick_for_away = freekick_for_away + int(fk)
            freekick_for_away = math.ceil(freekick_for_away / len(forwardNamesAway))
            
            lines[atk_def_line] = "AtkDef = "
            lines[atk_freekick_def_line] = "AtkFreeKickDef = "
            for ind,pos in enumerate(defenderPositionsAway):
                def_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == defenderNamesAway[ind])].values
                sp = def_ratings_row[0]['short_passing']
                lp = def_ratings_row[0]['long_passing']
                if (pos == "L"):
                    lines[39 - 1] = lines[39 - 1][24:] + "1" + lines[39 - 1][:25]
                elif (pos == "LR"):
                    lines[39 - 1] = lines[39 - 1][27:] + "1" + lines[39 - 1][:28]
                elif (pos == "CL"):
                    lines[39 - 1] = lines[39 - 1][30:] + "1" + lines[39 - 1][:31]
                elif (pos == "C"):
                    lines[39 - 1] = lines[39 - 1][33:] + "1" + lines[39 - 1][:34]
                elif (pos == "CR"):
                    lines[39 - 1] = lines[39 - 1][36:] + "1" + lines[39 - 1][:37]
                elif (pos == "RL"):
                    lines[39 - 1] = lines[39 - 1][39:] + "1" + lines[39 - 1][:40]
                elif (pos == "R"):
                    lines[39 - 1] = lines[39 - 1][42:] + "1" + lines[39 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_def_line] = lines[atk_def_line] + f"[pos[{pos}] == 1]Def({sp, lp, prob_to_lose_home_forwards, aggression_home_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[pos[{pos}] == 1]FKDef({freekick_def_away, pos})"
                else:
                    lines[atk_def_line] = lines[atk_def_line] + f"[] [pos[{pos}] == 1]Def({sp, lp, prob_to_lose_home_forwards, aggression_home_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[] [pos[{pos}] == 1]FKDef({freekick_def_away, pos})"

            lines[atk_middef_line] = "AtkMidDef = "
            lines[atk_freekick_middef_line] = "AtkFreeKickMidDef = "
            for ind,pos in enumerate(midDefPositionsAway):
                #TODO modify midfielder ratings in pcsp file
                middef_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midDefNamesAway[ind])].values
                sp = middef_ratings_row[0]['attacking_short_passing']
                lp = middef_ratings_row[0]['attacking_long_passing']
                if (pos == "L"):
                    lines[40 - 1] = lines[40 - 1][24:] + "1" + lines[40 - 1][:25]
                elif (pos == "LR"):
                    lines[40 - 1] = lines[40 - 1][27:] + "1" + lines[40 - 1][:28]
                elif (pos == "CL"):
                    lines[40 - 1] = lines[40 - 1][30:] + "1" + lines[40 - 1][:31]
                elif (pos == "C"):
                    lines[40 - 1] = lines[40 - 1][33:] + "1" + lines[40 - 1][:34]
                elif (pos == "CR"):
                    lines[40 - 1] = lines[40 - 1][36:] + "1" + lines[40 - 1][:37]
                elif (pos == "RL"):
                    lines[40 - 1] = lines[40 - 1][39:] + "1" + lines[40 - 1][:40]
                elif (pos == "R"):
                    lines[40 - 1] = lines[40 - 1][42:] + "1" + lines[40 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_middef_line] = lines[atk_middef_line] + f"[pos[{pos}] == 1]MidDef({sp, lp, prob_to_lose_home_middeffielders, aggression_home_middeffielders, pos})"
                    lines[atk_freekick_middef_line] = lines[atk_freekick_middef_line] + f"[pos[{pos}] == 1]FKMidDef({freekick_middef_away, pos})"
                else:
                    lines[atk_middef_line] = lines[atk_middef_line] + f"[] [pos[{pos}] == 1]MidDef({sp, lp,prob_to_lose_home_middeffielders, aggression_home_middeffielders, pos})"
                    lines[atk_freekick_middef_line] = lines[atk_freekick_middef_line] + f"[] [pos[{pos}] == 1]FKMidDef({freekick_middef_away, pos})"

            lines[atk_mid_line] = "AtkMid = "
            lines[atk_freekick_mid_line] = "AtkFreeKickMid = "
            for ind,pos in enumerate(midfielderPositionsAway):
                #TODO modify midfielder ratings in pcsp file
                mid_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midfielderNamesAway[ind])].values
                sp = mid_ratings_row[0]['attacking_short_passing']
                lp = mid_ratings_row[0]['attacking_long_passing']
                ls = mid_ratings_row[0]['power_long_shots']
                if (pos == "L"):
                    lines[41 - 1] = lines[41 - 1][24:] + "1" + lines[41 - 1][:25]
                elif (pos == "LR"):
                    lines[41 - 1] = lines[41 - 1][27:] + "1" + lines[41 - 1][:28]
                elif (pos == "CL"):
                    lines[41 - 1] = lines[41 - 1][30:] + "1" + lines[41 - 1][:31]
                elif (pos == "C"):
                    lines[41 - 1] = lines[41 - 1][33:] + "1" + lines[41 - 1][:34]
                elif (pos == "CR"):
                    lines[41 - 1] = lines[41 - 1][36:] + "1" + lines[41 - 1][:37]
                elif (pos == "RL"):
                    lines[41 - 1] = lines[41 - 1][39:] + "1" + lines[41 - 1][:40]
                elif (pos == "R"):
                    lines[41 - 1] = lines[41 - 1][42:] + "1" + lines[41 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[pos[{pos}] == 1]Mid({sp, lp, ls,prob_to_lose_home_midfielders, aggression_home_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[pos[{pos}] == 1]FKMid({freekick_mid_away, pos})"
                else:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[] [pos[{pos}] == 1]Mid({sp, lp,ls, prob_to_lose_home_midfielders, aggression_home_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[] [pos[{pos}] == 1]FKMid({freekick_mid_away, pos})"
            
            for ind,pos in enumerate(forwardPositionsAway):
            #TODO modify forward ratings in pcsp file
                for_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == forwardNamesAway[ind])].values
                sp = for_ratings_row[0]['attacking_short_passing']
                lp = for_ratings_row[0]['attacking_long_passing']
                ls = for_ratings_row[0]['power_long_shots']
                fi = for_ratings_row[0]['attacking_finishing']
                vo = for_ratings_row[0]['attacking_volleys']
                dr = for_ratings_row[0]['skill_dribbling']
                he = for_ratings_row[0]['attacking_heading_accuracy']
                if (pos == "L"):
                    lines[42 - 1] = lines[42 - 1][24:] + "1" + lines[42 - 1][:25]
                    lines[96 - 1] = lines[96 - 1][24:] + "4" + lines[96 - 1][:25]
                elif (pos == "LR"):
                    lines[42 - 1] = lines[42 - 1][27:] + "1" + lines[42 - 1][:28]
                    lines[96 - 1] = lines[96 - 1][27:] + "4" + lines[96 - 1][:28]
                elif (pos == "CL"):
                    lines[42 - 1] = lines[42 - 1][30:] + "1" + lines[42 - 1][:31]
                    lines[96 - 1] = lines[96 - 1][30:] + "4" + lines[96 - 1][:31]
                elif (pos == "C"):
                    lines[42 - 1] = lines[42 - 1][33:] + "1" + lines[42 - 1][:34]
                    lines[96 - 1] = lines[96 - 1][33:] + "4" + lines[96 - 1][:34]
                elif (pos == "CR"):
                    lines[42 - 1] = lines[42 - 1][36:] + "1" + lines[42 - 1][:37]
                    lines[96 - 1] = lines[96 - 1][36:] + "4" + lines[96 - 1][:37]
                elif (pos == "RL"):
                    lines[42 - 1] = lines[42 - 1][39:] + "1" + lines[42 - 1][:40]
                    lines[96 - 1] = lines[96 - 1][39:] + "4" + lines[96 - 1][:40]
                elif (pos == "R"):
                    lines[42 - 1] = lines[42 - 1][42:] + "1" + lines[42 - 1][:43]
                    lines[96 - 1] = lines[96 - 1][42:] + "1" + lines[96 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_for_line] = lines[atk_for_line] + f"[pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr,prob_to_lose_home_defenders, aggression_home_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[pos[{pos}] == 1]FKFor({freekick_for_away, pos})"
                else:
                    lines[atk_for_line] = lines[atk_for_line] + f"[] [pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr, prob_to_lose_home_defenders, aggression_home_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[] [pos[{pos}] == 1]FKFor({freekick_for_away, pos})"
            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
        else if (is3levels_home and is4levels_away): #TODO
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperNameHome = home_team[0]
            defenderPositionsHome = homePositions[1:def_H]
            defenderNamesHome = home_team[1:def_H]
            midfielderPositionsHome = homePositions[def_H:def_H +mid_H]
            midfielderNamesHome = home_team[def_H:def_H +mid_H]
            forwardPositionsHome = homePositions[def_H+mid_H:]
            forwardNamesHome = home_team[def_H+mid_H:]
            
            awayPositions = away_seq.split(',')
            away_team = away_team.split(',')
            goalkeeperNameAway = away_team[0]
            defenderPositionsAway = awayPositions[1:def_4A]
            defenderNamesAway = away_team[1:def_4A]
            midDefPositionsAway = awayPositions[def_4A:def_4A +midDef_4A]
            midDefNamesAway = away_team[def_4A:def_4A +midDef_4A]
            midfielderPositionsAway = awayPositions[def_4A +midDef_4A:def_4A +midDef_4A +mid_4A]
            midfielderNamesAway = away_team[def_4A:def_4A +midDef_4A +mid_4A]
            forwardPositionsAway = awayPositions[def_4A +midDef_4A +mid_4A:]
            forwardNamesAway = away_team[def_4A +midDef_4A +mid_4A:]
            ##generate home pcsp file using 3 levels template
            
            #first create the home pcsp file from the template file
            out_file = f"pcspDir//{home}{away}{season}.pcsp"
            open(out_file,'w').close() #creates the file
            with open(template_file_3f, 'r') as fp_in, open(out_file, 'w') as fp_out: #copy template file to out file
                for line in fp_in:
                    fp_out.write(line)
            with open(out_file, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
            
            # Modify the desired row and column
            #remember that we are reading from array and the numbers are the indexes of the array
            #and not the true columns and rows,so minus 1 from them
            
            #TODO modify Goalkeeper ratings in pcsp file
            #home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home)].values
            gk_home_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) and (df_ratings['long_name'] == goalkeeperNameHome)].values
            short_pass_rating = gk_home_ratings_row[0]['short_passing']
            long_pass_rating = gk_home_ratings_row[0]['long_passing']
            gk_away_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) and (df_ratings['long_name'] == goalkeeperNameAway)].values
            gk_handling_rating = gk_away_ratings_row[0]['gk_handling']
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
            lines[def_kep_line] = f"DefKep = [pos[C] == 1]Kep_2({gk_handling_rating}, C);\n"
            # Calculate probability to lose posession to away team forwards
            # Calculate also the aggression rating
            no_of_forwards = len(forwardNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_forwards):
                away_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == forwardNamesAway[ind])].values
                interception_ratings = away_forward_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_forward_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_forward_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_forward_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_forwards = math.ceil(combined_ratings / no_of_forwards)
            aggression_away_forwards = math.ceil(aggression_ratings / no_of_forwards)
            
            # Calculate probability to lose posession to away team midfielders
            no_of_midfielders = len(midfielderNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_midfielders):
                away_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midfielderNamesAway[ind])].values
                interception_ratings = away_midfielder_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_midfielder_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_midfielder_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_midfielder_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_midfielders = math.ceil(combined_ratings / no_of_midfielders)
            aggression_away_midfielders = math.ceil(aggression_ratings / no_of_midfielders)
            
            # Calculate probability to lose posession to away team defenders
            no_of_defenders = len(defenderNamesAway)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_defenders):
                away_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == defenderNamesAway[ind])].values
                interception_ratings = away_defender_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_defender_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_defender_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_defender_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_defenders = math.ceil(combined_ratings / no_of_defenders)
            aggression_away_defenders = math.ceil(aggression_ratings / no_of_defenders)
            
            freekick_def_home = 0
            for ind in range(len(defenderNamesHome)):
                home_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                lp = home_defender_ratings_row[0]['long_passing']
                freekick_def_home = freekick_def_home + int(lp)
            freekick_def_home = math.ceil(freekick_def_home / len(defenderNamesHome))
            
            freekick_mid_home = 0
            for ind in range(len(midfielderNamesHome)):
                home_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midfielderNamesHome[ind])].values
                fk = home_midfielder_ratings_row[0]['skill_fk_accuracy']
                freekick_mid_home = freekick_mid_home + int(fk)
            freekick_mid_home = math.ceil(freekick_mid_home / len(midfielderNamesHome))
            
            freekick_for_home = 0
            for ind in range(len(forwardNamesHome)):
                home_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == forwardNamesHome[ind])].values
                fk = home_forward_ratings_row[0]['skill_fk_accuracy']
                freekick_for_home = freekick_for_home + int(fk)
            freekick_for_home = math.ceil(freekick_for_home / len(forwardNamesHome))
            
            lines[atk_def_line] = "AtkDef = "
            lines[atk_freekick_def_line] = "AtkFreeKickDef = "
            for ind,pos in enumerate(defenderPositionsHome):
                def_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                sp = def_ratings_row[0]['short_passing']
                lp = def_ratings_row[0]['long_passing']
                if (pos == "L"):
                    lines[39 - 1] = lines[39 - 1][24:] + "1" + lines[39 - 1][:25]
                elif (pos == "LR"):
                    lines[39 - 1] = lines[39 - 1][27:] + "1" + lines[39 - 1][:28]
                elif (pos == "CL"):
                    lines[39 - 1] = lines[39 - 1][30:] + "1" + lines[39 - 1][:31]
                elif (pos == "C"):
                    lines[39 - 1] = lines[39 - 1][33:] + "1" + lines[39 - 1][:34]
                elif (pos == "CR"):
                    lines[39 - 1] = lines[39 - 1][36:] + "1" + lines[39 - 1][:37]
                elif (pos == "RL"):
                    lines[39 - 1] = lines[39 - 1][39:] + "1" + lines[39 - 1][:40]
                elif (pos == "R"):
                    lines[39 - 1] = lines[39 - 1][42:] + "1" + lines[39 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_def_line] = lines[atk_def_line] + f"[pos[{pos}] == 1]Def({sp, lp, prob_to_lose_away_forwards, aggression_away_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[pos[{pos}] == 1]FKDef({freekick_def_home, pos})"
                else:
                    lines[atk_def_line] = lines[atk_def_line] + f"[] [pos[{pos}] == 1]Def({sp, lp, prob_to_lose_away_forwards, aggression_away_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[] [pos[{pos}] == 1]FKDef({freekick_def_home, pos})"

            lines[atk_mid_line] = "AtkMid = "
            lines[atk_freekick_mid_line] = "AtkFreeKickMid = "
            for ind,pos in enumerate(midfielderPositionsHome):
                #TODO modify midfielder ratings in pcsp file
                mid_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midfielderNamesHome[ind])].values
                sp = mid_ratings_row[0]['attacking_short_passing']
                lp = mid_ratings_row[0]['attacking_long_passing']
                ls = mid_ratings_row[0]['power_long_shots']
                if (pos == "L"):
                    lines[40 - 1] = lines[40 - 1][24:] + "1" + lines[40 - 1][:25]
                elif (pos == "LR"):
                    lines[40 - 1] = lines[40 - 1][27:] + "1" + lines[40 - 1][:28]
                elif (pos == "CL"):
                    lines[40 - 1] = lines[40 - 1][30:] + "1" + lines[40 - 1][:31]
                elif (pos == "C"):
                    lines[40 - 1] = lines[40 - 1][33:] + "1" + lines[40 - 1][:34]
                elif (pos == "CR"):
                    lines[40 - 1] = lines[40 - 1][36:] + "1" + lines[40 - 1][:37]
                elif (pos == "RL"):
                    lines[40 - 1] = lines[40 - 1][39:] + "1" + lines[40 - 1][:40]
                elif (pos == "R"):
                    lines[40 - 1] = lines[40 - 1][42:] + "1" + lines[40 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[pos[{pos}] == 1]Mid({sp, lp, ls,prob_to_lose_away_midfielders, aggression_away_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[pos[{pos}] == 1]FKMid({freekick_mid_home, pos})"
                else:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[] [pos[{pos}] == 1]Mid({sp, lp,ls, prob_to_lose_away_midfielders, aggression_away_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[] [pos[{pos}] == 1]FKMid({freekick_mid_home, pos})"
            for ind,pos in enumerate(forwardPositionsHome):
            #TODO modify forward ratings in pcsp file
                for_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == forwardNamesHome[ind])].values
                sp = for_ratings_row[0]['attacking_short_passing']
                lp = for_ratings_row[0]['attacking_long_passing']
                ls = for_ratings_row[0]['power_long_shots']
                fi = for_ratings_row[0]['attacking_finishing']
                vo = for_ratings_row[0]['attacking_volleys']
                dr = for_ratings_row[0]['skill_dribbling']
                he = for_ratings_row[0]['attacking_heading_accuracy']
                if (pos == "L"):
                    lines[41 - 1] = lines[41 - 1][24:] + "1" + lines[41 - 1][:25]
                    lines[91 - 1] = lines[91 - 1][24:] + "4" + lines[91 - 1][:25]
                elif (pos == "LR"):
                    lines[41 - 1] = lines[41 - 1][27:] + "1" + lines[41 - 1][:28]
                    lines[91 - 1] = lines[91 - 1][27:] + "4" + lines[91 - 1][:28]
                elif (pos == "CL"):
                    lines[41 - 1] = lines[41 - 1][30:] + "1" + lines[41 - 1][:31]
                    lines[91 - 1] = lines[91 - 1][30:] + "4" + lines[91 - 1][:31]
                elif (pos == "C"):
                    lines[41 - 1] = lines[41 - 1][33:] + "1" + lines[41 - 1][:34]
                    lines[91 - 1] = lines[91 - 1][33:] + "4" + lines[91 - 1][:34]
                elif (pos == "CR"):
                    lines[41 - 1] = lines[41 - 1][36:] + "1" + lines[41 - 1][:37]
                    lines[91 - 1] = lines[91 - 1][36:] + "4" + lines[91 - 1][:37]
                elif (pos == "RL"):
                    lines[41 - 1] = lines[41 - 1][39:] + "1" + lines[41 - 1][:40]
                    lines[91 - 1] = lines[91 - 1][39:] + "4" + lines[91 - 1][:40]
                elif (pos == "R"):
                    lines[41 - 1] = lines[41 - 1][42:] + "1" + lines[41 - 1][:43]
                    lines[91 - 1] = lines[91 - 1][42:] + "1" + lines[91 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_for_line] = lines[atk_for_line] + f"[pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr,prob_to_lose_away_defenders, aggression_away_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[pos[{pos}] == 1]FKFor({freekick_for_home, pos})"
                else:
                    lines[atk_for_line] = lines[atk_for_line] + f"[] [pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr, prob_to_lose_away_defenders, aggression_away_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[] [pos[{pos}] == 1]FKFor({freekick_for_home, pos})"
            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////         
            #then create the away pcsp file from the template file
            out_file = f"pcspDir\\{away}{home}{season}.pcsp"
            open(out_file,'w').close() #creates the file
            with open(template_file_4f, 'r') as fp_in, open(out_file, 'w') as fp_out: #copy template file to out file
                for line in fp_in:
                    fp_out.write(line)
            with open(out_file, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
            
            # Calculate probability to lose posession to home team forwards
            # Calculate also the aggression rating
            no_of_forwards = len(forwardNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_forwards):
                home_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == forwardNamesHome[ind])].values
                interception_ratings = home_forward_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = home_forward_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = home_forward_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(home_forward_ratings_row[0]['mentality_aggression'])
            prob_to_lose_home_forwards = math.ceil(combined_ratings / no_of_forwards)
            aggression_home_forwards = math.ceil(aggression_ratings / no_of_forwards)
            
            # Calculate probability to lose posession to home team midfielders
            no_of_midfielders = len(midfielderNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_midfielders):
                home_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midfielderNamesHome[ind])].values
                interception_ratings = home_midfielder_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = home_midfielder_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = home_midfielder_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(home_midfielder_ratings_row[0]['mentality_aggression'])
            prob_to_lose_home_midfielders = math.ceil(combined_ratings / no_of_midfielders)
            aggression_home_midfielders = math.ceil(aggression_ratings / no_of_midfielders)
            
            # Calculate probability to lose posession to away team midfielders
            no_of_middeffielders = len(midDefNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_middeffielders):
                away_middef_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == midDefNamesHome[ind])].values
                interception_ratings = away_middef_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = away_middef_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = away_middef_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(away_middef_ratings_row[0]['mentality_aggression'])
            prob_to_lose_away_middeffielders = math.ceil(combined_ratings / no_of_middeffielders)
            aggression_away_middeffielders = math.ceil(aggression_ratings / no_of_middeffielders)
            
            # Calculate probability to lose posession to home team defenders
            no_of_defenders = len(defenderNamesHome)
            combined_ratings = 0
            aggression_ratings = 0
            for ind in range(no_of_defenders):
                home_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                interception_ratings = home_defender_ratings_row[0]['mentality_interceptions']
                standing_tackle_ratings = home_defender_ratings_row[0]['defending_standing_tackle']
                sliding_tackle_ratings = home_defender_ratings_row[0]['defending_sliding_tackle']
                max_rating_out_of_the_three = max(int(interception_ratings),int(standing_tackle_ratings),int(sliding_tackle_ratings))
                combined_ratings = combined_ratings + max_rating_out_of_the_three
                
                aggression_ratings = aggression_ratings + int(home_defender_ratings_row[0]['mentality_aggression'])
            prob_to_lose_home_defenders = math.ceil(combined_ratings / no_of_defenders)
            aggression_home_defenders = math.ceil(aggression_ratings / no_of_defenders)
            
            freekick_def_away = 0
            for ind in range(len(defenderNamesAway)):
                away_defender_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == defenderNamesAway[ind])].values
                lp = away_defender_ratings_row[0]['long_passing']
                freekick_def_away = freekick_def_away + int(lp)
            freekick_def_away = math.ceil(freekick_def_away / len(defenderNamesAway))
            
            freekick_middef_away = 0
            for ind in range(len(midDefNamesAway)):
                away_middeffielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midDefNamesAway[ind])].values
                fk = away_middeffielder_ratings_row[0]['attacking_long_passing']
                freekick_middef_away = freekick_middef_away + int(fk)
            freekick_middef_away = math.ceil(freekick_middef_away / len(midDefNamesAway))
            
            freekick_mid_away = 0
            for ind in range(len(midfielderNamesAway)):
                away_midfielder_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midfielderNamesAway[ind])].values
                fk = away_midfielder_ratings_row[0]['skill_fk_accuracy']
                freekick_mid_away = freekick_mid_away + int(fk)
            freekick_mid_away = math.ceil(freekick_mid_away / len(midfielderNamesAway))
            
            freekick_for_away = 0
            for ind in range(len(forwardNamesAway)):
                away_forward_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == forwardNamesAway[ind])].values
                fk = away_forward_ratings_row[0]['skill_fk_accuracy']
                freekick_for_away = freekick_for_away + int(fk)
            freekick_for_away = math.ceil(freekick_for_away / len(forwardNamesAway))
            
            lines[atk_def_line] = "AtkDef = "
            lines[atk_freekick_def_line] = "AtkFreeKickDef = "
            for ind,pos in enumerate(defenderPositionsAway):
                def_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == defenderNamesAway[ind])].values
                sp = def_ratings_row[0]['short_passing']
                lp = def_ratings_row[0]['long_passing']
                if (pos == "L"):
                    lines[39 - 1] = lines[39 - 1][24:] + "1" + lines[39 - 1][:25]
                elif (pos == "LR"):
                    lines[39 - 1] = lines[39 - 1][27:] + "1" + lines[39 - 1][:28]
                elif (pos == "CL"):
                    lines[39 - 1] = lines[39 - 1][30:] + "1" + lines[39 - 1][:31]
                elif (pos == "C"):
                    lines[39 - 1] = lines[39 - 1][33:] + "1" + lines[39 - 1][:34]
                elif (pos == "CR"):
                    lines[39 - 1] = lines[39 - 1][36:] + "1" + lines[39 - 1][:37]
                elif (pos == "RL"):
                    lines[39 - 1] = lines[39 - 1][39:] + "1" + lines[39 - 1][:40]
                elif (pos == "R"):
                    lines[39 - 1] = lines[39 - 1][42:] + "1" + lines[39 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_def_line] = lines[atk_def_line] + f"[pos[{pos}] == 1]Def({sp, lp, prob_to_lose_home_forwards, aggression_home_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[pos[{pos}] == 1]FKDef({freekick_def_away, pos})"
                else:
                    lines[atk_def_line] = lines[atk_def_line] + f"[] [pos[{pos}] == 1]Def({sp, lp, prob_to_lose_home_forwards, aggression_home_forwards, pos})"
                    lines[atk_freekick_def_line] = lines[atk_freekick_def_line] + f"[] [pos[{pos}] == 1]FKDef({freekick_def_away, pos})"

            lines[atk_middef_line] = "AtkMidDef = "
            lines[atk_freekick_middef_line] = "AtkFreeKickMidDef = "
            for ind,pos in enumerate(midDefPositionsAway):
                #TODO modify midfielder ratings in pcsp file
                middef_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midDefNamesAway[ind])].values
                sp = middef_ratings_row[0]['attacking_short_passing']
                lp = middef_ratings_row[0]['attacking_long_passing']
                if (pos == "L"):
                    lines[40 - 1] = lines[40 - 1][24:] + "1" + lines[40 - 1][:25]
                elif (pos == "LR"):
                    lines[40 - 1] = lines[40 - 1][27:] + "1" + lines[40 - 1][:28]
                elif (pos == "CL"):
                    lines[40 - 1] = lines[40 - 1][30:] + "1" + lines[40 - 1][:31]
                elif (pos == "C"):
                    lines[40 - 1] = lines[40 - 1][33:] + "1" + lines[40 - 1][:34]
                elif (pos == "CR"):
                    lines[40 - 1] = lines[40 - 1][36:] + "1" + lines[40 - 1][:37]
                elif (pos == "RL"):
                    lines[40 - 1] = lines[40 - 1][39:] + "1" + lines[40 - 1][:40]
                elif (pos == "R"):
                    lines[40 - 1] = lines[40 - 1][42:] + "1" + lines[40 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_middef_line] = lines[atk_middef_line] + f"[pos[{pos}] == 1]MidDef({sp, lp, prob_to_lose_home_middeffielders, aggression_home_middeffielders, pos})"
                    lines[atk_freekick_middef_line] = lines[atk_freekick_middef_line] + f"[pos[{pos}] == 1]FKMidDef({freekick_middef_away, pos})"
                else:
                    lines[atk_middef_line] = lines[atk_middef_line] + f"[] [pos[{pos}] == 1]MidDef({sp, lp,prob_to_lose_home_middeffielders, aggression_home_middeffielders, pos})"
                    lines[atk_freekick_middef_line] = lines[atk_freekick_middef_line] + f"[] [pos[{pos}] == 1]FKMidDef({freekick_middef_away, pos})"

            lines[atk_mid_line] = "AtkMid = "
            lines[atk_freekick_mid_line] = "AtkFreeKickMid = "
            for ind,pos in enumerate(midfielderPositionsAway):
                #TODO modify midfielder ratings in pcsp file
                mid_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == midfielderNamesAway[ind])].values
                sp = mid_ratings_row[0]['attacking_short_passing']
                lp = mid_ratings_row[0]['attacking_long_passing']
                ls = mid_ratings_row[0]['power_long_shots']
                if (pos == "L"):
                    lines[41 - 1] = lines[41 - 1][24:] + "1" + lines[41 - 1][:25]
                elif (pos == "LR"):
                    lines[41 - 1] = lines[41 - 1][27:] + "1" + lines[41 - 1][:28]
                elif (pos == "CL"):
                    lines[41 - 1] = lines[41 - 1][30:] + "1" + lines[41 - 1][:31]
                elif (pos == "C"):
                    lines[41 - 1] = lines[41 - 1][33:] + "1" + lines[41 - 1][:34]
                elif (pos == "CR"):
                    lines[41 - 1] = lines[41 - 1][36:] + "1" + lines[41 - 1][:37]
                elif (pos == "RL"):
                    lines[41 - 1] = lines[41 - 1][39:] + "1" + lines[41 - 1][:40]
                elif (pos == "R"):
                    lines[41 - 1] = lines[41 - 1][42:] + "1" + lines[41 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[pos[{pos}] == 1]Mid({sp, lp, ls,prob_to_lose_home_midfielders, aggression_home_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[pos[{pos}] == 1]FKMid({freekick_mid_away, pos})"
                else:
                    lines[atk_mid_line] = lines[atk_mid_line] + f"[] [pos[{pos}] == 1]Mid({sp, lp,ls, prob_to_lose_home_midfielders, aggression_home_midfielders, pos})"
                    lines[atk_freekick_mid_line] = lines[atk_freekick_mid_line] + f"[] [pos[{pos}] == 1]FKMid({freekick_mid_away, pos})"
            
            for ind,pos in enumerate(forwardPositionsAway):
            #TODO modify forward ratings in pcsp file
                for_ratings_row = df_ratings.loc[(df_ratings['club_name'] == away) & (df_ratings['long_name'] == forwardNamesAway[ind])].values
                sp = for_ratings_row[0]['attacking_short_passing']
                lp = for_ratings_row[0]['attacking_long_passing']
                ls = for_ratings_row[0]['power_long_shots']
                fi = for_ratings_row[0]['attacking_finishing']
                vo = for_ratings_row[0]['attacking_volleys']
                dr = for_ratings_row[0]['skill_dribbling']
                he = for_ratings_row[0]['attacking_heading_accuracy']
                if (pos == "L"):
                    lines[42 - 1] = lines[42 - 1][24:] + "1" + lines[42 - 1][:25]
                    lines[96 - 1] = lines[96 - 1][24:] + "4" + lines[96 - 1][:25]
                elif (pos == "LR"):
                    lines[42 - 1] = lines[42 - 1][27:] + "1" + lines[42 - 1][:28]
                    lines[96 - 1] = lines[96 - 1][27:] + "4" + lines[96 - 1][:28]
                elif (pos == "CL"):
                    lines[42 - 1] = lines[42 - 1][30:] + "1" + lines[42 - 1][:31]
                    lines[96 - 1] = lines[96 - 1][30:] + "4" + lines[96 - 1][:31]
                elif (pos == "C"):
                    lines[42 - 1] = lines[42 - 1][33:] + "1" + lines[42 - 1][:34]
                    lines[96 - 1] = lines[96 - 1][33:] + "4" + lines[96 - 1][:34]
                elif (pos == "CR"):
                    lines[42 - 1] = lines[42 - 1][36:] + "1" + lines[42 - 1][:37]
                    lines[96 - 1] = lines[96 - 1][36:] + "4" + lines[96 - 1][:37]
                elif (pos == "RL"):
                    lines[42 - 1] = lines[42 - 1][39:] + "1" + lines[42 - 1][:40]
                    lines[96 - 1] = lines[96 - 1][39:] + "4" + lines[96 - 1][:40]
                elif (pos == "R"):
                    lines[42 - 1] = lines[42 - 1][42:] + "1" + lines[42 - 1][:43]
                    lines[96 - 1] = lines[96 - 1][42:] + "1" + lines[96 - 1][:43]
                else:
                    print("wrong position")
                    sys.exit(1)
                #TODO modify defender ratings in pcsp file
                if ind == 0:
                    lines[atk_for_line] = lines[atk_for_line] + f"[pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr,prob_to_lose_home_defenders, aggression_home_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[pos[{pos}] == 1]FKFor({freekick_for_away, pos})"
                else:
                    lines[atk_for_line] = lines[atk_for_line] + f"[] [pos[{pos}] == 1]For({sp, lp,fi,ls,vo,he,dr, prob_to_lose_home_defenders, aggression_home_defenders, pos})"
                    lines[atk_freekick_for_line] = lines[atk_freekick_for_line] + f"[] [pos[{pos}] == 1]FKFor({freekick_for_away, pos})"
            
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
        else if (is4levels_home and is3levels_away):
            #TODO
        else:
            print("Unknown formation")
    #after adding all the pcsp for the matches, we can start to run the PAT3 Console on the files
    consolePath = 'C:\\Program Files\\Process Analysis Toolkit\\Process Analysis Toolkit 3.5.1\\PAT3.Console.exe'
    # Define the directory path
    dir_path = 'C:\\Users\\nicky\\Desktop\\pcspDir'
    out_path = 'C:\\Users\\nicky\\Desktop\\output'
    # Get a list of all files in the directory
    file_list = os.listdir(dir_path)

    # Iterate over the list and read each file
    ind = 0
    for file_name in file_list:
        file_path = os.path.join(dir_path, file_name)
        file_out = f"{out_path}\\output{ind}.txt" #Should not be in same directory as pcsp since it might interfere with the for loop
        if not os.path.isfile(file_out):
            # Create destination file if it does not exist
            open(file_out, 'w').close()
        command = [consolePath, '-pcsp',file_path, file_out]
        result = subprocess.check_output(command)
        print(result)
        ind = ind + 1
    #create the new probabilities/season.csv
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(['match_url','home_prob_softmax'])
    # then from all the outputs, extract out the probabilities from home team and away team, then softmax them to get the softmaxed home team victory probability
    home_prob = 0
    away_prob = 0
    softmax = []
    for ind,file_name in enumerate(os.listdir(out_path)):
        if ind % 2 == 0:
            with open(file_name, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
                get_prob = lines[21][75:91].split(',')
                home_prob = ceil((float(get_prob[0]) + float(get_prob[1]))/2)
        if ind % 2 == 1:
            with open(file_name, 'r') as file:
                # Read the contents of the file into a list of lines
                lines = file.readlines()
                get_prob = lines[21][75:91].split(',')
                away_prob = ceil((float(get_prob[0]) + float(get_prob[1]))/2)
                softmax.append(str(softmax([home_prob,away_prob])[0]))
            
    for ind,url in enumerate(match_url_arr):
        workbook.append([url, softmax[ind]])
    workbook.save(f"new_probabilities/{season}.csv")
        
if __name__ == "__main__":
    seasons = [20152016, 20162017, 20172018, 20182019, 20192020, 20202021]
    for season in seasons:
        readfile(season)

# Added function for dribbling success probability
def dribblingSuccessProbability(player, defender):
    # Skill weights
    skillWeight = 0.6
    physicalWeight = 0.3
    otherWeight = 0.1

    # Skill scores
    playerSkillScore = player['skill_dribbling'] + player['skill_ball_control'] + player['movement_agility'] + player['movement_balance']
    defenderSkillScore = defender['defending'] + defender['defending_standing_tackle'] + defender['defending_sliding_tackle'] + defender['mentality_interceptions']

    # Physical attribute scores
    playerPhysicalScore = player['power_strength'] + player['power_stamina'] + player['pace']
    defenderPhysicalScore = defender['power_strength'] + defender['power_stamina'] + defender['pace']

    # Other factors scores
    playerOtherScore = player['mentality_composure'] + player['work_rate']
    defenderOtherScore = defender['mentality_composure'] + defender['work_rate']

    # Calculate total scores
    playerTotalScore = skillWeight * playerSkillScore + physicalWeight * playerPhysicalScore + otherWeight * playerOtherScore
    defenderTotalScore = skillWeight * defenderSkillScore + physicalWeight * defenderPhysicalScore + otherWeight * defenderOtherScore

    # Calculate dribbling success probability
    probability = playerTotalScore / (playerTotalScore + defenderTotalScore)

    return probability

def softmax(z):
    """Compute softmax values for each sets of scores in z."""
    exponents = [math.exp(value) for value in z]
    exp_sum = sum(exponents)
    return [exp_value / exp_sum for exp_value in exponents]
    
    
    
#Use this code as reference
def simulate_betting(season):

    df_betting = pd.read_csv(f"betting_dataset/{season}.csv")
    df_original = pd.read_csv(f"original_probabilities/{season}.csv")
    df_new = pd.read_csv(f"new_probabilities/{season}.csv")

    # bet $100 for every match
    original_net, new_net = 0, 0
    for index, row in df_betting.iterrows():
        match_url = row['match_url']
        home_odds = row['B365H']
        away_odds = row['B365A']
        draw_odds = row['B365D']
        # 0 = home_win, 1 = away_win, 2 = draw
        result = row['result']

        original_home_prob = df_original.loc[df_original['match_url'] == match_url]['home_prob_softmax'].values[0]
        new_home_prob = df_new.loc[df_new['match_url'] == match_url]['home_prob_softmax'].values[0]

        # predict draw
        if abs((1-original_home_prob) - original_home_prob) < 0.001:
            if result == 2: original_net += (draw_odds * 100) - 100
            else: original_net -= 100
        # predict home win
        elif original_home_prob > (1-original_home_prob):
            if result == 0: original_net += (home_odds * 100) - 100
            else: original_net -= 100
        # predict away win
        elif original_home_prob < (1-original_home_prob):
            if result == 1: original_net += (away_odds * 100) - 100
            else: original_net -= 100

        # predict draw
        if abs((1-new_home_prob) - new_home_prob) < 0.001:
            if result == 2: new_net += (draw_odds * 100) - 100
            else: new_net -= 100
        # predict home win
        elif new_home_prob > (1-new_home_prob):
            if result == 0: new_net += (home_odds * 100) - 100
            else: new_net -= 100
        # predict away win
        elif new_home_prob < (1-new_home_prob):
            if result == 1: new_net += (away_odds * 100) - 100
            else: new_net -= 100
        
    print(f"season {season} net profit (original, new): (${original_net}, ${new_net})")
