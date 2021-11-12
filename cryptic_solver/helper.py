import json

english_dict = {}

def load_words():
    dict = {}
    with open('cryptic_solver/words_alpha.txt') as word_file:
        for w in word_file.read().split():
            length = len(w)
            res = dict.get(length)
            if (res == None):
                dict.update({length: [w]})
            else:
                res.append(w)
    return dict.copy()

def matching(pattern, responses):
    result = []
    for response in responses:
        match = True
        for k,v in pattern.items():
            if (response[int(k)] != v):
                match = False
                break
        if (match):
            result.append(response)
    return result

def makeList(text):
    text = text.translate({ord(i): None for i in '[]\"\' '})
    return text.split(',')

def getCandidates(pattern, word_length):
    global english_dict
    if english_dict == {}:
        english_dict = load_words()
    return matching(pattern, english_dict.get(word_length))

def getExplanation(response_text):
    response_text = response_text.translate({ord(i): None for i in '\"\''})
    if response_text == "[]":
        return ""
    split = response_text.split(':')
    explanation = split[1].strip()
    return explanation[:-1]

def get_most_confident(solutions):
    max = 0
    solution = ""
    for candidate in solutions:
        confidence = float(candidate['confidence'])
        if confidence > max:
            max = confidence
            solution = candidate['candidate']

    return solution

def format_word_length(word_length):
    return f"({str(word_length)})"


def parse_unlikely_with_explanations(unlikely_json):
    """
    Parses the json from the call to unlikely.ai API and build list of solutions
    with explanations
    """
    # Index into screen list, then second element of screen list is the data we
    # need and then get the candidate list
    candidates = unlikely_json["screen-list"][1]["candidate-list"]

    # The minimum confidence an answer must have in order to be returned
    # to frontend
    minimum_confidence = 0.05

    answers = []

    for candidate in candidates:
        if candidate["confidence"] >= minimum_confidence:
            answer = {"answer" : candidate["candidate"], \
                        "confidence" : candidate["confidence"], \
                        "explanation" : candidate["explanation"]}
            answers.append(answer)

    return answers

def format_haskell_answers(response):
    """
    Response from haskell server is in the form:
    ["<answer with explanation>", "<answer with explanation>", ...]
    """
    # response = response.translate({ord(i): None for i in '[]\"\' '})

    # Trim opening and closing square bracket
    response = response[1, len(response) - 1]

    # Split response into a list of solutions - answers with explanations
    solutions = response.split(',')
    for solution in solutions:
        # Trim quotes
        solution = solution[1, len(solution) - 1]
        # Split into answer and explanation
        solution = solution.split(':')
        # Get rid of whitespace in answer
        solution[0] = solution[0].replace(" ", "")


    return solutions
