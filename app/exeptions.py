from fastapi import HTTPException, status


class NoteFoundException(HTTPException):
    def __init__(self, note_text: str, note_image: str = ""):
        detail = {
            "response": "ok",
            "note_final_text": note_text,
            "note_image": note_image,
        }
        super().__init__(status_code=status.HTTP_200_OK, detail=detail)
