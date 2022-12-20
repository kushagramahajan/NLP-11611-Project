from tags import *
import copy

from nltk.corpus import wordnet as wn


def how_many(tree):
    # print('HOW MANY...inside')
  
    noun_phrase = tree[0]
    verb_phrase = tree[1]
    ques_tree = copy.deepcopy(tree)
    main_verb = verb_phrase[0]
    ind_verb_phrase = 1
    ques_tree_list = []

    
    if((len(verb_phrase) >= 2) and (main_verb.label() in [VBD, VBP, VBZ])):
        # print('HOW MANY inside first if')
        
        obj_elem = verb_phrase[1]
        
        main_noun = ""
        if(obj_elem[0].label() == CD):
            for i in range(len(obj_elem)):
                if(i == 0 or i == len(obj_elem)-1):
                    continue
                if(not (obj_elem[i].label()[0] == 'J' and obj_elem[i].label()[1] == 'J')):
                    main_noun = ""
            if(obj_elem[len(obj_elem)-1].label() == NNS):
                main_noun = (obj_elem[len(obj_elem)-1])[0]
        
        if(obj_elem.label() == NP and len(main_noun) > 0):
            # print('HOW MANY inside second if')
          
            sample_ans = copy.deepcopy((ques_tree[1])[1])
            del ((ques_tree[1])[1])
            ques_tree_list.append((ques_tree, sample_ans))

        
    ques_tree = copy.deepcopy(tree)

    main_noun = ""
    if(noun_phrase[0].label() == CD):
        for i in range(len(noun_phrase)):
            if(i == 0 or i == len(noun_phrase)-1):
                continue
            if(not (noun_phrase[i].label()[0] == 'J' and noun_phrase[i].label()[1] == 'J')):
                main_noun = ""
        if(noun_phrase[len(noun_phrase)-1].label() == NNS):
            main_noun = (noun_phrase[len(noun_phrase)-1])[0]

    # print('HOW MANY main_noun: ', main_noun)
    if(len(main_noun) > 0):
        # print('HOW MANY inside third if')
        sample_ans = copy.deepcopy(ques_tree[0])
        del (ques_tree[0])      
        ques_tree_list.append((ques_tree, sample_ans))


    return ques_tree_list



def who(tree, NERtags):
    # print('tree: ', tree)
    noun_phrase = tree[0]
    verb_phrase = tree[1]
    main_verb = verb_phrase[0]
    ind_verb_phrase = 1

    ques_tree = copy.deepcopy(tree)

    ques_tree_list = []
    hierarchy_ne = [0]
    # print('noun_phrase: ', noun_phrase)
    # print('NEpresent([0], tree, [PERSON], NERtags): ', NEpresent(hierarchy_ne, tree, [PERSON], NERtags))

    
    if((len(verb_phrase) >= 2) and (main_verb.label() in [VBD, VBP, VBZ])):
        tree_elem = verb_phrase[ind_verb_phrase]
        # print('tree_elem: ', tree_elem)
        hierarchy_ne = [1, 1]
        # print('WHO...tree_elem: ', tree_elem)
        if(NEpresent(hierarchy_ne, tree, [PERSON], NERtags) and tree_elem.label() == NP):
            del ((ques_tree[1])[1])
            ques_tree_list.append((ques_tree, None))

    ques_tree = copy.deepcopy(tree)
    hierarchy_ne = [0]
    
    if(NEpresent(hierarchy_ne, tree, [PERSON], NERtags)):
        # print('inside third if')
        del (ques_tree[0])
        ques_tree_list.append((ques_tree, None))

    

    return ques_tree_list



