#!/usr/bin/env python3

#### REFERENCES

# https://www.rangakrish.com/index.php/2018/04/22/question-answering-using-dependency-trees/
# https://spacy.io/usage/linguistic-features#dependency-parse
# https://youtu.be/ohM7D21C_8Q

####

import sys
import spacy
import re
from nltk.tokenize import word_tokenize
import gensim
from gensim.models import KeyedVectors
import answerQuestions
from collections import Counter
import neuralcoref

import warnings

warnings.filterwarnings("ignore")

def final_answer(q, a_s):

    # Get the type of the question and call the corresponding function
    doc_q = nlp(q)
    doc_a = nlp(a_s)
    q_type, q_pos = answerQuestions.get_question_type(doc_q, nlp)
    function = getattr(answerQuestions, q_type)
    ner_text = []
    ner_label = []
    for i in doc_a.ents:
        ner_text.append(i.text)
        ner_label.append(i.label_)
    answer = function(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp)
    answer = prettify(answer)
    return answer

def prettify(sentence):

    # Final printing of the answer
    if sentence[-1] != ".":
        sentence = sentence + "."
    doc = nlp(sentence)
    factored_sent = [(w.text, w.pos_) for w in doc]
    normalized_sent = [w.capitalize() if t in ["PROPN"] else w for (w,t) in factored_sent]
    normalized_sent[0] = normalized_sent[0].capitalize()
    for index in range(len(normalized_sent) - 1):
        if normalized_sent[index + 1] not in [",", ".", "!"]:
          normalized_sent[index] = normalized_sent[index] + " "
    final_sentence = "".join(normalized_sent)
    return final_sentence

def read_t_file(file):
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()
    cleaned_text = clean_text(text)
    return cleaned_text

def clean_text(text):
    # Get each sentence and also do correference resolution
    text = text.split("\n")
    text = [i for i in text if len(i.split()) >= 10]
    doc = nlp('\n'.join(text))
    text = doc._.coref_resolved
    return text.split('\n')

def read_q_file(file):
    with open(file, "r", encoding="utf-8") as f:
        questions = f.readlines()
    cleaned_questions = []
    for question in questions:
        cleaned_questions.append(clean_question(question))
    return cleaned_questions

def clean_question(question):
    question = question.lower()
    question = re.sub('[?:]', '', question)
    return question


def get_answers(text, questions, w2vec):
    answers = []
    tokenized_text, sentences = get_tokenized_sentences(text)
    # For each question, get its answer and append to list of answers
    for question in questions:
        try:
            res = get_answer_for_q(tokenized_text, sentences, question, w2vec)
            answers.append(res)
        except Exception as e:
            answers.append("Yes.")
    return answers

def get_tokenized_sentences(text):
    all_text = ' '.join(text)
    doc = nlp(all_text)
    # Consider only sentences more than 5 words long and tokenize the text
    sentences = [str(sentence) for sentence in list(doc.sents) if len(str(sentence).split()) >= 5]
    tokenized_text = [list(filter(lambda x: x in w2vec.index_to_key, word_tokenize(sentence.lower()))) for sentence in
                      sentences]
    return tokenized_text, sentences

def get_answer_for_q(tokenized_text, sentences, question, w2vec):
    # Get the top 3 relevant sentences from w2vec and word overlap similarity
    relevant_sentences = get_relevant_sentences(tokenized_text, sentences, question, w2vec)
    # Get top sentence from spacy similarity
    relevant_sentence = get_relevant_sentence_spcy(sentences, question)

    # Combine both / select one
    cand_passage = get_final_sentence(relevant_sentences, relevant_sentence)
    # Apply rules to extract answer
    final_answer = get_final_answer(question, cand_passage)
    return final_answer

def get_final_sentence(relevant_sentences, relevant_sentence):
    # If spacy selected sentence is in w2vec sentences, return that
    # Else return 1st sentence of w2vec and spacy sentence
    if (relevant_sentence in set(relevant_sentences)):
        return [relevant_sentence]
    return [relevant_sentences[0], relevant_sentence]


def get_relevant_sentence_spcy(sentences, question):
    # Get the most similar sentence based on spacy similarity
    q_nlp = nlp(question)
    max_sim = 0
    max_sim_sentence = sentences[0]
    for i in sentences:
        sent_nlp = nlp(i)
        sim = q_nlp.similarity(sent_nlp)
        if(sim > max_sim):
            max_sim = sim
            max_sim_sentence = i
    return max_sim_sentence

def get_relevant_sentences(tokenized_text, sentences, question, w2vec):
    # Get top 3 candidate sentences based on w3vec similarity and word overlap
    sentence_f = [0, 0, 0]
    max_sim = [0, 0, 0]
    split_question = list(filter(lambda x: x in w2vec.index_to_key, word_tokenize(question)))
    ind = 0

    for split_sentence in tokenized_text:
        sim_w2vec = w2vec.n_similarity(split_sentence, split_question)
        sim_w_overlap = len(set([i for i in sentences[ind].split() if i not in nlp.Defaults.stop_words]).intersection(set([i for i in question.split() if i not in nlp.Defaults.stop_words])))/len(set([i for i in sentences[ind].split() if i not in nlp.Defaults.stop_words]).union(set([i for i in question.split() if i not in nlp.Defaults.stop_words])))
        sim = sim_w2vec + sim_w_overlap
        # Can use nsim here also
        if sim > max_sim[0]:
            max_sim[1:3] = max_sim[0:2]
            sentence_f[1:3] = sentence_f[0:2]
            max_sim[0] = sim
            sentence_f[0] = ind
        elif sim > max_sim[1]:
            max_sim[2] = max_sim[1]
            sentence_f[2] = sentence_f[1]
            max_sim[1] = sim
            sentence_f[1] = ind
        elif sim > max_sim[2]:
            max_sim[2] = sim
            sentence_f[2] = ind
        ind += 1
    return [sentences[sentence_f[0]], sentences[sentence_f[1]], sentences[sentence_f[2]]]


def get_final_answer(question, cand_passage):
    res = ''
    # If there was only 1, pass it and return the answer
    if len(cand_passage) == 1:
        res = final_answer(question, cand_passage[0].lower())
    # Else, for each candidate pass and take majority vote
    else:
        l = []
        for i in cand_passage:
            l.append(final_answer(question, i.lower()))
        if len(l[0]) >= 5:
            res = l[0]
        else:
            if l[0] == "Yes." or l[1] == "Yes.":
                return "Yes."
            c = Counter(l)
            value, count = c.most_common()[0]
            res = value
    return res



if __name__ == "__main__":
    t_file = sys.argv[1]
    q_file = sys.argv[2]
    w2vec = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
    nlp = spacy.load('en_core_web_md')
    neuralcoref.add_to_pipe(nlp)
    text = read_t_file(t_file)
    questions = read_q_file(q_file)
    answers = get_answers(text, questions, w2vec)
    
    for i in answers:
        print(i)

