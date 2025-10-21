from __future__ import annotations
import configparser, datetime, logging, sqlite3, json, sys, io, os
import requests, PIL.Image, PIL.ImageDraw
from . import utils


# region Providers

class IDataProvider:
    """
    Class for providing data from JSON-like files
    """

    _PATH: str = utils.get_path("data/")
    """
    Path to the directory with JSON-like files
    """

    _FILENAME: str = "{0}.json"
    """
    Filename of JSON-like files
    """

    _DATA_VALUES: dict[str, type]
    """
    Dictionary with filenames and containers

    Example:
        _DATA_VALUES = {"users": UsersContainer}
    """

    def __init__(self) -> None:
        for filename, container in self._DATA_VALUES.items():
            try:
                with open(self._PATH + self._FILENAME.format(filename), "rb") as file:
                    setattr(self, filename, container(json.loads(file.read())))
            except:
                setattr(self, filename, None)


class IConfigProvider:
    """
    Class for providing data from configuration file
    """

    class IConfig:
        """
        Class that represents a section in configuration file
        """

        _SECTION: str = None
        """
        Name of the section in configuration file

        Example:
            _SECTION = "Settings"
        """

        _CONFIG_VALUES: dict[str, type]
        """
        Dictionary with settings and their types
        """

        def __init__(self, parent: IConfigProvider = None) -> None:
            if isinstance(parent, IConfigProvider):
                self._CONFIG_VALUES = parent._CONFIG_VALUES.get(self._SECTION)

                self._incorrect_content_exception = configparser.ParsingError(
                    "configuration file is filled incorrectly!"
                )
                self._config = configparser.ConfigParser()
                self._config.read(parent._PATH)

                if not self._config.has_section(self._SECTION):
                    self._config.add_section(self._SECTION)

                for setting, data_type in self._CONFIG_VALUES.items():
                    try:
                        setattr(self, setting, self._config.get(self._SECTION, setting))
                    except:
                        self._config.set(self._SECTION, setting, data_type.__name__)
                        with open(parent._PATH, "w", encoding="utf-8") as file:
                            self._config.write(file)

                for setting, data_type in self._CONFIG_VALUES.items():
                    try:
                        match data_type.__name__:
                            case "int":
                                setattr(self, setting, int(getattr(self, setting)))
                            case "float":
                                setattr(self, setting, float(getattr(self, setting)))
                            case "bool":
                                if getattr(self, setting) not in (str(True), str(False)):
                                    setattr(self, setting, None)
                                    raise self._incorrect_content_exception
                                else:
                                    setattr(self, setting, getattr(self, setting) == str(True))
                            case "dict" | "list":
                                setattr(self, setting, json.loads(getattr(self, setting)))
                    except:
                        setattr(self, setting, None)
                        raise self._incorrect_content_exception

                if not self.values:
                    raise self._incorrect_content_exception

        @property
        def values(self) -> dict | None:
            """
            :return: Values stored in section
            """

            try:
                return {setting: getattr(self, setting) for setting in self._CONFIG_VALUES.keys()}
            except:
                return None

    _PATH: str = utils.get_path("config.ini")
    """
    Path to the configuration file
    """

    _CONFIG_VALUES: dict[str, dict[str, type]]
    """
    Dictionary with sections, their settings and their types

    Example:
        _CONFIG_VALUES = {"Settings": {"version": str}}
    """

    _CONFIG_OBJECTS: dict[str, type]
    """
    Dictionary with names of attributes and child objects

    Example:
        _CONFIG_OBJECTS = {"settings": SettingsConfig}
    """

    def __init__(self) -> None:
        for name, data_class in self._CONFIG_OBJECTS.items():
            setattr(self, name, data_class(self))


