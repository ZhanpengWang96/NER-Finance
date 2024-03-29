import tensorflow as tf
import numpy as np
import os, argparse, time
from model import BiLSTM_CRF
from utils import str2bool, get_logger, get_entity, get_entity_of_one_type
from data import read_corpus, read_dictionary, random_embedding, read_corpus_for_eval, tag_dict_build
from data import tag2label as tag2label_default
import pickle

## Session configuration
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # default: 0
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.2  # need ~700MB GPU memory

## hyperparameters
parser = argparse.ArgumentParser(description='BiLSTM-CRF for Chinese NER task')
parser.add_argument('--train_data', type=str, default='data_path', help='train data source')
parser.add_argument('--test_data', type=str, default='data_path', help='test data source')
parser.add_argument('--batch_size', type=int, default=24, help='#sample of each minibatch')
parser.add_argument('--epoch', type=int, default=30, help='#epoch of training')
parser.add_argument('--hidden_dim', type=int, default=300, help='#dim of hidden state')
parser.add_argument('--optimizer', type=str, default='Adam', help='Adam/Adadelta/Adagrad/RMSProp/Momentum/SGD')
parser.add_argument('--CRF', type=str2bool, default=True, help='use CRF at the top layer. if False, use Softmax')
parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
parser.add_argument('--clip', type=float, default=5.0, help='gradient clipping')
parser.add_argument('--dropout', type=float, default=0.5, help='dropout keep_prob')
parser.add_argument('--update_embedding', type=str2bool, default=True, help='update embedding during training')
parser.add_argument('--pretrain_embedding', type=str, default='random',
                    help='use pretrained char embedding or init it randomly')
parser.add_argument('--embedding_dim', type=int, default=300, help='random init char embedding_dim')
parser.add_argument('--shuffle', type=str2bool, default=True, help='shuffle training data before each epoch')
parser.add_argument('--mode', type=str, default='demo', help='train/test/demo/local_test')
parser.add_argument('--demo_model', type=str, default='1521112368', help='model for test and demo')
parser.add_argument('--lang', type=str, default='en', help='zh/en choose train/test language')
parser.add_argument('--read_tags', type=str2bool, default=True, help='read tags from data set or use default tag dict')
args = parser.parse_args()

## get char embeddings
if args.lang == 'zh':
    word2id = read_dictionary(os.path.join('.', args.train_data, 'word2id.pkl'))
    if args.pretrain_embedding == 'random':
        embeddings = random_embedding(word2id, args.embedding_dim)
    else:
        embedding_path = 'pretrain_embedding.npy'
        embeddings = np.array(np.load(embedding_path), dtype='float32')
else:
    word2id = read_dictionary(os.path.join('.', args.train_data, 'word2id_en.pkl'))
    embeddings = random_embedding(word2id, args.embedding_dim)

# define tags dictionary
if args.read_tags:
    # change whlie changing dataset
    tag2label = tag_dict_build(os.path.join('.', args.train_data, 'train_data_en'))
    # print(tag2label)
else:
    tag2label = tag2label_default

# read corpus and get training data
if args.mode != 'demo':
    # change whlie changing dataset
    train_path = os.path.join('.', args.train_data, 'train_data_en')
    # change whlie changing dataset
    test_path = os.path.join('.', args.test_data, 'test_data_en')
    train_data = read_corpus(train_path)
    test_data = read_corpus(test_path);
    test_size = len(test_data)
    _, test_data_raw = read_corpus_for_eval(test_path)

# paths setting
paths = {}
timestamp = str(int(time.time())) if args.mode == 'train' else args.demo_model
output_path = os.path.join('.', args.train_data + "_save", timestamp)
if not os.path.exists(output_path): os.makedirs(output_path)
summary_path = os.path.join(output_path, "summaries")
paths['summary_path'] = summary_path
if not os.path.exists(summary_path): os.makedirs(summary_path)
model_path = os.path.join(output_path, "checkpoints/")
if not os.path.exists(model_path): os.makedirs(model_path)
ckpt_prefix = os.path.join(model_path, "model")
paths['model_path'] = ckpt_prefix
result_path = os.path.join(output_path, "results")
paths['result_path'] = result_path
if not os.path.exists(result_path): os.makedirs(result_path)
log_path = os.path.join(result_path, "log.txt")
paths['log_path'] = log_path
get_logger(log_path).info(str(args))

