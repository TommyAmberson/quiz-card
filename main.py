from jinja2 import Environment, FileSystemLoader
import argparse
import csv
import os
import pdfkit
import pdfplumber
import re


class QuizCard:
    """
    A class to represent a quiz card extracted from the PDF.

    Attributes:
        card_type (str): The type of the card (e.g., SIT).
        ref (str): The reference or verse associated with the card.
        extra_info (str): Any additional information for SIT questions.
        club (str): The club or group associated with the card.
        question (str): The question text of the card.
        answer (str): The answer to the question.
    """

    def __init__(
        self, card_type="", ref="", extra_info="", club="", question="", answer=""
    ):
        """
        Initializes a QuizCard object with default empty values for each field.

        Args:
            card_type (str): The type of the card.
            ref (str): The reference for the card.
            extra_info (str): Extra information, mostly for SIT questions.
            club (str): Club information (if available).
            question (str): The question text.
            answer (str): The answer text.
        """
        self.card_type = card_type
        self.ref = ref
        self.extra_info = extra_info
        self.club = club
        self.question = question
        self.answer = answer

    def __str__(self):
        """
        Returns a string representation of the QuizCard object for debugging.

        Returns:
            str: A formatted string representation of the QuizCard's fields.
        """
        return (
            f"Type: {self.card_type}\n"
            f"Ref: {self.ref}\n"
            f"Extra Info: {self.extra_info}\n"
            f"Club: {self.club}\n"
            f"Q: {self.question}\n"
            f"A: {self.answer}\n"
        )

    def to_dict(self):
        """
        Converts the QuizCard object to a dictionary for CSV output.

        Returns:
            dict: A dictionary representation of the QuizCard object.
        """
        return {
            "Type": self.card_type.strip(),
            "Ref": self.ref.strip(),
            "Extra Info": self.extra_info.strip(),
            "Club": self.club.strip(),
            "Question": self.question.strip(),
            "Answer": self.answer.strip(),
        }


def parse_pdf(file_path):
    """
    Parses a PDF file and extracts quiz cards from it.

    The function handles PDFs with two columns of text. It processes each page
    and splits the text into words. Fields like 'Type:', 'Ref:', 'Club:',
    'Question:', and 'Answer:' are identified, and words are appended to the
    correct fields in a QuizCard object.

    Args:
        file_path (str): The path to the PDF file to be parsed.

    Returns:
        list: A list of QuizCard objects extracted from the PDF.
    """
    cards = []
    current_card = QuizCard()
    current_field = None

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            for i in range(2):  # Assuming there are two columns
                x0 = i * (page.width / 2)  # Left column boundary
                x1 = (i + 1) * (page.width / 2)  # Right column boundary
                text = page.within_bbox((x0, 0, x1, page.height)).extract_text()

                if text:
                    # Split the column's text into lines
                    lines = text.splitlines()

                    # Loop through each line in the extracted text
                    for line in lines:
                        line = line.strip()  # Remove extra whitespace
                        if line:  # Ignore empty lines
                            words = line.split()  # Split line into individual words

                            for word in words:
                                # Detect and handle different fields based on headers
                                if word.startswith("Type:"):
                                    # Start of a new card detected, save the
                                    # previous card if it's valid
                                    if (
                                        current_card.card_type
                                        and current_card.ref
                                        and current_card.question
                                        and current_card.answer
                                    ):
                                        # Append the current card to the list of cards
                                        cards.append(current_card)
                                        # Create a new card for the next one
                                        current_card = QuizCard()

                                    # Set the current field to 'type' and store the type
                                    current_field = "type"
                                    current_card.card_type = word[
                                        len("Type:") :
                                    ].strip()

                                elif word.startswith("Ref:"):
                                    # Reference field detected, prepare to store the reference
                                    current_field = "ref"
                                    current_card.ref = word[len("Ref:") :].strip()

                                elif current_field == "ref" and re.compile(
                                    r"\d+:\d+"
                                ).search(word):
                                    # Detect end of the reference field based
                                    # on a regex that matches a verse format
                                    # (e.g., 5:22)
                                    current_card.ref += " " + word
                                    # Switch to the extra_info field for
                                    # capturing additional data for SIT
                                    # questions
                                    current_field = "extra_info"

                                elif word.startswith("Club"):
                                    # Club information detected (Note: "Club" without colon ":")
                                    current_field = "club"
                                    current_card.club = word[len("Club") :].strip()

                                elif word.startswith("Question:"):
                                    # Question field detected, prepare to store the question
                                    current_field = "question"
                                    current_card.question = word[
                                        len("Question:") :
                                    ].strip()

                                elif word.startswith("Answer:"):
                                    # Answer field detected, prepare to store the answer
                                    current_field = "answer"
                                    current_card.answer = word[len("Answer:") :].strip()

                                else:
                                    # If it's just a word, append it to the
                                    # current field. This handles multi-word
                                    # fields like questions or answers
                                    if current_field == "type":
                                        current_card.card_type += " " + word
                                    elif current_field == "ref":
                                        current_card.ref += " " + word
                                    elif current_field == "extra_info":
                                        current_card.extra_info += " " + word
                                    elif current_field == "club":
                                        current_card.club += " " + word
                                    elif current_field == "question":
                                        current_card.question += " " + word
                                    elif current_field == "answer":
                                        current_card.answer += " " + word

    # At the end, save the last card if it's valid
    if (
        current_card.card_type
        and current_card.ref
        and current_card.question
        and current_card.answer
    ):
        cards.append(current_card)
    else:
        # Print a message if a card was incomplete
        print(f"Incomplete card: {current_card}")

    return cards  # Return the list of parsed quiz cards


