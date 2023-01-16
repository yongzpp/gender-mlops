from config import cfg
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline

class Optimizer(object):
    '''
    Object to perform Bayes Optimization (hyperopt)
    '''
    def __init__(self, X_train, X_test, y_train, y_test):
        '''
        Initialize search space for logistic regression
        '''
        self.X_train, self.X_test, self.y_train, self.y_test = X_train, X_test, y_train, y_test
        self.max_iter = cfg.optimize.max_evals
        self.space = {'C': hp.quniform('C', 0.01, 1000, 1),
                      'solver':hp.choice ('solver', ['lbfgs', 'saga', 'newton-cg'])}
        self.solver = ['lbfgs', 'saga', 'newton-cg']

    def objective(self, space):
        '''
        Objective to maximize
        :param space: search space
        :return loss (negative of accuracy since minimization)
        '''
        pipeline = make_pipeline(
                TfidfVectorizer(
                    analyzer='char',
                    ngram_range=(cfg.train.ngram[0], cfg.train.ngram[1]),
                ),
                LogisticRegression(max_iter=1000, C=space["C"], solver=space["solver"]),
            )
        pipeline.fit(self.X_train, self.y_train)
        accuracy = pipeline.score(self.X_test, self.y_test)

        print ("SCORE:", accuracy)
        return {'loss': -accuracy, 'status': STATUS_OK }

    def optimize(self):
        '''
        :param: the data needed to run (pandas.Series)
        :return parameters of best model
        '''
        trials = Trials()
        best_hyperparams = fmin(fn=self.objective, space=self.space, algo=tpe.suggest, \
                            max_evals=self.max_iter, trials=trials)
        print(best_hyperparams)
        return best_hyperparams["C"], self.solver[best_hyperparams["solver"]]