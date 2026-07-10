Документация по работе сервиса генерации инструкций. LLM + AI

Архитектура

Подключение через АПИ телеграм
 

Основная нода выполнения кода

 

Сервис подключен через АПИ telegram через прокси-сервер https://ai-bot.vn1.ru/
- n8n развернут на сервере  HostName 158.160.74.41 по адресу https://ai-bot.vn1.ru/vn1/
- vpn развернут на сервере в Нидерландах через https://ztv.su/login
админ-панель http://185.159.130.151:49152/6pFGXBCy48FIzCGpsM
- репозиторий проекта https://github.com/deorditse/vn1_bot

На сервере крутится полноценный FastApi проект в контейнере на архитектуре DDD, эндпоинт преобразования docx -> html (http://backend-vn1:8010/converter/docx)
Принцип работы: docx -> преобразование в markdown через Pandoc python -> LangGrapth для генерации html разметки из markdown по графу:
 
Валидация html разметки нодой validate_content_html

Дебагинг через утилиту mitmproxy + langSmith
