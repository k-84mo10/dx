import os


def delete_ds_store(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == ".DS_Store":
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")


if __name__ == "__main__":
    target_directory = os.path.join(
        os.path.expanduser("~/dx"), "data/data4/data4_1case_merged"
    )  # 対象のディレクトリのパスを指定してください

    delete_ds_store(target_directory)