class IAssetsProvider:
    """
    Class for providing various assets data
    """

    class IDirectory:
        """
        Class that represents a directory with various assets
        """

        _PATH: str = None
        """
        Path to the directory with assets files

        Example:
            _PATH = "images/"
        """

        _FILENAME: str = None
        """
        Filename of assets files

        Example:
            _FILENAME = "{0}.png"
        """

        _NAMES: set[str]
        """
        Names of files in the directory

        Example:
            _NAMES = {"picture1", "picture2"}
        """

        def __init__(self, parent: IAssetsProvider) -> None:
            self._PATH = parent._PATH + self._PATH

            if isinstance(parent, IAssetsProvider):
                for filename in self._NAMES:
                    setattr(self, filename, parent.file_image(self._PATH + self._FILENAME.format(filename)))

    class INetwork:
        """
        Class that represents a set of images obtained from a network
        """

        _URLS: dict[str, str]
        """
        Dictionary with names of attributes and URLs

        Example:
            _URLS = {"example": "https://example.com/image.png"}
        """

        def __init__(self, parent: IAssetsProvider) -> None:
            if isinstance(parent, IAssetsProvider):
                for name, url in self._URLS.items():
                    setattr(self, name, parent.network_image(url))

    _PATH: str = utils.get_path("assets/")
    """
    Path to the directory with assets folders
    """

    _ASSETS_OBJECTS: dict[str, type]
    """
    Dictionary with names of attributes and child objects

    Example:
        _ASSETS_OBJECTS = {"images": ImagesAssets, "example": ExampleNetwork}
    """

    def __init__(self) -> None:
        for name, data_class in self._ASSETS_OBJECTS.items():
            setattr(self, name, data_class(self))

    @staticmethod
    def file_image(path: str) -> PIL.Image.Image:
        """
        :return: Image object from a file
        """

        with open(path, "rb") as file:
            return PIL.Image.open(io.BytesIO(file.read()))

    @staticmethod
    def network_image(url: str) -> PIL.Image.Image:
        """
        :return: Image object from a URL
        """

        return PIL.Image.open(io.BytesIO(requests.get(url).content))

    @staticmethod
    def round_corners(image: PIL.Image.Image, radius: int) -> PIL.Image.Image:
        """
        :return: Image with rounded edges of the specified radius
        """

        if image.mode != "RGB":
            image = image.convert("RGB")
        width, height = image.size

        shape = PIL.Image.new("L", (radius * 2, radius * 2), 0)
        PIL.ImageDraw.Draw(shape).ellipse((0, 0, radius * 2, radius * 2), fill=255)

        alpha = PIL.Image.new("L", image.size, "white")
        alpha.paste(shape.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(shape.crop((0, radius, radius, radius * 2)), (0, height - radius))
        alpha.paste(shape.crop((radius, 0, radius * 2, radius)), (width - radius, 0))
        alpha.paste(shape.crop((radius, radius, radius * 2, radius * 2)), (width - radius, height - radius))
        image.putalpha(alpha)

        return image


class IStringsProvider:
    """
    Class for providing various strings data
    """

    class IStrings:
        """
        Class that represents a container for strings
        """

        pass

    _STRINGS_OBJECTS: dict[str, type]
    """
    Dictionary with names of attributes and child objects

    Example:
        _STRINGS_OBJECTS = {"localizable": LocalizableStrings}
    """

    def __init__(self) -> None:
        for name, data_class in self._STRINGS_OBJECTS.items():
            setattr(self, name, data_class())


# endregion

# region Managers

class IDatabaseManager:
    """
    Class for managing database connections
    """

    class IDatabase(sqlite3.Connection):
        """
        Class that represents a database connection
        """

        _NAME: str = None
        """
        Name of the database

        Example:
            _NAME = "users"
        """

        _SQL: str = None
        """
        SQL expression for creating a database

        Example:
            _SQL = f\"\"\"CREATE TABLE IF NOT EXISTS {_NAME} (user_id INTEGER PRIMARY KEY NOT NULL)\"\"\"
        """

        _FILENAME: str = "{0}.db"
        """
        File extension of database
        """

        def __init__(self, parent: IDatabaseManager) -> None:
            if isinstance(parent, IDatabaseManager):
                self._FILENAME = self._FILENAME.format(self._NAME)

                super().__init__(
                    database=parent._PATH + self._FILENAME,
                    check_same_thread=False,
                )

                self._cursor.execute(self._SQL)
                self.commit()

        @property
        def _cursor(self) -> sqlite3.Cursor:
            return self.cursor()

    _PATH: str = utils.get_path("db/")
    """
    Path to the directory with databases
    """

    _DATABASE_OBJECTS: dict[str, type]
    """
    Dictionary with names of attributes and child objects

    Example:
        _DATABASE_OBJECTS = {"users": UsersDatabase}
    """

    def __init__(self) -> None:
        os.makedirs(self._PATH, exist_ok=True)

        for name, data_class in self._DATABASE_OBJECTS.items():
            setattr(self, name, data_class(self))

    def close_all(self) -> None:
        """
        Closes all database connections
        """
        for database in self._DATABASE_OBJECTS.keys():
            getattr(self, database).close()


if sys.platform == "win32":
    import winreg


    class IRegistryManager:
        """
        Class for managing data in the Windows Registry
        """

        class IRegistry:
            """
            Class that represents a key with parameters in the Windows Registry
            """

            _NAME: str = None
            """
            Name of key in the Windows Registry

            Example:
                _NAME = "OAuth"
            """

            _REGISTRY_VALUES: dict[str, int]
            """
            Dictionary with settings and their types
            """

            _path: winreg.HKEYType

            def __init__(self, parent: IRegistryManager = None) -> None:
                if isinstance(parent, IRegistryManager):
                    self._REGISTRY_VALUES = parent._REGISTRY_VALUES.get(self._NAME)
                    self._path = winreg.CreateKey(parent._path, self._NAME)

                    for setting in self._REGISTRY_VALUES.keys():
                        try:
                            setattr(self, setting, winreg.QueryValueEx(self._path, setting)[int()])
                        except:
                            setattr(self, setting, None)

            @property
            def values(self) -> dict | None:
                """
                :return: Values stored in key in the Windows Registry
                """

                try:
                    return {setting: getattr(self, setting) for setting in self._REGISTRY_VALUES.keys()}
                except:
                    return None

            def refresh(self) -> IRegistryManager.IRegistry:
                """
                :return: Instance with refreshed values
                """

                self.__init__()
                return self

            def update(self, **kwargs) -> None:
                """
                Updates provided settings in the Windows Registry
                """

                for setting, value in kwargs.items():
                    winreg.SetValueEx(self._path, setting, None, self._REGISTRY_VALUES.get(setting), value)
                    setattr(self, setting, value)

        _KEY: str
        """
        Path to key in the Windows Registry

        Example:
            _KEY = "Software\\\\\\\\diquoks Software\\\\\\\\pyquoks"
        """

        _REGISTRY_VALUES: dict[str, dict[str, int]]
        """
        Dictionary with keys, their settings and their types

        Example:
            _REGISTRY_VALUES = {"OAuth": {"access_token": winreg.REG_SZ}}
        """

        _REGISTRY_OBJECTS: dict[str, type]
        """
        Dictionary with names of attributes and child objects

        Example:
            _REGISTRY_OBJECTS = {"oauth": OAuthRegistry}
        """

        _path: winreg.HKEYType

        def __init__(self) -> None:
            self._path = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self._KEY)

            for name, data_class in self._REGISTRY_OBJECTS.items():
                setattr(self, name, data_class(self))

        def refresh(self) -> IRegistryManager:
            """
            :return: Instance with refreshed values
            """

            self.__init__()
            return self


