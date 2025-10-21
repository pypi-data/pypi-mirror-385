"""The definition of alliteration that we use here is the repetition
of word-initial consonants or consonant clusters.
"""

from poetry_analysis.utils import normalize


def count_alliteration(text: str) -> dict:
    """Count the number of times the same word-initial letter occurs in a text.

    Examples:
        >>> text = "Sirius som seer"
        >>> count_alliteration(text)
        {'s': 3}
    """
    words = text.split()
    initial_counts = {}

    for word in words:
        initial_letter = word[0].lower()
        if initial_letter in initial_counts:
            initial_counts[initial_letter] += 1
        else:
            initial_counts[initial_letter] = 1

    alliteration_count = {letter: count for letter, count in initial_counts.items() if count > 1}

    return alliteration_count


def extract_alliteration(text: list[str]) -> list[dict]:
    """Extract words that start with the same letter from a text.

    NB! This function is case-insensitive and compares e.g. S to s as the same letter.

    Args:
        text (list): A list of strings, where each string is a line of text.

    Examples:
        >>> text = ['Stjerneklare Septembernat Sees Sirius', 'Sydhimlens smukkeste Stjerne']
        >>> extract_alliteration(text)
        [{'line': 0, 'symbol': 's', 'count': 4, 'words': ['Stjerneklare', 'Septembernat', 'Sees', 'Sirius']}, {'line': 1, 'symbol': 's', 'count': 3, 'words': ['Sydhimlens', 'smukkeste', 'Stjerne']}]
    """

    alliterations = []

    for i, line in enumerate(text):
        words = line.split() if isinstance(line, str) else line
        seen = {}
        for j, word in enumerate(words):
            initial_letter = word[0].lower()
            if not initial_letter.isalpha():
                continue

            if initial_letter in seen:
                seen[initial_letter].append(word)
            else:
                seen[initial_letter] = [word]

            if (j == len(words) - 1) and any(len(v) > 1 for v in seen.values()):
                alliteration_symbols = [k for k, v in seen.items() if len(v) > 1]
                for symbol in alliteration_symbols:
                    alliterations.append(
                        {
                            "line": i,
                            "symbol": symbol,
                            "count": len(seen[symbol]),
                            "words": seen[symbol],
                        }
                    )

    return alliterations


# New helper function to group indices considering stop words
def group_alliterating_word_indices(
    indices: list[int], all_words_in_line: list[str], stop_words: list[str]
) -> list[list[int]]:
    """
    Groups words that alliterate, allowing specified ``stop_words`` in between.

    Args:
        indices: Indides of alliterating words in the line.
        all_words_in_line: All words in the line.
        stop_words: Words allowed to intervene between alliterating words.

    Returns:
        list of groups, each group is a list of alliterating words,
            where allowed stop words may intervene between them.
    """
    if not indices:
        return []

    result_groups = []
    current_group_indices = [indices[0]]

    for i in range(1, len(indices)):
        prev_allit_idx = current_group_indices[-1]
        current_potential_idx = indices[i]

        can_extend_group = True
        # Check words between prev_allit_idx and current_potential_idx
        if current_potential_idx > prev_allit_idx + 1:
            for intervening_idx in range(prev_allit_idx + 1, current_potential_idx):
                if (
                    intervening_idx >= len(all_words_in_line)
                    or not all_words_in_line[intervening_idx]
                    or all_words_in_line[intervening_idx].lower() not in stop_words
                ):
                    can_extend_group = False
                    break

        if can_extend_group:
            current_group_indices.append(current_potential_idx)
        else:
            # Store group if it has at least 2 alliterating words
            if len(current_group_indices) >= 2:
                result_groups.append(list(current_group_indices))  # Store a copy
            current_group_indices = [current_potential_idx]

    # Add the last formed group if it's valid
    if len(current_group_indices) >= 2:
        result_groups.append(list(current_group_indices))

    alliteration_groups = [[all_words_in_line[i] for i in group_indices] for group_indices in result_groups]

    return alliteration_groups


def group_words_by_initial_letter(words: list[str], store_indices: bool = False) -> dict:
    """Iterate over a list of words and append the word or its position to a dict
    with the word-initial letter as the key.

    Args:
        words: List of word tokens (str).
        store_indices: If True, append the word position (int)
            in the word list to the output dictionary.

    Returns:
        dict: a dictionary with single letters as keys
             and lists of words beginning on the letters as the values.
    """
    seen = {}
    for i, word in enumerate(words):
        # Ensure word is not empty before accessing word_token[0]
        if (not word) or (not word[0].isalpha()):
            continue

        initial_letter = word[0].casefold()
        item = i if store_indices else word
        if initial_letter in seen:
            seen[initial_letter].append(item)
        else:
            seen[initial_letter] = [item]
    return seen


def find_line_alliterations(text: str, allowed_intervening_words: list | None = None) -> list:
    """Find alliterating words on a line.

    Args:
        text: A line of text with multiple tokens
        allowed_intervening_words: words that can occur between two alliterating words
            without breaking the alliteration effect. Defaults to "og", "i", and "er".
    Returns:
        list of lists of words that are alliterating
    """
    filler_words = ["og", "i", "er"] if allowed_intervening_words is None else allowed_intervening_words

    words = normalize(text)

    # Stores {initial_letter: [indices_of_words_starting_with_this_letter]}
    seen = group_words_by_initial_letter(words, store_indices=True)

    annotations = []
    # The following logic identifies all groups of words in the line that start with the same consonant,
    # treating them as alliterations if the initial letter appears more than once and grouping them
    # while allowing certain intervening words.
    if not any(len(idx_list) > 1 for idx_list in seen.values()):
        return annotations

    for symbol, positions in seen.items():
        if is_vowel(symbol):  # Only extract consonant alliterations
            continue
        if len(positions) <= 1:  # Need at least two words starting with this letter
            continue
        # Group indices considering allowed intervening words and get the words
        alliterating_groups = group_alliterating_word_indices(positions, words, filler_words)
        annotations += alliterating_groups

    return annotations


def is_vowel(symbol: str) -> bool:
    vowels = "aeiouyøæå"
    return symbol.casefold() in vowels


def count_alliterations(annotations: list[list[str]]) -> int:
    """Calculate the largest number of alliterating words for sequences of alliterations."""
    counter = [len(allit) for allit in annotations]
    return max(counter)


def fetch_alliteration_symbols(annotations: list[list[str]]) -> list:
    """Gather the first letter of a word from each alliterating word group in a list of annotations."""
    symbols = [group[0][0] for group in annotations]
    return symbols


if __name__ == "__main__":
    # Test the functions with doctest
    import doctest

    doctest.testmod()
