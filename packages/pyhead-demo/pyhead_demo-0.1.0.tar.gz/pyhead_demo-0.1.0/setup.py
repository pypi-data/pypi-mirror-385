from setuptools import setup, find_packages

# Прочитати README для довгого опису
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyhead-demo',  # <-- ВАШЕ УНІКАЛЬНЕ ІМ'Я ПАКЕТУ
    version='0.1.0',     # Початкова версія
    packages=find_packages(),
    install_requires=[
        'click',  # Наша єдина залежність
    ],
    entry_points={
        'console_scripts': [
            # Цей рядок створює команду 'pyhead-demo' в терміналі
            'pyhead-demo=pyhead_demo.__main__:pyhead', # ІМ'Я_КОМАНДИ=ШЛЯХ:ФУНКЦІЯ
        ],
    },
    author='Анастасія',
    author_email='trushchaknastya@gmail.com',
    description='A Python implementation of the head command.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/anastasiatrushchak/pyhead-demo', # Посилання на ваш репозиторій
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7', # Вказуємо мінімальну версію Python
)