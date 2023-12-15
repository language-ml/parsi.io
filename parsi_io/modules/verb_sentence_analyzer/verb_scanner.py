import re


def find_shenase_from_mazi(shenase_mazi):
    if shenase_mazi == 'م':
        return 1
    if shenase_mazi == 'ی':
        return 2
    if shenase_mazi == '':
        return 3
    if shenase_mazi == 'یم':
        return 4
    if shenase_mazi == 'ید':
        return 5
    if shenase_mazi == 'ند':
        return 6


def find_shenase_from_naghli(shenase_mazi):
    if shenase_mazi == 'ام':
        return 1
    if shenase_mazi == 'ای':
        return 2
    if shenase_mazi == 'است':
        return 3
    if shenase_mazi == 'ایم':
        return 4
    if shenase_mazi == 'اید':
        return 5
    if shenase_mazi == 'اند':
        return 6


def find_shenase_from_mozare(shenase_mozare):
    if shenase_mozare == 'م':
        return 1
    if shenase_mozare == 'ی':
        return 2
    if shenase_mozare == 'د':
        return 3
    if shenase_mozare == 'یم':
        return 4
    if shenase_mozare == 'ید':
        return 5
    if shenase_mozare == 'ند':
        return 6


def remove_whitespaces(string):
    return "".join(re.split(r'[\s,\u200c]+', string))


