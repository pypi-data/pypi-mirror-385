import unittest
from eldar_string_utils.analysis import (
    count_vowels, count_consonants, is_palindrome,
    word_frequency, longest_word, shortest_word
)

class TestAnalysis(unittest.TestCase):

    def test_count_vowels(self):
        self.assertEqual(count_vowels('Hello World'), 3)

    def test_count_consonants(self):
        self.assertEqual(count_consonants('Hello World'), 7)

    def test_is_palindrome(self):
        self.assertTrue(is_palindrome('madam'))
        self.assertFalse(is_palindrome('hello'))

    def test_word_frequency(self):
        self.assertEqual(word_frequency('Hello hello world'), {'hello': 2, 'world': 1})

    def test_longest_word(self):
        self.assertEqual(longest_word('I love programming'), 'programming')

    def test_shortest_word(self):
        self.assertEqual(shortest_word('I love programming'), 'I')

if __name__ == '__main__':
    unittest.main()
