from bs4 import BeautifulSoup
import requests
import pandas

container= list()
#job_title
#job_company
#job_place
#job_exp_required
#job_posted

def getjob(keyword, ):
    url= "https://www.ctgoodjobs.hk/ctjob/listing/joblist.asp?keywordForQuickSearch={}&page=1".format(keyword)
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'html.parser')
    jobs = soup.find_all("div", class_="row jl-row jl-de active")
    for job in jobs:
        job_title= job.find("div", class_="jl-title").get_text()
        job_company= job.find("div", class_="jl-comp").get_text()
        job_place= job.find("li", class_="loc col-xs-12").get_text()
        job_exp_required= job.find("li", class_="exp col-xs-12").get_text()
        job_posted= job.find("li",class_="post-date col-xs-12").get_text()
        
        container.append({
            'title' : job_title,
            'company' : job_company,
            'place' : job_place,
            'exp_required' : job_exp_required,
            'posted' : job_posted
        })
         
    

def main():
    
    keyword = input("input the keyword: ")
    getjob(keyword)
    print(container)

if __name__ == '__main__':
    main()
