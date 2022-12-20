#!/usr/bin/env python3

#### REFERENCES

# https://github.com/gzhami/nlp_qa_project
# https://www.youtube.com/watch?v=ujsDOPfgnbk
# https://www.nltk.org/howto/wordnet.html
# https://www.analyticsvidhya.com/blog/2021/06/nlp-application-named-entity-recognition-ner-in-python-with-spacy/
# https://www.analyticsvidhya.com/blog/2019/02/stanfordnlp-nlp-library-python/


####

import sys, os
from bs4 import BeautifulSoup
import spacy
import nltk
import sentence_process
import question_file
import copy
import warnings
from nltk.tag.stanford import StanfordNERTagger
from nltk.parse.stanford import StanfordParser
from tags import *

os.environ['JAVAHOME'] = "/usr/bin/java"
# os.environ['STANFORD_MODELS'] = "/Users/kushagramahajan/Desktop/NLP/project_code/stanford-parser/jars"
# os.environ['STANFORD_PARSER'] = "/Users/kushagramahajan/Desktop/NLP/project_code/stanford-parser/jars"

os.environ['STANFORD_MODELS'] = "jars"
os.environ['STANFORD_PARSER'] = "jars"

warnings.filterwarnings("ignore")




ques_types_list = ['where', 'when', 'what', 'who', 'whom', 'whose', 'why', 'which', 'how many']

def get_questions(tree, NERtags):

    fin_ques_list = {}
    for q_type in ques_types_list:
        if(q_type == 'when'):
            fin_ques_list[q_type] = question_file.when(tree, NERtags)
        if(q_type == 'what'):
            fin_ques_list[q_type] = question_file.what(tree, NERtags)
        if(q_type == 'where'):
            fin_ques_list[q_type] = question_file.where(tree, NERtags)
        if(q_type == 'who'):
            fin_ques_list[q_type] = question_file.who(tree, NERtags)
        if(q_type == 'whom'):
            fin_ques_list[q_type] = question_file.whom(tree, NERtags)
        if(q_type == 'whose'):
            fin_ques_list[q_type] = question_file.whose(tree)
        if(q_type == 'why'):
            fin_ques_list[q_type] = question_file.why(tree)
        # if(q_type == 'which'):
        #     fin_ques_list[q_type] = question_file.which(tree)
        if(q_type == 'how many'):
            # print('HOW MANY...qtype call')
            fin_ques_list[q_type] = question_file.how_many(tree)

    return fin_ques_list