def save_to_csv(cards, output_file):
    """
    Saves the list of QuizCards to a CSV file.

    Args:
        cards (list): The list of QuizCard objects to be written to the CSV file.
        output_file (str): The path to the output CSV file.
    """
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        # Define the fieldnames for the CSV columns
        fieldnames = ["Type", "Ref", "Extra Info", "Club", "Question", "Answer"]
        # Create a CSV DictWriter object to write dictionaries to the CSV
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        # Write the header row
        writer.writeheader()
        # Write each quiz card as a row in the CSV
        for card in cards:
            writer.writerow(card.to_dict())


def save_to_pdf(cards, output_file):
    """
    Save the list of QuizCards to a reformatted PDF file.

    Args:
        cards (list): The list of QuizCard objects to be written to the PDF file.
        output_file (str): The path to the output PDF file.
    """
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("template.html")

    html_string = ""
    for card in cards:
        template_vars = {"body": card.card_type}
        html_string += template.render(template_vars)

    print("------------------ HTML String ------------------")
    print(html_string)

    options = {
        "page-size": "A4",
        "margin-top": "0.75in",
        "margin-right": "0.75in",
        "margin-bottom": "0.75in",
        "margin-left": "0.75in",
        "encoding": "UTF-8",
        "enable-local-file-access": None,
        "no-outline": None,
    }

    print("\n------------ Converting HTML to PDF -------------")
    pdfkit.from_string(
        html_string,
        output_file,
        options=options,
    )


def check_output_extension(output_file, output_type):
    """
    Checks if the file extension matches the selected output type.

    Args:
        output_file (str): The output file path.
        output_type (str): The selected output type ('csv' or 'pdf').

    Raises:
        ValueError: If the file extension doesn't match the output type.
    """
    ext = os.path.splitext(output_file)[1].lower()
    if output_type == "csv" and ext != ".csv":
        raise ValueError(
            f"Output file extension '{ext}' does not match the output type 'csv'."
        )
    elif output_type == "pdf" and ext != ".pdf":
        raise ValueError(
            f"Output file extension '{ext}' does not match the output type 'pdf'."
        )


def main():
    """
    Main function to parse a PDF file and save the extracted quiz cards to a CSV or PDF.

    This function handles the command-line arguments for input and output file paths,
    and allows the user to select the output type (csv or pdf).
    """
    parser = argparse.ArgumentParser(description="Parse quiz cards from a PDF file.")
    parser.add_argument("--in_file", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--out_file", "-o", required=True, help="Output file path")
    parser.add_argument(
        "--output_type",
        "-t",
        default="csv",
        choices=["csv", "pdf"],
        help="Specify the output format (csv or pdf). Default is csv.",
    )
    args = parser.parse_args()

    # Check if the output file has the correct extension
    check_output_extension(args.out_file, args.output_type)

    # Parse the PDF file to extract quiz cards
    cards = parse_pdf(args.in_file)

    # Save the output based on the selected format
    if args.output_type == "csv":
        save_to_csv(cards, args.out_file)
    elif args.output_type == "pdf":
        save_to_pdf(cards, args.out_file)

    print(f"Saved quiz cards to {args.out_file} as {args.output_type.upper()}")


if __name__ == "__main__":
    main()
