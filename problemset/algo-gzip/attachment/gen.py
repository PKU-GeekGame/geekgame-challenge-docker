from pathlib import Path

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

def gen(user, ch) -> Path:
    template = Path('server_template.py').read_text()
    
    var_xor = 3 + user.get_partition(ch, 29)
    var_seed = SEEDS[user.get_partition(ch, len(SEEDS))]
    
    template = template.replace('__VARIANT_XOR__', str(var_xor))
    template = template.replace('__VARIANT_SEED__', repr(var_seed))
    
    dst_path = Path('_gen').resolve() / str(user._store.id)
    dst_path.mkdir(exist_ok=True, parents=True)
    
    out_path = dst_path / 'server.py'
    with out_path.open('w') as f:
        f.write(template)
    return out_path