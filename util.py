from datetime import datetime
from config import setting


def convert_ggojang(user_id): # 꼬쟝 -> 꼬장 변환
    if user_id == setting.SAVIOR_ID:
        user_id = setting.GGO_JANG_ID

    return user_id


def convert_members(text, user_id):
    members = [convert_ggojang(user_id)]
    is_id_field = False
    user_id = ''
    for c in list(text):
        if c == '@':
            is_id_field = True
            continue

        elif c == '>':
            is_id_field = False
            user_id = convert_ggojang(int(user_id))
            members.append(user_id)
            user_id = ''

        if is_id_field:
            user_id += c
    return list(set(members))


def convert_external_members(text):
    members = [{
        'id': create_id() + i,
        'nickname': nickname
    } for i, nickname in enumerate(text.strip().split())]
    return members


def convert_item(text):
    item = ''
    for c in list(text):
        if c == '>':
            item = ''

        elif c != '<':
            item += c

    return item


def get_division_id(string):
    for i, c in enumerate(string):
        if c == '#':
            return int(string[i + 1:])


def create_id():
    return int(datetime.now().timestamp() * 1000)