def where(tree, NERtags):
    noun_phrase = tree[0]
    verb_phrase = tree[1]
    main_verb = verb_phrase[0]

    ind_verb_phrase = 1

    ques_tree = copy.deepcopy(tree)

    ques_tree_list = []


    if((len(verb_phrase) >= 2) and (main_verb.label() in [VBD, VBP, VBZ])):
        # print('WHERE...inside first if')
        tree_elem = verb_phrase[ind_verb_phrase]
        # print('verb_phrase[0].label(): ', verb_phrase[0].label())
        # print('verb_phrase[1].label(): ', verb_phrase[1].label())
        # if(len(verb_phrase) >= 3):
        #   print('verb_phrase[2].label(): ', verb_phrase[2].label())
        
        if(len(verb_phrase) >= 3 and (tree_elem.label() != PP)):
            # print('WHERE...inside second if')
          
            ind_verb_phrase += 1
            tree_elem = verb_phrase[ind_verb_phrase]

        prep = tree_elem[0]
        # print('prep.label(): ', prep.label())
        # print('tree_elem.label(): ', tree_elem.label())

        if((tree_elem.label() == PP)):
            # print('WHERE...inside third if')
            # print('NERtags: ', NERtags)
            # print('NEpresent([1,ind_verb_phrase,1], tree, [LOCATION], NERtags): ', NEpresent([1,ind_verb_phrase,1], tree, [LOC, GPE], NERtags))
            obj_elem = tree_elem[1]
            hierarchy_ne = [1, ind_verb_phrase, 1]
            # print('obj_elem.label(): ', obj_elem.label())
            if((obj_elem.label() == NP) and (prep.label() in [IN, TO]) and (NEpresent(hierarchy_ne, tree, [LOC, GPE], NERtags) or not NEpresent(hierarchy_ne, tree, [DATE, TIME], NERtags))):
                # print('WHERE...inside fourth if')
                # print('sample_ans: ', sample_ans)
                del ((ques_tree[1])[ind_verb_phrase])
                # print('ques_tree: ', ques_tree)
                ques_tree_list.append((ques_tree, None))


    return ques_tree_list



def why(tree):
    # print('tree: ', tree)
    verb_phrase = tree[1]
    main_verb = verb_phrase[0]
    ind_verb_phrase = 1

    ques_tree = copy.deepcopy(tree)

    ques_tree_list = []

    if((len(verb_phrase) >= 2) and (main_verb.label() in [VBD, VBP, VBZ])):
        # print('inside main_verb label check if')
        # print('verb_phrase: ', verb_phrase)
        tree_elem = verb_phrase[ind_verb_phrase]
        # print('tree_elem: ', tree_elem)
        
        if(len(verb_phrase) >= 3 and tree_elem.label() != SBAR):
            ind_verb_phrase += 1
            tree_elem = verb_phrase[ind_verb_phrase]

        if(tree_elem.label() == SBAR and tree_elem[0].label() == IN and ((tree_elem[0])[0].lower() == 'because' or (tree_elem[0])[0].lower() == 'since' or (tree_elem[0])[0].lower() == 'as')):
            del ((ques_tree[1])[ind_verb_phrase])
            ques_tree_list.append((ques_tree, None))

    return ques_tree_list






