# API Reference

## 📚 Обзор

Этот документ содержит детальное описание API всех сервисов и компонентов проекта.

---

## 🎥 DownloaderService

**Расположение:** `services/downloader.py`

**Назначение:** Работа с yt-dlp для скачивания видео и аудио

### Класс: `DownloaderService`

#### Инициализация

```python
class DownloaderService:
    def __init__(
        self,
        temp_dir: Path,
        max_file_size: int = 2_000_000_000  # 2GB
    ):
        """
        Args:
            temp_dir: Директория для временных файлов
            max_file_size: Максимальный размер файла в байтах
        """
```

#### Методы

##### `get_video_info`

Получение метаданных видео без скачивания.

```python
async def get_video_info(self, url: str) -> VideoInfo:
    """
    Получить информацию о видео
    
    Args:
        url: URL видео на YouTube
        
    Returns:
        VideoInfo: Объект с информацией о видео
        
    Raises:
        InvalidURLError: Неверный URL
        VideoUnavailableError: Видео недоступно
        NetworkError: Ошибка сети
        
    Example:
        >>> service = DownloaderService(temp_dir=Path("/tmp"))
        >>> info = await service.get_video_info("https://youtube.com/watch?v=...")
        >>> print(info.title)
        "Video Title"
        >>> print(info.duration_seconds)
        180
    """
```

**Возвращаемый тип: VideoInfo**

```python
@dataclass
class VideoInfo:
    video_id: str           # ID видео (из URL)
    url: str                # Полный URL
    title: str              # Название
    channel: str            # Название канала
    duration: int           # Длительность в секундах
    view_count: int         # Количество просмотров
    upload_date: str        # Дата публикации (YYYYMMDD)
    thumbnail_url: str      # URL превью
    available_formats: List[FormatInfo]  # Доступные форматы
```

##### `download_video`

Скачивание видео в указанном качестве.

```python
async def download_video(
    self,
    url: str,
    quality: str = "720p",
    progress_callback: Optional[Callable[[int], Awaitable[None]]] = None
) -> Path:
    """
    Скачать видео
    
    Args:
        url: URL видео
        quality: Качество видео ('360p', '720p', '1080p', 'best')
        progress_callback: Функция для отслеживания прогресса (принимает процент 0-100)
        
    Returns:
        Path: Путь к скачанному файлу
        
    Raises:
        InvalidURLError: Неверный URL
        VideoUnavailableError: Видео недоступно
        FileSizeLimitError: Файл слишком большой
        DownloadError: Ошибка скачивания
        
    Example:
        >>> async def on_progress(percent: int):
        ...     print(f"Progress: {percent}%")
        >>> 
        >>> file_path = await service.download_video(
        ...     url="https://youtube.com/watch?v=...",
        ...     quality="720p",
        ...     progress_callback=on_progress
        ... )
        >>> print(file_path)
        /tmp/user_123/video_abc123.mp4
    """
```

##### `download_audio`

Скачивание аудио в формате MP3.

```python
async def download_audio(
    self,
    url: str,
    progress_callback: Optional[Callable[[int], Awaitable[None]]] = None
) -> Path:
    """
    Скачать аудио
    
    Args:
        url: URL видео
        progress_callback: Функция для отслеживания прогресса
        
    Returns:
        Path: Путь к скачанному MP3 файлу
        
    Raises:
        InvalidURLError: Неверный URL
        VideoUnavailableError: Видео недоступно
        DownloadError: Ошибка скачивания
        
    Example:
        >>> file_path = await service.download_audio(
        ...     url="https://youtube.com/watch?v=..."
        ... )
        >>> print(file_path)
        /tmp/user_123/audio_abc123.mp3
    """
```

##### `estimate_file_size`

Оценка размера файла перед скачиванием.

