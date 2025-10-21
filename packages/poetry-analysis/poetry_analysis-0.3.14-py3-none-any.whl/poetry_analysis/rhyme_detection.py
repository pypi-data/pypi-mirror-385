import json
import logging
import re
import string
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from convert_pa import phonetic_inventory

from poetry_analysis import utils


@dataclass
class Verse:
    id_: str | int
    rhyme_score: int = 0
    rhyme_tag: str = ""
    text: str = ""
    transcription: str = ""
    tokens: list | None = None
    syllables: list | None = None
    last_token: str | None = None
    rhymes_with: str | int | None = None

    @property
    def dict(self) -> dict:
        """Return the Verse object as a dictionary."""
        dictionary = self.__dict__
        dictionary["verse_id"] = self.id_
        del dictionary["id_"]
        return dictionary


def is_stressed(syllable: str | list) -> bool:
    """Check if a syllable is stressed by searching for stress markers.

    Stress markers:
        - `0`: Vowel/syllable nucleus without stress
        - `1`: Primary stress with toneme 1
        - `2`: Primary stress with toneme 2
        - `3`: Secondary stress

    Examples:
        >>> is_stressed("a1")
        True
        >>> is_stressed("a0")
        False
        >>> is_stressed(["a", "1"])
        True
        >>> is_stressed(["a", "0"])
        False
    """
    if isinstance(syllable, list):
        syllable = " ".join(syllable)
    result = re.search(r"[123]", syllable)
    return bool(result)


def strip_stress(phoneme: str) -> str:
    """Strip the stress marker from a phoneme."""
    return phoneme.strip("0123")


def is_nucleus(symbol: str, orthographic: bool = False) -> bool:
    """Check if a phoneme or a letter is a valid syllable nucleus."""
    valid_nuclei = get_valid_nuclei(orthographic=orthographic)
    return strip_stress(symbol) in valid_nuclei


def get_valid_nuclei(orthographic: bool = False) -> list:
    """Return the list of valid syllable nuclei with either graphemes or Nofabet phonemes.

    Args:
        orthographic: If True, return graphemes
    """
    return utils.VALID_NUCLEI if orthographic else phonetic_inventory.PHONES_NOFABET["nuclei"]


def find_nucleus(word: str, orthographic: bool = False) -> re.Match | None:
    """Check if a word has a valid syllable nucleus."""
    valid_nuclei = get_valid_nuclei(orthographic=orthographic)
    rgx = re.compile(rf"({'|'.join(valid_nuclei)})")
    nucleus = rgx.search(word)
    return nucleus


def is_schwa(string: str) -> bool:
    """Check if a string object is the schwa sound."""
    string = string.strip()
    return (string == "e") or (string == "AX") or (string == "AX0")


def remove_syllable_onset(syllable: list) -> list | None:
    """Split a syllable nucleus and coda from the onset to find the rhyming part of the syllable."""
    for idx, phone in enumerate(syllable):
        if is_nucleus(phone):
            return syllable[idx:]
    logging.debug("No nucleus found in %s", syllable)


def score_rhyme(sequence1: str, sequence2: str, orthographic: bool = False) -> float:
    """Check if two words rhyme and return a rhyming score.

    Returns:
        `1.0`:    Only the syllable nucleus + coda (=rhyme) match # perfect or proper rhyme
        `0.5`:    NØDRIM or lame rhyme. One of the words is fully contained in the other, e.g. 'tusenfryd' / 'fryd'
        `0.0`:    No match
    """

    substring = shared_ending_substring(sequence1, sequence2)

    if not substring:
        logging.debug("No shared ending substring found in %s and %s", sequence1, sequence2)
        return 0

    nucleus = find_nucleus(substring, orthographic=orthographic)

    if not nucleus:
        logging.debug("no nucleus found in %s", substring)
        return 0
    if utils.is_grammatical_suffix(substring):
        logging.debug("only the grammatical suffixes match: %s", substring)
        # e.g. "arbeidet" / "skrevet"
        return 0
    if utils.is_grammatical_suffix(substring[nucleus.start() :]):
        logging.debug("the rhyming part is a grammatical suffix: %s", substring[nucleus.start() :])
        # e.g. "blomster" / "fester"
        return 0
    if is_schwa(substring):
        logging.debug(
            "the rhyming part is scwha (%s) and the words share no other vowels: %s",
            substring,
            (sequence1, sequence2),
        )
        return 0

    if not sequence1.endswith(substring) or not sequence2.endswith(substring):
        # not an end rhyme
        logging.debug("not an end rhyme: %s and %s", sequence1, sequence2)
        return 0
    if substring in (sequence1, sequence2):
        # one of the words is fully contained in the other
        logging.debug("Nødrim: %s and %s", sequence1, sequence2)
        return 0.5

    if nucleus and (sequence1 != sequence2):
        logging.debug("Proper rhyme: %s and %s", sequence1, sequence2)
        return 1
    # otherwise, assume that the words do not rhyme
    logging.debug("No condition met for a rhyme: %s and %s", sequence1, sequence2)
    return 0


