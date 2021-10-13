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