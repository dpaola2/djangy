# Configuration options set by command-line arguments to install.py
ACTION                  = None  # 'install' or 'upgrade'
MASTER_NODE             = False
WORKER_NODE             = False
PROXYCACHE_NODE         = False
MASTER_MANAGER_HOST     = None
DEFAULT_PROXYCACHE_HOST = None
DEFAULT_DATABASE_HOST   = None
WORKERHOSTS             = []
PRODUCTION              = False
TO_SOUTH                = False

RABBITMQ_THIS_HOST      = None
RABBITMQ_LEADER_HOST    = None

# Configuration options set in config.py
DB_ROOT_PASSWORD = 'password goes here'
MASTER_DATABASES = [
    # (username, password, dbname)
    ('djangy',  'password goes here', 'djangy'),
    ('web_ui',  'password goes here', 'web_ui'),
    ('web_api', 'password goes here', 'web_api')
]

# S3 access stuff
S3_ACCESS_KEY   = 'password goes here'
S3_SECRET       = 'password goes here'
S3_BUCKET       = 'djangy_backups'

# Billing stuff
DEVPAYMENTS_TESTING     = 'password goes here'
DEVPAYMENTS_PRODUCTION  = 'password goes here'
DEVPAYMENTS_API_KEY     = DEVPAYMENTS_TESTING
