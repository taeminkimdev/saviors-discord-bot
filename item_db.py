import random

db = {
    '나이트브링어샤프슈터': 'nightbringersharpshooter.png',
    '샤프슈터': 'nightbringersharpshooter.png',
    '샾슈': 'nightbringersharpshooter.png',

    '아다만티움': 'adamantium.png',
    '아다': 'adamantium.png',

    '글라스기브넨의심장': 'heartofglasghaibhleann.png',
    '글기심장': 'heartofglasghaibhleann.png',
    '심장': 'heartofglasghaibhleann.png',

    '손상된글라스기브넨의깃털': 'damagedfeatherofglasghaibhleann.png',
    '깃털': 'damagedfeatherofglasghaibhleann.png',
    '글깃': 'damagedfeatherofglasghaibhleann.png',
    '글기깃털': 'damagedfeatherofglasghaibhleann.png',

    '불완전한공상의왕관헤일로': 'unfinisheddesirescrownhalo.png',
    '헤일로': 'unfinisheddesirescrownhalo.png',

    '미니어처': 'miniature.png',
    '인챈트': 'enchant.png',
    '강화권': 'setltemenhance.png',

    '잘려나간겨울의꿈결정': 'shardofseveredwinterdream.png',
    '꿈결': 'shardofseveredwinterdream.png',
    '잘결': 'shardofseveredwinterdream.png',

    '결정화된겨울의잔해': 'crystalizeddebirsofwinter.png',
    '잔해': 'crystalizeddebirsofwinter.png',

    '붕괴된마력의정수': 'brokenmagicalessence.png',
    '붕마정': 'brokenmagicalessence.png',

    '여명의검': 'swordofdawn.png',
    '여명검': 'swordofdawn.png',
    '여명': 'swordofdawn.png',

    '플루아의눈물': 'fflurstears.png',
    '눈물': 'fflurstears.png',
    '플루아즙': 'fflurstears.png',
    '즙': 'fflurstears.png',

    '심술난고양이의구슬': 'orbofgrumpykitty.png',
    '심고구': 'orbofgrumpykitty.png',
    '땅콩': 'orbofgrumpykitty.png',
    '구슬': 'orbofgrumpykitty.png'
}
default_img = 'default.png'


def get_url(name: str):
    name = name.replace(' ', '')
    if '인챈트' in name:
        return db['인챈트']

    if '강화권' in name:
        return db['강화권']

    if '미니어처' in name:
        return db['미니어처']

    try:
        img = db[name]
    except KeyError:
        return default_img

    # 심영 이스터에그
    if img == 'orbofgrumpykitty.png':
        if random.randint(1, 10) == 10:
            img = 'goza.png'

    return img