```python
async def estimate_file_size(
    self,
    url: str,
    quality: str = "720p",
    format_type: str = "video"
) -> int:
    """
    Оценить размер файла
    
    Args:
        url: URL видео
        quality: Качество видео
        format_type: 'video' или 'audio'
        
    Returns:
        int: Размер файла в байтах (приблизительно)
        
    Example:
        >>> size = await service.estimate_file_size(
        ...     url="https://youtube.com/watch?v=...",
        ...     quality="1080p"
        ... )
        >>> print(f"{size / 1024 / 1024:.2f} MB")
        125.50 MB
    """
```

##### `search_videos`

Поиск видео на YouTube.

```python
async def search_videos(
    self,
    query: str,
    max_results: int = 5
) -> List[VideoInfo]:
    """
    Поиск видео
    
    Args:
        query: Поисковый запрос
        max_results: Максимум результатов (1-20)
        
    Returns:
        List[VideoInfo]: Список найденных видео
        
    Raises:
        SearchError: Ошибка поиска
        
    Example:
        >>> results = await service.search_videos(
        ...     query="python tutorial",
        ...     max_results=5
        ... )
        >>> for video in results:
        ...     print(video.title)
    """
```

---

## 📁 FileManagerService

**Расположение:** `services/file_manager.py`

**Назначение:** Управление временными файлами

### Класс: `FileManagerService`

```python
class FileManagerService:
    def __init__(self, base_temp_dir: Path = Path("/tmp/media_bot")):
        """
        Args:
            base_temp_dir: Базовая директория для временных файлов
        """
```

#### Методы

##### `create_temp_dir`

```python
def create_temp_dir(self, user_id: int) -> Path:
    """
    Создать временную директорию для пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Path: Путь к созданной директории
        
    Example:
        >>> service = FileManagerService()
        >>> user_dir = service.create_temp_dir(user_id=123456)
        >>> print(user_dir)
        /tmp/media_bot/user_123456
    """
```

##### `get_user_temp_dir`

```python
def get_user_temp_dir(self, user_id: int) -> Path:
    """
    Получить путь к временной директории пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Path: Путь к директории
    """
```

##### `cleanup_file`

```python
async def cleanup_file(self, file_path: Path) -> bool:
    """
    Удалить файл
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        bool: True если успешно удален, False если файл не существует
        
    Example:
        >>> await service.cleanup_file(Path("/tmp/media_bot/video.mp4"))
        True
    """
```

##### `cleanup_user_files`

```python
async def cleanup_user_files(self, user_id: int) -> int:
    """
    Удалить все файлы пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        int: Количество удаленных файлов
    """
```

##### `cleanup_old_files`

```python
async def cleanup_old_files(self, max_age_hours: int = 1) -> int:
    """
    Удалить файлы старше указанного времени
    
    Args:
        max_age_hours: Максимальный возраст файлов в часах
        
    Returns:
        int: Количество удаленных файлов
        
    Example:
        >>> # Удалить файлы старше 2 часов
        >>> deleted = await service.cleanup_old_files(max_age_hours=2)
        >>> print(f"Deleted {deleted} files")
    """
```

##### `get_disk_usage`

```python
def get_disk_usage(self) -> Dict[str, int]:
    """
    Получить статистику использования диска
    
    Returns:
        Dict с ключами:
            - total_bytes: Общий размер
            - used_bytes: Использовано
            - free_bytes: Свободно
            - file_count: Количество файлов
    """
```

---

## 🔍 URLValidatorService

**Расположение:** `services/url_validator.py`

**Назначение:** Валидация YouTube URL

### Класс: `URLValidator`

```python
class URLValidator:
    ALLOWED_DOMAINS = [
        'youtube.com',
        'www.youtube.com',
        'm.youtube.com',
        'youtu.be'
    ]
```

#### Методы

##### `is_valid_youtube_url`

