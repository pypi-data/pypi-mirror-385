import re
import string

# Count Vowels
def count_vowels(text):
    vowels = 'aiueoAIUEO'
    return sum(1 for char in text if char in vowels)

# word = 'Good Morning'
# print(count_vowels(word))

# reverse word
def reverse_word(text):
    words = text.split()
    reversed = []

    for word in words:
        rev_word = word[::-1]
        reversed.append(rev_word)

    result = ' '.join(reversed)
    return result

# word = 'Happy Birthday !!!'
# print(reverse_word(word))

# Remove punctuation
def remove_punctuation(text):
    # ?!_%^$#
    punctuation = string.punctuation
    cleaned_text = ""

    for char in text:
        if char not in punctuation:
            cleaned_text += char

    return cleaned_text

# word = 'Goodbye World !!'
# print(remove_punctuation(word))

# word count
def word_count(text):
    words = text.split()
    count = len(words)
    return count

# word = 'Hello world'
# print(word_count(word))

# char frequency
def char_frequency(text):
    freq = {}
    for char in text:
        if char != ' ':
            freq[char] = freq.get(char, 0) + 1
    return freq

# word  = 'Hello World !!!'
# print(char_frequency(word) )

# Capitalize Senteces
def capitalize_sentences(text):
    # Get text after punctuation
    sentences = re.split(r'(?<=[.!?]) +', text)
    return ' '.join(s.capitalize() for s in sentences)

# word = 'hello, good morning. my name is evan'
# print(capitalize_sentences(word))

def extract_emails(text):
    return re.findall(r'[\w\.-]+@[\w\.-]+', text)

# word = 'Here is my email. evan@amazon.com'
# print(extract_emails(word))

def remove_number(text):
    cleaned_text = ''
    for char in text:
        if not char.isdigit():
            cleaned_text += char
    return cleaned_text

# word = 'I live in 22th elm street'
# print(remove_number(word))