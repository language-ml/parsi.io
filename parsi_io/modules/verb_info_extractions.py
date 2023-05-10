from hazm import *
import tqdm
import re


class VerbInfoExtraction():
    def __init__(self):
        self.shenase_mazi = {
            'م': 'اول شخص مفرد',
            'ی': 'دوم شخص مفرد',
            '': 'سوم شخص مفرد',
            'ست': 'سوم شخص مفرد',
            'یم': 'اول شخص جمع',
            'ید': 'دوم شخص جمع',
            'ند': 'سوم شخص جمع',
        }
        self.shenase_mozare = {
            'م': 'اول شخص مفرد',
            'ی': 'دوم شخص مفرد',
            'د': 'سوم شخص مفرد',
            'یم': 'اول شخص جمع',
            'ید': 'دوم شخص جمع',
            'ند': 'سوم شخص جمع',
        }
        self.s_mozare1 = r"(د|ند|ید|یم|ی|م)"
        self.mazi_sade_re = r"\bن?({past_stem})({s})\b"
        self.mazi_sade = f"{self.mazi_sade_re}"
        self.mazi_estemrary_re = r"\bن?می.({past_stem})({s})\b"
        self.mazi_estemrary = f"{self.mazi_estemrary_re}"
        self.mazi_mostamar_re = r"\b(داشت{s}).ن?می.({past_stem})({s})\b"
        self.mazi_mostamar = f"{self.mazi_mostamar_re}"
        self.mazi_baeid_re = r"\bن?({past_stem})[ه].*[بود]({s})\b"
        self.mazi_baeid = f"{self.mazi_baeid_re}"
        self.mazi_naghli_re = r"\bن?({past_stem})[ه].*[ا]({s})\b"
        self.mazi_naghli = f"{self.mazi_naghli_re}"
        self.hal_ekhbari_re = r"\bن?می.*({present_stem})({s})\b"
        self.hal_ekhbari = f"{self.hal_ekhbari_re}"
        self.hal_eltazemi_re = r"\b[ب|ن].*({present_stem})({s})\b"
        self.hal_eltazemi = f"{self.hal_eltazemi_re}"
        self.hal_mostamar_re = r"\b(دار{s}).*[می|نمی].*({present_stem})({s})\b"
        self.hal_mostamar = f"{self.hal_mostamar_re}"
        self.aiande_re = r"\b(ن?خواه{s}).*({past_stem})\b"
        self.aiande = f"{self.aiande_re}"

    def get_lemma_set(self, tok):
        lemmatizer = Lemmatizer()
        return lemmatizer.lemmatize(tok)

    def process(self, text):
        normalizer = Normalizer()
        normalized = normalizer.normalize(text)
        tokens = word_tokenize(normalized)
        tokens_lem = [self.get_lemma_set(t) for t in tqdm.tqdm(tokens)]
        return tokens_lem, tokens

    def run(self, text):
        verbs_details = []
        tokens_lem, tokens = self.process(text)
        verbs_lem = []
        for (i, token) in enumerate(tokens_lem):
            if (re.search('.#.', token) != None):
                verbs_lem.append((i, token))
            elif re.match(r'\bن?می.+\b', token):
                temp_token = token.split('می')
                verbs_lem.append((i, self.get_lemma_set(temp_token[-1])))
                tokens[i] = 'می ' + temp_token[-1]

        counted = False
        verbs = []
        for j in range(len(verbs_lem)):
            i, verb_lem = verbs_lem[j]
            if re.match('داشت|دار', verb_lem) != None and (j+1) < len(verbs_lem) and ((verbs_lem[j+1][0]) == i+1):
                current_verb = tokens[i] + " " + tokens[i+1]
                counted = True
                verbs.append((current_verb, verbs_lem[j+1][1]))
            elif not counted:
                current_verb = tokens[i]
                verbs.append((current_verb, verb_lem))
            else:
                counted = False

        for current_verb, x in verbs:
            details = {}
            if re.search('.#.', x) != None:
                past_stem, present_stem = x.split('#')
                if re.search(f'.?{past_stem}.?', current_verb):
                    if re.search('خواه', current_verb):
                        details['زمان'] = 'آینده'
                        details['بن فعل'] = past_stem
                        details['شخص'] = ""
                        details['نوع'] = ""
                        for s in self.shenase_mozare:
                            aiande_format = self.aiande.format(
                                past_stem=details['بن فعل'], s=s)
                            if (re.match(aiande_format, current_verb)):
                                details['نوع'] = "آینده ساده"
                                details['شخص'] = self.shenase_mozare.get(s)
                    else:
                        details['زمان'] = 'گذشته'
                        details['بن فعل'] = past_stem

                        for s in self.shenase_mazi:
                            mazi_estemrary_format = self.mazi_estemrary.format(
                                past_stem=details['بن فعل'], s=s)
                            mazi_mostamar_format = self.mazi_mostamar.format(
                                past_stem=details['بن فعل'], s=s)
                            mazi_sade_format = self.mazi_sade.format(
                                past_stem=details['بن فعل'], s=s)
                            mazi_baeid_format = self.mazi_baeid.format(
                                past_stem=details['بن فعل'], s=s)
                            mazi_naghli_format = self.mazi_naghli.format(
                                past_stem=details['بن فعل'], s=s)
                            if (re.match(mazi_estemrary_format, current_verb)):
                                details['نوع'] = "گذشته استمراری"
                                details['شخص'] = self.shenase_mazi.get(s)
                            elif (re.match(mazi_mostamar_format, current_verb)):
                                details['نوع'] = "گذشته مستمر"
                                details['شخص'] = self.shenase_mazi.get(s)
                            elif (re.match(mazi_sade_format, current_verb)):
                                details['نوع'] = "گذشته ساده"
                                details['شخص'] = self.shenase_mazi.get(s)
                            elif (re.match(mazi_baeid_format, current_verb)):
                                details['نوع'] = "گذشته بعید"
                                details['شخص'] = self.shenase_mazi.get(s)
                            elif (re.match(mazi_naghli_format, current_verb)):
                                details['نوع'] = "گذشته نقلی"
                                details['شخص'] = self.shenase_mazi.get(s)

                        # remaining = current_verb.split(f'{past_stem}')
                elif re.search(f'.?{present_stem}.?', current_verb):
                    details['زمان'] = 'حال'
                    details['بن فعل'] = present_stem
                    details['شخص'] = ""
                    details['نوع'] = ""

                    for s in self.shenase_mozare:
                        hal_ekhbari_format = self.hal_ekhbari.format(
                            present_stem=details['بن فعل'], s=s)
                        hal_eltazemi_format = self.hal_eltazemi.format(
                            present_stem=details['بن فعل'], s=s)
                        hal_mostamar_format = self.hal_mostamar.format(
                            present_stem=details['بن فعل'], s=s)

                        if (re.match(hal_ekhbari_format, current_verb)):
                            details['شخص'] = self.shenase_mozare.get(s)
                            details['نوع'] = "حال اخباری"
                        elif (re.match(hal_eltazemi_format, current_verb)):
                            details['شخص'] = self.shenase_mozare.get(s)
                            details['نوع'] = "حال التزامی"
                        elif (re.match(hal_mostamar_format, current_verb)):
                            details['شخص'] = self.shenase_mozare.get(s)
                            details['نوع'] = "حال مستمر"

                    # remaining = current_verb.split(f'{present_stem}')

                verbs_details.append(details)

        return verbs_details


if __name__ == '__main__':
    model = VerbInfoExtraction()
    text = input()
    result = model.run(text)
    print(result)
