import codecs
import MySQLdb
import nltk
import pickle
import sys

n = 2

db = MySQLdb.connect(user='versifier', db='versifier')
c = db.cursor()

try:
    infile, corpus_name = sys.argv[1:3]
except:
    print "Please specify the input file and the corpus name!"
    exit()

c.execute('SELECT id FROM corpus WHERE name = %s', (corpus_name,))
if c.rowcount == 1:
    c.execute('DELETE FROM corpus WHERE name = %s', (corpus_name,))
    
c.execute('INSERT INTO corpus (name) VALUES (%s)', (corpus_name,))
db.commit()
c.execute('SELECT last_insert_id()')
corpus_id = c.fetchone()[0]

tokenizer = nltk.tokenize.RegexpTokenizer(r'[\w\']+|-+|[^\w\s\"\'-]')

f = codecs.open(infile, 'r', 'utf-8')
text = f.read()
toks = tokenizer.tokenize(text)
toks = [tok.lower() for tok in toks]

model = [{}, {}, {}]
last_toks = ('',) * (n + 1)
for tok in toks:
    last_toks = tuple(last_toks[i+1] if i < n else tok for i in xrange(n + 1))
    for i in xrange(n + 1):
        key = last_toks[n - i:]
        if key in model[i]:
            model[i][key] += 1
        else:
            model[i][key] = 1

for (tok,) in model[0]:
    c.execute('INSERT INTO unigram (corpus_id, tok1, count) VALUES (%s, %s, %s)',
              (corpus_id, tok, model[0][(tok,)]))
              
for (tok1, tok2) in model[1]:
    c.execute('''INSERT INTO bigram (corpus_id, tok1, tok2, count)
                 VALUES (%s, %s, %s, %s)''',
              (corpus_id, tok1, tok2, model[1][(tok1, tok2)]))
              
for (tok1, tok2, tok3) in model[2]:
    c.execute('''INSERT INTO trigram (corpus_id, tok1, tok2, tok3, count)
                 VALUES (%s, %s, %s, %s, %s)''',
              (corpus_id, tok1, tok2, tok3, model[2][(tok1, tok2, tok3)]))

db.commit()