def whose(tree):
    noun_phrase = tree[0]
    verb_phrase = tree[1]
    ques_tree = copy.deepcopy(tree)
    main_verb = verb_phrase[0]
    ind_verb_phrase = 1

    pos_pronoun_list = ['my', 'his', 'her', 'your', 'their']

    ques_tree_list = []


    
    if((len(verb_phrase) >= 2) and (main_verb.label() in [VBD, VBP, VBZ])):
        tree_elem = verb_phrase[ind_verb_phrase]
        ques_tree = copy.deepcopy(tree)

        if(tree_elem.label() == NP):
            
            ## checking for possessive pronoun

            is_pronoun = ""

            if((tree_elem[0].label() == PRP_POS) and (tree_elem[0][0].lower() in pos_pronoun_list)):
                lower_pron_pos = (tree_elem[0])[0].lower()
                for i in range(len(tree_elem)):
                    if(i == 0 or i == (len(tree_elem) - 1)):
                        continue
                    if(not (tree_elem[i].label()[0] == 'J' and tree_elem[i].label()[1] == 'J')):
                        is_pronoun = ""
                if(tree_elem[len(tree_elem)-1].label()[0] == 'N' and tree_elem[len(tree_elem)-1].label()[1] == 'N'):
                    is_pronoun = (tree_elem[len(tree_elem)-1])[0]



            if(len(is_pronoun) > 0):
                sample_ans = copy.deepcopy((ques_tree[1])[1])
                del ((ques_tree[1])[1])
                # print('ques_tree 2: ', ques_tree)
                ques_tree_list.append((ques_tree, sample_ans))
        
        ques_tree = copy.deepcopy(tree)

        if(len(verb_phrase) >= 3 and tree_elem.label() != PP):
            ind_verb_phrase += 1
            tree_elem = verb_phrase[ind_verb_phrase]
        
        prep = tree_elem[0]

        # if(len(tree_elem) >= 2):
        #   obj_elem = tree_elem[1]
        #   print('obj_elem: ', obj_elem)
          
        if((tree_elem.label() == PP) and (prep.label() in [TO, IN])):
            obj_elem = tree_elem[1]
            
            is_pronoun = ""

            if((obj_elem[0].label() == PRP_POS) and ((obj_elem[0])[0].lower() in pos_pronoun_list)):
                lower_pron_pos = (obj_elem[0])[0].lower()
                for i in range(len(obj_elem)):
                    if(i == 0 or i == (len(obj_elem) - 1)):
                        continue
                    if(not (obj_elem[i].label()[0] == 'J' and obj_elem[i].label()[1] == 'J')):
                        is_pronoun = ""
                if(obj_elem[len(obj_elem)-1].label()[0] == 'N' and obj_elem[len(obj_elem)-1].label()[1] == 'N'):
                    is_pronoun = (obj_elem[len(obj_elem)-1])[0]

            
            if((len(is_pronoun) > 0) and (obj_elem.label() == NP)):
                sample_ans = copy.deepcopy((ques_tree[1])[ind_verb_phrase])
                del ((ques_tree[1])[ind_verb_phrase])
                # print('ques_tree 3: ', ques_tree)
                ques_tree_list.append((ques_tree, sample_ans))

    
    

    ## checking possessive pronoun
          
    is_pronoun = ""

    if((noun_phrase[0].label() == PRP_POS) and ((noun_phrase[0])[0].lower() in pos_pronoun_list)):
        lower_pron_pos = (noun_phrase[0])[0].lower()

        for i in range(len(noun_phrase)):
            if(i == 0 or i == (len(noun_phrase) - 1)):
                continue
            if(not (noun_phrase[i].label()[0] == 'J' and noun_phrase[i].label()[1] == 'J')):
                is_pronoun = ""

        if(noun_phrase[len(noun_phrase)-1].label()[0] == 'N' and noun_phrase[len(noun_phrase)-1].label()[1] == 'N'):
            is_pronoun = (noun_phrase[len(noun_phrase)-1])[0]



    if(len(is_pronoun) > 0):
        sample_ans = copy.deepcopy(ques_tree[0])
        del ques_tree[0]
        # print('ques_tree 1: ', ques_tree)
        ques_tree_list.append((ques_tree, sample_ans))



    # print('ques_tree_list: ', ques_tree_list)
    return ques_tree_list







def whom(tree, NERtags):
    noun_phrase = tree[0]
    verb_phrase = tree[1]
    main_verb = verb_phrase[0]
    ind_verb_phrase = 1

    ques_tree = copy.deepcopy(tree)

    ques_tree_list = []

    if((len(verb_phrase) >= 2) and (main_verb.label() in [VBD, VBP, VBZ])):
        tree_elem = verb_phrase[ind_verb_phrase]
        
        if(len(verb_phrase) >= 3 and tree_elem.label() != PP):
            ind_verb_phrase += 1 
            tree_elem = verb_phrase[ind_verb_phrase]
        
        prep = tree_elem[0]
        # print('prep[0]: ', prep[0])
          
        if(tree_elem.label() == PP):
            obj_elem = tree_elem[1]
            hierarchy_ne = [1, ind_verb_phrase, 1]
            # print('WHOM...obj_elem: ', obj_elem)
            # print('WHOM...NEpresent([1, ind_verb_phrase, 1], tree, [PERSON], NERtags): ', NEpresent(hierarchy_ne, tree, [PERSON], NERtags))
            if(NEpresent(hierarchy_ne, tree, [PERSON], NERtags) and (obj_elem.label() == NP) and (prep.label() in [TO, IN])):
                del ((ques_tree[1])[ind_verb_phrase])
                # print('ques_tree: ', ques_tree)
                ques_tree_list.append((ques_tree, prep[0]))


    return ques_tree_list