with open('parsi_io/modules/verb_sentence_analyzer/infinitive.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

shakhs_name = {
    1: 'من',
    2: 'تو',
    3: 'او',
    4: 'ما',
    5: 'شما',
    6: 'ایشان'
}

bon_mazis = {}
bon_mozares = {}
for line in lines:
    columns = line.strip().split('@')
    if columns[9] != "WRITTEN":
        continue
    if columns[-4] != "" and columns[-4] not in bon_mozares.keys():
        bon_mozares[remove_whitespaces(columns[-4])] = columns[1]
    if columns[-5] != "" and columns[-5] not in bon_mazis.keys():
        bon_mazis[remove_whitespaces(columns[-5])] = columns[1]



mianjis_mozare = {}
for bon in bon_mozares.keys():
    mianjis_mozare['ی' + bon.replace('آ', 'ا') + 'ی'] = bon
    mianjis_mozare['ی' + bon.replace('آ', 'ا')] = bon
    mianjis_mozare[bon + 'ی'] = bon


bon_mazi_pattern = '(?P<bon_mazi>' + f'{"|".join(bon_mazis.keys())})'
bon_mozare_pattern = '(?P<bon_mozare>' + f'{"|".join(bon_mozares.keys())})'

bon_mozare_pattern_mianji = '(?P<bon_mozare>' + f'{"|".join(mianjis_mozare.keys())})'

pishvands = ['فرو', 'باز', 'در', 'فرا', 'بر', 'فر', 'ور', 'وا', 'پیش', 'پس', 'هم']

pishvand_patterns = '(?P<pishvand>' + f'{"|".join(pishvands)})'

shenase_mazi_without_name = '(' + 'م|ی|یم|ید|ند)?'
shenase_mazi = '(?P<shenase_mazi>' + 'م|ی|یم|ید|ند)?'
shenase_naghli = '(?P<shenase_naghli>' + 'ام|ای|است|ایم|اید|اند)'
shenase_naghli_without_name = '(' + 'ام|ای|است|ایم|اید|اند)'
shenase_mozare = '(?P<shenase_mozare>' + 'م|ی|د|یم|ید|ند)'
shenase_mozare_without_name = '(' + 'م|ی|د|یم|ید|ند)'

mazi_sade = '^' + pishvand_patterns + '?' + 'ن?' + bon_mazi_pattern + shenase_mazi + '$'
mazi_naghli = '^' + pishvand_patterns + '?' + 'ن?' + bon_mazi_pattern + 'ه ' + shenase_naghli + '$'
mazi_estemrari = '^' + pishvand_patterns + '?' + 'ن?' + 'می ' + bon_mazi_pattern + shenase_mazi + '$'
# mazi_naghli_mostamar = '^' + 'ن?' + 'داشته' + shenase_naghli_without_name + 'می ' + 'ن?' + bon_mazi_pattern + 'ه ' + shenase_naghli + '$'
mazi_baeed = '^' + pishvand_patterns + '?' + 'ن?' + bon_mazi_pattern + 'ه بود' + shenase_mazi + '$'
mazi_eltezami = '^' + pishvand_patterns + '?' + 'ن?' + bon_mazi_pattern + 'ه باش' + shenase_mazi + '$'
mazi_mostamar = '^' + 'داشت' + shenase_mazi_without_name + ' ' + pishvand_patterns + '?' + 'ن?' + 'می ' + bon_mazi_pattern + shenase_mazi + '$'

mozare_ekhbari = '^' + pishvand_patterns + '?' + 'ن?' + 'می ' + bon_mozare_pattern + shenase_mozare + '$'
mozare_eltezami = '^' + pishvand_patterns + '?' + '(ن|ب)?' + bon_mozare_pattern + shenase_mozare + '$'  # ب میتونه حذف شه  این نکته دارد
mozare_mostamar = '^' + 'دار' + shenase_mozare_without_name + ' ' + pishvand_patterns + '?' + 'ن?' + 'می ' + bon_mozare_pattern + shenase_mozare + '$'

mozare_ekhbari_mianji = '^' + pishvand_patterns + '?' + 'ن?' + 'می ' + bon_mozare_pattern_mianji + shenase_mozare + '$'
mozare_eltezami_mianji = '^' + pishvand_patterns + '?' + '(ن|ب)?' + bon_mozare_pattern_mianji + shenase_mozare + '$'  # ب میتونه حذف شه  این نکته دارد
mozare_mostamar_mianji = '^' + 'دار' + shenase_mozare_without_name + ' ' + pishvand_patterns + '?' + 'ن?' + 'می ' + bon_mozare_pattern_mianji + shenase_mozare + '$'

ayande = '^' + pishvand_patterns + '?' + 'ن?' + 'خواه' + shenase_mozare + ' ' + bon_mazi_pattern + '$'

all_regex = [mazi_sade, mazi_naghli, mazi_estemrari, mazi_baeed, mazi_eltezami, mazi_mostamar,
             mozare_ekhbari_mianji, mozare_eltezami_mianji, mozare_mostamar_mianji, mozare_ekhbari, mozare_eltezami,
             mozare_mostamar, ayande]
all_regex = [remove_whitespaces(x) for x in all_regex]

types = ['mazi_sade', 'mazi_naghli', 'mazi_estemrari', 'mazi_baeed', 'mazi_eltezami',
         'mazi_mostamar', 'mozare_ekhbari_mianji', 'mozare_eltezami_mianji', 'mozare_mostamar_mianji', 'mozare_ekhbari',
         'mozare_eltezami', 'mozare_mostamar', 'ayande']


# verb = [['دارم'], ['جبران' ,'می کنم']]


def find_main_verb(verb_parts):
    verb = None
    prefix_words = None
    if len(verb_parts) == 1:
        verb = verb_parts[0]
    elif len(verb_parts) > 1:
        verb = verb_parts[-1]
        prefix_words = " ".join(verb_parts[:-1])
    return verb, prefix_words


def find_verb_details(verbs, subject):
    our_verb = None
    if len(verbs) == 1:
        our_verb, prefix_words = find_main_verb(verbs[-1])
    elif len(verbs) > 1:
        first_verb, _ = find_main_verb(verbs[-2])
        second_verb, prefix_words = find_main_verb(verbs[-1])
        our_verb = first_verb + second_verb

    verb = remove_whitespaces(our_verb)
    results = []
    for regex in all_regex:
        if match := re.match(regex, verb):
            found_type = types[all_regex.index(regex)]
            if found_type.startswith('mazi'):
                if found_type.endswith('naghli'):
                    found_shenase_mazi = match.group('shenase_naghli')
                    shenase = find_shenase_from_naghli(found_shenase_mazi)
                else:
                    if match.group('shenase_mazi') != None:
                        found_shenase_mazi = match.group('shenase_mazi')
                    else:
                        found_shenase_mazi = ''
                    shenase = find_shenase_from_mazi(found_shenase_mazi)
                bon_mazi = match.group('bon_mazi')
                try:
                    pishvand = match.group('pishvand')
                except:
                    pishvand = None
                results.append(
                    {'root': bon_mazis[bon_mazi], 'structure': None, 'person': shakhs_name[shenase],
                     'tense': found_type,
                     'prefix': pishvand})
            if found_type.startswith('mozare'):
                if found_type.endswith('mianji'):
                    bon_mozare = mianjis_mozare[match.group('bon_mozare')]
                else:
                    bon_mozare = match.group('bon_mozare')
                found_shenase_mozare = match.group('shenase_mozare')
                shenase = find_shenase_from_mozare(found_shenase_mozare)
                try:
                    pishvand = match.group('pishvand')
                except:
                    pishvand = None
                results.append(
                    {'root': bon_mozares[bon_mozare], 'structure': None, 'person': shakhs_name[shenase],
                     'prefix': pishvand,
                     'tense': found_type})
            if found_type.startswith('ayande'):
                found_shenase_mozare = match.group('shenase_mozare')
                shenase = find_shenase_from_mozare(found_shenase_mozare)
                bon_mazi = match.group('bon_mazi')
                try:
                    pishvand = match.group('pishvand')
                except:
                    pishvand = None
                results.append(
                    {'root': bon_mazis[bon_mazi], 'structure': None, 'person': shakhs_name[shenase],
                     'tense': found_type,
                     'prefix': pishvand})

    for res in results:
        if res['prefix'] is not None:
            res['structure'] = 'prefixed'
        elif prefix_words is not None:
            res['root'] = prefix_words + ' ' + res['root']
            res['structure'] = 'compound'
        else:
            res['structure'] = 'simple'

    if len(results) == 0:
        return None

    if subject is None:
        for res in results:
            if not res['tense'].endswith('mianji'):
                return res
        return results[0]
    else:
        for res in results:
            if res['person'] == subject:
                return res

        res = results[0]
        res['person'] = subject
        return res
    return results[0]