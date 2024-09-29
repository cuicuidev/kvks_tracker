def match(score, array):
    closest_index = 0
    for idx, elem in enumerate(array):
        if elem <= score:
            closest_index = idx + 1
        else:
            break
    return closest_index


def choose(index, *args):
    return args[index - 1] if 0 < index <= len(args) else 0