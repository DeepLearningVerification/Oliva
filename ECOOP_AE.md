# ECOOP'25 Artifact: 


## Authors
    - Guanqin ZHANG (UNSW & CSIRO's Data61, Sydney, Australia)
    - Kota Fukuda  (Kyushu University, Fukuoka, Japan)
    - Zhenya Zhang  (Kyushu University, Fukuoka, Japan National Institute of Informatics, Tokyo, Japan)
    - H.M.N. Dilum Bandara (UNSW & CSIRO's Data61, Sydney, Australia)
    - Shiping CHEN  (UNSW & CSIRO's Data61, Sydney, Australia)
    - Jianjun Zhao  (Kyushu University, Fukuoka, Japan)
    - Yulei Sui (UNSW, Sydney, Australia)

## Important notes
    - Verifiers are mainly developed and well tested on Linux, using other operating systems might run into problems.
    - Verification problem is NP-complete, thus, hard to verify. Verifiers often take long time to finish. 


## 1. Quickstart

### 1.1 Requirements
    The following software is required for running this artifact:

    This artifact will be working fine with Linux/-alike. Please do not use it for Windows 

### 1.2 Installations
    With docker, you don't have to worry anything. 
    If building from scratch, please refer to 

### 1.3 Demonstration with a toy example (kick-the-tires-1)

#### Command:

``` 
python verifier_demo.py 
```

#### As shown:

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





### 1.4 Smoke Test Steps (kick-the-tires-2)

#### Command:
```
python run_single.py 61 0.0392156862745098 GR mnistL2 0 10
```

#### As shown:

```
~/Oliva# python run_single.py 1 0.0037421 GR mnistL2 0 10
************************** Proof 1 *****************************
Set parameter WLSAccessID
Set parameter WLSSecret
Model creation time:  0.09407567977905273
Status.VERIFIED
Results:  {<Status.VERIFIED: 1>: 1}
Average time: 0.37526464462280273
Verification Result: Status.VERIFIED
Time Taken: 0.38 seconds
Nodes Visited: 0
Lower Bound: None
```

## Available Badge 

We have already submitted as in the DART documentation, and publicly available at DOCKER, ZONODU, and Github. 

## Reusable Badge

```
python run_single.py 61 0.0392156862745098 GR mnistL2 0 10
```

Shown
```
Model creation time:  0.1075444221496582
SpecNode          LB:  -0.9929898977279663 status:  Status.UNKNOWN
Chosen relu for splitting: (1, 192) tensor(0.2752)

SpecNode          LB:  -0.9380231499671936 status:  Status.UNKNOWN

SpecNode          LB:  0.3237916827201843 status:  Status.VERIFIED
Chosen relu for splitting: (0, 158) tensor(0.2589)

SpecNode          LB:  -0.23620550334453583 status:  Status.UNKNOWN

SpecNode          LB:  None status:  Status.ADV_EXAMPLE
BnB Greedy Finished Verified Specicications, visited nodes: 5, find a counterexample
Status.ADV_EXAMPLE
Results:  {<Status.ADV_EXAMPLE: 2>: 1}
Average time: 6.60159969329834
Verification Result: Status.ADV_EXAMPLE
Time Taken: 6.60 seconds
Nodes Visited: 5
Lower Bound: -0.9380231499671936

```

Command:
```
python run_single.py 65 0.0392156862745098 GR mnistL4 0 10
```
Shown
```
:~/Oliva# python run_single.py 65 0.0392156862745098 GR mnistL4 0 10
Using Domain.LP abstract domain
************************** Proof 1 *****************************
Set parameter WLSAccessID
Set parameter WLSSecret
Set parameter LicenseID to value 2539858

Model creation time:  0.31084680557250977

SpecNode          LB:  -298.8519592285156 status:  Status.UNKNOWN
Chosen relu for splitting: (3, 155) tensor(37.8483)

SpecNode          LB:  -286.4038391113281 status:  Status.UNKNOWN

SpecNode          LB:  -287.9921569824219 status:  Status.UNKNOWN
BnB Greedy Finished Verified Specicications, visited nodes: 3
Status.UNKNOWN
Results:  {<Status.UNKNOWN: 3>: 1}
Average time: 31.596842050552368
Verification Result: Status.UNKNOWN
Time Taken: 31.60 seconds
Nodes Visited: 3
Lower Bound: -287.9921569824219
```

Command

```
python run_single.py 13 0.0470588235294117 GR cifarbase 0 10
```
Shown
```
Using Domain.LP abstract domain
Files already downloaded and verified
************************** Proof 1 *****************************
Set parameter WLSAccessID
Set parameter WLSSecret
Set parameter LicenseID to value 2539858
Academic license 2539858 - for non-commercial use only - registered to jo___@connect.polyu.hk
Model creation time:  1.7083404064178467

SpecNode          LB:  -1.7970117330551147 status:  Status.UNKNOWN
Chosen relu for splitting: (2, 53) tensor(0.4340)

SpecNode          LB:  -1.11887788772583 status:  Status.UNKNOWN

SpecNode          LB:  -1.0670123100280762 status:  Status.UNKNOWN
Chosen relu for splitting: (2, 5) tensor(0.2034)

SpecNode          LB:  -1.11887788772583 status:  Status.UNKNOWN

SpecNode          LB:  -1.116666316986084 status:  Status.UNKNOWN

...

```
## Functional Badge

### RQ0 - Data Statistics
Command
```
python AEC_scripts/RQ0.py --table1
```
Shown
```
Generating Table 1 analysis...
Model           Architecture            Dataset         #Activations    # Instances     #Images
MNISTL2         2 × 256 linear          MNIST           512             100             70
MNISTL4         4 × 256 linear          MNIST           1024            78              52
OVAL21BASE      2 Conv, 2 linear        CIFAR-10        3172            173             53
OVAL21WIDE      2 Conv, 2 linear        CIFAR-10        6244            196             53
OVAL21DEEP      4 Conv, 2 linear        CIFAR-10        6756            143             40
```
Command

```
python AEC_scripts/RQ0.py --figure3
```
Shown
```
Generating Figure 3 analysis...
Dataset                 Total   Verified        Falsified       Unknown
{'mnistL2': {'total': 100, 'verified': 84, 'falsified': 13, 'unknown': 3}, 'mnistL4': {'total': 78, 'verified': 39, 'falsified': 26, 'unknown': 13}, 'oval21_base': {'total': 173, 'verified': 40, 'falsified': 2, 'unknown': 131}, 'oval21_deep': {'total': 143, 'verified': 31, 'falsified': 2, 'unknown': 110}, 'oval21_wide': {'total': 196, 'verified': 31, 'falsified': 9, 'unknown': 156}}

```
Command
```
python AEC_scripts/RQ0.py --figure4
```
Shown
```
Generating Figure 4 analysis...
Distribution of instances by number of visited nodes:
$\mathdefault{MNIST_{L2}}$: {'0-10': 41, '11-50': 21, '51-100': 5, '101-200': 8, '201-500': 7, '501-1000': 11}
$\mathdefault{MNIST_{L4}}$: {'0-10': 21, '11-50': 20, '51-100': 6, '101-200': 4, '201-500': 9, '501-1000': 17}
$\mathdefault{OVAL21_{BASE}}$: {'0-10': 16, '11-50': 10, '51-100': 11, '101-200': 33, '201-500': 53, '501-1000': 37}
$\mathdefault{OVAL21_{DEEP}}$: {'0-10': 18, '11-50': 59, '51-100': 24, '101-200': 27, '201-500': 14, '501-1000': 1}
$\mathdefault{OVAL21_{WIDE}}$: {'0-10': 20, '11-50': 75, '51-100': 35, '101-200': 26, '201-500': 30, '501-1000': 10}
Total: {'0-10': 116, '11-50': 185, '51-100': 81, '101-200': 98, '201-500': 113, '501-1000': 76}
```


------

### RQ1 - Overall Performance Evaluation

Command
```
python AEC_scripts/RQ1.py --table2

```

Shown
```
Generating Table 2 analysis:
$\mnist_{{{\ltwo}}}$  &97&125.29 &88&50.81 &100&32.2 &96&95.94 &100&57.3  \\
$\mnist_{{{\lfour}}}$  &66&278.71 &44&465.64 &55&342.1 &67&266.98 &53&235.81  \\
$\OVAL_{{\base}}$ &42&770.7 &58&641.7 &70&621.21 &154&184.96 &159&155.29  \\
$\OVAL_{{\deep}}$ &33&735.69 &56&500.93 &56&480.96 &92&347.49 &87&328.21  \\
$\OVAL_{{\wide}}$ &40&739.97 &63&552.4 &65&523.62 &131&257.39 &112&303.43  \\

```
Our finshed experimental results is all available at ./ECOOPResults


<details><summary> Reproduce ALL data from Ground </summary>

In order to generate the results, each instances are under 1000s time budgets and for our BaB-baseline, Oliva^GR, and Oliva^SA, the promising time to finish all verification cases in 
3(verifier) x 1000(s) x 790(instances) = 658(h) under EC2 (8 core CPU x4Large 32G Ram). 

python verifier.py mnistL2 01 -1

python verifier.py mnistL4 01 -1

python verifier.py cifar10ovalbase 01 -1

python verifier.py cifar10ovaldeep 01 -1

python verifier.py cifar10ovalwide 01 -1

</details>

### Trial for validation

We value the reviewers' time, to easily validate our tool's reproducibility, we settled a short listed cases with initial 5 cases in our selected models and problem instances.

```
python verifier.py mnistL2 02 -1

python verifier.py mnistL4 02 -1

python verifier.py cifar10ovalbase 02 -1

python verifier.py cifar10ovaldeep 02 -1

python verifier.py cifar10ovalwide 02 -1

```
```
python AEC_scripts/RQ1.py --table3
```
Shown
```
Generating Table 3 analysis:
\bab-Baseline  & 0 & 81 &59 &9& 14\\ \hline
\abcrown & 112 & 0 & 11 &24& 40\\ \hline
\neuralsat & 127 &48 & 0  &32& 48\\\hline
\toolg & 271 &255 &226& 0 &  40\\\hline
\toolb & 247 &242 &213& 11 & 0  \\\hline
```


### Generating Table 4 analysis:
Command
```
python AEC_scripts/RQ1.py --table4
```
Shown
```


Statistics for overall:

Oliva$^{GR}$:
Min: 0.02
Max: 80.97
Median: 2.21
Mean: 7.27

Oliva$^{SA}$:
Min: 0.03
Max: 75.13
Median: 2.18
Mean: 7.57

...

```


----

### RQ2 (Figure 7)


```
/Oliva# python AEC_scripts/RQ2_box.py --a

===== BOXPLOT STATISTICS =====

--- Violated Instances (Status.ADV_EXAMPLE) ---
Oliva^GR:
  Count: 7
  Mean: 4.29
  Median: 1.81
  Min: 0.85
  Max: 17.52
  25th percentile: 1.05
  75th percentile: 3.87

Oliva^SA:
  Count: 7
  Mean: 5.99
  Median: 2.04
  Min: 0.87
  Max: 25.07
  25th percentile: 1.09
  75th percentile: 5.89

--- Certified Instances (Status.VERIFIED) ---
Oliva^GR:
  Count: 64
  Mean: 1.00
  Median: 1.00
  Min: 0.79
  Max: 1.33
  25th percentile: 0.94
  75th percentile: 1.07

Oliva^SA:
  Count: 64
  Mean: 1.18
  Median: 1.05
  Min: 0.81
  Max: 2.20
  25th percentile: 0.99
  75th percentile: 1.20

```
### RQ2 Sensitivity analysis (Figure 6)
```
 python AEC_scripts/RQ2_sa.py 

 ```

```
===== HEATMAP DATA FOR EACH METHOD =====
Global maximum count across all heatmaps: 117


==================================================
Method: sa0
==================================================

Heatmap Data (Values represent count of instances in each bin):
Performance Categories:
  0-0.5: Slower
  0.5-1: Slower
  1-2: Faster
  2-5: Faster
  5-10: Much Faster

--------------------------------------------------------------------------------

Heatmap Representation (count / intensity):
0-0.5 |   5  |   3  |   1  |   1  |   1  |   0 
0.5-1 | 114  |   3  |  10  |   1  |   0  |   0 
1-2   | 110  |   7  |   4  |   1  |   0  |   1 
--------------------------------------------------------------------------------
2-5   |   1  |   1  |   1  |   0  |   0  |   0 
5-10  |   2  |   0  |   0  |   0  |   0  |   0 

Row sums (by ratio category):
  0-0.5 (Slower): 11
  0.5-1 (Slower): 128
  1-2 (Faster): 123
  2-5 (Faster): 3
  5-10 (Much Faster): 2

Performance Summary:
  Slower:       139 (52.1%)
  Faster:       126 (47.2%)
  Much Faster:    2 (0.7%)

Column sums (by time bin):
  0-100s: 232
  100-200s: 14
  200-400s: 16
  400-600s: 3
  600-800s: 1
  800-1000s: 1

Total count: 267

==================================================
Method: sa1
==================================================

Heatmap Data (Values represent count of instances in each bin):
Performance Categories:
  0-0.5: Slower
  0.5-1: Slower
  1-2: Faster
  2-5: Faster
  5-10: Much Faster

--------------------------------------------------------------------------------

Heatmap Representation (count / intensity):
0-0.5 |   7  |   2  |   2  |   0  |   0  |   1 
0.5-1 | 108  |   5  |  11  |   1  |   0  |   1 
1-2   | 114  |   4  |   1  |   1  |   0  |   1 
--------------------------------------------------------------------------------
2-5   |   4  |   1  |   1  |   0  |   0  |   0 
5-10  |   1  |   0  |   0  |   0  |   0  |   0 

Row sums (by ratio category):
  0-0.5 (Slower): 12
  0.5-1 (Slower): 126
  1-2 (Faster): 121
  2-5 (Faster): 6
  5-10 (Much Faster): 1

Performance Summary:
  Slower:       138 (51.9%)
  Faster:       127 (47.7%)
  Much Faster:    1 (0.4%)

Column sums (by time bin):
  0-100s: 234
  100-200s: 12
  200-400s: 15
  400-600s: 2
  600-800s: 0
  800-1000s: 3

Total count: 266

```


----

### RQ 3 - Figure 8 

```
python AEC_scripts/RQ3.py --lambda

===== LAMBDA PARAMETER ANALYSIS =====

--- λ=0 ---
  Count: 20
  Mean: 3.39
  Median: 1.01
  Min: 0.74
  Max: 23.81
  25th percentile: 0.85
  75th percentile: 3.16

--- λ=0.2 ---
  Count: 20
  Mean: 4.04
  Median: 1.13
  Min: 0.74
  Max: 27.82
  25th percentile: 0.87
  75th percentile: 4.46

--- λ=0.4 ---
  Count: 20
  Mean: 4.24
  Median: 1.15
  Min: 0.74
  Max: 27.28
  25th percentile: 0.93
  75th percentile: 4.37

--- λ=0.5
(Default) ---
  Count: 20
  Mean: 4.69
  Median: 1.16
  Min: 0.75
  Max: 33.54
  25th percentile: 0.91
  75th percentile: 4.54
  
```

### RQ3 - Figure 9

```
python AEC_scripts/RQ3.py --alpha

===== LAMBDA PARAMETER ANALYSIS =====

--- λ=0 ---
  Count: 20
  Mean: 3.39
  Median: 1.01
  Min: 0.74
  Max: 23.81
  25th percentile: 0.85
  75th percentile: 3.16

--- λ=0.2 ---
  Count: 20
  Mean: 4.04
  Median: 1.13
  Min: 0.74
  Max: 27.82
  25th percentile: 0.87
  75th percentile: 4.46

--- λ=0.4 ---
  Count: 20
  Mean: 4.24
  Median: 1.15
  Min: 0.74
  Max: 27.28
  25th percentile: 0.93
  75th percentile: 4.37

--- λ=0.5
(Default) ---
  Count: 20
  Mean: 4.69
  Median: 1.16
  Min: 0.75
  Max: 33.54
  25th percentile: 0.91
  75th percentile: 4.54

--- λ=0.6 ---
  Count: 20
  Mean: 4.23
  Median: 1.15
  Min: 0.73
  Max: 27.00
  25th percentile: 0.92
  75th percentile: 4.42

--- λ=0.8 ---
  Count: 20
  Mean: 4.21
  Median: 1.14
  Min: 0.73
  Max: 26.58
  25th percentile: 0.91
  75th percentile: 4.41

--- λ=1 ---
  Count: 20
  Mean: 4.13
  Median: 1.09
  Min: 0.21
  Max: 25.67
  25th percentile: 0.85
  75th percentile: 4.81

--- Summary of Mean Speedups ---
  λ=0: 3.39x
  λ=0.2: 4.04x
  λ=0.4: 4.24x
  λ=0.5
(Default): 4.69x
  λ=0.6: 4.23x
  λ=0.8: 4.21x
  λ=1: 4.13x

```