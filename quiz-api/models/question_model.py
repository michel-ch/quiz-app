import base64
import re
from models.answer_model import Answer

class Question:
    def __init__(self, title, position, text, image_bytes: bytes, possible_answers=None,question_id=None):
        self.id = question_id
        self.title = title
        self.position = position
        self.text = text
        self.image = image_bytes
        self.possible_answers = possible_answers if possible_answers is not None else []

def question_from_json(json_data):
    image_base64 = json_data.get('image', '')
    image_bytes = b''

    if image_base64:
        try:
            if image_base64.startswith("data:"):
                match = re.match(r"^data:.*?;base64,(.*)$", image_base64)
                if match:
                    image_base64 = match.group(1)
                else:
                    raise ValueError("Invalid data URI format for image")
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            error_msg = str(e)
            if "number of data characters" in error_msg and "cannot be 1 more than a multiple of 4" in error_msg:
                print("Invalid base64 padding, skipping image decode: %s", error_msg)
                image_bytes = image_base64.encode('utf-8')
            else:
                raise ValueError("Image is not valid base64")

    answers = [
        Answer(
            text=a['text'],
            is_correct=a['isCorrect'],
            latitude=a.get('latitude'),
            longitude=a.get('longitude')
        )
        for a in json_data.get("possibleAnswers", [])
    ]

    return Question(
        title=json_data.get('title'),
        position=json_data.get('position'),
        text=json_data.get('text'),
        image_bytes=image_bytes,
        possible_answers=answers
    )

def question_to_json(question):
    image_base64 = ''
    if question.image:
        try:
            image_base64 = question.image.decode('utf-8')
        except UnicodeDecodeError:
            image_base64 = base64.b64encode(question.image).decode('utf-8')

    return {
        "id": question.id,
        "title": question.title,
        "position": question.position,
        "text": question.text,
        "image": image_base64,
        "possibleAnswers": [
            {
                k: v for k, v in {
                    "text": answer.text,
                    "isCorrect": answer.is_correct,
                    "latitude": answer.latitude,
                    "longitude": answer.longitude
                }.items() if v is not None
            }
            for answer in question.possible_answers
        ]
    }
