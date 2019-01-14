os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data' #nltk data kit

from textblob import TextBlob #dictionary
from config import FILTER_WORDS

##############
# KEYWORD DICTIONARIES
GREETING_KEYWORDS = ("hello", "hi", "hey",)
GREETING_RESPONSES = ["hi, want a dumpling?", "hey! come have a snack.", "hi yummy :)"]

def check_for_greeting(sentence):
    for word in sentence.words:
        if word.lower() in GREETING_KEYWORDS: #check if any of the user inputs includes a greeting
            return random.choice(GREETING_RESPONSES) #and return a random response

# dimsum prioritizes dimsum before anything else!
# so if we mention the bot, he will talk about dimsum
def check_for_dimsum(pronoun, noun, adjective):
    resp = None
    if pronoun == 'I' and (noun or adjective):
        if noun:
            if random.choice((True, False)):
                resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': noun.pluralize().capitalize()})
            else:
                resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
        else:
            resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp

# direct noun that is indefinite/uncountable
SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "I don't understand what this response is for."
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "Yeah, the shop next door specializes in {noun}!",
    "I don't know that much about {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "Nothing is as {adjective} as dimsum.",
    "How {adjective} is the restaurant next door?",
]

def respond(sentence):
    cleaned = preprocess(sentence)
    parsed = TextBlob(cleaned)
    #find the relevant parts of speech for dimsum to respond to
    pronoun, noun, adjective, verb = find_pos(parsed)
    #if we talk about dimsum, we use this function
    resp = check_for_dimsum(pronoun, noun, adjective)
    #if we have a greeting, we'll use the greeting function
    if not resp:
        resp = check_for_greeting(parsed)
    if not resp: #attempting to construct a new sentence
        if not pronoun:
            resp = random.choice(RAND_RESPONSE)
        elif pronoun == 'I' and not verb:
            resp = random.choice(SELF_RESPONSE)
        else:
            resp = construct_response(pronoun, noun, verb)
    if not resp:
        resp = random.choice(RAND_RESPONSE)

    logger.info("Returning phrase '%s'", resp)
    filter_response(resp) #good vibes only
    return resp

# grabs most relevant parts of speech for dimsum to talk about
# automatically returns pronoun, noun, adj, verb
# returns a tuple of None by default
def find_pos(parsed):
    pronoun = None
    noun = None
    adjective = None
    verb = None
    for sentence in parsed.sentences:
        pronoun = find_pronoun(sentence)
        noun = find_noun(sentence)
        adjective = find_adj(sentence)
        verb = find_verb(sentence)
    logger.info("Pronoun=%s, noun=%s, adj=%s, verb=%s", pronoun, noun, adjective, verb)
    return pronoun, noun, adjective, verb

def find_pronoun(sentence):
    pronoun = None
    for word, part_of_speech in sentence.pos_tags:
        # work through different pronouns
        if part_of_speech == 'PRP' and word.lower() == 'you':
            pronoun = 'I'
        elif part_of_speech == 'PRP' and word.lower() == 'i':
            pronoun = 'You'
    return pronoun


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 0: #if something has been inputted
        saying = sys.argv[1] #then it becomes the saying that we feed to dimsum