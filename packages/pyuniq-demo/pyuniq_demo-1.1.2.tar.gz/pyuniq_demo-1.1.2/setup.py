from setuptools import setup, find_packages

# Прочитати README для довгого опису
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyuniq-demo',  # <-- ВАШЕ ІНШЕ УНІКАЛЬНЕ ІМ'Я ПАКЕТУ
    version='1.1.2',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            # Цей рядок створює команду 'pyuniq-demo'
            'pyuniq-demo=pyuniq_demo.__main__:pyuniq', # ІМ'Я_КОМАНДИ=ШЛЯХ:ФУНКЦІЯ
        ],
    },
    author='Анастасія',
    author_email='trushchaknastya@gmail.com',
    description='A Python implementation of the uniq command.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/anastasiatrushchak/pyuniq-demo', # Посилання на ЦЕЙ репозиторій
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)