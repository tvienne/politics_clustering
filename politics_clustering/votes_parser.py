from functions import *

#################################
#  variables                  ###
#################################

input_file = "amendments_114_1.txt"
output_file = "votes_description_114_1.csv"

#################################
#  Main                       ###
#################################

# Loading XML and loading with impurities
in_file = open(input_file, "r")
votes_str = in_file.read()
votes_str = handle_measures_and_questions(votes_str)
amendments = votes_str.split("\n")

# Parsing XML :
xml_info = []
csv_info = []
votes = []
dates = []
issues = []
questions = []
results = []
yeas = []
nays = []
titles = []
pass_patterns = ["<?xml", "<vote_summary>", "</vote_summary>", "<votes>", "</votes>", "<vote>", "</vote>",
                 "<vote_tally>", "</vote_tally>"]
csv_info_patterns = ["<congress>", "<session>", "<congress_year>"]
vote_number = 0
for row in amendments:
    if [pattern for pattern in pass_patterns if pattern in row]:
        pass
    elif [pattern for pattern in csv_info_patterns if pattern in row]:
        csv_info.append(remove_xml_typo(row))
    elif "<vote_number>" in row:
        votes.append(int(remove_xml_typo(row)))
        vote_number = int(remove_xml_typo(row))
    elif "<vote_date>" in row:
        dates.append([vote_number, remove_xml_typo(row)])
    elif "<issue>" in row:
        issues.append([vote_number, remove_xml_typo(row)])
    elif "<question>" in row:
        questions.append([vote_number, remove_xml_typo(row)])
    elif "<yeas>" in row:
        yeas.append([vote_number, remove_xml_typo(row)])
    elif "<nays>" in row:
        nays.append([vote_number, remove_xml_typo(row)])
    elif "<result>" in row:
        results.append([vote_number, remove_xml_typo(row)])
    elif ("<title>" in row and "</title>" not in row) or ("<title>" not in row and "</title>" in row):
        #  handles <title>\n...\n</title>
        pass
    elif "<title>" in row and "</title>" in row:
        # handles <title>...</title>
        titles.append([vote_number, remove_xml_typo(row)])
    else:
        titles.append([vote_number, row])

# check parsing :
check_parsing(votes, dates, questions, issues, titles, yeas, nays)


# Write csv :
csv = assemble_to_csv(votes, dates, questions, issues, titles, yeas, nays)
csv_str = "\n".join(csv)
out_file = open(output_file, "w")
out_file.write(csv_str)

# Close files
in_file.close()
out_file.close()
