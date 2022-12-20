
from tags import *  

from nltk.tree import Tree
import mlconjug3

from nltk.stem import   WordNetLemmatizer
import copy

wordnet_lemmatizer = WordNetLemmatizer()


def get_accept_sent_forms():
    acc_forms = [(ROOT, ((SENT, (NP, VP, DOT_PERIOD)),))]
    return acc_forms


def filter_util(parse_tree, form):
    # print('form: ', form)
    if(parse_tree.label() == ROOT):
        if(len(parse_tree) > 0 and parse_tree[0].label() == SENT):
            if(len(parse_tree[0]) >= 2 and parse_tree[0][0].label() == NP and parse_tree[0][1].label() == VP):
                return True

    return False


# def filter_util(parse_tree, form):
#     if(not (type(form) == tuple)):
#         if(parse_tree.label() == form):
#             return True
#         else:
#             return False

#     node = form[0]
#     children = form[1]
#     if(parse_tree.label() == node and len(parse_tree) == len(children)):
#         for ind in range(len(parse_tree)):
#             child = parse_tree[ind]
#             if(filter_util(child, children[ind]) == False):
#                 return False
#         return True



def filter_by_form(parse_trees):

    sent_forms = get_accept_sent_forms()

    # print('parse_trees: ', parse_trees)

    filt_sents = []
    for tree in parse_trees:
        for ind_tree in tree:
            for ind_sent_form in sent_forms:
                # print('ind_tree: ', ind_tree)
                # print('filter_util(ind_tree, ind_sent_form): ', filter_util(ind_tree, ind_sent_form))
                if(filter_util(ind_tree, ind_sent_form) == True):
                    filt_sents.append(ind_tree[0])
    
    return filt_sents



def get_binary_ques(tree):
  
    subj = tree[0]

    word_first = copy.deepcopy(tree)
    while isinstance(word_first[0], Tree):
        word_first = word_first[0]
    
    if(word_first.label() != NNP):
        subj[0] = word_first[0].lower()
    else:
        subj[0] = word_first[0]


    if(subj.label() != NP):
        # print('join(tree.leaves()): ', ' '.join(tree.leaves()))
        return ' '.join(tree.leaves())

    
    verb_phrase = tree[1]
    main_verb = verb_phrase[0]
    verb = main_verb[0]
    
    w = wordnet_lemmatizer.lemmatize(verb, 'v')

    default_conjugator = mlconjug3.Conjugator(language='en')
    
    
    # print('main_verb: ', main_verb)
    # print('w: ', w)
    
    if(w == 'be' or main_verb.label() == 'MD' or (len(verb_phrase) >= 2 and w in ['have', 'do'] and verb_phrase[1].label() == VP)):
        # print('inside the modal checking if')
        
        str_subject = ' '.join(subj.leaves())
        bin_ques = verb + " " + str_subject + " "

        for i in range(len(verb_phrase)):
            if(i == 0):
                continue
            node = verb_phrase[i]
            str_verb_phrase = ' '.join(node.leaves())
            bin_ques = bin_ques + str_verb_phrase + " "
        # print('bin_ques1: ', bin_ques)
        return bin_ques

    else:
        main_verb[0] = w
        # print('main_verb: ', main_verb)
        
        if(main_verb.label() == VBD):
            inf_var = 'vb_past'
        elif(main_verb.label() == VBP):
            inf_var = 'vb_infinitive'
        elif(main_verb.label() == VBZ):
            inf_var = 'vb_3singular'
        
        # print('inflected output: ', inf_var)
        
        if(inf_var == 'vb_infinitive'):
            inf_fin = default_conjugator.conjugate("do").conjug_info['infinitive']['infinitive present']
        elif(inf_var == 'vb_past'):
            inf_fin = default_conjugator.conjugate("do").conjug_info['indicative']['indicative past tense']['3p']
        elif(inf_var == 'vb_3singular'):
            inf_fin = default_conjugator.conjugate("do").conjug_info['indicative']['indicative present']['3s']
        
        str_subject = ' '.join(subj.leaves())
        str_verb_phrase = ' '.join(verb_phrase.leaves())
        bin_ques1 = ' '.join([inf_fin, str_subject])
        bin_ques_fin = ' '.join([bin_ques1, str_verb_phrase])

        # print('bin_ques2: ', bin_ques_fin)
        
        return bin_ques_fin

