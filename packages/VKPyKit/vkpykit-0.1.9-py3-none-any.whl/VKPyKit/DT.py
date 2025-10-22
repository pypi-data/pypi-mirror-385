import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns


from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score, confusion_matrix
from IPython.display import display


class DT:

    """
    Decision Tree Classifier related visualizations
    To plot the confusion_matrix with percentages
    """

    def __init__(self):    
       print("DT object created!")

    # defining a function to compute different metrics to check performance of a classification model built using sklearn
    def model_performance_classification(self,
            model : DecisionTreeClassifier, 
            predictors : pd.DataFrame, 
            target: pd.Series) -> pd.DataFrame:
        """
        Function to compute different metrics to check classification model performance
        model: classifier \n
        predictors: independent variables \n
        target: dependent variable \n
        return: dataframe of different performance metrics
        """

        # predicting using the independent variables
        pred = model.predict(predictors)

        accuracy = accuracy_score(target, pred)  # to compute Accuracy
        recall = recall_score(target, pred)  # to compute Recall
        precision = precision_score(target, pred)  # to compute Precision
        f1 = f1_score(target, pred)  # to compute F1-score

        # creating a dataframe of metrics
        df_perf = pd.DataFrame(
            {"Accuracy": accuracy, "Recall": recall, "Precision": precision, "F1": f1},
            index=[0],
        )
        return df_perf

    def plot_confusion_matrix(self,
            model: DecisionTreeClassifier, 
            predictors : pd.DataFrame, 
            target: pd.DataFrame,
            x_label : str = 'Predicted', 
            y_label : str = 'Actual' )-> None: 
        """
        To plot the confusion_matrix with percentages \n
        model: classifier \n
        predictors: independent variables  \n
        target: dependent variable \n
        x_label: label for x-axis \n
        y_label: label for y-axis \n
        return: None
        """
        # Predict the target values using the provided model and predictors
        y_pred = model.predict(predictors)

        # Compute the confusion matrix comparing the true target values with the predicted values
        c_matrix = confusion_matrix(target, y_pred)

        # Create labels for each cell in the confusion matrix with both count and percentage
        labels = np.asarray(
            [
                ["{0:0.0f}".format(item) + "\n{0:.2%}".format(item / c_matrix.flatten().sum())]
                for item in c_matrix.flatten()
            ]
        ).reshape(2, 2)    # reshaping to a matrix

        # Set the figure size for the plot
        plt.figure(figsize=(6, 4))

        # Plot the confusion matrix as a heatmap with the labels
        sns.heatmap(c_matrix, annot=labels, fmt="")

        # Add a label to the y-axis
        plt.ylabel(y_label)

        # Add a label to the x-axis
        plt.xlabel(x_label)

    def tune_decision_tree(self,
            X_train : pd.DataFrame,
            y_train : pd.Series, 
            X_test : pd.DataFrame, 
            y_test : pd.Series,
            max_depth_v : tuple[int, int, int] = (2,11,2), 
            max_leaf_nodes_v : tuple[int, int, int]= (10, 51, 10), 
            min_samples_split_v: tuple[int, int, int]=(10, 51, 10),
            printall : bool = False,
            sortresultby :list = ['score_diff']) -> DecisionTreeClassifier:
        """
        Function to tune hyperparameters of Decision Tree Classifier \n
        X_train: training independent variables \n
        y_train: training dependent variable \n
        X_test: test independent variables \n  
        y_test: test dependent variable
        max_depth_v: tuple containing (start, end, step) values for max_depth parameter \n
        max_leaf_nodes_v: tuple containing (start, end, step) values for max_leaf_nodes parameter \n
        min_samples_split_v: tuple containing (start, end, step) values for min_samples_split parameter \n
        printall: whether to print all results (default is False) \n
        sortresultby: list of columns to sort the results by (default is ['score_diff']) \n
        return: best DecisionTreeClassifier model
        """


        # define the parameters of the tree to iterate over - Define by default
        max_depth_values = np.arange(max_depth_v[0], max_depth_v[1], max_depth_v[2])
        max_leaf_nodes_values = np.arange(max_leaf_nodes_v[0], max_leaf_nodes_v[1], max_leaf_nodes_v[2])
        min_samples_split_values = np.arange(min_samples_split_v[0], min_samples_split_v[1], min_samples_split_v[2])

        # initialize variables to store the best model and its performance
        best_estimator = None
        best_score_diff = float('inf')
        estimator_results = pd.DataFrame(columns=['max_depth', 'max_leaf_nodes', 'min_samples_split','Accuracy','Recall','Precision','F1', 'score_diff'])

        # iterate over all combinations of the specified parameter values
        for max_depth in max_depth_values:
            for max_leaf_nodes in max_leaf_nodes_values:
                for min_samples_split in min_samples_split_values:

                    # initialize the tree with the current set of parameters
                    estimator = DecisionTreeClassifier(
                        max_depth=max_depth,
                        max_leaf_nodes=max_leaf_nodes,
                        min_samples_split=min_samples_split,
                        random_state=42
                    )

                    # fit the model to the training data
                    estimator.fit(X_train, y_train)

                    # make predictions on the training and test sets
                    y_train_pred = estimator.predict(X_train)
                    y_test_pred = estimator.predict(X_test)

                    # calculate F1 scores for training and test sets
                    train_f1_score = f1_score(y_train, y_train_pred)
                    test_f1_score = f1_score(y_test, y_test_pred)

                    # calculate the absolute difference between training and test F1 scores
                    score_diff = abs(train_f1_score - test_f1_score)

                    dtree1_test_perf = self.model_performance_classification(
                        estimator, X_test, y_test
                    )
                    estimator_results = pd.concat([estimator_results, pd.DataFrame({'max_depth': [max_depth],
                                                                                    'max_leaf_nodes': [max_leaf_nodes],
                                                                                    'min_samples_split': [min_samples_split],
                                                                                    'Accuracy': dtree1_test_perf['Accuracy'].values,
                                                                                    'Recall': dtree1_test_perf['Recall'].values,
                                                                                    'Precision': dtree1_test_perf['Precision'].values,
                                                                                    'F1': dtree1_test_perf['F1'].values,
                                                                                    'score_diff': [score_diff]
                                                                                })],
                                                ignore_index=True)
                
                    # update the best estimator and best score if the current one has a smaller score difference
                    if score_diff < best_score_diff:
                        best_score_diff = score_diff
                        best_estimator = estimator

        estimator_results.sort_values(by=sortresultby, ascending=True, inplace=True)
        # Set display option to show all rows

        if printall:
            pd.set_option('display.max_rows', None)
            display(estimator_results)
            pd.reset_option('display.max_rows')
        else:
            display(estimator_results)
        
        return best_estimator

    def plot_feature_importance(self,
            model: DecisionTreeClassifier, 
            feature_names: list, 
            figsize: tuple[float, float] = (10, 6), 
            numberoftopfeatures: int =None,
            feature_title : str = 'Feature Importance',
            x_label : str = 'Importance Score',
            y_label : str = 'Features') -> None:
        """
        Plot feature importance for a given model and feature names

        model: trained model with feature_importances_ attribute \n
        feature_names: list of feature names    \n
        figsize: size of the figure (default (10,6)) \n
        numberoftopfeatures: number of top features to display (default None, i.e., display all features) \n
        feature_title: title of the feature importance plot \n
        x_label: label for x-axis \n
        y_label: label for y-axis \n
        return: None
        """
        importances = model.feature_importances_

        feature_importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        })

        feature_importance_df.sort_values(by='Importance', ascending=False, inplace=True)

        if numberoftopfeatures:
            feature_importance_df = feature_importance_df.head(numberoftopfeatures)

        plt.figure(figsize=figsize)
        sns.barplot(x='Importance', y='Feature', data=feature_importance_df, palette='viridis')
        plt.title(label=feature_title)
        plt.xlabel(xlabel=x_label)
        plt.ylabel(ylabel=y_label)
        plt.show()

    def show_decision_tree_structure(model: DecisionTreeClassifier, 
                                        feature_names : list,
                                        class_names : list = None, 
                                        figsize : tuple[float, float] =(20,10)) -> None:
            """
            Visualize the structure of the decision tree \n

            model: trained DecisionTreeClassifier model \n
            feature_names: list of feature names \n
            class_names: list of class names \n
            figsize: size of the figure (default (20,10)) \n
            return: None
            """
            
            # set the figure size for the plot
            plt.figure(figsize=figsize)

            # plotting the decision tree
            out = tree.plot_tree(
                model,                         # decision tree classifier model
                feature_names=feature_names,    # list of feature names (columns) in the dataset
                filled=True,                    # fill the nodes with colors based on class
                fontsize=9,                     # font size for the node text
                node_ids=False,                 # do not show the ID of each node
                class_names=class_names,               # whether or not to display class names
            )

            # add arrows to the decision tree splits if they are missing
            for o in out:
                arrow = o.arrow_patch
                if arrow is not None:
                    arrow.set_edgecolor("black")    # set arrow color to black
                    arrow.set_linewidth(1)          # set arrow linewidth to 1

            # displaying the plot
            plt.show()