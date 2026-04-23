from pathlib import Path

from common.gdownload import download_folder_from_google_drive


def ensure_faiss_index_dir(
    directory: str = "data",
    folder_name: str = "faiss_index_high",
    folder_url: str | None = None,
) -> Path:
    """
    FAISS 인덱스 디렉토리 존재 여부를 확인하고, 없으면 Google Drive에서 다운로드한 뒤
    인덱스 파일(index.faiss, index.pkl)이 존재하는 디렉토리 경로를 반환한다.
    """
    base_dir = Path.cwd().resolve()
    parent_dir = base_dir / directory
    target_dir = parent_dir / folder_name

    expected_files = ("index.faiss", "index.pkl")

    def has_index_files(path: Path) -> bool:
        return all((path / file_name).is_file() for file_name in expected_files)

    # 1) folder_name 디렉토리 안에 이미 있으면 그대로 반환
    if target_dir.is_dir() and has_index_files(target_dir):
        return target_dir

    # 2) 상위 directory(data) 바로 아래에 이미 있으면 그것을 반환
    if parent_dir.is_dir() and has_index_files(parent_dir):
        return parent_dir

    if not folder_url:
        raise ValueError(
            f"FAISS 인덱스를 찾을 수 없고, 다운로드를 위한 folder_url도 제공되지 않았습니다."
        )

    parent_dir.mkdir(parents=True, exist_ok=True)

    download_folder_from_google_drive(
        folder_url=folder_url,
        output_dir=str(parent_dir),
    )

    # 3) 다운로드 후 folder_name 디렉토리 안 확인
    if target_dir.is_dir() and has_index_files(target_dir):
        return target_dir

    # 4) 다운로드 후 parent_dir 바로 아래 확인
    if has_index_files(parent_dir):
        return parent_dir

    raise FileNotFoundError(
        "Google Drive 다운로드 후에도 FAISS 인덱스 파일(index.faiss, index.pkl)을 찾을 수 없습니다. "
        f"확인 경로: {target_dir}, {parent_dir}"
    )
