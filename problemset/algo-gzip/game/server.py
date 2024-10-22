import random
import gzip
from pathlib import Path

from variant import var_xor, var_seed
import logger

FLAG1 = Path('/flag1').read_text().strip()
FLAG2 = Path('/flag2').read_text().strip()

def average_bit_count(s):
    return sum(c.bit_count() for c in s) / len(s)

def main():
    text = input('Input text: ')
    assert len(text)<=1000
    assert all(0x20<=ord(c)<=0x7e for c in text)
    
    logger.write(None, ['input', text, var_xor, var_seed])
        
    text = [ord(c) ^ var_xor for c in text]
    random.seed(var_seed)
    random.shuffle(text)
    
    text = gzip.compress(bytes(text))
    print('\nAfter processing:\n')
    print(text)
    
    prefix = (text + b'\xFF'*256)[:256]
    bc = average_bit_count(prefix)
    if bc < 2.5:
        logger.write(None, ['getflag1', bc])
        print('\nGood! Flag 1: ', FLAG1)
    
    if b'[What can I say? Mamba out! --KobeBryant]' in text:
        logger.write(None, ['getflag2'])
        print('\nGood! Flag 2: ', FLAG2)
        
try:
    main()
except Exception as e:
    print('Error:', type(e))
    
    import traceback
    def get_traceback(e):
        lines = traceback.format_exception(type(e), e, e.__traceback__)
        return ''.join(lines)
    
    tb = get_traceback(e)
    logger.write(None, ['exception', str(type(e)), str(e), tb])