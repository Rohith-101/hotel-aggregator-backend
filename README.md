# hotel-aggregator-backend
Google Maps Local Business Scraper: Project Documentation
1.0 Introduction and Overview

This document provides a comprehensive overview of the Google Maps Local Business Scraper, a full-stack application engineered for the automated collection and organization of local business data. The system features a web-based user interface for on-demand execution and a robust backend service that manages the data extraction and storage processes. The architecture has been designed with a focus on reliability, performance, and data accuracy, leveraging a professional-grade scraping API. Furthermore, the entire application is architected for deployment on cloud platforms that offer free-tier services.
2.0 Core Functionalities and Features

The application is equipped with a suite of features designed to ensure efficient and accurate data collection:

    Comprehensive Data Extraction: The script gathers thirteen distinct data points for each business entity, encompassing contact information, customer ratings, service options, and precise GPS coordinates.

    Intelligent Pagination Logic: The scraper operates in manageable batches, processing a maximum of ten pages per execution. It incorporates a stateless resumption mechanism that intelligently continues the scraping process from its previous stopping point, thereby conserving resources and preventing redundant data collection.

    Duplicate Entry Prevention: A verification system is integrated to cross-reference with existing entries in the Google Sheet, ensuring that the database remains clean and free of duplicate records.

    Dual-Mode Automation: The system supports two modes of operation: on-demand scraping initiated via the web user interface and fully automated, scheduled execution managed by an external cron job service.

    Secure and Modern Architecture: The application is built upon a secure, decoupled architecture employing contemporary technologies such as FastAPI and React. All sensitive credentials, including API keys, are managed securely through environment variables.

3.0 System Architecture and Technology Stack

The project utilizes a modern, service-oriented architecture to optimize the efficiency and scalability of each component.

    Backend Service: A Python-based API developed with the FastAPI framework. It is responsible for processing scrape requests, interfacing with the scraping engine, and writing data to the designated Google Sheet.

    Frontend Interface: A user-friendly dashboard constructed with React (Next.js) and styled using Tailwind CSS.

    Scraping Engine: The core data extraction is handled by SerpApi. This selection is critical, as it provides a reliable mechanism for bypassing anti-scraping measures like CAPTCHAs and IP address blocking, delivering structured JSON data with high fidelity.

    Database: A Google Sheet is employed as a cost-effective and accessible data store.

    Hosting Infrastructure:

        The backend service is deployed on Render.

        The frontend application is deployed on Vercel.

        Scheduled tasks are orchestrated by cron-job.org.

4.0 Prerequisites for Deployment

Prior to deployment, the following accounts, tools, and credentials are required:

    Google Cloud Account: Necessary for the creation of a service account and the generation of credentials.json.

    SerpApi Account: Required to obtain a free API key for the scraping service.

    Render Account: For hosting the backend API.

    Vercel Account: For hosting the frontend web application.

    Node.js and npm: Must be installed on the local development machine for frontend setup.

    Python (version 3.9 or higher): Must be installed on the local machine for backend development.

    Git and a GitHub Account: Required for version control and facilitating deployment to the hosting platforms.

5.0 Step-by-Step Deployment Instructions
Part 1: Initial Configuration

    Google Sheet Preparation:

        Instantiate a new Google Sheet.

        Rename the primary tab to Data.

        Populate the first row with the following thirteen headers in sequence: Name, Category, Address, Rating, Reviews, Website, Phone, Price Level, Hours, Service Options, Latitude, Longitude, Scraped_At.

    Google Credentials Generation:

        Within the Google Cloud Console, create a new project and enable both the Google Drive API and the Google Sheets API.

        Generate a Service Account, assign it the Editor role, and download the corresponding JSON key. This file should be renamed to credentials.json.

        From the credentials.json file, copy the client_email value and share your Google Sheet with this email address, granting it "Editor" permissions.

    SerpApi Key Acquisition:

        Register for a free account at SerpApi.com and retrieve your Private API Key from the user dashboard.

Part 2: Backend Service Deployment (Render)

    Version Control Setup: Create a new GitHub repository for the backend and commit the main.py and requirements.txt files.

    Render Deployment:

        From the Render dashboard, create a new Web Service and link it to your backend repository.

        Configure the build and start commands as follows:

            Build Command: pip install -r requirements.txt

            Start Command: uvicorn main:app --host 0.0.0.0 --port 10000

        In the Environment section, define the following three secret variables:

            SHEET_NAME: The title of your Google Sheet.

            SERPAPI_KEY: Your private key from SerpApi.

            GOOGLE_CREDENTIALS_JSON: The complete JSON content of your credentials.json file.

        Initiate the service creation. Upon successful deployment, copy the provided live URL.

Part 3: Frontend Application Deployment (Vercel)

    Version Control Setup: Create a separate GitHub repository for the frontend and commit the Next.js project files.

    Vercel Deployment:

        From the Vercel dashboard, import your frontend repository.

        In the project's settings, navigate to Environment Variables and add the following:

            NEXT_PUBLIC_API_URL: The live URL of your deployed Render backend service.

        Deploy the project.

6.0 Usage and Automation Procedures
On-Demand Execution

To initiate a data scrape manually, navigate to the live Vercel URL of the frontend application, input a search query, and activate the "Start Scraping" button.
Scheduled Automation via cron-job.org

For automated, periodic execution, an external cron service is utilized.

    Account Creation: Register for a free account at cron-job.org.

    Cronjob Configuration: Create a new cronjob with the following parameters:

        Title: Assign a descriptive name (e.g., Daily Google Maps Scraper).

        URL: Provide the full URL of your Render backend, including the /scrape endpoint (e.g., https://scraper-backend-xxxx.onrender.com/scrape).

        Method: Set the HTTP request method to POST.

        Request Body (Payload): In the "POST data" field, supply the JSON payload for your desired default search query:

        {"query": "Grocery stores in Chennai"}

        Headers: Add a custom Content-Type header with the value application/json.

        Schedule: Configure the desired execution frequency using the provided interface.

    Save: Finalize the cronjob creation. The service will now trigger your API endpoint according to the defined schedule.

7.0 Ethical and Legal Considerations

It is important to note that the automated scraping of Google Maps may contravene its Terms of Service. This project is provided for educational and illustrative purposes only. Users should proceed with responsibility and remain mindful of the volume and frequency of their requests.