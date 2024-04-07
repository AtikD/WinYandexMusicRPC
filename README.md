# **WinSdk + Yandex Music Discord Rich Presence**
Discord RPC для показа музыки которую вы сейчас слушаете на компьютере. Загрузка треков и их обложка происходит из Яндекс Музыки.

![discord](./img/screen1.png)

Есть похожие RPC которые показывают текущий трек используя Api Яндекс Музыки. Но они не могут показывать что играет из радио(например `Моя Волна`).
Поэтому я создал скрипт который берет из `winsdk.windows.media.control` информацию о текущем треке, делает поиск в яндекс музыке и выводит трек в Discord.

Плюсы по сравнению с другими скриптами:    
Не нужен токен Яндекс Музыки ✅  
Показывает треки из подборок, радио ✅  
Не ограничен использованием Яндекс Музыки, музыку можно слушать хоть из ВКонтакте ✅  
Работает как с браузерами так и с приложениями ✅   
Показывает статус паузы ✅  
Показывает сколько осталось до конца трека ✅




## Требования
Работа проверена только на Windows 11 и Windows 10, на других версиях и платформах работать не будет.

Если вы не будете использовать ехе файл то:
1. Python 3.10+


## Как скачать и использовать Exe?
1. Скачиваем [последний доступный релиз](https://github.com/AtikD/WinYandexMusicRPC/releases)
  
2. Открываем WinYandexMusicRPC.exe

## Как скачать и использовать main.py?
1. Скачиваме архив с кодом

2. Открываем терминал и идем в папку где находится файл `requirements.txt`. Пишем `pip install -r requirements.txt`, для того что бы установить зависимости.

3. В терминал пишем `python main.py`

------------
В случае если вы слушаете музыку не только из яндекс музыки то рекомендую отключить галочку `strong_find`. Тогда будет показыватся лучший результат по поиску, но не всегда точный.

## Баги
Баги всегда существуют, но сначала их надо найти 🫡  
Если вы нашли ошибку, то не стесняйтесь сообщать о ней в [Issues](https://github.com/AtikD/WinYandexMusicRPC/issues)

## TODO
Если долгая пауза - убирать статус ✅  
Улучшить поиск песен ✅  
Вместо консоли сделать приложение в трее ✅    
Сделать чтобы таймер не сбрасывался при паузе трека ❌    
Добавить настройки ✅  
   
------------
Пожалуйста, покажите вашу заинтересованность в этом проекте, что бы я мог его обновлять по мере возможности.


>За основу был взят код [yandex-music-rpc](https://github.com/schwarzalexey/yandex-music-rpc/tree/main), а также [WinYandexMusicRPC](https://github.com/FozerG/WinYandexMusicRPC)

>Используется [Yandex Music API](https://github.com/MarshalX/yandex-music-api)   
