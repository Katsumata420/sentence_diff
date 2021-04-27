from unittest import TestCase
from sentence_diff import SentenceDiff


def diff(actual_sentence, target_sentence):
    return SentenceDiff(actual_sentence=actual_sentence, target_sentence=target_sentence)

class TestDifferencer(TestCase):

    def test_x_v_y_wer(self):
        d = diff("私 は りんご を 食べ る", "私 は は りんご を 食べ る")
        assert d.wer() == 1/7

    def test_y_v_x_wer(self):
        d = diff("私 は は りんご を 食べ る", "私 は りんご を 食べ る")
        assert d.wer() == 1/6

    def test_words_del(self):
        d = diff("私 は は りんご を 食べ る", "私 は りんご を 食べ る")
        assert d.mistakes() == [
        ("は", None, 2,'del')]

    def test_words_rep(self):
        d = diff("りんご が 食べ る", "りんご を 食べ る")
        assert d.mistakes() == [
        ("が", "を", 1, 'rep')]

    def test_words_ins(self):
        d = diff("りんご 好き", "りんご が とても 好き")
        assert d.mistakes() == [
        (None, "が", 1, 'ins'),
        (None, "とても", 1, 'ins')]

    def test_combined(self):
        d = diff("これ に ものすごい 誤り 分 でし た 。",\
            "これ は ものすごい 正解 文 です 。")
        assert d.mistakes() == \
            [('に', 'は', 1, 'rep'),
            ('誤り', None, 3, 'del'),
            ('分', '正解', 4, 'rep'),
            ('でし', '文', 5, 'rep'),
            ('た', 'です', 6, 'rep')]

    def test_no_mistakes(self):
        d = diff("こんにちは 、 よろしく", "こんにちは 、 よろしく")
        assert d.mistakes() == []

    def test_yes_no_words(self):
        d = diff("これ に ものすごい 誤り 分 でし た 。",\
            "これ は ものすごい 正解 文 です 。")
        assert d.yes_no_words() == [
        ("これ", True),
        ("に", False),
        ("ものすごい", True),
        ("誤り", False),
        ("分", False),
        ("でし", False),
        ("た", False),
        ("。", True)]

    def test_scored_words(self):
        d = diff("これ に ものすごい 誤り 分 でし た 。",\
            "これ は ものすごい 正解 文 です 。")
        assert d.get_scored_words() == [
        ('これ', 'これ', 0, None),
        ('に', 'は', 1, 'rep'),
        ('ものすごい', 'ものすごい', 2, None),
        ('誤り', None, 3, 'del'),
        ('分', '正解', 4, 'rep'),
        ('でし', '文', 5, 'rep'),
        ('た', 'です', 6, 'rep'),
        ('。', '。', 7, None)]

    def test_backtrace_ex(self):
        d = diff("こんにちは", "これ は ものすごい 正解 文 です 。")
        assert d.wer() == 1

    def test_ex_miss_mary(self):
        d = diff("こんにちは 、 よろしく", "こんにちは 、 よろしく")
        assert d.wer() == 0

    def test_i_want_water(self):
        actual = "私 は りんご が 好き"
        target = "私 は 好き"
        d = diff(actual, target)
        assert d.yes_no_words() ==[
            ('私', True), 
            ('は', True), 
            ('りんご', False), 
            ('が', False),
            ('好き', True)]