def longest_common_substring(string1: str, string2: str) -> str:
    """Find the longest common substring between two strings.

    Implementation based on the pseudocode from:
    https://en.wikipedia.org/wiki/Longest_common_substring#Dynamic_programming
    """
    m = len(string1)
    n = len(string2)
    L = np.zeros((m + 1, n + 1))
    z = 0
    result = ""

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if string1[i - 1] == string2[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
                if L[i][j] > z:
                    z = L[i][j]
                    result = string1[(i - int(z)) : i]
            else:
                L[i][j] = 0
    return result


def shared_ending_substring(string1: str, string2: str) -> str:
    """Find the shared substring at the end of two strings."""
    min_length = min(len(string1), len(string2))

    for i in range(1, min_length + 1):
        if string1[-i] != string2[-i]:
            final_substring = string1[-i + 1 :] if i > 1 else ""
            return final_substring
    return string1[-min_length:] if min_length > 0 else ""


def find_last_stressed_syllable(syll):
    """Find the last stressed syllable in a list of syllables."""
    n = len(syll)

    for i in range(1, n + 1):
        if re.search(r"[123]", syll[-i]):
            return syll[-i:]
    return syll[:]


def find_last_word(tokens: list[str]) -> str:
    """Find the last word in a list of tokens."""
    for token in reversed(tokens):
        if not utils.is_punctuation(token):
            return token
    return ""


def find_rhyming_line(current: Verse, previous_lines: list[Verse], orthographic: bool = False) -> tuple:
    """Check if the current line rhymes with any of the previous lines."""

    for idx, previous in reversed(list(enumerate(previous_lines))):
        if previous.last_token is None or current.last_token is None:
            continue
        rhyme_score = score_rhyme(previous.last_token, current.last_token, orthographic=orthographic)
        if rhyme_score > 0:
            return idx, rhyme_score
    return None, 0


def tag_rhyming_verses(verses: list, orthographic: bool = False) -> list:
    """Annotate end rhyme patterns in a poem stanza.

    Args:
        verses: list of verselines with words
        orthographic: if True, the words strings are orthographic,
            otherwise assume phonemic nofabet transcriptions
    Return:
        list of annotated verses with rhyme scores and rhyme tags
    """
    alphabet = iter(string.ascii_letters)

    processed = []  # needs to be a list!
    for idx, verseline in enumerate(verses):
        if not verseline:
            continue

        if orthographic:
            tokens = utils.normalize(verseline)
            last_word = find_last_word(tokens)
            if not last_word:
                logging.debug("No tokens found in %s", verseline)
                continue
            current_verse = Verse(
                id_=idx,
                text=verseline,
                tokens=tokens,
                last_token=last_word.casefold(),
            )
        else:
            syllables = utils.convert_to_syllables(verseline, ipa=False)
            last_syllable = " ".join(find_last_stressed_syllable(syllables))

            current_verse = Verse(
                id_=idx,
                transcription="\t".join(verseline),
                tokens=verseline,
                syllables=syllables,
                last_token=re.sub(r"[0123]", "", last_syllable),
            )

        rhyming_idx, rhyme_score = find_rhyming_line(current_verse, processed, orthographic=orthographic)

        if rhyming_idx is not None and rhyme_score > 0:
            rhyming_verse = processed[rhyming_idx]
            current_verse.rhyme_tag = rhyming_verse.rhyme_tag
            current_verse.rhyme_score = rhyme_score
            current_verse.rhymes_with = rhyming_verse.id_

        else:
            try:
                current_verse.rhyme_tag = next(alphabet)
            except StopIteration:
                logging.info("Ran out of rhyme tags at %s! Initialising new alphabet.", idx)
                alphabet = iter(string.ascii_letters)
                current_verse.rhyme_tag = next(alphabet)

        processed.append(current_verse)
    return processed


def collate_rhyme_scheme(annotated_stanza: list) -> str:
    """Join the rhyme tags rom each tagged verse to form a rhyme scheme."""
    return "".join(verse.rhyme_tag for verse in annotated_stanza)


def get_stanzas_from_transcription(transcription: dict, orthographic: bool = False) -> list:
    """Parse a dict of transcribed verse lines and return a list of stanzas."""
    line_ids = [x for x in transcription if x.startswith("line_")]
    n_lines = len(line_ids)
    logging.debug("Number of lines in poem: %s", n_lines)
    poem = []
    stanza = []
    for line_n in line_ids:
        verse = transcription.get(line_n)
        if (verse is not None) and (len(verse) > 0):
            words, pron = zip(*verse, strict=False)
            verseline = list(words if orthographic else pron)
            stanza.append(verseline)
        else:
            if len(stanza) == 0:
                continue
            poem.append(stanza)
            stanza = []
    if len(poem) == 0 and len(stanza) > 0:
        poem.append(stanza)
    return poem


def tag_stanzas(stanzas: list, orthographic: bool = False) -> Generator:
    """Iterate over stanzas and tag verses with a rhyme scheme."""
    for idx, stanza in enumerate(stanzas):
        tagged = tag_rhyming_verses(stanza, orthographic=orthographic)
        rhyme_scheme = collate_rhyme_scheme(tagged)

        yield {
            "stanza_id": idx,
            "rhyme_scheme": rhyme_scheme,
            "verses": [verse.dict for verse in tagged],
        }


def tag_text(text: str) -> Generator:
    """Annotate rhyming schemes in a text where stanzas are separated by two empty lines."""
    stanzas = utils.split_stanzas(text)
    file_annotations = tag_stanzas(stanzas, orthographic=True)
    return file_annotations


def tag_poem_file(poem_file: str, write_to_file: bool = False) -> list:
    """Annotate rhyming schemes in a poem from a file."""
    # Assume that the stanzas are independent of each other
    # and that the rhyme scheme is unique to each stanza

    filepath = Path(poem_file)
    file_content = filepath.read_text(encoding="utf-8")
    if filepath.suffix == ".json":
        poem = json.loads(file_content)
        poem_id = poem.get("text_id")
        orthographic = False
        stanzas = get_stanzas_from_transcription(poem, orthographic=orthographic)

    elif filepath.suffix == ".txt":
        poem_id = filepath.stem.split("_")[0]
        stanzas = utils.split_stanzas(file_content)
        orthographic = True

    logging.debug("Tagging poem: %s", poem_id)

    file_annotations = list(tag_stanzas(stanzas, orthographic=orthographic))

    if write_to_file:
        outputfile = filepath.parent / f"{filepath.stem}_rhyme_scheme.json"
        with outputfile.open("w") as f:
            f.write(json.dumps(file_annotations, ensure_ascii=False, indent=4))

        logging.debug("Saved rhyme scheme annotations for poem %s to \n\t%s", poem_id, outputfile)
    return file_annotations


def main():
    """Main function to run the rhyme detection script."""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Tag rhyme schemes in a poem.")
    parser.add_argument(
        "-f",
        "--poemfile",
        type=Path,
        help="Path to a json file with phonemic transcriptions.",
    )
    parser.add_argument(
        "-t",
        "--doctest",
        action="store_true",
        help="Run doctests in the module.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Set logging level to debug.")
    args = parser.parse_args()

    if args.verbose:
        today = datetime.today().date()
        logging_file = f"{__file__.split('.')[0]}_{today}.log"
        logging.basicConfig(level=logging.DEBUG, filename=logging_file, filemode="a")

    if args.poemfile:
        tag_poem_file(args.poemfile, write_to_file=True)

    if args.doctest:
        import doctest

        logging.debug("Running doctests...")
        doctest.testmod(verbose=True)
        logging.info("Doctests passed.")


if __name__ == "__main__":
    main()
