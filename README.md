# 🚌 Redbus Live Bus Data Analysis Dashboard

A complete data engineering project that scrapes live bus route and ticketing data from the Redbus platform, stores it in a cloud database, and visualizes it using an interactive Streamlit dashboard.

---

## ✨ Project Highlights

This project automates the entire data pipeline, from raw HTML extraction to dynamic web visualization.

* **Automated Web Scraping:** Uses **Selenium** to reliably extract comprehensive bus details, including bus names, types, departure/arrival times, durations, prices, and star ratings.
* **Data Storage:** Data is cleaned, consolidated using **Pandas**, and stored in a scalable **MySQL (TiDB Cloud)** database using the `mysql.connector-python` library.
* **Interactive Dashboard:** Built with **Streamlit** and **Plotly** to provide a professional, user-friendly interface for dynamic data exploration and visualization.
* **Extensive Coverage:** Scrapes data for multiple government and private bus operators across various Indian states.

---

## 💻 Tech Stack

| Category           | Technology          | Purpose                            |
| :---               | :---                | :---                               |
| **Language**       | Python              | Core programming language          |
| **Scraping**       | Selenium            | Web automation for data extraction |
| **Data Processing**| Pandas              | Data cleaning and transformation   |
| **Database**       | MySQL (TiDB Cloud)  | Scalable data storage              |
| **Dashboard**      | Streamlit, Plotly   | Web application and visualization  |

---

## 📁 Repository Structure

The project is structured to follow the data pipeline workflow:

| File                           | Pipeline Stage         | Description                                                                                         |
| :---                           | :---                   | :---                                                                                                |
| `bus_route_links.ipynb`        | **Scraping (Phase 1)** | Gathers the initial list of State/Private bus route links (URLs).                                   |
| `bus_details.ipynb`            | **Scraping (Phase 2)** | Iterates through the links to scrape detailed bus data (Schedules, Price, Rating, Seats).           |
| `mysql_connector_python.ipynb` | **ETL & Storage**      | Reads all scraped CSVs, performs final cleaning, and bulk-inserts the data into the MySQL database. |
| `streamlit.py`                 | **Visualization**      | The Streamlit application that connects to the database and renders the interactive dashboard.      |

---

