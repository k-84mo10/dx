import cv2
import numpy as np

# 画像を読み込む
image = cv2.imread(
    os.path.join(os.path.expanduser("~/dx"), "data/data4_1case/0010/IMG_0310.JPG")
)
# コントラストと明るさの変更
alpha = 0.5  # コントラストの倍率（1より大きい値でコントラストが上がる）
beta = 10  # 明るさの調整値（正の値で明るくなる）
darkened_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
cv2.imwrite("darkened_image.jpg", darkened_image)

# 画像Aと画像Bの横幅を取得
width = image.shape[1]

# 合成したい新しい画像を作成
result = np.zeros_like(image)

# シグモイド関数のパラメータを設定
a = 10  # シグモイド関数の傾斜を調整するパラメータ

# 画像Aと画像Bをシグモイド関数を使用して合成
for x in range(width):
    ratio = 1 / (1 + np.exp(-a * (x / width - 0.5)))
    result[:, x] = (image[:, x] * ratio + darkened_image[:, x] * (1 - ratio)).astype(
        np.uint8
    )


# 合成された画像を保存または表示
cv2.imwrite("result_sigmoid.jpg", result)
