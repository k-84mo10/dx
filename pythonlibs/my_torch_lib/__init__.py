import os
from random import triangular
from re import A

import japanize_matplotlib
import matplotlib.pyplot as plt
import numpy as np
import torch
from tqdm import tqdm

from pythonlibs.my_torch_lib.coins_cm import make_cm
from pythonlibs.my_torch_lib.coins_ls import make_ls


# 損失関数値計算用
def eval_loss(loader, device, net, criterion):
    # DataLoaderから最初の1セットを取得する
    for images, labels in loader:
        break

    # デバイスの割り当て
    inputs = images.to(device)
    labels = labels.to(device)

    # 予測値の計算
    outputs = net(inputs)

    #  損失値の計算
    loss = criterion(outputs, labels)

    return loss


# 学習用関数
def fit(
    net,
    optimizer,
    criterion,
    num_epochs,
    train_loader,
    test_loader,
    device,
    history,
    program_name,
    save_dir,
    which_data,
):
    base_epochs = len(history)

    classes = torch.tensor(
        [
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0, 1.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0, 0.0],
            [0.0, 1.0, 1.0, 1.0],
            [1.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0, 0.0],
            [1.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0, 0.0],
            [1.0, 1.0, 1.0, 1.0],
        ]
    )

    for epoch in range(base_epochs, num_epochs + base_epochs):
        # 1エポックあたりの正解数(精度計算用)
        n_train_acc = 0
        n_val_acc = np.array([0, 0, 0, 0, 0])
        # 1エポックあたりの累積損失(平均化前)
        train_loss, val_loss = 0, 0
        # 1エポックあたりのデータ累積件数
        n_train, n_test = 0, 0

        # 訓練フェーズ
        net.train()

        # train_progress_bar = tqdm(total=len(train_loader), leave=False)
        # for inputs, labels in train_loader:
        for inputs, labels in tqdm(train_loader, leave=False, disable=False):
            # 1バッチあたりのデータ件数
            train_batch_size = len(labels)
            # 1エポックあたりのデータ累積件数
            n_train += train_batch_size

            # GPUヘ転送
            inputs = inputs.to(device)
            labels = labels.to(device)

            # 勾配の初期化
            optimizer.zero_grad()

            # 予測計算
            outputs = net(inputs)

            # 損失計算
            loss = criterion(outputs, labels)

            # 勾配計算
            loss.backward()

            # パラメータ修正
            optimizer.step()

            # 予測ラベル導出
            predicted = torch.max(outputs, 1)[1]

            # 平均前の損失と正解数の計算
            # lossは平均計算が行われているので平均前の損失に戻して加算
            train_loss += loss.item() * train_batch_size
            n_train_acc += (predicted == labels).sum().item()

            # # Update the progress bar manually
            # train_progress_bar.update(1)

        # 予測フェーズ
        net.eval()

        for inputs_test, labels_test in test_loader:
            # 1バッチあたりのデータ件数
            test_batch_size = len(labels_test)
            # 1エポックあたりのデータ累積件数
            n_test += test_batch_size

            # GPUヘ転送
            inputs_test = inputs_test.to(device)
            labels_test = labels_test.to(device)

            # 予測計算
            outputs_test = net(inputs_test)

            # 損失計算
            loss_test = criterion(outputs_test, labels_test)

            # 予測ラベル導出
            predicted_test = torch.max(outputs_test, 1)[1]

            #  平均前の損失と正解数の計算
            # lossは平均計算が行われているので平均前の損失に戻して加算
            val_loss += loss_test.item() * test_batch_size
            for i in range(len(labels_test)):
                correct = (
                    (classes[predicted_test[i]] == classes[labels_test[i]]).sum().item()
                )
                n_val_acc[correct] += 1

        # # Close the progress bars
        # train_progress_bar.close()

        # 精度計算
        train_acc = n_train_acc / n_train
        val_acc = n_val_acc / n_test
        # 損失計算
        avg_train_loss = train_loss / n_train
        avg_val_loss = val_loss / n_test

        # 結果表示
        print(
            f"Epoch [{(epoch+1)}/{num_epochs+base_epochs}],"
            f"loss: {avg_train_loss:.5f} acc: {train_acc:.5f} val_loss: {avg_val_loss:.5f}, val_acc: {val_acc[4]:.5f}"
        )
        # 記録
        item = np.array([epoch + 1, avg_train_loss, train_acc, avg_val_loss, *val_acc])
        history = np.vstack((history, item))

        # モデルを保存
        if epoch == num_epochs:
            torch.save(
                net,
                os.path.join(
                    os.path.expanduser("~"),
                    "static",
                    f"{which_data}",
                    f"{program_name}",
                    f"epoch{epoch}.pth",
                ),
            )

        if epoch % 25 == 0 or epoch == num_epochs:
            make_cm(device, epoch, test_loader, save_dir, net)
            make_ls(device, epoch, test_loader, save_dir, net)

    return history


