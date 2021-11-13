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
    # Index into screen list, then last element of screen list is the data we
    # need and then get the candidate list
    candidates = unlikely_json["screen-list"]
    candidates = candidates[len(candidates) - 1]

    # Check if list of candidates exists
    if "candidate-list" in candidates:
        candidates = candidates["candidate-list"]
    else:
        return []

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
    # Trim opening and closing square bracket
    response = response[1 : len(response) - 1]

    # Split response into a list of responses - answers with explanations
    responses = response.split(',')
    solutions = []

    for i in range(len(responses)):
        solution = responses[i]
        # Trim quotes
        solution = solution[1 : len(solution) - 1]
        # Split into answer and explanation
        solution = solution.split(':')
        # Get rid of whitespace in answer
        solution[0] = solution[0].replace(" ", "")

        # Build dictionary in desired format
        sol = {}
        sol["answer"] = solution[0]
        sol["confidence"] = 1.0 / len(responses)
        sol["explanation"] = solution[1]

        solutions.append(sol)

    return solutions

def combine_solutions(hs_solutions, unlikely_solutions):
    """
    Takes the two lists of solutions produced from the Haskell solver
    and the Unlikely solver and adds all not duplicated Haskell solutions to
    the Unlikely solutions.

    returns the Unlikely solutions
    """
    for hs_sol in hs_solutions:
        is_duplicate = False
        for uai_sol in unlikely_solutions:
            if hs_sol["answer"] == uai_sol["answer"]:
                is_duplicate = True
                break;

        if not is_duplicate:
            unlikely_solutions.append(hs_sol)

    return unlikely_solutions
