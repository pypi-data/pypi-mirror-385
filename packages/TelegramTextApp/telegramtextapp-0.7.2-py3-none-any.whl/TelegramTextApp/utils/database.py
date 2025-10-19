import aiosqlite
import json
import sqlite3
import asyncio
import os
from . import logger
from .. import config 

logger = logger.setup("DATABASE")

db_dir = os.path.dirname(config.DB_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

async def SQL_request_async(query, params=(), fetch='one', jsonify_result=False):
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.cursor() as cursor:
            try:
                await cursor.execute(query, params)
                
                if fetch == 'all':
                    rows = await cursor.fetchall()
                    if rows:
                        columns = [desc[0] for desc in cursor.description]
                        result = []
                        for row in rows:
                            processed_row = {}
                            for i, col in enumerate(columns):
                                if isinstance(row[i], str) and row[i].startswith('{'):
                                    try:
                                        processed_row[col] = json.loads(row[i])
                                    except json.JSONDecodeError:
                                        processed_row[col] = row[i]
                                else:
                                    processed_row[col] = row[i]
                            result.append(processed_row)
                    else:
                        result = []
                
                elif fetch == 'one':
                    row = await cursor.fetchone()
                    if row:
                        columns = [desc[0] for desc in cursor.description]
                        result = {}
                        for i, col in enumerate(columns):
                            if isinstance(row[i], str) and row[i].startswith('{'):
                                try:
                                    result[col] = json.loads(row[i])
                                except json.JSONDecodeError:
                                    result[col] = row[i]
                            else:
                                result[col] = row[i]
                    else:
                        result = None
                
                else:  # Для запросов без выборки (INSERT/UPDATE/DELETE)
                    await db.commit()
                    result = None
                    
            except sqlite3.Error as e:
                await db.rollback()
                logger.error(f"Ошибка SQL: {e}")
                raise

    # Преобразование в JSON при необходимости
    if jsonify_result and result is not None:
        return json.dumps(result, ensure_ascii=False, indent=2)
    return result


def SQL_request(query, params=(), fetch='one', jsonify_result=False):
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)

            if fetch == 'all':
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                result = [
                    {
                        col: json.loads(row[i]) if isinstance(row[i], str) and row[i].startswith('{') else row[i]
                        for i, col in enumerate(columns)
                    }
                    for row in rows
                ]

            elif fetch == 'one':
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = {
                        col: json.loads(row[i]) if isinstance(row[i], str) and row[i].startswith('{') else row[i]
                        for i, col in enumerate(columns)
                    }
                else:
                    result = None
            else:
                conn.commit()
                result = None

        except sqlite3.Error as e:
            logger.error(f"Ошибка SQL: {e}")
            raise

    if jsonify_result and result is not None:
        return json.dumps(result, ensure_ascii=False, indent=2)
    return result


async def create_tables():
    # Пользователи
    await SQL_request_async('''
    CREATE TABLE IF NOT EXISTS TTA (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        message_id INTEGER,
        message_type TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_approved BOOLEAN DEFAULT 1,
        role TEXT DEFAULT 'user'
    )''')
    logger.debug("База настроена")

async def extract_user_data(bot_data, update=True):  # Извлекает данные пользователя из объекта бота/сообщения
    if hasattr(bot_data, 'message'):
        message = bot_data.message
        message_id = message.message_id
    else:
        message = bot_data
        try:
            if update is True:
                message_id = message.message_id
                if message.text.startswith('/'):
                    logger.debug("Обновление сообщения пользователя")
                    message_id = message.message_id+1
            else:
                user = await SQL_request_async('SELECT * FROM TTA WHERE telegram_id = ?', (message.chat.id,), "one")
                message_id = user["message_id"]
        except:
            message_id = message.message_id
    
    return {
        'telegram_id': message.chat.id,
        'first_name': message.chat.first_name,
        'last_name': message.chat.last_name,
        'username': message.chat.username,
        'message_id': message_id,
        'message_text': message.text
    }

async def create_user(bot_data):
    """Создает нового пользователя в базе данных."""
    user_data = await extract_user_data(bot_data)
    try:
        await SQL_request_async(
            '''
            INSERT INTO TTA (
                telegram_id, 
                first_name, 
                last_name, 
                username, 
                message_id
            ) VALUES (?, ?, ?, ?, ?)
            ''',
            (
        user_data['telegram_id'],
        user_data['first_name'],
        user_data['last_name'],
        user_data['username'],
        user_data['message_id']
            ), None
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка SQL при регистрации: {e}")
        return False

async def update_user_data(bot_data, update):
    """Обновляет данные пользователя в базе данных."""
    user_data = await extract_user_data(bot_data, update)
    try:
        await SQL_request_async(
            '''
            UPDATE TTA 
            SET 
                first_name = ?, 
                last_name = ?, 
                username = ?, 
                message_id = ? 
            WHERE telegram_id = ?
            ''',
            (
                user_data['first_name'],
                user_data['last_name'],
                user_data['username'],
                user_data['message_id'],
                user_data['telegram_id'],
            ), None
        )
    except Exception as e:
        logger.error(f"Не удалось обновить данные пользователя: {e}")

async def get_user(bot_data, update=False):
    """Возвращает пользователя, создает нового при отсутствии."""
    user_data = await extract_user_data(bot_data)
    telegram_id = user_data['telegram_id']
    user = await SQL_request_async('SELECT * FROM TTA WHERE telegram_id = ?', (telegram_id,), "one")
    
    if user:
        await update_user_data(bot_data, update)
        return await SQL_request_async('SELECT * FROM TTA WHERE telegram_id = ?', (telegram_id,), "one")
    else:
        if await create_user(bot_data):
            logger.info(f"Зарегистрирован новый пользователь: {telegram_id}")
            return await SQL_request_async('SELECT * FROM TTA WHERE telegram_id = ?', (telegram_id,))
        else:
            logger.error(f"Не удалось зарегистрировать пользователя {telegram_id}")
            return None

async def get_role_id(role):
    ids = await SQL_request_async('SELECT * FROM TTA WHERE role = ?', (role,), "all")
    return ids
