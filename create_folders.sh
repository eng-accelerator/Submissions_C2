names="Georgy Pulivilayil James
Rajkumar Vaitheeswaran
Debashis Nayak
Parag Doshi
Siddhartha
Nandini Reddy
Ivan Lewis
Venu Kunchala
neelay mehta
Prerna Jain
Maruti Divekar
Siddhant Chothe
Srikant Kumar Sahu
Amit Khandelwal
Sampathkumar Baskar
Guchi Jaurre
Sabitha P U
Vibha TS
Mishi Vidya Sinku
Sagar Parikh
Sunil Garg
Manish Kumar Pathak
Gaurav
Monalisa Samal
IT CARE Paweł Łabuz
Vishnu Priya K
Sushil Kumar
Sunita Sahu
Gururaja Kalmanje
Ramesh M
M MohanaVamsi
Avinash Behera
Jaywant D Mahajan
Mahender Endarapu
Mayur Chaudhari
Seshagiri Rao Vaidya
Deepak SIngh
Prasanna Neelavar
Girish Basavaraj Hiremath
S Vallurupalli
Ravindra Babburi
Srinivasan Muralidharan
Revolut Joint Card
Manohar Negi
Abdullah Ansari
Pramod bhagat
Ashish Sahu
Soumya S
sangu santosh
Vivek Trivedi
Ajay Kakadia
Chandra Sekhar Yandra
Saravanan P
Rajesh K
Durga Prasad Chimmili
Uma
Nilesh Anchan
Chandrap
Dineshbabu Sengottian
Aditya Bajpai
CORINTHIAN CARPENTER
Jayanthi K
Jatin Garg
Pradeep Kumar Myakala
Santheep
NIRANJAN SINGH
Swati Gambhir
Pranay Mishra
Shubham Gupta
Tang Kit
nitesh sharma
SHABBIR KAGALWALA
Sumit Vedpathak
Michal Maciejewski
V Kalyan Korumilli
Nitin Deshmukh
Srinivas Kini K
Mamta kumari
Anindita A Sarkar
Vasanth Kumar R
Leonel Vanegas
Girish Ramarao
Asheesh Ranjan Srivastava
Puja Rohatgi
Shaurya
Rashmi Iyer
Rahul Sharma"

while IFS= read -r name; do
    dir_name=$(echo "$name" | tr ' ' '_')
    mkdir -p "$dir_name"
    echo "# $dir_name" > "$dir_name/README.md"
done <<< "$names"
