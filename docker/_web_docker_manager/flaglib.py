import hashlib
import string

def partitioned(flags, challenge_key, token):
    uid = token.partition(':')[0]
    h = hashlib.sha256(f'{uid}-{challenge_key}'.encode()).hexdigest()
    partition = int(h, 16) % len(flags)
    return flags[partition]

def leet(flag, salt, token):
    uid = token.partition(':')[0]
    assert flag.startswith('flag{') and flag.endswith('}'), 'wrong flag format'
    
    uid = int(hashlib.sha256(f'{uid}-{salt}'.encode()).hexdigest(), 16)
    rcont = flag[len('flag{'):-len('}')]
    rdlis = []

    for i in range(len(rcont)):
        if rcont[i] in string.ascii_letters:
            rdlis.append(i)
    assert len(rdlis) >= 10, 'insufficient flag entropy'

    rdseed = (uid+233)*114547%123457
    for it in range(6):
        if not rdlis:  # no any leetable chars
            return flag

        np = rdseed%len(rdlis)
        npp = rdlis[np]
        rdseed = (rdseed+233)*114547%123457
        del rdlis[np]
        px = rcont[npp]
        rcont = rcont[:npp] + (px.upper() if px in string.ascii_lowercase else px.lower()) + rcont[npp+1:]

    return 'flag{'+rcont+'}'
