import pyinflect
import spacy
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
lemmatizer = WordNetLemmatizer()
ps = PorterStemmer()


# Function to check question type
def get_question_type(doc_q, nlp):
    type = "binary"
    q_pos = 0
    pos = 0
    for i in doc_q:
        #When
        if(i.tag_ == "WRB" and i.text.lower()== "when"):
          type = "when"
          q_pos = pos
          break
        # where
        if(i.tag_ == "WRB" and i.text.lower()== "where"):
            type = "where"
            q_pos = pos
            break
        # how/ how-many
        if(i.tag_ == "WRB" and i.text.lower()== "how"):
            if(i.head.text == "many"):
                type = "how_many"
            else:
                type = "how"
            q_pos = pos
            break
        # why
        if(i.tag_ == "WRB" and i.text.lower()== "why"):
            type = "why"
            q_pos = pos
            break
        # what
        if(i.tag_ in ["WP", "WDT"] and i.text.lower()== "what"):
            type = "what"
            q_pos = pos
            break
        # who
        if(i.tag_ == "WP" and i.text.lower()== "who"):
            type = "who"
            q_pos = pos
            break
        # which
        if(i.tag_ == "WDT" and i.text.lower()== "which"):
            type = "which"
            q_pos = pos
            break
        if (i.tag_ == "WP$" and i.text.lower() == "whose"):
            type = "who"
            q_pos = pos
            break
        if (i.tag_ == "WP" and i.text.lower() == "whom"):
            type = "who"
            q_pos = pos
            break
        pos += 1

    return type, q_pos

# Function to get all hyponyms
def hyponyms(word):
    all_hyponyms = set()
    for synset in wordnet.synsets(word):
        for hyponym in synset.hyponyms():
          for lemma in hyponym.lemmas():
              all_hyponyms.add(lemma.name().replace('_', ' '))
    return all_hyponyms

# Function to get all synonyms
def synonyms(word):
    all_synonyms = set()
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            all_synonyms.add(lemma.name().replace('_', ' '))
    return all_synonyms

# Function to get all antonyms
def antonyms(word):
    all_antonyms = set()
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            if lemma.antonyms():
                all_antonyms.add(lemma.antonyms()[0].name())
    return all_antonyms

# Function to return all children of node
def get_children(token):
    child = []
    for i in token.children:
        child += get_children(i)
    child += [token]
    return child

# Function that returns the past tense
def get_past_tense(token):
    if token.tag_ in ['VBP', 'VBZ', 'VB']:
        return token._.inflect("VBD")
    return token.text

