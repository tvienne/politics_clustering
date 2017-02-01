"""
Toolbox for XML us senators votes parsing
"""
import re
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


def handle_measures_and_questions(full_xml_str):
    """
    Handles xml parsing when field <measure> is nested in <question> field
    Examples : <question> .. <measure> text </measure> </question> => <question> ... </question>
    :param full_xml_str full xml with file format string
    :return: Cleaned xml without <measure> fields
    """
    clean_xml = re.sub(r"\n<measure>.*</measure>\n", r"", full_xml_str)
    clean_xml = re.sub(r"<question>\n", r"<question>", clean_xml)
    clean_xml = re.sub(r";", r",", clean_xml)

    return clean_xml


def remove_xml_typo(line):
    """
    Removes xml encapsulation '<...>' and "</...>" given string row
    :param line: string row
    :return: string row without xml pattern
    """
    cleaned_line = re.findall('>.*<', line)
    if cleaned_line:
        return cleaned_line[0][1:-1]
    else:
        return "null"


def fill_missing_titles(titles, votes):
    """
    Fill titles with "null" in case of a missing title
    :param titles: titles list with format [[vote_1, title_1], [vote_2, title_2]]
    :param votes: votes numbers list : [1, 2 ... n]
    :return: titles with added missing titles
    """
    # If needed  Add null values to missing titles :
    votes_indexes = [votes.index(element) for element in votes]
    for vote_index in votes_indexes:
        if titles[vote_index][0] != votes[vote_index]:
            print("Insert null value in field description for vote number : %s" % votes[vote_index])
            titles.insert(vote_index, [votes[vote_index], "null"])

    return titles


def check_parsing(vote_numbers_list, dates, questions, issues, descriptions, yeas, nays):
    """
    Checking parsing results by comparing the adequation between the information and the vote number
    (To success, all fields excepts vote_numbers_list have to be in format [[vote_numbers_list[0], field_0], ...
    [vote_numbers_list[n], field_n]])
    :param vote_numbers_list: vote number list
    :param dates: votes dates list
    :param questions: amendments questions list
    :param issues: issues list
    :param descriptions: description list
    :param yeas: yeas list
    :param nays: nays list
    :return: No return
    """

    # Checking CSV fields according to vote_number
    print("----- Checking parsing results :")
    fields_list = ["dates", "questions", "issues", "descriptions", "yeas", "nays"]
    field_counter = 0
    for field in (dates, questions, issues, descriptions, yeas, nays):
        field_name = fields_list[field_counter]
        for vote, element in zip(vote_numbers_list, field):
            # print("check field %s, on vote number %s" % (field_name, vote))
            if vote != element[0]:
                print("ERROR : on field %s, about vote number %s" % (field_name, vote))
                print("element : %s" % element[1])
                raise ValueError("ERROR on parsing")
        field_counter += 1
    print(">>> SUCCESS")


def assemble_to_csv(votes, dates, questions, issues, titles, yeas, nays):
    """
    Assembles csv from list to list to big csv string
    :param votes: vote numbers
    :param dates: votes dates
    :param questions: questions
    :param issues: issues
    :param titles: titles
    :param yeas: yeas
    :param nays: nayx
    :return: Assembled CSV
    """

    # Assembling information to CSV
    votes_date = [element[1] for element in dates]
    questions = [element[1] for element in questions]
    issues = [element[1] for element in issues]
    descriptions = [element[1] for element in titles]
    yeas = [element[1] for element in yeas]
    nays = [element[1] for element in nays]
    csv = ["vote_id;vote_date;question;issue;title;yeas;nays"]
    for vote_id, vote_date, question, issue, title, yea, nay in zip(votes, votes_date, questions, issues,
                                                                    descriptions, yeas, nays):
        csv.append("%s;%s;%s;%s;%s;%s;%s" % (vote_id, vote_date, question, issue, title, yea, nay))

    return csv


def calculate_distance_name(votes, senator_name_1, senator_name_2):
    """
    Computes euclidian distance between two senators based on their vote for different laws
    given their respective names.
    """
    senator_1_votes = votes[votes["name"] == senator_name_1].iloc[0, 3:].reshape(1, -1)
    senator_2_votes = votes[votes["name"] == senator_name_2].iloc[0, 3:].reshape(1, -1)
    distance = float(euclidean_distances(senator_1_votes, senator_2_votes)[0])
    return distance


def distance_sen_dem_rep(votes, senator_name):
    """
    Returns distances senator-democrats, senator-republicans.
    :param votes: votes dataframe
    :param senator_name:  senator name
    :return: distance_sen_democrats, distance_sen_republicans
    """
    # Get democrats and republicans lists
    democrat_names_list = list(votes[votes["party"] == "D"].name)
    republican_names_list = list(votes[votes["party"] == "R"].name)

    # Computing the mean distance between Angus and these two party
    democrat_distances = []
    republican_distances = []
    for democrat in democrat_names_list:
        democrat_distances.append(calculate_distance_name(votes, democrat, senator_name))
    for republican in republican_names_list:
        republican_distances.append(calculate_distance_name(votes, republican, senator_name))
    democrat_mean_distance = np.mean(democrat_distances)
    republican_mean_distance = np.mean(republican_distances)

    return democrat_mean_distance, republican_mean_distance


