import csv
import logging
import openpyxl
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
os.makedirs(BASE_DIR / "reports" / "csv", exist_ok=True)
os.makedirs(BASE_DIR / "reports" / "xlsx", exist_ok=True)

CSV_DIR = BASE_DIR / "reports/csv"
XLSX_DIR = BASE_DIR / "reports/xlsx"

logger = logging.getLogger(__name__)

def check_filename(path: Path, filename: str) -> str:
    if (path / filename).exists():
        original = Path(filename)
        num = 1
        new_filename = f"{original.stem}_{num}{original.suffix}"
        while (path / new_filename).exists():
            num += 1
            new_filename = f"{original.stem}_{num}{original.suffix}"
        logger.warning(f"File with name {filename} already exists. Report will be saved as {new_filename}")
        return new_filename
    else:
        return filename

def clean_reports_repos(repo: Path, num2leave: int) -> None:
    files = [p for p in repo.iterdir() if p.is_file()]
    files.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
    if num2leave < len(files):
        logger.info(f"Start deleting {len(files)-num2leave} oldest files from {repo}")
        for old_file in files[num2leave:]:
            old_file.unlink()
        logger.info(f"Repo is cleaned to {num2leave} files")
    else:
        logger.info(f"Repo has already less or equal to {num2leave} files")

def export2csv(filename: str, headers: list[str], data: list[list[str]], num2store: int) -> None:
    logger.info(f"Start saving results to {filename}")
    if num2store < 1:
        num2store = 3
        logger.warning("Number of files to store must be positive. Taking default=3")

    filename = check_filename(CSV_DIR, filename)

    with open(CSV_DIR / filename, 'w', encoding='utf-8') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow(headers)
        writer.writerows(data)
    logger.info("Report saved in csv format")

    clean_reports_repos(CSV_DIR, num2store)

def export2xlsx(filename: str, headers: list[str], data: list[list[str]], num2store: int) -> None:
    logger.info(f"Start saving results to {filename}")
    if num2store < 1:
        num2store = 3
        logger.warning("Number of files to store must be positive. Taking default=3")

    filename = check_filename(XLSX_DIR, filename)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Books Info"
    ws.append(headers)
    for row in data:
        ws.append(row)
    wb.save(XLSX_DIR / filename)
    logger.info("Report saved in xlsx format")


    clean_reports_repos(XLSX_DIR, num2store)