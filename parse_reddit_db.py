#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sqlite3
import requests
import enchant

english_enchant = enchant.Dict("en_US")


def append_result(text, label):
    """
    appends text and label to objectivity.json
    """
    a_dict = {'text': text, 'label': label}

    with open('objectivity.json') as f:
        data = json.load(f)

    data.append(a_dict)

    with open('objectivity.json', 'w') as f:
        json.dump(data, f)


def text_in_dataset(text):
    """
    returns true if text is already in the json dataset
    false otherwise
    """
    with open('objectivity.json') as f:
        data = json.load(f)
    for x in data:
        if x['text'] == text:
            return True
    return False


def is_english(text):
    """
    returns true if text is mostly english, false otherwise
    """
    words = set([x for x in text.split(' ') if x.strip() != ''])
    scores = []
    for word in words:
        if english_enchant.check(word):
            scores.append(1)
        else:
            scores.append(0)
    score = sum(scores) / len(scores)
    if score > .7:
        return True
    return False


def check_text(text):
    """
    checks text with ensemble of machine learning services
    and returns label if score is high enough
    """
    if not is_english(text):
        return 'not english'
    ports = ['5000', '5001']
    scores = []
    for port in ports:
        r = requests.post('http://0.0.0.0' + ':' + port, data={'text': text})
        scores.append(json.loads(r.text)['objectivity'])
    score = sum(scores) / len(scores)
    if score > .85:
        # objective
        label = 'objective'
    elif score < .5:
        # subjective
        label = 'subjective'
    else:
        label = 'error rate'
    return label


con = sqlite3.connect('/media/glen/Seagate Backup Plus Drive/redditcomments.sqlite')
with con:

    cur = con.cursor()
    cur.execute("SELECT * FROM May2015;")
    for i in range(100000):
        rows = cur.fetchone()
        text = rows[17]
        if not text_in_dataset(text):
            print(text)
            label = check_text(text)
            if label != 'error rate' and label != 'not english':
                append_result(text, label)
                print(label)
            elif label == 'not english':
                print('Text is mostly not English')
            else:
                print('Ensemble score falls into the error rate between objective and subjective')
        else:
            print('Text already in dataset, skipping.')
