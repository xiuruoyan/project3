import sys
import pickle

import nltk
nltk.download(['punkt', 'wordnet'])
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import pandas as pd
from sqlalchemy import create_engine
from nltk.corpus import stopwords
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split, GridSearchCV

def load_data(database_filepath):
    """
    Loads data from database
    Input:
        database_filepath: path to the sqlite database
    Output:
        X: feature dataframe
        Y: labels dataframe
    """
    engine = create_engine('sqlite:///' + database_filepath)
    df = pd.read_sql_query('select * from cleanedData', engine)

    X = df['message'].values
    Y = df.drop(['id','message','original','genre'], axis=1)
    category_names = Y.columns
    return X, Y, category_names


def tokenize(text):
    """
    Tokenizes a given text.
    Input:
        text: text string
    Output:
        cleaned_tokens: array of clean tokens
    """
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    cleaned_tokens = []
    for i in tokens:
        clean_tok = lemmatizer.lemmatize(i).lower().strip()
        cleaned_tokens.append(clean_tok)

    return cleaned_tokens


def build_model():
    """
    Build multi-lassification model
    """

    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', MultiOutputClassifier(RandomForestClassifier()))
    ])

    parameters = {
        'vect__ngram_range': ((1, 1), (1, 2)),
        'clf__estimator__min_samples_split': [2, 4],
    }

    cv = GridSearchCV(pipeline, param_grid=parameters, verbose=2, n_jobs=4)
    return cv


def evaluate_model(model, X_test, Y_test, category_names):
    """
    Evaluate the model against a test dataset
    Input:
        model: Trained model
        X_test: Test features
        Y_test: Test labels
        category_names: Category names
    """
    y_preds = model.predict(X_test)
    print(classification_report(y_preds, Y_test.values, target_names=category_names))
    print("------ Accuracy scores for each category -------\n")
    for i in range(36):
        print("Accuracy score for " + Y_test.columns[i] + 'is' , accuracy_score(Y_test.values[:,i],y_preds[:,i]))

def save_model(model, model_filepath):
    """
    Save the model to a Python pickle
    Input:
        model: Trained model
        model_filepath: Path to save the model
    """
    pickle.dump(model, open(model_filepath, 'wb'))

def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()