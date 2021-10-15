def matching(pattern, responses):
    result = []
    for response in responses:
        match = True
        for k,v in pattern.items():
            if (response[k] != v):
                match = False
                break
        if (match):
            result.append(response)
    return result

def getFromList(text):
    text = text.translate({ord(i): None for i in '[]\"\' '})
    #print(text)
    #print(text.split(','))
    return text.split(',')

#getFromList("[california, mem, weewooweewoo]")