#!/usr/bin/python 
# -*- coding: utf-8 -*-
import json
import os

# {"word": [0, 12]}
moe_idx_dict = {}
moe_dict = b''
offset = 0


def ifo_file():
    print("==== gen ifo file ====")
    content = "StarDict's dict ifo file\n"
    content += "version=2.4.2\n"
    content += "wordcount="
    content += str(len(moe_idx_dict))
    content += "\n"
    content += "idxfilesize="
    idx_file_size = os.path.getsize("./moe.idx")
    content += str(idx_file_size)
    content += "\n"
    content += "bookname=萌典\n"
    content += "sametypesequence=m\n"
    with open('./moe.ifo', 'a') as out:
        out.write(content)


def idx_file():
    print("==== gen idx file ====")
    with open('./moe.idx', 'ab') as out:
        for k in moe_idx_dict:
            out.write(k.encode('utf-8'))
            out.write(b'\x00')
            arr = moe_idx_dict[k]
            out.write(arr[0].to_bytes(4, 'big'))
            out.write(arr[1].to_bytes(4, 'big'))


def dict_file():
    print("==== gen dict file ====")
    with open('./moe.dict', 'ab') as out:
        out.write(moe_dict)


def parse_moe_json():
    f = open("./dict-revised.json")
    data = json.load(f)
    lc = 0
    for word in data:
        title = word['title']
        # skip PUA code
        if '{' in title:
            continue
        data = word_data(word)
        global moe_dict
        data_bytes = data.encode('utf-8')
        size = len(data_bytes)
        global offset
        arr = [offset, size]
        moe_idx_dict[title] = arr
        moe_dict += data_bytes
        offset = len(moe_dict)
        lc += 1
        if lc % 10000 == 0:
            print("Deal word: " + str(lc))
    f.close()


def word_data(word):
    data = ''
    data += word['title']
    data += '\n'
    heteronyms = word['heteronyms']
    for hm in heteronyms:
        if 'pinyin' in hm:
            data += hm['pinyin']
            data += '\n'
        if 'bopomofo' in hm:
            data += hm['bopomofo']
            data += '\n'
        if 'definitions' in hm:
            definitions = hm['definitions']
            for definition in definitions:
                if 'def' in definition:
                    data += definition['def']
                    data += '\n'
                if 'link' in definition:
                    for lnk in definition['link']:
                        data += lnk
                        data += '\n'
                if 'example' in definition:
                    for e in definition['example']:
                        data += e
                        data += '\n'
                if 'quote' in definition:
                    for qt in definition['quote']:
                        data += '  '
                        data += qt
                        data += '\n'
                if 'synonyms' in definition:
                    data += '近义词: '
                    data += definition['synonyms']
                    data += '\n'
                if 'antonyms' in definition:
                    data += '反义词: '
                    data += definition['antonyms']
                    data += '\n'
                data += '\n'
    return data


if __name__ == '__main__':
    parse_moe_json()
    idx_file()
    dict_file()
    ifo_file()


