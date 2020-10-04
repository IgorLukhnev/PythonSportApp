DATE = 0
HOME = 1
AWAY = 2
HOME_GOALS = 3
AWAY_GOALS = 4
WINNER = 5
HOME_YELLOW_CARDS = 6
AWAY_YELLOW_CARDS = 7
HOME_RED_CARDS = 8
AWAY_RED_CARDS = 9

T_WINS = 0
T_DRAWS = 1
T_LOSES = 2
T1_PTS = 3
T2_PTS = 4

GAMES = 0
WINS = 1
DRAWS = 2
LOSES = 3
GOAL_DIFFERENCE = 4
PTS = 5

YELLOW = 0
RED = 1

NAME = 0
NUM = 1

POS = 0
METHOD = 1

SCORE = 1

TEAM1 = 0
TEAM2 = 1

ANS = 0
TEAMS = 1

DATA_FRAME = 0
SORTING = 1


# Supportive functions:
def read_csv(location):
    with open(location, 'r') as p:
        data_frame = []
        p.readline()
        for line in p:
            match = line.strip().split(',')
            match = match[1:7] + match[18:22]
            data_frame.append(match)
    return data_frame


def list_intersection(list1, list2):
    ans = [value for value in list1 if value in list2]
    return ans


def pairs_from_list(items):
    stop = len(items)
    pairs = []
    for k in range(stop - 1):
        item1 = items[k]
        for i in range(k+1, stop):
            item2 = items[i]
            pairs.append((item1, item2))
    return pairs


# Functions for operating requests:
def first_request(locs):
    req = input('\n'
                'Please, choose the tournament, that you want to discover\n'
                'press 1 - to choose spanish La Liga \n'
                '2 - german Bundesliga\n'
                'enter - to exit: ')
    if req != '':
        try:
            req = int(req)
            if 1 <= req <= 2:
                season = choose_season()
                if season is not None:
                    data = locs[req - 1][DATA_FRAME][season - 1]
                    request = read_request(data, locs[req - 1])
                    while request is not None:
                        print('\n' + request)
                        request = read_request(data, locs[req - 1])
                return first_request(locs)
            else:
                return first_request(locs)
        except:
            return first_request(locs)


def choose_season():
    season = input('\n'
                   'Which season you are interesting in?\n'
                   'Press 1 - to see the results of 2017-2018 years season or\n'
                   'press 2 - to see the results of 2018-2019, enter - to exit: ')
    try:
        season = int(season)
        if 1 <= season <= 2:
            return season
        else:
            return choose_season()
    except:
        if season != '':
            return choose_season()


def read_request(data, tournament):
    req = input('\n'
                'PLease, choose the type of information you are interesting in \n'
                'press 1 - to see matches of a team,\n'
                '2 - to see matches on date, \n'
                '3 - to see a ranking table, \n'
                'enter - to exit: ')
    if req == '1':
        team_name = input('\n'
                          'Enter name of the team: ')
        teams_matches = matches_for_team(data)
        while team_name not in teams_matches and team_name != '':
            team_name = input('\n'
                              'There are not any team with such name! \n'
                              'Enter name of the team: ')
        if team_name == '':
            return read_request(data, tournament)
        else:
            return print_table(teams_matches[team_name])
    elif req == '2':
        date = input('\n'
                     'Enter the date in format DD/MM/YYYY: ')
        dates_matches = matches_at_date(data)
        while date not in dates_matches and date != '':
            date = input('\n'
                         'Not matches on this date, check the format.\n'
                         'Enter the date in format DD/MM/YYYY: ')
        if date == '':
            return read_request(data, tournament)
        else:
            return print_table(dates_matches[date])
    elif req == '3':
        return print_table((ranking_table(data, tournament)))
    elif req == '':
        return
    else:
        return read_request(data, tournament)


# Responses:
def goal_difference(data):
    goal_differ = dict()
    for match in data:
        team1 = match[HOME]
        team2 = match[AWAY]
        k = 1
        for team in [team1, team2]:
            goal_differ.setdefault(team, 0)
            goal_differ[team] += k * (int(match[HOME_GOALS]) - int(match[AWAY_GOALS]))
            k *= -1
    return goal_differ


def who_winner(winner, ranking, team1, team2):
    if winner == 'H':
        ranking[team1][WINS] += 1
        ranking[team1][PTS] += 3
        ranking[team2][LOSES] += 1
    elif winner == 'D':
        ranking[team1][DRAWS] += 1
        ranking[team1][PTS] += 1
        ranking[team2][DRAWS] += 1
        ranking[team2][PTS] += 1
    elif winner == 'A':
        ranking[team1][LOSES] += 1
        ranking[team2][WINS] += 1
        ranking[team2][PTS] += 3
    return ranking