# Answer to when question
def when(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp):
    # Get root word
    root_w = -1
    root_w_text = ""
    for i in doc_q:
        if i.dep_ == "ROOT":
            root_w = i
            root_w_text = i.text

    # Remove that word
    q = ' '.join([i.text for i in doc_q])
    q = q.split()
    q = q[:q_pos] + q[q_pos + 1:]
    q = ' '.join(q)
    doc_q = nlp(q)

    # check if root is AUX
    n_root_aux = False
    for token in doc_q:
        if token.dep_ == "ROOT" and token.pos_ == "AUX":
            n_root_aux = True
        break

    swap_l = q_pos
    swap_r = -1
    nns = ["NN", "NNP", "NNS", "CD"]
    # Now we want to form a part of the answer (starting) from the question
    # If root is aux do based on position
    if n_root_aux:
        swap_l = 0
        l_tok = [i for i in doc_q]
        for token in range(len(l_tok)):
            if l_tok[token].dep_ == "ROOT" and token != len(l_tok) - 1:
                if (l_tok[token + 1].tag_ in nns):
                    swap_r = token
                    j = token + 2
                    while j < len(l_tok):
                        if (l_tok[j].tag_ not in nns):
                            swap_r = j
                            break
                        j += 1
                    if j == len(l_tok):
                        swap_r = j
                elif (l_tok[token + 1].tag_ == "DT"):
                    swap_r = token
                    j = token + 2
                    while j < len(l_tok):
                        if (l_tok[j].tag_ not in nns):
                            swap_r = j
                            break
                        j += 1
                    if j == len(l_tok):
                        swap_r = j
    else:
        # Do based on dependency parsing, get the start and end indexes of the question
        l_tok = [i for i in doc_q]
        acceptable_start_states = set(["NNP", "NN", "DT", "PRP", "NNS", "CD"])
        for token in range(len(l_tok)):
            if l_tok[token].text == root_w_text:
                token_children = list(l_tok[token].children)
                for token_child_idx in range(1, len(token_children)):
                    if (token_children[token_child_idx - 1].pos_ == "AUX" or token_children[
                        token_child_idx - 1].tag_ == "WRB") and token_children[
                        token_child_idx].tag_ in acceptable_start_states:
                        childs = get_children(token_children[token_child_idx])
                        sorted_childs = sorted(childs, key=lambda x: x.i)
                        swap_r = sorted_childs[-1].i + 1
                        swap_l = sorted_childs[0].i - 1
                        break

    # Based on the indexes, swap it to form the starting of the answer
    q = q.split()
    if swap_r != -1 and q[swap_l].lower() == "did":
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + q[swap_r:]
        sente_l[swap_r - 1] = get_past_tense(l_tok[swap_r])
        sente_l = ' '.join(sente_l)
    elif swap_r != -1 and q[swap_l].lower() == "do":
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + q[swap_r:]
        sente_l = ' '.join(sente_l)
    elif swap_r != -1:
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + [q[swap_l]] + q[swap_r:]
        sente_l = ' '.join(sente_l)
    else:
        sente_l = ' '.join(q)

    # Now find the position of the root word in the answer
    pos_l = -1;
    pos_r = -1;
    a_tok = [i for i in doc_a]

    sente_r = ""

    # Try to find the root token of the question in the answer
    root_token_in_question = -1
    root_token_in_answer = -1
    found_question_root = 0
    for word in doc_a:
        # Case 1 if it is the same as the question
        if root_w.pos_ != "AUX" and (
                word.lemma_ == root_w.lemma_ or word.text == root_w_text):  # or word.lemma_ in root_hyponyms:
            root_token_in_question = word
            found_question_root = 1
            break
        # Case 2 if it is the independent root of answer
        if word.dep_ == "ROOT":
            root_token_in_answer = word

    root_token = -1
    # Preference for Case 1
    if found_question_root == 1:
        root_token = root_token_in_question
    else:
        root_token = root_token_in_answer


    # Now, go through all children of root independently and check for ADP tags
    # Then with NER tag, search for TIME/DATE and return that part of the dependency tree
    root_token_children = list(root_token.children)
    first_adp_child = -1
    for child in root_token_children:
        # Can consider inside ones  also
        if child.pos_ == "ADP":
            first_adp_child = child
            children_of_adp = get_children(first_adp_child)
            children_of_adp = children_of_adp[:-1]
            sorted_children_of_adp = sorted(children_of_adp, key=lambda x: x.i)
            text_sorted_children_of_adp = [token.text for token in sorted_children_of_adp]
            stringified_candidate_token = " ".join(text_sorted_children_of_adp)
            if stringified_candidate_token in ner_text:
                index = ner_text.index(stringified_candidate_token)
                if ner_label[index] in ["DATE", "TIME"]:
                    sente_r = first_adp_child.text + " " + stringified_candidate_token
                    break
        else:
            grand_children = get_children(child)
            flag = 0
            for grand_child in grand_children:
                if grand_child.pos_ == "ADP":
                    first_adp_child = grand_child
                    children_of_adp = get_children(first_adp_child)
                    children_of_adp = children_of_adp[:-1]
                    sorted_children_of_adp = sorted(children_of_adp, key=lambda x: x.i)
                    text_sorted_children_of_adp = [token.text for token in sorted_children_of_adp]
                    stringified_candidate_token = " ".join(text_sorted_children_of_adp)
                    if stringified_candidate_token in ner_text:
                        index = ner_text.index(stringified_candidate_token)
                        if ner_label[index] in ["DATE", "TIME"]:
                            sente_r = first_adp_child.text + " " + stringified_candidate_token
                            flag = 1
                            break
            if flag == 1:
                break

    res = ""
    if sente_r == "":
        res = a_s
    else:
        res = sente_l + " " + sente_r
    return res

