from __future__ import annotations
import typing
import waitress, flask


class ILocalhostFlask(flask.Flask):
    """
    Class for creating a simple localhost server
    """

    _RULES: dict[str, typing.Callable]
    """
    Dictionary with rules and functions
    
    Example:
        _RULES = {"/": base_redirect}
    """

    def __init__(self, import_name: str) -> None:
        super().__init__(import_name)

        for rule, view_func in self._RULES.items():
            self.add_url_rule(
                rule=rule,
                view_func=view_func,
            )

    def serve(self, port: int) -> None:
        """
        Starts this Flask application
        """

        waitress.serve(
            app=self,
            host="127.0.0.1",
            port=port,
        )
