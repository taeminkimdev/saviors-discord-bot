from typing import List


class Member:
    def __init__(self, id, nickname, is_divided):
        self.id = id
        self.nickname = nickname
        self.is_divided = is_divided

    @property
    def json(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'is_divided': self.is_divided
        }


class Division:
    def __init__(self, id, item, created_at, members: List[Member]):
        self.id = id
        self.item = item
        self.created_at = created_at
        self.members = members

    @property
    def json(self):
        return {
            'id': self.id,
            'item': self.item,
            'created_at': self.created_at,
            'members': [member.json for member in self.members]
        }

    @property
    def get_item_with_division_id(self):
        return f'{self.item} #{self.id}'

    def _rearrange(self, user_id):
        for i, member in enumerate(self.members):
            if member.id == user_id:
                member = self.members.pop(i)
                self.members.insert(0, member)
                return

    def get_members_string(self, user_id):
        self._rearrange(user_id)

        complete_string = ':white_check_mark: '
        not_complete_string = ':heavy_check_mark: '

        for i, member in enumerate(self.members):
            if member.is_divided:
                if len(complete_string) != 19:
                    complete_string += ', '
                complete_string += member.nickname
            else:
                if len(not_complete_string) != 19:
                    not_complete_string += ', '
                not_complete_string += member.nickname

        return f'> {not_complete_string}' if len(complete_string) == 19 else f'> {not_complete_string}\n> {complete_string}'

    def get_members(self, user_id):
        self._rearrange(user_id)

        member_string = ''
        for i, member in enumerate(self.members):
            member_string += member.nickname
            if len(self.members) != i + 1:
                member_string += ', '

        if len(member_string) > 40:
            member_string = f'{member_string[:40]}...'

        return member_string
