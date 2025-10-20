import string
from collections import Counter
import re

def count_vowels(text):
    vowels = "aeiouAEIOU"
    return sum(1 for char in text if char in vowels)

def count_consonants(text):
    vowels = "aeiouAEIOU"
    return sum(1 for char in text if char.isalpha() and char not in vowels)

def is_palindrome(text):
    cleaned = ''.join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]

def word_frequency(text):
    words = [w.strip(string.punctuation).lower() for w in text.split()]
    return dict(Counter(words))

def longest_word(text):
    words = text.split()
    return max(words, key=len, default="")

def shortest_word(text):
    words = text.split()
    return min(words, key=len, default="")

def average_word_length(text):
    words = text.split()
    return sum(len(w) for w in words)/len(words) if words else 0

def count_sentences(text):
    return sum(text.count(c) for c in ".!?")

def most_common_word(text):
    freq = word_frequency(text)
    if freq:
        return max(freq, key=freq.get)
    return ""

def least_common_word(text):
    freq = word_frequency(text)
    if freq:
        return min(freq, key=freq.get)
    return ""

def count_numeric(text):
    return sum(1 for c in text if c.isdigit())

def count_uppercase(text):
    return sum(1 for c in text if c.isupper())

def count_lowercase(text):
    return sum(1 for c in text if c.islower())

def count_whitespace(text):
    return sum(1 for c in text if c.isspace())

def contains_word(text, word):
    return word.lower() in [w.strip(string.punctuation).lower() for w in text.split()]

def unique_words(text):
    words = [w.strip(string.punctuation).lower() for w in text.split()]
    return [w for w in set(words) if words.count(w) == 1]

def count_punctuation(text):
    return sum(1 for c in text if c in string.punctuation)

def sentence_lengths(text):
    sentences = re.split(r'[.!?]+', text)
    return [len(s.split()) for s in sentences if s.strip()]

def words_starting_with(text, char):
    char = char.lower()
    return [w for w in text.split() if w.lower().startswith(char)]

def words_ending_with(text, char):
    char = char.lower()
    return [w for w in text.split() if w.lower().endswith(char)]
