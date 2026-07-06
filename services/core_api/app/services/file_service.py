import asyncio


class FileService:
    @staticmethod
    async def process_document(file_content: bytes, filename: str) -> dict:
        # Placeholder for OCR/Parsing logic
        await asyncio.sleep(2)  # Simulate processing

        file_extension = filename.split(".")[-1].lower()

        return {
            "filename": filename,
            "status": "success",
            "parsed_text": f"This is placeholder extracted text from {filename}. In a real scenario, this would contain OCR results.",
            "entities_found": ["Contract", "Landlord", "Tenant", "Notice Period"],
            "document_type": file_extension.upper(),
        }
