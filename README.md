conda create --name backtest-plots  python=3.8

conda activate backtest-plots

pip install -r requirements.txt

cd src/flow_plots

jupyter notebook

Check ./src/flow_plots/plot_flow.ipynb (Note: run jupyter from src/flow_plots)
