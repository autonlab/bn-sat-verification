cd src

# There are two requirements
# 1. Model your Bayesian Network in pysmile and save in library native format (.xdsl)
# 2. Create bnc_configs/temperature.json config file
python scripts/convert_to_shih.py --input_file models/temperature.xdsl --output_file bnc_networks/temperature.net
python convert_net_to_odd.py --netconfigpath "bnc_configs/temperature.json" --netfilepath bnc_networks/temperature.net
python odd_parser.py --filepath odd_models/test/temperature_1.odd
python tseitin_encoding.py --odd odd_models/test/temperature_1.odd --cnf cnf_files/temperature.json --verbose