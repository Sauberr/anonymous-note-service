from fastapi_babel import Babel, BabelConfigs

from app.core.templates import templates

babel_configs = BabelConfigs(
    ROOT_DIR=__file__,
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="locales",
)

babel = Babel(babel_configs)
babel.install_jinja(templates)
