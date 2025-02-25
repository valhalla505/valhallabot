from setuptools import setup, find_packages

setup(
    name="valhallabot",
    version="1.0.0",
    author="Ahmed",
    author_email="almkhtrt@gmail.com",
    description="A Telegram bot for sending emails with customizable settings.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/valhallabot",
    packages=find_packages(),
    install_requires=[
        "pyTelegramBotAPI",
        "smtplib",
        "email",
        "datetime",
        "threading",
        "random",
        "json",
        "os",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)