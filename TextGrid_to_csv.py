import os

def get_items(data):
    nb_items = int(data[6].strip('\n')[7:]) # get i from the 7th line ('size = i')
    items = []
    i = 9
    for j in range(nb_items):
        i, lst = get_subitems(data, i)
        items.append(lst)
    return items

def get_subitems(data, start_index):
    lst = []
    temp = []
    i = start_index + 6
    while i < len(data):
        if len(data[i]) >= 4 and data[i][4] == ' ':  # this line is NOT a new item?
            if data[i][8] == ' ':  # this line is NOT a new subitem?
                # collect value to temp, as float if possible
                value = data[i].split(' = ')[1].strip(' "\n')
                try:
                    temp.append(float(value))
                except:
                    temp.append(value)
            else:
                if len(temp) > 0:
                    lst.append(tuple(temp))  # add temp as tuple to lst
                    temp = []  # empty temp
            i += 1
        else:
            break
    lst.append(tuple(temp))  # don't forget the last tuple!
    return i, lst

files = [
    'data/gold/sentence3_manual.TextGrid',
    'data/MAUS/sentence3_MAUS.TextGrid',
    'data/MAUS/s1102a_MAUS.TextGrid',
    'data/MAUS/s1701a_MAUS.TextGrid'
]

for file in files:
    with open(file) as f:
        raw = f.readlines()
        data = get_items(raw)
    name, ext = os.path.splitext(file)
    lst = ['_words', '_grouped_phonemes', '_phonemes']
    for i in range(len(data)):
        newfile = name + lst[i] + '.csv'
        with open(newfile, 'w') as f:
            f.write('start;end;utterance\n')
            for tpl in data[i]:
                line = ";".join([str(x) for x in tpl])
                f.write(line + '\n')