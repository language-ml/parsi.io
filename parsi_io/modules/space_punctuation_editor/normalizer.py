from regexer import Regexer

class Normalizer:
    def __init__(self) -> None:
        self.regexer = Regexer()


    """
    This method used to:
        *   Remove Extra spaces 
        *   Remove extra newlines
        *   Remove Extra ZWNJs
        *   Remove keshide, carriage
        *   Translate Latin numbers to Persian numbers
        *   Replace quotation with gyoome
        *   Relace dot with momayez
        *   Replace 3 dots
        *   Remove FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SHADDA, SUKUN
    @param text a pure text to refine
    @return refined text as string
    """
    def characterRefine(self, text):

        character_refinement_patterns = [
            (r' {2,}', ' '),  # remove extra spaces
        	(r'\n{3,}', '\n\n'),  # remove extra newlines
            (r'\u200c{2,}', '\u200c'),  # remove extra ZWNJs
        	(r'[ـ\r]', ''),  # remove keshide, carriage returns
            ('"([^\n"]+)"', r'«\1»'),  # replace quotation with gyoome
        	('([\d+])\.([\d+])', r'\1٫\2'),  # replace dot with momayez
        	(r' ?\.\.\.', ' …'),  # replace 3 dots
           	# remove FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SHADDA, SUKUN
           	('[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652]', ''),
        ]
        
        character_refinement_patterns = self.regexer.compilePatterns(character_refinement_patterns)

        translation_src, translation_dst = ' ىكي“”', ' یکی""'
        translation_src += '0123456789%,'
        translation_dst += '۰۱۲۳۴۵۶۷۸۹٪،'
        translations = self.makeTrans(translation_src, translation_dst)
        text = text.translate(translations)

        for pattern, repl in character_refinement_patterns:
            text = pattern.sub(repl, text)

        return text

    """
    This method used to:
        *   Remove space before and after quotation
        *   Remove space before and after symbols
        *   Put space after . and :
    @param text a pure text to refine
    @return refined text as string
    """
    def punctuationRefine(self, text):

        punc_after, punc_before = r'\.:!،؛؟»\]\)\}', r'«\[\(\{'
        punctuation_spacing_patterns = self.regexer.compilePatterns([
            # remove space before and after quotation
            ('" ([^\n"]+) "', r'"\1"'),
            (' ([' + punc_after + '])', r'\1'),  # remove space before
            ('([' + punc_before + ']) ', r'\1'),  # remove space after
            # put space after . and :
            ('([' + punc_after[:3] + '])([^ ' + \
             punc_after + '\d۰۱۲۳۴۵۶۷۸۹])', r'\1 \2'),
            ('([' + punc_after[3:] + '])([^ ' + punc_after + '])',
             r'\1 \2'),  # put space after
            ('([^ ' + punc_before + '])([' + punc_before + '])',
             r'\1 \2'),  # put space before
            ('(?<=.)\s+(?=[\(\{\[])', ''), # remove space before open symbols
            ('(\)|\}|\]) ?', '\\1 ') # put space after close symbols
        ])

        for pattern, repl in punctuation_spacing_patterns:
            text = pattern.sub(repl, text)
        return text
    """
    This method used to map chars to each other(zip). example: 1->۱
    @param A source string
    @param B destination string
    @return a dictionary of mapped words
    """
    def makeTrans(self, A, B): return dict((ord(a), b) for a, b in zip(A, B))
    """
    This method used to manage normalization operation
    @param text unormaized text
    @return normalized text
    """
    
    def normalize(self, text):

        # Refine chars in text(persianify numbers, remove e-erabs, etc.)
        text = self.characterRefine(text)
        # punctuation refinement
        text = self.punctuationRefine(text)
        return text
