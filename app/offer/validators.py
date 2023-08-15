from fastapi import UploadFile, File

SIGNATURES = {
    'JPEG': ['FF D8 FF DB', 'FF D8 FF E0', 'FF D8 FF E1'],
    'PDF': ['25 50 44 46 2D'],
    'PNG': ['89 50 4E 47 0D 0A 1A 0A'],
    'DOCX': ['50 4B 03 04 14 00 06 00'],
    'DOC': ['EC A5 C1 00']
}


def check_file_signature(file: UploadFile = File(...)):
    hex_bytes = ' '.join(['{:02X}'.format(byte) for byte in file.file.read(8)])
    ct = file.content_type
    extension = ct[ct.find('/') + 1:]
    is_verified = False
    for signature in SIGNATURES[extension.upper()]:
        if signature in hex_bytes:
            is_verified = True
        if is_verified:
            file.file.seek(0)
            return is_verified
    return is_verified