# Function to answer when question
def where(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp):
    # SAME as when but with different NER tags
    root_w = -1
    root_w_text = ""
    for i in doc_q:
        if i.dep_ == "ROOT":
            root_w = i
            root_w_text = i.text

    new_ner_text = []
    new_ner_label = []
    for i in range(len(ner_text)):
        t = ner_text[i].split()
        for j in t:
            new_ner_text.append(j)
            new_ner_label.append(ner_label[i])

    ner_text = new_ner_text
    ner_label = new_ner_label
    # Remove that word
    q = ' '.join([i.text for i in doc_q])
    q = q.split()
    q = q[:q_pos] + q[q_pos + 1:]
    q = ' '.join(q)
    doc_q = nlp(q)
    n_root_aux = False
    for token in doc_q:
        if token.dep_ == "ROOT" and token.pos_ == "AUX":
            n_root_aux = True
        break

    swap_l = q_pos
    swap_r = -1
    nns = ["NN", "NNP", "NNS", "CD"]
    if n_root_aux:
        swap_l = 0
        l_tok = [i for i in doc_q]
        for token in range(len(l_tok)):
            if l_tok[token].dep_ == "ROOT" and token != len(l_tok) - 1:
                if (l_tok[token + 1].tag_ in nns):
                    swap_r = token
                    j = token + 2
                    while j < len(l_tok):
                        if (l_tok[j].tag_ not in nns):
                            swap_r = j
                            break
                        j += 1
                    if j == len(l_tok):
                        swap_r = j
                elif (l_tok[token + 1].tag_ == "DT"):
                    swap_r = token
                    j = token + 2
                    while j < len(l_tok):
                        if (l_tok[j].tag_ not in nns):
                            swap_r = j
                            break
                        j += 1
                    if j == len(l_tok):
                        swap_r = j
    else:
        # Get the sentence form of question
        swap_l = q_pos
        swap_r = -1
        l_tok = [i for i in doc_q]
        acceptable_start_states = set(["NNP", "NN", "DT", "PRP", "NNS", "CD"])
        for token in range(len(l_tok)):
            if l_tok[token].text == root_w_text:
                token_children = list(l_tok[token].children)
                for token_child_idx in range(1, len(token_children)):
                    if (token_children[token_child_idx - 1].pos_ == "AUX" or token_children[
                        token_child_idx - 1].tag_ == "WRB") and token_children[
                        token_child_idx].tag_ in acceptable_start_states:
                        childs = get_children(token_children[token_child_idx])
                        sorted_childs = sorted(childs, key=lambda x: x.i)

                        swap_r = sorted_childs[-1].i + 1
                        swap_l = sorted_childs[0].i - 1
                        break

    q = q.split()
    if q[swap_l].lower() == "did":
        if swap_r != -1:
            sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + q[swap_r:]
            sente_l[swap_r - 1] = get_past_tense(l_tok[swap_r])
            sente_l = ' '.join(sente_l)
        else:
            sente_l = q[:swap_l] + q[swap_l + 1:]
            sente_l = ' '.join(sente_l)
    elif swap_r != -1 and q[swap_l].lower() == "do":
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + q[swap_r:]
        sente_l = ' '.join(sente_l)
    elif swap_r != -1:
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + [q[swap_l]] + q[swap_r:]
        sente_l = ' '.join(sente_l)
    else:
        sente_l = ' '.join(q)

    # Now find the position of the root word in the answer
    pos_l = -1;
    pos_r = -1;
    a_tok = [i for i in doc_a]

    sente_r = ""

    # Try to find the root token
    root_token_in_question = -1
    root_token_in_answer = -1
    found_question_root = 0
    for word in doc_a:
        # Case 1 if it is the same as the question
        if root_w.pos_ != "AUX" and (
                word.lemma_ == root_w.lemma_ or word.text == root_w_text):  # or word.lemma_ in root_hyponyms:
            root_token_in_question = word
            found_question_root = 1
            break
        # Case 2 if it is the independent root of answer
        if word.dep_ == "ROOT":
            root_token_in_answer = word

    root_token = -1
    # Preference for Case 1
    if found_question_root == 1:
        root_token = root_token_in_question
    else:
        root_token = root_token_in_answer

    # Lemmatize and also check
    # Identify the root, check its children (ADP), break off at first match if its
    # NER tag is date or time

    root_token_children = list(root_token.children)
    first_adp_child = -1
    for child in root_token_children:
        # Can consider inside ones  also
        if child.pos_ == "ADP":
            first_adp_child = child
            children_of_adp = get_children(first_adp_child)
            children_of_adp = children_of_adp[:-1]
            sorted_children_of_adp = sorted(children_of_adp, key=lambda x: x.i)
            text_sorted_children_of_adp = [token.text for token in sorted_children_of_adp]
            stringified_candidate_token = " ".join(text_sorted_children_of_adp)

            prev_loc = 0
            for possible_ner in text_sorted_children_of_adp:
                flag_loc = 0
                if possible_ner == "," and (prev_loc == 1):
                    sente_r = sente_r.rstrip() + possible_ner + " "
                    flag_loc = 1
                if possible_ner in ner_text and (prev_loc == 1 or (prev_loc == 0 and flag_loc == 0)):
                    index = ner_text.index(possible_ner)
                    if ner_label[index] in ["GPE", "LOC"]:
                        sente_r = sente_r + possible_ner + " "
                        prev_loc = 1
                        flag_loc = 1
                if flag_loc == 0:
                    prev_loc = 0
            if sente_r != "":
                sente_r = first_adp_child.text + " " + sente_r
                break
        else:
            grand_children = get_children(child)
            flag = 0
            for grand_child in grand_children:
                if grand_child.pos_ == "ADP":
                    first_adp_child = grand_child
                    children_of_adp = get_children(first_adp_child)
                    children_of_adp = children_of_adp[:-1]
                    sorted_children_of_adp = sorted(children_of_adp, key=lambda x: x.i)
                    text_sorted_children_of_adp = [token.text for token in sorted_children_of_adp]
                    stringified_candidate_token = " ".join(text_sorted_children_of_adp)
                    prev_loc = 0
                    for possible_ner in text_sorted_children_of_adp:
                        flag_loc = 0
                        if possible_ner == "," and (prev_loc == 1):
                            sente_r = sente_r.rstrip() + possible_ner + " "
                            flag_loc = 1
                        if possible_ner in ner_text and (prev_loc == 1 or (prev_loc == 0 and flag_loc == 0)):
                            index = ner_text.index(possible_ner)
                            if ner_label[index] in ["GPE", "LOC"]:
                                sente_r = sente_r + possible_ner + " "
                                prev_loc = 1
                                flag_loc = 1
                        if flag_loc == 0:
                            prev_loc = 0
                    if sente_r != "":
                        flag = 1
                        sente_r = first_adp_child.text + " " + sente_r
                        break
            if flag == 1:
                break

    res = ""
    if sente_r == "":
        res = a_s
    else:
        res = sente_l + " " + sente_r
    res = res.strip()
    if res[-1] == ",":
        res = res[:-1]
    return res

