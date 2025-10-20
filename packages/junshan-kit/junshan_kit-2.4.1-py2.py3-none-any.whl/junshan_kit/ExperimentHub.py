import sys, os, torch, random
import numpy as np
import torch.nn as nn
import torch.utils.data as Data
from torch.utils.data import Subset, random_split
from junshan_kit import ComOptimizers, datahub, Models, TrainingParas, SPBM

# -------------------------------------
def set_seed(seed=42):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def device(Paras):
    device = torch.device(f"{Paras['cuda']}" if torch.cuda.is_available() else "cpu")
    Paras["device"] = device
    use_color = sys.stdout.isatty()
    Paras["use_color"] = use_color

    return Paras

# -------------------------------------
class Train_Steps:
    def __init__(self, args) -> None:
        self.args = args

    def _model_map(self, model_name):
        model_mapping = self.args.model_mapping

        return model_mapping[model_name]
    
    def get_train_group(self):
        training_group = []
        for cfg in self.args.train_group:
            model, dataset, optimizer = cfg.split("-")
            training_group.append((self._model_map(model), dataset, optimizer))

        return training_group
    
    def set_paras(self, results_folder_name, py_name, time_str, OtherParas):
        Paras = {
        # Name of the folder where results will be saved.
        "results_folder_name": results_folder_name,
        # Whether to draw loss/accuracy figures.
        "DrawFigs": "ON",
        # Whether to use log scale when drawing plots.
        "use_log_scale": "ON",
        # Print loss every N epochs.
        "epoch_log_interval": 1,
        # Timestamp string for result saving.
        "time_str": time_str,
        # Random seed
        "seed": OtherParas['seed'],
        # Device used for training.
        "cuda": f"cuda:{self.args.cuda}",

        # batch-size 
        "batch_size": self.args.bs,

        # epochs
        "epochs": self.args.e,

        # split_train_data
        "split_train_data": self.args.s,

        # select_subset
        "select_subset": self.args.subset,

        # subset_number_dict
        "subset_number_dict": TrainingParas.subset_number_dict(OtherParas),

        # validation
        "validation": TrainingParas.validation(),

        # validation_rate
        "validation_rate": TrainingParas.validation_rate(),

        # model list
        "model_list" : TrainingParas.model_list(),

        # model_type
        "model_type": TrainingParas.model_type(),

        # data_list
        "data_list": TrainingParas.data_list(),

        # optimizer_dict
        "optimizer_dict": TrainingParas.optimizer_dict(OtherParas)
        }
        Paras["py_name"] = py_name
        
        return Paras
    
    # <Step_3> : Chosen_loss
    def chosen_loss(self, model_name, Paras):
        # ---------------------------------------------------
        # There have an addition parameter
        if model_name == "LogRegressionBinaryL2":
            Paras["lambda"] = 1e-3
        # ---------------------------------------------------

        if model_name in ["LeastSquares"]:
            loss_fn = nn.MSELoss()

        else:
            if Paras["model_type"][model_name] == "binary":
                loss_fn = nn.BCEWithLogitsLoss()

            elif Paras["model_type"][model_name] == "multi":
                loss_fn = nn.CrossEntropyLoss()

            else:
                loss_fn = nn.MSELoss()
                print("\033[91m The loss function is error!\033[0m")
                assert False
        Paras["loss_fn"] = loss_fn

        return loss_fn, Paras
    
    # <Step_4> : import data --> step.py
    def load_data(self, model_name, data_name, Paras):
        # load data
        train_path = f"./exp_data/{data_name}/training_data"
        test_path = f"./exp_data/{data_name}/test_data"
        # Paras["train_ratio"] = 1.0
        # Paras["select_subset"].setdefault(data_name, False)
        # Paras["validation"].setdefault(data_name, False)

        if data_name == "MNIST":
            train_dataset, test_dataset, transform = datahub.MNIST(Paras, model_name)

        elif data_name == "CIFAR100":
            train_dataset, test_dataset, transform = datahub.CIFAR100(Paras, model_name)

        elif data_name == "CALTECH101_Resize_32":
            Paras["train_ratio"] = 0.7
            train_dataset, test_dataset, transform = datahub.caltech101_Resize_32(
                Paras["seed"], Paras["train_ratio"], split=True
            )

        elif data_name in ["Vowel", "Letter", "Shuttle", "w8a"]:
            Paras["train_ratio"] = Paras["split_train_data"][data_name]
            train_dataset, test_dataset, transform = datahub.get_libsvm_data(
                train_path + ".txt", test_path + ".txt", data_name
            )

        elif data_name in ["RCV1", "Duke", "Ijcnn"]:
            Paras["train_ratio"] = Paras["split_train_data"][data_name]
            train_dataset, test_dataset, transform = datahub.get_libsvm_bz2_data(
                train_path + ".bz2", test_path + ".bz2", data_name, Paras
            )

        else:
            transform = None
            print(f"The data_name is error!")
            assert False

        return train_dataset, test_dataset, transform
    # <Step_4>

    # <subset> : Step 5.1 -->step.py
    def set_subset(self, data_name, Paras, train_dataset, test_dataset):
        if self.args.subset[0]>1:
            train_num = self.args.subset[0]
            test_num = self.args.subset[1]
            train_subset_num = min(train_num, len(train_dataset))
            test_subset_num = min(test_num, len(test_dataset))

            train_subset_indices = list(range(int(train_subset_num)))
            train_dataset = Subset(train_dataset, train_subset_indices)

            test_subset_indices = list(range(int(test_subset_num)))
            test_dataset = Subset(test_dataset, test_subset_indices)
            
        else:
            train_ratios= self.args.subset[0]
            test_ratios= self.args.subset[1]

            train_subset_indices = list(range(int(train_ratios * len(train_dataset))))
            train_dataset = Subset(train_dataset, train_subset_indices)

            test_subset_indices = list(range(int(test_ratios * len(test_dataset))))
            test_dataset = Subset(test_dataset, test_subset_indices)

        return train_dataset, test_dataset

    # <validation> : Step 5.2   --> step.py
    def set_val_set(self, data_name, train_dataset, Paras):
        if Paras["validation"][data_name]:
            size_ = len(train_dataset)
            val_size = int(size_ * Paras["validation_rate"][data_name])
            train_size = size_ - val_size

            train_dataset, val_dataset = random_split(
                train_dataset,
                [train_size, val_size],
                generator=torch.Generator().manual_seed(Paras["seed"]),
            )

        else:
            val_dataset = Subset(train_dataset, [])

        return train_dataset, val_dataset
    # <validation>


    # <get_dataloader> Step 5.3 -->step.py
    def get_dataloader(self, data_name, train_dataset, test_dataset, Paras):
        set_seed(Paras["seed"])
        g = torch.Generator()
        g.manual_seed(Paras["seed"])

        # Create training DataLoader
        
        train_loader = Data.DataLoader(
            dataset=train_dataset,
            shuffle=True,
            batch_size=self.args.bs,
            generator=g,
            num_workers=4,
        )

        # test loader
        test_loader = Data.DataLoader(
            dataset=test_dataset,
            shuffle=False,
            batch_size=self.args.bs,
            generator=g,
            num_workers=4,
        )
    
        return train_loader, test_loader
    # <get_dataloader>

    def hyperparas_and_path(
        self,
        model_name,
        data_name,
        optimizer_name,
        Paras,
    ):
        params_gird = Paras["optimizer_dict"][optimizer_name]["params"]
        keys, values = list(params_gird.keys()), list(params_gird.values())

        # Set the path for saving results
        folder_path = f'./{Paras["results_folder_name"]}/seed_{Paras["seed"]}/{model_name}/{data_name}/{optimizer_name}/train_{Paras["train_data_num"]}_test_{Paras["test_data_num"]}/Batch_size_{self.args.bs}/epoch_{self.args.e}/{Paras["time_str"]}'
        os.makedirs(folder_path, exist_ok=True)

        return keys, values, folder_path

    
    # <Reloading> Step 7.3 --> step.py
    def reloading_model_dataloader(self,
        base_model_fn,
        initial_state_dict,
        data_name,
        train_dataset,
        test_dataset,
        Paras,
    ):
        set_seed(Paras["seed"])
        model = base_model_fn()
        model.load_state_dict(initial_state_dict)
        model.to(Paras["device"])
        train_loader, test_loader = self.get_dataloader(
            data_name, train_dataset, test_dataset, Paras
        )

        return model, train_loader, test_loader
    # <Reloading>

    def chosen_optimizer(self, optimizer_name, model, hyperparams, Paras):
        if optimizer_name == "SGD":
            optimizer = torch.optim.SGD(model.parameters(), lr=hyperparams["alpha"])

        elif optimizer_name == "ADAM":
            optimizer = torch.optim.Adam(
                model.parameters(),
                lr=hyperparams["alpha"],
                betas=(hyperparams["beta1"], hyperparams["beta2"]),
                eps=hyperparams["epsilon"],
            )

        elif optimizer_name in ["SPBM-TR"]:
            optimizer = SPBM.TR(model.parameters(), model, hyperparams, Paras)

        elif optimizer_name in ["SPBM-TR-NoneLower"]:
            optimizer = SPBM.TR_NoneLower(model.parameters(), model, hyperparams, Paras)
        
        elif optimizer_name in ["SPBM-TR-NoneSpecial"]:
            optimizer = SPBM.TR_NoneSpecial(model.parameters(), model, hyperparams, Paras)
        
        elif optimizer_name in ["SPBM-TR-NoneCut"]:
            optimizer = SPBM.TR_NoneCut(model.parameters(), model, hyperparams, Paras)

        elif optimizer_name in ["SPBM-PF-NoneLower"]:
            optimizer = SPBM.PF_NoneLower(model.parameters(), model, hyperparams, Paras)

        elif optimizer_name in ["SPBM-PF"]:
            optimizer = SPBM.PF(model.parameters(), model, hyperparams, Paras)
        
        elif optimizer_name in ["SPBM-PF-NoneCut"]:
            optimizer = SPBM.PF_NoneCut(model.parameters(), model, hyperparams, Paras)

        elif optimizer_name in ["SPSmax"]:
            optimizer = ComOptimizers.SPSmax(
                model.parameters(), model, hyperparams, Paras
            )

        elif optimizer_name in ["ALR-SMAG"]:
            optimizer = ComOptimizers.ALR_SMAG(
                model.parameters(), model, hyperparams, Paras
            )

        elif optimizer_name in ["Bundle"]:
            optimizer = ComOptimizers.Bundle(
                model.parameters(), model, hyperparams, Paras
            )

        else:
            raise NotImplementedError(f"{optimizer_name} is not supported.")

        return optimizer

    