### the ADVP condition for sentences like james came 2 days ago.
def when(tree, NERtags):
    # print('tree: ', tree)
    noun_phrase = tree[0]
    verb_phrase = tree[1]
    main_verb = verb_phrase[0]
    dir_object = verb_phrase[1]
    ques_tree = copy.deepcopy(tree)

    ques_tree_list = []
    ind_verb_phrase = 1

    # print('WHEN...in when_mod')
    # print('len(verb_phrase): ', len(verb_phrase))
    # print('main_verb.label(): ', main_verb.label())
      
    if(len(verb_phrase) >= 2 and (main_verb.label() in [VBD, VBP, VBZ])):
        tree_elem = verb_phrase[ind_verb_phrase]
        # print('WHEN...in first if')
        if(len(verb_phrase) >= 3 and (tree_elem.label() != PP and tree_elem.label() != ADVP)):
            # print('WHEN...in second if')    
            ind_verb_phrase += 1
            tree_elem = verb_phrase[ind_verb_phrase]

        prep = tree_elem[0]

        hierarchy_ne = [1, ind_verb_phrase]

        if((tree_elem.label() == ADVP) and NEpresent(hierarchy_ne, tree, [TIME, DATE], NERtags)):
            # print('WHEN...in third if')
              
            del ((ques_tree[1])[ind_verb_phrase])
            ques_tree_list.append((ques_tree, None))      


        if((tree_elem.label() == PP)):
            # print('WHEN...in fourth if')
            obj_elem = tree_elem[1]
            hierarchy_ne = [1, ind_verb_phrase, 1]

            if((obj_elem.label() == NP) and (prep.label() in [IN, TO]) and NEpresent(hierarchy_ne, tree, [TIME, DATE], NERtags)):
                # print('WHEN...in fifth if')
                del ((ques_tree[1])[ind_verb_phrase])
                ques_tree_list.append((ques_tree, None))


    return ques_tree_list





def what(tree, NERtags):
    noun_phrase = tree[0]
    verb_phrase = tree[1]
    main_verb = verb_phrase[0]
    dir_object = verb_phrase[1]

    ques_tree_list = []

    # print('noun_phrase: ', noun_phrase)
    # print('verb_phrase: ', verb_phrase)
    # print('tree: ', tree)
    # print('NERtags: ', NERtags)

    
    ques_tree = copy.deepcopy(tree)

    hierarchy_ne = [1, 1]
    
    if(dir_object.label() == NP and (not NEpresent(hierarchy_ne, ques_tree, [PERSON], NERtags)) and len(verb_phrase) >= 2 and (main_verb.label() in [VBD, VBP, VBZ])):
        del ((ques_tree[1])[1])
        ques_tree_list.append((ques_tree, None))

    # print('what ques_tree_list: ', ques_tree_list)
    
    ques_tree = copy.deepcopy(tree)
    hierarchy_ne = [0]
    # print('WHAT...NEpresent(hierarchy_ne, ques_tree, [PERSON], NERtags): ', NEpresent(hierarchy_ne, ques_tree, [PERSON], NERtags))
    # print('ques_tree[0]: ', ques_tree[0])
    if(not NEpresent(hierarchy_ne, ques_tree, [PERSON], NERtags)):
        del (ques_tree[0])
        ques_tree_list.append((ques_tree, None))

    
    return ques_tree_list



def NEpresent(hierarchy, tree, NEclass, NERtags):
    num_leaves = 0
    sample_tree = tree


    for i in range(len(hierarchy)):
        index = hierarchy[i]

        leaves_at_ind = 0
        for tree_lev in sample_tree[:index]:
            leaves_at_ind = leaves_at_ind + len(tree_lev.leaves())

        num_leaves = num_leaves + leaves_at_ind
        sample_tree = sample_tree[index]

    
    num_leaves_fin_level = num_leaves + len(sample_tree.leaves())

    
    for i in range(num_leaves, num_leaves_fin_level):
        # print('NERtags[i][0]: ', NERtags[i][0])
        if(NERtags[i][1] not in NEclass and wn.morphy(NERtags[i][0].lower())):
            temp_syn_string = wn.morphy(NERtags[i][0].lower())+'.n.01'
        else:
            temp_syn_string = NERtags[i][0].lower()+'.n.01'
        try:
            if(NERtags[i][1] not in NEclass):
                temp_syn = wn.synset(temp_syn_string)
                # print('temp_syn_string: ', temp_syn_string)
                # print('temp_syn: ', temp_syn)
              # print('temp_syn.lowest_common_hypernyms(wn.synset(homo.n.01)): ', temp_syn.lowest_common_hypernyms(wn.synset('homo.n.01')))
            if(PERSON in NEclass):
                # print('inside PERSON if...')
                if((NERtags[i][1] in NEclass) or temp_syn.lowest_common_hypernyms(wn.synset('homo.n.01'))[0] == wn.synset('person.n.01') or (NERtags[i][0].lower() in ['he', 'she', 'they'])):
                    return True
            else:
                if((NERtags[i][1] in NEclass)):
                    return True
        except:
            continue
    return False

