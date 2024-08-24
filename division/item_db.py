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

emoji_db = {
    'unfinisheddesirescrownhalo': {
        'id': 1276172128084824104,
        'name': 'unfinisheddesirescrownhalo'
    },
    'swordofdawn': {
        'id': 1276172114302468186,
        'name': 'swordofdawn'
    },
    'shardofseveredwinterdream': {
        'id': 1276172101597790289,
        'name': 'shardofseveredwinterdream'
    },
    'setltemenhance': {
        'id': 1276172086179659846,
        'name': 'setltemenhance'
    },
    'orbofgrumpykitty': {
        'id': 1276172072082739200,
        'name': 'orbofgrumpykitty'
    },
    'nightbringersharpshooter': {
        'id': 1276172052356665394,
        'name': 'nightbringersharpshooter'
    },
    'miniature': {
        'id': 1276172035470528646,
        'name': 'miniature'
    },
    'heartofglasghaibhleann': {
        'id': 1276172018450174044,
        'name': 'heartofglasghaibhleann'
    },
    'fflurstears': {
        'id': 1276172000984956948,
        'name': 'fflurstears'
    },
    'enchant': {
        'id': 1276171984040103937,
        'name': 'enchant'
    },
    'damagedfeatherofglasghaibhleann': {
        'id': 1276171958995652629,
        'name': 'damagedfeatherofglasghaibhleann'
    },
    'crystalizeddebirsofwinter': {
        'id': 1276171943820918815,
        'name': 'crystalizeddebirsofwinter'
    },
    'brokenmagicalessence': {
        'id': 1276171927257354334,
        'name': 'brokenmagicalessence'
    },
    'adamantium': {
        'id': 1276171907678605444,
        'name': 'adamantium'
    }
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

    return img


def get_emoji(item_name):
    eng_name = get_url(item_name).removesuffix('.png')
    try:
        emoji = emoji_db[eng_name]
    except KeyError:
        return '<:null:1276173189248192603>'

    return f'<:{emoji["name"]}:{emoji["id"]}>'