def ranking_table(data, tournament):
    sorting_reqs = tournament[SORTING]
    ranking = dict()
    goal_differ = goal_difference(data)
    for match in data:
        home_team = match[HOME]
        away_team = match[AWAY]
        winner = match[WINNER]
        for each in [home_team, away_team]:
            ranking.setdefault(each, [0, 0, 0, 0, 0, 0])
            ranking[each][GAMES] += 1
        ranking = who_winner(winner, ranking, home_team, away_team)
    for each in ranking:
        ranking[each][GOAL_DIFFERENCE] = goal_differ[each]
    rank_list = []
    for key in ranking:
        team = [key] + ranking[key]
        rank_list.append(team)
    rank_list.sort(key=lambda x: x[PTS + 1], reverse=True)
    i = 1
    pos = 1
    while i < len(rank_list):
        cur_team_pts = rank_list[i - 1][PTS + 1]
        next_team_pts = rank_list[i][PTS + 1]
        if cur_team_pts == next_team_pts:
            team1 = rank_list[i - 1][NAME]
            team2 = rank_list[i][NAME]
            eq_pts_teams = [team1, team2]
            j = i + 1
            while cur_team_pts == rank_list[j][PTS + 1]:
                eq_pts_teams.append(rank_list[j][NAME])
                j += 1
            teams_order = tie_breaker(data, eq_pts_teams, sorting_reqs)
            cur_pos = pos
            for team in teams_order:
                k = i - 1
                while team[NAME] != rank_list[k][NAME] and k < j:
                    k += 1
                cur_pos = pos + team[NUM]
                rank_list[k] = [cur_pos] + rank_list[k]
            i = j + 1
            pos = cur_pos + 1
        else:
            rank_list[i - 1] = [pos] + rank_list[i - 1]
            pos += 1
            i += 1
    rank_list[i - 1] = [pos] + rank_list[i - 1]
    rank_list.sort(key=lambda x: x[POS])
    return rank_list


def matches_for_team(data):
    teams_matches = dict()
    for match in data:
        home_team = match[HOME]
        away_team = match[AWAY]
        for each in [home_team, away_team]:
            teams_matches.setdefault(each, list())
            teams_matches[each].append(tuple(match))
    return teams_matches


def matches_at_date(data):
    date_matches = dict()
    for match in data:
        date = match[DATE]
        date_matches.setdefault(date, [])
        date_matches[date].append(match)
    return date_matches


# Functions for printing responses:
def print_table(matrix):
    table = '\n'
    raws = []
    len_list = []
    for i in range(len(matrix[0])):
        len_list.append(max(len(str(x[i])) for x in matrix))
    for line in matrix:
        st = ''
        i = 0
        for word in line:
            word = str(word)
            space = len_list[i] - len(word) + 1
            st = st + word + space * ' '
            i += 1
        raws.append(st)
    return table.join(raws)


# Sorting criterion
def hth_matches(data, team1, team2):
    matches = matches_for_team(data)
    team1_matches = matches[team1]
    team2_matches = matches[team2]
    mutual_matches = list_intersection(team1_matches, team2_matches)
    return mutual_matches


def hth_goals(data, teams):
    pairs_of_teams = pairs_from_list(teams)
    difference = dict()
    for pair in pairs_of_teams:
        team1 = pair[TEAM1]
        team2 = pair[TEAM2]
        goal_differ = [0, 0]
        mutual_matches = hth_matches(data, team1, team2)
        for each in mutual_matches:
            if each[HOME] == team1:
                k = 1
            else:
                k = -1
            goal_differ[TEAM1] += k * (int(each[HOME_GOALS]) - int(each[AWAY_GOALS]))
            goal_differ[TEAM2] -= k * (int(each[HOME_GOALS]) - int(each[AWAY_GOALS]))
        difference.setdefault(team1, 0)
        difference[team1] += goal_differ[TEAM1]
        difference.setdefault(team2, 0)
        difference[team2] += goal_differ[TEAM2]
    result = []
    for each in teams:
        result.append((each, difference[each]))
    result.sort(key=lambda x: x[1], reverse=True)
    return result


def hth_pts(data, teams):
    pairs_of_teams = pairs_from_list(teams)
    teams_pts = {}
    for pair in pairs_of_teams:
        team1 = pair[TEAM1]
        team2 = pair[TEAM2]
        points = [0, 0]
        mutual_matches = hth_matches(data, team1, team2)
        for each in mutual_matches:
            if each[HOME] == team1:
                point1, point2 = TEAM1, TEAM2
            else:
                point1, point2 = TEAM2, TEAM1
            if each[WINNER] == 'H':
                points[point1] += 3
            elif each[WINNER] == 'D':
                points[point1] += 1
                points[point2] += 1
            else:
                points[point2] += 3
        teams_pts.setdefault(team1, 0)
        teams_pts[team1] += points[TEAM1]
        teams_pts.setdefault(team2, 0)
        teams_pts[team2] += points[TEAM2]
    result = []
    for each in teams:
        result.append((each, teams_pts[each]))
    result.sort(key=lambda x: x[1], reverse=True)
    return result


def goal_breaker(data, teams):
    goal_differ = goal_difference(data)
    result = []
    for team in teams:
        result.append((team, goal_differ[team]))
    result.sort(key=lambda x: x[1], reverse=True)
    return result


