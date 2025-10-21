from importlib.metadata import version, PackageNotFoundError
from packaging.version import parse as parse_version

MIN_PSYCOPG2_VERSION = parse_version('2.5')

for package in ['psycopg2', 'psycopg2-binary']:
    try:
        if parse_version(version(package)) < MIN_PSYCOPG2_VERSION:
            raise ImportError('Minimum required version for psycopg2 is 2.5')
        break
    except PackageNotFoundError:
        pass

__version__ = version('deepnote-sqlalchemy-redshift')

from sqlalchemy.dialects import registry  # noqa

registry.register(
    "redshift", "sqlalchemy_redshift.dialect",
    "RedshiftDialect_psycopg2"
)
registry.register(
    "redshift.psycopg2", "sqlalchemy_redshift.dialect",
    "RedshiftDialect_psycopg2"
)

registry.register(
    "redshift+redshift_connector", "sqlalchemy_redshift.dialect",
    "RedshiftDialect_redshift_connector"
)