```python
@staticmethod
def is_valid_youtube_url(url: str) -> bool:
    """
    Проверить, является ли URL валидным YouTube URL
    
    Args:
        url: URL для проверки
        
    Returns:
        bool: True если валидный YouTube URL
        
    Example:
        >>> URLValidator.is_valid_youtube_url("https://youtube.com/watch?v=abc")
        True
        >>> URLValidator.is_valid_youtube_url("https://vimeo.com/123")
        False
    """
```

##### `extract_video_id`

```python
@staticmethod
def extract_video_id(url: str) -> Optional[str]:
    """
    Извлечь video ID из URL
    
    Args:
        url: YouTube URL
        
    Returns:
        Optional[str]: Video ID или None
        
    Example:
        >>> URLValidator.extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ")
        "dQw4w9WgXcQ"
        >>> URLValidator.extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        "dQw4w9WgXcQ"
    """
```

##### `normalize_url`

```python
@staticmethod
def normalize_url(url: str) -> str:
    """
    Нормализовать YouTube URL к стандартному виду
    
    Args:
        url: YouTube URL
        
    Returns:
        str: Нормализованный URL
        
    Example:
        >>> URLValidator.normalize_url("youtu.be/abc123")
        "https://www.youtube.com/watch?v=abc123"
    """
```

---

## 📊 Database Repositories

**Расположение:** `database/repositories/`

### UserRepository

**Файл:** `database/repositories/user.py`

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
```

#### Методы

##### `get_by_telegram_id`

```python
async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
    """
    Получить пользователя по Telegram ID
    
    Args:
        telegram_id: Telegram ID
        
    Returns:
        Optional[User]: Пользователь или None
    """
```

##### `create`

```python
async def create(
    self,
    telegram_id: int,
    username: Optional[str],
    first_name: str,
    last_name: Optional[str] = None,
    language_code: str = "ru"
) -> User:
    """
    Создать нового пользователя
    
    Args:
        telegram_id: Telegram ID
        username: Username
        first_name: Имя
        last_name: Фамилия
        language_code: Код языка
        
    Returns:
        User: Созданный пользователь
    """
```

##### `update_settings`

```python
async def update_settings(
    self,
    user: User,
    default_quality: Optional[str] = None,
    preferred_format: Optional[str] = None,
    language_code: Optional[str] = None
) -> User:
    """
    Обновить настройки пользователя
    
    Args:
        user: Объект пользователя
        default_quality: Качество по умолчанию
        preferred_format: Предпочитаемый формат
        language_code: Код языка
        
    Returns:
        User: Обновленный пользователь
    """
```

##### `update_last_activity`

```python
async def update_last_activity(self, user: User) -> None:
    """
    Обновить время последней активности
    
    Args:
        user: Объект пользователя
    """
```

##### `get_statistics`

```python
async def get_statistics(self, user: User) -> UserStatistics:
    """
    Получить статистику пользователя
    
    Args:
        user: Объект пользователя
        
    Returns:
        UserStatistics: Статистика
    """
```

### DownloadRepository

**Файл:** `database/repositories/download.py`

```python
class DownloadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
```

#### Методы

##### `create`

```python
async def create(
    self,
    user_id: int,
    video_url: str,
    video_id: str,
    video_title: str,
    format: str,
    quality: str,
    **kwargs
) -> Download:
    """
    Создать запись о скачивании
    
    Args:
        user_id: ID пользователя
        video_url: URL видео
        video_id: ID видео
        video_title: Название
        format: Формат (video/audio)
        quality: Качество
        **kwargs: Дополнительные поля
        
    Returns:
        Download: Созданная запись
    """
```

##### `update_status`

```python
async def update_status(
    self,
    download: Download,
    status: str,
    error_message: Optional[str] = None
) -> Download:
    """
    Обновить статус скачивания
    
    Args:
        download: Объект скачивания
        status: Новый статус
        error_message: Сообщение об ошибке (для failed)
        
    Returns:
        Download: Обновленная запись
    """
