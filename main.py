import pdfplumber
import re


class QuizCard:
    def __init__(self, card_type="", ref="", club="", question="", answer=""):
        self.card_type = card_type
        self.ref = ref
        self.club = club
        self.question = question
        self.answer = answer

    def __str__(self):
        return f"Type: {self.card_type}\nRef: {self.ref}\nClub: {self.club}\nQ: {self.question}\nA: {self.answer}\n"


def parse_pdf(file_path):
    cards = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.splitlines()
                current_card = QuizCard()
                for line in lines:
                    line = line.strip()
                    if line:  # Ignore empty lines
                        if line.startswith("Type:"):
                            current_card.card_type = line[len("Type:") :].strip()
                        elif line.startswith("Ref:"):
                            current_card.ref = line[len("Ref:") :].strip()
                        elif line.startswith("Club:"):
                            current_card.club = line[len("Club:") :].strip()
                        elif line.startswith("Question:"):
                            current_card.question = line[len("Question:") :].strip()
                        elif line.startswith("Answer:"):
                            current_card.answer = line[len("Answer:") :].strip()
                            cards.append(
                                current_card
                            )  # Append the card when the answer is set
                            current_card = QuizCard()  # Reset for the next card

    return cards


def main():
    file_path = "/home/amberson/Code/quiz-cards/Practice-Questions-Through-Acts-12.pdf"
    cards = parse_pdf(file_path)

    for card in cards:
        print(card)


if __name__ == "__main__":
    main()
