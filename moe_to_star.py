#!/usr/bin/python 
# -*- coding: utf-8 -*-
import json
import os


class StarFormat:
    def __init__(self, json_path):
        self.json_path = json_path
        # {"word":[0, 10]}
        self.moe_idx_dict = {}
        # dict bytes
        self.moe_dict = b''
        self.offset = 0

    def idx_file(self):
        print("==== gen idx file ====")
        with open('./moe.idx', 'ab') as out:
            for k in self.moe_idx_dict:
                out.write(k.encode('utf-8'))
                out.write(b'\x00')
                arr = self.moe_idx_dict[k]
                out.write(arr[0].to_bytes(4, 'big'))
                out.write(arr[1].to_bytes(4, 'big'))

    def dict_file(self):
        print("==== gen dict file ====")
        with open('./moe.dict', 'ab') as out:
            out.write(self.moe_dict)

    def ifo_file(self):
        print("==== gen ifo file ====")
        content = "StarDict's dict ifo file\n"
        content += "version=2.4.2\n"
        content += "wordcount="
        content += str(len(self.moe_idx_dict))
        content += "\n"
        content += "idxfilesize="
        idx_file_size = os.path.getsize("./moe.idx")
        content += str(idx_file_size)
        content += "\n"
        content += "bookname=萌典\n"
        content += "sametypesequence=m\n"
        with open('./moe.ifo', 'a') as out:
            out.write(content)

    def parse_moe_json(self):
        f = open(self.json_path)
        data = json.load(f)
        lc = 0
        for word in data:
            title = word['title']
            # skip PUA code
            if '{' in title:
                continue
            data = word_data(word)
            data_bytes = data.encode('utf-8')
            size = len(data_bytes)
            arr = [self.offset, size]
            self.moe_idx_dict[title] = arr
            self.moe_dict += data_bytes
            self.offset = len(self.moe_dict)
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
    star_dict = StarFormat("./dict-revised.json")
    star_dict.parse_moe_json()
    star_dict.idx_file()
    star_dict.dict_file()
    star_dict.ifo_file()
