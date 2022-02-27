from parsi_io.modules.address_extractions import AddressExtraction
import glob
import re
import os
import collections

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]

test_dir = os.getcwd()+'/parsi_io/test/testcases/address/'

def get_testcases():
    in_texts = []
    out_texts = []
    in_files = glob.glob(test_dir+'in/input*.txt')
    out_files = glob.glob(test_dir+'out/output*.txt')
    in_files.sort(key=natural_keys)
    out_files.sort(key=natural_keys)

    for i, j in zip(in_files, out_files):
        with open(i) as f:
            in_texts.append(f.read())
        with open(j) as f:
            out_texts.append(f.read())
    return in_texts, out_texts


def test_AddressExtraction():
    errors = []
    compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

    in_texts, out_texts = get_testcases()
    o = AddressExtraction()
    for i, j, k in zip(in_texts, out_texts, range(1, len(in_texts)+1)):
        res = o.run(i)
        if not compare(res, j.split('\n')):
            errors.append('Input {0}: your answer is {1} correct answer is {2}'.format(str(k), str(res), str(j.split('\n'))))
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))
