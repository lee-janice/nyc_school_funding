from src.analysis.pta_trends import pta_trends_analysis
from src.analysis.pta_cross_sectional_2025 import pta_cross_sectional_analysis

if __name__ == "__main__": 

    print("\nRunning trends-over-time analysis...")
    pta_trends_analysis("./output/pta_trends.txt")

    print("\nRunning cross-sectional analysis for 2025...")
    pta_cross_sectional_analysis(2025, "./output/pta_cross_sectional_2025.txt")
    

