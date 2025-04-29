# OLIVA

## Part I: Installation and Setup

#### Step (1) Set up for Python EVN
```
curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh 

bash Miniconda3-latest-Linux-x86_64.sh -b -u

source ~/miniconda3/bin/activate conda init bash

conda create -n oliva python=3.9 -y

conda activate oliva

pip install -r requirements.txt

```

#### Step (2) Installing Gurobi GUROBI installation instructions can be found at
    https://www.gurobi.com/documentation/9.5/quickstart_linux/software_installation_guid.html

For Linux-based systems the installation steps are: Install Gurobi:
```
wget https://packages.gurobi.com/9.1/gurobi9.1.2_linux64.tar.gz
tar -xvf gurobi9.1.2_linux64.tar.gz
cd gurobi912/linux64/src/build
sed -ie 's/^C++FLAGS =.*$/& -fPIC/' Makefile
make
cp libgurobi_c++.a ../../lib/
cd ../../
cp lib/libgurobi91.so /usr/local/lib -> (You may need to use sudo command for this)   
python3 setup.py install
cd ../../
```

#### Step (3) Update environment variables: i) Run following export commands in command prompt/terminal (these environment values are only valid for the current session) ii) Or copy the lines in the .bashrc file (or .zshrc if using zshell), and save the file

```
export GUROBI_HOME="$HOME/opt/gurobi950/linux64"
export GRB_LICENSE_FILE="$HOME/gurobi.lic"
export PATH="${PATH}:${GUROBI_HOME}/bin"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/$HOME/usr/local/lib:/usr/local/lib
```

Getting the free academic license To run GUROBI one also needs to get a free academic license. https://www.gurobi.com/documentation/9.5/quickstart_linux/retrieving_a_free_academic.html#subsection:academiclicense

a) Register using any academic email ID on the GUROBI website. b) Generate the license on https://portal.gurobi.com/iam/licenses/request/

Choose Named-user Academic

c)Use the command in the command prompt to generate the licesne.

(If not automatically done, place the license in one of the following locations " /opt/gurobi/gurobi.lic" or "$HOME/gurobi.lic")

#### Step (4) Install gurobipy

```
conda config --add channels https://conda.anaconda.org/gurobi

conda install gurobi -y
```

-----------

## Part II: Verification


### II.1 Demonstration with a toy example

``` 
python verifier_demo.py 
```

As shown

```
===========Performing Traditional BaB ===========
cur_spec:  -2.077680455153949 {}
cur_spec:  -1.9444060382513655 {(1, 1): -1}
cur_spec:  -2.077680455153949 {(1, 1): 1}
cur_spec:  0.3980555555555556 {(1, 1): -1, (1, 0): -1}
cur_spec:  -0.2855433333333335 {(1, 1): -1, (1, 0): 1}
cur_spec:  0.3980555555555556 {(1, 1): 1, (1, 0): -1}
cur_spec:  -1.451655555555556 {(1, 1): 1, (1, 0): 1}
find a counterexample 1.0 0.0 [-2.8335999999999997]
Total analyzer calls:  7

```
<img src="https://i.postimg.cc/rmtWs798/babrun.jpg" alt="BaB-baseline" width="450"/>


```
===========Performing Oliva ===========
cur_spec:  -2.077680455153949 {}
cur_spec:  -1.9444060382513655 {(1, 1): -1}
cur_spec:  -2.077680455153949 {(1, 1): 1}
cur_spec:  0.3980555555555556 {(1, 1): 1, (1, 0): -1}
cur_spec:  -1.451655555555556 {(1, 1): 1, (1, 0): 1}
find a counterexample 1.0 0.0 [-2.8335999999999997]
Total analyzer calls:  5

```

<img src="https://i.postimg.cc/28YvjcLD/oliverun.jpg" alt="OLIVA" width="450"/>

#### II.2 Running experiments

``` 
# e.g. To run CIFAR dataset with OVAL_DEEP model.
python verifier.py cifar10ovaldeep 01

# e.g. To run MNIST dataset with L4 model.
python verifier.py mnistL4 01

```

#### II.3 Comparisons
We have already generated all case and collected the properties stored in ./Compare/vnncomp2021 folder. 
The settings for alpha-beta-CROWN stored in mnistfc or oval yaml 

- To install the alpha-beta-CROWN 

```
# Remove the old environment, if necessary.
conda deactivate; conda env remove --name alpha-beta-crown
# install all dependents into the alpha-beta-crown environment
conda env create -f complete_verifier/environment.yaml --name alpha-beta-crown
# activate the environment
conda activate alpha-beta-crown
```

- To run alpha-beta-CROWN 
```
cd alpha-beta-CROWN/complete_verifier

# e.g. To run CIFAR dataset with OVAL_DEEP model.
python abcrown.py --config oval_deep.yaml --device=cpu

# e.g. To run MNIST dataset with L4 model.
python abcrown.py --config mnistfcL4.yaml --device=cpu
```

## Part III Results 

Our presented results on the paper are all available at ./ECOOPResults:

- To check the distribution of our data, please refer to
 ./ECOOPResults/histo.ipynb

- To check the over all results, please refer to 
./ECOOPResults/RQ1_overall.ipynb

- To check the speedup, please refer to 
./ECOOPResults/RQ1_scatterPlot.ipynb 

- To check the violated and certified verification, please refer to 
./ECOOPResults/RQ2_box.ipynb

- To check the hyper-parameter analysis 
./ECOOPResults/RQ3.ipynb


## Part IV Statistical difference of results (Oliva-G)

We present the statistical significance of the differences in our results by using Wilcoxon Signed Rank Test. In this table, the p-value indicates how significant the difference is between two results. The table presents statistical comparisons across different models and verification statuses, showing p-values and significance for various comparison targets. It includes both certified and non-certified models, with significance determined by a p-value threshold of 0.025. As the smaller the p-value, the more significant the difference.  

- Significant differences between Oliva and αβ-crown: There are 9 significant differences between Oliva and αβ-crown out of 10 total comparisons. Only OVAL21WDE in the "Not CERTIFIED" category shows a non-significant difference for this comparison.
- Non-significant differences between BaB-baseline and αβ-crown: There are 4 non-significant differences between BaB-baseline and αβ-crown out of 10 total comparisons. These occur for: OVAL21DEEP and OVAL21WDE in the "CERTIFIED" category, MNIST12 and OVAL21BASE in the "Not CERTIFIED" category. 
- For the 'certified' cases, the differences between Oliva and αβ-crown are statistically significant across 3 models. Similarly, Oliva and BaB-baseline show significant differences in all 5 models. Finally, αβ-crown and BaB-baseline show significant differences in 3 models.  
- For the 'not certified' cases, Oliva and αβ-crown show statistically significant difference in 2 models, Oliva and BaB-baseline show in 3 models, αβ-crown and BaB-baseline show in 4 models.

<img src='ECOOPResults/table_wilcoxon.png' alt='wilcoxon' width='950'/>

----------

## License and Copyright

Licensed under the [Apache License](https://www.apache.org/licenses/LICENSE-2.0)
- Our implementation is built on top of 
    - [ERAN] https://github.com/eth-sri/eran
    - [IVAN] https://github.com/uiuc-arc/Incremental-DNN-Verification 