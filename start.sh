#!/bin/bash

# Название виртуального окружения
VENV_DIR="venv"

# Проверяем, есть ли виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
  echo "Создаю виртуальное окружение..."
  python3 -m venv $VENV_DIR
fi

# Активируем виртуальное окружение
source $VENV_DIR/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install fastapi uvicorn

# Запускаем сервер в фоне
echo "Запускаю сервер..."
uvicorn app:app --reload &

# Ждём чуть-чуть, чтобы сервер поднялся
sleep 2

# Открываем локальный файл index.html в браузере
INDEX_PATH="$(pwd)/index.html"

if [ -f "$INDEX_PATH" ]; then
  echo "Открываю файл: $INDEX_PATH"
  open "file://$INDEX_PATH"
else
  echo "Файл index.html не найден в $(pwd)"
fi

# Держим скрипт пока сервер работает
wait