# 学習用関数
def fit_vec(
    net,
    optimizer,
    criterion,
    num_epochs,
    train_loader,
    test_loader,
    device,
    history,
    program_name,
    save_dir,
    which_data,
):
    base_epochs = len(history)

    classes = torch.tensor(
        [
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0, 1.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0, 0.0],
            [0.0, 1.0, 1.0, 1.0],
            [1.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0, 0.0],
            [1.0, 0.0, 1.0, 1.0],
            [1.0, 1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0, 0.0],
            [1.0, 1.0, 1.0, 1.0],
        ]
    )

    for epoch in range(base_epochs, num_epochs + base_epochs):
        # 1エポックあたりの正解数(精度計算用)
        n_train_acc = 0
        n_val_acc = np.array([0, 0, 0, 0, 0])
        # 1エポックあたりの累積損失(平均化前)
        train_loss, val_loss = 0, 0
        # 1エポックあたりのデータ累積件数
        n_train, n_test = 0, 0

        # 訓練フェーズ
        net.train()

        # train_progress_bar = tqdm(total=len(train_loader), leave=False)
        # for inputs, labels in train_loader:
        for inputs, labels in tqdm(train_loader, leave=False, disable=False):
            # 1バッチあたりのデータ件数
            train_batch_size = len(labels)
            # 1エポックあたりのデータ累積件数
            n_train += train_batch_size

            # GPUヘ転送
            inputs = inputs.to(device)
            labels = labels.to(device)

            # 勾配の初期化
            optimizer.zero_grad()

            # 予測計算
            outputs = net(inputs)

            labels_vec = torch.tensor(
                [classes[labels[i].item()] for i in range(len(labels))]
            ).to(device)
            # print(labels_vec)
            outputs_sig = torch.sigmoid(outputs)
            # 損失計算
            loss = criterion(outputs_sig, labels_vec) * len(classes[0])

            # 勾配計算
            loss.backward()

            # パラメータ修正
            optimizer.step()

            # 予測ラベル導出
            predicted = torch.where(outputs_sig < 0.5, 0.0, 1.0)

            # 平均前の損失と正解数の計算
            # lossは平均計算が行われているので平均前の損失に戻して加算
            train_loss += loss.item() * train_batch_size
            # n_train_acc += (predicted == labels).sum().item()
            for i in range(len(labels)):
                correct = (predicted[i] == labels_vec[i]).sum().item()
                if correct == 4:
                    n_train_acc += 1

            # # Update the progress bar manually
            # train_progress_bar.update(1)

        # 予測フェーズ
        net.eval()

        for inputs_test, labels_test in test_loader:
            # 1バッチあたりのデータ件数
            test_batch_size = len(labels_test)
            # 1エポックあたりのデータ累積件数
            n_test += test_batch_size

            # GPUヘ転送
            inputs_test = inputs_test.to(device)
            labels_test = labels_test.to(device)

            # 予測計算
            outputs_test = net(inputs_test)

            # 損失計算
            outputs_test_sig = torch.sigmoid(outputs_test)
            labels_test_vec = torch.tensor(
                [classes[labels_test[i].item()] for i in range(len(labels_test))]
            ).to(device)
            loss_test = criterion(outputs_test_sig, labels_test_vec) * len(classes[0])

            # 予測ラベル導出
            predicted_test = torch.where(outputs_test_sig < 0.5, 0.0, 1.0)

            #  平均前の損失と正解数の計算
            # lossは平均計算が行われているので平均前の損失に戻して加算
            val_loss += loss_test.item() * test_batch_size
            for i in range(len(labels_test)):
                correct = (
                    (classes[predicted_test[i]] == classes[labels_test[i]]).sum().item()
                )
                n_val_acc[correct] += 1

        # # Close the progress bars
        # train_progress_bar.close()

        # 精度計算
        train_acc = n_train_acc / n_train
        val_acc = n_val_acc / n_test
        # 損失計算
        avg_train_loss = train_loss / n_train
        avg_val_loss = val_loss / n_test
        # 結果表示
        print(
            f"Epoch [{(epoch+1)}/{num_epochs+base_epochs}],"
            f"loss: {avg_train_loss:.5f} acc: {train_acc:.5f} val_loss: {avg_val_loss:.5f}, val_acc: {val_acc:.5f}"
        )
        # 記録
        item = np.array([epoch + 1, avg_train_loss, train_acc, avg_val_loss, *val_acc])
        history = np.vstack((history, item))

        # モデルを保存
        if epoch == num_epochs:
            torch.save(
                net,
                os.path.join(
                    os.path.expanduser("~"),
                    "static",
                    f"{which_data}",
                    f"{program_name}",
                    f"epoch{epoch}.pth",
                ),
            )

        if epoch % 25 == 0 or epoch == num_epochs:
            make_cm(device, epoch, test_loader, save_dir, net)
            make_ls(device, epoch, test_loader, save_dir, net)

    return history


