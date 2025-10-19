from .functions import (clean_text,
                        re,
                        write_to_file,
                        cv2,np,
                        pytesseract,
                        Image,
                        sort_frames)
def preprocess_for_ocr(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)

    # Denoise
    denoised = cv2.bilateralFilter(contrast, d=9, sigmaColor=75, sigmaSpace=75)

    # Thresholding
    thresh = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=11,
        C=2
    )
    # Sharpen
    kernel = np.ones((3, 3), np.uint8)
    morph = cv2.dilate(thresh, kernel, iterations=1)    
    sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened = cv2.filter2D(thresh, -1, sharpen_kernel)

    return sharpened
def extract_text_from_image(image_path: str) -> str:
    try:
        processed_img = preprocess_for_ocr(image_path)
        pil_img = Image.fromarray(cv2.bitwise_not(processed_img))  # invert for OCR
        text = pytesseract.image_to_string(pil_img, lang='eng')
        return text
    except Exception as e:
        print(f"[OCR Error] {e}")
        return ""
def is_frame_analyzed(frame_file,video_text_data):
    for values in video_text_data:
        frame = values
        if isinstance(values,dict):
            frame = values.get("frame")
        if frame_file == frame:
            return True
def extract_image_text(image_path,remove_phrases=None):
    remove_phrases = remove_phrases or []
    if confirm_type(image_path,media_types=['image']):
        raw_text = extract_text_from_image(image_path)
        cleaned_text = clean_text(raw_text)
        text = determine_remove_text(cleaned_text,remove_phrases=info_data['remove_phrases'])
        return text
def extract_text_from_frame(image_path,):
    basename = os.pth.basename(image_path,image_texts)
    if not is_frame_analyzed(basename,video_text):
        text = extract_image_text(image_path,remove_phrases)
        return {"frame": basename, "text": text}
def extract_image_texts_from_directory(directory,image_texts=None,remove_phrases=None):
    image_texts = image_texts or []
    image_files = get_all_file_types(types=['image'],directory=directory)
    for i,image_path in enumerate(image_files):
        extracted_text = extract_text_from_frame(image_path,image_texts)
        if extracted_text:
            image_texts.append(extracted_text)
    image_texts = sort_frames(image_texts)
    return image_texts

def download_pdf(url: str, output_path: str):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"PDF downloaded successfully: {output_path}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
is_start = False
# Helper functions (as defined previously)
def preprocess_image(image_path: str, output_path: str) -> None:
    img = preprocess_for_ocr(image_path)
    cv2.imwrite(output_path, sharpened)
    return output_path

def convert_image_to_text(image_path: str,preprocess=True) -> str:
    try:
        if preprocess:
            img = preprocess_for_ocr(image_path: str)
        else:
            img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='eng')
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""