# Answer why questions
def why(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp):
    # Get root word
    root_w = -1
    root_w_text = ""
    for i in doc_q:
        if i.dep_ == "ROOT":
            root_w = i
            root_w_text = i.text

    # Remove that word
    q = ' '.join([i.text for i in doc_q])
    q = q.split()
    q = q[:q_pos] + q[q_pos + 1:]
    q = ' '.join(q)
    doc_q = nlp(q)
    n_root_aux = False
    for token in doc_q:
        if token.dep_ == "ROOT" and token.pos_ == "AUX":
            n_root_aux = True
        break

    swap_l = q_pos
    swap_r = -1
    nns = ["NN", "NNP", "NNS", "CD"]
    if n_root_aux:
        swap_l = 0
        l_tok = [i for i in doc_q]
        for token in range(len(l_tok)):
            if l_tok[token].dep_ == "ROOT" and token != len(l_tok) - 1:
                if (l_tok[token + 1].tag_ in nns):
                    swap_r = token
                    j = token + 2
                    while j < len(l_tok):
                        if (l_tok[j].tag_ not in nns):
                            swap_r = j
                            break
                        j += 1
                    if j == len(l_tok):
                        swap_r = j
                elif (l_tok[token + 1].tag_ == "DT"):
                    swap_r = token
                    j = token + 2
                    while j < len(l_tok):
                        if (l_tok[j].tag_ not in nns):
                            swap_r = j
                            break
                        j += 1
                    if j == len(l_tok):
                        swap_r = j
    else:
        # Get the sentence form of question
        swap_l = q_pos
        swap_r = -1
        l_tok = [i for i in doc_q]
        acceptable_start_states = set(["NNP", "NN", "DT", "PRP", "NNS", "CD"])
        for token in range(len(l_tok)):
            if l_tok[token].text == root_w_text:
                token_children = list(l_tok[token].children)
                for token_child_idx in range(1, len(token_children)):
                    if (token_children[token_child_idx - 1].pos_ == "AUX" or token_children[
                        token_child_idx - 1].tag_ == "WRB") and token_children[
                        token_child_idx].tag_ in acceptable_start_states:
                        childs = get_children(token_children[token_child_idx])
                        sorted_childs = sorted(childs, key=lambda x: x.i)
                        swap_r = sorted_childs[-1].i + 1
                        swap_l = sorted_childs[0].i - 1
                        break

    q = q.split()
    if swap_r != -1 and q[swap_l].lower() == "did":
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + q[swap_r:]
        sente_l[swap_r - 1] = get_past_tense(l_tok[swap_r])
        sente_l = ' '.join(sente_l)
    elif swap_r != -1 and q[swap_l].lower() == "do":
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + q[swap_r:]
        sente_l = ' '.join(sente_l)
    elif swap_r != -1:
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + [q[swap_l]] + q[swap_r:]
        sente_l = ' '.join(sente_l)
    else:
        sente_l = ' '.join(q)

    # Now find the position of the root word in the answer
    pos_l = -1;
    pos_r = -1;
    a_tok = [i for i in doc_a]

    sente_r = ""

    # Try to find the root token
    root_token_in_question = -1
    root_token_in_answer = -1
    found_question_root = 0
    for word in doc_a:
        # Case 1 if it is the same as the question
        if root_w.pos_ != "AUX" and (
                word.lemma_ == root_w.lemma_ or word.text == root_w_text):  # or word.lemma_ in root_hyponyms:
            root_token_in_question = word
            found_question_root = 1
            break
        # Case 2 if it is the independent root of answer
        if word.dep_ == "ROOT":
            root_token_in_answer = word

    root_token = -1
    # Preference for Case 1
    if found_question_root == 1:
        root_token = root_token_in_question
    else:
        root_token = root_token_in_answer

    # Now in the tree, check for the words because, due etc and get the corresponding part of the tree as the answer
    root_token_children = list(root_token.children)
    first_adp_child = -1
    for child in root_token_children:
        # Can consider inside ones  also
        if child.pos_ in ["ADP", "SCONJ"] and child.text.lower() in ["because", "due", "since", "as"]:
            first_adp_child = child
            children_of_adp = get_children(first_adp_child)
            children_of_adp = children_of_adp[:-1]
            sorted_children_of_adp = sorted(children_of_adp, key=lambda x: x.i)
            text_sorted_children_of_adp = [token.text for token in sorted_children_of_adp]
            stringified_candidate_token = " ".join(text_sorted_children_of_adp)
            sente_r = first_adp_child.text + " " + stringified_candidate_token
            break
        else:
            grand_children = get_children(child)
            flag = 0
            for grand_child in grand_children:
                if grand_child.pos_ in ["ADP", "SCONJ"] and grand_child.text.lower() in ["because", "due", "since",
                                                                                         "as"]:
                    first_adp_child = grand_child
                    children_of_adp = get_children(first_adp_child)
                    if len(children_of_adp) == 1:
                        t_ancestors = first_adp_child.ancestors
                        for t in t_ancestors:
                            children_of_adp = get_children(t)
                            break

                    sorted_children_of_adp = sorted(children_of_adp, key=lambda x: x.i)
                    sorted_children_of_adp = sorted_children_of_adp[1:]
                    text_sorted_children_of_adp = [token.text for token in sorted_children_of_adp]
                    stringified_candidate_token = " ".join(text_sorted_children_of_adp)
                    sente_r = first_adp_child.text + " " + stringified_candidate_token
                    flag = 1
                    break
            if flag == 1:
                break

    res = ""
    if sente_r == "":
        res = a_s
    else:
        res = sente_l + " " + sente_r
    return res