# 学習ログ解析
def evaluate_history(history, program_name, save_dir):
    # 損失と精度の確認
    max_index = history[:, 8].argmax()

    result_f = open(
        f"{save_dir}/{program_name}_abst.txt",
        "w",
        newline="\n",
    )
    datalines = [
        f"初期状態: 損失: {history[0,3]:.5f} 精度: {history[0,8]:.5f}\n",
        f"最終状態: 損失: {history[-1,3]:.5f} 精度: {history[-1,8]:.5f}\n",
        f"max: 損失: {history[max_index,3]:.5f} 精度: {history[max_index,8]:.5f}\n",
    ]
    result_f.writelines(datalines)
    result_f.close()

    num_epochs = len(history)
    if num_epochs < 10:
        unit = 1
    else:
        unit = num_epochs / 10

    # 学習曲線の表示 (損失)
    plt.figure(figsize=(9, 8))
    plt.plot(history[:, 0], history[:, 1], "b", label="訓練")
    plt.plot(history[:, 0], history[:, 3], "k", label="検証")
    plt.xticks(np.arange(0, num_epochs + 1, unit))
    plt.xlabel("繰り返し回数")
    plt.ylabel("損失")
    plt.title("学習曲線(損失)")
    plt.legend()
    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(os.path.join(save_dir, f"{program_name}_loss.png"))
    plt.show()

    # 学習曲線の表示 (精度)
    plt.figure(figsize=(9, 8))
    plt.plot(history[:, 0], history[:, 2], "b", label="訓練")
    plt.plot(history[:, 0], history[:, 4], "k", label="検証")
    plt.xticks(np.arange(0, num_epochs + 1, unit))
    plt.xlabel("繰り返し回数")
    plt.ylabel("精度")
    plt.title("学習曲線(精度)")
    plt.legend()
    plt.savefig(os.path.join(save_dir, f"{program_name}_acc.png"))
    plt.show()


# イメージとラベル表示
def show_images_labels(loader, classes, net, device, program_name, save_dir):
    # DataLoaderから最初の1セットを取得する
    for images, labels in loader:
        break
    # 表示数は50個とバッチサイズのうち小さい方
    n_size = min(len(images), 50)

    if net is not None:
        # デバイスの割り当て
        inputs = images.to(device)
        labels = labels.to(device)

        # 予測計算
        outputs = net(inputs)
        predicted = torch.max(outputs, 1)[1]
        # images = images.to('cpu')

    # 最初のn_size個の表示
    plt.figure(figsize=(20, 15))
    for i in range(n_size):
        ax = plt.subplot(5, 10, i + 1)
        label_name = classes[labels[i]]
        # netがNoneでない場合は、予測結果もタイトルに表示する
        if net is not None:
            predicted_name = classes[predicted[i]]
            # 正解かどうかで色分けをする
            if label_name == predicted_name:
                c = "k"
            else:
                c = "b"
            ax.set_title(label_name + ":" + predicted_name, c=c, fontsize=20)
        # netがNoneの場合は、正解ラベルのみ表示
        else:
            ax.set_title(label_name, fontsize=20)
        # TensorをNumPyに変換
        image_np = images[i].numpy().copy()
        # 軸の順番変更 (channel, row, column) -> (row, column, channel)
        img = np.transpose(image_np, (1, 2, 0))
        # 値の範囲を[-1, 1] -> [0, 1]に戻す
        img = (img + 1) / 2
        # 結果表示
        plt.imshow(img)
        ax.set_axis_off()
    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(os.path.join(save_dir, f"{program_name}_images.png"))
    # plt.savefig("/mnt/image_labels.png")
    plt.show()


# PyTorch乱数固定用
def torch_seed(seed=123):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms = True
