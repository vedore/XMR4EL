import os
import time
import platform

if platform.machine() == 'aarch64':  # ARM only
    os.environ['LD_PRELOAD'] = '/lib/aarch64-linux-gnu/libgomp.so.1'

# LD_PRELOAD=/lib/aarch64-linux-gnu/libgomp.so.1
from argparse import ArgumentParser
from xmr4el.featurization.preprocessor import Preprocessor
from xmr4el.xmr.model import XModel


"""
    Depending on the train file, different number of labels, 

    * train_Disease_100.txt -> 13240 labels, 
    * train_Disease_500.txt -> 13190 labels, 
    * train_Disease_1000.txt -> 13203 labels,  

    Labels file has,

    * labels.txt -> 13292 labels,
"""

def main():
    
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument("-ds_len", type=int, default=10000000)
    parser.add_argument("-train_path", type=str, required=True)
    parser.add_argument("-model_config", type=str, default=".models/xmr4el_base_config.json")
    
    args = parser.parse_args()
    
    start = time.time()
    
    train_data = Preprocessor.load_pubtator_file(args.train_path)
    
    X_train, Y_train = Preprocessor.organize_pubtator_output(train_data)
    
    del train_data
    
    xmodel = XModel.load_config(args.model_config)

    xmodel.train(X_train[:args.ds_len], Y_train[:args.ds_len])

    # Save the tree
    save_dir = os.path.join(os.getcwd(), "test/test_data/saved_trees")  # Ensure this path is correct and writable
    xmodel.save(save_dir)

    end = time.time()
    print(f"{end - start} secs of running")

# Here is code
if __name__ == "__main__":
    main()
