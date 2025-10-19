from __future__ import annotations

from typing import TYPE_CHECKING

from je_editor.pyside_ui.main_ui.menu.dock_menu.build_dock_menu import set_dock_menu
from je_editor.pyside_ui.main_ui.menu.language_menu.build_language_server import set_language_menu
from je_editor.pyside_ui.main_ui.menu.style_menu.build_style_menu import set_style_menu
from je_editor.pyside_ui.main_ui.menu.tab_menu.build_tab_menu import set_tab_menu
from je_editor.pyside_ui.main_ui.menu.text_menu.build_text_menu import set_text_menu
from je_editor.utils.logging.loggin_instance import jeditor_logger

if TYPE_CHECKING:
    from je_editor.pyside_ui.main_ui.main_editor import EditorMain
from PySide6.QtWidgets import QMenuBar

from je_editor.pyside_ui.main_ui.menu.check_style_menu.build_check_style_menu import set_check_menu
from je_editor.pyside_ui.main_ui.menu.file_menu.build_file_menu import set_file_menu
from je_editor.pyside_ui.main_ui.menu.help_menu.build_help_menu import set_help_menu
from je_editor.pyside_ui.main_ui.menu.run_menu.build_run_menu import set_run_menu
from je_editor.pyside_ui.main_ui.menu.python_env_menu.build_venv_menu import set_venv_menu


def set_menu_bar(ui_we_want_to_set: EditorMain) -> None:
    jeditor_logger.info(f"set_menu_bar.py set_menu_bar ui_we_want_to_set: {ui_we_want_to_set}")
    # set menu
    ui_we_want_to_set.menu = QMenuBar()
    set_file_menu(ui_we_want_to_set)
    set_run_menu(ui_we_want_to_set)
    set_text_menu(ui_we_want_to_set)
    set_check_menu(ui_we_want_to_set)
    set_help_menu(ui_we_want_to_set)
    set_venv_menu(ui_we_want_to_set)
    set_tab_menu(ui_we_want_to_set)
    set_dock_menu(ui_we_want_to_set)
    set_style_menu(ui_we_want_to_set)
    set_language_menu(ui_we_want_to_set)
    ui_we_want_to_set.setMenuBar(ui_we_want_to_set.menu)
