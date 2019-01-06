import spacy
from spacy.lang.en import English
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
import random
from gensim import corpora
import pickle
import gensim
from similar_twitter import load_json_from_file,create_dir_if_not_exist, write_all_lines, read_all_lines
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


def get_text_data_from_timelines(user_timelines_path, text_data_path):
    text_data = []
    user_timelines = load_json_from_file(user_timelines_path)

    for user, timelines in user_timelines.items():
        for id, timeline in timelines.items():
            full_text = timeline['full_text']
            tokens = prepare_text_for_lda(full_text)
            text_data.append(tokens)

    write_all_lines(text_data_path, [" ".join(l) for l in text_data])
    return text_data


def get_text_data_from_term_list(term_list_path, text_data_path):
    text_data = []
    term_list = load_json_from_file(term_list_path)

    for user, timelines in term_list.items():
        for id, timeline in timelines.items():
            full_text = timeline
            tokens = prepare_text_for_lda(full_text)
            text_data.append(tokens)

    write_all_lines(text_data_path, [" ".join(l) for l in text_data])
    return text_data


def train_lda_model_from_text_data(text_data, dictionary_path, corpus_path, model_path):
    dictionary = corpora.Dictionary(text_data)
    corpus = [dictionary.doc2bow(text) for text in text_data]

    pickle.dump(corpus, open(corpus_path, 'wb'))
    dictionary.save(dictionary_path)

    NUM_TOPICS = 5
    lda_model = gensim.models.ldamodel.LdaModel(corpus, num_topics=NUM_TOPICS, id2word=dictionary, passes=15)
    lda_model.save(model_path)


def load_model(dictionary_path, corpus_path, model_path):
    dictionary = gensim.corpora.Dictionary.load(dictionary_path)
    corpus = pickle.load(open(corpus_path, 'rb'))
    lda_model = gensim.models.ldamodel.LdaModel.load(model_path)
    return dictionary, corpus, lda_model


def get_topics_using_saved_model(new_doc, dictionary, lda_model):
    new_doc = prepare_text_for_lda(new_doc)
    new_doc_bow = dictionary.doc2bow(new_doc)
    return lda_model.get_document_topics(new_doc_bow)


if __name__ == '__main__':
    # spacy.load('en')
    # nltk.download('wordnet')
    # nltk.download('stopwords')
    parser = English()
    en_stop = set(nltk.corpus.stopwords.words('english'))

    data_folder = os.path.join("cyber_security", "lda_model_03")
    create_dir_if_not_exist(data_folder)

    dictionary_path = os.path.join(data_folder, "dictionary.gensim")
    corpus_path = os.path.join(data_folder, "corpus.pkl")
    model_path = os.path.join(data_folder, "model.gensim")
    term_list_path = os.path.join(data_folder, '11_term_list.json')

    text_data_path = os.path.join(data_folder, "text_data.txt")
    text_data = get_text_data_from_term_list(term_list_path, text_data_path)

    # text_data = [l.split(" ") for l in read_all_lines(text_data_path)]
    train_lda_model_from_text_data(text_data, dictionary_path, corpus_path, model_path)

    dictionary, corpus, lda_model = load_model(dictionary_path, corpus_path, model_path)
    topics = lda_model.print_topics(num_words=4)
    for topic in topics:
        print(topic)

    # topics2 = get_topics_using_saved_model("Electric Scooters Could Reshape Cities", dictionary, lda_model)
    # for topic in topics2:
    #     print(topic)

    # """ visualize topic model """
    # import pyLDAvis.gensim
    # lda_display = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary, sort_topics=True)
    # pyLDAvis.show(lda_display)