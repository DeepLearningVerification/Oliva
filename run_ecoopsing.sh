while IFS=, read -r index epsilon
do
    echo "Running: python run_single.py $index $epsilon GR mnistL2 0 1000 1"
    echo "------------------------"
    python run_single.py $index $epsilon GR mnistL2 0 1000 1
done < L2Mnist.csv