def plot_party_cross(plot, crosstab, amendment_number, legend=False):
    """
    Plot a senator crosstab using differents colors for each party
    :param plot: matplotlib.plot object
    :param crosstab: pandas crosstab
    :param amendment_number: (string) amendment number.
    :param legend : (boolean) wheter or not plot legend
    :return:
    """
    # Making indexes
    democrat_index = [index - 0.05 for index in crosstab.index]
    republican_index = crosstab.index
    independant_index = [index + 0.05 for index in crosstab.index]

    # Plot
    plot.bar(democrat_index, crosstab["D"], width=0.05, color="b")
    plot.bar(republican_index, crosstab["R"], width=0.05, color="r")
    plot.bar(independant_index, crosstab["I"], width=0.05, color="g")

    plot.set_title("Motion %s votes results" % amendment_number, fontsize=10)
    plot.set_xlabel("votes")
    plot.set_xticks([0, 0.5, 1])
    plot.set_xticklabels(["0 (no)", "0.5 (unknown)", "1 (yes)"])
    plot.set_ylabel("count")
    if legend:
        rep_leg = mpatches.Patch(color='red', label='republicans')
        dem_leg = mpatches.Patch(color='blue', label='democrats')
        ind_leg = mpatches.Patch(color='green', label='independents')
        plot.legend(handles=[rep_leg, dem_leg, ind_leg], loc=9, prop={'size': 7})


def count_absent_votes(row):
    """
    (pandas apply function). Counts vote absences per senator searching vor 0.5 values.
    :param row: row from dataframe
    """
    absent = sum([1.0 * (vote == 0.5) for vote in row])
    return absent


def apply_color(party):
    """
    (pandas apply function) : maps a  pyplot color to every senator according to his party.
    :param party: party element
    :return: color
    """
    if party == "R":
        return "r"
    elif party == "D":
        return "b"
    elif party == "I":
        return "g"
    else:
        raise ValueError("party unknown")


def map_motions_columns(votes):
    """
    Maps comprehensible columns names for votes
    :param votes: votes dataframe
    :return: returns votes with mapped columns names.
    """
    votes.columns = ["motion_%s" % int(col) if '00' in col else col for col in votes.columns]
    return votes


def plot_cartography(plot, votes, legend=False, legend_size=10):
    cluster0_x = votes[votes["cluster"] == 0]["clust0_jitter"]
    cluster0_y = votes[votes["cluster"] == 0]["clust1_jitter"]
    colors_0 = votes[votes["cluster"] == 0]["party"].apply(lambda el: apply_color(el))

    cluster1_x = votes[votes["cluster"] == 1]["clust0_jitter"]
    cluster1_y = votes[votes["cluster"] == 1]["clust1_jitter"]
    colors_1 = votes[votes["cluster"] == 1]["party"].apply(lambda el: apply_color(el))

    plot.scatter(cluster0_x, cluster0_y, s=30, c=colors_0, marker="o")
    plot.scatter(cluster1_x, cluster1_y, s=30, c=colors_1, marker="s")
    plot.set_xlabel("distance to cluster 0")
    plot.set_ylabel("distance to cluster 1")

    if legend:
        republican_legend = mpatches.Patch(color='red', label='republicans')
        democrat_legend = mpatches.Patch(color='blue', label='democrats')
        clust0_legend = mlines.Line2D([], [], color="white", marker='o',
                                      markersize=10, label='cluster 0')
        clust1_legend = mlines.Line2D([], [], color='white', marker='s',
                                      markersize=10, label='cluster 1')

        plot.legend(handles=[republican_legend, democrat_legend, clust0_legend, clust1_legend],
                   prop={'size': legend_size}, loc=3)


def plot_senator(ax, votes, senator_name, senator_title, legend=False, legend_size=5):
    """
    Plots a senator on a matplotlib object using his name
    :param ax: matplotlib.pyplot object.
    :param votes: votes dataframe
    :param senator_name: name of senator.
    :param senator_title: title to give to the vizualisation.
    :param legend: (boolean) whether ot not display cartography legend
    :param legend_size : (integer) cartography legend size.
    :return:
    """
    # Plot cartography :
    plot_cartography(ax, votes, legend, legend_size)

    # Find senator coordinates:
    senator_x = votes[votes["name"] == senator_name]["clust0_jitter"]
    senator_y = votes[votes["name"] == senator_name]["clust1_jitter"]
    senator_color = "y"
    senator_marker = "h"

    ax.scatter(senator_x, senator_y, s=100, c=senator_color, marker=senator_marker)
    ax.set_title("%s" % senator_title)

