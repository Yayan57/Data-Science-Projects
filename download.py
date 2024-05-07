import requests

# URL of the webpage you want to download
url = "https://www.baseball-reference.com/leagues/majors/2013-schedule.shtml"

# Send a GET request
response = requests.get(url)
response.raise_for_status()  # This will raise an exception if there's an error

# Save the HTML content to a file
with open('2013_MLB_Schedule.html', 'w', encoding='utf-8') as file:
    file.write(response.text)

print("HTML file has been saved.")