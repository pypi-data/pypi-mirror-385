# Weblite Framework

Базовый фреймворк для веб-приложений.

## Установка

```bash
pip install weblite-framework
```

## BaseRepositoryClass - Базовый класс для репозиториев

`BaseRepositoryClass` предоставляет базовую функциональность для работы с базой данных через SQLAlchemy. Этот класс реализует паттерн Repository и обеспечивает типизированную работу с ORM моделями и DTO объектами.

### Основные возможности

- **Типизированная работа** с Generic типами `BaseRepositoryClass[DTO, SQLModel]`
- **Абстрактные методы** для маппинга между моделями и DTO
- **Управление транзакциями** с гибкими настройками
- **Базовые операции** CRUD для работы с БД

### Использование

```python
from typing import TypeVar
from weblite_framework.repository.base import BaseRepositoryClass
from weblite_framework.database.models import BaseModel

# Определяем типы
class UserDTO:
    def __init__(self, id_: int, name: str):
        self.id_ = id_
        self.name = name

class UserModel(BaseModel):
    id_: int
    name: str

# Создаем репозиторий
class UserRepository(BaseRepositoryClass[UserDTO, UserModel]):
    def _model_to_dto(self, model: UserModel) -> UserDTO:
        return UserDTO(id_=model.id_, name=model.name)
    
    def _dto_to_model(self, dto: UserDTO) -> UserModel:
        model = UserModel()
        model.id_ = dto.id_
        model.name = dto.name
        return model

# Использование
async def create_user(session: AsyncSession):
    repo = UserRepository(session=session)
    
    # Создание записи
    user_model = UserModel()
    user_model.name = "John"
    created_user = await repo._add_record(model=user_model)
    
    # Обновление записи
    existing_user = UserModel()
    existing_user.id_ = 1
    existing_user.name = "Old Name"
    
    new_data = UserModel()
    new_data.name = "New Name"
    
    updated_user = await repo._update(
        existing_model=existing_user, 
        new_data=new_data
    )
    
    # Выполнение запросов
    from sqlalchemy import select
    query = select(UserModel).where(UserModel.id_ == 1)
    result = await repo.execute(statement=query, is_use_active_transaction=False)
    
    # Коммит изменений
    await repo.commit()
```

### Основные методы

#### `_add_record(model: SQLModel) -> SQLModel`
Создает новую запись в базе данных и возвращает модель с присвоенным идентификатором.

#### `_update(existing_model: SQLModel, new_data: SQLModel, ignore_fields: list[str] | None = None) -> SQLModel`
Обновляет существующую запись в базе данных. Поле `_sa_instance_state` всегда игнорируется.

#### `execute(statement: Executable, is_use_active_transaction: bool = True) -> Result[Any]`
Выполняет SQL запрос с возможностью управления транзакциями:
- `is_use_active_transaction=True` - использует активную транзакцию
- `is_use_active_transaction=False` - создает новую транзакцию

#### `commit() -> None`
Выполняет коммит текущей транзакции.

#### `flush() -> None`
Сбрасывает изменения в базу данных без коммита.

#### `refresh(instance: SQLModel) -> None`
Обновляет состояние модели из базы данных.

### Абстрактные методы

#### `_model_to_dto(model: SQLModel) -> DTO`
Преобразует ORM модель в DTO объект. Должен быть реализован в дочернем классе.

#### `_dto_to_model(dto: DTO) -> SQLModel`
Преобразует DTO объект в ORM модель. Должен быть реализован в дочернем классе.

### Пример выполнения кастомных запросов

```python
from sqlalchemy import text

# Выполнение raw SQL
query = text("SELECT * FROM users WHERE age > :min_age")
result = await repo.execute(
    statement=query, 
    is_use_active_transaction=False
)

# Выполнение в рамках активной транзакции
async with session.begin():
    await repo._add_record(model=user_model)
    await repo.execute(statement=query, is_use_active_transaction=True)
    # Все операции выполняются в одной транзакции
```

### Примечания

- Все методы работают асинхронно
- Класс использует SQLAlchemy 2.0+ синтаксис
- Поддерживает типизацию через Generic типы
- Следует паттерну Repository для разделения логики доступа к данным

### Обработка ошибок и Rollback

Все транзакционные методы автоматически выполняют rollback при возникновении исключений:

```python
# При ошибке в любом методе автоматически выполняется rollback
try:
    await repo._add_record(model=user_model)
    await repo.commit()
except Exception as e:
    # Транзакция уже откачена автоматически
    print(f"Ошибка: {e}")
```

**Методы с автоматическим rollback:**
- `_add_record()` - при ошибке создания записи
- `_update()` - при ошибке обновления записи  
- `commit()` - при ошибке коммита
- `execute()` - при ошибке выполнения запроса
- `refresh()` - при ошибке обновления модели
- `flush()` - при ошибке сброса изменений
