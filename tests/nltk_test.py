#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> nltk_test
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2024/1/19 10:43
@Desc   ：
==================================================
"""
import nltk.data
from nltk import word_tokenize, PorterStemmer

nltk.data.path.append("/Users/zhanbei/PycharmProjects/infobase/nltk_data")


def nltk_stemmer(query: str):
    tokens = word_tokenize(query)
    stemmer = PorterStemmer()
    stems = [stemmer.stem(t) for t in tokens]

    return stems


if __name__ == '__main__':
    words: str = "What are the interfaces of the doop pipeline"
    print(nltk_stemmer(words))