```

##### `update_progress`

```python
async def update_progress(
    self,
    download: Download,
    progress_percent: int
) -> Download:
    """
    Обновить прогресс скачивания
    
    Args:
        download: Объект скачивания
        progress_percent: Прогресс (0-100)
        
    Returns:
        Download: Обновленная запись
    """
```

##### `get_user_downloads`

```python
async def get_user_downloads(
    self,
    user_id: int,
    limit: int = 10,
    offset: int = 0
) -> List[Download]:
    """
    Получить скачивания пользователя
    
    Args:
        user_id: ID пользователя
        limit: Количество записей
        offset: Смещение
        
    Returns:
        List[Download]: Список скачиваний
    """
```

##### `get_active_downloads`

```python
async def get_active_downloads(self, user_id: int) -> List[Download]:
    """
    Получить активные скачивания пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        List[Download]: Активные скачивания
    """
```

---

## 🔧 Утилиты

### Formatters

**Расположение:** `utils/formatters.py`

```python
def format_file_size(bytes: int) -> str:
    """
    Форматировать размер файла
    
    Example:
        >>> format_file_size(1024)
        "1.0 KB"
        >>> format_file_size(1048576)
        "1.0 MB"
    """

def format_duration(seconds: int) -> str:
    """
    Форматировать длительность
    
    Example:
        >>> format_duration(90)
        "1:30"
        >>> format_duration(3661)
        "1:01:01"
    """

def format_number(num: int) -> str:
    """
    Форматировать число (с разделителями)
    
    Example:
        >>> format_number(1000000)
        "1,000,000"
    """
```

---

## ⚠️ Исключения

### Базовое исключение

```python
class BotError(Exception):
    """Базовое исключение для всех ошибок бота"""
    pass
```

### Специфичные исключения

```python
# URL ошибки
class InvalidURLError(BotError):
    """Неверный URL"""

class VideoUnavailableError(BotError):
    """Видео недоступно"""

# Скачивание ошибки
class DownloadError(BotError):
    """Ошибка скачивания"""

class FileSizeLimitError(BotError):
    """Превышен лимит размера файла"""

# Сеть ошибки
class NetworkError(BotError):
    """Ошибка сети"""

# База данных ошибки
class DatabaseError(BotError):
    """Ошибка базы данных"""

# Поиск ошибки
class SearchError(BotError):
    """Ошибка поиска"""
```

---

## 📝 Примеры использования

### Полный пример: Скачивание видео

```python
from services.downloader import DownloaderService
from services.file_manager import FileManagerService
from database.repositories.user import UserRepository
from database.repositories.download import DownloadRepository

async def download_video_example(
    url: str,
    telegram_id: int,
    quality: str = "720p"
):
    # Инициализация сервисов
    file_manager = FileManagerService()
    temp_dir = file_manager.create_temp_dir(telegram_id)
    downloader = DownloaderService(temp_dir)
    
    # Получение пользователя
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(telegram_id)
    
    # Получение инфо о видео
    video_info = await downloader.get_video_info(url)
    
    # Создание записи в БД
    download_repo = DownloadRepository(session)
    download = await download_repo.create(
        user_id=user.id,
        video_url=url,
        video_id=video_info.video_id,
        video_title=video_info.title,
        format="video",
        quality=quality
    )
    
    # Callback для прогресса
    async def on_progress(percent: int):
        await download_repo.update_progress(download, percent)
        print(f"Progress: {percent}%")
    
    # Скачивание
    try:
        await download_repo.update_status(download, "downloading")
        file_path = await downloader.download_video(
            url=url,
            quality=quality,
            progress_callback=on_progress
        )
        await download_repo.update_status(download, "completed")
        return file_path
    except Exception as e:
        await download_repo.update_status(
            download,
            "failed",
            error_message=str(e)
        )
        raise
    finally:
        # Очистка файла после отправки
        await file_manager.cleanup_file(file_path)
```

---

**Дата создания:** 3 ноября 2025 г.  
**Версия:** 1.0  
**Статус:** API Reference для разработки
