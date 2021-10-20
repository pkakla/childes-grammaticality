import os
import re

import pandas as pd

PATH_ADJACENT_UTTERANCES = os.path.expanduser(
    "~/data/communicative_feedback/chi_car_adjacent_utterances.csv"
)

# codes that will be excluded from analysis
IS_UNTRANSCRIBED = lambda word: "www" in word
IS_INTERRUPTION = lambda word: word.startswith("+/")
IS_SELF_INTERRUPTION = lambda word: word == "+//"
IS_TRAILING_OFF = lambda word: word == "+..."
IS_TRAILING_OFF_2 = lambda word: word == "+.."
IS_EXCLUDED_WORD = lambda word: "@x:" in word
IS_PAUSE = lambda word: bool(re.match(r"\(\d*?\.*\d*?\)", word))
IS_OMITTED_WORD = lambda word: word.startswith("0")
IS_SATELLITE_MARKER = lambda word: word == "‡"
IS_QUOTATION_MARKER = lambda word: word in ['+"/', '+"/.', '+"', '+".']
IS_UNKNOWN_CODE = lambda word: word == "zzz"


def is_excluded_code(word):
    if (
        IS_UNTRANSCRIBED(word)
        or IS_INTERRUPTION(word)
        or IS_SELF_INTERRUPTION(word)
        or IS_TRAILING_OFF(word)
        or IS_TRAILING_OFF_2(word)
        or IS_EXCLUDED_WORD(word)
        or IS_PAUSE(word)
        or IS_OMITTED_WORD(word)
        or IS_SATELLITE_MARKER(word)
        or IS_QUOTATION_MARKER(word)
        or IS_UNKNOWN_CODE(word)
    ):
        return True
    return False


EMPTY_UTTERANCE = ""

# non-speech-related sounds
IS_SIMPLE_EVENT_NON_SPEECH = lambda word: word.startswith("&=") and word not in [
    CODE_EVENT_BABBLES,
    CODE_EVENT_VOCALIZES,
    CODE_EVENT_WHISPERS,
    CODE_EVENT_MUMBLES,
]
IS_OTHER_LAUGHTER = lambda word: word in ["ahhah", "haha", "hahaha", "hahahaha"]


def word_is_speech_related(word):
    if IS_SIMPLE_EVENT_NON_SPEECH(word) or IS_OTHER_LAUGHTER(word):
        return False
    return True


def get_paralinguistic_event(utterance):
    match = re.search(r"\[=! [\S\s]*]", utterance)
    if match:
        pos = match.regs[0]
        event = utterance[pos[0] : pos[1]]
        return event

    return None


def paralinguistic_event_is_speech_related(event):
    if (
        "babbl" in event
        or "hum" in event
        or "sing" in event
        or "whisper" in event
        or "mumbl" in event
    ):
        return True
    return False


def remove_nonspeech_events(utterance):
    # Remove paralinguistic events
    event = get_paralinguistic_event(utterance)
    if event:
        if not paralinguistic_event_is_speech_related(event):
            utterance = utterance.replace(event, "")

    words = utterance.split(" ")
    cleaned_utterance = [word for word in words if word_is_speech_related(word)]

    cleaned_utterance = " ".join(cleaned_utterance)
    cleaned_utterance = remove_whitespace(cleaned_utterance)
    return cleaned_utterance


def remove_whitespace(utterance):
    # Remove trailing whitespace
    cleaned_utterance = re.sub(r"\s+$", "", utterance)
    # Remove whitespace at beginning
    cleaned_utterance = re.sub(r"^\s+", "", cleaned_utterance)
    return cleaned_utterance


def clean_utterance(utterance):
    """Remove all superfluous annotation information."""
    # Remove timing information:
    utterance = re.sub(r"[^]+?", "", utterance)
    # remove postcodes
    utterance = re.sub(r"\[\+[\S\s]*]", "", utterance)
    # remove precodes
    utterance = re.sub(r"\[-[\S\s]*]", "", utterance)
    # remove comments
    utterance = re.sub(r"\[%[\S\s]*]", "", utterance)
    # remove explanations:
    utterance = re.sub(r"\[= [\S\s]*]", "", utterance)
    # remove replacements:
    utterance = re.sub(r"\[:+ [\S\s]*]", "", utterance)
    # remove error codes:
    utterance = re.sub(r"\[\*[\S\s]*]", "", utterance)
    # remove repetition markers / collapses:
    utterance = re.sub(r"\[/[\S\s]*]", "", utterance)
    utterance = re.sub(r"\[x[\S\s]*]", "", utterance)
    # remove overlap markers
    utterance = re.sub(r"\[<\d*]", "", utterance)
    utterance = re.sub(r"\[>\d*]", "", utterance)
    # remove best guess markers
    utterance = re.sub(r"\[\?[\S\s]*]", "", utterance)
    # remove alternative transcriptions
    utterance = re.sub(r"\[=\? [\S\s]*]", "", utterance)
    # remove stress markers
    utterance = re.sub(r"\[!+]", "", utterance)
    # Remove "complex local events"
    utterance = re.sub(r"\[\^\S*]", "", utterance)

    words = utterance.split(" ")
    cleaned_utterance = []
    for word in words:
        if not word == EMPTY_UTTERANCE and not is_excluded_code(word):
            # remove other codes:
            word = re.sub(r"@z:\S*", "", word)
            # child invented forms, family forms, neologisms
            word = re.sub(r"@c", "", word)
            word = re.sub(r"@f", "", word)
            word = re.sub(r"@n", "", word)
            # onomatopeia
            word = re.sub(r"@o", "", word)
            # singing
            word = re.sub(r"@si", "", word)
            # word play
            word = re.sub(r"@wp", "", word)
            # dialect
            word = re.sub(r"@d", "", word)
            # single letters
            word = re.sub(r"@l", "", word)
            # multiple letters
            word = re.sub(r"@k", "", word)
            # test words
            word = re.sub(r"@t", "", word)
            # other language marker
            word = re.sub(r"@s\S*", "", word)
            # metalinguistic
            word = re.sub(r"@q", "", word)
            # remove brackets
            word = word.replace("(", "").replace(")", "")
            # remove brackets
            word = word.replace("<", "").replace(">", "")
            # compound words
            word = word.replace("_", " ")
            word = word.replace("+", " ")
            # remove lengthening
            word = re.sub(r":", "", word)
            # remove inter-syllable pauses
            word = re.sub(r"\^", "", word)
            # remove filled-pause prefix
            word = re.sub(r"&-", "", word)

            cleaned_utterance.append(word)

    cleaned_utterance = " ".join(cleaned_utterance)

    # Remove punctuation
    cleaned_utterance = re.sub(r"[,\"„”]", "", cleaned_utterance)
    cleaned_utterance = re.sub(r"''", "", cleaned_utterance)
    cleaned_utterance = re.sub(r"[\.!\?]+\s*$", "", cleaned_utterance)

    cleaned_utterance = remove_whitespace(cleaned_utterance)
    return cleaned_utterance


