import os
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import JSONResponse
from app.utils.unzipper import clear_dir, extract_zip
from app.llm.query_handler import ask_llm

router = APIRouter()

UPLOAD_DIR = "uploads"
EXTRACT_DIR = "extracted_dataset"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

def count_images(p: Path) -> int:
    return sum(1 for f in p.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXTS)

def scan_dataset_and_save_manifest(dataset_path: str):
    dataset_path = Path(dataset_path)
    manifest = {"root": str(dataset_path), "classes": [], "counts": {}}
    if not dataset_path.exists():
        return manifest

    current = dataset_path
    while True:
        dirs = [d for d in current.iterdir() if d.is_dir()]
        files = [f for f in current.iterdir() if f.is_file()]
        has_images_here = any(f.suffix.lower() in IMG_EXTS for f in files)
        if len(dirs) == 1 and not has_images_here:
            current = dirs[0]
        else:
            break

    top_dirs = [d for d in current.iterdir() if d.is_dir()]
    split_names = {"train", "val", "test"}

    if top_dirs and all(d.name.lower() in split_names for d in top_dirs):
        for split in top_dirs:
            split_key = split.name.lower()
            manifest["counts"][split_key] = {}
            for cls_dir in split.iterdir():
                if cls_dir.is_dir():
                    c = count_images(cls_dir)
                    if c > 0:
                        cls_name = cls_dir.name.strip().lower()
                        manifest["classes"].append(cls_name)
                        manifest["counts"][split_key][cls_name] = c
        manifest["classes"] = sorted(list(set(manifest["classes"])))
    elif top_dirs:
        for cls_dir in top_dirs:
            if cls_dir.is_dir():
                c = count_images(cls_dir)
                if c > 0:
                    cls_name = cls_dir.name.strip().lower()
                    manifest["classes"].append(cls_name)
                    manifest["counts"][cls_name] = c
        manifest["classes"] = sorted(list(set(manifest["classes"])))
    else:
        c = count_images(current)
        if c > 0:
            manifest["classes"].append("root")
            manifest["counts"]["root"] = c

    manifest_path = Path(EXTRACT_DIR) / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[DEBUG] Classes detected: {manifest['classes']}")
    return manifest

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    clear_dir(UPLOAD_DIR)
    clear_dir(EXTRACT_DIR)

    zip_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(zip_path, "wb") as f:
        f.write(await file.read())

    extracted_path = extract_zip(zip_path, EXTRACT_DIR)

    # Single wrapper folder
    current = Path(extracted_path)
    while True:
        items = [i for i in current.iterdir() if i.is_dir()]
        files = [i for i in current.iterdir() if i.is_file()]
        has_images = any(f.suffix.lower() in IMG_EXTS for f in files)
        if len(items) == 1 and not has_images:
            current = items[0]
        else:
            break

    manifest = scan_dataset_and_save_manifest(str(current))

    return JSONResponse({
        "message": "Dataset uploaded and scanned successfully",
        "num_classes": len(manifest["classes"]),
        "classes": manifest["classes"],
        "counts": manifest["counts"]
    })

@router.post("/ask")
async def ask_dataset_question(request: Request):
    body = await request.json()
    question = body.get("query") or body.get("question")
    
    manifest_path = Path(EXTRACT_DIR) / "manifest.json"

    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
    else:
        manifest = scan_dataset_and_save_manifest(EXTRACT_DIR)

    classes = manifest.get("classes", [])
    counts = manifest.get("counts", {})

    if not classes:
        return JSONResponse({
            "question": question,
            "answer": "No classes detected. Please re-upload dataset.",
            "classes": [],
            "num_classes": 0,
            "counts": {}
        })

    prompt = f"""
You are a dataset assistant.

Dataset Info:
Number of classes: {len(classes)}
Classes: {classes}
Counts: {json.dumps(counts)}

Question: {question}
"""
    answer = ask_llm(prompt)

    return JSONResponse({
        "question": question,
        "answer": answer,
        "classes": classes,
        "num_classes": len(classes),
        "counts": counts
    })
