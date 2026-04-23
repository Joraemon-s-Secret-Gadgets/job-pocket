from pathlib import Path


def get_existing_path(directory: str, filename: str) -> Path:
    """
    현재 작업 디렉토리(app)를 기준으로 특정 파일이 존재하는지 확인하고,
    존재할 경우 해당 파일의 절대 경로를 반환한다.

    Docker 또는 실행 환경에서 working directory가 `app`으로 설정되어 있으므로,
    Path.cwd()를 기준으로 경로를 구성한다.

    Args:
        directory (str): 확인할 하위 디렉토리 (app 기준)
        filename (str): 확인할 파일명

    Returns:
        Path: 존재하는 파일의 절대 경로

    Raises:
        TypeError: directory 또는 filename이 문자열이 아닐 경우
        FileNotFoundError: 디렉토리 또는 파일이 존재하지 않을 경우

    Example:
        >>> path = get_existing_path("data", "sample.csv")
        >>> print(path)
        /app/data/sample.csv
    """

    if not isinstance(directory, str):
        raise TypeError("directory는 문자열(str)이어야 합니다.")

    if not isinstance(filename, str):
        raise TypeError("filename은 문자열(str)이어야 합니다.")

    base_dir = Path.cwd()
    target_dir = base_dir / directory
    target_file = target_dir / filename

    # 디렉토리 존재 + 디렉토리인지 확인
    if not target_dir.is_dir():
        raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {target_dir}")

    # 파일 존재 + 파일인지 확인
    if not target_file.is_file():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {target_file}")

    return target_file
