"""
게시물 입력값을 표준화하기 위한 선택지 모음.

물건 종류 / 색상 / 장소를 자유 입력이 아닌 정해진 값 중에서 고르게 해야
매칭 알고리즘(#21)이 "같은 종류인지", "같은 건물인지"를 정확하게 비교할 수 있다.
선택지를 바꿀 때는 매칭 점수 규칙도 함께 확인할 것.
"""

from django.db import models


class PostType(models.TextChoices):
    LOST = 'LOST', '분실물'
    FOUND = 'FOUND', '습득물'


class PostStatus(models.TextChoices):
    # 분실물: 찾는 중 / 습득물: 보관 중 -> 둘 다 "아직 해결 안 됨" 상태
    OPEN = 'OPEN', '진행중'
    # 주인에게 돌아간 게시물은 매칭 대상에서 제외 (#23)
    RETURNED = 'RETURNED', '반환완료'


class Category(models.TextChoices):
    WALLET = 'WALLET', '지갑'
    CARD = 'CARD', '카드/신분증'
    PHONE = 'PHONE', '휴대폰'
    EARPHONE = 'EARPHONE', '이어폰'
    LAPTOP = 'LAPTOP', '노트북/태블릿'
    BAG = 'BAG', '가방'
    UMBRELLA = 'UMBRELLA', '우산'
    KEY = 'KEY', '열쇠'
    CLOTHING = 'CLOTHING', '의류'
    ACCESSORY = 'ACCESSORY', '액세서리'
    BOOK = 'BOOK', '책/필기구'
    BOTTLE = 'BOTTLE', '텀블러/물병'
    ETC = 'ETC', '기타'


class Color(models.TextChoices):
    BLACK = 'BLACK', '검정'
    WHITE = 'WHITE', '흰색'
    GRAY = 'GRAY', '회색'
    RED = 'RED', '빨강'
    ORANGE = 'ORANGE', '주황'
    YELLOW = 'YELLOW', '노랑'
    GREEN = 'GREEN', '초록'
    BLUE = 'BLUE', '파랑'
    NAVY = 'NAVY', '남색'
    PURPLE = 'PURPLE', '보라'
    PINK = 'PINK', '분홍'
    BROWN = 'BROWN', '갈색'
    BEIGE = 'BEIGE', '베이지'
    SILVER = 'SILVER', '은색'
    GOLD = 'GOLD', '금색'
    ETC = 'ETC', '기타'


class Location(models.TextChoices):
    # 수정캠퍼스
    SUNGSHIN = 'SUNGSHIN', '성신관'
    SUJEONG = 'SUJEONG', '수정관'
    NANHYANG = 'NANHYANG', '난향관'
    UNJEONG = 'UNJEONG', '운정관'
    MUSIC = 'MUSIC', '음악관'
    FORMATIVE = 'FORMATIVE', '조형관'
    ADMIN = 'ADMIN', '행정관'
    # 그 외
    GREEN_CAMPUS = 'GREEN_CAMPUS', '운정그린캠퍼스'
    OUTDOOR = 'OUTDOOR', '교내 야외'
    ETC = 'ETC', '기타'
