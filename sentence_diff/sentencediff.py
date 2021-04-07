"""
compare
backtrace
"""
import numpy as np


class SentenceDiff:

    def __init__(self, actual_sentence, target_sentence):
        self._assert_not_empty(actual_sentence, target_sentence)
        # lowercase, normalize, tokenize
        self.actual_sentence = actual_sentence
        self.actual = self._tokenize(actual_sentence)
        self.target = self._tokenize(target_sentence)

    def wer(self):
        self._compare()
        return self.error

    def get_scored_words(self):
        self._compare()
        self._backtrace()
        return self.scored_words

    def mistakes(self):
        self._compare()
        self._backtrace()
        return [tupl for tupl in self.scored_words if tupl[3]]

    def yes_no_words(self):
        self._compare()
        self._backtrace()
        res = []
        for scored in self.scored_words:
            if scored[0]:
                res.append((scored[0], scored[3] is None))
        return res

    def print_debug(self):
        self._compare()
        self._backtrace()
        print("actual")
        print(self.actual)
        print("target")
        print(self.target)
        print("wer")
        print(self.error)
        # print(self.matrix)
        # print(self.path)
        print(self.alignment)
        print("")
        print(self.scored_words)
        print("")
        # print(self.insertions)
        # print(self.deletions)
        # print(self.substitutions)

    def _init_matrix(self, actual, target):
        # initialize the matrix per levenshtein distance
        shape = (len(target) + 1, len(actual) + 1)
        matrix = np.zeros(shape, dtype=np.uint32)
        matrix[0, :] = np.arange(shape[1])
        matrix[:, 0] = np.arange(shape[0])
        return matrix

    def _compare(self):
        wer, matrix = self._do_compare(self.actual, self.target)
        self.error = wer
        self.matrix = matrix

    def _do_compare(self, actual, target):
        matrix = self._init_matrix(actual, target)
        for trgt_pos, rw in enumerate(target):
            for actual_pos, hw in enumerate(actual):
                insert = matrix[trgt_pos + 1, actual_pos] + 1
                delete = matrix[trgt_pos, actual_pos + 1] + 1
                if rw != hw:
                    subst = matrix[trgt_pos, actual_pos] + 1
                else:
                    subst = matrix[trgt_pos, actual_pos]

                best = min(insert, delete, subst)
                matrix[trgt_pos + 1, actual_pos + 1] = best

        cost = matrix[-1, -1]
        if len(target) == 0:
            return 1
        wer = cost / len(target)
        return wer, matrix

    def _do_backtrace(self, actuals, targets, matrix, safe_mode_target=False,
                      safe_mode_actual=False):
        current_target_pos = len(targets) - 1
        current_actual_pos = len(actuals) - 1

        alignment = []
        path = []
        inserts = 0
        deletions = 0
        substitns = 0
        matched = 0

        while current_target_pos >= 0 or current_actual_pos >= 0:
            path.append((current_target_pos + 1, current_actual_pos + 1))
            start = matrix[current_target_pos + 1, current_actual_pos + 1]
            insert = matrix[current_target_pos + 1, current_actual_pos]
            delete = matrix[current_target_pos, current_actual_pos + 1]
            subst = matrix[current_target_pos, current_actual_pos]
            best = min(start, subst)

            # target position や actual position がマイナスになった際は、
            # 操作に制約をかける
            ## target position がマイナス: insert のみ
            """
            if current_target_pos < 0:
                return self._do_backtrace(actuals, targets, matrix,
                                          safe_mode_target=True)
            if current_actual_pos < 0:
                return self._do_backtrace(actuals, targets, matrix,
                                          safe_mode_actual=True)
            """

            if insert < best or (current_target_pos < 0 and insert == best):
                alignment.append((None, actuals[current_actual_pos]))
                inserts += 1
                current_actual_pos -= 1

            elif delete < best or (current_actual_pos < 0 and delete == best):
                alignment.append((targets[current_target_pos], None))
                deletions += 1
                current_target_pos -= 1

            else:
                if start == subst:  # no change
                    matched += 1
                else:
                    substitns += 1

                alignment.append((targets[current_target_pos],
                                  actuals[current_actual_pos]))
                current_target_pos -= 1
                current_actual_pos -= 1

        alignment.reverse()
        path.reverse()
        scored_words = []

        # the index returned in scored_words is relative to the *actual* sentence
        # but we need to keep track of both so we can look up the un-messed-with form of word
        a_idx = 0
        t_idx = 0
        for pair in alignment:

            if pair[0] == pair[1]:
                actual = actuals[a_idx]
                target = targets[t_idx]
                scored_words.append((actual, target, a_idx, None))
                a_idx += 1
                t_idx += 1

            elif pair[0] is None:
                actual = actuals[a_idx]
                scored_words.append((actual, None, a_idx, "del"))
                a_idx += 1

            elif pair[1] is None:
                target = targets[t_idx]
                scored_words.append((None, target, a_idx, "ins"))
                t_idx += 1

            else:

                actual = actuals[a_idx]
                target = targets[t_idx]
                scored_words.append((actual, target, a_idx, "rep"))
                a_idx += 1
                t_idx += 1

        return scored_words, alignment

    def _backtrace(self):
        scored_words, alignment =\
            self._do_backtrace(self.actual, self.target, self.matrix)
        self.scored_words = scored_words
        self.alignment = alignment

    def _tokenize(self, sentence):
        # tokenize with white space
        words = sentence.split()
        return words

    @staticmethod
    def _assert_not_empty(actual_sentence, target_sentence):
        assert target_sentence is not None
        assert actual_sentence is not None
        t = len(target_sentence)
        a = len(actual_sentence)
        if t == 0 or a == 0\
           and a == t:
            raise Exception("cannot compare empty sentences")