# Unintelligible words with an unclear phonetic shape should be transcribed as
CODE_UNINTELLIGIBLE = "xxx"

# Use the symbol yyy when you plan to code all material phonologically on a %pho line.
# (usually used when utterance cannot be matched to particular words)
CODE_PHONETIC = "yyy"

CODE_BABBLING = "@b"
CODE_UNIBET_PHONOLOGICAL_TRANSCRIPTION = "@u"
CODE_INTERJECTION = "@i"
CODE_PHONOLGICAL_CONSISTENT_FORM = "@p"
CODE_PHONOLOGICAL_FRAGMENT = "&"
CODE_EVENT_BABBLES = "&=babbles"
CODE_EVENT_VOCALIZES = "&=vocalizes"
CODE_EVENT_WHISPERS = "&=whispers"
CODE_EVENT_MUMBLES = "&=mumbles"

OTHER_BABBLING = ["ba", "baa", "babaa", "ababa", "bada"]


VOCAB = set(
    pd.read_csv("data/childes_custom_vocab.csv", header=None, names=["word"]).word
)


def is_babbling(word):
    if (
        word.endswith(CODE_BABBLING)
        or word.endswith(CODE_INTERJECTION)
        or word.startswith(CODE_PHONOLOGICAL_FRAGMENT)
        or word == CODE_UNINTELLIGIBLE
        or word == CODE_PHONETIC
        or word.startswith(CODE_EVENT_BABBLES)
        or word.startswith(CODE_EVENT_VOCALIZES)
        or word.startswith(CODE_EVENT_MUMBLES)
        or word in OTHER_BABBLING
        or (
            word.endswith(CODE_UNIBET_PHONOLOGICAL_TRANSCRIPTION)
            and word.lower().replace(CODE_UNIBET_PHONOLOGICAL_TRANSCRIPTION, "")
            not in VOCAB
        )
        or (
            word.endswith(CODE_PHONOLGICAL_CONSISTENT_FORM)
            and word.lower().replace(CODE_PHONOLGICAL_CONSISTENT_FORM, "") not in VOCAB
        )
    ):
        return True
    return False


def remove_babbling(utterance):
    # Remove paralinguistic events
    event = get_paralinguistic_event(utterance)
    if event:
        if paralinguistic_event_is_speech_related(event):
            utterance = utterance.replace(event, "")

    words = utterance.split(" ")
    filtered_utterance = [word for word in words if not is_babbling(word)]

    filtered_utterance = " ".join(filtered_utterance)
    filtered_utterance = clean_utterance(filtered_utterance)
    return filtered_utterance


def filter_corpora_based_on_response_latency_length(corpora, adj_utterances):
    # Calculate mean and stddev of response latency using data from Nguyen, Versyp, Cox, Fusaroli (2021)
    latency_data = pd.read_csv("data/MA turn-taking.csv")

    # Use only non-clinical data:
    latency_data = latency_data[latency_data["clinical group"] == "Healthy"]

    mean_latency = latency_data.adult_response_latency.mean()
    std_mean_latency = latency_data.adult_response_latency.std()
    print(
        f"Mean of response latency in meta-analysis: {mean_latency:.1f} +/- {std_mean_latency:.1f}"
    )

    min_age = latency_data.mean_age_infants_months.min()
    max_age = latency_data.mean_age_infants_months.max()
    mean_age = latency_data.mean_age_infants_months.max()
    print(
        f"Mean of child age in meta-analysis: {mean_age:.1f} (min: {min_age} max: {max_age})"
    )

    # Filter corpora to be in range of mean +/- 1 standard deviation
    filtered = []
    for corpus in corpora:
        mean = adj_utterances[
            adj_utterances.corpus == corpus
        ].response_latency.values.mean()
        if mean_latency - std_mean_latency < mean < mean_latency + std_mean_latency:
            filtered.append(corpus)

    return filtered