# endregion

# region Services

class LoggerService(logging.Logger):
    """
    Class that provides methods for parallel logging
    """

    _LOGS_PATH: str | None
    """
    Path to the logs file
    """

    def __init__(
            self,
            name: str,
            path: str = utils.get_path("logs/", only_abspath=True),
            filename: str = datetime.datetime.now().strftime("%d-%m-%y-%H-%M-%S"),
            file_handling: bool = True,
            level: int = logging.NOTSET,
    ) -> None:
        super().__init__(name, level)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(
            logging.Formatter(
                fmt="$levelname $asctime $name - $message",
                datefmt="%d-%m-%y %H:%M:%S",
                style="$",
            )
        )
        self.addHandler(stream_handler)

        if file_handling:
            os.makedirs(path, exist_ok=True)
            self._LOG_PATH = path + f"{filename}-{name}.log"

            file_handler = logging.FileHandler(
                self._LOG_PATH,
                encoding="utf-8",
            )
            file_handler.setFormatter(
                logging.Formatter(
                    fmt="$levelname $asctime - $message",
                    datefmt="%d-%m-%y %H:%M:%S",
                    style="$",
                ),
            )
            self.addHandler(file_handler)

    def get_logs_file(self) -> io.BufferedReader:
        """
        :return: Opened file-like object of current logs
        """
        return open(self._LOG_PATH, "rb")

    def log_exception(self, e: Exception) -> None:
        """
        Logs an exception with detailed traceback
        """

        self.error(msg=e, exc_info=True)

# endregion
