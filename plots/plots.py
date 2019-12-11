import matplotlib.pyplot as plt
import os
import torch
import shutil

# detect the current working directory and print it
path = os.path.dirname(os.path.abspath(__file__))
print("The current working directory is %s" % path)


def yes_or_no(question):
    reply = str(input(question + ' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")


def plot_and_save(pred_train, pred_test, label_train, label_test, train_error, test_error, show,
                  trained_model, save_string, path=path):
    if save_string is not None:
        path_create = path + '/' + save_string

        if os.path.isdir(path_create):
            print("Directory already exists")
            if yes_or_no('Do you want to rewrite the directory?'):
                shutil.rmtree(path_create)

        try:
            os.mkdir(path_create)
        except OSError:
            print("Creation of the directory %s failed" % path_create)
        else:
            print("Successfully created the directory %s " % path_create)

        save_path = path_create + '/' + 'model.pt'
        torch.save(trained_model.state_dict(), save_path)
        with open(path_create+'/model_summary.txt', 'w+') as f:
            f.write(str(trained_model))  # Python 3.x
        print("Model Saved")

    plt.plot(pred_train, label="Predictions on train set")
    plt.plot(label_train, label="Actual data")
    plt.legend()
    if show:
        plt.show()
    if save_string is not None:
        plt.savefig(fname=path_create + '/Train_vs_actual.png')

    plt.clf()

    plt.plot(train_error, label="Training loss")
    plt.legend()
    if show:
        plt.show()
    if save_string is not None:
        plt.savefig(fname=path_create + '/Train_loss.png')
    plt.clf()

    plt.plot(test_error, label="Test loss")
    plt.legend()
    if show:
        plt.show()
    if save_string is not None:
        plt.savefig(fname=path_create + '/Test_loss.png')
    plt.clf()

    plt.plot(pred_test, label="Predictions on test set")
    plt.plot(label_test, label="Actual data")
    plt.legend()
    if show:
        plt.show()
    if save_string is not None:
        plt.savefig(fname=path_create + '/Test_vs_actual.png')
    plt.clf()