# Answer how question
def how(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp):
    # Get root word as above
    root_w = -1
    root_w_text = ""
    for i in doc_q:
        if i.dep_ == "ROOT":
            root_w = i
            root_w_text = i.text

    # Remove that word

    q = ' '.join([i.text for i in doc_q])
    q = q.split()
    q = q[:q_pos] + q[q_pos + 1:]
    q = ' '.join(q)
    doc_q = nlp(q)
    l_tok = [i for i in doc_q]
    # If its is not AUX, eg how far, how long etc, return the whole sentence
    if l_tok[q_pos].pos_ != "AUX":
        q = q[:q_pos] + q[q_pos + 1:]
        doc_q = nlp(q)
        return a_s
    n_root_aux = False
    for token in doc_q:
        if token.dep_ == "ROOT" and token.pos_ == "AUX":
            n_root_aux = True
        break

    swap_l = q_pos
    swap_r = -1
    nns = ["NN", "NNP", "NNS", "CD"]
    if n_root_aux:
        swap_l = 0
        l_tok = [i for i in doc_q]
        for token in range(len(l_tok)):
            if l_tok[token].dep_ == "ROOT" and token != len(l_tok) - 1:
                if (l_tok[token + 1].tag_ in nns):
                    swap_r = token
                    j = token + 2
                    while j < len(l_tok):
                        if (l_tok[j].tag_ not in nns):
                            swap_r = j
                            break
                        j += 1
                    if j == len(l_tok):
                        swap_r = j
                elif (l_tok[token + 1].tag_ == "DT"):
                    swap_r = token
                    j = token + 2
                    while j < len(l_tok):
                        if (l_tok[j].tag_ not in nns):
                            swap_r = j
                            break
                        j += 1
                    if j == len(l_tok):
                        swap_r = j
    else:
        # Get the sentence form of question
        swap_l = q_pos
        swap_r = -1
        l_tok = [i for i in doc_q]
        acceptable_start_states = set(["NNP", "NN", "DT", "PRP", "NNS", "CD"])
        for token in range(len(l_tok)):
            if l_tok[token].text == root_w_text:
                token_children = list(l_tok[token].children)
                for token_child_idx in range(1, len(token_children)):
                    if (token_children[token_child_idx - 1].pos_ in ["AUX", "NN"] or token_children[
                        token_child_idx - 1].tag_ == "WRB") and token_children[
                        token_child_idx].tag_ in acceptable_start_states:
                        childs = get_children(token_children[token_child_idx])
                        sorted_childs = sorted(childs, key=lambda x: x.i)
                        swap_r = sorted_childs[-1].i + 1
                        swap_l = sorted_childs[0].i - 1
                        break

    q = q.split()
    if swap_r != -1 and q[swap_l].lower() == "did":
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + q[swap_r:]
        sente_l[swap_r - 1] = get_past_tense(l_tok[swap_r])
        sente_l = ' '.join(sente_l)
    elif swap_r != -1 and q[swap_l].lower() == "do":
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + q[swap_r:]
        sente_l = ' '.join(sente_l)
    elif swap_r != -1:
        sente_l = q[:swap_l] + q[swap_l + 1: swap_r] + [q[swap_l]] + q[swap_r:]
        sente_l = ' '.join(sente_l)
    else:
        sente_l = ' '.join(q)

    # Now find the position of the root word in the answer
    pos_l = -1;
    pos_r = -1;
    a_tok = [i for i in doc_a]

    sente_r = ""

    # Try to find the root token
    root_token_in_question = -1
    root_token_in_answer = -1
    found_question_root = 0
    for word in doc_a:
        # Case 1 if it is the same as the question
        if root_w.pos_ != "AUX" and (
                word.lemma_ == root_w.lemma_ or word.text == root_w_text):  # or word.lemma_ in root_hyponyms:
            root_token_in_question = word
            found_question_root = 1
            break
        # Case 2 if it is the independent root of answer
        if word.dep_ == "ROOT":
            root_token_in_answer = word

    root_token = -1
    # Preference for Case 1
    if found_question_root == 1:
        root_token = root_token_in_question
    else:
        root_token = root_token_in_answer

    # Check for the words of with, by and is
    root_token_children = list(root_token.children)
    first_adp_child = -1
    for child in root_token_children:
        # Can consider inside ones  also
        if (child.pos_ == "ADP" and child.text.lower() in ["with", "by", "is"]) or (
                child.pos_ == "VERB" and child.text.lower() in ["using"]):
            first_adp_child = child
            children_of_adp = get_children(first_adp_child)
            children_of_adp = children_of_adp[:-1]
            sorted_children_of_adp = sorted(children_of_adp, key=lambda x: x.i)
            text_sorted_children_of_adp = [token.text for token in sorted_children_of_adp]
            stringified_candidate_token = " ".join(text_sorted_children_of_adp)
            sente_r = first_adp_child.text + " " + stringified_candidate_token
            break
        else:
            grand_children = get_children(child)
            flag = 0
            for grand_child in grand_children:
                if grand_child.pos_ == "ADP":
                    first_adp_child = child
                    children_of_adp = get_children(first_adp_child)
                    children_of_adp = children_of_adp[:-1]
                    sorted_children_of_adp = sorted(children_of_adp, key=lambda x: x.i)
                    text_sorted_children_of_adp = [token.text for token in sorted_children_of_adp]
                    stringified_candidate_token = " ".join(text_sorted_children_of_adp)
                    sente_r = first_adp_child.text + " " + stringified_candidate_token
                    break
            if flag == 1:
                break

    res = ""
    if sente_r == "":
        res = a_s
    else:
        res = sente_l + " " + sente_r
    return res

