import hashlib
import os

token = os.environ['hackergame_token']
ch_key = 'algo-gzip'

def get_partition(challenge_key, n_part):
    uid = token.partition(':')[0]
    h = hashlib.sha256(f'{uid}-{challenge_key}'.encode()).hexdigest()
    partition = int(h, 16) % n_part
    return partition

SEEDS = [
    1, 111, 1111, 11111,
    10, 100, 1000,
    123, 1234, 12345, 123456, 12345678,
    1337, 114, 514, 1919, 114514, 10086,
    666, 6666, 66666, 888, 8888, 88888,
    '1', '111', '1111', '11111',
    '10', '100', '1000',
    '123', '1234', '12345', '123456', '12345678',
    '1337', '114', '514', '1919', '114514', '10086',
    '666', '6666', '66666', '888', '8888', '88888',
    'x', 'xx', 'xxx', 'X', 'XX', 'XXX',
    'seed', 'Seed', 'SEED'
    'geekgame', 'GeekGame', 'GEEKGAME',
    'yuanshen', 'yuan_shen', 'YuanShen', 'YUAN_SHEN',
    'genshin', 'Genshin', 'Genshin Impact', 'Genshin_Impact',
    'mihoyo', 'MiHoYo', 'MIHOYO',
    'kobe', 'Kobe', 'laoda', 'mamba', 'mamba out', 'mamba_out', 'mamba out!',
]

var_xor = 3 + get_partition(ch_key, 29)
var_seed = SEEDS[get_partition(ch_key, len(SEEDS))]
