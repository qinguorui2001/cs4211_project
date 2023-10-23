import pandas as pd
import sys
import os
class Pos(Enum):
    L = 0
    LR = 1
    CL = 2
    C = 3
    CR = 4
    RL = 5
    R = 6
#Create probability for every season
#matches_dataset_dir = f"matches"
def readfile(season):
    df_match = pd.read_csv(f"matches/epl_matches_{season}.csv")
    df_ratings = pd.read_csv(f"eplratings/epl_ratings_{season}.csv")
    template_file_3f = 'path/to/input/file.pcsp'
    template_file_4f = 'path/to/input/file.pcsp'
    #out_file = f"path/to/output/{home}{away}{season}.txt"
    # Verify input file
    if not os.path.isfile(template_file_3f):
        print("error: {} does not exist".format(template_file_3f))
        sys.exit(1)
    if not os.path.isfile(template_file_4f):
        print("error: {} does not exist".format(template_file_4f))
        sys.exit(1)
    
    #Goal: Generate PCSP files
        #Goal generate for 1 match
    for index, row in df_match.iterrows():
        #define row values for current row
        match_url = row['match_url'] #read from column 'match url'
        home = row['home_team']
        away = row['away_team']
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
        def_H,mid_H,for_H = 0 #for 3 levels
        def_4H, midDef_4H, mid_4H = 0 #for 4 levels, in this case def_4H replaces mid_H
        def_A,mid_A,for_A = 0 #for 3 levels
        def_4A,midDef_4A, mid_4A = 0 #for 4 levels, in this case def_4H replaces mid_H
        #address formatting issue for formations
        if "/" in home_fmn: #means 3 levels
            print("Is 3 levels")
            is3levels_home = True
            posArray = home_fmn.split('/')
            def_H,mid_H,for_H = posArray[0],posArray[1],int(posArray[2]) - 2000 
        else: #means 4 levels
            print("Is 4 levels")
            is4levels_home = True
            posArray = home_fmn.split('/')
            def_4H,midDef_4H, mid_4H,for_H = posArray[0],posArray[1],posArray[2], posArray[3]
           
        if "/" in away_fmn: #means 3 levels
            is3levels_away = True
            posArray = away_fmn.split('/')
            def_A,mid_A,for_A = posArray[0],posArray[1],int(posArray[2]) - 2000 
        else: #means 4 levels
            is4levels_away = True
            posArray = away_fmn.split('/')
            def_4A,midDef_4A, mid_4A,for_4A = posArray[0],posArray[1],posArray[2], posArray[3]
          
        if (is3levels_home):
            ##generate home pcsp file using 3 levels template
            
            #first create the home pcsp file from the template file
            out_file = f"path/to/output/{home}{away}{season}.pcsp"
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
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperNameHome = home_team[0]
            defenderPositionsHome = homePositions[1:def_H]
            defenderNamesHome = home_team[1:def_H]
            midfielderPositionsHome = homePositions[def_H:def_H +mid_H]
            midfielderNamesHome = home_team[def_H:def_H +mid_H]
            forwardPositionsHome = homePositions[def_H+mid_H:]
            forwardNamesHome = home_team[def_H+mid_H:]
            
            ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == goalkeeperNameHome)].values
            #TODO modify Goalkeeper ratings in pcsp file
            ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == goalkeeperNameHome)].values
            short_pass_rating = ratings_row[0]['short_passing']
            long_pass_rating = ratings_row[0]['long_passing']

            # Define the line number of AtkKep and DefKep in the file
            atk_kep_line_number = 53
            def_kep_line_number = 72

            # Update the rating of the AtkKep row
            lines[atk_kep_line_number - 1] = f"AtkKep = [pos[C] == 1]Kep_1({short_pass_rating}, {long_pass_rating}, C);\n"

            # Update the score of a DefKep row
            lines[def_kep_line_number - 1] = f"DefKep = [pos[C] == 1]Kep_2({short_pass_rating}, C);\n"  # 这里我用了short_pass_rating，你可以根据需要更改

            # write back file
            with open(out_file, 'w') as file:
                file.writelines(lines)

            
            for ind,pos in enumerate(defenderPositionsHome):
                ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                #TODO modify defender ratings in pcsp file
                if (pos == 'L'):
                    lines[41] = lines[41][:24] + '1' + lines[41][25:]
                    
                elif (pos == 'LR'):
                    lines[41] = lines[41][:27] + '1' + lines[41][28:]
                elif (pos == 'CL'):
                    lines[41] = lines[41][:30] + '1' + lines[41][31:]
                elif (pos == 'C'):
                    lines[41] = lines[41][:33] + '1' + lines[41][34:]
                elif (pos == 'CR'):
                    lines[41] = lines[41][:36] + '1' + lines[41][37:]
                elif (pos == 'RL'):
                    lines[41] = lines[41][:39] + '1' + lines[41][41:]
                else:
                    lines[41] = lines[41][:42] + '1' + lines[41][43:]
            for ind,pos in enumerate(midfielderPositionsHome):
                #TODO modify midfielder ratings in pcsp file
                if (pos == 'L'):
                    lines[42] = lines[42][:24] + '1' + lines[42][25:]
                elif (pos == 'LR'):
                    lines[42] = lines[42][:27] + '1' + lines[42][28:]
                elif (pos == 'CL'):
                    lines[42] = lines[42][:30] + '1' + lines[42][31:]
                elif (pos == 'C'):
                    lines[42] = lines[42][:33] + '1' + lines[42][34:]
                elif (pos == 'CR'):
                    lines[42] = lines[42][:36] + '1' + lines[42][37:]
                elif (pos == 'RL'):
                    lines[42] = lines[42][:39] + '1' + lines[42][40:]
                else:
                    lines[42] = lines[42][:42] + '1' + lines[42][43:]
            for ind,pos in enumerate(forwardPositionsHome):
            #TODO modify forward ratings in pcsp file
                if (pos == 'L'):
                    lines[43] = lines[43][:24] + '1' + lines[43][25:]
                    lines[85] = lines[85][:24] + '1' + lines[85][25:]
                elif (pos == 'LR'):
                    lines[43] = lines[43][:27] + '1' + lines[43][28:]
                    lines[85] = lines[85][:27] + '1' + lines[85][28:]
                elif (pos == 'CL'):
                    lines[43] = lines[43][:30] + '1' + lines[43][31:]
                    lines[85] = lines[85][:30] + '1' + lines[85][31:]
                elif (pos == 'C'):
                    lines[43] = lines[43][:33] + '1' + lines[43][34:]
                    lines[85] = lines[85][:33] + '1' + lines[85][34:]
                elif (pos == 'CR'):
                    lines[43] = lines[43][:36] + '1' + lines[43][37:]
                    lines[85] = lines[85][:36] + '1' + lines[85][37:]
                elif (pos == 'RL'):
                    lines[43] = lines[43][:39] + '1' + lines[43][40:]
                    lines[85] = lines[85][:39] + '1' + lines[85][40:]
                else:
                    lines[43] = lines[43][:42] + '1' + lines[43][43:]
                    lines[85] = lines[85][:42] + '1' + lines[85][43:]
            
            df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == )]
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
            
            #then create the away pcsp file from the template file
            out_file = f"path/to/output/{away}{home}{season}.pcsp"
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
            awayPositions = away_seq.split(',')
            defenderPositionsAway = awayPositions[1:def_A]
            midfielderPositionsAway = awayPositions[def_A:def_A +mid_A]
            forwardPositionsAway = awayPositions[def_A+mid_A:]
            #TODO: Complete the rest of the code for away team
            for ind,pos in enumerate(defenderPositionsAway):
                if (pos == 'L'):
                    lines[40] = lines[40][:24] + '1' + lines[40][25:]
                elif (pos == 'LR'):
                    lines[40] = lines[40][:27] + '1' + lines[40][28:]
                elif (pos == 'CL'):
                    lines[40] = lines[40][:30] + '1' + lines[40][31:]
                elif (pos == 'C'):
                    lines[40] = lines[40][:33] + '1' + lines[40][34:]
                elif (pos == 'CR'):
                    lines[40] = lines[40][:36] + '1' + lines[40][37:]
                elif (pos == 'RL'):
                    lines[40] = lines[40][:39] + '1' + lines[40][40:]
                else:
                    lines[40] = lines[40][:42] + '1' + lines[40][43:]
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
        else:
                        ##generate home pcsp file using 3 levels template
            
            #first create the home pcsp file from the template file
            out_file = f"path/to/output/{home}{away}{season}.pcsp"
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
            homePositions = home_seq.split(',')
            home_team = home_team.split(',')
            goalkeeperNameHome = home_team[0]
            defenderPositionsHome = homePositions[1:def_4H]
            midDeffielderPositionsHome= homePositions[def_4H:def_4H + midDef_4H]
            midDeffielderNamesHome= home_team[def_4H:def_4H + midDef_4H]
            defenderNamesHome = home_team[1:def_4H]
            midfielderPositionsHome = homePositions[midDef_4H:midDef_4H +mid_4H]
            midfielderNamesHome = home_team[midDef_4H:midDef_4H +mid_4H]
            forwardPositionsHome = homePositions[def_4H+ midDef_4H + mid_4H:]
            forwardNamesHome = home_team[def_4H + midDef_4H + mid_4H:]
            
            ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == goalkeeperNameHome)].values
            #TODO modify Goalkeeper ratings in pcsp file
            for ind,pos in enumerate(defenderPositionsHome):
                ratings_row = df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == defenderNamesHome[ind])].values
                #TODO modify defender ratings in pcsp file
                if (pos == 'L'):
                    lines[41] = lines[41][:24] + '1' + lines[41][25:]
                    
                elif (pos == 'LR'):
                    lines[41] = lines[41][:27] + '1' + lines[41][28:]
                elif (pos == 'CL'):
                    lines[41] = lines[41][:30] + '1' + lines[41][31:]
                elif (pos == 'C'):
                    lines[41] = lines[41][:33] + '1' + lines[41][34:]
                elif (pos == 'CR'):
                    lines[41] = lines[41][:36] + '1' + lines[41][37:]
                elif (pos == 'RL'):
                    lines[41] = lines[41][:39] + '1' + lines[41][41:]
                else:
                    lines[41] = lines[41][:42] + '1' + lines[41][43:]
            for ind,pos in enumerate(midDeffielderPositionsHome):
                #TODO modify midfielder ratings in pcsp file
                if (pos == 'L'):
                    lines[42] = lines[42][:27] + '1' + lines[42][28:]
                elif (pos == 'LR'):
                    lines[42] = lines[42][:30] + '1' + lines[42][31:]
                elif (pos == 'CL'):
                    lines[42] = lines[42][:33] + '1' + lines[42][34:]
                elif (pos == 'C'):
                    lines[42] = lines[42][:36] + '1' + lines[42][37:]
                elif (pos == 'CR'):
                    lines[42] = lines[42][:39] + '1' + lines[42][40:]
                elif (pos == 'RL'):
                    lines[42] = lines[42][:42] + '1' + lines[42][43:]
                else:
                    lines[42] = lines[42][:45] + '1' + lines[42][46:]
            for ind,pos in enumerate(midfielderPositionsHome):
                #TODO modify midfielder ratings in pcsp file
                if (pos == 'L'):
                    lines[43] = lines[43][:24] + '1' + lines[43][25:]
                elif (pos == 'LR'):
                    lines[43] = lines[43][:27] + '1' + lines[43][28:]
                elif (pos == 'CL'):
                    lines[43] = lines[43][:30] + '1' + lines[43][31:]
                elif (pos == 'C'):
                    lines[43] = lines[43][:33] + '1' + lines[43][34:]
                elif (pos == 'CR'):
                    lines[43] = lines[43][:36] + '1' + lines[43][37:]
                elif (pos == 'RL'):
                    lines[43] = lines[43][:39] + '1' + lines[43][40:]
                else:
                    lines[43] = lines[43][:42] + '1' + lines[43][43:]
            for ind,pos in enumerate(forwardPositionsHome):
            #TODO modify forward ratings in pcsp file
                if (pos == 'L'):
                    lines[44] = lines[44][:24] + '1' + lines[44][25:]
                    lines[89] = lines[89][:24] + '1' + lines[89][25:]
                elif (pos == 'LR'):
                    lines[44] = lines[44][:27] + '1' + lines[44][28:]
                    lines[89] = lines[89][:27] + '1' + lines[89][28:]
                elif (pos == 'CL'):
                    lines[44] = lines[44][:30] + '1' + lines[44][31:]
                    lines[89] = lines[89][:30] + '1' + lines[89][31:]
                elif (pos == 'C'):
                    lines[44] = lines[44][:33] + '1' + lines[44][34:]
                    lines[89] = lines[89][:33] + '1' + lines[89][34:]
                elif (pos == 'CR'):
                    lines[44] = lines[44][:36] + '1' + lines[44][37:]
                    lines[89] = lines[89][:36] + '1' + lines[89][37:]
                elif (pos == 'RL'):
                    lines[44] = lines[44][:39] + '1' + lines[44][40:]
                    lines[89] = lines[89][:39] + '1' + lines[89][40:]
                else:
                    lines[44] = lines[44][:42] + '1' + lines[44][43:]
                    lines[89] = lines[89][:42] + '1' + lines[89][43:]
            
            df_ratings.loc[(df_ratings['club_name'] == home) & (df_ratings['long_name'] == )]
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)
            
            #then create the away pcsp file from the template file
            out_file = f"path/to/output/{away}{home}{season}.pcsp"
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
            awayPositions = away_seq.split(',')
            defenderPositionsAway = awayPositions[1:def_A]
            midfielderPositionsAway = awayPositions[def_A:def_A +mid_A]
            forwardPositionsAway = awayPositions[def_A+mid_A:]
            #TODO: Complete the rest of the code for away team
            for ind,pos in enumerate(defenderPositionsAway):
                if (pos == 'L'):
                    lines[40] = lines[40][:24] + '1' + lines[40][25:]
                elif (pos == 'LR'):
                    lines[40] = lines[40][:27] + '1' + lines[40][28:]
                elif (pos == 'CL'):
                    lines[40] = lines[40][:30] + '1' + lines[40][31:]
                elif (pos == 'C'):
                    lines[40] = lines[40][:33] + '1' + lines[40][34:]
                elif (pos == 'CR'):
                    lines[40] = lines[40][:36] + '1' + lines[40][37:]
                elif (pos == 'RL'):
                    lines[40] = lines[40][:39] + '1' + lines[40][40:]
                else:
                    lines[40] = lines[40][:42] + '1' + lines[40][43:]
            # Open the file in write mode and write the modified content
            with open(out_file, 'w') as file:
                file.writelines(lines)



            
    #after adding all the pcsp for the matches, we can start to run the PAT3 Console on the files
    
    # then from all the outputs, extract out the probabilities from home tema and away team, then softmax them to get the softmaxed home team victory probability
    
    #add this probability into an excel file called New Probabilites
        
        
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
