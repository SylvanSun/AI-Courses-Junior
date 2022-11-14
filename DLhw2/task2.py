import numpy as np
from jittor import nn
import jittor as jt

from model import Classifier
from dataset import CIFAR10
from loss import make_loss
from utils.parser import make_parser


def train(model, train_loader, optimizer, epoch_idx, loss_function):
    model.train()
    batch_size = train_loader.batch_size
    num_data = len(train_loader)

    train_loss = []
    for batch_idx, (inputs, labels) in enumerate(train_loader):
        outputs = model(inputs)
        loss = loss_function(outputs, labels)
        optimizer.step(loss)
        train_loss.append(loss.item())
        print(
            "Train epoch: {}  {:.2f}%\tLoss:{:.6f}".format(
                epoch_idx, 100 * batch_idx * batch_size / num_data, loss.item()
            )
        )
    return np.mean(train_loss)


def val(model, test_loader, epoch_idx, loss_function):
    model.eval()
    num_data = len(test_loader)

    test_loss = []
    total_correct = 0
    count_data = 0
    for batch_idx, (inputs, labels) in enumerate(test_loader):
        batch_size = labels.shape[0]
        count_data += batch_size
        outputs = model(inputs)
        loss = loss_function(outputs, labels)
        test_loss.append(loss.item())
        pred = np.argmax(outputs.numpy(), axis=1)
        num_correct = np.sum(labels.numpy() == pred)
        total_correct += num_correct
        batch_acc = num_correct / batch_size
        print("Test epoch: {}  {:.2f}%\tAcc:{:.2f}".format(epoch_idx, 100 * count_data / num_data, batch_acc))
    total_acc = total_correct / num_data
    print(f"Test Epoch: {epoch_idx} \t Total Acc: {total_acc:.2f}")
    return np.mean(test_loss)


def task2(args):
    mode, batch_size, learning_rate, weight_decay, num_epoch, debug = (
        args.dataset,
        args.bs,
        args.lr,
        args.wd,
        args.ne,
        args.debug,
    )
    if debug:
        num_epoch = 1
    loss_function = make_loss()[args.loss]

    train_loader = CIFAR10(train=True, batch_size=batch_size, shuffle=True, data_choice=mode)
    test_loader = CIFAR10(train=False, batch_size=batch_size, shuffle=False, data_choice="default")

    model = Classifier()
    optimizer = nn.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)

    train_losses, test_losses = [], []
    for epoch_idx in range(1, num_epoch + 1):
        train_loss = train(model, train_loader, optimizer, epoch_idx, loss_function)
        test_loss = val(model, test_loader, epoch_idx, loss_function)
        train_losses.append(train_loss)
        test_losses.append(test_loss)


if __name__ == "__main__":
    if jt.has_cuda:
        jt.flags.use_cuda = 1
    parser = make_parser()
    task2(parser.parse_args())
