def insert_bible_text(event=None):
    from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
    from biblemate.uba.api import run_uba_api
    from biblemate import config

    buffer = event.app.current_buffer if event is not None else text_field.buffer
    selectedText = buffer.copy_selection().text
    references = BibleVerseParser(False).extractAllReferencesReadable(selectedText)
    bible_text = run_uba_api(f"BIBLE:::{config.default_bible}:::{references}")
    buffer.insert_text(format_assistant_content(bible_text))
    get_app().reset()
