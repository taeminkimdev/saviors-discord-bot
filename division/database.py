from pymysql import connect
from division.dto import Division, Member
from typing import List
from config import mysql


class Database:
    def __enter__(self):
        self.connection = connect(host=mysql.host,
                                  user=mysql.user,
                                  password=mysql.password,
                                  database=mysql.db)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.connection.close()

    def update_members(self, members):
        sql = """
        INSERT INTO members (id, nickname)
        VALUES(%s, %s) ON DUPLICATE KEY UPDATE
        nickname = VALUES(nickname)
        """

        datas = [(member['id'], member['nickname']) for member in members]
        self.cursor.executemany(sql, datas)
        self.connection.commit()

    def find_external_members(self, members_nickname):
        if len(members_nickname) == 0:
            return []

        sql = '''
            SELECT id
            FROM members 
            WHERE nickname IN (%s)'''

        format_strings = ','.join(['%s'] * len(members_nickname))
        self.cursor.execute(sql % format_strings, members_nickname)

        nickname_datas = self.cursor.fetchall()

        member_ids = [data[0] for data in nickname_datas]

        return member_ids

    def find_divisions_by_ids(self, division_ids: List[int]) -> List[Division]:
        sql = '''
            SELECT id, item, created_at
            FROM divisions 
            WHERE id IN (%s)'''

        format_strings = ','.join(['%s'] * len(division_ids))
        self.cursor.execute(sql % format_strings, division_ids)

        division_datas = self.cursor.fetchall()

        division_ids = [data[0] for data in division_datas]
        if len(division_ids) == 0:
            return []

        sql = '''
        SELECT division_id, member_id, m.nickname, is_divided
        FROM division_members dm
        INNER JOIN members m ON m.id = dm.member_id
        WHERE division_id IN (%s)'''

        format_strings = ','.join(['%s'] * len(division_ids))
        self.cursor.execute(sql % format_strings, tuple(division_ids))
        member_datas = self.cursor.fetchall()
        division_member = {}
        for data in member_datas:
            member = Member(id=data[1], nickname=data[2], is_divided=data[3])
            try:
                division_member[data[0]].append(member)
            except KeyError:
                division_member[data[0]] = [member]
        divisions = [Division(id=data[0],
                              item=data[1],
                              created_at=data[2],
                              members=division_member[data[0]])
                     for data in division_datas]

        return divisions

    def find_members_by_division_ids(self, division_ids: List[int]) -> List:
        sql = '''
            SELECT DISTINCT member_id, nickname
            FROM division_members dm
            INNER JOIN members m ON m.id = dm.member_id
            WHERE division_id IN ({division_ids}) AND is_divided = false'''

        sql = sql.format(division_ids=','.join(['%s'] * len(division_ids)))

        self.cursor.execute(sql, division_ids)
        member_datas = self.cursor.fetchall()
        members = [(data[0], data[1]) for data in member_datas]

        return members

    def update_partition_complete(self, division_ids, members):
        sql = '''
        UPDATE division_members 
        SET is_divided = true
        WHERE division_id IN ({division_ids}) AND member_id IN ({members})'''

        sql = sql.format(division_ids=','.join(['%s'] * len(division_ids)), members=','.join(['%s'] * len(members)))
        self.cursor.execute(sql, division_ids + members)

        sql = '''
        SELECT DISTINCT division_id
        FROM division_members
        WHERE is_divided = false AND division_id IN ({division_ids})'''
        sql = sql.format(division_ids=','.join(['%s'] * len(division_ids)))

        self.cursor.execute(sql, division_ids)
        datas = self.cursor.fetchall()

        divided = division_ids.copy()

        for division_id in datas:
            division_id = division_id[0]
            if division_id in division_ids:
                divided.remove(division_id)

        if len(divided) > 0:
            sql = 'UPDATE divisions SET status = "COMPLETED" WHERE id IN ({divided})'
            sql = sql.format(divided=','.join(['%s'] * len(divided)))
            self.cursor.execute(sql, divided)

        self.connection.commit()

        return divided

    def find_divisions_by_member_ids(self, member_ids: List[int]) -> List[Division]:
        if len(member_ids) == 0:
            sql = '''
            SELECT id, item, created_at
            FROM divisions 
            WHERE status = "CREATED"'''
            self.cursor.execute(sql)
        else:
            sql = '''
                SELECT id, item, created_at
                FROM divisions 
                WHERE status = "CREATED" 
                AND id in (SELECT division_id FROM division_members WHERE member_id = %s)'''
            self.cursor.execute(sql, member_ids[0])
        division_datas = self.cursor.fetchall()

        division_ids = [data[0] for data in division_datas]
        if len(division_ids) == 0:
            return []

        sql = '''
        SELECT division_id, member_id, m.nickname, is_divided
        FROM division_members dm
        INNER JOIN members m ON m.id = dm.member_id
        WHERE division_id IN (%s)'''

        format_strings = ','.join(['%s'] * len(division_ids))
        self.cursor.execute(sql % format_strings, tuple(division_ids))
        member_datas = self.cursor.fetchall()
        division_member = {}
        for data in member_datas:
            member = Member(id=data[1], nickname=data[2], is_divided=data[3])
            try:
                division_member[data[0]].append(member)
            except KeyError:
                division_member[data[0]] = [member]
        divisions = [Division(id=data[0],
                              item=data[1],
                              created_at=data[2],
                              members=division_member[data[0]])
                     for data in division_datas]

        result = []
        for division in divisions:
            if self._is_contain_all(member_ids, division.members):
                result.append(division)

        return result

    def _is_contain_all(self, member_ids: List[int], members: List[Member]):
        division_member_ids = [member.id for member in members]
        for member_id in member_ids:
            if member_id not in division_member_ids:
                return False

        return True

    def insert_division(self, id, item, created_at, status, members):
        sql = '''
        INSERT INTO divisions (id, item, created_at, status) 
        VALUES(%s, %s, %s, %s)'''

        data = (id, item, created_at, status)

        self.cursor.execute(sql, data)

        sql = '''
        INSERT INTO division_members (division_id, member_id, is_divided) 
        VALUES(%s, %s, %s)'''

        datas = [(id, member, False) for member in members]
        self.cursor.executemany(sql, datas)
        self.connection.commit()

    def delete_division(self, division_ids):
        sql = '''
        UPDATE divisions 
        SET status = "DELETED" 
        WHERE id IN (%s)'''

        format_strings = ','.join(['%s'] * len(division_ids))
        self.cursor.execute(sql % format_strings, tuple(division_ids))

        self.connection.commit()

    def complete_division(self, division_ids):
        sql = '''
        UPDATE divisions 
        SET status = "COMPLETED"
        WHERE id IN (%s)'''

        format_strings = ','.join(['%s'] * len(division_ids))
        self.cursor.execute(sql % format_strings, tuple(division_ids))

        self.connection.commit()
