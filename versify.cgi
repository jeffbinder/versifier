#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# CGI setup

import cgi

data = cgi.FieldStorage()

corpus_name = data.getfirst('corpus_name')
meter = data.getfirst('meter')
repetitions = data.getfirst('repetitions')
rhyme_scheme = data.getfirst('rhyme_scheme')

print "Content-Type: text/html;charset=utf-8"
print

# Data validation

import re

corpus_name = str(corpus_name)
meter = str(meter)
repetitions = int(repetitions)
rhyme_scheme = str(rhyme_scheme)

if repetitions <= 0:
    print "Number of repetitions must be positive."
    exit()
if (len(meter) + 1) * repetitions > (16 + 2) * 16 + 1:
    print "Meter pattern is too long."
    exit()
if not corpus_name in ('coleridge', 'byron', 'shakespeare', 'milton'):
    print "Invalid corpus name."
    exit()
if not re.match(r'[-u|]+', meter):
    print "Invalid meter."
    exit()
    
meter = '|'.join([meter] * repetitions)

lines = meter.split('|')
num_non_empty_lines = len([1 for line in lines if len(line) > 0])
max_syllables = max(len(line) for line in lines)

if num_non_empty_lines > 16:
    print "Number of lines cannot exceed 16."
    exit()
if max_syllables > 16:
    print "Lines cannot have more than 16 syllables."
    exit()
if len(rhyme_scheme) > num_non_empty_lines:
    print "Not enough lines for rhyme scheme."
    exit()
if len(rhyme_scheme) < num_non_empty_lines:
    print "Too many lines for rhyme scheme."
    exit()

# Connect to database

import MySQLdb
from versifier import *
from config import *

db = MySQLdb.connect(user=mysql_username, passwd=mysql_passwd, db='versifier', charset='utf8')
c = db.cursor()

c.execute('SELECT id FROM corpus WHERE name = %s', (corpus_name,))
corpus_id = c.fetchone()[0]

# Generate poem

poem = generate_poem(c, corpus_id, meter, rhyme_scheme, None, gen_html=True)
print poem