if __name__ == "__main__":
    input_file = sys.argv[1]
    N = int(sys.argv[2])



    ### Parsing html files

    # text = parse_docs('../Course-Project-Data/set1/a1.htm')
    # print(text)



    ### Using txt input

    with open(input_file) as f:
        text = f.read()
    # print(text)

    ### TESTING input sentences
    # text = 'Your bike is outside.'
    # text = 'The boy purchased 3 big, huge bananas.'




    bin_question_list = []
    best_wh_question_list = []

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = (tokenizer.tokenize(text))

    sentences = [si for si in sentences if "\n" not in si]


    ## selecting max 50 sentences

    # sentences = sentences[:10]
    # print(sentences)

    parser = StanfordParser(model_path = "jars/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
    # parser = StanfordParser(model_path = "/Users/kushagramahajan/Desktop/NLP/project_code/stanford-parser/jars/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

    parse_trees = parser.raw_parse_sents(sentences)


    nlp = spacy.load('en_core_web_md')


    filtered_sentences = sentence_process.filter_by_form(parse_trees)

    # print('filtered_sentences: ', filtered_sentences)

    ques_type_dict = {'when':[], 'where':[], 'what':[], 'why':[], 'whose':[], 'who':[], 'how many':[], 'whom':[]}

    fin_question_list = []

    for i in range(len(filtered_sentences)):
        try:
            sent_list = filtered_sentences[i].leaves()
            
            
            sent_tags = []
            sent_tags_temp = []
            sent_tags_words = []

            doc = nlp(' '.join(sent_list))
            # print('doc.ents: ', doc.ents)
            for e in doc.ents:
                # print('tag labels: ', e.text, e.label_)
                for val in e.text.split():
                    sent_tags_temp.append((val, e.label_))
                    sent_tags_words.append(val)


            for ind in range(len(sent_list)):
                flag = 0
                for ind2 in range(len(sent_tags_words)):
                    if(sent_list[ind] == sent_tags_words[ind2]):
                        sent_tags.append(sent_tags_temp[ind2])
                        flag = 1
                if(flag == 0):
                    sent_tags.append((sent_list[ind], 'O'))

            # print('sent_list: ', sent_list)
            # print('sent_tags: ', sent_tags)

            wh_questions = get_questions(filtered_sentences[i], sent_tags)
            # print('wh_questions: ', wh_questions)

            for ques_type, ques_vals in wh_questions.items():
                # print('ques_vals: ', ques_vals)
                for (tree, temp_for_ans) in ques_vals:
                    # print('tree: ', tree)
                    # print('wh_q_type: ', wh_q_type)
                    ques = ' '.join([ques_type, sentence_process.get_binary_ques(tree)])
                    
                    if(ques_type == 'whom'):
                        ques = ' '.join([temp_for_ans, ques_type, sentence_process.get_binary_ques(tree)])


                    if(ques_type == 'how many'):
                        subset_str = ""
                        flag = 0
                        for ind in range(len(temp_for_ans)):
                            if(ind == 0 or ind == (len(temp_for_ans) - 1)):
                                continue
                            # print('temp_for_ans[ind]: ', temp_for_ans[ind])
                            if((temp_for_ans[ind].label()[0] == 'J' and temp_for_ans[ind].label()[1] == 'J')):
                                flag = 1
                                subset_str = subset_str + temp_for_ans[ind][0] + ", "
                        
                        if(temp_for_ans[len(temp_for_ans)-1].label()[0] == 'N' and temp_for_ans[len(temp_for_ans)-1].label()[1] == 'N'):
                            if(flag == 1):
                                subset_str = subset_str.strip(', ') + " "
                            subset_str = subset_str + temp_for_ans[len(temp_for_ans)-1][0]
                        
                        ques = ' '.join(['how many', subset_str, sentence_process.get_binary_ques(tree)])

                    # print('temp_for_ans: ', temp_for_ans)

                    if(ques_type == 'whose' or ques_type == 'which'):
                        subset_str = ""
                        flag = 0
                        for ind in range(len(temp_for_ans)):
                            if(ind == 0 or ind == (len(temp_for_ans) - 1)):
                                continue
                            # print('temp_for_ans[ind]: ', temp_for_ans[ind])
                            if((temp_for_ans[ind].label()[0] == 'J' and temp_for_ans[ind].label()[1] == 'J')):
                                flag = 1
                                subset_str = subset_str + temp_for_ans[ind][0] + ", "
                        
                        if(temp_for_ans[len(temp_for_ans)-1].label()[0] == 'N' and temp_for_ans[len(temp_for_ans)-1].label()[1] == 'N'):
                            if(flag == 1):
                                subset_str = subset_str.strip(', ') + " "
                            subset_str = subset_str + temp_for_ans[len(temp_for_ans)-1][0]

                        ques = ' '.join([ques_type, subset_str, sentence_process.get_binary_ques(tree)])

                    ques = ques.strip(' .,') + '?'
                    ques = ques[0].capitalize() + ques[1:]
                    ques = ques.replace(" ,", ",")
                    ques = ques.replace(" '", "'")
                    # print('ques: ', ques)
                    ques_type_dict[ques_type].append(ques)


                    ### Temporaray addition for question selection
                    if(len(ques) > 0):
                        best_wh_question_list.append(ques)



            ques = sentence_process.get_binary_ques(filtered_sentences[i])
            ques = ques.strip(' .,') + '?'
            ques = ques[0].capitalize() + ques[1:]
            ques = ques.replace(" ,", ",")
            ques = ques.replace(" '", "'")
            fin_question_list.append(ques)
            bin_question_list.append(ques)

        except:
            # print('catch i: ', i)
            continue
            
    # print('ques_type_dict: ', ques_type_dict)
    # print('fin_question_list: ', fin_question_list)
    try:
        count = 0
        for i in range(N):
            count+=1
            print(best_wh_question_list[i])
        if(count<N):
            for i in range(N-count):
                print(bin_question_list[i])
    except:
        pass

