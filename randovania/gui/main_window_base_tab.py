from randovania.interface_common.user_preferences import UserPreferences


class MainWindowBaseTab:
    _user_preferences: UserPreferences

    @property
    def user_preferences(self):
        return self._user_preferences

    @user_preferences.setter
    def user_preferences(self, value: UserPreferences):
        self._user_preferences = value
        self.on_user_preferences_changed()

    def on_user_preferences_changed(self):
        raise NotImplementedError()
