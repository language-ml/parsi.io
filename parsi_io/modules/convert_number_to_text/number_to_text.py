# coding: utf-8
"This module converts numbers into Persian text."

def number_grouper(number: int):
    "split number into groups of 3 digits"

    number_str, groups = str(number), list()

    while number_str:
        groups.append(number_str[-3:])
        number_str = number_str[:-3]
    
    groups.reverse()
    return groups


class number_str(str) :
    "number_str is a new type: mixed number and string"

    def __init__(self, number: str):
        
        if type(number).__name__ != 'str' :
            number = str(number)
        
        if not self.number_validation(number) :
            raise TypeError("Argument type isn't number_str!")

        self.is_negative = '-' in number
        
        group = number.split('.')
        
        self.integers, self.decimals = (group[0], '0') if len(group) == 1 else group
    
    def number_validation(self, number: str) -> bool:
        
        if len(number) == 0 :
            return False

        valid_chars = list('-0.123456789')

        for char in list(number) :
            if char not in valid_chars :
                return False
        
        if '-' in number :
            if number.index('-') != 0 :
                return False

        return False if (len(number.split('.')) - 1) > 1 else True


class ConvertNumberToText():
    "Converts numbers to Persian text."

    def __init__(self):
        
        # define arrays for number to text converter

        self.ones = {
            0  : 'صفر',
            1  : 'یک',
            2  : 'دو',
            3  : 'سه',
            4  : 'چهار',
            5  : 'پنج',
            6  : 'شش',
            7  : 'هفت',
            8  : 'هشت',
            9  : 'نه',
            10 : 'ده',
            11 : 'یازده',
            12 : 'دوازده',
            13 : 'سیزده',
            14 : 'چهارده',
            15 : 'پانزده',
            16 : 'شانزده',
            17 : 'هفده',
            18 : 'هجده',
            19 : 'نوزده'
        }
        
        self.tens = {
            0 : '',
            1 : 'ده',
            2 : 'بیست',
            3 : 'سی',
            4 : 'چهل',
            5 : 'پنجاه',
            6 : 'شصت',
            7 : 'هفتاد',
            8 : 'هشتاد',
            9 : 'نود'
        }
        
        self.hundreds = {
            0 : '',
            1 : 'صد',
            2 : 'دویست',
            3 : 'سیصد',
            4 : 'چهارصد',
            5 : 'پانصد',
            6 : 'ششصد',
            7 : 'هفتصد',
            8 : 'هشتصد',
            9 : 'نهصد'
        }

        self.thousands = {
            0  : '',
            1  : 'هزار',
            2  : 'میلیون',
            3  : 'میلیارد',
            4  : 'تریلیون',
            5  : 'کوادریلیون',
            6  : 'کوینتیلیون',
            7  : 'سکستیلیون',
            8  : 'سپتیلیون',
            9  : 'اکتیلیون',
            10 : 'نونیلیون',
            11 : 'دسیلیون'
        }
    
    def run(self, number: str) -> str:

        number = number_str(number)
        is_negative = number.is_negative
        integers = int(number.integers)
        decimals = number.decimals

        # check the decimal isn't too long.
        if len(decimals) > 12 :
            decimals = decimals[:12]
        
        decimals = decimals.rstrip('0')
        if decimals == '':
            decimals = '0'

        # absolute value: |number|
        if is_negative :
            integers *= -1
        
        if integers >= (10 ** 36) :
            raise OverflowError("Number too large.")

        if (integers + int(decimals)) == 0 :
            return self.ones[0]

        # split number into groups of 3 digits
        integer_groups = number_grouper(integers)
        integer_groups_len = igl = len(integer_groups)

        # convert each group of 3 digits to text

        text = ''

        if is_negative :
            text += 'منفی '
        
        for i, group in enumerate(integer_groups) :

            group = int(group)

            group_text = ''

            integer_groups_len -= 1

            jump = group == 0

            if group >= 100 :
                hundreds_digit = int(group // 100)
                group_text += self.hundreds[hundreds_digit]
                group = group % 100
                if group != 0 :
                    group_text += ' و '

            if group >= 20 or group == 10 :
                tens_digit = int(group // 10)
                group_text += self.tens[tens_digit]
                group = group % 10
                if group != 0 :
                    group_text += ' و '

            if group >= 1 and group <= 19 :
                group_text += self.ones[group]
                
            text += group_text
            
            if not jump :
                text += ' ' + self.thousands[integer_groups_len]
                if integer_groups_len != 0 :
                    _group = integer_groups[i:]
                    while '000' in _group : _group.remove('000')
                    if len(_group) != 1 :
                        text += ' و '
        
        if int(decimals) != 0 :

            text += ' ' if integers == 0 else ' و '

            # split number into groups of 3 digits
            decimals_groups = number_grouper(decimals)
            decimals_groups_len = dgl = len(decimals_groups)

            for group in decimals_groups :

                group = int(group)

                group_text = ''

                decimals_groups_len -= 1

                jump = group == 0

                if group >= 100 :
                    hundreds_digit = int(group // 100)
                    group_text += self.hundreds[hundreds_digit]
                    group = group % 100
                    if group != 0 :
                        group_text += ' و '

                if group >= 20 or group == 10 :
                    tens_digit = int(group // 10)
                    group_text += self.tens[tens_digit]
                    group = group % 10
                    if group != 0 :
                        group_text += ' و '

                if group >= 1 and group <= 19 :
                    group_text += self.ones[group]
                    
                text += group_text

                if not jump :
                    text += ' ' + self.thousands[decimals_groups_len]
                    if decimals_groups_len != 0 :
                        text += ' و '
            
            zwnj = '‌'  # ZERO WIDTH NON-JOINER - Codepoint: U+200C

            if dgl == 1 :
                zwnj = ''

            if len(str(decimals_groups[0])) == 1 :
                text += self.tens[1] + zwnj

            if len(str(decimals_groups[0])) == 2 :
                text += self.hundreds[1] + zwnj

            if len(str(decimals_groups[0])) == 3 :
                dgl += 1
            
            text += self.thousands[dgl - 1] + 'م'


        # Clean up text by removing any extra spaces
        return text.replace('  ', ' ').strip(' ')


if __name__ == '__main__' :
    model = ConvertNumberToText()
    text = input()
    result = model.run(text)
    print(result)
