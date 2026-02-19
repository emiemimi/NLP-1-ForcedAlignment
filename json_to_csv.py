import os
import json


def get_to_csv(file):
    with open(file) as f:
        data = json.load(f)
    name, ext = os.path.splitext(file)
    newfile = name + '.csv'
    with open(newfile, 'w') as f:
        f.write('start;end;utterance\n')
        segments_lst = data['segments']
        for sentence_dict in segments_lst:
            for word_dict in sentence_dict['words']:
                line = ';'.join([str(word_dict['start']), str(word_dict['end']), word_dict['word']])
                f.write(line + '\n')


files = [
    'data/Whisper/sentence3_whisper.json',
    'data/Whisper/s1102a_whisper.json',
    'data/Whisper/s1701a_whisper.json'
]

for file in files:
    get_to_csv(file)

