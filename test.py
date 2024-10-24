import os
import random
import string

def generate_random_text(length=50):
    """Generate random text"""
    words = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"]
    punctuation = ['.', '!', '?']
    
    text = ""
    for _ in range(random.randint(5, 10)):
        word = random.choice(words)
        text += word + " "
        if random.random() > 0.5:
            text += random.choice(punctuation) + " "
    
    return text[:length].strip()

def save_to_file(text, filename):
    """Save text to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"File '{filename}' created successfully.")
    except IOError as e:
        print(f"Error creating file '{filename}': {e}")

def create_text_files():
    """Create five text files in the current directory"""
    filenames = ['sample1.txt', 'sample2.txt', 'sample3.txt', 'sample4.txt', 'sample5.txt']
    
    for i, filename in enumerate(filenames, 1):
        content = generate_random_text()
        full_path = os.path.join(os.getcwd(), filename)
        save_to_file(content, full_path)

if __name__ == "__main__":
    # Create the text files
    create_text_files()
    print("All 5 text files have been created in the current directory.")
