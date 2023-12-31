import lore

from prepare_dataset import *
from neighbor_generator import *

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")


def main():

    # dataset_name = 'german_credit.csv'
    path_data = './datasets/'
    # dataset = prepare_german_dataset(dataset_name, path_data)

    # dataset_name = 'compas-scores-two-years.csv'
    dataset_name = 'adult.csv'
    # dataset_name = 'german_credit.csv'
    if(dataset_name == 'compas-scores-two-years.csv'):
        dataset = prepare_compass_dataset(dataset_name, path_data)
    elif(dataset_name == 'adult.csv'):
        dataset = prepare_adult_dataset(dataset_name, path_data)
    else:
        dataset = prepare_german_dataset(dataset_name, path_data)
    print(dataset['label_encoder'][dataset['class_name']].classes_)
    print(dataset['possible_outcomes'])
    print("continuous traces:",dataset['continuous'])
    print("discrete traces:",dataset['discrete'])


    # dataset_name = 'adult.csv'
    # dataset = prepare_adult_dataset(dataset_name, path_data)

    X, y = dataset['X'], dataset['y']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    blackbox = RandomForestClassifier(n_estimators=20)
    blackbox.fit(X_train, y_train)

    X2E = X_test
    y2E = blackbox.predict(X2E)
    y2E = np.asarray([dataset['possible_outcomes'][i] for i in y2E])

    idx_record2explain = 0

    explanation, infos = lore.explain(idx_record2explain, X2E, dataset, blackbox,
                                      ng_function=genetic_neighborhood,
                                      discrete_use_probabilities=True,
                                      continuous_function_estimation=False,
                                      returns_infos=True,
                                      path=path_data, sep=';', log=True)

    dfX2E = build_df2explain(blackbox, X2E, dataset).to_dict('records')
    dfx = dfX2E[idx_record2explain]
    # x = build_df2explain(blackbox, X2E[idx_record2explain].reshape(1, -1), dataset).to_dict('records')[0]

    print('x = %s' % dfx)
    print('r = ', explanation[0])
    print('Counterfactual: ',  explanation[1])

    covered = lore.get_covered(explanation[0][1], dfX2E, dataset)
    print(len(covered))
    print(covered)

    print(explanation[0][0][dataset['class_name']], '<<<<')

    def eval(x, y):
        return 0 if x == y else 1

    precision = [1-eval(v, explanation[0][0][dataset['class_name']]) for v in y2E[covered]]
    print(precision)
    print("precision:",np.mean(precision))
    print("standrad deviation:",np.std(precision))


if __name__ == "__main__":
    main()
