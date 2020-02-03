#!/usr/bin/env python
# coding: utf-8
# import libraries
import pytextrank
import networkx as nx
import operator
import json
import math
import logging
import sys

import spacy
nlp = spacy.load("en_core_web_sm")

import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger("PyTR")


# Add PyTextRank into the spaCy pipeline
tr = pytextrank.TextRank(logger=None)
nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)


# Now instead of walking through the entire Dir, try on one JSON file first.
json_path = 'PE_sample.pdf.json'
with open(json_path, 'r', encoding='utf-8') as jsonfile:
    json_string = json.load(jsonfile)


# Parse the JSON and convert it to Txt, devided by sections, and extract the title of the section
def FindObject(json):
    texts = []
    res = []
    titles = []
    for page in json['pages']:
        for element in page['elements']:
            try:    
                if element['type'] == 'heading':
                    title = GetText(element)
                    titles.append(title)
                    texts.append(res)
                    res = []
                if element['type'] in ['word', 'line', 'character', 'paragraph', 'heading', 'list']:
                    res.append(element)
            except TypeError:
                continue
    texts.append(res)
    return texts, titles


def GetText(text_object):
    result = ""
    if text_object['type'] in ['paragraph','heading','list']:
        for i in text_object['content']:
            result += GetText(i)
    if text_object['type'] in ['line']:
        for i in text_object['content']:
            result += GetText(i)
    elif text_object['type'] in ['word']:
        if type(text_object['content']) is list:
            for i in text_object['content']:
                result += GetText(i)
        else:
            result += text_object['content']
            result += ' '
    elif text_object['type'] in ['character']:
        result += text_object['content']
    return result                


# Get the text  
text = ""
sections = []
text_lists, titles = FindObject(json_string)
for text_list in text_lists:
    for text_Obj in text_list:
        text += GetText(text_Obj)
        text += '\n\n'
    sections.append(text)
    text = ""


# Now run textrank and save the output 
Output = []
for i, section in enumerate(sections[1:]):
    Dict = {}
    Final = {}

    doc = nlp(section)
    for phrase in doc._.phrases[:15]:
        Dict[phrase.text] = {'count': phrase.count, 'rank_score': phrase.rank}
 
    Final['section_title'] = titles[i]
    Final['text_rank'] = Dict
    
    Output.append(Final)
    print('\n----------\n')


# Output the rank result to JSON 
with open('output_sample1.json', 'w', encoding="utf-8") as outfile:
    json.dump(Output, outfile, indent=4, ensure_ascii=False)







