import argparse
import csv
import pdfplumber
import re


class QuizCard:
    # QuizCard class represents a single quiz card with various fields
    def __init__(
        self, card_type="", ref="", extra_info="", club="", question="", answer=""
    ):
        self.card_type = card_type  # Type of the card (e.g., SIT)
        self.ref = ref  # Reference (e.g., verse or source)
        self.extra_info = extra_info  # Additional information for SIT questions
        self.club = club  # Club information (if available)
        self.question = question  # The actual question text
        self.answer = answer  # The answer to the question

    def __str__(self):
        # String representation for debugging and displaying the card
        return (
            f"Type: {self.card_type}\n"
            f"Ref: {self.ref}\n"
            f"Extra Info: {self.extra_info}\n"
            f"Club: {self.club}\n"
            f"Q: {self.question}\n"
            f"A: {self.answer}\n"
        )

    def to_dict(self):
        # Convert the QuizCard into a dictionary to output as CSV
        return {
            "Type": self.card_type.strip(),
            "Ref": self.ref.strip(),
            "Extra Info": self.extra_info.strip(),
            "Club": self.club.strip(),
            "Question": self.question.strip(),
            "Answer": self.answer.strip(),
        }


def parse_pdf(file_path):
    # Main function to parse the PDF and extract quiz cards
    cards = []  # List to store all the parsed QuizCards
    current_card = QuizCard()  # Initialize a new QuizCard
    current_field = None  # Track which field is currently being populated

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            for i in range(2):  # Assuming two columns in each page
                x0 = i * (page.width / 2)  # Left boundary for each column
                x1 = (i + 1) * (page.width / 2)  # Right boundary for each column

                # Extract text from each column
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
                                    # Start of a new card detected, save the previous card if it's valid
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
                                    # Detect end of the reference field based on a regex that matches a verse format (e.g., 5:22)
                                    current_card.ref += " " + word
                                    # Switch to the extra_info field for capturing additional data
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
                                    # If it's just a word, append it to the current field
                                    # This handles multi-word fields like questions or answers
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
    """Save the list of QuizCards to a CSV file."""
    # Open the CSV file in write mode
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


def main():
    # Set up the argument parser to accept input and output files
    parser = argparse.ArgumentParser(description="Parse quiz cards from a PDF file.")
    parser.add_argument("--in_file", "-i", required=True, help="Input PDF file path")
    parser.add_argument("--out_file", "-o", required=True, help="Output CSV file path")
    args = parser.parse_args()

    # Get the input and output file paths from command-line arguments
    input_file = args.in_file
    output_file = args.out_file

    # Parse the PDF file to extract quiz cards
    cards = parse_pdf(input_file)

    # Save the parsed quiz cards to a CSV file
    save_to_csv(cards, output_file)

    print(f"Saved {len(cards)} quiz cards to {output_file}")


if __name__ == "__main__":
    main()
