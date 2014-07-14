CREATE DATABASE versifier;
USE versifier;

CREATE TABLE corpus (
  id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE unigram (
  corpus_id INTEGER NOT NULL,
  tok1 VARCHAR(31) NOT NULL,
  count BIGINT NOT NULL,
  FOREIGN KEY unigram_corpus_id (corpus_id) REFERENCES corpus (id) ON DELETE CASCADE,
  KEY (corpus_id, tok1)
);

CREATE TABLE bigram (
  corpus_id INTEGER NOT NULL,
  tok1 VARCHAR(31) NOT NULL,
  tok2 VARCHAR(31) NOT NULL,
  count BIGINT NOT NULL,
  FOREIGN KEY bigram_corpus_id (corpus_id) REFERENCES corpus (id) ON DELETE CASCADE,
  KEY (corpus_id, tok1, tok2)
);

CREATE TABLE trigram (
  corpus_id INTEGER NOT NULL,
  tok1 VARCHAR(31) NOT NULL,
  tok2 VARCHAR(31) NOT NULL,
  tok3 VARCHAR(31) NOT NULL,
  count BIGINT NOT NULL,
  FOREIGN KEY trigram_corpus_id (corpus_id) REFERENCES corpus (id) ON DELETE CASCADE,
  KEY (corpus_id, tok1, tok2, tok3)
);
