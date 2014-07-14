import MySQLdb

from versifier import *

corpus_name = 'shakespeare'

# Quatrain in iambic trimeter
meter = 'u-u-u-|u-u-u-|u-u-u-|u-u-u-'
rhyme_scheme = 'ABAB'

# Couplets in anapestic tetrameter
#meter = 'uu-uu-uu-uu-|uu-uu-uu-uu-|uu-uu-uu-uu-|uu-uu-uu-uu-'
#rhyme_scheme = 'AABB'

# Shakespearean sonnet
#meter = '|'.join(['u-u-u-u-u-'] * 14)
#rhyme_scheme = 'ABABCDCDEFEFGG'

# Spenserian stanza
#meter = '|'.join(['u-u-u-u-u-'] * 8) + '|u-u-u-u-u-u-'
#rhyme_scheme = 'ABABBCBCC'

db = MySQLdb.connect(user='versifier', db='versifier', charset='utf8')
c = db.cursor()

c.execute('SELECT id FROM corpus WHERE name = %s', (corpus_name,))
corpus_id = c.fetchone()[0]

poem = generate_poem(c, corpus_id, meter, rhyme_scheme, 140000)
print poem
