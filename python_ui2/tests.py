import unittest

from braille_ui import Event, Input, Mode, LessonState, build_sim_device, text_to_cells


class TestBraille(unittest.TestCase):

    def test_patterns(self):
        self.assertEqual(text_to_cells("a"), [1])
        self.assertEqual(text_to_cells("c"), [9])
        self.assertEqual(text_to_cells(" "), [0])


class TestMenu(unittest.TestCase):

    def test_menu_navigation(self):
        dev = build_sim_device()

        self.assertEqual(dev.mode, Mode.MENU)
        self.assertEqual(dev.selection, 0)

        dev.handle(Event(Input.FORWARD))
        self.assertEqual(dev.selection, 1)

    def test_open_lesson(self):
        dev = build_sim_device()

        dev.handle(Event(Input.MIC))

        self.assertEqual(dev.mode, Mode.LESSON)
        self.assertEqual(dev.state, LessonState.PRESENT)


class TestLesson(unittest.TestCase):

    def test_correct_answer(self):
        dev = build_sim_device()

        dev.handle(Event(Input.MIC))
        dev.handle(Event(Input.MIC))
        dev.handle(Event(Input.SPEECH, payload="cab"))

        self.assertEqual(dev.score, 1)
        self.assertEqual(dev.word_index, 1)

    def test_wrong_answer(self):
        dev = build_sim_device()

        dev.handle(Event(Input.MIC))
        dev.handle(Event(Input.MIC))
        dev.handle(Event(Input.SPEECH, payload="xyz"))

        self.assertEqual(dev.attempts, 1)
        self.assertEqual(dev.word_index, 0)

    def test_lesson_completion(self):
        dev = build_sim_device()

        dev.handle(Event(Input.MIC))

        for word in ["cab", "bad"]:
            dev.handle(Event(Input.MIC))
            dev.handle(Event(Input.SPEECH, payload=word))

        self.assertEqual(dev.mode, Mode.MENU)


class TestReader(unittest.TestCase):

    def test_reader_scroll(self):
        dev = build_sim_device()

        # Navigate to Story.
        dev.handle(Event(Input.FORWARD))
        dev.handle(Event(Input.FORWARD))
        dev.handle(Event(Input.MIC))

        self.assertEqual(dev.mode, Mode.READER)

        dev.handle(Event(Input.DIAL, 2))
        self.assertEqual(dev.reader_position, 2)

        dev.handle(Event(Input.BACKWARD))
        self.assertEqual(dev.mode, Mode.MENU)


if __name__ == "__main__":
    unittest.main()
