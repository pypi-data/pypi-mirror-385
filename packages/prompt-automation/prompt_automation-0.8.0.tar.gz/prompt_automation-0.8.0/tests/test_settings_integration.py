import json
from types import SimpleNamespace

from prompt_automation.variables import storage
from prompt_automation.hotkeys.base import HotkeyManager


def test_settings_global_reference_file_merges(monkeypatch, tmp_path):
    # Patch settings + overrides paths
    settings_dir = tmp_path / 'prompts' / 'styles' / 'Settings'
    settings_dir.mkdir(parents=True)
    settings_file = settings_dir / 'settings.json'
    overrides_file = tmp_path / 'placeholder-overrides.json'
    monkeypatch.setattr(storage, '_SETTINGS_DIR', settings_dir, raising=False)
    monkeypatch.setattr(storage, '_SETTINGS_FILE', settings_file, raising=False)
    monkeypatch.setattr(storage, '_PERSIST_FILE', overrides_file, raising=False)

    # Write settings with global_files.reference_file
    ref = tmp_path / 'ref.txt'
    ref.write_text('hello')
    settings_file.write_text(json.dumps({'global_files': {'reference_file': str(ref)}}))

    from prompt_automation.variables.files import get_global_reference_file
    # Should pick up from settings even though overrides file absent
    assert get_global_reference_file() == str(ref)


def test_settings_hotkey_default(monkeypatch, tmp_path):
    settings_dir = tmp_path / 'prompts' / 'styles' / 'Settings'
    settings_dir.mkdir(parents=True)
    settings_file = settings_dir / 'settings.json'
    settings_file.write_text(json.dumps({'hotkey': 'alt+shift+p'}))

    from prompt_automation.variables import storage as st
    monkeypatch.setattr(st, '_SETTINGS_DIR', settings_dir, raising=False)
    monkeypatch.setattr(st, '_SETTINGS_FILE', settings_file, raising=False)

    # Ensure no local hotkey file exists
    monkeypatch.setattr('prompt_automation.hotkeys.base.HOTKEY_FILE', tmp_path / 'hotkey.json', raising=False)

    hk = HotkeyManager.get_current_hotkey()
    assert hk == 'alt+shift+p'


def test_use_mcp_server_round_trip(monkeypatch, tmp_path):
    settings_dir = tmp_path / 'prompts' / 'styles' / 'Settings'
    settings_dir.mkdir(parents=True)
    settings_file = settings_dir / 'settings.json'

    monkeypatch.setattr(storage, '_SETTINGS_DIR', settings_dir, raising=False)
    monkeypatch.setattr(storage, '_SETTINGS_FILE', settings_file, raising=False)

    assert storage.get_use_mcp_server() is False

    storage.set_use_mcp_server(True)
    assert storage.get_use_mcp_server() is True

    payload = json.loads(settings_file.read_text())
    assert payload['use_mcp_server'] is True

    storage.set_use_mcp_server(False)
    assert storage.get_use_mcp_server() is False


def test_settings_panel_checkbox_invokes_use_mcp_server(monkeypatch):
    from prompt_automation.gui import settings_panel

    class DummyBooleanVar:
        def __init__(self, value=False):
            self._value = value

        def get(self):
            return self._value

        def set(self, value):
            self._value = value

    class DummyWidget:
        def __init__(self, *_, **kwargs):
            self.command = kwargs.get('command')
            self.variable = kwargs.get('variable')
            self.text = kwargs.get('text')

        def pack(self, *_, **__):
            return self

    class DummyFrame(DummyWidget):
        pass

    class DummyToplevel(DummyWidget):
        def __init__(self, *_, **__):
            pass

        def title(self, *_):
            return None

        def resizable(self, *_):
            return None

        def destroy(self):
            return None

    class DummyOptionMenu(DummyWidget):
        def __init__(self, *_, **__):
            pass

    class DummyCheckbutton(DummyWidget):
        instances = []

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.pack_kwargs = None
            DummyCheckbutton.instances.append(self)

        def pack(self, *_, **kwargs):
            self.pack_kwargs = kwargs
            return self

        def invoke(self):
            if self.command:
                self.command()

    class DummyStringVar:
        def __init__(self, value=None):
            self._value = value

        def get(self):
            return self._value

        def set(self, value):
            self._value = value

    dummy_module = SimpleNamespace(
        BooleanVar=DummyBooleanVar,
        Button=DummyWidget,
        Checkbutton=DummyCheckbutton,
        Frame=DummyFrame,
        Label=DummyWidget,
        OptionMenu=DummyOptionMenu,
        StringVar=DummyStringVar,
        Toplevel=DummyToplevel,
    )

    monkeypatch.setattr(settings_panel, 'tk', dummy_module, raising=False)
    monkeypatch.setattr(settings_panel, '_refresh_hotkey', lambda: None, raising=False)

    monkeypatch.setattr(settings_panel.storage, 'get_background_hotkey_enabled', lambda: False)
    monkeypatch.setattr(settings_panel.storage, 'get_espanso_enabled', lambda: False)
    monkeypatch.setattr(settings_panel.storage, 'get_use_mcp_server', lambda: False)
    monkeypatch.setattr(settings_panel.storage, 'get_mcp_debug_mode', lambda: 'off')
    monkeypatch.setattr(settings_panel.storage, 'set_background_hotkey_enabled', lambda value: None)
    monkeypatch.setattr(settings_panel.storage, 'set_espanso_enabled', lambda value: None)
    monkeypatch.setattr(settings_panel.storage, 'set_mcp_debug_mode', lambda value: None)

    toggled = []

    def fake_set_use_mcp_server(value):
        toggled.append(value)

    monkeypatch.setattr(settings_panel.storage, 'set_use_mcp_server', fake_set_use_mcp_server)
    monkeypatch.setattr(settings_panel, 'is_mcp_observability_enabled', lambda: False, raising=False)
    monkeypatch.setattr(settings_panel, 'is_mcp_enabled', lambda: False, raising=False)

    DummyCheckbutton.instances = []

    settings_panel.open_settings_panel(object())

    # Last created Checkbutton corresponds to MCP server toggle
    cb = DummyCheckbutton.instances[-1]
    assert cb.text == "Use MCP server integration"

    # Simulate user enabling the checkbox
    cb.variable.set(True)
    cb.invoke()

    assert toggled == [True]
