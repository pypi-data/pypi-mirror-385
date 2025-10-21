from __future__ import annotations


class IContainer:
    """
    Class for storing lists of models and another parameters
    """

    _ATTRIBUTES: set[str] | dict[str, set[str]] = None
    """
    Set of parameters that also can be stored one key deep

    Example:
        _ATTRIBUTES = {"beatmap_id", "score_id"}

        _ATTRIBUTES = {"attributes": {"max_combo", "star_rating"}}
    """

    _DATA: dict[str, type] = None
    """
    Dictionary with name and type of models stored in list inside ``json_data``

    Example:
        _DATA = {"scores": ScoreModel}
    """

    _OBJECTS: dict[str, type] = None
    """
    Dictionary with keys of ``json_data`` and types of models stored in a list inside

    Example:
        _OBJECTS = {"beatmaps": BeatmapModel, "scores": ScoreModel}
    """

    _data: dict
    """
    Initial data that was passed into object
    """

    def __init__(self, json_data: dict) -> None:
        self._data = json_data

        if isinstance(self._ATTRIBUTES, set):
            for name in self._ATTRIBUTES:
                setattr(self, name, self._data.get(name, None))
        elif isinstance(self._ATTRIBUTES, dict):
            for key, attributes in self._ATTRIBUTES.items():
                if isinstance(attributes, set):
                    for name in attributes:
                        try:
                            setattr(self, name, self._data.get(key).get(name, None))
                        except:
                            setattr(self, name, None)

        if isinstance(self._DATA, dict):
            for name, data_class in self._DATA.items():
                try:
                    setattr(self, name, [data_class(data) for data in self._data])
                except:
                    setattr(self, name, None)
        elif isinstance(self._OBJECTS, dict):
            for name, data_class in self._OBJECTS.items():
                try:
                    setattr(self, name, [data_class(data) for data in self._data.get(name)])
                except:
                    setattr(self, name, None)


class IModel:
    """
    Class for storing parameters and models
    """

    _ATTRIBUTES: set[str] | dict[str, set[str]] = None
    """
    Set of parameters that also can be stored one key deep

    Example:
        _ATTRIBUTES = {"beatmap_id", "score_id"}

        _ATTRIBUTES = {"attributes": {"max_combo", "star_rating"}}
    """

    _OBJECTS: dict[str, type] = None
    """
    Dictionary with attributes and their models
    
    Example:
        _OBJECTS = {"score": ScoreModel}
    """

    _data: dict | list[dict]
    """
    Initial data that was passed into object
    """

    def __init__(self, json_data: dict | list[dict]) -> None:
        self._data = json_data

        if isinstance(self._ATTRIBUTES, set):
            for name in self._ATTRIBUTES:
                setattr(self, name, self._data.get(name, None))
        elif isinstance(self._ATTRIBUTES, dict):
            for key, attributes in self._ATTRIBUTES.items():
                if isinstance(attributes, set):
                    for name in attributes:
                        try:
                            setattr(self, name, self._data.get(key).get(name, None))
                        except:
                            setattr(self, name, None)

        if isinstance(self._OBJECTS, dict):
            for name, data_class in self._OBJECTS.items():
                try:
                    setattr(self, name, data_class(self._data.get(name)))
                except:
                    setattr(self, name, None)


class IValues:
    """
    Class for storing various parameters and values
    """

    _ATTRIBUTES: set[str] = None
    """
    Attributes that can be stored in this class

    Example:
        _ATTRIBUTES = {"settings", "path"}
    """

    def __init__(self, **kwargs) -> None:
        for name in self._ATTRIBUTES:
            setattr(self, name, kwargs.get(name, None))

    def update(self, **kwargs) -> None:
        self.__init__(**kwargs)
