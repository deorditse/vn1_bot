from enum import Enum

from app import __version__, release_notes
from common import current_time_msk_str
from app.config import config

"""
===================================================================================================================
Tags
===================================================================================================================
"""


class Tags(str, Enum):
    searchParser = "Поиск через парсинг"


"""
===================================================================================================================
Description
===================================================================================================================
"""

api_version = __version__
api_release_notes = release_notes
start_time = current_time_msk_str("%d %b %Y - %H:%M:%S MSK")

description_template = f"""
### Сервис VN1 
* Версия: **{api_version}**
* Запущен: **{start_time}** 
* На порту: **{str(config.api_port)}**
* Режим работы: **{config.api_mode}**
* CRUD mode: **{'ТОЛЬКО ЧТЕНИЕ' if config.api_is_readonly else 'все операции'}**
* Логирование: **{config.log_path}**
* Последние изменения: {api_release_notes}
"""

description = description_template \
    .replace('\n+', '<br>\n✔️') \
    .replace('\n>', '<br>\n🐌') \
    .replace('\n-', '<br>\n📌') \
    .replace('(!)', '⚠️')

# """
# ===================================================================================================================
# Metadata
# ===================================================================================================================
# """
tags_metadata = [
    {
        "name": Tags.searchParser,
        "description": '''
        Генерация с помощью AI
        ''',
    },

]
