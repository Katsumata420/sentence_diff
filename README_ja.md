# Sentence Differences - sentence_diff
Package to difference ~~English~~ **Japanese** sentences via Liechtenstein distance, calculate word error rate, and list out word by word differences.

# Basic usage
- `SentenceDiff(error_senntece, reference_sentence)`

```python

from sentence_diff import SentenceDiff

d = SentenceDiff("これ は ものすごい 誤り 分 です 。", "これ は ものすごい 正解 文 です 。")
assert d.mistakes() == [
  ('誤り', '正解', 3, 'rep'),
  ('分', '文', 4, 'rep')]

```

### Word Error Rate - wer()

```python
d = SentenceDiff("まっ て くもっ て 理不尽 です 。", "まったくもって 理不尽 です 。")
assert d.wer() == 0.5
```

### Changes - mistakes()

Added words
```python
d = SentenceDiff("りんご 好き", "りんご が とても 好き")
assert d.mistakes() == [
(None, 'が', 1, 'ins'),
(None, 'とても', 1, 'ins')]
```

Changed words 
```python
d = SentenceDiff("りんご が 食べ る", "りんご を 食べ る")
assert d.mistakes() == [
("が", "を", 1, 'rep')]
```

Skipped words
```python
d = SentenceDiff("私 は は りんご を 食べ る", "私 は りんご を 食べ る")
assert d.mistakes() == [
('は', None, 2, 'del')]
```

No differences (ignores punctuation and case)
```python
d = SentenceDiff("こんにちは 、 よろしく", "こんにちは 、 よろしく")
assert d.mistakes() == []
```

### 誤った単語抽出（False） - yes_no_words()

```python
d = SentenceDiff("これ に ものすごい 誤り 分 でし た 。", "これ は ものすごい 正解 文 です 。")
assert d.yes_no_words() == [
("これ", True),
("に", False),
("ものすごい", True),
("誤り", False),
("分", False),
("でし", False),
("た", False),
("。", True)]
```
