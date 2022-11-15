import os
import pickle
import numpy as np
from jittor.dataset import Dataset
import jittor as jt


class CIFAR10P(Dataset):
    base_folder = "cifar-10-batches-py"
    train_list = ["data_batch_1", "data_batch_2", "data_batch_3", "data_batch_4", "data_batch_5"]
    test_list = ["test_batch"]
    meta = {"filename": "batches.meta", "key": "label_names"}

    def __init__(self, train=True, batch_size=64, drop_last=False, shuffle=True, root="cifar_data/"):
        super(CIFAR10P, self).__init__(batch_size=batch_size, drop_last=drop_last, shuffle=shuffle)
        self.root = root
        self.train = train
        if self.train:
            downloaded_list = self.train_list
        else:
            downloaded_list = self.test_list
        self.data, self.targets = [], []
        for file_name in downloaded_list:
            file_path = os.path.join(self.root, self.base_folder, file_name)
            with open(file_path, "rb") as f:
                entry = pickle.load(f, encoding="latin1")
                self.data.append(entry["data"])
                if "labels" in entry:
                    self.targets.extend(entry["labels"])
                else:
                    self.targets.extend(entry["fine_labels"])
        self.data = np.vstack(self.data).reshape(-1, 3, 32, 32)
        self._load_meta()
        self.H = self.data.shape[2] // 2
        self.W = self.data.shape[3] // 2

    def _load_meta(self):
        path = os.path.join(self.root, self.base_folder, self.meta["filename"])
        with open(path, "rb") as infile:
            data = pickle.load(infile, encoding="latin1")
            self.classes = data[self.meta["key"]]
        self.class_to_idx = {_class: i for i, _class in enumerate(self.classes)}

    def __getitem__(self, index):
        img = self.data[index]
        cutted = [img[:, :self.H, :self.W], img[:, :self.H, self.W:], img[:, self.H:, :self.W], img[:, self.H:, self.W:]]
        stacked = np.stack(cutted, axis=0)
        permutation_order = jt.randperm(4)
        permuted = stacked[permutation_order]
        label = np.zeros(shape=(4, 4), dtype=np.int32)
        for i in range(4):
            label[i, permutation_order[i]] = 1
        return permuted, label.reshape(-1, 1)

    def __len__(self):
        return len(self.data)
          


if __name__ == "__main__":

    train_data = CIFAR10P(train=True, batch_size=64)
    img, label = train_data[0]
    
    for _, (img, label) in enumerate(train_data):
        print(img.shape)
        print(label.shape)
        break