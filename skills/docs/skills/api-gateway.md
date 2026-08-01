# API Gateway Skill Candidates

## Возможности

- Классификация пользовательского запроса и выбор skill.
- Нормализация SSE-ответа в финальное frontend message event.
- Диагностика upstream connectivity и routing errors.

## Ограничения

- Gateway skill не должен заменять бизнес-логику downstream сервисов.
- Любой новый routing path должен иметь явный fallback и spec.
