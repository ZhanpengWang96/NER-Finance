import logging, sys, argparse


def str2bool(v):
    # copy from StackOverflow
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_entity_of_one_type(tag_seq, char_seq, type):
    length = len(char_seq)
    ENTITY = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-' + type.upper():
            if type.lower() in locals().keys():
                ENTITY.append(entity)
                del entity
            entity = char
            if i + 1 == length:
                ENTITY.append(entity)
        if tag == 'I-' + type.upper():
            entity += char
            if i + 1 == length:
                ENTITY.append(entity)
        if tag not in ['I-' + type.upper(), 'B-' + type.upper()]:
            if type.lower() in locals().keys():
                ENTITY.append(entity)
                del entity
            continue
    return ENTITY


def get_entity(tag_seq, char_seq):
    PER = get_PER_entity(tag_seq, char_seq)
    LOC = get_LOC_entity(tag_seq, char_seq)
    ORG = get_ORG_entity(tag_seq, char_seq)
    COM = get_COM_entity(tag_seq, char_seq)
    PRO = get_PRO_entity(tag_seq, char_seq)

    return PER, LOC, ORG, COM, PRO


def get_PER_entity(tag_seq, char_seq):
    length = len(char_seq)
    PER = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-PER':
            if 'per' in locals().keys():
                PER.append(per)
                del per
            per = char
            if i + 1 == length:
                PER.append(per)
        if tag == 'I-PER':
            per += char
            if i + 1 == length:
                PER.append(per)
        if tag not in ['I-PER', 'B-PER']:
            if 'per' in locals().keys():
                PER.append(per)
                del per
            continue
    return PER


def get_LOC_entity(tag_seq, char_seq):
    length = len(char_seq)
    LOC = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-LOC':
            if 'loc' in locals().keys():
                LOC.append(loc)
                del loc
            loc = char
            if i + 1 == length:
                LOC.append(loc)
        if tag == 'I-LOC':
            loc += char
            if i + 1 == length:
                LOC.append(loc)
        if tag not in ['I-LOC', 'B-LOC']:
            if 'loc' in locals().keys():
                LOC.append(loc)
                del loc
            continue
    return LOC


def get_ORG_entity(tag_seq, char_seq):
    length = len(char_seq)
    ORG = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-ORG':
            if 'org' in locals().keys():
                ORG.append(org)
                del org
            org = char
            if i + 1 == length:
                ORG.append(org)
        if tag == 'I-ORG':
            org += char
            if i + 1 == length:
                ORG.append(org)
        if tag not in ['I-ORG', 'B-ORG']:
            if 'org' in locals().keys():
                ORG.append(org)
                del org
            continue
    return ORG


def get_COM_entity(tag_seq, char_seq):
    length = len(char_seq)
    COM = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-COM':
            if 'com' in locals().keys():
                COM.append(com)
                del com
            com = char
            if i + 1 == length:
                COM.append(com)
        if tag == 'I-COM':
            com += char
            if i + 1 == length:
                COM.append(com)
        if tag not in ['I-COM', 'B-COM']:
            if 'com' in locals().keys():
                COM.append(com)
                del com
            continue
    return COM


def get_PRO_entity(tag_seq, char_seq):
    length = len(char_seq)
    PRO = []
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-PRO':
            if 'pro' in locals().keys():
                PRO.append(pro)
                del pro
            pro = char
            if i + 1 == length:
                PRO.append(pro)
        if tag == 'I-PRO':
            pro += char
            if i + 1 == length:
                PRO.append(pro)
        if tag not in ['I-PRO', 'B-PRO']:
            if 'pro' in locals().keys():
                PRO.append(pro)
                del pro
            continue
    return PRO


def get_logger(filename):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    return logger
