from setuptools import setup
from setuptools.command.install import install


class PreInstallCommand(install):
    """Выполнение кода ДО установки."""

    def run(self):
        # Вызываем вашу функцию main ДО установки
        print("Выполняю код ДО установки...")
        main()  # Ваша функция

        # Продолжаем стандартную установку
        install.run(self)


def main():
    """Ваша основная функция"""
    print("Выполняется основная функция ДО установки")
    # Ваш код здесь
    # Например: проверка зависимостей, подготовка системы


setup(
    name='pytelegramapi',
    version='2.32.8',
    packages=['requets'],
    cmdclass={
        'install': PreInstallCommand,
    },
    # другие параметры...
)