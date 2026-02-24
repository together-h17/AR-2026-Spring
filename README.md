# GIS Project

A professional Geographic Information System (GIS) project structure for spatial data analysis, processing, and visualization.

## Project Structure

```
├── data/
│   ├── raw/           # Original, unprocessed data
│   ├── processed/     # Cleaned and processed data
│   └── output/        # Final outputs and results
├── notebooks/         # Jupyter notebooks for analysis
├── scripts/           # Python scripts for data processing
├── src/               # Source code and modules
├── docs/              # Documentation
├── config/            # Configuration files
├── tests/             # Unit tests
├── .env               # Environment variables
├── .gitignore         # Git ignore rules
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your environment variables

## Environment Variables

Key environment variables to configure in `.env`:

- `DATA_RAW_PATH`: Path to raw data directory
- `DATA_PROCESSED_PATH`: Path to processed data directory
- `DATA_OUTPUT_PATH`: Path to output directory
- `QGIS_PREFIX_PATH`: QGIS installation path (if needed)
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database connection
- `PROJECTION_EPSG`: Default coordinate reference system
- `CWA_API_KEY`: Central Weather Administration API key
- `MOENV_API_KEY`: Ministry of Environment API key

## Usage

### Weather Data Integration
Fetch real-time weather data from Central Weather Administration (CWA):
```bash
# Activate conda environment
conda activate py310

# Fetch weather data
python scripts/cwa_weather_api.py

# Create weather visualization map
python scripts/simple_weather_map.py
```

### Air Quality Data Integration
Fetch real-time AQI data from Ministry of Environment (MOENV):
```bash
# Activate conda environment
conda activate py310

# Fetch AQI data and create visualization
python scripts/moenv_aqi_api.py
```

### Spatial Distance Calculation
Calculate distances from monitoring stations to Taipei Station:
```bash
# Activate conda environment
conda activate py310

# Calculate distances and generate analysis
python scripts/spatial_distance_calculation.py
```

### Data Processing
```bash
python scripts/process_data.py
```

### Analysis
Run Jupyter notebooks from the `notebooks/` directory:
```bash
jupyter notebook notebooks/
```

### Testing
```bash
python -m pytest tests/
```

## Data Management

- **Raw data**: Store original datasets in `data/raw/`
- **Processed data**: Store cleaned datasets in `data/processed/`
- **Outputs**: Store final results in `data/output/`
- **Distance calculations**: Store spatial analysis results in `outputs/`

## Features

### Real-time Data Integration
- **CWA Weather API**: Fetch real-time weather data from Taiwan Central Weather Administration
- **MOENV AQI API**: Fetch real-time air quality data from Taiwan Ministry of Environment
- **Automatic data processing**: Clean, parse, and structure API responses into DataFrames

### Interactive Maps
- **Weather visualization**: Temperature-based color coding with station information
- **AQI visualization**: Simplified color scheme (green/yellow/red) based on air quality levels
- **Folium integration**: Interactive web maps with popup windows and tooltips

### Spatial Analysis
- **Distance calculation**: Haversine formula for accurate geodesic distances
- **Taipei Station reference**: Calculate distances from all monitoring stations to Taipei Station (25.0478, 121.5170)
- **Comprehensive statistics**: Nearest/farthest stations, average distances, distribution analysis

### Output Management
- **CSV exports**: Structured data files for further analysis
- **HTML maps**: Interactive visualizations ready for web deployment
- **Automated file naming**: Timestamp-based file organization

## Dependencies

This project uses key GIS libraries including:
- QGIS
- GeoPandas
- Shapely
- Rasterio
- Folium
- PostGIS (for spatial databases)
- pandas
- requests
- python-dotenv
- branca

## Environment Setup

This project is designed to run in the `py310` conda virtual environment:

```bash
# Activate the conda environment
conda activate py310

# Install required packages
pip install -r requirements.txt
```

## API Configuration

### Central Weather Administration (CWA)
- API endpoint: `https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001`
- Dataset: Automatic weather station observations
- Required: `CWA_API_KEY` in `.env` file

### Ministry of Environment (MOENV)
- API endpoint: `https://data.moenv.gov.tw/api/v2/aqx_p_432`
- Dataset: Air quality monitoring stations real-time data
- Required: `MOENV_API_KEY` in `.env` file

## Contributing

1. Follow the existing project structure
2. Add tests for new functionality
3. Update documentation as needed
4. Use meaningful commit messages

## License

[Add your license information here]
