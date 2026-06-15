from src.SharedKernel.base.Container import Configuration
from src.Infrastructure.Config import Config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
import urllib.parse

def extract_search_path_from_url(url: str) -> tuple[str, dict]:
    """
    Extract search_path from PostgreSQL URL options.
    Returns (clean_url, connect_args) tuple.
    """
    parsed_url = urllib.parse.urlparse(url)
    connect_args = {}

    if parsed_url.query:
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'options' in query_params:
            options_value = query_params['options'][0]
            if options_value.startswith('-csearch_path='):
                search_path = options_value.split('=')[1]
                connect_args['server_settings'] = {'search_path': search_path}

        # Rebuild URL without options
        clean_url = parsed_url._replace(query='').geturl()
        return clean_url, connect_args

    return url, connect_args


config = Config()
config.load_env_yaml()

PG_URL = config.databases.postgresql.url
MYSQL_URL = config.databases.mysql.url

PG_URL, connect_args = extract_search_path_from_url(PG_URL)

engine = create_async_engine(PG_URL, echo=False, connect_args=connect_args, pool_pre_ping=True, pool_recycle=3600)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@Configuration
class DatabaseSessionConfig():
    @property
    def session(self) -> AsyncSession:
        return async_session()


