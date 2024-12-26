REGEXUSERNAME = r'^[\w.@+-]+$'
MAX_LEN_USERNAME_PASSWORD = 150
MAX_LEN_EMAIL = 254
WRONGUSERNAME = 'me'
MAX_LEN_CHARFIELD = 256
MAX_LEN_SLUGFIELD = 64
MAX_LEN_MINI = 16
MIN_SCORE = 1
NO_PUT_METHODS = ('get', 'post', 'patch', 'delete')
UNIT_MEASUREMENT = (
    ('г', 'Грамм'),
    ('кг', 'Килограмм'),
    ('мл', 'Миллилитр'),
    ('л', 'Литр'),
    ('ст. л.', 'Столовая ложка'),
    ('ч. л.', 'Чайная ложка'),
    ('шт.', 'Штук'),
    ('капля', 'Капля'),
    ('кусок', 'Кусок'),
    ('банка', 'Банка'),
    ('щепотка', 'щепотка'),
    ('стакан', 'стакан'),
    ('веточка', 'веточка'),
    ('кусок', 'кусок'),
    ('батон', 'батон'),
)
USER = 'user'
ADMIN = 'admin'
ROLE_USER = [
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор')
]
PAGINATOR_PAGE_SIZE = 6
MAX_PAGE_SIZE = 10
