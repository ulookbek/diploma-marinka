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

# Запускаем сервер
echo "Запускаю сервер..."
uvicorn app:app --reload &

# Ждём немного чтобы сервер успел стартовать
sleep 2

# Открываем браузер на localhost
echo "Открываю браузер..."
open "http://127.0.0.1:8000/"

# Оставляем сервер работающим в фоне
wait