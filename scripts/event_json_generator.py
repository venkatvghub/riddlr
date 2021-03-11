#!/usr/bin/env python
import json
fp = open("a.json","r")
data = json.load(fp)
fp.close()
formatted = []
index = 1
for item in data:
    title = item['Title']
    source = item['Title']
    text = item['Text']
    answers = item['Answer'].split('\n')
    media = item['Media']
    path = title.replace(' ','-').lower()
    tmp = {
            'index': index,
            'title': title,
            'source': source,
            'text': text,
            'answer': {
                    'case': False,
                    'hints': [],
                    'choices': answers
                    },
            'path': path
            }
    if media != '':
        tmp['media'] = {
                        'url': media,
                        'type': 'img'
                        }
    else:
        tmp['media'] = {}
    index += 1
    formatted.append(tmp)
foo_json = {
            'id': 'foo',
            'start': 1400000000,
            "intro": "A treasure hunt is one of many different types of games with one or more players who try to find hidden objects or places by following a series of clues. Treasure hunt games may be an indoor or outdoor activity.      Outdoors they can be played in a garden or the treasure could be located anywhere around the world.",
            "social": "https://example.com/example-company",
            "host": "example-company",
            "faq": "https://example.com/example-oth/faq",
            "discuss": "https://example.com/example-oth/forums",
            'finish': '',
            'name': 'Foo-Bar : RZP Platform Offsite Treasure Hunt',
            'levels': formatted
            }
print(json.dumps(foo_json))
