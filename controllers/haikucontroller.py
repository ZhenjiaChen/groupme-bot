import json
from string import punctuation
import traceback


class HaikuController:
    SYLLABLE_DICTIONARY_PATH = "syllables.json"
    PUNCTUATIONS = punctuation[0:6] + punctuation[7:]

    def __init__(self, user_name=None, message=None, verbose=False) -> None:
        self.syllable_dictionary = self.loadDictFromFile(self.SYLLABLE_DICTIONARY_PATH)
        self.user_name = user_name or ''
        self.message = message or ''
        self.verbose = verbose

    def loadDictFromFile(self, path):
        """
        Load json file
        """
        dictionary = {}
        with open(path) as file:
            data = file.read()
            dictionary = json.loads(data)
        return dictionary

    def saveDictToFile(self, dictionary):
        """
        Saves a Python dictionary to local json file
        """
        with open(self.SYLLABLE_DICTIONARY_PATH, "w") as file:
            file.write(json.dumps(dictionary))

    def memorize(self, word, syllables):
        self.syllable_dictionary[word] = syllables
        self.saveDictToFile(self.SYLLABLE_DICTIONARY_PATH, self.syllable_dictionary)
        return self.syllable_dictionary

    def syllables(self, word):
        """
        Returns number of syllables in a word

        First checks if word is memoized in json file before requesting from
        """
        try:
            # Removes punctuation and lowercases word
            lower = word.replace(
                u"\u2019", "'"
            ).replace(
                u"\u2018", "'"
            ).translate(
                str.maketrans("", "", self.PUNCTUATIONS)
            ).lower()
            # word is in json file
            if syllables := self.syllable_dictionary.get(lower):
                print(f'{word}: {syllables}') if self.verbose else None
                return syllables

        except Exception:
            print(f'Error retrieving syllables for {word}. {traceback.format_exc()}')
        return None

    def is_haiku(self):
        """
        Returns true if text is a haiku
        """
        if not self.message:
            return False
        total_syllable_count = 0
        has_valid_line_1 = False
        has_valid_line_2 = False
        has_valid_line_3 = False
        text_tokens = self.message.split()
        if len(text_tokens) > 17:
            return False

        for word in text_tokens:
            if (syllables_count := self.syllables(word)) is None:
                return False
            total_syllable_count += syllables_count
            if total_syllable_count == 5:
                has_valid_line_1 = True
            elif total_syllable_count > 5 and not has_valid_line_1:
                return False
            elif total_syllable_count == 12:
                has_valid_line_2 = True
            elif total_syllable_count > 12 and not has_valid_line_2:
                return False
            elif total_syllable_count == 17:
                has_valid_line_3 = True
            elif total_syllable_count > 17:
                return False
        return has_valid_line_1 and has_valid_line_2 and has_valid_line_3

    def capitalize(self, word):
        first_letter = word[0].capitalize()
        rest = word[1:]
        return f'{first_letter}{rest}'

    def format_haiku(self):
        """
        Formats haiku
        """
        line1 = []
        line2 = []
        line3 = []
        syllable_count = 0
        originalcase = self.message.split()
        lowercase = self.message.translate(str.maketrans("", "", self.PUNCTUATIONS)).lower().split()

        for i in range(len(lowercase)):
            syllable_count += self.syllables(lowercase[i])
            if syllable_count <= 5:
                if len(line1) == 0:
                    line1.append(self.capitalize(originalcase[i]))
                else:
                    line1.append(originalcase[i])
            elif syllable_count <= 12:
                if len(line2) == 0:
                    line2.append(self.capitalize(originalcase[i]))
                else:
                    line2.append(originalcase[i])
            elif syllable_count <= 17:
                if len(line3) == 0:
                    line3.append(self.capitalize(originalcase[i]))
                else:
                    line3.append(originalcase[i])
        lines = [' '.join(line) for line in [line1, line2, line3]]
        return '\n'.join(lines)

    def get_response_message(self):
        if not self.is_haiku():
            return None

        haiku = self.format_haiku()
        return f'{haiku}\n\n                      -{self.user_name}'
