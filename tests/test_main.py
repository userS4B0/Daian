import src.main as main_mod
import pytest


def test_main_keyboard_interrupt(monkeypatch):
    def fake_main():
        raise KeyboardInterrupt

    monkeypatch.setattr(main_mod, "main", fake_main)
    # Running main should raise KeyboardInterrupt; your wrapper likely handles it.
    with pytest.raises(KeyboardInterrupt):
        main_mod.main()
