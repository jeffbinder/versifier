import pickle
import random
import re
import unicodedata

n = 2

from nltk.corpus import cmudict
dictionary = cmudict.dict()
from nltk.corpus import stopwords
stopwords = stopwords.words('english')

vowel_cluster = re.compile('[aeiouyAEIOUY]+')
word = re.compile(r'\w[\w\']*|\'\w[\w\']*')

def remove_accents(str):
    nkfd_form = unicodedata.normalize('NFKD', str)
    return u''.join([c for c in nkfd_form if not unicodedata.combining(c)])

def get_nsyls(tok):
    if not word.match(tok):
        return 0
    if not tok in dictionary:
        num_vowel_clusters = vowel_cluster.findall(remove_accents(tok))
        nsyls = len(num_vowel_clusters)
        if nsyls == 0:
            nsyls = 1
        return nsyls
    pron = dictionary[tok][0]
    nsyls = sum(1 for ph in pron if ph[-1].isdigit())
    return nsyls

def get_meter(tok):
    if not word.match(tok):
        return ''
    if not tok in dictionary:
        return None
    pron = dictionary[tok][0]
    meter = ''
    for ph in pron:
        if ph[-1].isdigit():
            meter += 'u' if ph[-1] == '0' else '-'
    return meter
    
def get_rhyme(tok):
    if not tok in dictionary:
        return None
    pron = dictionary[tok][0]
    rhyme = ''
    for ph in pron:
        if ph[-1].isdigit():
            rhyme = ph
        else:
            rhyme += ph
    return rhyme

def validate_punct(tok, desired_meter, punct_permitted, desired_rhyme):
    if tok in ('$', '{', '}', '(', ')', '[', ']') or tok.isdigit():
        return False
    if word.match(tok):
        return False
    return punct_permitted

def validate_word(tok, desired_meter, punct_permitted, desired_rhyme):
    if tok.isdigit():
        return False
    if not word.match(tok):
        return False
        
    meter = get_meter(tok)
    if meter:
        if not desired_meter.startswith(meter):
            return False
        nsyls = len(meter)
    else:
        return False
        # Alternative: just check the estimated number of syllables and ignore
        # meter for words not in the dictionary.
        #nsyls = get_nsyls(tok)
        #if '|' in desired_meter[:nsyls]:
        #    return False
    
    if (len(desired_meter) <= nsyls or desired_meter[nsyls] == '|') and desired_rhyme:
        if tok in stopwords:
            return False
        rhyme = get_rhyme(tok)
        if desired_rhyme is True:
            return rhyme is not None
        else:
            rhyme_pattern, prohibited_words = desired_rhyme
            return rhyme == rhyme_pattern and tok not in prohibited_words
        
    return True

def get_next_tok(c, corpus_id, last_toks, desired_meter, punct_permitted, desired_rhyme):

    if len(last_toks) == 2:
        c.execute('''SELECT tok3, count FROM trigram
                     WHERE corpus_id = %s AND tok1 = %s AND tok2 = %s''',
                  (corpus_id, last_toks[0], last_toks[1]))
    elif len(last_toks) == 1:
        c.execute('''SELECT tok2, count FROM bigram
                     WHERE corpus_id = %s AND tok1 = %s''',
                  (corpus_id, last_toks[0]))
    elif len(last_toks) == 0:
        c.execute('''SELECT tok1, count FROM unigram
                     WHERE corpus_id = %s''',
                  (corpus_id,))
                  
    if not c.rowcount:
        return get_next_tok(c, corpus_id, last_toks[1:], desired_meter, punct_permitted, desired_rhyme)
    
    d = dict(c.fetchall())
    
    # First determine whether there will be a punctuation mark next.
    punct_options = [tok for tok in d if validate_punct(tok, desired_meter,
                                                        punct_permitted, desired_rhyme)]
    total = sum(d[x] for x in d)
    probs = []
    p1 = 0.0
    for tok2 in punct_options:
        p2 = p1 + float(d[tok2]) / total
        probs.append((tok2, p1, p2))
        p1 = p2
    probs.append((None, p1, 1.0))
    
    x = random.random()
    for tok, p1, p2 in probs:
        if x >= p1 and x < p2:
            break
    if tok:
        return tok, desired_meter
    
    # If a punctuation mark wasn't selected, try to find a word to use. 
    word_options = [tok for tok in d if validate_word(tok, desired_meter,
                                                      punct_permitted, desired_rhyme)]
    if not word_options:
        if len(last_toks) == 0:
            return None
        else:
            return get_next_tok(c, corpus_id, last_toks[1:], desired_meter, punct_permitted, desired_rhyme)
    
    total = sum(d[x] for x in word_options)
    probs = []
    p1 = 0.0
    for tok2 in word_options:
        p2 = p1 + float(d[tok2]) / total
        probs.append((tok2, p1, p2))
        p1 = p2
    
    x = random.random()
    for tok, p1, p2 in probs:
        if x >= p1 and x < p2:
            break
    nsyls = get_nsyls(tok)
    return tok, desired_meter[nsyls:]

def generate_poem(c, corpus_id, meter, rhyme_scheme, max_len, gen_html=False):
    remaining_meter = meter
    remaining_rhyme_scheme = rhyme_scheme

    last_toks = ('$',) * n
    start_of_line = True
    start_of_sentence = True
    punctuation_permitted = False
    hyphen_before = False
    rhymes = {}

    poem = ''

    while remaining_meter:
        if remaining_meter.startswith('|'):
            # Used when there is an empty line.
            poem += '<br/>' if gen_html else '\n'
            remaining_meter = remaining_meter[1:]
            start_of_line = True
            
        if remaining_rhyme_scheme:
            rhyme_type = remaining_rhyme_scheme[0]
            desired_rhyme = rhymes.get(rhyme_type, True)
        else:
            desired_rhyme = False

        result = get_next_tok(c, corpus_id, last_toks, remaining_meter,
                              punctuation_permitted and not start_of_line,
                              desired_rhyme)
        if result:
            tok, remaining_meter = result
        else:
            return generate_poem(c, corpus_id, meter, rhyme_scheme, max_len, gen_html)
    
        if word.match(tok):
            punctuation_permitted = True
        else:
            punctuation_permitted = False
    
        if not start_of_line and not hyphen_before and word.match(tok):
            poem += ' '
        if start_of_sentence:
            if tok.startswith('\''):
                poem += '\'' + tok[1:].capitalize()
            else:
                poem += tok.capitalize()
        elif tok == 'i':
            poem += 'I'
        elif tok.startswith('i\''):
            poem += tok.capitalize()
        else:
            poem += tok
    
        if tok in ('.', '!', '?'):
            start_of_sentence = True
        else:
            start_of_sentence = False
        if tok.endswith('-'):
            hyphen_before = True
        else:
            hyphen_before = False
        
        if remaining_meter.startswith('|'):
            if rhyme_type in rhymes:
                rhyme, prohibited_words = rhymes[rhyme_type]
                rhymes[rhyme_type] = (rhyme, prohibited_words + [tok])
            else:
                rhymes[rhyme_type] = (get_rhyme(tok), [tok])
            poem += '<br/>' if gen_html else '\n'
            remaining_meter = remaining_meter[1:]
            remaining_rhyme_scheme = remaining_rhyme_scheme[1:]
            start_of_line = True
        else:
            start_of_line = False
            
        if max_len is not None and len(poem) > max_len - 1:
            return generate_poem(c, corpus_id, meter, rhyme_scheme, max_len, gen_html)
        
        last_toks = tuple(last_toks[i+1] if i < n - 1 else tok for i in xrange(n))
            
    return poem + '.'
