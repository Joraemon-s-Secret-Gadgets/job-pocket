from pathlib import Path
import gdown


def download_folder_from_google_drive(folder_url: str, output_dir: str) -> Path:
    """
    Google Drive 폴더를 지정한 경로에 다운로드한다.

    Args:
        folder_url (str): Google Drive 폴더 URL
        output_dir (str): 다운로드 대상 상위 디렉토리

    Returns:
        Path: 다운로드 경로
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    gdown.download_folder(
        url=folder_url,
        output=str(output_path),
        quiet=False,
        use_cookies=False,
    )

    return output_path