# Answer how many question type
def how_many(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp):
    # Iterate through cardinals, for each cardinal get the number i.e the last one after you split the text. Then find the token corresponding
    # to that number and get its immediate ancestor. If it is equal to word_after_many, return the cardinal
    # Get root word
    root_w = -1
    root_w_text = ""
    for i in doc_q:
        if i.dep_ == "ROOT":
            root_w = i
            root_w_text = i.text

    word_after_many = "";
    tok = [i for i in doc_q]
    for i in range(len(tok)):
        if tok[i].text.lower() == "many":
            word_after_many = tok[i + 1].text

    sente_r = ""
    flag = 0
    for i in ner_text:
        numb = '';
        for j in i.split():
            d = nlp(j)
            for k in d.ents:
                if k.label_ in ["CARDINAL", "QUANTITY"]:
                    numb = k.text
                break
        for token in doc_a:
            if token.text == numb:
                ancestor = list(token.ancestors)[0]
                if ancestor.text.lower() == word_after_many.lower():
                    sente_r = i
                    flag = 1
                    break
            if flag:
                break

    res = ""
    if sente_r == "":
        res = a_s
    else:
        res = sente_r
    return res

# Answer who question type
def who(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp):

    # Find the NER tags of PERSON/ORG
    q = ' '.join([i.text for i in doc_q])
    q = q.split()
    q = q[:q_pos] + q[q_pos + 1:]
    q = ' '.join(q)
    doc_q = nlp(q)
    entities = []
    l_tok = [token for token in doc_a]
    i = 0
    while i < len(l_tok):
        if l_tok[i].tag_ in ["NN", "NNP", "NNS"] and l_tok[i].pos_ == "PROPN":
            text = l_tok[i].text
            j = i + 1
            while j < len(l_tok) and l_tok[j].tag_ in ["NN", "NNP", "NNS"] and l_tok[j].pos_ == "PROPN":
                text += " " + l_tok[j].text
                j += 1
            entities.append(text)
            i = j
        i += 1

    fin_ent = []
    for i in entities:
        flag = 0
        doc = nlp(i)
        for j in doc.ents:
            if j.text != i or j.label_ not in ["PERSON", "ORG"]:
                flag = 1
        if flag == 0:
            fin_ent.append(i)

    entities = fin_ent
    for i in range(len(ner_label)):
        if ner_label[i] in ["PERSON", "ORG"]:
            entities.append(ner_text[i])

    max_sim = -1;
    if len(entities) == 0:
        return a_s
    elif len(entities) == 1:
        return entities[0]

    else:
        max_t = entities[0];
        for i in entities:
            new_as = a_s.replace(i, "")
            new_doc_as = nlp(new_as)
            sim = doc_q.similarity(new_doc_as)
            if sim > max_sim:
                max_sim = sim
                max_t = i

        return max_t

