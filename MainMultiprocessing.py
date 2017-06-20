from __future__ import print_function

from nltk.tokenize.punkt import PunktSentenceTokenizer
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import networkx as nx
import os, os.path
from multiprocessing import Pool


def open_file(file_name):
    f = open(file_name, "r")
    return f.read()


def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])


def sentence_splitter(file_name):
    with open(file_name) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    paragraph = []
    for sentence in content:
        sentences = sentence.split(".")
        for tem in sentences:
            space = tem.count(" ")
            if (tem != "" and space > 2):
                paragraph.append(remove_non_ascii(tem))

    content = ". ".join(paragraph)

    # document = open_file(file_name)
    # document.replace("." , " ")
    # document = '. '.join(document.strip().split(' \n'))
    # document.replace('\n', " ")

    sentence_tokenizer = PunktSentenceTokenizer()
    sentences = sentence_tokenizer.tokenize(content)
    return sentences


def bag_of_words(sentences):
    for sentence in sentences:
        return Counter(word.lower().strip('.,') for word in sentence.split(' '))


def create_matrix(sentences):
    c = CountVectorizer()
    bow_matrix = c.fit_transform(sentences)
    return bow_matrix


def matrix_normalizer(bow_matrix):
    normalized_matrix = TfidfTransformer().fit_transform(bow_matrix)
    return normalized_matrix


def get_similairty_graph(bow_matrix):
    normalized_matrix = matrix_normalizer(bow_matrix)
    similarity_graph = normalized_matrix * normalized_matrix.T
    return similarity_graph


def sentence_ranker(similarity_graph):
    nx_graph = nx.from_scipy_sparse_matrix(similarity_graph)
    scores = nx.pagerank(nx_graph)
    return scores


def score_sorter(scores, sentences):
    ranked = sorted(((scores[i], s) for i, s in enumerate(sentences)),
                    reverse=True)
    return ranked


def ranker(file_name, k):
    sentences = sentence_splitter(file_name)
    sentence_to_file(file_name, sentences)
    bow_matrix = create_matrix(sentences)
    similarity_graph = get_similairty_graph(bow_matrix)
    scores = sentence_ranker(similarity_graph)
    ranked = score_sorter(scores, sentences)
    return ranked[0:k]


def sentence_to_file(file_name, sentences):
    file_name = "SentenceOutput/" + file_name
    f = open(file_name, "w")
    for s in sentences:
        print(s, file=f)
    print("Sentence collection for doc - Done")


def process_file(file_name):
    n = 2  # number of legal case docs
    k = 10  # number of sentences to be returned by textrank
    print (file_name)
    rank_file_name = "Cases/" + file_name + ".txt"
    ranked = ranker(rank_file_name, k)

    output_file_name = "Output/" + file_name + ".txt"
    f = open(output_file_name, "w")
    for j in range(0, k):
        print(ranked[j][1], file=f)

    return True


def store_sentences(n, k):
    r_matrix = []
    r_matrix.append([])

    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Cases")
    # print path
    fileNames = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    nameIndex = []
    for fn in fileNames:
        nameIndex.append(fn.split(".")[0])
    nameIndex.sort()

    p = Pool(8)
    success = p.map(process_file, nameIndex)

if __name__ == '__main__':
    n = 2  # number of legal case docs
    k = 10  # number of sentences to be returned by textrank
    print("k sentence picking is started")
    store_sentences(n, k)
    print("k sentence picking is finished")
    # print(ranker("Cases/case0.txt", 10))
