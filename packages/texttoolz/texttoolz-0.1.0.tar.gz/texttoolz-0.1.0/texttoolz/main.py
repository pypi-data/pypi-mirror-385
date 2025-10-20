import re
import string

# Count Vowels
def count_vowels(text):
    vowels = 'aiueoAIUEO'
    return sum(1 for char in text if char in vowels)

# print(count_vowels('Good Morning'))

def reverse_word(text):
    words = text.split()
    reversed = []

    for word in words:
        rev_word = word[::-1]
        reversed.append(rev_word)

    result = ' '.join(reversed)
    return result

# print(reverse_word('Happy Birthday !!!'))

def remove_punctuation(text):
    # ?!_%^$#
    punctuation = string.punctuation
    cleaned_text = ""

    for char in text:
        if char not in punctuation:
            cleaned_text += char

    return cleaned_text

# print(remove_punctuation('Goodbye World !!'))

def word_count(text):
    words = text.split()
    count = len(words)
    return count

# print(word_count('Hello World'))