import requests
import urllib.parse

haskellURL = "http://84.238.224.41:5001"

def solveClue(clue, solutionLength):
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{haskellURL}/solve/{clue}/{solutionLength}"

    r = requests.get(url=fullURL)


    print(unlist(r.text))
    return unlist(r.text)

def solveWithAnswer(clue, solutionLength, answer):
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{haskellURL}/solveWithAnswer/{clue}/{solutionLength}/{answer}"

    r = requests.get(url=fullURL)

    print(unlist(r.text))
    return unlist(r.text)


def unlist(response):
    return response[2:-2]

if __name__ == "__main__":
    solveClue("Peeling paint, profit slack, upset, in a state", 10)
    solveClue("Following kick-off, running back for corner", 4)
    solveWithAnswer("Peeling paint, profit slack, upset, in a state", 10, "california")
