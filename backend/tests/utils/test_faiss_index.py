from utils.faiss_index import ensure_faiss_index_dir

FAISS_URL = "https://drive.google.com/drive/folders/1y7UKpJGDh-wMI2koNVzWywXW7sL-ee3D"


def test_ensure_faiss_index_dir_download():
    path = ensure_faiss_index_dir(
        directory="data",
        folder_name="faiss_index_high",
        folder_url=FAISS_URL,
    )

    assert path.exists(), "FAISS 폴더가 생성되지 않음"
    assert path.is_dir(), "FAISS 경로가 디렉토리가 아님"
