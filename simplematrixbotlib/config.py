from dataclasses import dataclass, field, fields, asdict
import toml
import re
from typing import Set, Union


def _config_dict_factory(tmp) -> dict:
    return {
        'simplematrixbotlib': {
            'config':
            {_strip_leading_underscore(name): value
             for name, value in tmp}
        }
    }


def _strip_leading_underscore(tmp: str) -> str:
    return tmp[1:] if tmp[0] == '_' else tmp


@dataclass
class Config:
    _join_on_invite: bool = True
    _allowlist: Set[re.Pattern] = field(
        default_factory=set)  # TODO: default to bot's homeserver
    _blocklist: Set[re.Pattern] = field(default_factory=set)

    def _check_set_regex(self,
                         value: Set[str]) -> Union[Set[re.Pattern], None]:
        new_list = set()
        for v in value:
            try:
                tmp = re.compile(v)
            except re.error:
                print(
                    f"{v} is not a valid regular expression. Ignoring your list update."
                )
                return None
            new_list.add(tmp)
        return new_list

    def _load_config_dict(self, config_dict: dict) -> None:
        # TODO: make this into a factory, so defaults can be set based on loaded values?
        # e.g. emoji_verify should default to enabled when encryption_enabled
        existing_fields = [
            _strip_leading_underscore(f.name) for f in fields(self)
        ]
        for key, value in config_dict.items():
            if key not in existing_fields:
                continue
            setattr(self, key, value)

    def load_toml(self, file_path: str) -> None:
        with open(file_path, 'r') as file:
            config_dict: dict = toml.load(file)['simplematrixbotlib']['config']
            self._load_config_dict(config_dict)

    def save_toml(self, file_path: str) -> None:
        tmp = asdict(self, dict_factory=_config_dict_factory)
        with open(file_path, 'w') as file:
            toml.dump(tmp, file)

    @property
    def join_on_invite(self) -> bool:
        """
        Returns
        -------
        boolean
            Whether the bot is configured to automatically accept all invites it receives
        """
        return self._join_on_invite

    @join_on_invite.setter
    def join_on_invite(self, value: bool) -> None:
        self._join_on_invite = value

    @property
    def allowlist(self) -> Set[re.Pattern]:
        """
        Returns
        -------
        Set[re.Pattern]
            A set of regular expressions matching Matrix IDs.
            Can be used in conjunction with blocklist to check if the sender is allowed to issue a command to the bot.
            An empty set implies that everyone is allowed.
        """
        return self._allowlist

    @allowlist.setter
    def allowlist(self, value: Set[str]) -> None:
        checked = self._check_set_regex(value)
        if checked is None:
            return
        self._allowlist = checked

    def add_allowlist(self, value: Set[str]) -> None:
        """
        Parameters
        ----------
        value : Set[str]
            A set of strings which represent Matrix IDs or a regular expression matching Matrix IDs to be added to allowlist.
        """
        checked = self._check_set_regex(value)
        if checked is None:
            return
        self._allowlist = self._allowlist.union(checked)

    def remove_allowlist(self, value: Set[str]) -> None:
        """
        Parameters
        ----------
        value : Set[str]
            A set of strings which represent Matrix IDs or a regular expression matching Matrix IDs to be removed from allowlist.
        """
        checked = self._check_set_regex(value)
        if checked is None:
            return
        self._allowlist = self._allowlist - checked

    @property
    def blocklist(self) -> Set[re.Pattern]:
        """
        Returns
        -------
        Set[re.Pattern]
            A set of regular expressions matching Matrix IDs.
            Can be used in conjunction with allowlist to check if the sender is disallowed to issue a command to the bot.
        """
        return self._blocklist

    @blocklist.setter
    def blocklist(self, value: Set[str]) -> None:
        checked = self._check_set_regex(value)
        if checked is None:
            return
        self._blocklist = checked

    def add_blocklist(self, value: Set[str]) -> None:
        """
        Parameters
        ----------
        value : Set[str]
            A set of strings which represent Matrix IDs or a regular expression matching Matrix IDs to be added to blocklist.
        """
        checked = self._check_set_regex(value)
        if checked is None:
            return
        self._blocklist = self._blocklist.union(checked)

    def remove_blocklist(self, value: Set[str]) -> None:
        """
        Parameters
        ----------
        value : Set[str]
            A set of strings which represent Matrix IDs or a regular expression matching Matrix IDs to be removed from blocklist.
        """
        checked = self._check_set_regex(value)
        if checked is None:
            return
        self._blocklist = self._blocklist - checked