def hth_goals_scored(data, teams):
    result = []
    pairs_of_teams = pairs_from_list(teams)
    teams_goals = {}
    for pair in pairs_of_teams:
        team1 = pair[TEAM1]
        team2 = pair[TEAM2]
        mutual_matches = hth_matches(data, team1, team2)
        for match in mutual_matches:
            team1 = match[HOME]
            team2 = match[AWAY]
            k = HOME_GOALS
            for team in (team1, team2):
                teams_goals.setdefault(team, 0)
                teams_goals[team] += int(match[k])
                k = AWAY_GOALS
    for team in teams:
        result.append((team, teams_goals[team]))
    result.sort(key=lambda x: x[1], reverse=True)
    return result


def hth_away_goals_scored(data, teams):
    result = []
    pairs_of_teams = pairs_from_list(teams)
    teams_goals = {}
    for pair in pairs_of_teams:
        team1 = pair[TEAM1]
        team2 = pair[TEAM2]
        mutual_matches = hth_matches(data, team1, team2)
        for match in mutual_matches:
            team2 = match[AWAY]
            teams_goals.setdefault(team2, 0)
            teams_goals[team2] += int(match[AWAY_GOALS])
    for team in teams:
        result.append((team, teams_goals[team]))
    result.sort(key=lambda x: x[1], reverse=True)
    return result


def goals_scored(data, teams):
    goals = dict()
    all_matches = matches_for_team(data)
    result = []
    for team in teams:
        matches = all_matches[team]
        for match in matches:
            team1 = match[HOME]
            scoring = [match[HOME_GOALS], match[AWAY_GOALS]]
            goals.setdefault(team, 0)
            if team1 == team:
                goals[team] += int(scoring[0])
            else:
                goals[team] += int(scoring[1])
        result.append((team, goals[team]))
    result.sort(key=lambda x: x[1], reverse=True)
    return result


def away_goals_scored(data, teams):
    goals = dict()
    all_matches = matches_for_team(data)
    result = []
    for team in teams:
        matches = all_matches[team]
        for match in matches:
            team1 = match[HOME]
            scoring = [match[HOME_GOALS], match[AWAY_GOALS]]
            goals.setdefault(team, 0)
            if team1 != team:
                goals[team] += int(scoring[1])
        result.append((team, goals[team]))
    result.sort(key=lambda x: x[1], reverse=True)
    return result


def fair_play_scores(data):
    cards = dict()
    for match in data:
        index1 = HOME_YELLOW_CARDS
        index2 = HOME_RED_CARDS
        for team in (match[HOME], match[AWAY]):
            cards.setdefault(team, [0, 0])
            cards[team][YELLOW] += int(match[index1])
            cards[team][RED] += int(match[index2])
            index1 += 1
            index2 += 1
    scores = dict()
    for team in cards:
        scores[team] = cards[team][YELLOW] + 3 * cards[team][RED]
    return scores


def fair_play_comp(data, teams):
    scores = fair_play_scores(data)
    result = []
    for team in teams:
        result.append((team, scores[team]))
    result.sort(key=lambda x: x[1])
    return result


# Tie breaking functions:
def if_broken(result):
    check = result[0][SCORE]
    for j in range(1, len(result)):
        if result[j][SCORE] == check:
            return False, j - 1
        else:
            check = result[j][SCORE]
            j += 1
    return True, len(result)


def tie_breaker(data, teams, rules):
    ans = []
    methods = [hth_pts,
               hth_goals,
               fair_play_comp,
               goal_breaker,
               goals_scored,
               hth_goals_scored,
               hth_away_goals_scored,
               away_goals_scored]
    methods_order = sorted(zip(rules, methods), key=lambda x: x[0])
    while methods_order[0][POS] == 0:
        methods_order.pop(0)
    method_res = methods_order[0][METHOD](data, teams)
    checker = if_broken(method_res)
    teams_order = []
    i = 1
    while not checker[ANS] and i < len(methods_order):
        teams_order += method_res[:checker[TEAMS]]
        teams = [x[NAME] for x in method_res[checker[TEAMS]:]]
        method_res = methods_order[i][METHOD](data, teams)
        checker = if_broken(method_res)
        i += 1
    teams_order += method_res[:checker[TEAMS]]
    pos = 0
    for team in teams_order:
        ans.append((team[NAME], pos))
        pos += 1
    if not checker[ANS]:
        for team in method_res[checker[TEAMS]:]:
            ans.append((team[NAME], pos))
    return ans


try:
    dataFrames = []
    with open('tournaments.txt', 'r', encoding='utf-8') as f:
        toursList = []
        for line in f:
            toursList.append(line.strip().split(','))
    for each in toursList:
        locData = []
        for location in each:
            locData.append(read_csv(location))
        reqsFile = each[0].split('.')[0].strip('0123456789')
        with open(f'./requirements/{reqsFile}.txt', 'r', encoding='utf-8') as f:
            sortingReqs = [int(x.strip()) for x in f]
        dataFrames.append((locData, sortingReqs))
    userReq = first_request(dataFrames)
    while userReq is not None:
        userReq = first_request(dataFrames)
except:
    print('Some of files cannot be open')