# training model
if args.mode == 'train':
    pickle.dump(tag2label, open(os.path.join(output_path, 'tag2label'), 'wb'))
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()

    ## train model on the whole training data
    print("train data: {}".format(len(train_data)))
    model.train(train=train_data, dev=test_data)  # use test_data as the dev_data to see overfitting phenomena

# testing model
elif args.mode == 'test':
    tag2label = pickle.load(open(os.path.join(output_path, 'tag2label'), 'rb'))
    ckpt_file = tf.train.latest_checkpoint(model_path)
    print(ckpt_file)
    paths['model_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    print("test data: {}".format(test_size))
    model.test(test_data)



## testing model locally
elif args.mode == 'local_test':
    tag2label = pickle.load(open(os.path.join(output_path, 'tag2label'), 'rb'))
    ckpt_file = tf.train.latest_checkpoint(model_path)
    print(ckpt_file)
    paths['model_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    saver = tf.train.Saver()
    with tf.Session(config=config) as sess:
        print('============= local_test =============')
        saver.restore(sess, ckpt_file)
        print(model.evaluate_local(sess, test_data, test_data_raw))



## demo
elif args.mode == 'demo':
    tag2label = pickle.load(open(os.path.join(output_path, 'tag2label'), 'rb'))
    ckpt_file = tf.train.latest_checkpoint(model_path)
    print(ckpt_file)
    paths['model_path'] = ckpt_file
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths, config=config)
    model.build_graph()
    saver = tf.train.Saver()
    print(tag2label)
    keyset = set()

    for key in list(tag2label.keys()):
        if key == 'O':
            continue
        keyset.add(key[2:])

    with tf.Session(config=config) as sess:
        print('============= demo =============')
        saver.restore(sess, ckpt_file)
        if args.lang == 'zh':
            while (1):
                print('Please input your sentence:')
                demo_sent = input()
                if demo_sent == '' or demo_sent.isspace():
                    print('See you next time!')
                    break
                else:
                    demo_sent = list(demo_sent.strip())
                    demo_data = [(demo_sent, ['O'] * len(demo_sent))]
                    print(demo_data)
                    tag = model.demo_one(sess, demo_data)
                    print(tag)
                    # PER, LOC, ORG, COM, PRO = get_entity(tag, demo_sent)
                    # print('PER: {}\nLOC: {}\nORG: {}\nCOM: {}\nPRO: {}'.format(PER, LOC, ORG, COM, PRO))

        elif args.lang == 'en':
            while (1):
                print('Please input your sentence:')
                sent = input()
                if sent == '' or sent.isspace():
                    print('See you next time!')
                    break
                else:
                    sent = list(sent.strip().split(' '))
                    demo_sent = []
                    for word in sent:
                        if word.isspace():
                            continue
                        demo_sent.append(word.strip().lower())
                    demo_data = [(demo_sent, ['O'] * len(demo_sent))]
                    tag = model.demo_one(sess, demo_data)
                    output_list = []
                    for w, t in zip(demo_sent, tag):
                        output_list.append([w, t])

                    print(output_list)
                    # for key in keyset:
                    #     entity = get_entity_of_one_type(tag, demo_sent, key)
                    #     print(key)
                    #     print(entity)



elif args.mode == 'atom':
    sent = input()
    sent = list(sent.strip().split(' '))
    demo_sent = []
    print(sent)
    for word in sent:
        if word.isspace():
            continue
        demo_sent.append(word.strip().lower())

    print(demo_sent)
    # keyset = set()
    # for key in list(tag2label.keys()):
    #     if key == 'O':
    #         continue
    #     keyset.add(key[2:])
    #
    # print(keyset)
