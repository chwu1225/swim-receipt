"""
Number to Chinese Conversion Service
Convert numeric amounts to Chinese numeral representation
"""


def amount_to_chinese(amount):
    """
    Convert numeric amount to Chinese numeral string
    Example: 12345 -> '\u58f9\u842c\u8cb3\u4edf\u53c3\u4f70\u8086\u62fe\u4f0d\u5143\u6574'
    """
    if amount is None:
        return ''

    # Handle decimal
    amount = float(amount)
    if amount < 0:
        return '\u8ca0' + amount_to_chinese(-amount)

    # Chinese numerals
    digits = ['\u96f6', '\u58f9', '\u8cb3', '\u53c3', '\u8086', '\u4f0d', '\u9678', '\u67d2', '\u634c', '\u7396']
    units = ['', '\u62fe', '\u4f70', '\u4edf']
    big_units = ['', '\u842c', '\u5104', '\u5146']

    # Split integer and decimal parts
    int_part = int(amount)
    dec_part = round((amount - int_part) * 100)  # Get cents

    if int_part == 0:
        result = '\u96f6'
    else:
        result = ''
        str_int = str(int_part)
        length = len(str_int)

        # Process each digit group (4 digits each)
        group_count = (length + 3) // 4
        str_int = str_int.zfill(group_count * 4)

        for g in range(group_count):
            group = str_int[g * 4:(g + 1) * 4]
            group_result = ''
            zero_flag = False

            for i, digit in enumerate(group):
                d = int(digit)
                if d == 0:
                    zero_flag = True
                else:
                    if zero_flag and group_result:
                        group_result += '\u96f6'
                    group_result += digits[d] + units[3 - i]
                    zero_flag = False

            if group_result:
                result += group_result + big_units[group_count - 1 - g]

        # Clean up result
        result = result.replace('\u62fe\u96f6', '\u62fe')

    # Add currency unit
    result += '\u5143'

    # Handle decimal part (cents)
    if dec_part == 0:
        result += '\u6574'
    else:
        jiao = dec_part // 10  # Dimes
        fen = dec_part % 10    # Cents

        if jiao > 0:
            result += digits[jiao] + '\u89d2'
        elif fen > 0:
            result += '\u96f6'

        if fen > 0:
            result += digits[fen] + '\u5206'

    return result


def format_amount(amount):
    """Format amount with comma separators"""
    if amount is None:
        return '0'
    return '{:,.0f}'.format(float(amount))


# Test
if __name__ == '__main__':
    test_amounts = [0, 1, 10, 100, 1000, 10000, 12345, 50, 800, 29028, 50000]
    for amt in test_amounts:
        print(f'{amt:>10} -> {amount_to_chinese(amt)}')
