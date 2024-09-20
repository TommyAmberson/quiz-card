import argparse
import csv
import pdfplumber
import re


class QuizCard:
    def __init__(
        self, card_type="", ref="", extra_info="", club="", question="", answer=""
    ):
        self.card_type = card_type
        self.ref = ref
        # Extra information for SIT questions
        self.extra_info = extra_info
        self.club = club
        self.question = question
        self.answer = answer

    def __str__(self):
        return (
            f"Type: {self.card_type}\n"
            f"Ref: {self.ref}\n"
            f"Extra Info: {self.extra_info}\n"
            f"Club: {self.club}\n"
            f"Q: {self.question}\n"
            f"A: {self.answer}\n"
        )

    def to_dict(self):
        """Convert the QuizCard to a dictionary for CSV output."""
        return {
            "Type": self.card_type.strip(),
            "Ref": self.ref.strip(),
            "Extra Info": self.extra_info.strip(),
            "Club": self.club.strip(),
            "Question": self.question.strip(),
            "Answer": self.answer.strip(),
        }


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
                                # Check for header keywords and set the
                                # current_field so that subsequent words are
                                # added to the right field.

                                if word.startswith(
                                    "Type:"
                                ):  # Check for "Type:". This starts a card

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

                                elif word.startswith("Ref:"):  # Check for "Ref:".
                                    current_field = "ref"
                                    current_card.ref = word[len("Ref:") :].strip()

                                elif current_field == "ref" and (
                                    re.compile(r"\d+:\d+").search(word)
                                ):  # Becuase the extra_info does not have a
                                    # header we need to search for the last
                                    # word of the ref field

                                    # This word is the end of the ref field
                                    current_card.ref += " " + word

                                    # Next part is extra_info
                                    current_field = "extra_info"

                                elif word.startswith(
                                    "Club"
                                ):  # Check for "Club". Note the absense of a ":"
                                    current_field = "club"
                                    current_card.club = word[len("Club") :].strip()

                                elif word.startswith(
                                    "Question:"
                                ):  # Check for "Question:".
                                    current_field = "question"
                                    current_card.question = word[
                                        len("Question:") :
                                    ].strip()

                                elif word.startswith("Answer:"):  # Check for "Answer:".
                                    current_field = "answer"
                                    current_card.answer = word[len("Answer:") :].strip()

                                else:  # just a normal word
                                    # Add word to the current field
                                    if current_field == "type":
                                        current_card.card_type += (
                                            " " if current_card.card_type else ""
                                        ) + word
                                    elif current_field == "ref":
                                        current_card.ref += (
                                            " " if current_card.ref else ""
                                        ) + word
                                    elif current_field == "extra_info":
                                        current_card.extra_info += (
                                            " " if current_card.extra_info else ""
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
        print(f"Incomplete card: {current_card}")

    return cards


def save_to_csv(cards, output_file):
    """Save the list of QuizCards to a CSV file."""
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Type", "Ref", "Extra Info", "Club", "Question", "Answer"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        writer.writeheader()
        for card in cards:
            writer.writerow(card.to_dict())


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Parse quiz cards from a PDF file.")
    parser.add_argument("--in_file", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--out_file", "-o", required=True, help="Output CSV file path")
    args = parser.parse_args()

    # Get the file paths from the command-line arguments
    input_file = args.in_file
    output_file = args.out_file

    # Parse the PDF
    cards = parse_pdf(input_file)

    # Save the parsed cards to a CSV file
    save_to_csv(cards, output_file)

    print(f"Saved {len(cards)} quiz cards to {output_file}")


if __name__ == "__main__":
    main()
