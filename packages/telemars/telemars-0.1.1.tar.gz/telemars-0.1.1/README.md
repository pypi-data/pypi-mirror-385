# telemars

**telemars** — это высокоуровневая, асинхронная библиотека-надстройка для работы с API Mediascope, построенная на базе `mediascope-api-lib`.

Инструмент создан для решения ключевых проблем оригинальной библиотеки: отсутствия валидации данных, медленной работы
и сложности в поддержке кода.

## Установка

```bash
pip install telemars
```

## Конфигурация

Для работы библиотеки необходимо создать файл `settings.json` в корне проекта со следующей структурой:

```json
{
    "username": "YOUR_USERNAME",
    "passw": "YOUR_PASSWORD",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "auth_server": "https://auth.mediascope.net/auth/realms/mediascope/protocol/openid-connect/token",
    "root_url": "https://api.mediascope.net/tvindex/api/v1"
}
```

Данное требование обусловлено особенностями оригинальной библиотеки `mediascope-api-lib`.

**Внимание:** Не забудьте добавить `settings.json` в `.gitignore`, чтобы не допустить утечки конфиденциальных данных.

## Контрибьюция

Предложения по улучшению и доработке проекта приветствуются. Если вы обнаружили проблему или у вас есть идеи по
развитию функционала, пожалуйста, создайте соответствующий Issue.

## Контакты

Email: [prosvirnin.a@outlook.com](mailto:prosvirnin.a@outlook.com)  
Telegram: [@prosvirninjr](https://t.me/prosvirninjr)
