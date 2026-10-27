# NYC Airbnb Market Analytics Pipeline

An end-to-end data pipeline and dashboard analyzing the NYC short-term rental market. 

## 🏗️ Architecture
This project demonstrates a production-style analytics stack:
1. **Snowflake**: Data warehouse (RAW → STAGING → ANALYTICS)
2. **dbt**: ELT transformations with automated testing and lineage
3. **Streamlit**: Interactive, cached dashboard for business users

## 📊 Key Business Insights
- **Inventory Concentration**: Bedford-Stuyvesant (Brooklyn) hosts the highest volume of listings (1,505), while Midtown (Manhattan) has the highest volume of premium listings (1,336 at a $373 median).
- **Market Spread**: Manhattan's neighbourhood median prices vary wildly (from ~$100 to over $500), indicating a highly fragmented market of budget and ultra-luxury stays. The outer boroughs (Bronx, Queens, Staten Island) are tightly clustered around $100-$130.
- **Room Type Dynamics**: Entire homes dominate in Manhattan, while private rooms see higher relative volume in Brooklyn and Queens.

## 🛠️ Technical Highlights
- **Data Quality**: Handled 30,259 raw listings, cleaning currency strings (`$` and `,`), and filtering extreme price outliers (>$2,000/night) using dbt staging and intermediate models.
- **Advanced SQL**: Utilized window functions (`QUALIFY`, `MEDIAN`, `PERCENTILE_CONT`) to enrich listing-level data with neighbourhood-level context.
- **Testing**: Implemented 13 dbt generic and custom tests to ensure PK uniqueness, referential integrity, and business logic (e.g., ensuring all reported neighbourhoods have >10 listings).
- **Cost Control**: Operated entirely on an X-Small Snowflake warehouse with 60-second auto-suspend, executing the entire project for under 2 Snowflake credits.

## 📂 Project Structure
- `airbnb_dbt/`: Contains the dbt project (models, tests, sources).
- `dashboard/`: Contains the Streamlit application and Snowflake connection logic.

## 🚀 How to Run Locally
1. Set up Snowflake and load the Inside Airbnb NYC dataset.
2. Configure `~/.dbt/profiles.yml` with your Snowflake credentials.
3. Run `dbt run` and `dbt test` in the `airbnb_dbt` directory.
4. Add your credentials to `dashboard/.streamlit/secrets.toml`.
5. Run `streamlit run dashboard/app.py`.


## Project Traces
![Dashboard Screenshot 1](dashboard/assets/dashboard1.png)
![Dashboard Screenshot 2](dashboard/assets/dashboard2.png)
![Dashboard Screenshot 3](dashboard/assets/dashboard3.png)
![Dashboard Screenshot 4](dashboard/assets/dashboard4.png)
![Dashboard Screenshot 5](dashboard/assets/dashboard5.png)
![Dashboard Screenshot 6](dashboard/assets/dashboard6.png)
![Dashboard Screenshot 7](dashboard/assets/dashboard7.png)