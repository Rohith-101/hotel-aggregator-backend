
Hotel Review Aggregator: Project Documentation

The Hotel Review Aggregator is a full-stack web application engineered to automate the collection, consolidation, and visualization of hotel review data from multiple online travel agencies (OTAs) and review platforms. The system provides a centralized dashboard to analyze key metrics such as overall ratings, review counts, and recent review trends, and automatically exports the aggregated data to a Google Sheet for further analysis.

The application is built with a modern, service-oriented architecture, focusing on reliability, performance, and data accuracy. It is designed for free-tier deployment on modern cloud platforms.
2.0 Core Features

    Multi-Source Aggregation: The application accepts a list of URLs from various sources (Booking.com, TripAdvisor, Google Reviews) for a single hotel and scrapes the data from each.

    Detailed Data Extraction: The script is designed to capture a rich dataset, including the Hotel Name, Source, Overall Rating, Total Review Count, Address, Website, Phone Number, and snippets of the most recent user reviews.

    Interactive Dashboard: A professional, user-friendly frontend built with React (Next.js) provides an interactive dashboard with summary cards, comparison charts, and a detailed table of recent reviews.

    Concurrent Scraping: To ensure a responsive user experience, the backend performs scraping operations for all provided URLs simultaneously using a thread pool, significantly reducing the total processing time.

    Google Sheets Automation: All successfully scraped data is automatically formatted and appended to a designated Google Sheet, creating a persistent and easily accessible database.

3.0 System Architecture and Technology Stack

The project utilizes a modern, decoupled architecture to ensure that each component is independent and scalable.

    Backend Service: A Python API built with the FastAPI framework. It serves as the core of the application, handling incoming scrape requests, interfacing with the scraping engine, standardizing data, and writing to the Google Sheet.

    Frontend Interface: A dynamic dashboard built with React (Next.js) and styled with Tailwind CSS. It provides the user interface for inputting URLs and visualizing the aggregated data.

    Scraping Engine: SerpApi is used as the scraping client. This is a critical architectural choice that abstracts away the complexities of browser automation, CAPTCHA solving, and proxy management, ensuring high data accuracy and reliability by returning structured JSON data.

    Database: A Google Sheet is used as a simple and effective data store.

    Hosting Infrastructure:

        Backend: Deployed on Render.

        Frontend: Deployed on Vercel.

4.0 Prerequisites for Deployment

To deploy and run this application, the following accounts, tools, and credentials are required:

    Google Cloud Account: For creating a service account and generating a credentials.json file to access the Google Sheets API.

    SerpApi Account: To obtain a free API key for the scraping service.

    Render Account: For hosting the backend API.

    Vercel Account: For hosting the frontend web application.

    Node.js and npm: Required for setting up the frontend project locally.

    Python (3.9+): Required for the backend.

    Git and a GitHub Account: For version control and deployment to the hosting platforms.

5.0 Step-by-Step Deployment Instructions
Part 1: Initial Configuration

    Google Sheet Preparation:

        Create a new Google Sheet.

        Rename the first tab to AggregatedData.

        Populate the first row with the headers: Hotel Name, Source, Overall Rating, Review Count, Address, Website, Phone, Recent Reviews Snippets, Scraped_At.

    Google Credentials Generation:

        In the Google Cloud Console, create a new project and enable the Google Drive API and Google Sheets API.

        Create a Service Account, assign it the "Editor" role, and download its JSON key. Rename this file to credentials.json.

        Copy the client_email from the JSON file and share your Google Sheet with this email, granting it "Editor" permissions.

    SerpApi Key Acquisition:

        Sign up for a free account at SerpApi.com and copy your Private API Key from the dashboard.

Part 2: Backend Deployment (Render)

    Version Control Setup: Create a GitHub repository for the backend and commit the main.py and requirements.txt files.

    Render Deployment:

        Create a new Web Service on Render and link it to your backend repository.

        Set the Build Command to pip install -r requirements.txt.

        Set the Start Command to uvicorn main:app --host 0.0.0.0 --port 10000.

        In the Environment section, add the following three secret variables:

            SHEET_NAME: The name of your Google Sheet.

            SERPAPI_KEY: Your private key from SerpApi.

            GOOGLE_CREDENTIALS_JSON: The complete JSON content of your credentials.json file.

        Create the service and copy the live URL once it's deployed.

Part 3: Frontend Deployment (Vercel)

    Version Control Setup: Create a separate GitHub repository for the frontend and commit the Next.js project files.

    Vercel Deployment:

        Import your frontend repository into Vercel.

        In the project's settings, go to Environment Variables and add:

            NEXT_PUBLIC_API_URL: The live URL of your deployed Render backend.

        Deploy the project.

6.0 Usage Instructions

To use the application, navigate to the live Vercel URL, paste the hotel URLs (one per line) into the text area, and click the "Aggregate Reviews" button. The dashboard will populate with the aggregated data, which will also be saved to your Google Sheet.