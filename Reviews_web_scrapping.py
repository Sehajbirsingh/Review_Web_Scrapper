import requests
from bs4 import BeautifulSoup
import csv
import time

# Base URL for the Yelp page
base_url = 'https://www.yelp.ca/biz/pai-northern-thai-kitchen-toronto-5'

# Function to extract reviewer names
def extract_reviewer_names(soup):
    reviewer_names = []
    reviewer_containers = soup.find_all('div', class_='user-passport-info')
    for container in reviewer_containers:
        name = container.find('a', class_='y-css-12ly5yx')
        if name:
            reviewer_names.append(name.text.strip())
    return reviewer_names

# Function to extract review ratings
def extract_ratings(soup):
    ratings = []
    rating_containers = soup.find_all('li', class_='y-css-mu4kr5')
    for container in rating_containers:
        rating_element = container.find('div', class_='y-css-1jwbncq', role='img')
        if rating_element:
            rating = rating_element['aria-label'].split()[0]
            ratings.append(rating)
    return ratings

# Function to extract review texts
def extract_review_texts(soup):
    review_texts = []
    review_containers = soup.select('li.y-css-mu4kr5')

    for container in review_containers:
        review_text_element = container.find('span', lang='en')
        if review_text_element:
            review_text = review_text_element.get_text(separator='\n').strip()
            review_texts.append(review_text)
    return review_texts

# Function to save results to CSV
def save_to_csv(reviewer_names, ratings, review_texts, filename='yelp_reviews_all.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Reviewer Name', 'Rating', 'Review Text'])
        # Write data rows
        for name, rating, text in zip(reviewer_names, ratings, review_texts):
            writer.writerow([name, rating, text])
    print(f"Data saved to {filename}")

# Main scraping function
def scrape_reviews():
    all_reviewer_names = []
    all_ratings = []
    all_review_texts = []

    # Start the timer
    start_time = time.time()

    # Process page 1
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        all_reviewer_names.extend(extract_reviewer_names(soup))
        all_ratings.extend(extract_ratings(soup))
        all_review_texts.extend(extract_review_texts(soup))
    else:
        print(f"Failed to retrieve page 1. Status code: {response.status_code}")

    # Process pages 2 to 372
    for i in range(1, 372):
        url = f"{base_url}?start={i * 10}"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            all_reviewer_names.extend(extract_reviewer_names(soup))
            all_ratings.extend(extract_ratings(soup))
            all_review_texts.extend(extract_review_texts(soup))
            print(f"Page {i + 1} processed: {len(all_reviewer_names)} reviews extracted.")
        else:
            print(f"Failed to retrieve page {i + 1}. Status code: {response.status_code}")

    # Save all results to CSV
    save_to_csv(all_reviewer_names, all_ratings, all_review_texts)
    
    # Calculate and print the total time taken
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total number of reviews scraped: {len(all_reviewer_names)}")
    print(f"Time taken: {elapsed_time:.2f} seconds")

# Execute the scraping
scrape_reviews()
