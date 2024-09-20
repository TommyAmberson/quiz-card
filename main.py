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
        return (
            f"Type: {self.card_type}\n"
            f"Ref: {self.ref}\n"
            f"Club: {self.club}\n"
            f"Q: {self.question}\n"
            f"A: {self.answer}\n"
        )


def parse_pdf(file_path):
    cards = []
    current_card = QuizCard()
    current_field = None

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            for i in range(2):  # Assuming there are two columns
                x0 = i * (page.width / 2)
                x1 = (i + 1) * (page.width / 2)
                text = page.within_bbox((x0, 0, x1, page.height)).extract_text()

                if text:
                    lines = text.splitlines()
                    for line in lines:
                        line = line.strip()
                        if line:  # Ignore empty lines
                            # Tokenize the line into words
                            words = line.split()
                            for word in words:
                                # Check for header keywords
                                if word.startswith("Type:"):
                                    # Save the current card before starting a new one
                                    if (
                                        current_card.card_type
                                        and current_card.ref
                                        and current_card.question
                                        and current_card.answer
                                    ):
                                        cards.append(current_card)
                                        # Reset for the next card
                                        current_card = QuizCard()

                                    current_field = "type"
                                    current_card.card_type = word[
                                        len("Type:") :
                                    ].strip()

                                elif word.startswith("Ref:"):
                                    current_field = "ref"
                                    current_card.ref = word[len("Ref:") :].strip()

                                elif word.startswith("Club"):
                                    current_field = "club"
                                    current_card.club = word[len("Club:") :].strip()

                                elif word.startswith("Question:"):
                                    current_field = "question"
                                    current_card.question = word[
                                        len("Question:") :
                                    ].strip()

                                elif word.startswith("Answer:"):
                                    current_field = "answer"
                                    current_card.answer = word[len("Answer:") :].strip()

                                else:
                                    # Add word to the current field, without leading spaces for the first word
                                    if current_field == "type":
                                        current_card.card_type += (
                                            " " if current_card.card_type else ""
                                        ) + word
                                    elif current_field == "ref":
                                        current_card.ref += (
                                            " " if current_card.ref else ""
                                        ) + word
                                    elif current_field == "club":
                                        current_card.club += (
                                            " " if current_card.club else ""
                                        ) + word
                                    elif current_field == "question":
                                        current_card.question += (
                                            " " if current_card.question else ""
                                        ) + word
                                    elif current_field == "answer":
                                        current_card.answer += (
                                            " " if current_card.answer else ""
                                        ) + word

    # Save the last card
    if (
        current_card.card_type
        and current_card.ref
        and current_card.question
        and current_card.answer
    ):
        cards.append(current_card)
    else:
        print(f"Uncomplete card: {current_card}")

    return cards


def main():
    file_path = "/home/amberson/Code/quiz-cards/Practice-Questions-Through-Acts-12.pdf"
    cards = parse_pdf(file_path)

    for card in cards:
        print(card)


if __name__ == "__main__":
    main()
