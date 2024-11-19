# pipreqs . --force
pipreqs . --force --mode=no-pin
## awk -F'==' '{print $1}' requirements.txt > packages.txt

pip freeze > all_requirements.txt

grep -Ff requirements.txt all_requirements.txt > final_requirements.txt
rm requirements.txt all_requirements.txt packages.txt
mv final_requirements.txt requirements.txt