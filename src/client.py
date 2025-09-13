import os
import yaml
import json
import gettext
import discord
from json import JSONDecodeError
from discord.ext import commands
from discord.app_commands import Translator, locale_str, TranslationContext


class ConfigFile:
    def __init__(self, prefix: str = "", token: str = ""):
        self.prefix = prefix
        self.token = token


class EmptyConfig(Exception):
    def __init__(self, config_path: str):
        self.message = f"Please, set up variables in {config_path}"
        super().__init__(self.message)


class Protocol(commands.Bot):
    def __init__(self, intents, activity, data_folder, config):
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)
        self.config_path = self.data_folder + config

        with open(self.config_path, "a+", encoding="utf8") as file:
            file.seek(0)
            try:
                data = json.load(file)
                self.config = ConfigFile(**data)
                if self.config.token == "":
                    raise EmptyConfig(self.config_path)
            except JSONDecodeError:
                json.dump(
                    ConfigFile().__dict__,
                    file,
                    sort_keys=False,
                    indent=4,
                    ensure_ascii=False,
                )
                raise EmptyConfig(self.config_path)

        self.__locales = {}
        self.__help_locales = {}
        for entry in next(os.walk("./locales"))[1]:
            self.__locales[entry] = gettext.translation(
                "protocol",
                localedir="./locales",
                languages=[entry]
            )
            with open(f"./locales/{entry}/help.yml", "r", encoding="UTF-8") as file:
                self.__help_locales[entry] = yaml.safe_load(file)
        for loca in self.__locales.values():
            loca.install()

        super().__init__(
            command_prefix=self.config.prefix, intents=intents, activity=activity
        )
        self.characters = None

    def locale(self, locale: str):
        locale = str(locale)
        if locale not in self.__locales:
            locale = "en_US"
        return self.__locales[locale].gettext

    def help_locale(self, locale: str):
        locale = str(locale)
        if locale not in self.__help_locales:
            return self.__help_locales["en_US"]
        return self.__help_locales[locale]

    def get_locales(self):
        return self.__locales

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=557589422372028416))
        await self.tree.set_translator(ProtocolTranslator(self))

    async def on_command_error(self, ctx, error):
        print(error)


class ProtocolTranslator(Translator):
    def __init__(self, bot: Protocol):
        self.__locales = bot.get_locales()

    async def translate(
            self,
            string: locale_str,
            locale: discord.Locale,
            context: TranslationContext
    ):
        lcl = str(locale)
        if lcl not in self.__locales:
            lcl = "en_US"
        _ = self.__locales[lcl].gettext
        return _(string.message)
