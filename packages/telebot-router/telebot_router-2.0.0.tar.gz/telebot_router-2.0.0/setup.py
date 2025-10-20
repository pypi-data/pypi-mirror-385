from setuptools import setup, find_packages
import pathlib

# Fayl yo'lini olish
here = pathlib.Path(__file__).parent.resolve()

# README.md dan tavsifni o‘qish
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="telebot-router",  # 📦 PyPI nomi
    version="2.0.0",
    author="o6.javohir.ergashev@gmail.com",
    description="Aiogram-style Router for pyTeleBot — simple, async-ready, and powerful routing system.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/Ergashev2006/telebot-router",  # asosiy repo

    license="MIT",
    license_files=["LICENSE"],

    packages=find_packages(exclude=("tests*", "examples*", "docs*")),
    include_package_data=True,

    python_requires=">=3.7",


    extras_require={
        "dev": ["pytest", "black", "flake8", "twine", "build"],
    },

    keywords=[
        "telegram", "bot", "telebot", "router",
        "aiogram", "async", "python-telegram-bot", "pyTelegramBotAPI"
    ],

    classifiers=[
        "Development Status :: 5 - Production/Stable",  # yoki "4 - Beta"
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],

)