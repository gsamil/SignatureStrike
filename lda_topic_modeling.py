import spacy
from spacy.lang.en import English
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
import random
from gensim import corpora
import pickle
import gensim
from similar_twitter import load_json_from_file,create_dir_if_not_exist
import os


def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        # elif token.orth_.startswith('@'):
        #     lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens


def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)


def prepare_text_for_lda(text):
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens


def load_model(dictionary_path, corpus_path, model_path):
    dictionary = gensim.corpora.Dictionary.load(dictionary_path)
    corpus = pickle.load(open(corpus_path, 'rb'))
    lda_model = gensim.models.ldamodel.LdaModel.load(model_path)
    return dictionary, corpus, lda_model


def get_topics_using_saved_model(new_doc, dictionary, lda_model):
    new_doc = prepare_text_for_lda(new_doc)
    new_doc_bow = dictionary.doc2bow(new_doc)
    return lda_model.get_document_topics(new_doc_bow)


def train_lda_model_from_text_data(text_data, dictionary_path, corpus_path, model_path):
    dictionary = corpora.Dictionary(text_data)
    corpus = [dictionary.doc2bow(text) for text in text_data]

    pickle.dump(corpus, open(corpus_path, 'wb'))
    dictionary.save(dictionary_path)

    NUM_TOPICS = 5
    lda_model = gensim.models.ldamodel.LdaModel(corpus, num_topics=NUM_TOPICS, id2word=dictionary, passes=15)
    lda_model.save(model_path)
    topics = lda_model.print_topics(num_words=4)
    for topic in topics:
        print(topic)
    return topics


def get_text_data_from_timelines(user_timelines_path):
    text_data = []
    user_timelines = load_json_from_file(user_timelines_path)

    for user, timelines in user_timelines.items():
        for id, timeline in timelines.items():
            full_text = timeline  # ['full_text']
            tokens = prepare_text_for_lda(full_text)
            text_data.append(tokens)

    return text_data

if __name__ == '__main__':
    # spacy.load('en')
    # nltk.download('wordnet')
    # nltk.download('stopwords')
    parser = English()
    en_stop = set(nltk.corpus.stopwords.words('english'))

    data_folder = "cyber_security"
    out_folder = os.path.join(data_folder, "lda_model_00")
    create_dir_if_not_exist(out_folder)

    dictionary_path = os.path.join(out_folder, "dictionary.gensim")
    corpus_path = os.path.join(out_folder, "corpus.pkl")
    model_path = os.path.join(out_folder, "model.gensim")
    user_timelines_path = os.path.join(data_folder, '9_user_timelines.json')

    # text_data = get_text_data_from_timelines(user_timelines_path)
    # topics = train_lda_model_from_text_data(text_data, dictionary_path, corpus_path, model_path)

    dictionary, corpus, lda_model = load_model(dictionary_path, corpus_path, model_path)
    topics = lda_model.print_topics(num_words=4)
    for topic in topics:
        print(topic)

    # topics2 = get_topics_using_saved_model("Electric Scooters Could Reshape Cities", dictionary, lda_model)
    # for topic in topics2:
    #     print(topic)

    # """ visualize topic model """
    import pyLDAvis.gensim
    lda_display = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary, sort_topics=True)
    pyLDAvis.show(lda_display)