import os


def get_to_csv(file, type):
    if type == '_words':
        j = 3
        k = 0
    else:
        j = 4
        k = 1
    with open(file) as f:
        data = f.readlines()[9:]
    name, ext = os.path.splitext(file)
    newfile = name + type + '.csv'
    with open(newfile, 'w') as f:
        f.write('start;end;utterance\n')
        for i in range(len(data) - 1):
            start = data[i][j:].split(' ')[0]
            end = data[i + 1][j:].split(' ')[0]
            utterance = data[i][j:].split(' ')[2+k].strip(';\n')
            line = ';'.join([start, end, utterance])
            f.write(line + '\n')


files = [
    'data/gold/s1102a.words',
    'data/gold/s1102a.phones',
    'data/gold/s1701a.words',
    'data/gold/s1701a.phones'
]

get_to_csv(files[0], '_words')
get_to_csv(files[1], '_phones')
get_to_csv(files[2], '_words')
get_to_csv(files[3], '_phones')