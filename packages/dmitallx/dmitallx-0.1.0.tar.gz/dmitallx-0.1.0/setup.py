from setuptools import setup, find_packages

setup(
    name='dmitallx',  # Имя вашей библиотеки
    version='0.1.0',  # Версия
    packages=find_packages(),  # Автоматически находит все пакеты
    install_requires=[
        'rich',  # Укажите зависимости, если они есть
        'functools',
    ],
    author='DmitX',  # Ваше имя
    author_email='Hieso123@yandex.com',  # Ваш email
    description='Небольшая библиотека для упрощения привычных действий.',  # Краткое описание
    long_description=open('README.md').read(),  # Подробное описание из README
    long_description_content_type='text/markdown',  # Тип содержимого описания
    url='https://github.com/Hieso/dmitallx',  # Ссылка на репозиторий
    classifiers=[
        'Programming Language :: Python :: 3',  # Поддержка Python 3
        'License :: OSI Approved :: MIT License',  # Лицензия
        'Operating System :: OS Independent',  # Операционные системы
    ],
    python_requires='>=3.6',  # Минимальная версия Python
)