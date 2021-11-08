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