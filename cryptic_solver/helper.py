import json
from cryptic_solver.trie import Trie

english_dict = None

def load_words():
    """
    Populates a dictionary with all English words.

    Returns:

    A dict containing all words from words_alpha.txt
    """
    trie = Trie()
    with open('cryptic_solver/words_alpha.txt') as word_file:
        for w in word_file.read().split():
            trie.add(w)
    return trie

def matching(pattern, responses):
    """
    Filters a list of possible solutions based on known letters.
    Parameters:
    pattern: a string with known letters and underscores for unknown letters
             For example, _A_C_E
    responses: a list of strings, all of which are potential solutions to the clue
    Returns:
    result: a list of the solutions from responses that match the given pattern
    """
    result = []
    for response in responses:
        if (matches_pattern(response, pattern)):
            result.append(response)
    return result

def make_list(text):
    """
    Converts the raw text output from the Haskell server into a Python list for
    packaging into a JSON format.

    Parameters:

    text: the raw text response from the Haskell server, containing all returned solutions

    Returns:

    A Python list of those same solutions
    """
    text = convert_from_unicode(text)
    text = text.translate({ord(i): None for i in '[]\"\' '})
    return text.split(',')

def get_candidates(pattern, word_length):


    search_string = pattern.replace("?", "_")
    # # for i in range(word_length):
    # #     # if str(i) in pattern:
    # #     #     search_string += str.lower(pattern[str(i)])
    # #     # # elif i in pattern:
    # #     # #     search_string += str.lower(pattern[i])
    # #     # else:
    # #     #     search_string += '_'
    # #     if pattern[i] == '?':
    # #         pattern[i] = "_"

    # print("search string:", search_string)
    search_string = search_string.lower()

    global english_dict
    if english_dict == None:
        english_dict = load_words()
    result = english_dict.search(search_string)
    return result

def get_explanation(response_text):
    """
    Extracts the explanation given by the Haskell code from a HTTP response from the server.

    Parameters:

    text: the raw text response from the Haskell server, containing the solution and its explanation

    Returns:

    A Python singleton list of the explanation given for the solution
    """
    response_text = convert_from_unicode(response_text)
    response_text = response_text.translate({ord(i): None for i in '\"\''})
    if response_text == "[]":
        return ""
    split = response_text.split(':')
    explanation = split[1].strip()
    return explanation[:-1]

def get_most_confident(solutions):
    """
    Filters all the solutions given by the Unlikely solver, returning the one with the most confidence

    Parameters:

    solutions: a JSON object containing a list of candidate solutions, each with an associated confidence score

    Returns:

    solution: the most confident solution from all those given in solutions
    """
    max = 0
    solution = ""
    for candidate in solutions:
        confidence = float(candidate['confidence'])
        if confidence > max:
            max = confidence
            solution = candidate['candidate']

    return solution

def format_word_length(word_length):
    """
    Formats the given word_length for use with the Unlikely solver.

    Parameters:

    word_length: the length of the solution

    Returns:

    The given word_length wrapped in parentheses
    """
    return f"({str(word_length)})"


def parse_unlikely_with_explanations(unlikely_json):
    """
    Parses the json from the call to unlikely.ai API and build list of solutions
    with explanations.

    Parameters:

    unlikely_json: The JSON object returned from the Unlikely solver

    Returns:

    answers: a list of dict objects corresponding to candidate solutions with a confidence greater than a minimum threshold
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
                        "explanation" : candidate["explanation"], \
                        "source": "unlikely"}
            answers.append(answer)

    return answers

def format_haskell_answers(response):
    """
    Formats the response from the Haskell server to match those from the Unlikely solver,
    associating a confidence score with each

    Parameters:

    response: Response from the Haskell server of the form:
    ["<answer with explanation>", "<answer with explanation>", ...]

    Returns:

    solutions: A list of dict objects, each corresponding to one of the solutions and containing
               answer, explanation and confidence keys.
    """
    # Check if response is not empty
    if response == "[]":
        return []

    response = convert_from_unicode(response)

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
        sol["source"] = "morse"

        solutions.append(sol)

    return solutions

def combine_solutions(unlikely_solutions, hs_solutions):
    """
    Takes the two lists of solutions produced from the Haskell solver
    and the Unlikely solver and adds all not duplicated Haskell solutions to
    the Unlikely solutions.

    Parameters:

    hs_solutions: the solutions from the Haskell solver

    unlikely_solutions: the solutions from the Unlikely solver

    Returns:

    the union of the Unlikely solutions with the Haskell solutions
    """
    hs_answers = set(map(lambda s: s["answer"].lower(), hs_solutions))
    print(hs_solutions)
    for unlikely_sol in unlikely_solutions:
        if not unlikely_sol["answer"].lower() in hs_answers:
            hs_solutions.append(unlikely_sol)

    return hs_solutions

def filter_by_pattern(solutions, pattern):
    # Given a list of solutions, will filter them by whether they match a given pattern
    filtered = []
    for solution in solutions:
        answer = solution["answer"]
        # Since the unlikely solver returns two word answers with a dash or space between words,
        # we get rid of that dash or space
        answer = answer.replace("-", "")
        answer = answer.replace(" ", "")

        if matches_pattern(answer, pattern):
            filtered.append(solution)
    return filtered

def matches_pattern(answer, pattern):
    # Assumes length of answer is the same as length of pattern
    answer_upper = answer.upper().translate({ord(i): None for i in '\"\''})
    for i in range(len(answer_upper)):
        if pattern[i] != '?' and pattern[i] != '_' and answer_upper[i] != pattern[i]:
            return False
    return True

def convert_from_unicode(text):
    """

    Converts decimal encodings of non-ASCII characters in the response text from the Haskell solver into the
    corresponding characters.

    Parameters:

    text: the text of the response from the Haskell solver.

    Returns:

    text: the same text modified with the properly encoded characters

    """
    encodings = []
    for i, char in enumerate(text):
        if char == '\\':
            code = ""
            j = i + 1
            while j < len(text) and text[j].isdigit():
                code += text[j]
                j += 1
            encodings.append(int(code))

    for code in encodings:
        text = text.replace("\\" + str(code), chr(code))
    return text
