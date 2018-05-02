import sys, pickle, os, random
import numpy as np

## tags, BIO
tag2label = {"O": 0,
             "B-PER": 1, "I-PER": 2,
             "B-LOC": 3, "I-LOC": 4,
             "B-ORG": 5, "I-ORG": 6,
             "B-COM": 7, "I-COM": 8,
             "B-PRO": 9, "I-PRO": 10,
             "B-MISC": 11, "I-MISC": 12
             }


def read_corpus(corpus_path):
    """
    read corpus and return the list of samples
    :param corpus_path:
    :return: data 以句子为单位返回二元祖列表
    """
    data = []
    with open(corpus_path, encoding='utf-8') as fr:
        lines = fr.readlines()
    sent_, tag_ = [], []
    for line in lines:
        if line != '\n':
            if len(line.strip().split()) == 2:
                [char, label] = line.strip().split()
            sent_.append(char)
            tag_.append(label)
        else:
            data.append((sent_, tag_))
            sent_, tag_ = [], []

    return data


def read_corpus_for_eval(corpus_path):
    """
    read corpus and return the list of samples
    :param corpus_path:
    :return: data 以句子为单位返回二元祖列表
            data_raw 返回的二元组列表, 但是未经预测
    """
    data, data_raw = [], []
    with open(corpus_path, encoding='utf-8') as fr:
        lines = fr.readlines()
    sent_, tag_, tag_raw = [], [], []
    for line in lines:
        if line != '\n':
            if len(line.strip().split()) == 2:
                [char, label] = line.strip().split()
            sent_.append(char)
            tag_.append(label)
            tag_raw.append('O')
        else:
            data.append((sent_, tag_))
            data_raw.append((sent_, tag_raw))
            sent_, tag_, tag_raw = [], [], []

    return data, data_raw


def vocab_build(vocab_path, corpus_path, min_count):
    """

    :param vocab_path:
    :param corpus_path:
    :param min_count:
    :return:
    """
    data = read_corpus(corpus_path)
    word2id = {}
    for sent_, tag_ in data:
        for word in sent_:
            if word.isdigit():
                word = '<NUM>'
            elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
                word = '<ENG>'
            if word not in word2id:
                word2id[word] = [len(word2id) + 1, 1]
            else:
                word2id[word][1] += 1
    low_freq_words = []
    for word, [word_id, word_freq] in word2id.items():
        if word_freq < min_count and word != '<NUM>' and word != '<ENG>':
            low_freq_words.append(word)
    for word in low_freq_words:
        del word2id[word]

    new_id = 1
    for word in word2id.keys():
        word2id[word] = new_id
        new_id += 1
    word2id['<UNK>'] = new_id
    word2id['<PAD>'] = 0

    print(len(word2id))
    with open(vocab_path, 'wb') as fw:
        pickle.dump(word2id, fw)


def vocab_build_en(vocab_path, corpus_path):
    data = read_corpus(corpus_path)
    word2id = {}
    for sent_, tag_ in data:
        for word in sent_:
            word = word.lower()
            if word.isdigit():
                word = '<NUM>'
            if word not in word2id:
                word2id[word] = [len(word2id) + 1, 1]
            else:
                word2id[word][1] += 1

    new_id = 1
    for word in word2id.keys():
        word2id[word] = new_id
        new_id += 1
    word2id['<UNK>'] = new_id
    word2id['<PAD>'] = 0

    print(len(word2id))
    with open(vocab_path, 'wb') as fw:
        pickle.dump(word2id, fw)


def tag_dict_build(corpus_path):
    print('reading tags..')
    raw = read_corpus(corpus_path)
    tag_set = set()
    for _, tag_ in raw:
        for tag in tag_:
            tag_set.add(tag)
    tag_dict = {}
    new_id = 0
    for tag in tag_set:
        tag_dict[tag] = new_id
        new_id += 1

    print('tags dict: ', tag_dict)

    return tag_dict


def sentence2id(sent, word2id):
    """
    把一个句子中的汉子转换成id
    :param sent:
    :param word2id:
    :return:
    """
    sentence_id = []
    for word in sent:
        if word.isdigit():
            word = '<NUM>'
        elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
            word = '<ENG>'
        if word not in word2id:
            word = '<UNK>'
        sentence_id.append(word2id[word])
    return sentence_id


def sentence2id_en(sent, word2id):
    """
    把一个句子中的单词转换成id
    :param sent:
    :param word2id:
    :return:
    """
    sentence_id = []
    for word in sent:
        if word.isdigit():
            word = '<NUM>'
        if word not in word2id:
            word = '<UNK>'
        sentence_id.append(word2id[word])
    return sentence_id


def read_dictionary(vocab_path):
    """
    读取word和id对应文件
    :param vocab_path:
    :return:
    """
    vocab_path = os.path.join(vocab_path)
    with open(vocab_path, 'rb') as fr:
        word2id = pickle.load(fr)
    print('vocab_size:', len(word2id))
    return word2id


def random_embedding(vocab, embedding_dim):
    """

    :param vocab:
    :param embedding_dim:
    :return:
    """
    embedding_mat = np.random.uniform(-0.25, 0.25, (len(vocab), embedding_dim))
    embedding_mat = np.float32(embedding_mat)
    return embedding_mat


def pad_sequences(sequences, pad_mark=0):
    """

    :param sequences:
    :param pad_mark:
    :return:
    """
    max_len = max(map(lambda x: len(x), sequences))
    seq_list, seq_len_list = [], []
    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_len] + [pad_mark] * max(max_len - len(seq), 0)
        seq_list.append(seq_)
        seq_len_list.append(min(len(seq), max_len))
    return seq_list, seq_len_list


def batch_yield(data, batch_size, vocab, tag2label, shuffle=False, lang=None):
    """
    一个迭代器 每次next 返回新的batch
    :param data:
    :param batch_size:
    :param vocab:
    :return:
    """
    if shuffle:
        random.shuffle(data)

    seqs, labels = [], []
    for (sent_, tag_) in data:
        if lang == 'zh':
            sent_ = sentence2id(sent_, vocab)  # 把对应句子中的文字换成id
        elif lang == 'en':
            sent_ = sentence2id_en(sent_, vocab) # 把对应句子中的单词换成id
        label_ = [tag2label[tag] for tag in tag_]  # 把对应句子中的标注换成字典中的数字

        if len(seqs) == batch_size:  # 够一个批次就yield
            yield seqs, labels
            seqs, labels = [], []

        seqs.append(sent_)
        labels.append(label_)

    if len(seqs) != 0:
        yield seqs, labels


if __name__ == '__main__':
    # vocab_build_en('word2id_en.pkl','train_data_en')
    raw = read_corpus('train_data_en')
    tag_set = set()
    for _, tag_ in raw:
        for tag in tag_:
            tag_set.add(tag)
    tag_dict = {}
    new_id = 1
    for tag in tag_set:
        tag_dict[tag] = new_id
        new_id += 1

    print(tag_dict)