# Answer binary question type
def binary(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp):
    # Get all the ADJ ADV NOUN VERB from question and check if they are in answer
    q = q.lower()
    doc_q = nlp(q)
    a_s = a_s.lower()
    doc_a = nlp(a_s)
    question_texts = []
    for token in doc_q:
        if token.pos_ in ["ADJ", "NOUN", "VERB", "PROPN"]:
            question_texts.append(token.text)

    answer_texts = []
    for token in doc_a:
        if token is None:
            continue
        if token.pos_ == "VERB":
            inflected_token = token._.inflect("VB")
            if inflected_token != token.text:
                answer_texts.append(inflected_token)
            answer_texts.append(token.text)
        else:
             answer_texts.append(token.text)

    q = "";
    for i in question_texts:
        if i is not None:
            q += i +" "
    q = q.strip()
    a_s = "";
    for i in answer_texts:
        if i is not None:
            a_s += i + " "
    a_s = a_s.strip()
    # q = " ".join(question_texts)
    # a_s = " ".join(answer_texts)
    doc_q = nlp(q)
    doc_a = nlp(a_s)

    stemmed_q = []
    stemmed_a = []
    for token in doc_q:
        stemmed_q.append(ps.stem(token.text))
    for token in doc_a:
        stemmed_a.append(ps.stem(token.text))
    q = " ".join(stemmed_q)
    a_s = " ".join(stemmed_a)
    doc_q = nlp(q)
    doc_a = nlp(a_s)

    # Check if token exists with neg dependency
    is_question_negated = 0
    for token in doc_q:
        if token.dep_ == "neg":
            is_question_negated = 1
            break

    is_answer_negated = 0
    for token in doc_a:
        if token.dep_ == "neg":
            is_answer_negated = 1
            break

    question_texts = []
    answer_texts = []
    for token in doc_q:
        question_texts.append(token.text.strip())
    for token in doc_a:
        answer_texts.append(token.text.strip())

    for text in question_texts:
        if text not in answer_texts:
            syn_hyp = synonyms(text).union(hyponyms(text))
            ants = antonyms(text)
            check = any(item in answer_texts for item in syn_hyp)
            if not check:
                return "No"
            check = any(item in answer_texts for item in ants)
            if not check:
                return "No"

    if (is_question_negated and is_answer_negated) or (not is_question_negated and not is_answer_negated):
        return "Yes"
    else:
        return "No"



def what(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp):
    # Return the sentence as what and which questions can be subjective and is difficult to parse based on rules
    return a_s

def which(q, doc_q, q_pos, a_s, doc_a, ner_text, ner_label, nlp):
    return a_s

